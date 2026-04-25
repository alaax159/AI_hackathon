"""ChromaDB-backed retrieval over the Palestinian Basic Law RAG chunks.

Usage:
    python -m model.rag --build          # embed all chunks into ChromaDB
    python -m model.rag --query "..."    # quick retrieval sanity check
"""
from __future__ import annotations

import argparse
import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
CHUNKS_FILE = ROOT / "data" / "processed" / "rag_chunks.jsonl"
DEFAULT_CHROMA_DIR = ROOT / "chroma_db"
DEFAULT_EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
COLLECTION_NAME = "palestine_basic_law"


def _chroma_dir() -> Path:
    return Path(os.environ.get("CHROMA_DIR", DEFAULT_CHROMA_DIR))


def _embed_model() -> str:
    return os.environ.get("EMBED_MODEL", DEFAULT_EMBED_MODEL)


@lru_cache(maxsize=1)
def _get_client():
    import chromadb
    return chromadb.PersistentClient(path=str(_chroma_dir()))


@lru_cache(maxsize=1)
def _get_embedding_fn():
    from chromadb.utils import embedding_functions
    return embedding_functions.SentenceTransformerEmbeddingFunction(model_name=_embed_model())


@lru_cache(maxsize=1)
def _get_collection():
    """Cached handle to the live collection — avoids re-initializing the
    embedding model on every retrieval call."""
    return _get_client().get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=_get_embedding_fn(),
        metadata={"hnsw:space": "cosine"},
    )


def _get_or_create_collection(client, embedding_fn):
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"},
    )


def _load_chunks() -> list[dict]:
    if not CHUNKS_FILE.exists():
        raise FileNotFoundError(
            f"{CHUNKS_FILE} is missing. Run `python -m pipeline.palestine_law_pipeline` first."
        )
    rows: list[dict] = []
    with CHUNKS_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _normalize_metadata(meta: dict) -> dict:
    # Chroma only accepts primitive metadata values.
    out: dict[str, str | int | float | bool] = {}
    for k, v in meta.items():
        if isinstance(v, (str, int, float, bool)) or v is None:
            out[k] = v if v is not None else ""
        elif isinstance(v, (list, tuple)):
            out[k] = ", ".join(str(x) for x in v)
        else:
            out[k] = str(v)
    return out


def build() -> int:
    """(Re)build the vector store from rag_chunks.jsonl."""
    chunks = _load_chunks()
    client = _get_client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    _get_collection.cache_clear()
    collection = _get_or_create_collection(client, _get_embedding_fn())

    ids = [c["id"] for c in chunks]
    docs = [c["text"] for c in chunks]
    metas = [_normalize_metadata(c.get("metadata", {})) for c in chunks]
    collection.add(ids=ids, documents=docs, metadatas=metas)
    return len(ids)


def retrieve(query: str, top_k: int = 3) -> list[dict]:
    """Return the top_k most relevant chunks for a natural-language query."""
    collection = _get_collection()
    # Chroma raises if n_results <= 0 or exceeds the corpus size.
    n = max(1, min(int(top_k), max(1, collection.count())))
    result = collection.query(query_texts=[query], n_results=n)
    docs: list[str] = (result.get("documents") or [[]])[0]
    metas: list[dict] = (result.get("metadatas") or [[]])[0]
    ids: list[str] = (result.get("ids") or [[]])[0]
    distances: list[float] = (result.get("distances") or [[]])[0] or [None] * len(docs)
    return [
        {"id": ids[i], "text": docs[i], "metadata": metas[i], "distance": distances[i]}
        for i in range(len(docs))
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build or query the Palestinian Basic Law vector store.")
    parser.add_argument("--build", action="store_true", help="Embed all RAG chunks into ChromaDB.")
    parser.add_argument("--query", type=str, help="Run a similarity query.")
    parser.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args()

    if args.build:
        n = build()
        print(f"[rag] embedded {n} chunks into {_chroma_dir()}")
    if args.query:
        hits = retrieve(args.query, top_k=args.top_k)
        for rank, hit in enumerate(hits, 1):
            print(f"[{rank}] {hit['metadata'].get('article', '')}  (d={hit['distance']})")
            print(hit["text"][:300])
            print()
    if not args.build and not args.query:
        parser.print_help()


if __name__ == "__main__":
    main()
