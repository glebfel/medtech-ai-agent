from sqlalchemy import text
from sqlalchemy.orm import Session


class ICD10Repository:
    def __init__(self, session: Session):
        self._session = session

    def search_by_description(self, query: str, limit: int = 5) -> list[dict]:
        """Search ICD-10 codes using PostgreSQL trigram similarity + ILIKE fallback."""
        stmt = text("""
            SELECT code, description,
                   similarity(LOWER(description), LOWER(:query)) AS sim
            FROM icd10_codes
            WHERE LOWER(description) %% LOWER(:query)
               OR LOWER(description) LIKE LOWER(:pattern)
            ORDER BY sim DESC
            LIMIT :limit
        """)
        rows = self._session.execute(
            stmt,
            {"query": query, "pattern": f"%{query.strip()}%", "limit": limit},
        ).fetchall()

        return [
            {"code": r.code, "description": r.description, "sim": r.sim}
            for r in rows
        ]
