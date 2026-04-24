"""PDF form generation for common legal documents.

Generates fillable demand letters / complaints using reportlab. These are
simple single-page templates designed to be starting points that users
can adapt before filing.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _output_dir() -> Path:
    d = Path(os.environ.get("FORM_OUTPUT_DIR", ROOT / "data" / "forms" / "filled"))
    d.mkdir(parents=True, exist_ok=True)
    return d


@dataclass
class FormRequest:
    form_type: str  # e.g. "eviction_response", "labor_complaint"
    fields: dict[str, str]


def _header(canvas, title: str) -> None:
    canvas.setFont("Helvetica-Bold", 16)
    canvas.drawString(72, 760, title)
    canvas.setFont("Helvetica", 9)
    canvas.drawString(72, 745, f"Generated: {date.today().isoformat()}")
    canvas.line(72, 740, 540, 740)


def _wrap(canvas, text: str, x: int, y: int, width: int = 460, leading: int = 14) -> int:
    """Draw wrapped text, return the final y position."""
    from reportlab.pdfbase.pdfmetrics import stringWidth

    canvas.setFont("Helvetica", 11)
    words = text.split()
    line: list[str] = []
    for word in words:
        trial = " ".join(line + [word])
        if stringWidth(trial, "Helvetica", 11) > width and line:
            canvas.drawString(x, y, " ".join(line))
            y -= leading
            line = [word]
        else:
            line.append(word)
    if line:
        canvas.drawString(x, y, " ".join(line))
        y -= leading
    return y


_TEMPLATES: dict[str, dict[str, str]] = {
    "eviction_response": {
        "title": "Response to Eviction Notice",
        "body": (
            "To the landlord, {landlord_name},\n\n"
            "I, {tenant_name}, residing at {address}, received a verbal notice on "
            "{notice_date} directing me to vacate the property within {notice_period} days.\n\n"
            "Under the Palestinian Basic Law (2003, amended 2005) — specifically Articles 17, 21, "
            "23 and 30 — my right to housing and the inviolability of my home are protected. "
            "A verbal notice has no standing; any eviction must follow written notice and a "
            "proper judicial procedure. I hereby reserve my right to contest this notice before "
            "the competent court.\n\n"
            "Please direct any further communication in writing to the address above.\n\n"
            "Sincerely,\n{tenant_name}"
        ),
    },
    "labor_complaint": {
        "title": "Labor Complaint",
        "body": (
            "To the Ministry of Labor,\n\n"
            "I, {employee_name}, am filing a complaint against my employer, {employer_name}, "
            "regarding the following matter: {issue_summary}.\n\n"
            "Under Article 25 of the Palestinian Basic Law (2003, amended 2005), work is a right "
            "and labor relationships must guarantee justice, welfare, and social benefits. I "
            "respectfully request an investigation and remedy under Palestinian Labour Law No. 7 "
            "of 2000.\n\n"
            "Sincerely,\n{employee_name}"
        ),
    },
    "detention_rights_notice": {
        "title": "Notice of Rights Upon Detention",
        "body": (
            "To the detaining authority,\n\n"
            "Regarding the detention of {detainee_name} on {detention_date}, I assert the "
            "following rights under the Palestinian Basic Law (2003, amended 2005):\n\n"
            "- Article 11: arrest only by judicial order, and only in places designated by law.\n"
            "- Article 12: the detainee must be informed of the charges in a language they "
            "understand, and must have immediate access to a lawyer.\n"
            "- Article 13: any statement obtained under duress or torture is null and void.\n"
            "- Article 14: the detainee is presumed innocent and must be represented by a lawyer.\n\n"
            "I request immediate confirmation of these rights and access to {detainee_name}.\n\n"
            "Sincerely,\n{filer_name}"
        ),
    },
}


def available_forms() -> list[str]:
    return sorted(_TEMPLATES.keys())


def generate_pdf(form_type: str, fields: dict[str, str], out_path: str | None = None) -> str:
    from reportlab.pdfgen import canvas

    tpl = _TEMPLATES.get(form_type)
    if not tpl:
        raise ValueError(f"unknown form_type: {form_type!r}. Available: {available_forms()}")

    body = tpl["body"]
    missing = [k for k in _required_fields(body) if k not in fields]
    if missing:
        raise ValueError(f"missing fields for {form_type}: {missing}")

    filled_body = body.format(**fields)
    out = Path(out_path) if out_path else _output_dir() / f"{form_type}_{date.today().isoformat()}.pdf"

    c = canvas.Canvas(str(out))
    _header(c, tpl["title"])
    y = 720
    for paragraph in filled_body.split("\n\n"):
        y = _wrap(c, paragraph.replace("\n", " "), 72, y) - 8
        if y < 100:
            c.showPage()
            _header(c, tpl["title"])
            y = 720
    c.save()
    return str(out)


def _required_fields(body: str) -> list[str]:
    import string

    fields: list[str] = []
    for _, field, _, _ in string.Formatter().parse(body):
        if field:
            fields.append(field)
    return fields
