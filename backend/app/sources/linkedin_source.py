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
        urls = []

        potential_slug = f"{first_name.lower()}-{last_name.lower()}"
        direct_url = f"https://www.linkedin.com/in/{potential_slug}"
        urls.append(direct_url)

        urls.append(f"https://www.linkedin.com/in/{potential_slug}-1")
        urls.append(f"https://www.linkedin.com/in/{potential_slug}-2")

        # Note: Les URLs de recherche LinkedIn sont désactivées car
        # elles ne fonctionnent pas bien avec Firecrawl
        # search_query = self.build_search_query(full_name, company)
        # linkedin_search = f"https://www.linkedin.com/search/results/people/?keywords={search_query}"

        return urls[:1]  # Limiter à 1 URL pour éviter les coûts inutiles