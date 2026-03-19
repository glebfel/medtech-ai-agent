from typing import Optional

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from src.models.med_term import MedTermEntity


class MedTermsRepository:
    def __init__(self, session: Session):
        self._session = session

    def find_by_term(self, term: str) -> Optional[MedTermEntity]:
        """Exact case-insensitive match."""
        stmt = select(MedTermEntity).where(
            func.lower(MedTermEntity.term) == term.strip().lower()
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def find_similar(self, term: str, threshold: float = 0.3) -> Optional[MedTermEntity]:
        """Fuzzy match using pg_trgm similarity."""
        stmt = text("""
            SELECT id, term, explanation,
                   similarity(LOWER(term), LOWER(:term)) AS sim
            FROM med_terms
            WHERE similarity(LOWER(term), LOWER(:term)) >= :threshold
            ORDER BY sim DESC
            LIMIT 1
        """)
        row = self._session.execute(
            stmt, {"term": term.strip(), "threshold": threshold}
        ).fetchone()

        if row is None:
            return None

        return self._session.get(MedTermEntity, row.id)
