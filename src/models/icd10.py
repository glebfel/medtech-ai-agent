from sqlalchemy import Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class ICD10CodeEntity(Base):
    __tablename__ = "icd10_codes"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        Index(
            "idx_icd10_description_trgm",
            "description",
            postgresql_using="gin",
            postgresql_ops={"description": "gin_trgm_ops"},
        ),
    )
