"""Local LLM inference wrapper with RAG-augmented prompting.

Lazy-loads the model so importing this module is cheap. Exports:

    answer(question, language="en") -> dict

The returned dict contains `answer`, `sources`, and `prompt` for inspection.

Speed notes
-----------
- The default model is auto-selected based on hardware and the requested
  language. On CPU we use a small instruction-tuned model so demos do not
  hang for minutes; on GPU we can afford a 7B legal model.
- Generation is greedy by default (do_sample=False) — legal answers benefit
  from determinism, and greedy is materially faster than sampling.
- On GPU we try to load the model in 4-bit (bitsandbytes) for ~3x speedup
  and ~4x lower VRAM. Falls back to fp16 if bnb is unavailable.
- Tokenizer chat templates are used when the model exposes one — the
  hand-rolled [INST] string is only used as a last resort.
"""
from __future__ import annotations

import os
import re
import textwrap
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from model.rag import retrieve

SYSTEM_PROMPT_EN = textwrap.dedent(
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

SYSTEM_PROMPT_AR = textwrap.dedent(
    """\
    أنت مساعد قانوني يساعد المواطنين الفلسطينيين على فهم حقوقهم
    بموجب القانون الأساسي الفلسطيني (2003، المعدل 2005).

    القواعد:
    - أجب فقط بناءً على السياق القانوني المُقدَّم.
    - استخدم لغة بسيطة وواضحة يفهمها الجميع.
    - اختم دائماً بالعبارة: "هذه معلومات قانونية عامة. لحالتك الخاصة،
      يُرجى استشارة محامٍ فلسطيني مُرخَّص أو زيارة مركز للمساعدة القانونية."
    - لا تقدم نصيحة قد تضر المستخدم.
    - إذا لم تكن الإجابة في المواد القانونية المُقدَّمة، أوضح ذلك بصراحة.
    - أجب باللغة العربية الفصحى.
    """
)

DISCLAIMER_EN = (
    "This is general legal information. For your specific situation, "
    "consult a licensed Palestinian lawyer or visit a legal aid center."
)

DISCLAIMER_AR = (
    "هذه معلومات قانونية عامة. لحالتك الخاصة، يُرجى استشارة "
    "محامٍ فلسطيني مُرخَّص أو زيارة مركز للمساعدة القانونية."
)

ARABIC_RE = re.compile(r"[؀-ۿݐ-ݿࢠ-ࣿ]")


@dataclass
class AnswerResult:
    answer: str
    sources: list[dict]
    prompt: str


def _has_cuda() -> bool:
    try:
        import torch
        return bool(torch.cuda.is_available())
    except Exception:
        return False


def _detect_language(text: str, hint: str | None = None) -> str:
    """Return 'ar' if the text contains Arabic script, else hint or 'en'."""
    if hint in ("ar", "en"):
        return hint
    return "ar" if ARABIC_RE.search(text or "") else "en"


def _default_model(language: str) -> str:
    """Pick a model based on language and available hardware.

    The user can always override with `LLM_MODEL`. Defaults:
      - GPU + Arabic   -> Qwen 2.5 7B Instruct (multilingual, strong AR)
      - GPU + English  -> Saul 7B Instruct (legal-tuned EN)
      - CPU + any      -> Qwen 2.5 1.5B Instruct (small, fast, multilingual)
    """
    if _has_cuda():
        return (
            "Qwen/Qwen2.5-7B-Instruct" if language == "ar"
            else "Equall/Saul-7B-Instruct-v1"
        )
    return "Qwen/Qwen2.5-1.5B-Instruct"


def _model_name(language: str = "en") -> str:
    return os.environ.get("LLM_MODEL") or _default_model(language)


def _llm_mode() -> str:
    """auto | llm | rag.

    "auto" (default) uses the LLM only if a GPU is available — running a
    7B legal model on CPU takes minutes per question, so on CPU we fall
    back to a stitched RAG answer that returns in milliseconds.
    """
    return os.environ.get("LLM_MODE", "auto").lower()


def _should_call_llm() -> bool:
    mode = _llm_mode()
    if mode == "llm":
        return True
    if mode == "rag":
        return False
    return _has_cuda()


def _max_new_tokens() -> int:
    return int(os.environ.get("LLM_MAX_NEW_TOKENS", "256"))


def _temperature() -> float:
    return float(os.environ.get("LLM_TEMPERATURE", "0.0"))


def _device_map() -> str:
    return os.environ.get("LLM_DEVICE", "auto")


def _load_4bit_kwargs():
    """4-bit quantization via bitsandbytes for fast GPU inference."""
    try:
        from transformers import BitsAndBytesConfig
        import torch
        return {
            "quantization_config": BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
            )
        }
    except Exception:
        return None


