from functools import lru_cache

from pydantic import Field, SecretStr, computed_field, field_validator
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
    openai_api_key: SecretStr = SecretStr("")
    openai_model: str = "gpt-4o-mini"

    # Anthropic (Claude)
    anthropic_api_key: SecretStr = SecretStr("")
    anthropic_model: str = "claude-sonnet-4-6-20250620"

    # GigaChat
    gigachat_credentials: SecretStr = SecretStr("")
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
    db_password: SecretStr = SecretStr("medassist")
    db_pool_size: int = 5
    db_max_overflow: int = 10

    # Data paths
    data_dir: str = Field(default="data", description="Path to seed JSON files")

    # Logging
    log_level: LogLevel = LogLevel.INFO

    # LangSmith (optional, enables automatic LLM tracing)
    langchain_tracing_v2: bool = False
    langchain_api_key: SecretStr = SecretStr("")
    langchain_project: str = "medassist"

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.db_user}:{self.db_password.get_secret_value()}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @field_validator("llm_provider", mode="before")
    @classmethod
    def _normalize_provider(cls, v: str) -> str:
        return v.strip().lower()



@lru_cache
def get_settings() -> Settings:
    return Settings()
