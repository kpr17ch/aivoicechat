"""Application configuration utilities."""

from pathlib import Path
from functools import lru_cache
from typing import Any, List

from pydantic import BaseModel, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_DIR = Path(__file__).resolve().parents[2]


class LoggingConfig(BaseModel):
    """Simple struct describing logging options."""

    level: str = "INFO"
    json_logs: bool = False


class Settings(BaseSettings):
    """Application settings pulled from environment variables."""

    app_name: str = "AI Voice Assistant Platform"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/assistants"
    openai_api_key: str
    frontend_origins: List[HttpUrl] | str | None = None
    log_level: str = "INFO"
    default_voice: str = "sage"
    default_system_instructions: str = "Du bist ein hilfreicher KI-Assistent."
    default_greeting_message: str | None = None
    conversation_temperature: float = 0.8

    openai_realtime_url: str = "https://api.openai.com/v1/realtime?model=gpt-realtime-mini"
    openai_realtime_model: str = "gpt-realtime-mini"
    temperature: float = 0.8

    enable_audio_recording: bool = False
    recordings_dir: str = "recordings"
    port: int = 8000

    gmail_email: str = "kaiperich@gmail.com"
    gmail_app_password: str | None = None
    enable_email_tool: bool = True

    model_config = SettingsConfigDict(
        env_file=(
            str(REPO_ROOT / ".env"),
            str(BACKEND_DIR / ".env"),
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        """Return normalized list of allowed origins for CORS."""
        if isinstance(self.frontend_origins, list):
            return [str(origin) for origin in self.frontend_origins]
        if isinstance(self.frontend_origins, str):
            return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]
        return ["http://localhost:3000"]

    @property
    def logging(self) -> LoggingConfig:
        """Return logging configuration derived from env."""
        return LoggingConfig(level=self.log_level.upper())

    def assistant_payload(self) -> dict[str, Any]:
        """Return default assistant settings exposed via API."""
        return {
            "voice": self.default_voice,
            "system_instructions": self.default_system_instructions,
            "greeting_message": self.default_greeting_message,
            "temperature": self.conversation_temperature,
        }


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
