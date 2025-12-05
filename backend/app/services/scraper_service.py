import os
import time
import requests
from typing import List, Dict, Optional
from firecrawl import Firecrawl
from app.sources import get_all_sources
from app.utils.url_validator import filter_accessible_urls, get_realistic_headers

class ScraperService:
    def __init__(self):
        self.firecrawl_api_key = os.getenv('FIRECRAWL_API_KEY')
        self.firecrawl = None
        if self.firecrawl_api_key:
            try:
                self.firecrawl = Firecrawl(api_key=self.firecrawl_api_key)
            except Exception as e:
                print(f"Warning: Firecrawl initialization failed: {e}")

        # ScraperAPI fallback (optional)
        self.scraperapi_key = os.getenv('SCRAPERAPI_KEY')
        if self.scraperapi_key:
            print(f"[ScraperAPI] ✓ Enabled as fallback for blocked URLs")

        self.sources = get_all_sources()
        print(f"Loaded {len(self.sources)} source modules: {[s.get_name() for s in self.sources]}")

    def collect_urls_from_sources(self, first_name: str, last_name: str, company: str) -> Dict[str, List[str]]:        
        urls_by_source = {}

        for source in self.sources:
            source_name = source.get_name()
            try:
                urls = source.get_urls(first_name, last_name, company)
                urls_by_source[source_name] = urls
                print(f"Source '{source_name}': {len(urls)} URLs generated")
            except Exception as e:
                print(f"Error getting URLs from source '{source_name}': {e}")
                urls_by_source[source_name] = []

        return urls_by_source

    def scrape_with_scraperapi(self, url: str) -> Optional[str]:
        """
        Fallback scraper using ScraperAPI for sites that block Firecrawl
        ScraperAPI bypasses anti-bot protection (Cloudflare, Datadome, etc.)
        """
        if not self.scraperapi_key:
            return None

        try:
            print(f"[ScraperAPI] Attempting fallback scraping: {url}")

            # ScraperAPI endpoint
            api_url = "https://api.scraperapi.com"
            params = {
                'api_key': self.scraperapi_key,
                'url': url,
                'render': 'false',  # false = plus rapide, true = JS rendering
            }

            response = requests.get(api_url, params=params, timeout=30)

            if response.status_code == 200:
                content = response.text
                print(f"[ScraperAPI] ✓ Success: {len(content)} chars")
                return content
            else:
                print(f"[ScraperAPI] ✗ Error {response.status_code}")
                return None

        except Exception as e:
            print(f"[ScraperAPI] ✗ Exception: {str(e)}")
            return None

    def scrape_with_firecrawl(self, url: str, use_fallback: bool = True) -> Optional[Dict]:
        """
        Scrape avec Firecrawl, fallback vers ScraperAPI si 403/blocked
        """
        if not self.firecrawl:
            raise ValueError("Firecrawl API key not configured")

        try:
            print(f"[Firecrawl] Scraping: {url}")
            result = self.firecrawl.scrape(
                url,
                formats=['markdown', 'html']
            )

            if result and (result.markdown or result.html):
                print(f"[Firecrawl] ✓ Success: {len(result.markdown or '')} chars")
                return result
            else:
                print(f"[Firecrawl] ✗ Empty result")

                # Fallback vers ScraperAPI si disponible
                if use_fallback and self.scraperapi_key:
                    print(f"[Fallback] Trying ScraperAPI for {url}")
                    scraperapi_content = self.scrape_with_scraperapi(url)
                    if scraperapi_content:
                        # Convertir en format compatible Firecrawl
                        return type('obj', (object,), {
                            'markdown': scraperapi_content[:10000],  # Limiter à 10k chars
                            'html': None
                        })

                return None

        except Exception as e:
            error_msg = str(e).lower()
            print(f"[Firecrawl] ✗ Error: {str(e)}")

            # Si rate limit exceeded, extraire le délai et retourner None (sera géré par la boucle)
            if 'rate limit' in error_msg:
                # On ne retry pas ici, on laisse la boucle gérer avec le délai global
                print(f"[Firecrawl] ⚠ Rate limit hit, will be handled by rate limiting logic")
                return None

            # Si erreur 403/blocked, essayer ScraperAPI
            if use_fallback and self.scraperapi_key and ('403' in error_msg or 'forbidden' in error_msg or 'blocked' in error_msg):
                print(f"[Fallback] Firecrawl blocked (403), trying ScraperAPI")
                scraperapi_content = self.scrape_with_scraperapi(url)
                if scraperapi_content:
                    return type('obj', (object,), {
                        'markdown': scraperapi_content[:10000],
                        'html': None
                    })

            return None

    def scrape_person_data(self, first_name: str, last_name: str, company: str) -> Dict[str, any]:
        if not self.firecrawl:
            raise ValueError("Firecrawl API key not configured. Please set FIRECRAWL_API_KEY in .env")

        print(f"\n=== Scraping Profile: {first_name} {last_name} @ {company} ===")
        urls_by_source = self.collect_urls_from_sources(first_name, last_name, company)

        all_urls = []
        url_to_source = {}

        for source_name, urls in urls_by_source.items():
            for url in urls:
                all_urls.append(url)
                url_to_source[url] = source_name

        print(f"\n=== URL Validation ===")
        accessible_urls = filter_accessible_urls(all_urls, timeout=3, max_concurrent=50)

        if not accessible_urls:
            raise Exception(
                "No accessible URLs found. "
                "All URLs either timed out or returned errors. "
                "This could indicate:\n"
                "1) Network connectivity issues\n"
                "2) All URLs are invalid/dead\n"
                "3) Sites are blocking requests"
            )

        linkedin_data = None
        pappers_data = None
        dvf_data = None
        hatvp_data = None

        for source in self.sources:
            if hasattr(source, 'linkedin_cache') and source.linkedin_cache:
                linkedin_data = source.linkedin_cache
                print(f"[LinkedIn] ✓ Using cached LinkedIn data: {linkedin_data['urls']}")

            if hasattr(source, 'get_cached_data'):
                cached = source.get_cached_data()
                if cached:
                    source_name = source.get_name()
                    if source_name == 'pappers_legal':
                        pappers_data = cached
                        print(f"[Pappers] ✓ Legal data collected for {cached.get('full_name')}")
                    elif source_name == 'dvf_immobilier':
                        dvf_data = cached
                        print(f"[DVF] ✓ Real estate data collected: {cached.get('count')} mention(s)")
                    elif source_name == 'hatvp_ppe':
                        hatvp_data = cached
                        ppe_status = "DETECTED ⚠" if cached.get('ppe_detected') else "Not detected"
                        print(f"[HATVP] ✓ PPE status: {ppe_status}")

        collected_data = {
            "urls_by_source": urls_by_source,
            "accessible_urls": accessible_urls,
            "scraped_content": [],
            "sources": [],
            "linkedin_data": linkedin_data,
            "pappers_data": pappers_data,
            "dvf_data": dvf_data,
            "hatvp_data": hatvp_data,
            "stats": {
                "total_urls_generated": len(all_urls),
                "accessible": len(accessible_urls),
                "attempted": 0,
                "successful": 0,
                "failed": 0
            }
        }

        max_total_scrapes = int(os.getenv("MAX_TOTAL_SCRAPES", '3'))  # Maximum 3 scrapes

        # Firecrawl rate limit: 10 req/min (Free tier)
        # Pour être safe: 1 requête toutes les 6 secondes
        rate_limit_delay = 6.5  # secondes entre chaque scrape

        successful_scrapes = 0
        scrape_start_time = time.time()

        for idx, url in enumerate(accessible_urls[:max_total_scrapes]):
            if successful_scrapes >= max_total_scrapes:
                break

            # Rate limiting: attendre entre chaque scrape (sauf le premier)
            if idx > 0:
                elapsed = time.time() - scrape_start_time
                expected_time = idx * rate_limit_delay
                if elapsed < expected_time:
                    wait_time = expected_time - elapsed
                    print(f"[Rate Limit] Waiting {wait_time:.1f}s before next scrape ({idx+1}/{min(len(accessible_urls), max_total_scrapes)})...")
                    time.sleep(wait_time)

            collected_data["stats"]["attempted"] += 1

            source_name = url_to_source.get(url, "unknown")

            content = self.scrape_with_firecrawl(url)

            if content:
                content_text = content.markdown if content.markdown is not None else ""

                # Valider que le contenu est exploitable
                if len(content_text.strip()) > 100:
                    collected_data["scraped_content"].append({
                        "source": source_name,
                        "url": url,
                        "content": content_text[:5000],  # Limiter taille
                        "success": True
                    })
                    collected_data["sources"].append(url)
                    collected_data["stats"]["successful"] += 1
                    successful_scrapes += 1
                else:
                    print(f"[Firecrawl] ⚠ Content too short, skipping")
                    collected_data["stats"]["failed"] += 1
            else:
                collected_data["stats"]["failed"] += 1

        # Étape 3: Ajouter les données LinkedIn fusionnées si disponibles
        if linkedin_data:
            # Le nouveau format contient plusieurs profils fusionnés
            collected_data["scraped_content"].append({
                "source": "linkedin_snippets",
                "url": ", ".join(linkedin_data['urls']),  # Toutes les URLs LinkedIn
                "content": linkedin_data['combined_snippet'],  # Contenu fusionné
                "success": True
            })
            # Ajouter toutes les URLs LinkedIn aux sources
            collected_data["sources"].extend(linkedin_data['urls'])
            collected_data["stats"]["successful"] += 1
            print(f"[LinkedIn] ✓ Added {linkedin_data['count']} merged LinkedIn profile(s) to scraped content")

        print(f"\n=== Scraping Stats ===")
        print(f"Attempted: {collected_data['stats']['attempted']}")
        print(f"Successful: {collected_data['stats']['successful']}")
        print(f"Failed: {collected_data['stats']['failed']}")

        if collected_data["stats"]["successful"] == 0:
            raise Exception(
                "Failed to scrape any valid data. "
                "This could be due to: "
                "1) Firecrawl rate limits "
                "2) Invalid URLs "
                "3) Sites blocking scraping. "
                "Please try again in a few moments."
            )

        return collected_data