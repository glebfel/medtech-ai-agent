import os

from alembic import command
from alembic.config import Config
from dotenv import load_dotenv

from src.agent.memory import create_checkpointer
from src.db import get_session, init_engine
from src.db.seed import seed_if_empty
from src.logging_config import get_logger, setup_logging
from src.settings import Settings, get_settings

logger = get_logger("infrastructure")


def _run_migrations(database_url: str) -> None:
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option(name="sqlalchemy.url", value=database_url)
    command.upgrade(alembic_cfg, revision="head")
    logger.info("Database migrations applied")


def _configure_langsmith(settings: Settings) -> None:
    if settings.langchain_tracing_v2 and settings.langchain_api_key.get_secret_value():
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key.get_secret_value()
        os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
        logger.info("LangSmith tracing enabled (project=%s)", settings.langchain_project)


def init_infrastructure():
    load_dotenv()
    settings = get_settings()

    setup_logging(settings.log_level)
    _configure_langsmith(settings)
    _run_migrations(settings.database_url)

    init_engine(
        settings.database_url,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
    )
    with get_session() as session:
        seed_if_empty(session, data_dir=settings.data_dir)

    checkpointer = create_checkpointer(settings.database_url)

    logger.info("Infrastructure initialized, LLM provider=%s", settings.default_llm_provider.value)
    return checkpointer, settings
