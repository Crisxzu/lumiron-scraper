from typing import List, Type
from app.sources.base_source import BaseSource
from app.sources.linkedin_source import LinkedInSource
from app.sources.company_website_source import CompanyWebsiteSource
from app.sources.serper_search_source import SerperSearchSource

AVAILABLE_SOURCES: List[Type[BaseSource]] = [
    SerperSearchSource,   # Recherche Google via API Serper (URLs + snippets)
    CompanyWebsiteSource,  # Sites d'entreprise (.com et .fr)
    # LinkedInSource,      # Désactivé: LinkedIn bloque le scraping
]

def get_all_sources() -> List[BaseSource]:
    return [source_class() for source_class in AVAILABLE_SOURCES]

def get_sources_by_name(source_names: List[str]) -> List[BaseSource]:
    source_map = {source_class.get_name(): source_class for source_class in AVAILABLE_SOURCES}
    return [source_map[name]() for name in source_names if name in source_map]
