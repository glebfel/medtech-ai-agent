from typing import Optional

from src.db import get_session
from src.repositories.med_terms import MedTermsRepository


class MedTermsService:
    @staticmethod
    def explain(term: str) -> Optional[str]:
        """Look up a medical term in the database.

        Tries exact match first, then falls back to fuzzy similarity via pg_trgm.
        Returns formatted explanation or None if not found.
        """
        with get_session() as session:
            repo = MedTermsRepository(session)

            # Exact match
            entity = repo.find_by_term(term)
            if entity is not None:
                return f"{entity.term.upper()}: {entity.explanation}"

            # Fuzzy fallback
            similar = repo.find_similar(term, threshold=0.3)
            if similar is not None:
                return (
                    f"Did you mean '{similar.term.upper()}'?\n\n"
                    f"{similar.term.upper()}: {similar.explanation}"
                )

            return None
