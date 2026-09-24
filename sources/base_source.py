from abc import ABC, abstractmethod


class JobSource(ABC):

    @abstractmethod
    def search_jobs(
        self,
        keyword: str,
        location: str,
        page: int = 1
    ) -> list[dict]:
        """
        Busca ofertas y devuelve una lista normalizada.
        """
        pass