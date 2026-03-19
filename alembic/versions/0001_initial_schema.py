"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2025-03-19
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_table(
        "drug_interactions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("drug_a", sa.String(255), nullable=False),
        sa.Column("drug_b", sa.String(255), nullable=False),
        sa.Column("severity", sa.String(50), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("recommendation", sa.Text, nullable=False),
    )

    op.create_table(
        "icd10_codes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("code", sa.String(20), unique=True, nullable=False),
        sa.Column("description", sa.Text, nullable=False),
    )
    op.create_index(
        "idx_icd10_description_trgm",
        "icd10_codes",
        ["description"],
        postgresql_using="gin",
        postgresql_ops={"description": "gin_trgm_ops"},
    )

    op.create_table(
        "med_terms",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("term", sa.String(100), unique=True, nullable=False),
        sa.Column("explanation", sa.Text, nullable=False),
    )
    op.create_index(
        "idx_med_term_trgm",
        "med_terms",
        ["term"],
        postgresql_using="gin",
        postgresql_ops={"term": "gin_trgm_ops"},
    )

    op.create_table(
        "dosage_info",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("medication", sa.String(255), unique=True, nullable=False),
        sa.Column("dose_mg_per_kg_min", sa.Float, nullable=False),
        sa.Column("dose_mg_per_kg_max", sa.Float, nullable=False),
        sa.Column("max_daily_mg", sa.Float, nullable=False),
        sa.Column("frequency", sa.String(255), nullable=False),
        sa.Column("form", sa.String(100), nullable=False),
        sa.Column("min_age", sa.Float, nullable=False, server_default="0"),
        sa.Column("pediatric_note", sa.Text, nullable=False),
        sa.Column("adult_note", sa.Text, nullable=False),
        sa.Column("geriatric_note", sa.Text, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("dosage_info")
    op.drop_table("med_terms")
    op.drop_table("icd10_codes")
    op.drop_table("drug_interactions")
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
