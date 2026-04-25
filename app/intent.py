"""Lightweight legal-intent classifier.

This keyword matcher is deliberately simple — it's fast, dependency-free,
and accurate enough to pick the right RAG filter buckets. Swap with a
fine-tuned classifier later if needed.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

INTENTS: dict[str, list[str]] = {
    "eviction": [
        "evict", "eviction", "landlord", "tenant", "rent", "lease", "housing",
        "أخلاء", "إخلاء", "مالك", "إيجار", "سكن",
    ],
    "labor": [
        "salary", "wage", "fired", "dismiss", "overtime", "union", "strike", "work hours", "labor",
        "راتب", "أجر", "طرد", "فصل", "نقابة", "إضراب", "عمل",
    ],
    "family": [
        "divorce", "custody", "marriage", "child support", "alimony", "inheritance",
        "طلاق", "حضانة", "زواج", "نفقة", "ميراث",
    ],
    "criminal": [
        # Basic Law + Penal Procedure Law No. 3/2001 keywords
        "arrest", "detain", "detained", "detention", "police", "torture", "charge", "charged",
        "lawyer", "counsel", "court", "warrant", "bail", "custody", "interrogat", "confession",
        "flagrant", "prosecution", "misdemean", "felony", "prison", "silent", "silence",
        "اعتقال", "احتجاز", "شرطة", "تعذيب", "تهمة", "محامٍ", "محامي", "محكمة",
        "مذكرة", "كفالة", "نيابة", "استجواب", "اعتراف", "صمت", "سجن", "جناية", "جنحة",
        "نيابة عامة", "قاضي صلح", "المتهم",
    ],
    "property": [
        "property", "land", "confiscate", "expropriate", "compensation",
        "ملكية", "أرض", "مصادرة", "تعويض",
    ],
    "emergency": [
        "state of emergency", "martial law", "curfew",
        "حالة طوارئ", "حظر تجول",
    ],
    "education": [
        "school", "university", "tuition", "education",
        "مدرسة", "جامعة", "تعليم",
    ],
    "discrimination": [
        "discriminat", "equal", "race", "religion", "gender",
        "تمييز", "مساواة", "دين",
    ],
}


@dataclass
class Intent:
    label: str
    confidence: float
    matched: list[str]


def classify(text: str) -> Intent:
    lowered = text.lower()
    scores: dict[str, tuple[int, list[str]]] = {}
    for label, kws in INTENTS.items():
        matches = [kw for kw in kws if re.search(re.escape(kw.lower()), lowered)]
        if matches:
            scores[label] = (len(matches), matches)

    if not scores:
        return Intent(label="general", confidence=0.0, matched=[])

    label, (hits, matches) = max(scores.items(), key=lambda kv: kv[1][0])
    total = sum(c for c, _ in scores.values())
    return Intent(label=label, confidence=hits / total, matched=matches)
