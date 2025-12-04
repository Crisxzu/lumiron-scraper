from abc import ABC, abstractmethod
from typing import List

class BaseSource(ABC):
    @abstractmethod
    def get_urls(self, first_name: str, last_name: str, company: str) -> List[str]:
        pass

    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        pass

    @classmethod
    def get_description(cls) -> str:
        return "No description available"

    def build_search_query(self, *terms) -> str:
        from urllib.parse import quote_plus
        return quote_plus(" ".join(str(term) for term in terms if term))
