"""
Source Pappers - Intelligence économique et légale (France)
Récupère les informations légales d'une entreprise et ses dirigeants
API: https://www.pappers.fr/api/documentation
"""

from typing import List, Dict, Optional
import requests
import os
from app.sources.base_source import BaseSource


class PappersSource(BaseSource):
    """
    Source Pappers pour enrichissement légal et économique
    Stratégie: On économise les crédits en ne recherchant que si entreprise fournie
    On récupère les 3 premiers résultats pour plus de contexte
    """

    API_BASE_URL = "https://api.pappers.fr/v2"

    @classmethod
    def get_name(cls) -> str:
        return "pappers_legal"

    @classmethod
    def get_description(cls) -> str:
        return "Données légales et économiques des entreprises (Pappers)"

    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('PAPPERS_API_KEY')
        if not self.api_key:
            print("[Pappers] ⚠ API key not configured, source will be skipped")

        # Configuration du mode (light, medium, full)
        self.mode = os.getenv('PAPPERS_MODE', 'light').lower()
        self.include_decisions = os.getenv('PAPPERS_INCLUDE_DECISIONS', 'false').lower() == 'true'
        self.include_parcelles = os.getenv('PAPPERS_INCLUDE_PARCELLES', 'false').lower() == 'true'
        self.include_observations = os.getenv('PAPPERS_INCLUDE_OBSERVATIONS', 'false').lower() == 'true'
        self.include_entreprises_dirigees = os.getenv('PAPPERS_INCLUDE_ENTREPRISES_DIRIGEES', 'true').lower() == 'true'
        self.include_bodacc_person = os.getenv('PAPPERS_INCLUDE_BODACC_PERSON', 'true').lower() == 'true'

        self.pappers_data = None  # Cache pour éviter multiple appels

        # Log de la configuration
        if self.api_key:
            print(f"[Pappers] Mode: {self.mode} | Decisions: {self.include_decisions} | Parcelles: {self.include_parcelles} | BODACC: {self.include_bodacc_person}")

    def get_urls(self, first_name: str, last_name: str, company: str) -> List[str]:
        """
        Pappers ne fournit pas d'URLs à scraper mais des données API
        On retourne une URL fictive pour signaler qu'on a des données
        """
        if not self.api_key:
            print("[Pappers] ⚠ Skipped (no API key)")
            return []

        if not company:
            print("[Pappers] ⚠ Skipped (no company name provided)")
            return []

        # Recherche des entreprises (3 premiers résultats)
        companies_data = self._search_companies(company, first_name, last_name)
        if not companies_data:
            print(f"[Pappers] ✗ No companies found for: {company}")
            return []

        # Stocker toutes les données
        self.pappers_data = {
            'companies': companies_data,
            'full_name': f"{first_name} {last_name}",
            'search_query': company,
            'bodacc_person': getattr(self, 'bodacc_person_cache', None)  # Ajouter les publications BODACC de la personne
        }

        print(f"[Pappers] ✓ Collected data for {len(companies_data)} compan{'y' if len(companies_data)==1 else 'ies'}")

        # Log des publications BODACC si trouvées
        bodacc_data = getattr(self, 'bodacc_person_cache', None)
        if bodacc_data:
            print(f"[Pappers] ✓ + {bodacc_data.get('total', 0)} BODACC publication(s) for {first_name} {last_name}")

        # Calcul et log du coût total
        total_credits = self._calculate_total_credits(len(companies_data))
        print(f"[Pappers] 💰 Estimated total cost: ~{total_credits} credits")

        # Retourner une URL fictive pour signaler qu'on a des données
        return [f"pappers://legal-data/{company}"]

    def _search_companies(self, company_name: str, first_name: str, last_name: str) -> List[Dict]:
        """Recherche les 3 premières entreprises correspondantes et enrichit les données"""
        try:
            url = f"{self.API_BASE_URL}/recherche"
            headers = {'api-key': self.api_key}
            params = {
                'q': company_name,
                'bases': 'entreprises',
                'precision': 'standard',
                'par_page': 3  # Les 3 premiers résultats
            }

            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            companies = []
            if data.get('resultats'):
                for company in data['resultats']:
                    # Enrichir chaque entreprise avec détails économiques
                    siren = company.get('siren')
                    enriched_company = {
                        'nom_entreprise': company.get('nom_entreprise'),
                        'siren': siren,
                        'siege': company.get('siege', {}),
                        'representants': company.get('representants', []),
                    }

                    # Chercher la personne parmi les représentants
                    person_mandates = self._find_person_in_representants(
                        first_name, last_name, company.get('representants', [])
                    )
                    enriched_company['person_found'] = len(person_mandates) > 0
                    enriched_company['person_mandates'] = person_mandates

                    # Récupérer détails économiques (si SIREN valide)
                    if siren:
                        economic_data = self._get_company_details(siren)
                        if economic_data:
                            enriched_company['economic_data'] = economic_data

                    companies.append(enriched_company)

                print(f"[Pappers] ✓ Found {len(companies)} compan{'y' if len(companies)==1 else 'ies'}: {[c.get('nom_entreprise') for c in companies]}")

            # NOUVEAU: Rechercher les publications BODACC du dirigeant (si activé)
            if self.include_bodacc_person:
                bodacc_publications = self._search_bodacc_by_person(first_name, last_name)
                if bodacc_publications:
                    # Stocker séparément pour analyse
                    self.bodacc_person_cache = bodacc_publications
            else:
                print(f"[Pappers BODACC] Skipped (disabled in config)")

            return companies

        except Exception as e:
            print(f"[Pappers] ✗ Error searching companies: {e}")
            return []

    def _search_bodacc_by_person(self, first_name: str, last_name: str) -> Optional[Dict]:
        """
        Recherche les publications BODACC par nom de dirigeant
        Endpoint correct : /recherche-publications (pas /recherche-publications-bodacc)
        Coût : 1 crédit par page (on prend 10 résultats = 1 crédit)
        """
        try:
            url = f"{self.API_BASE_URL}/recherche-publications"
            headers = {'api-key': self.api_key}

            # Nettoyer le nom (enlever espaces, tirets multiples)
            clean_last = ' '.join(last_name.split())
            clean_first = ' '.join(first_name.split())

            params = {
                'nom_dirigeant': clean_last,
                'prenom_dirigeant': clean_first,
                'par_page': 10,  # 10 résultats max (1 crédit)
                'page': 1
            }

            print(f"[Pappers BODACC] Searching publications for {clean_first} {clean_last}")
            response = requests.get(url, params=params, headers=headers, timeout=10)

            # Si 400, l'API n'a pas trouvé ou paramètres invalides
            if response.status_code == 400:
                print(f"[Pappers BODACC] ℹ No publications or invalid search for {clean_first} {clean_last}")
                return None

            response.raise_for_status()
            data = response.json()

            publications = data.get('resultats', [])
            total = data.get('total', 0)

            if publications:
                print(f"[Pappers BODACC] ✓ Found {len(publications)} publication(s) (total: {total})")

                # Classifier par type
                types_found = {}
                for pub in publications:
                    pub_type = pub.get('type', 'Autre')
                    types_found[pub_type] = types_found.get(pub_type, 0) + 1

                print(f"[Pappers BODACC] Types: {types_found}")

                return {
                    'publications': publications,
                    'total': total,
                    'types': types_found
                }
            else:
                print(f"[Pappers BODACC] ℹ No publications found for {first_name} {last_name}")
                return None

        except Exception as e:
            print(f"[Pappers BODACC] ✗ Error searching publications: {e}")
            return None

    def _find_person_in_representants(self, first_name: str, last_name: str, representants: List[Dict]) -> List[Dict]:
        """Cherche la personne parmi les représentants"""
        person_mandates = []

        for rep in representants:
            rep_name = rep.get('nom', '').lower()
            rep_prenom = rep.get('prenom', '').lower()

            if (last_name.lower() in rep_name and first_name.lower() in rep_prenom):
                person_mandates.append({
                    'qualite': rep.get('qualite', 'N/A'),
                    'date_prise_de_poste': rep.get('date_prise_de_poste'),
                    'nom_complet': f"{rep.get('prenom', '')} {rep.get('nom', '')}",
                })

        if person_mandates:
            print(f"[Pappers] ✓ Found {len(person_mandates)} mandate(s) for {first_name} {last_name}")

        return person_mandates

    def _get_company_details(self, siren: str) -> Optional[Dict]:
        """Récupère les détails économiques d'une entreprise avec champs supplémentaires configurables"""
        try:
            url = f"{self.API_BASE_URL}/entreprise"
            headers = {'api-key': self.api_key}

            # Champs supplémentaires configurables selon le mode
            champs_supplementaires = [
                'representants_legaux',      # Gratuit
                'categorie_entreprise',      # Gratuit
                'motif_cessation',           # Gratuit
            ]

            # Ajouter les champs payants selon la config
            credits_cost = 0
            if self.include_entreprises_dirigees:
                champs_supplementaires.append('entreprises_dirigees')  # 1 crédit
                credits_cost += 1

            if self.include_observations:
                champs_supplementaires.append('observations')  # 0.5 crédit
                credits_cost += 0.5

            if self.include_decisions:
                champs_supplementaires.append('decisions')  # 5 crédits
                credits_cost += 5

            if self.include_parcelles:
                champs_supplementaires.append('parcelles_detenues')  # 5 crédits
                credits_cost += 5

            params = {
                'siren': siren,
                'champs_supplementaires': ','.join(champs_supplementaires)
            }

            print(f"[Pappers] Fetching details for SIREN {siren} (~{1 + credits_cost} credits)")

            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Extraire les données pertinentes pour la due diligence
            economic_info = {
                # Données économiques
                'capital_social': data.get('capital_social'),
                'chiffre_affaires': data.get('chiffre_affaires'),
                'resultat': data.get('resultat'),
                'effectif': data.get('effectif'),
                'date_creation': data.get('date_creation'),
                'date_immatriculation_rcs': data.get('date_immatriculation_rcs'),
                'categorie_juridique': data.get('categorie_juridique'),

                # Statut juridique (RED FLAGS)
                'statut_rcs': data.get('statut_rcs'),
                'date_radiation_rcs': data.get('date_radiation_rcs'),
                'entreprise_cessee': data.get('entreprise_cessee', False),

                # Procédures collectives (CRITIQUE pour Due Diligence)
                'procedures_collectives': data.get('procedures_collectives', []),

                # Annonces BODACC (annonces légales, tribunaux)
                'annonces_bodacc': data.get('publications_bodacc', []),

                # Comptes et bilans
                'comptes': data.get('comptes', []),
                'dernier_exercice': data.get('dernier_exercice', {}),

                # Mandataires (pour procédures)
                'mandataires_judiciaires': data.get('mandataires_judiciaires', []),

                # Autres établissements (réseau)
                'nombre_etablissements': data.get('nombre_etablissements'),
                'nombre_etablissements_ouverts': data.get('nombre_etablissements_ouverts'),

                # Métadonnées
                'derniere_mise_a_jour': data.get('derniere_mise_a_jour'),
            }

            return economic_info

        except Exception as e:
            print(f"[Pappers] ✗ Error getting company details for SIREN {siren}: {e}")
            return None

    def _calculate_total_credits(self, num_companies: int) -> float:
        """Calcule le coût total estimé en crédits"""
        # Recherche initiale : 1 crédit
        total = 1

        # Détails par entreprise
        cost_per_company = 1  # Base
        if self.include_entreprises_dirigees:
            cost_per_company += 1
        if self.include_observations:
            cost_per_company += 0.5
        if self.include_decisions:
            cost_per_company += 5
        if self.include_parcelles:
            cost_per_company += 5

        total += cost_per_company * num_companies

        # BODACC personne
        if self.include_bodacc_person:
            total += 1

        return total

    def get_cached_data(self) -> Optional[Dict]:
        """Récupère les données Pappers pour que le scraper puisse les utiliser"""
        return self.pappers_data