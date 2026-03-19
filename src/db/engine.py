from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.logging_config import get_logger
from src.models.base import Base

logger = get_logger("db.engine")

_engine: Optional[Engine] = None
_session_factory: Optional[sessionmaker[Session]] = None


def _to_sqlalchemy_url(database_url: str) -> str:
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


def init_engine(database_url: str) -> None:
    global _engine, _session_factory

    url = _to_sqlalchemy_url(database_url)
    _engine = create_engine(url, pool_size=5, max_overflow=10, pool_pre_ping=True)
    _session_factory = sessionmaker(bind=_engine, expire_on_commit=False)

    with _engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        conn.commit()

    Base.metadata.create_all(_engine)
    logger.info("Database engine initialized (host=%s, db=%s)", _engine.url.host, _engine.url.database)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_engine() first.")

    session = _session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_engine() -> Engine:
    if _engine is None:
        raise RuntimeError("Database not initialized. Call init_engine() first.")
    return _engine


def close_engine() -> None:
    global _engine, _session_factory
    if _engine is not None:
        _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("Database engine closed")
