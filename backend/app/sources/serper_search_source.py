import os
import requests
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from app.sources.base_source import BaseSource

class SerperSearchSource(BaseSource):
    def __init__(self):
        self.api_key = os.getenv('SERPER_API_KEY')
        self.base_url = "https://google.serper.dev/search"
        self.news_url = "https://google.serper.dev/news"

    @classmethod
    def get_name(cls) -> str:
        return "serper_search"

    @classmethod
    def get_description(cls) -> str:
        return "ReEn cherche Google via Serper API (web + news + snippets)"

    def search_google(self, query: str, num_results: int = 10) -> Optional[Dict]:
        """
        Recherche Google via Serper
        Note: Serper retourne max 10 résultats par page, utilise pagination pour plus
        """
        if not self.api_key:
            print("[Serper] API key not configured, skipping")
            return None

        try:
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }

            # Serper retourne max 10 résultats par page
            # Pour avoir plus, il faut paginer
            num_pages = (num_results + 9) // 10  # Arrondi supérieur
            all_results = []

            for page in range(1, num_pages + 1):
                payload = {
                    'q': query,
                    'page': page,
                    'num': 10,  # Max 10 par page
                    'gl': 'fr',
                }

                if page == 1:
                    print(f"[Serper] Searching: {query} ({num_results} results via {num_pages} page(s))")

                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    organic = data.get('organic', [])
                    all_results.extend(organic)

                    if page == 1:
                        print(f"[Serper] ✓ Page 1: {len(organic)} results")
                    else:
                        print(f"[Serper] ✓ Page {page}: {len(organic)} results")

                    # Si moins de 10 résultats, pas de page suivante
                    if len(organic) < 10:
                        break
                else:
                    print(f"[Serper] ✗ Page {page} Error {response.status_code}")
                    break

            # Retourner au format Serper standard
            return {
                'organic': all_results[:num_results],  # Limiter au nombre demandé
                'searchParameters': {'q': query, 'num': num_results}
            }

        except Exception as e:
            print(f"[Serper] ✗ Exception: {e}")
            return None

    def search_news(self, query: str, num_results: int = 10) -> Optional[Dict]:
        """
        Recherche Google News via Serper
        Note: Serper retourne max 10 résultats par page, utilise pagination pour plus
        """
        if not self.api_key:
            print("[Serper News] API key not configured, skipping")
            return None

        try:
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }

            # Pagination pour obtenir plus de 10 résultats
            num_pages = (num_results + 9) // 10
            all_news = []

            for page in range(1, num_pages + 1):
                payload = {
                    'q': query,
                    'page': page,
                    'num': 10,
                    'gl': 'fr',
                }

                if page == 1:
                    print(f"[Serper News] Searching: {query} ({num_results} articles via {num_pages} page(s))")

                response = requests.post(
                    self.news_url,
                    headers=headers,
                    json=payload,
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    news = data.get('news', [])
                    all_news.extend(news)

                    if page == 1:
                        print(f"[Serper News] ✓ Page 1: {len(news)} articles")
                    else:
                        print(f"[Serper News] ✓ Page {page}: {len(news)} articles")

                    if len(news) < 10:
                        break
                else:
                    print(f"[Serper News] ✗ Page {page} Error {response.status_code}")
                    break

            return {
                'news': all_news[:num_results],
                'searchParameters': {'q': query, 'num': num_results}
            }

        except Exception as e:
            print(f"[Serper News] ✗ Exception: {e}")
            return None

    def extract_urls_and_snippets(self, search_results: Dict, is_news: bool = False) -> List[Dict]:
        extracted = []

        # Support both organic results (web search) and news results
        results = search_results.get('news', []) if is_news else search_results.get('organic', [])

        for result in results:
            url = result.get('link')
            snippet = result.get('snippet', '')
            title = result.get('title', '')

            if url:
                extracted.append({
                    'url': url,
                    'snippet': snippet,
                    'title': title,
                    'position': result.get('position', 999),
                    'scrapable': self._is_url_scrapable(url),
                    'date': result.get('date', None) if is_news else None  # Date pour les news
                })

        extracted.sort(key=lambda x: x['position'])

        return extracted

    def _is_url_scrapable(self, url: str) -> bool:        
        if not url:
            return False
        
        non_scrapable_domains = [
            'linkedin.com',  
            'facebook.com',  
            'twitter.com',   
            'instagram.com', 
            'youtube.com',   
        ]

        for domain in non_scrapable_domains:
            if domain in url.lower():
                return False

        return True

    def get_urls(self, first_name: str, last_name: str, company: str) -> List[str]:
        """
        v3.1: Parallélisé pour -75% de temps (20s → 5s)
        Exécute toutes les requêtes Serper en parallèle avec ThreadPoolExecutor
        """
        start_time = time.time()
        full_name = f"{first_name} {last_name}"
        last_name_only = last_name
        linkedin_slug = f"{first_name.lower()}-{last_name.lower()}".replace(' ', '-')

        scrapable_urls = []
        linkedin_profiles = []

        # ========== PHASE 1: Préparer TOUTES les requêtes (batching) ==========
        queries_batch = []

        # Query 1: Recherche générale
        queries_batch.append(('general', f'{full_name} {company}', 50, 'search'))

        # Query 2: Google News
        queries_batch.append(('news', f'{full_name} {company}', 30, 'news'))

        # Query 3: Twitter/X
        queries_batch.append(('twitter', f'site:twitter.com OR site:x.com "{full_name}" {company}', 10, 'search'))

        # Query 4: Sites officiels français
        queries_batch.extend([
            ('legifrance', f'site:legifrance.gouv.fr "{full_name}" OR "{last_name_only}"', 10, 'search'),
            ('infogreffe', f'site:infogreffe.fr "{full_name}" OR "{company}"', 10, 'search'),
            ('societe', f'site:societe.com "{company}"', 10, 'search'),
            ('verif', f'site:verif.com "{company}"', 10, 'search'),
        ])

        # Query 5: Recherches complémentaires
        queries_batch.extend([
            ('roles', f'{full_name} {company} (CEO OR CTO OR CFO OR Director OR Manager OR Président OR Gérant)', 20, 'search'),
            ('media', f'"{full_name}" interview OR article OR tribune', 15, 'search'),
            ('team', f'{company} "{last_name_only}" équipe OR team OR about', 15, 'search'),
        ])

        # Query 6: LinkedIn Posts & Activity
        queries_batch.extend([
            ('linkedin_posts', f'site:linkedin.com/posts/{first_name.lower()}-{last_name.lower()}', 20, 'search'),
            ('linkedin_activity', f'site:linkedin.com/in/{linkedin_slug}/recent-activity', 15, 'search'),
            ('linkedin_engagement', f'site:linkedin.com "{full_name}" (shared OR posted OR commented)', 15, 'search'),
            ('linkedin_company', f'site:linkedin.com "{full_name}" {company} activity', 10, 'search'),
        ])

        # Query 7: Recherches spécialisées
        queries_batch.extend([
            ('github', f'site:github.com "{full_name}" OR "{last_name_only}"', 10, 'search'),
            ('podcasts', f'"{full_name}" podcast OR conférence OR talk OR webinar', 10, 'search'),
            ('patents', f'site:patents.google.com "{full_name}"', 5, 'search'),
            ('publications', f'"{full_name}" {company} publication OR recherche OR étude', 10, 'search'),
            ('tech_media', f'"{full_name}" TechCrunch OR Maddyness OR FrenchWeb OR LesEchos', 10, 'search'),
        ])

        # ========== PHASE 2: Exécuter TOUTES les requêtes en PARALLÈLE ==========
        print(f"[Serper] 🚀 Lancement de {len(queries_batch)} requêtes en parallèle...")

        results_map = {}
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_query = {
                executor.submit(
                    self.search_news if query_type == 'news' else self.search_google,
                    query,
                    num
                ): (label, query_type)
                for label, query, num, query_type in queries_batch
            }

            for future in as_completed(future_to_query):
                label, query_type = future_to_query[future]
                try:
                    result = future.result()
                    if result:
                        results_map[label] = result
                        print(f"[Serper] ✓ {label}: {len(result.get('organic', []) or result.get('news', []))} résultats")
                except Exception as e:
                    print(f"[Serper] ✗ {label} error: {e}")

        parallel_time = time.time() - start_time
        print(f"[Serper] ⚡ Toutes les requêtes terminées en {parallel_time:.1f}s (parallèle)")

        # ========== PHASE 3: Traiter les résultats ==========
        # Query 1: Recherche générale (v3.1: augmenté à 50 résultats)
        results1 = results_map.get('general')

        if results1:
            extracted = self.extract_urls_and_snippets(results1)
            self._store_snippets(extracted, full_name, company)

            for item in extracted:
                if 'linkedin.com' in item['url']:
                    # v3.1: Filtrer les homonymes LinkedIn
                    if self._is_linkedin_url_relevant(item['url'], first_name, last_name):
                        linkedin_profiles.append({
                            'url': item['url'],
                            'snippet': item['snippet'],
                            'title': item['title'],
                            'position': item.get('position', 999)
                        })
                        print(f"[Serper] ✓ LinkedIn found: {item['url']}")
                    else:
                        print(f"[Serper] ✗ LinkedIn homonym rejected: {item['url']}")
                elif item['scrapable']:
                    # v3.1: Filtrer pages Société.com/Verif.com non pertinentes
                    if 'societe.com' in item['url'] or 'verif.com' in item['url']:
                        if not self._is_company_registry_url_relevant(item['url'], company):
                            print(f"[Serper] ✗ Registry rejected (wrong company): {item['url']}")
                            continue
                    scrapable_urls.append(item['url'])

        # Query 2: Recherche Google News API pour articles récents (v3.1: augmenté à 30)
        results_news = results_map.get('news')

        if results_news:
            extracted_news = self.extract_urls_and_snippets(results_news, is_news=True)
            self._store_snippets(extracted_news, full_name, company)

            for item in extracted_news:
                if item['scrapable'] and item['url'] not in scrapable_urls:
                    scrapable_urls.append(item['url'])
                    date_str = f" ({item['date']})" if item.get('date') else ""
                    print(f"[Serper News] ✓ Article found: {item['title'][:60]}{date_str}")

        # Query 3: Recherche Twitter/X pour déclarations publiques (v3.1: augmenté à 10)
        results_twitter = results_map.get('twitter')

        if results_twitter:
            extracted_twitter = self.extract_urls_and_snippets(results_twitter)
            # Les tweets sont traités comme des snippets (pas de scraping direct)
            self._store_snippets(extracted_twitter, full_name, company)

            for item in extracted_twitter:
                if ('twitter.com' in item['url'] or 'x.com' in item['url']) and item['snippet']:
                    # Ajouter les snippets Twitter au cache pour analyse
                    print(f"[Serper] ✓ Twitter/X mention found: {item['url']}")

        # Query 4: Recherche sites officiels français (v3.1: augmenté à 10 résultats)
        official_sites_labels = [
            ('legifrance', 'Légifrance (Justice)'),
            ('infogreffe', 'Infogreffe (Greffe)'),
            ('societe', 'Société.com'),
            ('verif', 'Verif.com'),
        ]

        for label, source_name in official_sites_labels:
            results_official = results_map.get(label)
            if results_official:
                extracted_official = self.extract_urls_and_snippets(results_official)
                self._store_snippets(extracted_official, full_name, company)

                for item in extracted_official:
                    # v3.1: Filtrer les pages Société.com/Verif.com non pertinentes
                    if 'societe.com' in item['url'] or 'verif.com' in item['url']:
                        if not self._is_company_registry_url_relevant(item['url'], company):
                            print(f"[Serper] ✗ {source_name} rejected (wrong company): {item['url']}")
                            continue

                    if item['scrapable'] and item['url'] not in scrapable_urls:
                        scrapable_urls.append(item['url'])
                    if item['snippet']:
                        print(f"[Serper] ✓ {source_name} mention: {item['title'][:50]}")

        # Query 5: Recherches complémentaires pour plus de diversité (v3.1: augmenté)
        additional_labels = ['roles', 'media', 'team']

        for label in additional_labels:
            if len(scrapable_urls) >= 80:  # v3.1: Stop si on a déjà 80 URLs (au lieu de 40)
                break

            results = results_map.get(label)

            if results:
                extracted = self.extract_urls_and_snippets(results)
                self._store_snippets(extracted, full_name, company)

                for item in extracted:
                    if 'linkedin.com' in item['url']:
                        # v3.1: Filtrer les homonymes LinkedIn
                        if self._is_linkedin_url_relevant(item['url'], first_name, last_name):
                            if not any(p['url'] == item['url'] for p in linkedin_profiles):
                                linkedin_profiles.append({
                                    'url': item['url'],
                                    'snippet': item['snippet'],
                                    'title': item['title'],
                                    'position': item.get('position', 999)
                                })
                                print(f"[Serper] ✓ LinkedIn found: {item['url']}")
                        else:
                            print(f"[Serper] ✗ LinkedIn homonym rejected: {item['url']}")
                    elif item['scrapable'] and item['url'] not in scrapable_urls:
                        # v3.1: Filtrer pages Société.com/Verif.com non pertinentes
                        if 'societe.com' in item['url'] or 'verif.com' in item['url']:
                            if not self._is_company_registry_url_relevant(item['url'], company):
                                print(f"[Serper] ✗ Registry rejected (wrong company): {item['url']}")
                                continue
                        scrapable_urls.append(item['url'])

        # Query 6: LinkedIn Posts & Activity (v3.1: NOUVEAU - collecte enrichie)
        # Objectif: Récupérer 10-15 posts LinkedIn avec commentaires visibles dans snippets
        linkedin_activity_labels = [
            ('linkedin_posts', 'LinkedIn Posts'),
            ('linkedin_activity', 'LinkedIn Activity'),
            ('linkedin_engagement', 'LinkedIn Engagement'),
            ('linkedin_company', 'LinkedIn Company Posts'),
        ]

        for label, source_name in linkedin_activity_labels:
            results_linkedin = results_map.get(label)

            if results_linkedin:
                extracted_linkedin = self.extract_urls_and_snippets(results_linkedin)
                self._store_snippets(extracted_linkedin, full_name, company)

                for item in extracted_linkedin:
                    if 'linkedin.com' in item['url']:
                        # v3.1: Filtrer les homonymes LinkedIn
                        if self._is_linkedin_url_relevant(item['url'], first_name, last_name):
                            if not any(p['url'] == item['url'] for p in linkedin_profiles):
                                linkedin_profiles.append({
                                    'url': item['url'],
                                    'snippet': item['snippet'],
                                    'title': item['title'],
                                    'position': item.get('position', 999)
                                })
                                print(f"[Serper] ✓ {source_name}: {item['url']}")
                        else:
                            print(f"[Serper] ✗ {source_name} homonym rejected: {item['url']}")

        # Query 7: Recherches spécialisées (v3.1: NOUVEAU)
        specialized_labels = [
            ('github', 'GitHub'),
            ('podcasts', 'Podcasts/Talks'),
            ('patents', 'Brevets'),
            ('publications', 'Publications'),
            ('tech_media', 'Médias Tech'),
        ]

        for label, source_name in specialized_labels:
            if len(scrapable_urls) >= 100:  # Hard limit à 100 URLs
                break

            results_specialized = results_map.get(label)

            if results_specialized:
                extracted_specialized = self.extract_urls_and_snippets(results_specialized)
                self._store_snippets(extracted_specialized, full_name, company)

                for item in extracted_specialized:
                    if item['scrapable'] and item['url'] not in scrapable_urls:
                        scrapable_urls.append(item['url'])
                    if item['snippet']:
                        print(f"[Serper] ✓ {source_name} mention: {item['title'][:50]}")

        if linkedin_profiles:
            linkedin_profiles.sort(key=lambda x: x['position'])

            combined_content = self._merge_linkedin_profiles(linkedin_profiles, full_name)

            self.linkedin_cache = {
                'urls': [p['url'] for p in linkedin_profiles],
                'combined_snippet': combined_content,
                'count': len(linkedin_profiles)
            }
            print(f"[Serper] ✓ Merged {len(linkedin_profiles)} LinkedIn profile(s)")

        print(f"[Serper] Collected {len(scrapable_urls)} scrapable URLs + LinkedIn profiles: {len(linkedin_profiles)}")
        return scrapable_urls

    def _is_company_registry_url_relevant(self, url: str, company: str) -> bool:
        """
        v3.1: Filtre les pages Société.com/Verif.com pour ne garder que les pages de l'entreprise cible.

        Accepte:
        - ✓ https://www.societe.com/societe/msdev-884571142.html
        - ✓ https://www.verif.com/societe/MSDEV-68d9c5791299230338aeaf2d/

        Rejette:
        - ✗ https://www.societe.com/societe/izers-844443663.html (autre entreprise)
        - ✗ https://www.societe.com/manager/... (page manager générique)
        - ✗ https://www.verif.com/top/activity-sector-... (page liste générique)
        """
        url_lower = url.lower()
        company_normalized = company.lower().replace(' ', '-').replace('é', 'e').replace('è', 'e')

        # Rejeter les pages génériques (listes, managers, tops, etc.)
        generic_patterns = [
            '/manager/',
            '/top/',
            '/activity-sector',
            '/directory/',
            '/search/',
            '/list/',
            '/classement/'
        ]

        for pattern in generic_patterns:
            if pattern in url_lower:
                return False

        # Pour Société.com et Verif.com, vérifier que l'URL contient le nom de l'entreprise
        if 'societe.com' in url_lower or 'verif.com' in url_lower:
            # L'URL doit contenir le nom de l'entreprise dans le slug
            if company_normalized not in url_lower:
                return False

        return True

    def _is_linkedin_url_relevant(self, url: str, first_name: str, last_name: str) -> bool:
        """
        v3.1: Filtre les homonymes LinkedIn en vérifiant que l'URL contient le nom complet.
        Exemples:
        - ✓ https://fr.linkedin.com/in/chris-emerson-kouassi
        - ✗ https://fr.linkedin.com/in/aklade-kouassi-sosthene (autre Kouassi)
        - ✗ https://uk.linkedin.com/in/cjemerson (Chris Emerson différent)
        """
        url_lower = url.lower()

        # Normaliser les noms (enlever accents, lowercase)
        first_normalized = first_name.lower().replace(' ', '-').replace('é', 'e').replace('è', 'e')
        last_normalized = last_name.lower().replace(' ', '-').replace('é', 'e').replace('è', 'e')

        # Vérifier que l'URL contient les deux parties du nom
        # Accepter: /in/prenom-nom, /in/nom-prenom, ou /in/initiale-nom
        has_first = first_normalized in url_lower or first_name[0].lower() in url_lower
        has_last = last_normalized in url_lower

        # L'URL doit contenir au moins le nom de famille
        if not has_last:
            return False

        # Si c'est juste un répertoire (/pub/dir/), on refuse
        if '/pub/dir/' in url_lower or '/directory/' in url_lower:
            return False

        # Pour les noms très communs (ex: "Chris"), exiger aussi le prénom complet
        # pour éviter les homonymes (ex: cjemerson vs chris-emerson-kouassi)
        if len(last_name) < 6 and not has_first:
            return False

        return True

    def _merge_linkedin_profiles(self, profiles: List[Dict], person_name: str) -> str:
        if not profiles:
            return ""

        merged_content = f"# Profils LinkedIn pour {person_name}\n\n"
        merged_content += f"**{len(profiles)} profil(s) trouvé(s)**\n\n"

        for i, profile in enumerate(profiles, 1):
            merged_content += f"## Profil {i}\n\n"
            merged_content += f"**URL:** {profile['url']}\n\n"
            merged_content += f"**Titre:** {profile['title']}\n\n"
            merged_content += f"**Résumé:**\n{profile['snippet']}\n\n"
            merged_content += "---\n\n"

        merged_content += "*Note: Ces informations proviennent des snippets Google Search (LinkedIn bloque le scraping direct).*"

        return merged_content

    def _store_snippets(self, extracted: List[Dict], person_name: str, company: str):
        """
        For now, just for debugging purposes
        """
        linkedin_snippets = []

        for item in extracted:
            if 'linkedin.com' in item['url']:
                linkedin_snippets.append({
                    'snippet': item['snippet'],
                    'title': item['title']
                })

        if linkedin_snippets:
            print(f"[Serper] Found {len(linkedin_snippets)} LinkedIn snippets for {person_name} @ {company}")