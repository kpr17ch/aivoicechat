from __future__ import annotations

from typing import Any, Mapping

import structlog

_LOGGER = structlog.get_logger("voice_assistant")

_LEVEL_MAP = {
    "TRACE": "debug",
    "DEBUG": "debug",
    "INFO": "info",
    "SUCCESS": "info",
    "WARNING": "warning",
    "ERROR": "error",
    "CRITICAL": "critical",
}


def log_event(event_type: str, data: Mapping[str, Any] | str | None = None, level: str = "INFO") -> None:
    """Emit a structured log entry for voice assistant events."""
    log = _LOGGER.bind(category=event_type)

    if data is None:
        payload: dict[str, Any] = {}
    elif isinstance(data, Mapping):
        payload = dict(data)
    else:
        payload = {"message": str(data)}

    method_name = _LEVEL_MAP.get(level.upper(), "info")
    log_method = getattr(log, method_name, log.info)
    log_method(event_type, **payload)


def format_openai_event(response: Mapping[str, Any]) -> tuple[str, dict[str, Any], str]:
    """Return structured event information for OpenAI realtime responses."""
    event_type = str(response.get("type", "unknown"))
    payload: dict[str, Any] = {
        "event_id": response.get("event_id", "N/A"),
    }
    level = "INFO"

    if event_type == "response.done":
        resp_data = response.get("response", {}) or {}
        usage = resp_data.get("usage", {}) or {}

        transcript: str | None = None
        for item in resp_data.get("output", []) or []:
            if not isinstance(item, Mapping):
                continue
            content = item.get("content", []) or []
            for part in content:
                if isinstance(part, Mapping) and part.get("type") in {"audio", "message"}:
                    transcript = transcript or part.get("transcript") or part.get("text")
        payload.update(
            {
                "response_id": resp_data.get("id", "N/A"),
                "status": resp_data.get("status", "N/A"),
                "voice": resp_data.get("voice"),
                "temperature": resp_data.get("temperature"),
                "transcript": transcript,
                "usage": {
                    "total": usage.get("total_tokens", 0),
                    "input": usage.get("input_tokens", 0),
                    "output": usage.get("output_tokens", 0),
                    "input_text": (usage.get("input_token_details") or {}).get("text_tokens", 0),
                    "input_audio": (usage.get("input_token_details") or {}).get("audio_tokens", 0),
                    "cached": (usage.get("input_token_details") or {}).get("cached_tokens", 0),
                    "output_text": (usage.get("output_token_details") or {}).get("text_tokens", 0),
                    "output_audio": (usage.get("output_token_details") or {}).get("audio_tokens", 0),
                },
            }
        )
    elif event_type in {"response.audio.delta", "response.output_audio.delta"}:
        delta = response.get("delta", "") or ""
        payload.update(
            {
                "response_id": response.get("response_id", "N/A"),
                "item_id": response.get("item_id", "N/A"),
                "bytes": len(delta),
            }
        )
        level = "DEBUG"
    elif event_type == "rate_limits.updated":
        payload["rate_limits"] = response.get("rate_limits")
        level = "DEBUG"
    elif event_type == "response.content.done":
        payload.update(
            {
                "item_id": response.get("item_id", "N/A"),
                "role": response.get("role"),
            }
        )
        level = "DEBUG"
    elif event_type in {
        "input_audio_buffer.speech_started",
        "input_audio_buffer.speech_stopped",
        "input_audio_buffer.committed",
    }:
        payload.update(
            {
                "item_id": response.get("item_id", "N/A"),
                "audio_start_ms": response.get("audio_start_ms"),
                "audio_end_ms": response.get("audio_end_ms"),
                "previous_item_id": response.get("previous_item_id"),
            }
        )
    elif event_type == "session.created":
        session = response.get("session", {}) or {}
        payload.update(
            {
                "session_id": session.get("id", "N/A"),
                "model": session.get("model"),
                "voice": session.get("voice"),
            }
        )
    elif event_type == "session.updated":
        session = response.get("session", {}) or {}
        instructions = session.get("instructions")
        payload.update(
            {
                "session_id": session.get("id", "N/A"),
                "model": session.get("model"),
                "voice": session.get("voice"),
                "instructions_preview": instructions[:80] if isinstance(instructions, str) else None,
            }
        )
    elif event_type == "error":
        error = response.get("error", {}) or {}
        payload.update(
            {
                "error_type": error.get("type"),
                "error_code": error.get("code"),
                "error_message": error.get("message"),
            }
        )
        level = "ERROR"

    event_name = f"openai.{event_type.replace('.', '_')}"
    return event_name, payload, level
