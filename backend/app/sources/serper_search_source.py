import os
import requests
from typing import List, Dict, Optional
from app.sources.base_source import BaseSource

class SerperSearchSource(BaseSource):    
    def __init__(self):
        self.api_key = os.getenv('SERPER_API_KEY')
        self.base_url = "https://google.serper.dev/search"

    @classmethod
    def get_name(cls) -> str:
        return "serper_search"

    @classmethod
    def get_description(cls) -> str:
        return "Recherche Google via Serper API (avec snippets)"

    def search_google(self, query: str, num_results: int = 5) -> Optional[Dict]:        
        if not self.api_key:
            print("[Serper] API key not configured, skipping")
            return None

        try:
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }

            payload = {
                'q': query,
                'num': num_results,
                'gl': 'fr',
            }

            print(f"[Serper] Searching: {query}")
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                print(f"[Serper] ✓ Found {len(data.get('organic', []))} results")
                return data
            else:
                print(f"[Serper] ✗ Error {response.status_code}: {response.text}")
                return None

        except Exception as e:
            print(f"[Serper] ✗ Exception: {e}")
            return None

    def extract_urls_and_snippets(self, search_results: Dict) -> List[Dict]:        
        extracted = []

        organic_results = search_results.get('organic', [])

        for result in organic_results:
            url = result.get('link')
            snippet = result.get('snippet', '')
            title = result.get('title', '')

            if url:
                extracted.append({
                    'url': url,
                    'snippet': snippet,
                    'title': title,
                    'position': result.get('position', 999),
                    'scrapable': self._is_url_scrapable(url)
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
        full_name = f"{first_name} {last_name}"
        scrapable_urls = []
        linkedin_profiles = []

        query1 = f'{full_name} {company}'
        results1 = self.search_google(query1, num_results=10)

        if results1:
            extracted = self.extract_urls_and_snippets(results1)

            self._store_snippets(extracted, full_name, company)

            for item in extracted:
                if 'linkedin.com' in item['url']:
                    linkedin_profiles.append({
                        'url': item['url'],
                        'snippet': item['snippet'],
                        'title': item['title'],
                        'position': item.get('position', 999)
                    })
                    print(f"[Serper] ✓ LinkedIn found: {item['url']}")
                elif item['scrapable']:
                    scrapable_urls.append(item['url'])

        if len(scrapable_urls) < 2:
            query2 = f'{full_name} {company} (CEO OR CTO OR CFO OR Director OR Manager)'
            results2 = self.search_google(query2, num_results=3)

            if results2:
                extracted = self.extract_urls_and_snippets(results2)
                self._store_snippets(extracted, full_name, company)

                for item in extracted:
                    if 'linkedin.com' in item['url']:
                        if not any(p['url'] == item['url'] for p in linkedin_profiles):
                            linkedin_profiles.append({
                                'url': item['url'],
                                'snippet': item['snippet'],
                                'title': item['title'],
                                'position': item.get('position', 999)
                            })
                            print(f"[Serper] ✓ LinkedIn found: {item['url']}")
                    elif item['scrapable'] and item['url'] not in scrapable_urls:
                        scrapable_urls.append(item['url'])

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