# AI Legal Aid for Palestine 🇵🇸

A voice-based AI legal assistant that helps Palestinian citizens understand their rights under the Palestinian Basic Law (2003, amended 2005), auto-fill legal forms, and find nearby legal aid clinics — available in Arabic and English.

---

## Project Overview

Most people who face legal problems — eviction, labor disputes, custody issues — have no access to a lawyer. This project puts a legal expert in their pocket, for free.

The system works like this:

1. User speaks their problem in Arabic or English
2. Whisper transcribes the speech to text
3. The intent is classified (eviction, labor, family, criminal, etc.)
4. Relevant articles from the Palestinian Basic Law are retrieved via RAG
5. A local legal LLM reasons over the retrieved law and explains the user's rights in plain language
6. The system optionally auto-fills a legal form (PDF) or refers to a nearby clinic

---

## Repository Structure

```
legal-aid-palestine/
│
├── data/
│   ├── raw/
│   │   └── palestine_basic_law_en.txt        # Full text from constituteproject.org
│   ├── processed/
│   │   ├── articles.jsonl                    # Parsed articles (id, title, text)
│   │   ├── training_qa.jsonl                 # Fine-tuning Q&A pairs
│   │   └── rag_chunks.jsonl                  # RAG vector store chunks
│   └── forms/
│       └── templates/                        # PDF form templates
│
├── pipeline/
│   └── palestine_law_pipeline.py             # Fetch → parse → generate Q&A + RAG chunks
│
├── model/
│   ├── finetune.py                           # QLoRA fine-tuning script
│   ├── inference.py                          # Local inference wrapper
│   └── rag.py                               # ChromaDB vector store + retrieval
│
├── app/
│   ├── main.py                              # FastAPI backend
│   ├── transcribe.py                        # Whisper speech-to-text
│   ├── intent.py                            # Legal intent classifier
│   ├── form_filler.py                       # PDF auto-fill
│   └── referral.py                          # Nearby clinic lookup
│
├── frontend/
│   └── index.html                           # Simple voice UI (Arabic + English)
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Speech-to-text | `faster-whisper` | Best Arabic transcription, runs offline |
| Legal reasoning | `SaulLM-7B` or `Mistral-7B` (QLoRA fine-tuned) | Open source, no API dependency |
| Vector store | `ChromaDB` | Lightweight, local, easy to set up |
| Embeddings | `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` | Arabic + English support |
| Backend | `FastAPI` | Fast, async, easy to deploy |
| PDF forms | `reportlab` + `pypdf` | Generate and fill Arabic-ready PDFs |
| Frontend | Plain HTML + JS | Works on any device, low bandwidth |

---

## Setup

### 1. Clone and install

```bash
git clone https://github.com/your-username/legal-aid-palestine
cd legal-aid-palestine
pip install -r requirements.txt
```

### 2. Build the data pipeline

```bash
# Fetch, parse, and generate training data from the Palestinian Basic Law
python pipeline/palestine_law_pipeline.py

# Output files:
# data/processed/articles.jsonl        — structured articles
# data/processed/training_qa.jsonl     — Q&A pairs for fine-tuning
# data/processed/rag_chunks.jsonl      — chunks for vector DB
```

### 3. Build the vector store

```bash
python model/rag.py --build
# Embeds all RAG chunks into ChromaDB
# Stored locally at: ./chroma_db/
```

### 4. (Optional) Fine-tune the model

Only needed if you want a fully custom model. Skip this for a quick demo — just use SaulLM-7B directly with RAG.

```bash
python model/finetune.py \
  --base_model "Equall/Saul-7B-Instruct-v1" \
  --data "data/processed/training_qa.jsonl" \
  --output_dir "./legal-model-lora" \
  --epochs 3
