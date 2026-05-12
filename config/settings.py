"""Configuration for the generic analysis pipeline."""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Typed env-driven settings for the Ollama-based pipeline."""

    OLLAMA_BASE_URL: str = Field(
        default="http://localhost:11434/api/chat",
        validation_alias="OLLAMA_URL",
    )
    OLLAMA_MODEL: str = Field(
        default="qwen3.5:9b",
        validation_alias="OLLAMA_MODEL",
    )
    OLLAMA_TEMPERATURE: float = 0.2
    OLLAMA_MAX_TOKENS: int = 2048
    OLLAMA_TIMEOUT_SECONDS: int = 300

    # Local fallback options: enable to run without a live Ollama server
    USE_LOCAL_FALLBACK: bool = False
    # If True, automatically fallback to local when Ollama request fails
    FALLBACK_ON_ERROR: bool = True

    MAX_LOOP_ITERATIONS: int = 5
    MATERIALITY_THRESHOLD: float = 3.0
    SHARED_FS_PATH: str = "output/shared"
    LOG_LEVEL: str = "DEBUG"
    DEBUG: bool = True
    DEFAULT_DOMAIN: str = "generic"
    DOMAIN_CONFIG_PATH: str = "config/domains.yaml"
    ROUTER_MAX_RETRIES: int = 2

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
