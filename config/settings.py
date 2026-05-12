"""Configuration for the generic analysis pipeline."""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Typed env-driven settings for the vLLM-based pipeline."""

    VLLM_BASE_URL: str = Field(
        default="http://localhost:8000/v1",
        validation_alias="VLLM_URL",
    )
    VLLM_MODEL: str = Field(
        default="qwen3.6:35b",
        validation_alias="VLLM_MODEL",
    )
    VLLM_TEMPERATURE: float = 0.2
    VLLM_MAX_TOKENS: int = 2048
    VLLM_TIMEOUT_SECONDS: int = 300

    # Local fallback options: enable to run without a live vLLM server
    USE_LOCAL_FALLBACK: bool = False
    # If True, automatically fallback to local when vLLM request fails
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
