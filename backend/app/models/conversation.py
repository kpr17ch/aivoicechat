"""Database model for stored conversation transcripts."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class ConversationSession(SQLModel, table=True):
    """Represents a recorded AI voice conversation with transcript metadata."""

    __tablename__ = "conversation_sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    stream_sid: str = Field(max_length=128, index=True, unique=True)
    state: str = Field(default="initialized", max_length=50)
    started_at: Optional[datetime] = Field(default=None)
    ended_at: Optional[datetime] = Field(default=None)
    duration_seconds: Optional[int] = Field(default=None)
    turn_count: int = Field(default=0)
    user_phone: Optional[str] = Field(default=None, max_length=50)
    latest_user_text: Optional[str] = Field(default=None)
    latest_assistant_text: Optional[str] = Field(default=None)
    data_version: int = Field(default=1)
    metadata_json: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSON),
    )
    transcript_json: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSON),
    )
    transcript_text: Optional[str] = Field(default=None)
    transcript_json_path: Optional[str] = Field(default=None, max_length=500)
    transcript_txt_path: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
