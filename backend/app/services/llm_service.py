import os
import json
from typing import Dict, List, Optional
from pathlib import Path
from jinja2 import Template
from openai import OpenAI

class LLMService:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = None
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)

        self.prompt_template = self._load_prompt_template()

    def _clean_pappers_data(self, pappers_data: Dict) -> Optional[Dict]:
        """
        Nettoie les données Pappers pour ne garder que les champs utiles.
        Évite d'envoyer 5000 lignes de JSON brut au LLM.
        """
        if not pappers_data:
            return None

        cleaned = {}

        # Entreprise principale
        if 'entreprise' in pappers_data:
            ent = pappers_data['entreprise']
            cleaned['entreprise'] = {
                'nom': ent.get('nom_entreprise'),
                'siren': ent.get('siren'),
                'forme_juridique': ent.get('forme_juridique'),
                'date_creation': ent.get('date_creation'),
                'capital': ent.get('capital'),
                'effectif': ent.get('tranche_effectif'),
                'activite': ent.get('libelle_activite_principale'),
                'siege': {
                    'ville': ent.get('siege', {}).get('ville'),
                    'code_postal': ent.get('siege', {}).get('code_postal')
                }
            }

            # Données financières (CRITIQUE)
            if 'dernier_bilan' in ent:
                bilan = ent['dernier_bilan']
                cleaned['entreprise']['finances'] = {
                    'exercice': bilan.get('date_cloture_exercice'),
                    'chiffre_affaires': bilan.get('chiffre_affaires'),
                    'resultat_net': bilan.get('resultat'),
                    'capitaux_propres': bilan.get('capitaux_propres'),
                    'total_bilan': bilan.get('total_bilan')
                }

        # Dirigeants et bénéficiaires
        if 'representants' in pappers_data:
            cleaned['dirigeants'] = [
                {
                    'nom': rep.get('nom'),
                    'prenom': rep.get('prenom'),
                    'qualite': rep.get('qualite'),
                    'date_prise_poste': rep.get('date_prise_de_poste')
                }
                for rep in pappers_data['representants'][:10]  # Max 10 dirigeants
            ]

        if 'beneficiaires_effectifs' in pappers_data:
            cleaned['beneficiaires'] = [
                {
                    'nom': ben.get('nom'),
                    'prenom': ben.get('prenom'),
                    'pourcentage_capital': ben.get('pourcentage_parts'),
                    'pourcentage_votes': ben.get('pourcentage_votes')
                }
                for ben in pappers_data['beneficiaires_effectifs'][:5]  # Max 5 bénéficiaires
            ]

        # Mandats dans d'autres entreprises
        if 'mandats' in pappers_data:
            cleaned['autres_mandats'] = [
                {
                    'entreprise': m.get('nom_entreprise'),
                    'siren': m.get('siren'),
                    'qualite': m.get('qualite'),
                    'actif': m.get('actif', True)
                }
                for m in pappers_data['mandats'][:15]  # Max 15 mandats
            ]

        # Publications BODACC récentes
        if 'publications_bodacc' in pappers_data:
            cleaned['bodacc'] = [
                {
                    'type': pub.get('type'),
                    'date': pub.get('date_parution'),
                    'numero': pub.get('numero_parution')
                }
                for pub in pappers_data['publications_bodacc'][:10]  # Max 10 pubs
            ]

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


    def _load_prompt_template(self) -> Template:
        # Utiliser le nouveau prompt Due Diligence
        template_path = Path(__file__).parent.parent / 'templates' / 'prompts' / 'due_diligence_analysis.txt'

        if not template_path.exists():
            raise FileNotFoundError(f"Prompt template not found: {template_path}")

        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        return Template(template_content)

    def create_analysis_prompt(self, first_name: str, last_name: str, company: str, scraped_data: List[Dict], pappers_data: Dict = None, dvf_data: Dict = None, hatvp_data: Dict = None) -> str:
        content_summary = "\n\n".join([
            f"Source: {item['source']}\nQuery: {item['url']}\nContent:\n{item['content'][:2000]}"
            for item in scraped_data
        ])

        # Nettoyer et formater les données structurées (économie de tokens + focus sur l'essentiel)
        pappers_cleaned = self._clean_pappers_data(pappers_data)
        dvf_cleaned = self._clean_dvf_data(dvf_data)
        hatvp_cleaned = self._clean_hatvp_data(hatvp_data)

        pappers_formatted = json.dumps(pappers_cleaned, indent=2, ensure_ascii=False) if pappers_cleaned else None
        dvf_formatted = json.dumps(dvf_cleaned, indent=2, ensure_ascii=False) if dvf_cleaned else None
        hatvp_formatted = json.dumps(hatvp_cleaned, indent=2, ensure_ascii=False) if hatvp_cleaned else None

        prompt = self.prompt_template.render(
            first_name=first_name,
            last_name=last_name,
            company=company,
            content_summary=content_summary,
            pappers_data=pappers_formatted,
            dvf_data=dvf_formatted,
            hatvp_data=hatvp_formatted
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
                        # On le transforme en "Observé : Trait (données insuffisantes pour justifier)"
                        cleaned_traits.append(f"Observé : {trait} (justification insuffisante - à valider)")

                pa['personality_traits'] = cleaned_traits

        return profile_data

    def analyze_profile(self, first_name: str, last_name: str, company: str, scraped_data: List[Dict], pappers_data: Dict = None, dvf_data: Dict = None, hatvp_data: Dict = None) -> Dict:
        if not self.client:
            raise ValueError("OpenAI API key not configured")

        if not scraped_data or all(not item.get('success') for item in scraped_data):
            raise ValueError("No valid scraped data available for analysis")

        try:
            prompt = self.create_analysis_prompt(first_name, last_name, company, scraped_data, pappers_data, dvf_data, hatvp_data)

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

