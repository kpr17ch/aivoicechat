import base64
import binascii
from datetime import datetime
from pathlib import Path

from app.core.twilio_logging import log_event
from app.utils.audio import save_ulaw_segment, SAMPLE_RATE


async def finalize_audio_segment(
    current_audio_buffer: bytearray,
    audio_segment_index: int,
    stream_recording_dir: Path | None,
    reason: str,
    enable_recording: bool
) -> int:
    if not enable_recording or stream_recording_dir is None:
        return audio_segment_index

    if not current_audio_buffer:
        return audio_segment_index

    segment_bytes = bytes(current_audio_buffer)
    current_audio_buffer.clear()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    segment_filename = f"user_input_{audio_segment_index + 1:03d}_{timestamp}.wav"
    segment_path = stream_recording_dir / segment_filename

    try:
        raw_byte_count, sample_count = save_ulaw_segment(segment_bytes, segment_path)
    except Exception as exc:
        log_event("Audio Recording Failed", {
            "reason": reason,
            "file_path": str(segment_path),
            "error": str(exc)
        }, "ERROR")
        return audio_segment_index

    duration_ms = int(sample_count / SAMPLE_RATE * 1000) if SAMPLE_RATE else 0
    log_event("User Audio Recorded", {
        "file_path": str(segment_path),
        "reason": reason,
        "raw_bytes": raw_byte_count,
        "samples": sample_count,
        "duration_ms_estimate": duration_ms
    }, "SUCCESS")

    return audio_segment_index + 1


def decode_audio_chunk(payload: str) -> bytes | None:
    try:
        return base64.b64decode(payload)
    except (binascii.Error, TypeError) as exc:
        log_event("Audio Chunk Decode Failed", {"error": str(exc)}, "ERROR")
        return None
