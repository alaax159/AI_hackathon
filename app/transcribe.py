"""Whisper-based speech-to-text (Arabic + English).

Tuned for speed:
  - WHISPER_MODEL defaults to "small" (Arabic on small is already solid).
  - On GPU, compute_type defaults to "float16"; on CPU, "int8".
  - beam_size=1 with VAD filtering — roughly 2x faster than the default
    beam search and accurate enough for short legal queries.
  - Arabic is forced when the caller passes language="ar" so Whisper does
    not waste time on language detection.
"""
from __future__ import annotations

import os
import shutil
import tempfile
from dataclasses import dataclass
from functools import lru_cache


class FfmpegMissingError(RuntimeError):
    """Raised when ffmpeg is not on PATH — faster-whisper can't decode webm/ogg without it."""


def ensure_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None:
        raise FfmpegMissingError(
            "ffmpeg is not on PATH. Browser audio (webm/ogg) requires ffmpeg to decode. "
            "Install it: https://www.gyan.dev/ffmpeg/builds/  (Windows: extract and add bin/ to PATH)."
        )


@dataclass
class Transcript:
    text: str
    language: str
    duration: float


def _default_compute_type(device: str) -> str:
    if device == "cuda":
        return "float16"
    return "int8"


@lru_cache(maxsize=1)
def _get_model():
    from faster_whisper import WhisperModel
    model_name = os.environ.get("WHISPER_MODEL", "small")
    device = os.environ.get("WHISPER_DEVICE", "auto")
    if device == "auto":
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
        except Exception:
            device = "cpu"
    compute_type = os.environ.get("WHISPER_COMPUTE", _default_compute_type(device))
    return WhisperModel(model_name, device=device, compute_type=compute_type)


def transcribe_file(path: str, language: str | None = None) -> Transcript:
    # Browser-recorded audio (webm/ogg) must go through ffmpeg. WAV would skip
    # this, but we don't get WAV from MediaRecorder, so check up front.
    if not path.lower().endswith(".wav"):
        ensure_ffmpeg()
    model = _get_model()
    segments, info = model.transcribe(
        path,
        language=language,
        vad_filter=True,
        beam_size=1,
        condition_on_previous_text=False,
    )
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
