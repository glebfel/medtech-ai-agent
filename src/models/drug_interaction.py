from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class DrugInteractionEntity(Base):
    __tablename__ = "drug_interactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    drug_a: Mapped[str] = mapped_column(String(255), nullable=False)
    drug_b: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Optional[list]] = mapped_column(Vector(768), nullable=True)
