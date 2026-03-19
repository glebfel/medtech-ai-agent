from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.med_term import MedTermEntity


class MedTermsRepository:
    def __init__(self, session: Session):
        self._session = session

    def find_by_semantic(
        self, query_embedding: list[float], limit: int = 3
    ) -> list[MedTermEntity]:
        stmt = (
            select(MedTermEntity)
            .where(MedTermEntity.embedding.is_not(None))
            .order_by(MedTermEntity.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )
        return list(self._session.execute(stmt).scalars().all())
