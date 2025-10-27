import audioop
import wave
from pathlib import Path

SAMPLE_RATE = 8000
SAMPLE_WIDTH = 2


def save_ulaw_segment(raw_audio: bytes, destination: Path) -> tuple[int, int]:
    if not raw_audio:
        return 0, 0

    try:
        pcm_audio = audioop.ulaw2lin(raw_audio, SAMPLE_WIDTH)
    except audioop.error as exc:
        raise ValueError(f"Failed to convert μ-law audio: {exc}") from exc

    destination.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(destination), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(SAMPLE_WIDTH)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(pcm_audio)

    return len(raw_audio), len(pcm_audio) // SAMPLE_WIDTH
