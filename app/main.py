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
from app.form_filler import available_forms, generate_pdf
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
    question: str = Field(..., min_length=2)
    language: str = Field("en", pattern="^(en|ar)$")
    top_k: int = 3


class AskResponse(BaseModel):
    answer: str
    intent: dict
    sources: list[dict]
    clinics: list[dict]


class FormRequest(BaseModel):
    form_type: str
    fields: dict[str, str]


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    result = llm_answer(req.question, language=req.language, top_k=req.top_k)
    detected = intent_mod.classify(req.question)
    clinics = referral.find_clinics(intent=detected.label, limit=3)
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
    )


@app.post("/transcribe")
async def transcribe_endpoint(
    audio: UploadFile = File(...),
    language: str | None = Form(None),
) -> dict:
    try:
        from app.transcribe import transcribe_bytes
    except ImportError as exc:
        raise HTTPException(status_code=503, detail=f"transcription unavailable: {exc}") from exc

    data = await audio.read()
    suffix = Path(audio.filename or "").suffix or ".webm"
    try:
        result = transcribe_bytes(data, suffix=suffix, language=language)
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


@app.get("/", response_class=HTMLResponse)
def root() -> HTMLResponse:
    index = FRONTEND_DIR / "index.html"
    if not index.exists():
        return HTMLResponse("<h1>Backend running</h1><p>Frontend not found.</p>")
    return HTMLResponse(index.read_text(encoding="utf-8"))
