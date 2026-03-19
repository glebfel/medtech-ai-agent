from langchain_ollama import OllamaEmbeddings

from src.logging_config import get_logger
from src.settings import get_settings

logger = get_logger("services.embeddings")

_embeddings = None


def get_embeddings() -> OllamaEmbeddings:
    global _embeddings
    if _embeddings is None:
        settings = get_settings()
        _embeddings = OllamaEmbeddings(
            model=settings.embedding_model,
            base_url=settings.ollama_base_url,
        )
        logger.info(
            "Using Ollama embeddings (%s, dim=%d)",
            settings.embedding_model,
            settings.embedding_dim,
        )
    return _embeddings


def embed_text(text: str) -> list[float]:
    return get_embeddings().embed_query(text)


def embed_texts(texts: list[str]) -> list[list[float]]:
    return get_embeddings().embed_documents(texts)