```

Requires a GPU with 8GB+ VRAM. Works on Google Colab T4.

### 5. Run the app

```bash
uvicorn app.main:app --reload --port 8000
# Open: http://localhost:8000
```

---

## Data Pipeline Details

### Source

The Palestinian Basic Law (2003, amended 2005) is sourced from:

- **Constitute Project** — https://constituteproject.org/constitution/Palestine_2005
- **Palestinian Basic Law archive** — https://palestinianbasiclaw.org
- **OHCHR database** — https://adsdatabase.ohchr.org

These are public domain government texts. No copyright restrictions.

### Pipeline steps

```
constituteproject.org
        │
        ▼
   fetch_constitution()
        │  Raw HTML/text
        ▼
   parse_articles()
        │  List of {id, title, text}
        ▼
   ┌────┴────┐
   ▼         ▼
generate_   generate_
qa_pairs()  rag_chunks()
   │              │
   ▼              ▼
training_      rag_
qa.jsonl      chunks.jsonl
```

### Training data format (JSONL)

```jsonl
{"instruction": "Under Palestinian law, what are my rights regarding personal freedom and unlawful arrest?", "response": "Under Article 11 of the Palestinian Basic Law: Personal freedom is a natural right, shall be guaranteed and may not be violated. It is unlawful to arrest, search, imprison, restrict the freedom, or prevent the movement of any person, except by judicial order in accordance with the provisions of the law. Note: This is general legal information. For specific legal advice, please consult a qualified Palestinian lawyer.", "source": "Palestine Basic Law 2003 (rev. 2005)", "article": "Article 11"}
{"instruction": "What does Article 14 of the Palestinian Basic Law say about presumption of innocence and right to a lawyer?", "response": "According to Article 14 of the Palestinian Basic Law (2003, amended 2005): An accused person is considered innocent until proven guilty in a court of law. Any person accused in a criminal case shall be represented by a lawyer.", "source": "Palestine Basic Law 2003 (rev. 2005)", "article": "Article 14"}
```

### RAG chunk format (JSONL)

```jsonl
{"id": "palestine_basic_law_Article_11", "text": "Article 11 (TITLE TWO — PUBLIC RIGHTS AND LIBERTIES): Personal freedom is a natural right, shall be guaranteed and may not be violated...", "metadata": {"source": "Palestine Basic Law 2003", "article": "Article 11", "title": "TITLE TWO — PUBLIC RIGHTS AND LIBERTIES", "keywords": ["arrest", "freedom", "detention", "judicial order"]}}
```

---

## Model Details

### Option A — RAG only (fastest, good for hackathon demo)

Use SaulLM-7B-Instruct directly. Feed it the relevant Basic Law articles at inference time via RAG. No training needed.

```python
# model/inference.py
from transformers import pipeline
from model.rag import retrieve

llm = pipeline("text-generation", model="Equall/Saul-7B-Instruct-v1")

def answer(user_question):
    chunks = retrieve(user_question, top_k=3)
    context = "\n\n".join(chunks)
    prompt = f"""[INST]
You are a legal aid assistant for Palestinian citizens.
Use ONLY the following legal articles to answer. Always add a note to consult a real lawyer.

Legal context:
{context}

User question: {user_question}
[/INST]"""
    return llm(prompt, max_new_tokens=400, temperature=0.2)[0]["generated_text"]
