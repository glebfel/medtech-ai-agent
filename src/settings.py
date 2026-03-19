from functools import lru_cache

from pydantic import Field, computed_field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.schemas.enums import LLMProvider, LogLevel


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM
    llm_provider: LLMProvider = LLMProvider.OPENAI

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # GigaChat
    gigachat_credentials: str = ""
    gigachat_scope: str = "GIGACHAT_API_PERS"
    gigachat_verify_ssl: bool = False

    # Ollama
    ollama_model: str = "llama3.1"
    ollama_base_url: str = "http://localhost:11434"

    # Database
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "medassist"
    db_user: str = "medassist"
    db_password: str = "medassist"
    db_pool_size: int = 5
    db_max_overflow: int = 10

    # Data paths
    data_dir: str = Field(default="data", description="Path to seed JSON files")

    # Logging
    log_level: LogLevel = LogLevel.INFO

    # LangSmith (optional, enables automatic LLM tracing)
    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    langchain_project: str = "medassist"

    @computed_field
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @field_validator("llm_provider", mode="before")
    @classmethod
    def _normalize_provider(cls, v: str) -> str:
        return v.strip().lower()

    @model_validator(mode="after")
    def _validate_llm_credentials(self) -> "Settings":
        if self.llm_provider == LLMProvider.OPENAI and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        if self.llm_provider == LLMProvider.GIGACHAT and not self.gigachat_credentials:
            raise ValueError("GIGACHAT_CREDENTIALS is required when LLM_PROVIDER=gigachat")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
