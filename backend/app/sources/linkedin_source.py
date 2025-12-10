from typing import List
from app.sources.base_source import BaseSource

class LinkedInSource(BaseSource):
    @classmethod
    def get_name(cls) -> str:
        return "linkedin"

    @classmethod
    def get_description(cls) -> str:
        return "Recherche de profils LinkedIn (taux de succès variable)"

    def get_urls(self, first_name: str, last_name: str, company: str) -> List[str]:
        """
        Returns LinkedIn URLs to scrape including profile and activity pages.

        With premium mode (MAX_TOTAL_SCRAPES=50), includes:
        - Main profile page
        - Recent activity pages (for post analysis)
        - Detail activity pages (for deeper engagement analysis)
        """
        urls = []

        # Base profile URL
        potential_slug = f"{first_name.lower()}-{last_name.lower()}"
        base_url = f"https://www.linkedin.com/in/{potential_slug}"

        # Main profile
        urls.append(base_url)

        # Activity pages for LinkedIn post analysis (v3.1 feature)
        # These pages contain recent posts, articles, and engagement data
        urls.append(f"{base_url}/recent-activity/all/")
        urls.append(f"{base_url}/recent-activity/shares/")
        urls.append(f"{base_url}/recent-activity/articles/")
        urls.append(f"{base_url}/detail/recent-activity/")

        # Alternative profile URLs (in case primary slug doesn't match)
        urls.append(f"https://www.linkedin.com/in/{potential_slug}-1")
        urls.append(f"https://www.linkedin.com/in/{potential_slug}-2")

        # Note: Les URLs de recherche LinkedIn sont désactivées car
        # elles ne fonctionnent pas bien avec Firecrawl
        # search_query = self.build_search_query(full_name, company)
        # linkedin_search = f"https://www.linkedin.com/search/results/people/?keywords={search_query}"

        # Return first 5 URLs (main profile + 4 activity pages)
        # With MAX_TOTAL_SCRAPES=50, we have budget for comprehensive LinkedIn analysis
        return urls[:5]