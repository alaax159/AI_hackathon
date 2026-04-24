"""Local LLM inference wrapper with RAG-augmented prompting.

Lazy-loads the model so importing this module is cheap. Exports:

    answer(question, language="en") -> dict

The returned dict contains `answer`, `sources`, and `prompt` for inspection.
"""
from __future__ import annotations

import os
import textwrap
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from model.rag import retrieve

SYSTEM_PROMPT = textwrap.dedent(
    """\
    You are a legal aid assistant helping Palestinian citizens understand their rights
    under the Palestinian Basic Law (2003, amended 2005).

    Rules:
    - Answer ONLY based on the provided legal context.
    - Use plain, simple language (Grade 8 reading level).
    - Always end with: "This is general legal information. For your specific situation,
      consult a licensed Palestinian lawyer or visit a legal aid center."
    - Never give advice that could harm the user.
    - If the answer is not in the provided articles, say so clearly.
    - Respond in the user's language (Arabic or English).
    """
)

DISCLAIMER = (
    "This is general legal information. For your specific situation, "
    "consult a licensed Palestinian lawyer or visit a legal aid center."
)


@dataclass
class AnswerResult:
    answer: str
    sources: list[dict]
    prompt: str


def _model_name() -> str:
    return os.environ.get("LLM_MODEL", "Equall/Saul-7B-Instruct-v1")


def _max_new_tokens() -> int:
    return int(os.environ.get("LLM_MAX_NEW_TOKENS", "400"))


def _temperature() -> float:
    return float(os.environ.get("LLM_TEMPERATURE", "0.2"))


def _device() -> str:
    return os.environ.get("LLM_DEVICE", "auto")


@lru_cache(maxsize=1)
def _get_pipeline():
    """Lazily load the text-generation pipeline (heavy)."""
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    import torch

    name = _model_name()
    tokenizer = AutoTokenizer.from_pretrained(name)
    model = AutoModelForCausalLM.from_pretrained(
        name,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map=_device() if torch.cuda.is_available() else None,
    )
    return pipeline("text-generation", model=model, tokenizer=tokenizer)


def build_prompt(question: str, chunks: list[dict], language: str = "en") -> str:
    context = "\n\n".join(
        f"[{c['metadata'].get('article', '?')}] {c['text']}" for c in chunks
    )
    lang_hint = "Respond in Arabic." if language == "ar" else "Respond in English."
    return textwrap.dedent(
        f"""\
        [INST] <<SYS>>
        {SYSTEM_PROMPT.strip()}
        {lang_hint}
        <</SYS>>

        Legal context:
        {context}

        User question: {question}
        [/INST]
        """
    )


def _fallback_answer(question: str, chunks: list[dict]) -> str:
    """If no LLM is available, stitch together the top retrieved articles.

    This keeps the demo functional on CPU-only machines without GPU weights.
    """
    if not chunks:
        return (
            "I could not find a relevant provision of the Palestinian Basic Law for your "
            f"question: {question!r}. {DISCLAIMER}"
        )
    lines = [
        "Based on the Palestinian Basic Law (2003, amended 2005), the following provisions apply:",
    ]
    for c in chunks:
        article = c["metadata"].get("article", "Article ?")
        lines.append(f"- {article}: {c['text']}")
    lines.append(DISCLAIMER)
    return "\n\n".join(lines)


def answer(question: str, *, language: str = "en", top_k: int = 3) -> dict[str, Any]:
    chunks = retrieve(question, top_k=top_k)
    prompt = build_prompt(question, chunks, language=language)

    try:
        pipe = _get_pipeline()
        output = pipe(
            prompt,
            max_new_tokens=_max_new_tokens(),
            temperature=_temperature(),
            do_sample=_temperature() > 0,
            return_full_text=False,
        )
        text = output[0]["generated_text"].strip() if output else ""
        if not text:
            text = _fallback_answer(question, chunks)
    except Exception as exc:  # pragma: no cover — model loading can fail for many reasons
        text = _fallback_answer(question, chunks)
        text += f"\n\n[note] model unavailable: {type(exc).__name__}"

    return AnswerResult(answer=text, sources=chunks, prompt=prompt).__dict__


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument("question")
    parser.add_argument("--lang", default="en", choices=["en", "ar"])
    parser.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args()
    result = answer(args.question, language=args.lang, top_k=args.top_k)
    print(json.dumps({"answer": result["answer"], "sources": [s["metadata"] for s in result["sources"]]}, ensure_ascii=False, indent=2))
