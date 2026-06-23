"""
Semantic embeddings service for the GraphRAG retrieval.

WHY THIS FILE?
=============
The old retrieval matched the student's question to a concept by counting
shared KEYWORDS. It misses paraphrases: "how do I find where a curve crosses
zero?" shares no keyword with "Bisection method", yet they mean the same
thing.

This service upgrades the retrieval to SEMANTIC search: it turns each text
into a vector (an "embedding") with a multilingual sentence-transformer,
and compares meanings by cosine similarity. Questions and concepts that
mean the same thing get a high score even with different words.

It degrades gracefully: if `sentence-transformers` is not installed, the
flag EMBEDDINGS_AVAILABLE is False and the RAG service falls back to the
keyword matching. So the platform never breaks because of this.

Install (on the backend machine):
    pip install sentence-transformers
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except Exception as exc:  # noqa: BLE001
    EMBEDDINGS_AVAILABLE = False
    logger.info("Embeddings disabled (sentence-transformers not installed): %s", exc)

# Small, fast, MULTILINGUAL model (handles FR + EN). ~120 MB, CPU-friendly.
_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

_model = None
_cache: dict[str, "object"] = {}  # text -> normalized vector


def is_available() -> bool:
    return EMBEDDINGS_AVAILABLE


def _get_model():
    """Lazy-load the model on first use (avoids slowing startup)."""
    global _model
    if not EMBEDDINGS_AVAILABLE:
        return None
    if _model is None:
        logger.info("Loading embedding model: %s ...", _MODEL_NAME)
        _model = SentenceTransformer(_MODEL_NAME)
        logger.info("Embedding model loaded.")
    return _model


def encode(text: str):
    """Return the normalized embedding vector of a text (cached), or None."""
    model = _get_model()
    if model is None or not text:
        return None
    if text in _cache:
        return _cache[text]
    vec = model.encode(text, normalize_embeddings=True)
    _cache[text] = vec
    return vec


def cosine(a, b) -> float:
    """Cosine similarity of two NORMALIZED vectors (= dot product)."""
    return float(np.dot(a, b))


def best_match(query: str, candidates: list[tuple[str, str]]) -> tuple[str, float] | None:
    """Pick the candidate whose MEANING is closest to the query.

    candidates : list of (id, text). Returns (best_id, similarity) or None
    if embeddings are unavailable / nothing to compare.
    """
    model = _get_model()
    if model is None or not candidates:
        return None
    q_vec = encode(query)
    if q_vec is None:
        return None
    best_id, best_sim = None, -1.0
    for cid, text in candidates:
        v = encode(text)
        if v is None:
            continue
        sim = cosine(q_vec, v)
        if sim > best_sim:
            best_sim, best_id = sim, cid
    if best_id is None:
        return None
    return best_id, best_sim
