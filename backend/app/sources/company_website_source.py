from typing import List
from app.sources.base_source import BaseSource

class CompanyWebsiteSource(BaseSource):
    @classmethod
    def get_name(cls) -> str:
        return "company_website"

    @classmethod
    def get_description(cls) -> str:
        return "Pages web d'entreprise (équipe, à propos, leadership)"

    def get_urls(self, first_name: str, last_name: str, company: str) -> List[str]:
        urls = []
        domains = self._guess_company_domains(company)

        for domain in domains:
            common_paths = [
                "/about",
                "/team",
                "/leadership",
                "/equipe",
                "/qui-sommes-nous",
            ]

            for path in common_paths:
                urls.append(f"https://www.{domain}{path}")

        return urls

    def _guess_company_domains(self, company: str) -> List[str]:
        clean_name = company.lower().replace(" ", "").replace("-", "")

        known_domains_map = {
            "microsoft": ["microsoft.com"],
            "google": ["google.com", "google.fr"],
            "apple": ["apple.com"],
            "meta": ["about.meta.com"],
            "facebook": ["about.meta.com"],
            "amazon": ["amazon.com", "amazon.fr"],
            "totalenergies": ["totalenergies.com", "totalenergies.fr"],
            "total": ["totalenergies.com", "totalenergies.fr"],
            "netflix": ["netflix.com"],
            "spotify": ["spotify.com"],
            "airbnb": ["airbnb.com", "airbnb.fr"],
            "uber": ["uber.com"],
            "bnpparibas": ["bnpparibas.com", "bnpparibas.fr"],
            "societegenerale": ["societegenerale.com", "societegenerale.fr"],
            "orange": ["orange.com", "orange.fr"],
            "renault": ["renault.com", "renault.fr"],
            "peugeot": ["peugeot.com", "peugeot.fr"],
            "carrefour": ["carrefour.com", "carrefour.fr"],
            "airfrance": ["airfrance.com", "airfrance.fr"],
            "sncf": ["sncf.com", "sncf.fr"],
        }

        if clean_name in known_domains_map:
            return known_domains_map[clean_name]
        else:
            return [f"{clean_name}.com", f"{clean_name}.fr"]
