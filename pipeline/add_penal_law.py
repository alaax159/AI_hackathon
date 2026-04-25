"""
Add Palestinian Penal Procedure Law No. 3 of 2001 articles to the RAG data files
and rebuild the ChromaDB vector store.

Run: python -m pipeline.add_penal_law
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLES_FILE  = ROOT / "data" / "processed" / "articles.jsonl"
CHUNKS_FILE    = ROOT / "data" / "processed" / "rag_chunks.jsonl"

SOURCE = "Penal Procedure Law No. 3 of 2001"

PENAL_ARTICLES = [
    # ── BOOK ONE: CRIMINAL ACTION ──────────────────────────────────────────
    {
        "article": "Article 1",
        "title": "BOOK ONE — CRIMINAL ACTION",
        "text": "The right to file and conduct a criminal action shall be vested exclusively with the Public Prosecution.",
        "keywords": ["criminal action", "prosecution", "public prosecution", "ملاحقة جزائية", "نيابة عامة"],
    },
    {
        "article": "Article 12",
        "title": "BOOK ONE — PRESCRIPTION PERIODS",
        "text": "The criminal action shall lapse by prescription after the following periods: ten (10) years for felonies, three (3) years for misdemeanours, and one (1) year for contraventions, calculated from the date of the criminal act.",
        "keywords": ["prescription", "statute of limitations", "felony", "misdemeanor", "تقادم", "جناية", "جنحة"],
    },
    # ── FLAGRANT CRIMES ────────────────────────────────────────────────────
    {
        "article": "Article 26",
        "title": "BOOK ONE — FLAGRANT CRIMES",
        "text": "A crime shall be deemed flagrant if it is being committed at the moment it is discovered, or has just been committed. It shall also be deemed flagrant if the perpetrator is pursued by public clamour immediately after its commission, or is found shortly thereafter carrying weapons, tools, or objects that give rise to the presumption of his participation in the crime.",
        "keywords": ["flagrant", "in the act", "fresh pursuit", "جريمة مشهودة", "تلبس"],
    },
    # ── ARREST ────────────────────────────────────────────────────────────
    {
        "article": "Article 29",
        "title": "BOOK ONE — ARREST OF THE ACCUSED",
        "text": "No person may be arrested or imprisoned except by order of the competent authority as set forth in the law. Every person arrested shall be treated in a manner that preserves his human dignity, and shall not be subjected to any physical or mental harm.",
        "keywords": ["arrest", "detention", "warrant", "human dignity", "اعتقال", "احتجاز", "مذكرة", "كرامة إنسانية"],
    },
    {
        "article": "Article 30",
        "title": "BOOK ONE — ARREST OF THE ACCUSED",
        "text": "Judicial officers may arrest the accused without a warrant in the following cases: if there is sufficient evidence that a flagrant felony or misdemeanour has been committed; if the accused resists or attempts to resist the officer; or if the accused is found without identification.",
        "keywords": ["warrantless arrest", "flagrant", "judicial officer", "اعتقال بلا مذكرة", "جريمة مشهودة"],
    },
    {
        "article": "Article 31",
        "title": "BOOK ONE — ARREST OF THE ACCUSED",
        "text": "Judicial officers may obtain arrest warrants from the Public Prosecution for felonies and serious misdemeanours when sufficient evidence exists. The warrant shall state the name of the accused, the charge, and the authority issuing the warrant.",
        "keywords": ["arrest warrant", "public prosecution", "felony", "مذكرة اعتقال", "جناية", "نيابة عامة"],
    },
    {
        "article": "Article 32",
        "title": "BOOK ONE — ARREST OF THE ACCUSED",
        "text": "Any person who witnesses a flagrant felony or misdemeanour shall be empowered to arrest the perpetrator and deliver him to the nearest judicial officer or police station without delay.",
        "keywords": ["citizen arrest", "flagrant", "police station", "قبض مواطن", "جريمة مشهودة"],
    },
    {
        "article": "Article 34",
        "title": "BOOK ONE — ARREST OF THE ACCUSED",
        "text": "The judicial officer shall hear the statement of the arrested person immediately, and if the matter cannot be resolved, shall send him together with the minutes of arrest to the competent Deputy-Prosecutor within twenty-four (24) hours of arrest.",
        "keywords": ["24 hours", "statement", "deputy prosecutor", "24 ساعة", "إفادة", "نائب نيابة"],
    },
    {
        "article": "Article 35",
        "title": "BOOK ONE — ARREST OF THE ACCUSED",
        "text": "The judicial officer may use the appropriate force necessary to effect an arrest when the accused resists or attempts to flee. Force shall be proportionate to the situation and must not be excessive.",
        "keywords": ["use of force", "arrest", "resistance", "استخدام القوة", "مقاومة الاعتقال"],
    },
    # ── SEARCH ────────────────────────────────────────────────────────────
    {
        "article": "Article 39",
        "title": "BOOK ONE — SEARCH OF HOMES",
        "text": "No home may be searched except by a written warrant issued by the Public Prosecution or in its presence. The warrant shall be issued based upon an accusation directed at the occupant of the home or upon compelling evidence that a person involved in a crime or objects related to it are concealed therein.",
        "keywords": ["home search", "search warrant", "public prosecution", "تفتيش المنزل", "مذكرة تفتيش", "نيابة عامة"],
    },
    {
        "article": "Article 47",
        "title": "BOOK ONE — SEARCH OF HOMES",
        "text": "The search of a female person shall be conducted only by a female officer or a female designated for this purpose. The dignity and privacy of the female searched shall be fully respected throughout the procedure.",
        "keywords": ["female search", "privacy", "dignity", "تفتيش أنثى", "خصوصية", "كرامة"],
    },
    {
        "article": "Article 52",
        "title": "BOOK ONE — SEARCH OF HOMES",
        "text": "Any search conducted in violation of the provisions of this law shall be considered null and void, and any evidence obtained through such an unlawful search shall not be admissible as evidence in any criminal proceeding.",
        "keywords": ["illegal search", "null", "void", "inadmissible evidence", "تفتيش غير مشروع", "بطلان", "دليل مرفوض"],
    },
    # ── INVESTIGATION / INTERROGATION RIGHTS ──────────────────────────────
    {
        "article": "Article 96",
        "title": "BOOK ONE — INTERROGATION RIGHTS",
        "text": "When the accused appears before the Deputy-Prosecutor for interrogation, the Deputy-Prosecutor shall first establish his identity and inform him of the charges attributed to him. The accused shall be notified of his right to retain legal counsel before being interrogated. The accused shall also be warned that anything he states may be used as evidence against him.",
        "keywords": ["interrogation", "right to counsel", "charges", "Miranda rights", "notification", "استجواب", "حق التمثيل القانوني", "إخطار بالتهم"],
    },
    {
        "article": "Article 97",
        "title": "BOOK ONE — INTERROGATION RIGHTS",
        "text": "The accused shall have the right to remain silent and not to respond to any questions put to him. His silence may not be construed as an admission of any charge, and no adverse inference may be drawn from his exercise of the right to silence.",
        "keywords": ["right to silence", "remain silent", "no adverse inference", "حق الصمت", "لا إقرار من الصمت"],
    },
    {
        "article": "Article 102",
        "title": "BOOK ONE — RIGHT TO COUNSEL DURING INVESTIGATION",
        "text": "The accused shall have the right to seek the assistance of counsel during the investigation. The counsel shall have the right to review the preceding minutes of investigation and to submit written memoranda containing his observations and demands to the Deputy-Prosecutor.",
        "keywords": ["right to counsel", "lawyer", "investigation", "legal representation", "حق في محامٍ", "تمثيل قانوني", "التحقيق"],
    },
    # ── CUSTODY AND PROVISIONAL DETENTION ─────────────────────────────────
    {
        "article": "Article 103",
        "title": "BOOK ONE — COMMUNICATION BAN",
        "text": "The Attorney-General may decide to ban communication with the accused for a period not to exceed ten (10) days, subject to renewal once only for the same period. This measure shall not prevent the accused from communicating with his legal counsel at any time.",
        "keywords": ["communication ban", "isolation", "attorney general", "legal counsel", "حظر التواصل", "عزل", "المحامي"],
    },
    {
        "article": "Article 115",
        "title": "BOOK ONE — CUSTODY AND PROVISIONAL DETENTION",
        "text": "A judicial officer shall deliver an arrested person promptly to the nearest police station following the arrest, and shall prepare a detailed report of the arrest including the time, place, circumstances, and the charges upon which the arrest is based.",
        "keywords": ["police station", "arrest report", "custody", "مركز شرطة", "تقرير اعتقال", "حجز"],
    },
    {
        "article": "Article 119",
        "title": "BOOK ONE — CUSTODY AND PROVISIONAL DETENTION",
        "text": "The Deputy-Prosecutor may request the competent Magistrate Judge to extend the detention of the accused for a period not to exceed fifteen (15) days when necessary for the completion of the investigation. This extension shall not be granted unless the investigation requires it.",
        "keywords": ["detention extension", "magistrate", "15 days", "investigation", "تمديد الاحتجاز", "قاضي صلح", "15 يوماً"],
    },
    {
        "article": "Article 120",
        "title": "BOOK ONE — CUSTODY AND PROVISIONAL DETENTION",
        "text": "The Magistrate Judge may detain the accused for periods not to exceed fifteen (15) days each, renewable, provided the total aggregate detention period during investigation does not exceed forty-five (45) days. In no case may the detention period exceed the penalty prescribed for the offence charged.",
        "keywords": ["maximum detention", "45 days", "investigation", "Magistrate", "أقصى مدة احتجاز", "45 يوماً", "قاضي صلح"],
    },
    {
        "article": "Article 123",
        "title": "BOOK ONE — DETAINEE RIGHTS",
        "text": "Every detainee shall have the right to contact his family members immediately upon detention and to consult privately with his legal counsel at any time. No authority may prevent or obstruct the exercise of this right.",
        "keywords": ["detainee rights", "contact family", "legal counsel", "right to communicate", "حقوق المعتقل", "التواصل مع الأسرة", "محامٍ"],
    },
    {
        "article": "Article 124",
        "title": "BOOK ONE — DETAINEE RIGHTS",
        "text": "The prison warden shall not allow communication with the detainee except with written permission from the Public Prosecution. However, this restriction shall not apply to communications between the detainee and his legal counsel, which must be allowed at all times without conditions or monitoring.",
        "keywords": ["prison warden", "communication permission", "legal counsel", "unrestricted access", "مدير السجن", "إذن التواصل", "المحامي"],
    },
    {
        "article": "Article 125",
        "title": "BOOK ONE — LAWFUL DETENTION",
        "text": "No person may be detained or imprisoned except in a Correctional and Rehabilitation Centre or in a place designated for that purpose by law. Detention in any other location is unlawful and constitutes a criminal offence.",
        "keywords": ["lawful detention", "prison", "correctional centre", "illegal detention", "احتجاز مشروع", "سجن", "احتجاز غير قانوني"],
    },
    # ── BAIL ──────────────────────────────────────────────────────────────
    {
        "article": "Article 130",
        "title": "BOOK ONE — BAIL AND PROVISIONAL RELEASE",
        "text": "An accused may not be released on bail unless he designates an elected domicile within the jurisdiction of the court in charge of the case. The court shall determine the bail amount based upon the gravity of the charge and the personal circumstances of the accused.",
        "keywords": ["bail", "provisional release", "domicile", "court jurisdiction", "كفالة", "إفراج مؤقت", "موطن مختار"],
    },
    {
        "article": "Article 131",
        "title": "BOOK ONE — BAIL AND PROVISIONAL RELEASE",
        "text": "A petition for the release on bail of an unarraigned accused shall be submitted to the judge authorised to issue the order. The judge shall examine the petition within forty-eight (48) hours of submission and may grant bail, deny it, or request additional information.",
        "keywords": ["bail petition", "release", "judge", "48 hours", "طلب الإفراج بكفالة", "قاضي", "48 ساعة"],
    },
    # ── BOOK TWO: TRIAL — EVIDENCE ────────────────────────────────────────
    {
        "article": "Article 211",
        "title": "BOOK TWO — EVIDENCE AND ATTORNEY-CLIENT PRIVILEGE",
        "text": "Communications and information exchanged between the accused and his counsel in connection with the criminal case shall be confidential and shall not be admitted as evidence in any proceedings. The attorney-client privilege shall not be waived except by the accused himself.",
        "keywords": ["attorney-client privilege", "confidentiality", "counsel", "evidence", "السرية المهنية", "محامٍ", "دليل"],
    },
    {
        "article": "Article 214",
        "title": "BOOK TWO — CONFESSION AND EVIDENCE",
        "text": "A confession shall be valid and admissible as evidence only if it is made voluntarily and freely, without any form of coercion, duress, or promise of benefit. The confession must correspond to the actual circumstances of the crime and must constitute a complete and unequivocal acknowledgment of the charge.",
        "keywords": ["confession", "voluntary", "coercion", "duress", "admissible", "اعتراف", "طوعي", "إكراه", "قبول كدليل"],
    },
    {
        "article": "Article 217",
        "title": "BOOK TWO — RIGHT TO SILENCE AT TRIAL",
        "text": "The accused shall have the right to remain silent at trial and to refuse to answer any questions. His silence or refusal to answer shall not be construed as a confession or as evidence of guilt, and the court may not draw any adverse inference from the exercise of this right.",
        "keywords": ["right to silence", "trial", "no adverse inference", "guilt", "حق الصمت في المحاكمة", "لا يُعدّ اعترافاً"],
    },
    # ── BOOK TWO: TRIAL PROCEDURES ────────────────────────────────────────
    {
        "article": "Article 237",
        "title": "BOOK TWO — TRIAL PROCEDURES",
        "text": "Trials shall be conducted in public unless the court determines that public proceedings would be contrary to public order or morality, or that the privacy of a party requires a closed session. The accused and his counsel shall have the right to attend all sessions of the trial.",
        "keywords": ["public trial", "open court", "accused attendance", "defence counsel", "محاكمة علنية", "حضور المتهم", "المحامٍ"],
    },
    {
        "article": "Article 244",
        "title": "BOOK TWO — RIGHT TO DEFENCE COUNSEL",
        "text": "The accused in a felony case shall be represented by defence counsel. If the accused does not appoint counsel, the court shall appoint one for him at the expense of the State. The court-appointed counsel shall have adequate time to prepare his defence.",
        "keywords": ["defence counsel", "felony", "state-appointed lawyer", "court-appointed", "محامي دفاع", "جناية", "محامٍ معيّن من المحكمة"],
    },
    {
        "article": "Article 246",
        "title": "BOOK TWO — ACCUSED RIGHTS AT TRIAL",
        "text": "Before the commencement of trial, the accused shall be informed in a language he understands of: the charges attributed to him, his right to remain silent, his right to legal representation, and his right to call witnesses on his behalf.",
        "keywords": ["accused rights", "charges", "right to silence", "legal representation", "witnesses", "حقوق المتهم", "التهم", "الصمت", "التمثيل القانوني"],
    },
    {
        "article": "Article 273",
        "title": "BOOK TWO — JUDGMENT AND EVIDENCE",
        "text": "The court shall base its judgment solely on evidence presented and discussed during the trial. Any statement obtained through coercion, torture, threat, or unlawful inducement shall be disregarded and shall not be relied upon in forming the judgment.",
        "keywords": ["judgment", "evidence", "coercion", "torture", "unlawful", "حكم", "دليل", "إكراه", "تعذيب", "اعتراف منتزع بالإكراه"],
    },
]


def article_id(art: dict) -> str:
    num = art["article"].replace("Article ", "").strip()
    return f"penal_procedure_law_Article_{num}"


def to_articles_jsonl(art: dict) -> str:
    return json.dumps({
        "id":      article_id(art),
        "title":   art["title"],
        "text":    art["text"],
        "article": art["article"],
        "source":  SOURCE,
    }, ensure_ascii=False)


def to_rag_chunk(art: dict) -> str:
    chunk_text = f"{art['article']} ({art['title']}): {art['text']}"
    return json.dumps({
        "id":   article_id(art),
        "text": chunk_text,
        "metadata": {
            "source":   SOURCE,
            "article":  art["article"],
            "title":    art["title"],
            "keywords": art.get("keywords", []),
        },
    }, ensure_ascii=False)


def _existing_ids(path: Path) -> set[str]:
    ids = set()
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    ids.add(json.loads(line)["id"])
    return ids


def main() -> None:
    existing_articles = _existing_ids(ARTICLES_FILE)
    existing_chunks   = _existing_ids(CHUNKS_FILE)

    added = 0
    with ARTICLES_FILE.open("a", encoding="utf-8") as af, \
         CHUNKS_FILE.open("a", encoding="utf-8") as cf:
        for art in PENAL_ARTICLES:
            aid = article_id(art)
            if aid not in existing_articles:
                af.write(to_articles_jsonl(art) + "\n")
                existing_articles.add(aid)
            if aid not in existing_chunks:
                cf.write(to_rag_chunk(art) + "\n")
                existing_chunks.add(aid)
                added += 1

    print(f"[add_penal_law] added {added} new penal procedure law articles")

    # Rebuild vector store
    print("[add_penal_law] rebuilding ChromaDB vector store...")
    sys.path.insert(0, str(ROOT))
    from model.rag import build
    n = build()
    print(f"[add_penal_law] vector store rebuilt with {n} total chunks")


if __name__ == "__main__":
    main()
