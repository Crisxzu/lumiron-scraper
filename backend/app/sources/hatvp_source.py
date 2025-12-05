"""
Source HATVP - Haute Autorité pour la Transparence de la Vie Publique
Détection des Personnes Politiquement Exposées (PPE)
Alternative gratuite à Pappers personne_politiquement_exposee (1 crédit)
"""

from typing import List, Dict, Optional
from app.sources.base_source import BaseSource


class HAVTPSource(BaseSource):
    """
    Source HATVP - Haute Autorité pour la Transparence de la Vie Publique
    Détecte si une personne est politiquement exposée (PPE)

    CRITIQUE pour Due Diligence bancaire et financière:
    - Obligations de déclaration d'intérêts
    - Conformité LCB-FT (Lutte Contre le Blanchiment)
    - Risque de conflit d'intérêts

    URL : https://hatvp.fr
    Accès : Gratuit via Serper (pas d'API publique)
    """

    @classmethod
    def get_name(cls) -> str:
        return "hatvp_ppe"

    @classmethod
    def get_description(cls) -> str:
        return "Personnes Politiquement Exposées - HATVP"

    def get_urls(self, first_name: str, last_name: str, company: str) -> List[str]:
        """
        Recherche HATVP via Serper pour détecter PPE
        Pas d'API publique, on utilise Google Search
        """
        from app.sources.serper_search_source import SerperSearchSource

        print("[HATVP] Searching for politically exposed person status")

        serper = SerperSearchSource()
        full_name = f"{first_name} {last_name}"
        hatvp_snippets = []

        # Query 1: Site HATVP direct
        query_hatvp = f'site:hatvp.fr "{full_name}"'
        results = serper.search_google(query_hatvp, num_results=5)

        if results:
            extracted = serper.extract_urls_and_snippets(results)
            for item in extracted:
                if item['snippet']:
                    hatvp_snippets.append({
                        'url': item['url'],
                        'snippet': item['snippet'],
                        'title': item['title'],
                        'source': 'HATVP'
                    })
                    print(f"[HATVP] ✓ PPE mention found: {item['title'][:50]}")

        # Query 2: Déclarations d'intérêts (élargi)
        query_declaration = f'"{full_name}" ("déclaration d\'intérêts" OR "déclaration de patrimoine" OR "élu" OR "mandat électif" OR "fonction publique")'
        results_decl = serper.search_google(query_declaration, num_results=5)

        if results_decl:
            extracted_decl = serper.extract_urls_and_snippets(results_decl)
            for item in extracted_decl:
                if item['snippet'] and 'hatvp' in item['url'].lower() or 'élu' in item['snippet'].lower() or 'mandat' in item['snippet'].lower():
                    hatvp_snippets.append({
                        'url': item['url'],
                        'snippet': item['snippet'],
                        'title': item['title'],
                        'source': 'Public declaration'
                    })
                    print(f"[HATVP] ✓ Political activity mention: {item['title'][:50]}")

        # Query 3: Assemblée Nationale / Sénat
        query_parlement = f'site:assemblee-nationale.fr OR site:senat.fr "{full_name}"'
        results_parl = serper.search_google(query_parlement, num_results=3)

        if results_parl:
            extracted_parl = serper.extract_urls_and_snippets(results_parl)
            for item in extracted_parl:
                if item['snippet']:
                    hatvp_snippets.append({
                        'url': item['url'],
                        'snippet': item['snippet'],
                        'title': item['title'],
                        'source': 'Parliament'
                    })
                    print(f"[HATVP] ✓ Parliament mention: {item['title'][:50]}")

        # Stocker les résultats
        if hatvp_snippets:
            self.hatvp_cache = {
                'snippets': hatvp_snippets,
                'count': len(hatvp_snippets),
                'full_name': full_name,
                'ppe_detected': True
            }
            print(f"[HATVP] 🚨 PPE DETECTED: {len(hatvp_snippets)} mention(s) - HIGH RISK")
        else:
            self.hatvp_cache = {
                'snippets': [],
                'count': 0,
                'full_name': full_name,
                'ppe_detected': False
            }
            print(f"[HATVP] ✓ No PPE status detected for {full_name}")

        # Retourner URL fictive si PPE détecté
        return [f"hatvp://ppe/{full_name}"] if hatvp_snippets else []

    def get_cached_data(self) -> Optional[Dict]:
        """Récupère les données HATVP pour que le scraper puisse les utiliser"""
        return getattr(self, 'hatvp_cache', None)
