"""Whisper-based speech-to-text (Arabic + English)."""
from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from functools import lru_cache


@dataclass
class Transcript:
    text: str
    language: str
    duration: float


@lru_cache(maxsize=1)
def _get_model():
    from faster_whisper import WhisperModel
    model_name = os.environ.get("WHISPER_MODEL", "small")
    device = os.environ.get("WHISPER_DEVICE", "cpu")
    compute_type = os.environ.get("WHISPER_COMPUTE", "int8")
    return WhisperModel(model_name, device=device, compute_type=compute_type)


def transcribe_file(path: str, language: str | None = None) -> Transcript:
    model = _get_model()
    segments, info = model.transcribe(path, language=language, vad_filter=True)
    text = " ".join(seg.text.strip() for seg in segments).strip()
    return Transcript(text=text, language=info.language, duration=info.duration)


def transcribe_bytes(data: bytes, suffix: str = ".webm", language: str | None = None) -> Transcript:
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(data)
        tmp_path = tmp.name
    try:
        return transcribe_file(tmp_path, language=language)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
