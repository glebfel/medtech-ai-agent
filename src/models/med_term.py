from sqlalchemy import Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class MedTermEntity(Base):
    __tablename__ = "med_terms"

    id: Mapped[int] = mapped_column(primary_key=True)
    term: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        Index(
            "idx_med_term_trgm",
            "term",
            postgresql_using="gin",
            postgresql_ops={"term": "gin_trgm_ops"},
        ),
    )
