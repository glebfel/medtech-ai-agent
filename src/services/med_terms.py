from typing import Optional

from src.db import get_session
from src.logging_config import get_logger
from src.repositories.med_terms import MedTermsRepository
from src.services.embeddings import embed_text

logger = get_logger("services.med_terms")


class MedTermsService:
    @staticmethod
    def explain(term: str) -> Optional[str]:
        with get_session() as session:
            repo = MedTermsRepository(session)
            try:
                query_vec = embed_text(term)
                results = repo.find_by_semantic(query_embedding=query_vec, limit=1)
                if results:
                    e = results[0]
                    return f"{e.term.upper()}: {e.explanation}"
            except Exception as ex:
                logger.error("Semantic search failed: %s", ex)

            return None
