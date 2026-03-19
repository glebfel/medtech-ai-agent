from src.db import get_session
from src.schemas.icd10 import ICD10SearchResult
from src.repositories.icd10 import ICD10Repository


class ICD10Service:
    @staticmethod
    def search(query: str, limit: int = 5) -> list[ICD10SearchResult]:
        """Search ICD-10 codes by description keywords using trigram similarity."""
        with get_session() as session:
            repo = ICD10Repository(session)
            rows = repo.search_by_description(query, limit)

            return [
                ICD10SearchResult(
                    code=row["code"],
                    description=row["description"],
                    similarity=row["sim"],
                )
                for row in rows
            ]
