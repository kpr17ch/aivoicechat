"""Application configuration utilities."""

from pathlib import Path
from functools import lru_cache
from typing import Any, List

from pydantic import BaseModel, Field, HttpUrl
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
    openai_transcription_model: str = "gpt-4o-mini-transcribe"

    enable_audio_recording: bool = False
    recordings_dir: str = "recordings"
    transcripts_dir: str = "transcripts"
    port: int = 8000

    gmail_email: str = "kaiperich@gmail.com"
    gmail_app_password: str | None = None
    enable_email_tool: bool = True
    transcription_phrase_hints_raw: str | None = Field(
        default=None, alias="TRANSCRIPTION_PHRASE_HINTS"
    )
    transcription_phrase_defaults: list[str] = Field(
        default_factory=lambda: [
            "+49",
            "plus vier neun",
            "null",
            "eins",
            "zwei",
            "drei",
            "vier",
            "fünf",
            "sechs",
            "sieben",
            "acht",
            "neun",
            "zwo",
            "doppel null",
            "doppel eins",
            "doppel zwei",
            "doppel drei",
            "doppel vier",
            "doppel fünf",
            "doppel sechs",
            "doppel sieben",
            "doppel acht",
            "doppel neun",
            "Vorwahl",
            "Rückrufnummer",
            "Bestellnummer",
            "Kundennummer",
            "Buchstabe A",
            "Buchstabe B",
            "Buchstabe C",
            "Buchstabe D",
            "Buchstabe E",
            "Buchstabe F",
            "Buchstabe G",
            "Buchstabe H",
        ]
    )
    transcription_prompt_override: str | None = Field(
        default=None, alias="TRANSCRIPTION_PROMPT"
    )
    transcription_language_override: str | None = Field(
        default="de", alias="TRANSCRIPTION_LANGUAGE"
    )

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

    @property
    def transcription_phrase_hints(self) -> list[str]:
        """Return phrase hints for speech recognition."""
        phrases: list[str] = []
        if self.transcription_phrase_hints_raw:
            separators = [",", ";", "\n"]
            raw = self.transcription_phrase_hints_raw
            for sep in separators:
                raw = raw.replace(sep, "|")
            phrases.extend([p.strip() for p in raw.split("|") if p.strip()])
        if not phrases:
            phrases = []
        phrases.extend(self.transcription_phrase_defaults)
        seen: set[str] = set()
        ordered: list[str] = []
        for phrase in phrases:
            key = phrase.lower()
            if key not in seen:
                seen.add(key)
                ordered.append(phrase)
        return ordered

    @property
    def transcription_language(self) -> str | None:
        """Return language code used for speech transcription."""
        language = self.transcription_language_override
        return language.strip() if isinstance(language, str) and language.strip() else None

    @property
    def transcription_prompt(self) -> str | None:
        """Return descriptive prompt for speech transcription biasing."""
        base_prompt = None
        if self.transcription_prompt_override and self.transcription_prompt_override.strip():
            base_prompt = self.transcription_prompt_override.strip()
        else:
            base_prompt = (
                "Es handelt sich um deutschsprachige Servicegespräche."
                " Achte besonders auf Telefonnummern im Format '+49 …' oder '0 …'."
                " Die Landesvorwahl ist 'plus vier neun', niemals 'plus neun vier'."
                " Lies Ziffern einzeln vor (eins, zwei, drei …) und bestätige sie sorgfältig."
                " Erkenne Begriffe wie Bestellnummer, Kundennummer, Stornierung, Rückrufnummer, SecureCloud."
            )

        hints = self.transcription_phrase_hints
        if not base_prompt and not hints:
            return None

        if hints:
            hint_list = ", ".join(hints[:25])
            hint_suffix = f" Relevante Begriffe: {hint_list}."
        else:
            hint_suffix = ""

        composed = f"{base_prompt}{hint_suffix}" if base_prompt else hint_suffix
        return composed.strip() if composed else None

    @property
    def recordings_path(self) -> Path:
        """Return absolute path for audio recordings."""
        recordings = Path(self.recordings_dir)
        return recordings if recordings.is_absolute() else BACKEND_DIR / recordings

    @property
    def transcripts_path(self) -> Path:
        """Return absolute path for conversation transcripts."""
        transcripts = Path(self.transcripts_dir)
        return transcripts if transcripts.is_absolute() else BACKEND_DIR / transcripts

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
