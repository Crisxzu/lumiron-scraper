from typing import List, Type
from app.sources.base_source import BaseSource
# from app.sources.linkedin_source import LinkedInSource
# from app.sources.company_website_source import CompanyWebsiteSource
from app.sources.serper_search_source import SerperSearchSource
from app.sources.pappers_source import PappersSource
from app.sources.dvf_source import DVFSource
from app.sources.hatvp_source import HAVTPSource

AVAILABLE_SOURCES: List[Type[BaseSource]] = [
    PappersSource,        # Intelligence économique et légale (API Pappers)
    SerperSearchSource,   # Recherche Google via API Serper (URLs + snippets + news)
    DVFSource,            # Transactions immobilières (DVF - data.gouv.fr)
    HAVTPSource,          # Personnes Politiquement Exposées (HATVP)
    # CompanyWebsiteSource,  # Désactivé: URLs devinées peu fiables, mieux via Serper
    # LinkedInSource,      # Désactivé: LinkedIn bloque le scraping
]

def get_all_sources() -> List[BaseSource]:
    return [source_class() for source_class in AVAILABLE_SOURCES]

def get_sources_by_name(source_names: List[str]) -> List[BaseSource]:
    source_map = {source_class.get_name(): source_class for source_class in AVAILABLE_SOURCES}
    return [source_map[name]() for name in source_names if name in source_map]
