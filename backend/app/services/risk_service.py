"""At-risk student detection service (Brique IA 4).

WHAT IT DOES
============
Computes 8 behavioural features for a student from the database (quiz
scores, activity, BKT mastery, error rate), feeds them to a trained
classifier, and returns whether the student is at risk of failing /
dropping out, with a probability and the TOP FACTORS that explain it.

The 8 features are exactly the ones scripts/generate_risk_data.py uses,
so the model trained on simulated data transfers directly to real data.

GRACEFUL DEGRADATION
If scikit-learn/joblib or the model file are missing, assess() returns
None and the caller simply does not show a risk flag. Nothing breaks.
"""
from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.mastery import ConceptMastery
from app.models.quiz import QuizResult

logger = logging.getLogger(__name__)

try:
    import joblib
    import numpy as np
    SKLEARN_AVAILABLE = True
except Exception as exc:  # noqa: BLE001
    SKLEARN_AVAILABLE = False
    logger.info("Risk model disabled (scikit-learn/joblib missing): %s", exc)

_MODEL_FILE = Path(__file__).resolve().parents[1] / "data" / "risk_model.joblib"
LOW_MASTERY_THRESHOLD = 40.0

_bundle = None
_loaded = False


def _load():
    global _bundle, _loaded
    if _loaded:
        return _bundle
    _loaded = True
    if not SKLEARN_AVAILABLE or not _MODEL_FILE.exists():
        if not _MODEL_FILE.exists():
            logger.info("Risk model not found at %s", _MODEL_FILE)
        return None
    try:
        _bundle = joblib.load(_MODEL_FILE)
        logger.info("Risk model loaded (%d features)", len(_bundle.get("features", [])))
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to load risk model: %s", exc)
        _bundle = None
    return _bundle


def is_available() -> bool:
    return _load() is not None


# ------------------------------------------------------------------
# Feature extraction from the real database
# ------------------------------------------------------------------
def extract_features(db: Session, etudiant_id: int) -> dict | None:
    """Compute the 8 behavioural features for a student, or None if the
    student has no quiz history yet (cannot assess)."""
    results = (
        db.query(QuizResult)
        .filter(QuizResult.etudiant_id == etudiant_id)
        .order_by(QuizResult.date_tentative.asc())
        .all()
    )
    if not results:
        return None

    scores = [float(r.score) for r in results]
    avg_score = sum(scores) / len(scores)
    quizzes_count = len(results)
    avg_time_min = sum(int(r.temps_reponse or 0) for r in results) / len(results) / 60.0

    now = datetime.now(UTC)
    last = max(r.date_tentative for r in results)
    if last.tzinfo is None:
        last = last.replace(tzinfo=UTC)
    days_since_last = max(0.0, (now - last).total_seconds() / 86400.0)

    # Score trend = slope of scores over attempt order.
    if len(scores) >= 2 and SKLEARN_AVAILABLE:
        xs = np.arange(len(scores))
        score_trend = float(np.polyfit(xs, scores, 1)[0])
    else:
        score_trend = 0.0

    masteries = (
        db.query(ConceptMastery)
        .filter(ConceptMastery.etudiant_id == etudiant_id)
        .all()
    )
    mvals = [float(m.niveau_maitrise) for m in masteries]
    if mvals:
        avg_mastery = sum(mvals) / len(mvals)
        low_mastery_ratio = sum(1 for v in mvals if v < LOW_MASTERY_THRESHOLD) / len(mvals)
    else:
        avg_mastery = avg_score
        low_mastery_ratio = 1.0 if avg_score < LOW_MASTERY_THRESHOLD else 0.0

    # Error rate from the detailed evaluations.
    total = wrong = 0
    for r in results:
        for ev in (r.evaluation_detaillee or []):
            if isinstance(ev, dict):
                total += 1
                if not ev.get("is_correct", False):
                    wrong += 1
    error_rate = (wrong / total) if total else (1.0 - avg_score / 100.0)

    return {
        "avg_score": round(avg_score, 2),
        "quizzes_count": quizzes_count,
        "avg_time_min": round(avg_time_min, 2),
        "days_since_last": round(days_since_last, 2),
        "score_trend": round(score_trend, 3),
        "avg_mastery": round(avg_mastery, 2),
        "low_mastery_ratio": round(low_mastery_ratio, 3),
        "error_rate": round(error_rate, 3),
    }


# ------------------------------------------------------------------
# Prediction
# ------------------------------------------------------------------
def predict_from_features(features: dict) -> dict | None:
    """Run the classifier on a feature dict. Returns the risk verdict, the
    probability, and the top factors pushing this student towards risk."""
    bundle = _load()
    if not bundle:
        return None
    order = bundle["features"]
    try:
        x = np.array([[float(features[f]) for f in order]])
    except (KeyError, TypeError, ValueError):
        return None
    xs = bundle["scaler"].transform(x)
    proba = float(bundle["clf"].predict_proba(xs)[0][1])
    at_risk = proba >= float(bundle.get("threshold", 0.5))

    # Per-student explanation: contribution = coefficient * standardised value.
    # Positive contributions push towards risk; we surface the top ones.
    contrib = bundle["clf"].coef_[0] * xs[0]
    ranked = sorted(zip(order, contrib), key=lambda kv: -kv[1])
    top_factors = [name for name, c in ranked if c > 0][:3]

    return {
        "at_risk": bool(at_risk),
        "probability": round(proba, 3),
        "top_factors": top_factors,
    }


def assess(db: Session, etudiant_id: int) -> dict | None:
    """Full assessment for one student: features + risk verdict, or None
    if the model is unavailable or the student has no history."""
    if not is_available():
        return None
    features = extract_features(db, etudiant_id)
    if features is None:
        return None
    verdict = predict_from_features(features)
    if verdict is None:
        return None
    return {**verdict, "features": features}
