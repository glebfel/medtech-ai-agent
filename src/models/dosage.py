from sqlalchemy import Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class DosageInfoEntity(Base):
    __tablename__ = "dosage_info"

    id: Mapped[int] = mapped_column(primary_key=True)
    medication: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    dose_mg_per_kg_min: Mapped[float] = mapped_column(Float, nullable=False)
    dose_mg_per_kg_max: Mapped[float] = mapped_column(Float, nullable=False)
    max_daily_mg: Mapped[float] = mapped_column(Float, nullable=False)
    frequency: Mapped[str] = mapped_column(String(255), nullable=False)
    form: Mapped[str] = mapped_column(String(100), nullable=False)
    min_age: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    pediatric_note: Mapped[str] = mapped_column(Text, nullable=False)
    adult_note: Mapped[str] = mapped_column(Text, nullable=False)
    geriatric_note: Mapped[str] = mapped_column(Text, nullable=False)
