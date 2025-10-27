"""Assistant settings model."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class AssistantSettings(SQLModel, table=True):
    """Persisted assistant configuration."""

    __tablename__ = "assistant_settings"

    id: Optional[int] = Field(default=None, primary_key=True)
    voice: str = Field(default="sage", max_length=50)
    system_instructions: str = Field(default="")
    greeting_message: Optional[str] = Field(default=None)
    template_name: str = Field(default="allgemein", max_length=100)
    phone_number: Optional[str] = Field(default=None, max_length=50, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
