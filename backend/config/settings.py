from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings for Tamizh JARVIS."""
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "Tamizh JARVIS"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    PORT: int = 8000
    HOST: str = "127.0.0.1"
    LOG_LEVEL: str = "INFO"

    # AI Provider Settings
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    LOCAL_LLM_BASE_URL: str = "http://localhost:11434"
    LOCAL_LLM_MODEL: str = "llama3"
    DEFAULT_AI_PROVIDER: str = "auto"  # "gemini", "local", or "auto"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./jarvis.db"

    # Security
    SECURITY_REQUIRE_APPROVAL_FOR_HIGH_RISK: bool = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
