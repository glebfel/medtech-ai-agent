from src.db import get_session
from src.logging_config import get_logger
from src.repositories.icd10 import ICD10Repository
from src.schemas.icd10 import ICD10SearchResult
from src.services.embeddings import embed_text

logger = get_logger("services.icd10")


class ICD10Service:
    @staticmethod
    def search(query: str, limit: int = 5) -> list[ICD10SearchResult]:
        with get_session() as session:
            repo = ICD10Repository(session)
            try:
                query_vec = embed_text(query)
                rows = repo.search_by_semantic(query_embedding=query_vec, limit=limit)
                if rows:
                    return [
                        ICD10SearchResult(
                            code=row["code"],
                            description=row["description"],
                            similarity=row["sim"],
                        )
                        for row in rows
                    ]
            except Exception as ex:
                logger.error("Semantic ICD-10 search failed: %s", ex)

            return []
