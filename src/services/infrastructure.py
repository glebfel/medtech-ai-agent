import os

import psycopg
from alembic import command
from alembic.config import Config
from dotenv import load_dotenv
from langgraph.store.postgres import PostgresStore
from langgraph.store.postgres.base import PostgresIndexConfig
from ollama import Client as OllamaClient

from src.agent.memory import create_checkpointer
from src.services.embeddings import get_embeddings
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
        logger.info(
            "LangSmith tracing enabled (project=%s)", settings.langchain_project
        )


def _ensure_embedding_model(settings: Settings) -> None:
    try:
        client = OllamaClient(
            host=settings.ollama_base_url, timeout=settings.embedding_pull_timeout
        )
        models = [m.model.split(":")[0] for m in client.list().models]
        if settings.embedding_model not in models:
            logger.info("Pulling embedding model %s...", settings.embedding_model)
            client.pull(settings.embedding_model)
            logger.info("Embedding model %s ready", settings.embedding_model)
    except Exception as e:
        logger.warning("Could not ensure embedding model: %s", e)


def init_infrastructure() -> tuple:
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
    _ensure_embedding_model(settings)

    with get_session() as session:
        seed_if_empty(session, data_dir=settings.data_dir)

    checkpointer = create_checkpointer(settings.database_url)

    store_conn = psycopg.connect(settings.database_url, autocommit=True)
    ttl_config = None
    if settings.memory_ttl_days > 0:
        ttl_seconds = settings.memory_ttl_days * 86400
        ttl_config = {
            "default_ttl": ttl_seconds,
            "refresh_on_read": True,
            "sweep_interval_minutes": settings.memory_sweep_interval_minutes,
        }
    index_config = PostgresIndexConfig(
        dims=settings.embedding_dim,
        embed=get_embeddings(),
    )
    store = PostgresStore(store_conn, index=index_config, ttl=ttl_config)
    store.setup()

    logger.info(
        "Infrastructure initialized, LLM provider=%s",
        settings.default_llm_provider.value,
    )
    return checkpointer, store, settings
