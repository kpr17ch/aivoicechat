"""Pydantic schemas for conversation transcripts."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ConversationEntry(BaseModel):
    timestamp: Optional[str] = None
    role: Optional[str] = None
    text: Optional[str] = None
    status: Optional[str] = None
    sources: Optional[list[str]] = None
    normalized_text: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


class ConversationSummary(BaseModel):
    id: int
    stream_sid: str
    state: str
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    turn_count: int
    user_phone: Optional[str] = None
    latest_user_text: Optional[str] = None
    latest_assistant_text: Optional[str] = None
    transcript_available: bool = True
    created_at: datetime
    updated_at: datetime


class ConversationListResponse(BaseModel):
    total: int
    items: list[ConversationSummary] = Field(default_factory=list)


class ConversationDetail(BaseModel):
    id: int
    stream_sid: str
    state: str
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    turn_count: int
    user_phone: Optional[str] = None
    latest_user_text: Optional[str] = None
    latest_assistant_text: Optional[str] = None
    entries: list[ConversationEntry] = Field(default_factory=list)
    metadata: Optional[dict[str, Any]] = None
    transcript_json_path: Optional[str] = None
    transcript_txt_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
