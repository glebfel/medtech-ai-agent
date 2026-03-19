from alembic import context
from sqlalchemy import create_engine

from src.models.base import Base
from src.models.dosage import DosageInfoEntity  # noqa: F401
from src.models.drug_interaction import DrugInteractionEntity  # noqa: F401
from src.models.icd10 import ICD10CodeEntity  # noqa: F401
from src.models.med_term import MedTermEntity  # noqa: F401
from src.models.chat_session import ChatSessionEntity  # noqa: F401

target_metadata = Base.metadata


def run_migrations_online() -> None:
    url = context.config.get_main_option("sqlalchemy.url")
    if url and url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)

    connectable = create_engine(url)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
