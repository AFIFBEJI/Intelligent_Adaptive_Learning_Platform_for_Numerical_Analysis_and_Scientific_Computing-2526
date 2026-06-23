"""Error-type classification service (Brique IA 3).

WHAT IT DOES
============
Given a short text describing a student's mistake, it predicts the error
TYPE from the 11-class taxonomy of app/data/error_taxonomy.py, with a
confidence score. This replaces the old approach where the error type had
to be hand-tagged on every distractor (the "static, rule-based" method the
PFE specification criticises).

It loads a model trained by scripts/train_error_classifier.py:
  - PRIMARY features: semantic embeddings (reuses Brique IA 2)
  - FALLBACK features: TF-IDF
The model bundle records which method it used, so this service vectorises
new text the same way.

GRACEFUL DEGRADATION
If scikit-learn / joblib are missing, or the model file is absent, or the
confidence is too low, classify() returns code "unknown" and the caller
falls back to the existing behaviour. The platform never breaks.
"""
from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import joblib
    import numpy as np
    SKLEARN_AVAILABLE = True
except Exception as exc:  # noqa: BLE001
    SKLEARN_AVAILABLE = False
    logger.info("Error classifier disabled (scikit-learn/joblib missing): %s", exc)

_MODEL_FILE = Path(__file__).resolve().parents[1] / "data" / "error_classifier.joblib"

_bundle = None
_loaded = False


def _load():
    """Lazy-load the model bundle once."""
    global _bundle, _loaded
    if _loaded:
        return _bundle
    _loaded = True
    if not SKLEARN_AVAILABLE or not _MODEL_FILE.exists():
        if not _MODEL_FILE.exists():
            logger.info("Error classifier model not found at %s", _MODEL_FILE)
        return None
    try:
        _bundle = joblib.load(_MODEL_FILE)
        logger.info("Error classifier loaded (method=%s, %d classes)",
                    _bundle.get("method"), len(_bundle.get("classes", [])))
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to load error classifier: %s", exc)
        _bundle = None
    return _bundle


def is_available() -> bool:
    return _load() is not None


def classify(text: str, lang: str = "en") -> dict:
    """Predict the error type of a mistake description.

    Returns {"code": str, "confidence": float}. On any problem or when the
    model is not confident enough, returns {"code": "unknown", ...}.
    """
    bundle = _load()
    if not bundle or not text or not text.strip():
        return {"code": "unknown", "confidence": 0.0}

    # Vectorise the text the same way the model was trained.
    if bundle["method"] == "embeddings":
        from app.services import embedding_service
        if not embedding_service.is_available():
            return {"code": "unknown", "confidence": 0.0}
        vec = embedding_service.encode(text)
        if vec is None:
            return {"code": "unknown", "confidence": 0.0}
        X = np.asarray(vec).reshape(1, -1)
    else:  # tfidf
        X = bundle["vectorizer"].transform([text])

    clf = bundle["clf"]
    proba = clf.predict_proba(X)[0]
    idx = int(np.argmax(proba))
    confidence = float(proba[idx])
    code = bundle["classes"][idx]

    # Low confidence -> stay "unknown" rather than guess wrongly.
    if confidence < float(bundle.get("threshold", 0.30)):
        return {"code": "unknown", "confidence": round(confidence, 3)}
    return {"code": code, "confidence": round(confidence, 3)}