```

### Option B — Fine-tuned model (best accuracy)

QLoRA fine-tune on `data/processed/training_qa.jsonl` using the script in `model/finetune.py`. See Setup step 4.

Recommended base models:

| Model | Best for |
|---|---|
| `Equall/Saul-7B-Instruct-v1` | English legal text, strong base |
| `mistralai/Mistral-7B-Instruct-v0.2` | General multilingual, easy fine-tune |
| `inceptionai/jais-13b-chat` | Arabic-first, best for Arabic users |
| `FreedomIntelligence/AceGPT-7B` | Arabic-optimized alternative |

---

## Key Legal Articles Covered

The model is trained on all 121 articles of the Basic Law. High-priority articles for the legal aid use case:

| Article | Topic |
|---|---|
| 9 | Equality before the law — no discrimination |
| 11 | Personal freedom — unlawful arrest |
| 12 | Rights of detained persons — right to a lawyer |
| 13 | Prohibition of torture — confessions under duress are void |
| 14 | Presumption of innocence |
| 15 | No collective punishment |
| 17 | Home is inviolable — search warrants required |
| 21 | Property rights — expropriation only with fair compensation |
| 23 | Right to housing |
| 24 | Right to free education |
| 25 | Right to work — labor protections |
| 30 | Right to access courts |
| 110–113 | State of emergency rights |

---

## Demo Script (Hackathon)

The most powerful demo scenario:

> "My landlord verbally told me I have 3 days to leave. What are my rights?"

Expected flow:
1. Whisper transcribes the Arabic voice input
2. Intent: `eviction`
3. RAG retrieves Articles 11, 17, 21, 30
4. Model responds: explains that a verbal notice has no legal standing, the landlord must provide written notice, and the user has the right to contest in court
5. System generates a PDF demand letter to the landlord
6. Shows the nearest free legal clinic in Nablus/Ramallah

---

## System Prompt

```
You are a legal aid assistant helping Palestinian citizens understand their rights
under the Palestinian Basic Law (2003, amended 2005).

Rules:
- Answer ONLY based on the provided legal context
- Use plain, simple language (Grade 8 reading level)
- Always end with: "This is general legal information. For your specific situation, consult a licensed Palestinian lawyer or visit a legal aid center."
- Never give advice that could harm the user
- If the answer is not in the provided articles, say so clearly
- Support both Arabic and English responses
```

---

## Roadmap

- [x] Data pipeline (fetch + parse + generate training data)
- [x] RAG vector store with Palestinian Basic Law
- [x] Fine-tuning script (QLoRA)
- [x] FastAPI backend
- [ ] Arabic voice input (Whisper integration)
- [ ] PDF form auto-fill (eviction notice response, labor complaint)
- [ ] Referral database (legal aid clinics in West Bank + Gaza)
- [ ] Mobile-friendly frontend
- [ ] Expand to: Labour Law, Family Law, Criminal Procedure Law
- [ ] Jordanian Civil Law coverage (still applicable in West Bank)

---

## Adding More Laws

The pipeline is designed to be extended. To add a new law:

1. Add the raw text to `data/raw/`
2. Update `parse_articles()` in the pipeline to handle its format
3. Add topic mappings to `ARTICLE_TOPICS`
4. Re-run the pipeline
5. Rebuild the vector store

Recommended next laws to add:
- Palestinian Labour Law No. 7 of 2000
- Palestinian Civil Procedure Law
- Palestinian Penal Code
- Jordanian Civil Law (applicable in West Bank)
- Personal Status Law

---

## Requirements

```
transformers>=4.40.0
peft>=0.10.0
trl>=0.8.0
bitsandbytes>=0.43.0
accelerate>=0.29.0
sentence-transformers>=2.7.0
chromadb>=0.5.0
faster-whisper>=1.0.0
fastapi>=0.111.0
uvicorn>=0.29.0
reportlab>=4.1.0
pypdf>=4.2.0
datasets>=2.19.0
torch>=2.2.0
requests>=2.31.0
python-multipart>=0.0.9
```

---

## Important Note

This system provides **general legal information only**, not legal advice. It is not a substitute for a qualified Palestinian lawyer. Always direct users to professional legal help for serious matters.

---

## License

MIT License — free to use, modify, and distribute.

---

## Resources

- Palestinian Basic Law (English): https://constituteproject.org/constitution/Palestine_2005
- Palestinian Basic Law Archive: https://palestinianbasiclaw.org
- SaulLM-7B Model: https://huggingface.co/Equall/Saul-7B-Instruct-v1
- Jais Arabic Model: https://huggingface.co/inceptionai/jais-13b-chat
- LawBench Benchmark: https://github.com/open-compass/LawBench
