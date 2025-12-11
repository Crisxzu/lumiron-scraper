from typing import Dict
from app.services.scraper_service import ScraperService
from app.services.llm_service import LLMService
from app.services.cache_service import CacheService

class ProfileService:
    def __init__(self):
        self.scraper = ScraperService()
        self.llm = LLMService()
        self.cache = CacheService()

    def get_person_profile(self, first_name: str, last_name: str, company: str, force_refresh: bool = False) -> Dict:
        try:
            print(f"\n[ProfileService] Starting profile collection for {first_name} {last_name}")
            cached_result = self.cache.get(first_name, last_name, company, force_refresh=force_refresh)

            if cached_result:
                print(f"[ProfileService] ✓ Using cached profile (age: {cached_result['cache_age_seconds']}s)")
                return {
                    "success": True,
                    "data": cached_result['profile_data'],
                    "cached": True,
                    "cache_age_seconds": cached_result['cache_age_seconds'],
                    "cache_created_at": cached_result['cache_created_at']
                }

            print(f"[ProfileService] Cache miss or force refresh, scraping data...")
            scraped_data = self.scraper.scrape_person_data(first_name, last_name, company)

            scraped_content_list = [
                data for data in scraped_data["scraped_content"]
                if data.get('success')
            ]

            if not scraped_content_list:
                raise ValueError("No valid data was scraped. Unable to generate profile.")

            print(f"[ProfileService] Analyzing {len(scraped_content_list)} scraped content(s) with OpenAI")
            profile_data = self.llm.analyze_profile(
                first_name,
                last_name,
                company,
                scraped_content_list,
                scraped_data.get("pappers_data"),
                scraped_data.get("dvf_data"),
                scraped_data.get("hatvp_data"),
                scraped_data.get("linkedin_urls", [])  # v3.1: Pass LinkedIn URLs for traceability
            )

            # v3.1: Ajouter sources web + URLs LinkedIn analysées
            sources = scraped_data.get("sources", [])

            # Extraire URLs LinkedIn depuis linkedin_activity_analysis
            if "linkedin_activity_analysis" in profile_data:
                linkedin_urls = profile_data["linkedin_activity_analysis"].get("linkedin_urls_analyzed", [])
                if linkedin_urls:
                    # Ajouter URLs LinkedIn aux sources (déduplication)
                    sources.extend([url for url in linkedin_urls if url not in sources])

            profile_data["sources"] = sources

            self.cache.set(first_name, last_name, company, scraped_data, profile_data)

            print(f"[ProfileService] ✓ Profile successfully generated and cached")

            return {
                "success": True,
                "data": profile_data,
                "cached": False
            }

        except ValueError as e:
            print(f"[ProfileService] ✗ Validation error: {e}")
            return {
                "success": False,
                "error": "Configuration ou données invalides",
                "message": str(e)
            }

        except Exception as e:
            print(f"[ProfileService] ✗ Unexpected error: {e}")
            return {
                "success": False,
                "error": "Erreur lors du traitement",
                "message": str(e)
            }
