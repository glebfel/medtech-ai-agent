from langchain_core.language_models import BaseChatModel
from langchain_gigachat import GigaChat
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from src.schemas.enums import LLMProvider
from src.settings import Settings


def create_llm(settings: Settings, temperature: float = 0.1) -> BaseChatModel:
    provider = settings.llm_provider

    if provider == LLMProvider.OPENAI:
        return ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=temperature,
        )

    if provider == LLMProvider.GIGACHAT:
        return GigaChat(
            credentials=settings.gigachat_credentials,
            scope=settings.gigachat_scope,
            model="GigaChat",
            verify_ssl_certs=settings.gigachat_verify_ssl,
            temperature=temperature,
        )

    if provider == LLMProvider.OLLAMA:
        return ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=temperature,
        )

    raise ValueError(f"Unsupported LLM provider: {provider}")
