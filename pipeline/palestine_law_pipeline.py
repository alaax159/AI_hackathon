"""Palestinian Basic Law data pipeline.

Fetches (or loads offline) the Palestinian Basic Law (2003, amended 2005),
parses it into articles, and emits three artefacts:

    data/processed/articles.jsonl      — {id, title, text}
    data/processed/training_qa.jsonl   — {instruction, response, source, article}
    data/processed/rag_chunks.jsonl    — {id, text, metadata}

Run:
    python -m pipeline.palestine_law_pipeline
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
RAW_FILE = RAW_DIR / "palestine_basic_law_en.txt"

DISCLAIMER = (
    "This is general legal information. For your specific situation, "
    "consult a licensed Palestinian lawyer or visit a legal aid center."
)

# Sectional titles used by the Palestinian Basic Law.
TITLES: dict[int, str] = {
    1: "TITLE ONE — THE PALESTINIAN NATIONAL AUTHORITY",
    9: "TITLE TWO — PUBLIC RIGHTS AND LIBERTIES",
    34: "TITLE THREE — THE LEGISLATIVE AUTHORITY",
    63: "TITLE FOUR — THE EXECUTIVE AUTHORITY",
    97: "TITLE FIVE — THE JUDICIAL AUTHORITY",
    108: "TITLE SIX — FINANCIAL AFFAIRS",
    110: "TITLE SEVEN — SECURITY FORCES AND POLICE",
    113: "TITLE EIGHT — STATE OF EMERGENCY PROVISIONS",
    118: "TITLE NINE — GENERAL AND TRANSITIONAL PROVISIONS",
}

# Keyword tags per article — used to boost RAG metadata filters.
ARTICLE_TOPICS: dict[int, list[str]] = {
    9: ["equality", "discrimination", "non-discrimination"],
    10: ["human rights", "international conventions"],
    11: ["arrest", "freedom", "detention", "judicial order"],
    12: ["detention", "lawyer", "right to counsel", "charges"],
    13: ["torture", "coercion", "confession", "ill-treatment"],
    14: ["innocence", "presumption", "fair trial", "lawyer"],
    15: ["collective punishment", "personal responsibility"],
    16: ["deportation", "exile", "residence"],
    17: ["home", "search", "warrant", "privacy"],
    18: ["religion", "belief", "worship"],
    19: ["expression", "opinion", "speech"],
    20: ["movement", "residence", "travel"],
    21: ["property", "expropriation", "compensation"],
    22: ["social services", "welfare", "insurance", "martyrs"],
    23: ["housing", "shelter"],
    24: ["education", "literacy", "free education"],
    25: ["work", "labor", "wages", "unions"],
    26: ["political rights", "assembly", "parties"],
    27: ["press", "media", "publication"],
    28: ["citizenship", "nationality"],
    29: ["child", "children", "motherhood"],
    30: ["courts", "access to justice", "litigation"],
    31: ["human rights commission"],
    32: ["rights enforcement", "redress"],
    33: ["environment"],
    110: ["state of emergency", "declaration"],
    111: ["emergency powers", "rights suspension"],
    112: ["emergency parliamentary review"],
    113: ["emergency oversight"],
}


# ---------------------------------------------------------------------------
# Canonical article text (English) — paraphrased from the public-domain
# Palestinian Basic Law 2003 as amended 2005. Kept here so the pipeline runs
# without network access. If the raw HTML/PDF is downloaded into
# data/raw/palestine_basic_law_en.txt, that text is preferred.
# ---------------------------------------------------------------------------

BASIC_LAW_ARTICLES: list[tuple[int, str]] = [
    (1, "Palestine is part of the larger Arab World, and the Palestinian people are part of the Arab Nation. Arab unity is an objective that the Palestinian people shall work to achieve."),
    (2, "The people are the source of powers, which shall be exercised through the legislative, executive, and judicial authorities, based upon the principle of separation of powers, in the manner set forth in this Basic Law."),
    (3, "Jerusalem is the capital of Palestine."),
    (4, "Islam is the official religion in Palestine. Respect and sanctity of all other heavenly religions shall be maintained. The principles of Islamic Shari'a shall be a principal source of legislation. Arabic shall be the official language."),
    (5, "The system of government in Palestine shall be a democratic parliamentary system based upon political and party pluralism. The President of the National Authority shall be directly elected by the people. The government shall be accountable to the President and to the Palestinian Legislative Council."),
    (6, "The principle of the rule of law shall be the basis of government in Palestine. All governmental powers, agencies, institutions, and individuals shall be subject to the law."),
    (7, "Palestinian citizenship shall be regulated by law."),
    (8, "The flag of Palestine shall consist of four colors and shall be regulated by law."),
    (9, "Palestinians shall be equal before the law and the judiciary, without distinction based upon race, sex, color, religion, political views, or disability."),
    (10, "Basic human rights and liberties shall be protected and respected. The Palestinian National Authority shall work without delay to become a party to regional and international declarations and covenants that protect human rights."),
    (11, "Personal freedom is a natural right, shall be guaranteed and may not be violated. It is unlawful to arrest, search, imprison, restrict the freedom, or prevent the movement of any person, except by judicial order in accordance with the provisions of the law. The law shall determine the period of prearrest detention. Imprisonment or detention is only permitted in places subject to laws pertaining to the organization of prisons."),
    (12, "Any arrested or detained person shall be informed of the reasons for his arrest or detention. He shall be promptly informed, in a language he understands, of the charges brought against him. He shall have the right to contact a lawyer and to be tried without delay before a court of law."),
    (13, "No person shall be subject to any duress or torture. Indictees and all persons deprived of their freedom shall receive proper treatment. All statements or confessions obtained through violation of the provisions of the first paragraph of this Article shall be considered null and void."),
    (14, "An accused person is considered innocent until proven guilty in a court of law that guarantees him the right to defend himself. Any person accused in a criminal case shall be represented by a lawyer."),
    (15, "Punishment shall only be imposed on individuals. Collective punishment is prohibited. Crime and punishment shall only be determined by the law. Punishment shall be imposed only by a judicial ruling and shall apply only to acts committed after the effective date of the law."),
    (16, "It is prohibited to carry out any medical or scientific experiment on any person without prior legal consent. No person shall be subject to medical examination, treatment or surgery, except in accordance with the law. Transplantation of human organs and new scientific developments shall be regulated by law."),
    (17, "Homes shall be inviolable; they may not be subject to surveillance, entered, or searched, except in accordance with a valid judicial order and pursuant to the provisions of the law. Any consequences resulting from violations of this Article shall be considered invalid, and whoever is affected by such violations shall be entitled to fair remedy, guaranteed by the Palestinian National Authority."),
    (18, "Freedom of belief, worship and the performance of religious rites are guaranteed, provided they do not violate public order or public morals."),
    (19, "Freedom of opinion may not be prejudiced. Every person shall have the right to express his opinion and to circulate it orally, in writing, or in any form of expression or art, with due consideration to the provisions of the law."),
    (20, "Freedom of residence and movement shall be guaranteed within the limits of the law."),
    (21, "The economic system in Palestine shall be based on the principles of a free market economy. Private property, whether real estate or movable property, shall be protected. It shall not be expropriated except in the public interest and for a fair compensation in accordance with the law, or pursuant to a judicial ruling. Confiscation of property shall be permitted only by a judicial ruling."),
    (22, "Social, health, disability and retirement insurance shall be regulated by law. Maintaining the welfare of families of martyrs, prisoners of war, the injured and the disabled is a duty that shall be regulated by law. The Palestinian National Authority shall guarantee these persons education, health and social insurance."),
    (23, "Proper housing is a right for every citizen. The Palestinian National Authority shall secure housing for those who are without shelter."),
    (24, "Education is a right for every citizen, and shall be compulsory until at least the end of the basic level. Education shall be free in public schools and institutions. The National Authority shall supervise all levels of education and its institutions, and shall strive to upgrade the educational system. The law shall guarantee the independence of universities, institutes of higher education, and scientific research centers."),
    (25, "Work is a right, a duty, and an honor. The Palestinian National Authority shall strive to provide it to every citizen able to perform it. Work relationships shall be organized in a manner that guarantees justice to all and provides workers with welfare, security, and health and social benefits. Every person shall have the right to join unions to protect his interests. The right to strike shall be exercised within the limits of the law."),
    (26, "Palestinians shall have the right to participate in political life, both as individuals and as groups. They shall have the right to form, establish and join political parties, unions and associations in accordance with the law, and the right to hold private meetings without police presence."),
    (27, "The establishment of newspapers and all media means is a right for all, guaranteed by this Basic Law. Their financing resources shall be subject to the scrutiny of the law. Freedom of audio, visual, and written media, as well as freedom to print, publish, distribute and transmit, together with the freedom of individuals working in this field, shall be guaranteed by this Basic Law and other related laws."),
    (28, "No Palestinian may be deported from the homeland, prevented or prohibited from returning to it, banned from leaving it, stripped of his citizenship, or handed over to any foreign entity."),
    (29, "Maternity and childhood welfare are national duties. Children shall have the right to comprehensive protection and welfare, not to be exploited for any purpose, not to be allowed to perform work that might damage their safety, health or education, to be protected from harmful and cruel treatment, to be separated from adults when detained, and to receive legal assistance."),
    (30, "Submitting a case to court is a safeguarded and guaranteed right for all people. Each Palestinian shall have the right to seek redress from his natural judge. The law shall regulate judicial procedures in a manner that ensures the rapid settlement of cases. Laws may not contain any provisions that provide immunity against any civil or criminal action or penalty arising from a wrongful act."),
    (31, "An Independent Commission for Human Rights shall be established pursuant to a law that will specify its formation, duties, and jurisdiction. The Commission shall submit its reports to the President of the National Authority and to the Palestinian Legislative Council."),
    (32, "Any violation of any personal freedom, of the sanctity of the private life of human beings, or of any of the rights or liberties that have been guaranteed by law or by this Basic Law shall be considered a crime, and civil and criminal cases resulting from such violations may not be subject to any statute of limitations. The National Authority shall guarantee a fair remedy to those who suffered from such damage."),
    (33, "A balanced and clean environment is a human right. The preservation and protection of the Palestinian environment from pollution for the sake of present and future generations is a national duty."),
    (97, "The judicial authority shall be independent and shall be exercised by the courts of different kinds and levels. The law shall determine the manner of their formation and their jurisdiction. They shall issue their rulings in accordance with the law. Judgments shall be announced and executed in the name of the Palestinian Arab People."),
    (98, "Judges shall be independent. No other authority may interfere in their judiciary work or in the affairs of justice. The honor of the judiciary, and its integrity and justice, are the bases of rule and a guarantee of rights and freedoms."),
    (101, "Shari'a and religious matters shall be regulated by law. They shall be administered by Shari'a and religious courts in accordance with the law."),
    (102, "Administrative courts may be established by law to deal with administrative disputes and disciplinary cases. The law shall determine their other jurisdictions, the procedures to be followed before them, as well as the consequences of the rulings they pass."),
    (110, "A state of emergency in which the security of the nation is threatened due to war, invasion, armed rebellion, or natural disaster may be declared by a decree from the President of the National Authority for a period not exceeding thirty days. It is possible to extend the state of emergency for another period of thirty days after obtaining the approval of two-thirds of the Palestinian Legislative Council members."),
    (111, "The Decree declaring a state of emergency shall clearly include the reasons, the region covered, and its duration. The Palestinian Legislative Council shall have the right to review the announcement of the state of emergency or its extension, and to take the appropriate decisions."),
    (112, "It is unlawful to impose restrictions on fundamental rights and freedoms when a state of emergency is declared, except to the extent necessary to fulfill the purpose stated in the decree declaring the state of emergency."),
    (113, "It is unlawful to dissolve or to suspend the Palestinian Legislative Council during a state of emergency, nor is it permitted to suspend the provisions of this title. Any arrest based on the declaration of a state of emergency shall be subject to the following minimum requirements: any arrest must be reviewed by the Attorney General or the competent court within fifteen days, the arrested person shall have the right to appoint a lawyer of his choice."),
]


# ---------------------------------------------------------------------------
# Data containers
# ---------------------------------------------------------------------------


@dataclass
class Article:
    id: str
    article_number: int
    title: str
    text: str


# ---------------------------------------------------------------------------
# Fetch / load
# ---------------------------------------------------------------------------


def fetch_constitution(url: str | None = None, timeout: int = 15) -> str | None:
    """Best-effort fetch of the Basic Law text. Returns None on failure."""
    if url is None:
        url = "https://www.constituteproject.org/constitution/Palestine_2005?lang=en"
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        return None

    try:
        response = requests.get(url, timeout=timeout, headers={"User-Agent": "legal-aid-pipeline/1.0"})
        response.raise_for_status()
    except Exception:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    text = "\n".join(p.get_text(" ", strip=True) for p in soup.find_all(["p", "h2", "h3"]))
    return text or None


def load_raw_text() -> str | None:
    if RAW_FILE.exists():
        return RAW_FILE.read_text(encoding="utf-8")
    return None


# ---------------------------------------------------------------------------
# Parse
# ---------------------------------------------------------------------------


ARTICLE_RE = re.compile(r"Article\s+\(?(\d+)\)?\s*[:.\-]?\s*(.*?)(?=Article\s+\(?\d+\)?\s*[:.\-]?|$)", re.DOTALL | re.IGNORECASE)


def parse_articles_from_text(text: str) -> list[Article]:
    out: list[Article] = []
    for match in ARTICLE_RE.finditer(text):
        num = int(match.group(1))
        body = re.sub(r"\s+", " ", match.group(2)).strip()
        if not body:
            continue
        out.append(Article(
            id=f"palestine_basic_law_Article_{num}",
            article_number=num,
            title=_title_for(num),
            text=body,
        ))
    return out


def _title_for(article_number: int) -> str:
    current = TITLES[1]
    for threshold, title in sorted(TITLES.items()):
        if article_number >= threshold:
            current = title
    return current


def parse_articles() -> list[Article]:
    text = load_raw_text()
    if text:
        parsed = parse_articles_from_text(text)
        if parsed:
            return parsed
    return [
        Article(
            id=f"palestine_basic_law_Article_{num}",
            article_number=num,
            title=_title_for(num),
            text=body,
        )
        for num, body in BASIC_LAW_ARTICLES
    ]


# ---------------------------------------------------------------------------
# Q&A generation
# ---------------------------------------------------------------------------


QUESTION_TEMPLATES: dict[int, list[str]] = {
    9: [
        "Under Palestinian law, am I protected from discrimination?",
        "What does the Palestinian Basic Law say about equality before the law?",
    ],
    11: [
        "Under Palestinian law, what are my rights regarding personal freedom and unlawful arrest?",
        "Can the police arrest me without a judicial order in Palestine?",
    ],
    12: [
        "What are my rights if I am detained in Palestine?",
        "Do I have the right to a lawyer immediately after arrest under the Palestinian Basic Law?",
    ],
    13: [
        "Is torture or forced confession legal under the Palestinian Basic Law?",
    ],
    14: [
        "What does Article 14 of the Palestinian Basic Law say about presumption of innocence and right to a lawyer?",
    ],
    15: [
        "Is collective punishment allowed under Palestinian law?",
    ],
    17: [
        "Can the police search my home without a warrant in Palestine?",
    ],
    21: [
        "Can the government take my property? What compensation am I entitled to?",
    ],
    23: [
        "Do I have a right to housing under Palestinian law?",
    ],
    24: [
        "Is education free in Palestine?",
    ],
    25: [
        "What are my labor rights under the Palestinian Basic Law?",
        "Do I have the right to strike or join a union in Palestine?",
    ],
    28: [
        "Can a Palestinian citizen be deported or stripped of citizenship?",
    ],
    30: [
        "Do I have a right to go to court in Palestine?",
    ],
    110: [
        "How is a state of emergency declared in Palestine?",
    ],
    113: [
        "What rights do I have if I am arrested during a state of emergency?",
    ],
}


def _default_questions(article: Article) -> list[str]:
    return [
        f"What does Article {article.article_number} of the Palestinian Basic Law say?",
        f"Under the Palestinian Basic Law, what rights does Article {article.article_number} grant?",
    ]


def _format_response(article: Article) -> str:
    return (
        f"Under Article {article.article_number} of the Palestinian Basic Law "
        f"(2003, amended 2005): {article.text} {DISCLAIMER}"
    )


def generate_qa_pairs(articles: Iterable[Article]) -> list[dict]:
    pairs: list[dict] = []
    for art in articles:
        questions = QUESTION_TEMPLATES.get(art.article_number) or _default_questions(art)
        response = _format_response(art)
        for q in questions:
            pairs.append({
                "instruction": q,
                "response": response,
                "source": "Palestine Basic Law 2003 (rev. 2005)",
                "article": f"Article {art.article_number}",
            })
    return pairs


# ---------------------------------------------------------------------------
# RAG chunks
# ---------------------------------------------------------------------------


def _chunk(text: str, max_chars: int = 900, overlap: int = 120) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks


def generate_rag_chunks(articles: Iterable[Article]) -> list[dict]:
    out: list[dict] = []
    for art in articles:
        header = f"Article {art.article_number} ({art.title}): "
        for i, piece in enumerate(_chunk(art.text)):
            chunk_id = art.id if i == 0 else f"{art.id}__part_{i}"
            out.append({
                "id": chunk_id,
                "text": header + piece,
                "metadata": {
                    "source": "Palestine Basic Law 2003",
                    "article": f"Article {art.article_number}",
                    "title": art.title,
                    "keywords": ARTICLE_TOPICS.get(art.article_number, []),
                },
            })
    return out


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------


def write_jsonl(path: Path, rows: Iterable[dict]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False))
            f.write("\n")
            count += 1
    return count


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def run(try_fetch: bool = False) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    if try_fetch and not RAW_FILE.exists():
        fetched = fetch_constitution()
        if fetched:
            RAW_FILE.write_text(fetched, encoding="utf-8")
            print(f"[fetch] wrote {RAW_FILE}")
        else:
            print("[fetch] skipped — using embedded articles")

    articles = parse_articles()
    print(f"[parse] {len(articles)} articles")

    n1 = write_jsonl(
        PROCESSED_DIR / "articles.jsonl",
        ({"id": a.id, "title": a.title, "text": a.text, "article": f"Article {a.article_number}"} for a in articles),
    )
    qa = generate_qa_pairs(articles)
    n2 = write_jsonl(PROCESSED_DIR / "training_qa.jsonl", qa)
    chunks = generate_rag_chunks(articles)
    n3 = write_jsonl(PROCESSED_DIR / "rag_chunks.jsonl", chunks)

    print(f"[write] articles.jsonl   ({n1})")
    print(f"[write] training_qa.jsonl ({n2})")
    print(f"[write] rag_chunks.jsonl  ({n3})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Palestinian Basic Law dataset.")
    parser.add_argument("--fetch", action="store_true", help="Attempt to download the raw text before parsing.")
    args = parser.parse_args()
    run(try_fetch=args.fetch)


if __name__ == "__main__":
    main()