@lru_cache(maxsize=2)
def _get_pipeline(name: str):
    """Lazily load a text-generation pipeline keyed by model name."""
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    import torch

    tokenizer = AutoTokenizer.from_pretrained(name)
    if tokenizer.pad_token_id is None and tokenizer.eos_token_id is not None:
        tokenizer.pad_token_id = tokenizer.eos_token_id

    use_cuda = torch.cuda.is_available()
    load_kwargs: dict[str, Any] = {}
    if use_cuda:
        bnb = _load_4bit_kwargs()
        if bnb is not None:
            load_kwargs.update(bnb)
        else:
            load_kwargs["torch_dtype"] = torch.float16
        load_kwargs["device_map"] = _device_map()
    else:
        load_kwargs["torch_dtype"] = torch.float32

    model = AutoModelForCausalLM.from_pretrained(name, **load_kwargs)
    if hasattr(model, "config"):
        model.config.use_cache = True
    return pipeline("text-generation", model=model, tokenizer=tokenizer)


@lru_cache(maxsize=2)
def _get_tokenizer(name: str):
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained(name)


def build_prompt(question: str, chunks: list[dict], language: str = "en") -> str:
    """Build a chat-style prompt. Uses the tokenizer's chat template when available."""
    context = "\n\n".join(
        f"[{c['metadata'].get('article', '?')}] {c['text']}" for c in chunks
    )
    system = SYSTEM_PROMPT_AR.strip() if language == "ar" else SYSTEM_PROMPT_EN.strip()
    user = (
        f"السياق القانوني:\n{context}\n\nسؤال المستخدم: {question}"
        if language == "ar"
        else f"Legal context:\n{context}\n\nUser question: {question}"
    )

    try:
        tok = _get_tokenizer(_model_name(language))
        if getattr(tok, "chat_template", None):
            return tok.apply_chat_template(
                [{"role": "system", "content": system},
                 {"role": "user", "content": user}],
                tokenize=False,
                add_generation_prompt=True,
            )
    except Exception:
        pass

    return f"[INST] <<SYS>>\n{system}\n<</SYS>>\n\n{user}\n[/INST]\n"


def _fallback_answer(question: str, chunks: list[dict], language: str = "en") -> str:
    """If no LLM is available, stitch together the top retrieved articles."""
    disclaimer = DISCLAIMER_AR if language == "ar" else DISCLAIMER_EN
    if not chunks:
        if language == "ar":
            return (
                "لم أتمكن من العثور على نص ذي صلة في القانون الأساسي الفلسطيني "
                f"لسؤالك: {question!r}. {disclaimer}"
            )
        return (
            "I could not find a relevant provision of the Palestinian Basic Law for your "
            f"question: {question!r}. {disclaimer}"
        )
    if language == "ar":
        lines = ["استناداً إلى القانون الأساسي الفلسطيني (2003، المعدل 2005)، تنطبق الأحكام التالية:"]
    else:
        lines = ["Based on the Palestinian Basic Law (2003, amended 2005), the following provisions apply:"]
    for c in chunks:
        article = c["metadata"].get("article", "Article ?")
        lines.append(f"- {article}: {c['text']}")
    lines.append(disclaimer)
    return "\n\n".join(lines)


def answer(question: str, *, language: str | None = "en", top_k: int = 3) -> dict[str, Any]:
    language = _detect_language(question, hint=language)
    chunks = retrieve(question, top_k=top_k)

    # Fast path: on CPU (or when LLM_MODE=rag) skip the model entirely. The
    # stitched RAG answer is verbatim Basic Law text — perfectly accurate
    # for legal information and returns in milliseconds.
    if not _should_call_llm():
        text = _fallback_answer(question, chunks, language=language)
        return AnswerResult(answer=text, sources=chunks, prompt="").__dict__

    prompt = build_prompt(question, chunks, language=language)
    try:
        pipe = _get_pipeline(_model_name(language))
        temp = _temperature()
        gen_kwargs: dict[str, Any] = {
            "max_new_tokens": _max_new_tokens(),
            "return_full_text": False,
            "pad_token_id": pipe.tokenizer.pad_token_id,
            "use_cache": True,
        }
        if temp > 0:
            gen_kwargs.update(do_sample=True, temperature=temp, top_p=0.9)
        else:
            gen_kwargs.update(do_sample=False)
        output = pipe(prompt, **gen_kwargs)
        text = output[0]["generated_text"].strip() if output else ""
        if not text:
            text = _fallback_answer(question, chunks, language=language)
    except Exception as exc:  # pragma: no cover — model loading can fail for many reasons
        text = _fallback_answer(question, chunks, language=language)
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
    print(json.dumps(
        {"answer": result["answer"], "sources": [s["metadata"] for s in result["sources"]]},
        ensure_ascii=False, indent=2,
    ))
