import os
from typing import List, Dict, Optional
from firecrawl import Firecrawl
from app.sources import get_all_sources
from app.utils.url_validator import filter_accessible_urls

class ScraperService:
    def __init__(self):
        self.firecrawl_api_key = os.getenv('FIRECRAWL_API_KEY')
        self.firecrawl = None
        if self.firecrawl_api_key:
            try:
                self.firecrawl = Firecrawl(api_key=self.firecrawl_api_key)
            except Exception as e:
                print(f"Warning: Firecrawl initialization failed: {e}")

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

    def scrape_with_firecrawl(self, url: str) -> Optional[Dict]:
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
                return None

        except Exception as e:
            print(f"[Firecrawl] ✗ Error: {str(e)}")
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
        accessible_urls = filter_accessible_urls(all_urls, timeout=3, max_concurrent=20)

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
        for source in self.sources:
            if hasattr(source, 'linkedin_cache') and source.linkedin_cache:
                linkedin_data = source.linkedin_cache
                print(f"[LinkedIn] ✓ Using cached LinkedIn data: {linkedin_data['urls']}")
                break

        collected_data = {
            "urls_by_source": urls_by_source,
            "accessible_urls": accessible_urls,
            "scraped_content": [],
            "sources": [],
            "linkedin_data": linkedin_data,
            "stats": {
                "total_urls_generated": len(all_urls),
                "accessible": len(accessible_urls),
                "attempted": 0,
                "successful": 0,
                "failed": 0
            }
        }

        max_total_scrapes = int(os.getenv("MAX_TOTAL_SCRAPES", '3'))  # Maximum 3 scrapes

        successful_scrapes = 0

        for url in accessible_urls[:max_total_scrapes]:
            if successful_scrapes >= max_total_scrapes:
                break

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