"""FastAPI backend for the Palestine Legal Aid assistant."""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app import intent as intent_mod
from app import referral
from app import triage as triage_mod
from app.form_filler import available_forms, generate_pdf
from model.inference import _detect_language as detect_language
from model.inference import answer as llm_answer

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT / "frontend"

app = FastAPI(title="AI Legal Aid for Palestine", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=2000)
    # "auto" lets the inference layer detect Arabic vs English from the question.
    language: str = Field("auto", pattern="^(en|ar|auto)$")
    # Chroma rejects top_k <= 0; cap at the corpus size to avoid surprises.
    top_k: int = Field(3, ge=1, le=20)


class AskResponse(BaseModel):
    answer: str
    intent: dict
    sources: list[dict]
    clinics: list[dict]
    triage: dict
    action_plan: list[dict]
    language: str


class FormRequest(BaseModel):
    form_type: str
    fields: dict[str, str]


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    lang = None if req.language == "auto" else req.language
    resolved_lang = detect_language(req.question, hint=lang)
    result = llm_answer(req.question, language=lang, top_k=req.top_k)
    detected = intent_mod.classify(req.question)
    clinics = referral.find_clinics(intent=detected.label, limit=3)
    tr = triage_mod.assess(req.question, detected.label, language=resolved_lang)
    plan = triage_mod.action_plan(detected.label, language=resolved_lang)
    return AskResponse(
        answer=result["answer"],
        intent={
            "label": detected.label,
            "confidence": detected.confidence,
            "matched": detected.matched,
        },
        sources=[
            {"article": s["metadata"].get("article"), "title": s["metadata"].get("title"), "text": s["text"]}
            for s in result["sources"]
        ],
        clinics=clinics,
        triage={
            "level": tr.level,
            "color": tr.color,
            "label": tr.label,
            "deadline_hint": tr.deadline_hint,
        },
        action_plan=plan,
        language=resolved_lang,
    )


@app.post("/transcribe")
async def transcribe_endpoint(
    audio: UploadFile = File(...),
    language: str | None = Form(None),
) -> dict:
    try:
        from app.transcribe import FfmpegMissingError, transcribe_bytes
    except ImportError as exc:
        raise HTTPException(status_code=503, detail=f"transcription unavailable: {exc}") from exc

    data = await audio.read()
    suffix = Path(audio.filename or "").suffix or ".webm"
    try:
        result = transcribe_bytes(data, suffix=suffix, language=language)
    except FfmpegMissingError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover — whisper errors are varied
        raise HTTPException(status_code=500, detail=f"transcription failed: {exc}") from exc
    return {"text": result.text, "language": result.language, "duration": result.duration}


@app.get("/forms")
def list_forms() -> dict:
    return {"forms": available_forms()}


@app.post("/forms/generate")
def forms_generate(req: FormRequest) -> FileResponse:
    try:
        pdf_path = generate_pdf(req.form_type, req.fields)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return FileResponse(pdf_path, media_type="application/pdf", filename=Path(pdf_path).name)


@app.get("/clinics")
def clinics_endpoint(
    intent: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    limit: int = 3,
) -> dict:
    return {"clinics": referral.find_clinics(intent=intent, lat=lat, lon=lon, limit=limit)}


if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/sw.js")
def service_worker() -> FileResponse:
    """Serve the service worker at the root so its scope covers the whole site."""
    return FileResponse(
        FRONTEND_DIR / "sw.js",
        media_type="application/javascript",
        headers={"Service-Worker-Allowed": "/", "Cache-Control": "no-cache"},
    )


@app.get("/manifest.json")
def manifest() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "manifest.json", media_type="application/manifest+json")


@app.get("/", response_class=HTMLResponse)
def root() -> HTMLResponse:
    index = FRONTEND_DIR / "index.html"
    if not index.exists():
        return HTMLResponse("<h1>Backend running</h1><p>Frontend not found.</p>")
    return HTMLResponse(index.read_text(encoding="utf-8"))
