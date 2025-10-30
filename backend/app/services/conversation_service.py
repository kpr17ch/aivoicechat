"""Persistence helpers for conversation transcripts."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionMaker
from app.models.conversation import ConversationSession


async def _get_by_stream_sid(
    session: AsyncSession, stream_sid: str
) -> ConversationSession | None:
    statement = select(ConversationSession).where(
        ConversationSession.stream_sid == stream_sid
    )
    result = await session.execute(statement)
    return result.scalars().first()


def _merge_metadata(
    existing: dict[str, Any] | None, incoming: dict[str, Any] | None
) -> dict[str, Any] | None:
    if not incoming:
        return existing
    merged = dict(existing or {})
    for key, value in incoming.items():
        merged[key] = value
    return merged


def _compute_duration_seconds(
    started_at: datetime | None, ended_at: datetime | None
) -> int | None:
    if not started_at or not ended_at:
        return None
    delta = ended_at - started_at
    return max(int(delta.total_seconds()), 0)


async def upsert_conversation_snapshot(
    *,
    stream_sid: str,
    state: str,
    turn_count: int,
    transcript_payload: dict[str, Any] | None,
    transcript_text: str | None,
    json_path: str | None,
    text_path: str | None,
    started_at: datetime | None,
    ended_at: datetime | None,
    last_user_text: str | None,
    last_assistant_text: str | None,
    user_phone: str | None,
    metadata: dict[str, Any] | None,
) -> None:
    """Create or update a stored conversation transcript snapshot."""

    async with AsyncSessionMaker() as session:
        conversation = await _get_by_stream_sid(session, stream_sid)
        now = datetime.utcnow()

        duration_seconds = _compute_duration_seconds(started_at, ended_at)
        metadata_payload = metadata or {}

        if conversation is None:
            conversation = ConversationSession(
                stream_sid=stream_sid,
                state=state,
                started_at=started_at or now,
                ended_at=ended_at,
                duration_seconds=duration_seconds,
                turn_count=turn_count,
                user_phone=user_phone,
                latest_user_text=last_user_text,
                latest_assistant_text=last_assistant_text,
                transcript_json=transcript_payload or None,
                transcript_text=transcript_text,
                transcript_json_path=json_path,
                transcript_txt_path=text_path,
                metadata_json=metadata_payload or None,
                created_at=now,
                updated_at=now,
            )
            session.add(conversation)
        else:
            conversation.state = state
            conversation.turn_count = turn_count
            conversation.latest_user_text = last_user_text or conversation.latest_user_text
            conversation.latest_assistant_text = (
                last_assistant_text or conversation.latest_assistant_text
            )
            if user_phone and not conversation.user_phone:
                conversation.user_phone = user_phone
            if started_at and (
                conversation.started_at is None or started_at < conversation.started_at
            ):
                conversation.started_at = started_at
            if ended_at:
                conversation.ended_at = ended_at
            computed_duration = _compute_duration_seconds(
                conversation.started_at, conversation.ended_at
            )
            conversation.duration_seconds = (
                computed_duration if computed_duration is not None else duration_seconds
            )
            conversation.transcript_json = transcript_payload or conversation.transcript_json
            if transcript_text:
                conversation.transcript_text = transcript_text
            if json_path:
                conversation.transcript_json_path = json_path
            if text_path:
                conversation.transcript_txt_path = text_path
            conversation.metadata_json = _merge_metadata(
                conversation.metadata_json, metadata_payload
            )
            conversation.updated_at = now

        await session.commit()


async def list_conversations(
    *, limit: int = 20, offset: int = 0
) -> tuple[list[ConversationSession], int]:
    """Return paginated conversations ordered by newest first."""

    async with AsyncSessionMaker() as session:
        total_stmt = select(func.count()).select_from(ConversationSession)
        total_result = await session.execute(total_stmt)
        total = int(total_result.scalar() or 0)

        stmt = (
            select(ConversationSession)
            .order_by(ConversationSession.started_at.desc(), ConversationSession.id.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all(), total


async def get_conversation_by_id(
    conversation_id: int,
) -> ConversationSession | None:
    """Return a single conversation by identifier."""

    async with AsyncSessionMaker() as session:
        stmt = select(ConversationSession).where(
            ConversationSession.id == conversation_id
        )
        result = await session.execute(stmt)
        return result.scalars().first()


async def get_conversation_by_stream_sid(
    stream_sid: str,
) -> ConversationSession | None:
    """Return a conversation record using the stream SID."""

    async with AsyncSessionMaker() as session:
        return await _get_by_stream_sid(session, stream_sid)
