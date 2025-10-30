"""Conversation transcript endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, PlainTextResponse

from app.models.conversation import ConversationSession
from app.schemas.conversation import (
    ConversationDetail,
    ConversationEntry,
    ConversationListResponse,
    ConversationSummary,
)
from app.services import get_conversation_by_id, list_conversations

router = APIRouter()


def _to_summary(model: ConversationSession) -> ConversationSummary:
    return ConversationSummary(
        id=model.id,
        stream_sid=model.stream_sid,
        state=model.state,
        started_at=model.started_at,
        ended_at=model.ended_at,
        duration_seconds=model.duration_seconds,
        turn_count=model.turn_count,
        user_phone=model.user_phone,
        latest_user_text=model.latest_user_text,
        latest_assistant_text=model.latest_assistant_text,
        transcript_available=bool(model.transcript_json or model.transcript_text),
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _build_entries(model: ConversationSession) -> list[ConversationEntry]:
    transcript_payload = model.transcript_json or {}
    raw_entries: list[dict[str, Any]] = transcript_payload.get("entries", [])  # type: ignore[assignment]
    result: list[ConversationEntry] = []
    for entry in raw_entries:
        try:
            result.append(ConversationEntry.model_validate(entry))
        except Exception:
            fallback = {
                "timestamp": entry.get("timestamp"),
                "role": entry.get("role"),
                "text": entry.get("text"),
                "status": entry.get("status"),
                "sources": entry.get("sources"),
                "metadata": entry.get("metadata"),
                "normalized_text": entry.get("normalized_text"),
            }
            result.append(ConversationEntry.model_validate(fallback))
    return result


def _to_detail(model: ConversationSession) -> ConversationDetail:
    return ConversationDetail(
        id=model.id,
        stream_sid=model.stream_sid,
        state=model.state,
        started_at=model.started_at,
        ended_at=model.ended_at,
        duration_seconds=model.duration_seconds,
        turn_count=model.turn_count,
        user_phone=model.user_phone,
        latest_user_text=model.latest_user_text,
        latest_assistant_text=model.latest_assistant_text,
        entries=_build_entries(model),
        metadata=model.metadata_json,
        transcript_json_path=model.transcript_json_path,
        transcript_txt_path=model.transcript_txt_path,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _text_from_transcript(model: ConversationSession) -> str:
    if model.transcript_text:
        return model.transcript_text
    payload = model.transcript_json or {}
    lines = [
        f"# Transcript for {model.stream_sid}",
        f"State: {model.state}",
    ]
    updated_at = payload.get("updated_at")
    if updated_at:
        lines.append(f"Updated: {updated_at}")
    lines.append("")
    for entry in payload.get("entries", []):
        role = (entry.get("role") or "unknown").upper()
        timestamp = entry.get("timestamp", "")
        text_value = entry.get("text") or "[pending]"
        lines.append(f"[{timestamp}] {role}: {text_value}")
    return "\n".join(lines) + "\n"


def _safe_filename(value: str | None, fallback: str) -> str:
    if not value:
        return fallback
    safe_chars = [c if c.isalnum() or c in {"-", "_"} else "_" for c in value]
    sanitized = "".join(safe_chars).strip("._")
    return sanitized or fallback


@router.get("", response_model=ConversationListResponse)
async def list_conversation_summaries(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> ConversationListResponse:
    items, total = await list_conversations(limit=limit, offset=offset)
    summaries = [_to_summary(item) for item in items]
    return ConversationListResponse(total=total, items=summaries)


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation_detail(conversation_id: int) -> ConversationDetail:
    conversation = await get_conversation_by_id(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return _to_detail(conversation)


@router.get("/{conversation_id}/download")
async def download_conversation_transcript(
    conversation_id: int,
    format: str = Query("json", pattern="^(json|txt)$"),
):
    conversation = await get_conversation_by_id(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    identifier = _safe_filename(str(conversation.stream_sid), f"conversation-{conversation.id}")
    filename = f"{identifier}.{format}"

    if format == "json":
        if not conversation.transcript_json:
            raise HTTPException(status_code=404, detail="Transcript JSON not available")
        return JSONResponse(
            conversation.transcript_json,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=\"{filename}\""},
        )

    transcript_text = _text_from_transcript(conversation)
    if not transcript_text:
        raise HTTPException(status_code=404, detail="Transcript text not available")
    return PlainTextResponse(
        transcript_text,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename=\"{filename}\""},
    )
