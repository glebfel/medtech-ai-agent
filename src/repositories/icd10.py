from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.icd10 import ICD10CodeEntity


class ICD10Repository:
    def __init__(self, session: Session):
        self._session = session

    def search_by_semantic(
        self, query_embedding: list[float], limit: int = 5
    ) -> list[dict]:
        stmt = (
            select(
                ICD10CodeEntity.code,
                ICD10CodeEntity.description,
                ICD10CodeEntity.embedding.cosine_distance(query_embedding).label(
                    "distance"
                ),
            )
            .where(ICD10CodeEntity.embedding.is_not(None))
            .order_by("distance")
            .limit(limit)
        )
        rows = self._session.execute(stmt).fetchall()
        return [
            {"code": r.code, "description": r.description, "sim": 1 - r.distance}
            for r in rows
        ]
