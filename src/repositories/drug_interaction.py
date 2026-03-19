from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from src.models.drug_interaction import DrugInteractionEntity


class DrugInteractionRepository:
    def __init__(self, session: Session):
        self._session = session

    def find_by_drug_pair(
        self, drug_a: str, drug_b: str
    ) -> Optional[DrugInteractionEntity]:
        a = f"%{drug_a.strip().lower()}%"
        b = f"%{drug_b.strip().lower()}%"

        stmt = (
            select(DrugInteractionEntity)
            .where(
                or_(
                    (
                        func.lower(DrugInteractionEntity.drug_a).like(a)
                        & func.lower(DrugInteractionEntity.drug_b).like(b)
                    ),
                    (
                        func.lower(DrugInteractionEntity.drug_a).like(b)
                        & func.lower(DrugInteractionEntity.drug_b).like(a)
                    ),
                )
            )
            .limit(1)
        )
        return self._session.execute(stmt).scalar_one_or_none()
