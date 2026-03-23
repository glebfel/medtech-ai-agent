import httpx
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langchain_gigachat import GigaChat
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from src.schemas.enums import LLMProvider
from src.settings import Settings
from src.ui.constants import PROVIDER_MODELS

_DEFAULT_MODELS: dict[str, str] = {k: v[0] for k, v in PROVIDER_MODELS.items()}


def create_llm(
    settings: Settings, temperature: float = 0.1, model_name: str = ""
) -> BaseChatModel:
    provider = settings.default_llm_provider
    http_client = None if settings.verify_ssl else httpx.Client(verify=False)

    if provider == LLMProvider.OPENAI:
        return ChatOpenAI(
            model=model_name or _DEFAULT_MODELS["openai"],
            api_key=settings.openai_api_key,
            temperature=temperature,
            http_client=http_client,
        )

    if provider == LLMProvider.ANTHROPIC:
        return ChatAnthropic(
            model=model_name or _DEFAULT_MODELS["anthropic"],
            api_key=settings.anthropic_api_key,
            temperature=temperature,
            http_client=http_client,
        )

    if provider == LLMProvider.GIGACHAT:
        return GigaChat(
            credentials=settings.gigachat_credentials,
            scope=settings.gigachat_scope,
            model=model_name or _DEFAULT_MODELS["gigachat"],
            verify_ssl_certs=settings.verify_ssl,
            temperature=temperature,
        )

    if provider == LLMProvider.OLLAMA:
        return ChatOllama(
            model=model_name or _DEFAULT_MODELS["ollama"],
            base_url=settings.ollama_base_url,
            temperature=temperature,
        )

    raise ValueError(f"Unsupported LLM provider: {provider}")
