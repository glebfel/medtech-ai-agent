from sqlalchemy import Float, Index, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class DrugInteractionEntity(Base):
    __tablename__ = "drug_interactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    drug_a: Mapped[str] = mapped_column(String(255), nullable=False)
    drug_b: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)


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
