from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models.dosage import DosageInfoEntity


class DosageRepository:
    def __init__(self, session: Session):
        self._session = session

    def find_by_medication(self, medication: str) -> Optional[DosageInfoEntity]:
        """Find dosage info by exact medication name (case-insensitive)."""
        stmt = select(DosageInfoEntity).where(
            func.lower(DosageInfoEntity.medication) == medication.strip().lower()
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def list_all_names(self) -> list[str]:
        """Return sorted list of all medication names."""
        stmt = select(DosageInfoEntity.medication).order_by(DosageInfoEntity.medication)
        rows = self._session.execute(stmt).scalars().all()
        return list(rows)
