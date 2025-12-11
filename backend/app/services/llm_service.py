import os
import json
from typing import Dict, List, Optional
from pathlib import Path
from jinja2 import Template
from openai import OpenAI

# v3.1: Import content cleaning utilities
from app.utils.content_cleaner import (
    clean_scraped_html,
    parse_linkedin_posts,
    estimate_token_count
)

class LLMService:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = None
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)

        self.prompt_template = self._load_prompt_template()

    def _clean_pappers_data(self, pappers_data: Dict) -> Optional[Dict]:
        """
        Nettoie les données Pappers v3.1 pour ne garder que les champs utiles.
        Structure: pappers_data['companies'] contient liste d'entreprises avec economic_data
        """
        if not pappers_data or not pappers_data.get('companies'):
            return None

        cleaned = {
            'full_name': pappers_data.get('full_name'),
            'companies': []
        }

        # Nettoyer chaque entreprise trouvée
        for company in pappers_data['companies'][:3]:  # Max 3 entreprises
            company_clean = {
                'nom': company.get('nom_entreprise'),
                'siren': company.get('siren'),
                'person_found': company.get('person_found', False),
                'person_mandates': company.get('person_mandates', [])
            }

            # Extraire economic_data si présent
            if 'economic_data' in company:
                econ = company['economic_data']
                company_clean['economic'] = {
                    # Base
                    'capital_social': econ.get('capital_social'),
                    'chiffre_affaires': econ.get('chiffre_affaires'),
                    'resultat': econ.get('resultat'),
                    'effectif': econ.get('effectif'),
                    'date_creation': econ.get('date_creation'),
                    'statut_rcs': econ.get('statut_rcs'),
                    'entreprise_cessee': econ.get('entreprise_cessee'),

                    # RED FLAGS
                    'procedures_collectives': econ.get('procedures_collectives', []),
                    'date_radiation_rcs': econ.get('date_radiation_rcs'),

                    # Comptes (historique financier 5 ans)
                    'comptes': econ.get('comptes', [])[:5],  # 5 derniers exercices

                    # BODACC
                    'annonces_bodacc': econ.get('annonces_bodacc', [])[:10],
                }

                # v3.1: Champs premium (si disponibles)
                if 'entreprises_dirigees' in econ and econ['entreprises_dirigees']:
                    company_clean['economic']['entreprises_dirigees'] = list(econ['entreprises_dirigees'])[:10]

                if 'observations' in econ and econ['observations']:
                    company_clean['economic']['observations'] = list(econ['observations'])[:10]

                if 'decisions' in econ and econ['decisions']:
                    company_clean['economic']['decisions'] = list(econ['decisions'])[:5]  # Décisions de justice

                if 'parcelles_detenues' in econ and econ['parcelles_detenues']:
                    parcelles_data = econ['parcelles_detenues']
                    # Pappers retourne {'resultats': [], 'total': N, 'incomplet': bool}
                    if isinstance(parcelles_data, dict) and 'resultats' in parcelles_data:
                        company_clean['economic']['parcelles_detenues'] = parcelles_data.get('resultats', [])[:10]
                    else:
                        company_clean['economic']['parcelles_detenues'] = list(parcelles_data)[:10]

            cleaned['companies'].append(company_clean)

        # Publications BODACC de la personne (recherche par nom)
        if 'bodacc_person' in pappers_data and pappers_data['bodacc_person']:
            bodacc = pappers_data['bodacc_person']
            cleaned['bodacc_person'] = {
                'total': bodacc.get('total', 0),
                'publications': bodacc.get('publications', [])[:10],  # 10 premières
                'types': bodacc.get('types', {})
            }

        return cleaned

    def _clean_dvf_data(self, dvf_data: Dict) -> Optional[Dict]:
        """Nettoie les données DVF (déjà minimal normalement)"""
        if not dvf_data:
            return None

        return {
            'snippets_count': dvf_data.get('count', 0),
            'mentions': dvf_data.get('snippets', [])[:5],  # Max 5 mentions
            'full_name': dvf_data.get('full_name')
        }

    def _clean_hatvp_data(self, hatvp_data: Dict) -> Optional[Dict]:
        """Nettoie les données HATVP (déjà minimal normalement)"""
        if not hatvp_data:
            return None

        return {
            'ppe_detected': hatvp_data.get('ppe_detected', False),
            'snippets_count': hatvp_data.get('count', 0),
            'mentions': hatvp_data.get('snippets', [])[:5],  # Max 5 mentions
            'full_name': hatvp_data.get('full_name')
        }

    def _summarize_linkedin_posts(self, posts: List[Dict]) -> List[Dict]:
        """
        Pré-résume les posts LinkedIn avec GPT-4o-mini pour économiser des tokens.

        Réduit les posts de ~300-500 tokens chacun à ~50-100 tokens.
        Coût: $0.15/1M tokens (16x moins cher que GPT-4o)
        Réduction: ~80% des tokens

        Args:
            posts: Liste de posts parsés (avec content, date, engagement)

        Returns:
            Liste de posts résumés (avec content_summary, themes, expertise_signals)
        """
        if not posts or not self.client:
            return []

        summarized_posts = []

        try:
            for post in posts[:10]:  # Max 10 posts
                if not post.get('content') or len(post['content']) < 50:
                    continue

                # Résumer avec GPT-4o-mini (cheap & fast)
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",  # 16x cheaper than gpt-4o
                    messages=[
                        {
                            "role": "system",
                            "content": "Tu es un assistant d'analyse de contenu LinkedIn. Résume le post en identifiant les thématiques et signaux d'expertise. Réponds en JSON avec: {\"summary\": \"...\", \"themes\": [...], \"expertise_signals\": \"...\"}. Sois concis (max 2 phrases)."
                        },
                        {
                            "role": "user",
                            "content": f"Post LinkedIn:\n{post['content'][:1000]}"  # Limit input
                        }
                    ],
                    temperature=0.3,
                    max_tokens=150,  # Short summary
                    response_format={"type": "json_object"}
                )

                result = json.loads(response.choices[0].message.content)

                summarized_posts.append({
                    'content_summary': result.get('summary', ''),
                    'themes': result.get('themes', []),
                    'expertise_signals': result.get('expertise_signals', ''),
                    'date': post.get('date'),
                    'engagement': post.get('engagement')
                })

                print(f"[LLM] Post résumé: {len(post['content'])} chars → {len(result.get('summary', ''))} chars")

        except Exception as e:
            print(f"[LLM] Erreur résumé posts: {e}")
            # Fallback: retourner posts bruts (sans résumé)
            return [{'content_summary': p['content'][:200], 'themes': [], 'expertise_signals': ''} for p in posts[:5]]

        return summarized_posts

    def _clean_and_process_scraped_data(self, scraped_data: List[Dict]) -> tuple[str, List[Dict]]:
        """
        Nettoie et traite les données scrapées pour réduire les tokens.

        1. Nettoie HTML avec BeautifulSoup (supprime nav, footer, ads)
        2. Extrait posts LinkedIn si présents
        3. Résume les posts avec GPT-4o-mini
        4. Retourne contenu nettoyé + posts résumés

        Réduction estimée: 60-70% des tokens web

        Args:
            scraped_data: Données brutes de Firecrawl

        Returns:
            (content_summary: str, linkedin_posts_summarized: List[Dict])
        """
        cleaned_items = []
        all_linkedin_posts = []

        print(f"[LLM] Nettoyage de {len(scraped_data)} pages scrapées...")

        for item in scraped_data:
            url = item.get('url', '')
            raw_content = item.get('content', '')

            # Nettoyer HTML
            cleaned_content = clean_scraped_html(raw_content, url)

            # Estimer réduction
            tokens_before = estimate_token_count(raw_content)
            tokens_after = estimate_token_count(cleaned_content)
            reduction = ((tokens_before - tokens_after) / tokens_before * 100) if tokens_before > 0 else 0

            print(f"[LLM] {url[:50]}... : {tokens_before} → {tokens_after} tokens (-{reduction:.0f}%)")

            # Extraire posts LinkedIn si c'est une page d'activité
            if 'linkedin.com' in url.lower() and '/activity' in url.lower():
                posts = parse_linkedin_posts(raw_content)
                if posts:
                    all_linkedin_posts.extend(posts)
                    print(f"[LLM] {len(posts)} posts LinkedIn extraits de {url}")

            # Limiter contenu nettoyé (max 2000 chars par page)
            cleaned_items.append({
                'source': item.get('source', 'unknown'),
                'url': url,
                'content': cleaned_content[:2000]
            })

        # Assembler résumé du contenu
        content_summary = "\n\n".join([
            f"Source: {item['source']}\nURL: {item['url']}\n{item['content']}"
            for item in cleaned_items
        ])

        # Résumer les posts LinkedIn avec GPT-4o-mini
        linkedin_posts_summarized = []
        if all_linkedin_posts:
            print(f"[LLM] Résumé de {len(all_linkedin_posts)} posts LinkedIn avec GPT-4o-mini...")
            linkedin_posts_summarized = self._summarize_linkedin_posts(all_linkedin_posts)

        return content_summary, linkedin_posts_summarized

    def _load_prompt_template(self) -> Template:
        # Utiliser le nouveau prompt Due Diligence
        template_path = Path(__file__).parent.parent / 'templates' / 'prompts' / 'due_diligence_analysis.txt'

        if not template_path.exists():
            raise FileNotFoundError(f"Prompt template not found: {template_path}")

        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        return Template(template_content)

    # v3.1: Anchor profile logic removed (overkill for current use case)
    # Direct analysis with GPT-4o handles homonyms naturally with context

    def create_analysis_prompt(self, first_name: str, last_name: str, company: str, scraped_data: List[Dict], pappers_data: Dict = None, dvf_data: Dict = None, hatvp_data: Dict = None, linkedin_urls: List[str] = None) -> str:
        # v3.1: Nettoyer et traiter les données scrapées (réduction 60-70% tokens)
        content_summary, linkedin_posts_summarized = self._clean_and_process_scraped_data(scraped_data)

        pappers_cleaned = self._clean_pappers_data(pappers_data)
        dvf_cleaned = self._clean_dvf_data(dvf_data)
        hatvp_cleaned = self._clean_hatvp_data(hatvp_data)

        pappers_formatted = json.dumps(pappers_cleaned, indent=2, ensure_ascii=False) if pappers_cleaned else None
        dvf_formatted = json.dumps(dvf_cleaned, indent=2, ensure_ascii=False) if dvf_cleaned else None
        hatvp_formatted = json.dumps(hatvp_cleaned, indent=2, ensure_ascii=False) if hatvp_cleaned else None

        linkedin_posts_formatted = json.dumps(linkedin_posts_summarized, indent=2, ensure_ascii=False) if linkedin_posts_summarized else None
        linkedin_urls_formatted = json.dumps(linkedin_urls, indent=2, ensure_ascii=False) if linkedin_urls else None

        total_tokens = estimate_token_count(content_summary)
        if pappers_formatted:
            total_tokens += estimate_token_count(pappers_formatted)
        if linkedin_posts_formatted:
            total_tokens += estimate_token_count(linkedin_posts_formatted)

        print(f"[LLM] Tokens estimés pour l'analyse: ~{total_tokens} tokens")

        prompt = self.prompt_template.render(
            first_name=first_name,
            last_name=last_name,
            company=company,
            content_summary=content_summary,
            pappers_data=pappers_formatted,
            dvf_data=dvf_formatted,
            hatvp_data=hatvp_formatted,
            linkedin_posts=linkedin_posts_formatted,
            linkedin_urls=linkedin_urls_formatted
        )
        return prompt

    def _validate_and_fix_profile(self, profile_data: Dict) -> Dict:
        """
        Valide et corrige automatiquement les erreurs courantes du LLM.
        Applique les règles strictes que GPT-4o ignore parfois.
        """
        import re
        from datetime import datetime

        current_year = datetime.now().year

        # 1. Corriger dates futures (2025+)
        def fix_year(value):
            """Corrige une année si > current_year"""
            if isinstance(value, int) and value > current_year:
                return current_year
            if isinstance(value, str):
                # Chercher année 4 chiffres
                match = re.search(r'20\d{2}', value)
                if match:
                    year = int(match.group())
                    if year > current_year:
                        return value.replace(str(year), str(current_year))
            return value

        # Corriger companies_led.since
        if 'business_ecosystem' in profile_data and 'companies_led' in profile_data['business_ecosystem']:
            for company in profile_data['business_ecosystem']['companies_led']:
                if 'since' in company:
                    company['since'] = str(fix_year(company['since']))

        # Corriger career_timeline.year
        if 'career_timeline' in profile_data:
            for event in profile_data['career_timeline']:
                if 'year' in event:
                    event['year'] = fix_year(event['year'])

        # Corriger professional_experience.period
        if 'professional_experience' in profile_data:
            for exp in profile_data['professional_experience']:
                if 'period' in exp and exp['period']:
                    exp['period'] = str(fix_year(exp['period']))

        # 2. Forcer remplissage sources financières
        if 'financial_intelligence' in profile_data:
            fi = profile_data['financial_intelligence']

            # Si revenue_evolution rempli mais pas de source
            if fi.get('revenue_evolution') and not fi.get('revenue_evolution_source'):
                fi['revenue_evolution_source'] = "Source non spécifiée - Validation requise"

            # Si financial_stability rempli mais pas de source
            if fi.get('financial_stability') and not fi.get('financial_stability_source'):
                fi['financial_stability_source'] = "Source non spécifiée - Validation requise"

            # Si capital_structure rempli mais pas de source
            if fi.get('capital_structure') and not fi.get('capital_structure_source'):
                fi['capital_structure_source'] = "Source non spécifiée - Validation requise"

        # 3. Nettoyer personality_traits sans justification
        if 'psychology_and_approach' in profile_data:
            pa = profile_data['psychology_and_approach']

            if 'personality_traits' in pa and pa['personality_traits']:
                cleaned_traits = []
                for trait in pa['personality_traits']:
                    # Vérifier si format "Trait (justification)"
                    if '(' in trait and ')' in trait:
                        cleaned_traits.append(trait)
                    else:
                        # Trait sans justification → transformer ou supprimer
                        cleaned_traits.append(f"Observé : {trait} (justification insuffisante - à valider)")

                pa['personality_traits'] = cleaned_traits

        return profile_data

    def analyze_profile(self, first_name: str, last_name: str, company: str, scraped_data: List[Dict], pappers_data: Dict = None, dvf_data: Dict = None, hatvp_data: Dict = None, linkedin_urls: List[str] = None) -> Dict:
        if not self.client:
            raise ValueError("OpenAI API key not configured")

        if not scraped_data or all(not item.get('success') for item in scraped_data):
            raise ValueError("No valid scraped data available for analysis")

        try:
            prompt = self.create_analysis_prompt(first_name, last_name, company, scraped_data, pappers_data, dvf_data, hatvp_data, linkedin_urls)

            response = self.client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', "gpt-4o"),
                messages=[
                    {"role": "system", "content": "Tu es un expert en intelligence économique et due diligence. Tu analyses les données légales (Pappers), le patrimoine immobilier (DVF), les personnes politiquement exposées (HATVP) et les données web pour évaluer la crédibilité, solvabilité et personnalité d'une personne. Tu rédiges TOUJOURS EN FRANÇAIS et tu réponds en JSON valide."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)

            # Valider et corriger automatiquement les erreurs communes
            print("[LLM] Validation et correction post-génération...")
            result = self._validate_and_fix_profile(result)

            return result

        except Exception as e:
            print(f"OpenAI API error: {e}")
            raise Exception(f"Failed to analyze profile with OpenAI: {str(e)}")
