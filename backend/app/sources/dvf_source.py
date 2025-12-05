"""
Source DVF - Demandes de Valeurs Foncières (Transactions immobilières)
API gratuite data.gouv.fr pour détecter le patrimoine immobilier
Alternative gratuite à Pappers parcelles_detenues (15 crédits)
"""

from typing import List, Dict, Optional
from app.sources.base_source import BaseSource


class DVFSource(BaseSource):
    """
    Source DVF (Demandes de Valeurs Foncières)
    Base de données publique des transactions immobilières en France

    Stratégie: DVF API nécessite adresse exacte, donc on utilise Serper
    pour détecter mentions de patrimoine immobilier dans la presse/web

    API : https://app.dvf.etalab.gouv.fr/api (nécessite adresse)
    Alternative : Recherche Google via Serper pour mentions immobilières
    """

    @classmethod
    def get_name(cls) -> str:
        return "dvf_immobilier"

    @classmethod
    def get_description(cls) -> str:
        return "Transactions immobilières publiques (DVF - data.gouv.fr)"

    def get_urls(self, first_name: str, last_name: str, company: str) -> List[str]:
        """
        DVF API nécessite adresse exacte, pas de recherche par nom
        On utilise Serper pour détecter mentions immobilières dans la presse
        """
        from app.sources.serper_search_source import SerperSearchSource

        print("[DVF] Searching real estate mentions via Serper")

        serper = SerperSearchSource()
        full_name = f"{first_name} {last_name}"
        dvf_snippets = []

        # Query 1: Mentions immobilières générales
        query_real_estate = f'"{full_name}" (immobilier OR "achat immobilier" OR "vente immobilier" OR propriétaire OR patrimoine)'
        results = serper.search_google(query_real_estate, num_results=5)

        if results:
            extracted = serper.extract_urls_and_snippets(results)
            for item in extracted:
                if item['snippet']:
                    dvf_snippets.append({
                        'url': item['url'],
                        'snippet': item['snippet'],
                        'title': item['title']
                    })
                    print(f"[DVF] ✓ Real estate mention: {item['title'][:50]}")

        # Query 2: Site DVF direct (si mention dans presse)
        query_dvf_site = f'site:app.dvf.etalab.gouv.fr "{full_name}" OR "{last_name}"'
        results_dvf = serper.search_google(query_dvf_site, num_results=3)

        if results_dvf:
            extracted_dvf = serper.extract_urls_and_snippets(results_dvf)
            for item in extracted_dvf:
                if item['snippet']:
                    dvf_snippets.append({
                        'url': item['url'],
                        'snippet': item['snippet'],
                        'title': item['title']
                    })
                    print(f"[DVF] ✓ DVF direct mention: {item['title'][:50]}")

        # Stocker les snippets pour analyse
        if dvf_snippets:
            self.dvf_cache = {
                'snippets': dvf_snippets,
                'count': len(dvf_snippets),
                'full_name': full_name
            }
            print(f"[DVF] ✓ Collected {len(dvf_snippets)} real estate mention(s)")
        else:
            print(f"[DVF] ℹ No real estate mentions found for {full_name}")

        # Retourner URL fictive si données trouvées
        return [f"dvf://real-estate/{full_name}"] if dvf_snippets else []

    def get_cached_data(self) -> Optional[Dict]:
        """Récupère les snippets DVF pour que le scraper puisse les utiliser"""
        return getattr(self, 'dvf_cache', None)
