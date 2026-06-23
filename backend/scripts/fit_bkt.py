"""
Fit the Bayesian Knowledge Tracing parameters from real interaction logs.

This is the TRAINING step of the adaptive model. It reads every quiz
submission (QuizResult.evaluation_detaillee), rebuilds the per-student,
per-concept sequences of correct/incorrect answers, and fits the 4 BKT
parameters (p_L0, p_T, p_S, p_G) per concept by MAXIMUM LIKELIHOOD
(coarse grid search over the BKT forward likelihood).

The fitted parameters are written to app/data/bkt_params.json, which
bkt_service.py loads automatically at startup.

Run it (from the backend folder, in your venv):

    python scripts/fit_bkt.py

If a concept does not have enough sequences, it keeps the default
parameters (the script reports how many were fitted).
"""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Minimum number of answer-sequences required to fit a concept.
MIN_SEQUENCES = 8

# Coarse grids (kept small so the fit runs fast).
GRID_L0 = [0.1, 0.2, 0.3, 0.4, 0.5]
GRID_T = [0.05, 0.1, 0.15, 0.2, 0.3]
GRID_S = [0.05, 0.1, 0.15, 0.2]      # slip < 0.5
GRID_G = [0.1, 0.2, 0.25, 0.3]       # guess < 0.5


def sequence_loglik(seq: list[bool], l0: float, t: float, s: float, g: float) -> float:
    """Log-likelihood of one observation sequence under BKT (forward pass)."""
    p = l0
    ll = 0.0
    for correct in seq:
        p_correct = p * (1 - s) + (1 - p) * g
        p_correct = min(max(p_correct, 1e-6), 1 - 1e-6)
        ll += math.log(p_correct if correct else (1 - p_correct))
        if correct:
            p_post = p * (1 - s) / p_correct
        else:
            p_post = p * s / (1 - p_correct)
        p = p_post + (1 - p_post) * t
    return ll


def fit_concept(sequences: list[list[bool]]) -> dict[str, float]:
    """Grid-search MLE of the 4 BKT parameters for one concept."""
    best, best_ll = None, -math.inf
    for l0 in GRID_L0:
        for t in GRID_T:
            for s in GRID_S:
                for g in GRID_G:
                    ll = sum(sequence_loglik(seq, l0, t, s, g) for seq in sequences)
                    if ll > best_ll:
                        best_ll, best = ll, {"p_L0": l0, "p_T": t, "p_S": s, "p_G": g}
    return best or {}


def load_sequences_from_db() -> dict[str, list[list[bool]]]:
    """Rebuild per-(student, concept) answer sequences from QuizResult logs."""
    from app.core.database import SessionLocal
    from app.models.quiz import QuizResult

    db = SessionLocal()
    try:
        results = (
            db.query(QuizResult)
            .order_by(QuizResult.etudiant_id, QuizResult.date_tentative)
            .all()
        )
    finally:
        db.close()

    # (student, concept) -> ordered list of bool
    grouped: dict[tuple, list[bool]] = defaultdict(list)
    for r in results:
        details = r.evaluation_detaillee or []
        if isinstance(details, str):
            try:
                details = json.loads(details)
            except Exception:  # noqa: BLE001
                details = []
        for d in details:
            cid = d.get("concept_id")
            if not cid:
                continue
            grouped[(r.etudiant_id, cid)].append(bool(d.get("is_correct", False)))

    by_concept: dict[str, list[list[bool]]] = defaultdict(list)
    for (_student, cid), seq in grouped.items():
        if seq:
            by_concept[cid].append(seq)
    return by_concept


def main() -> None:
    print("=" * 60)
    print(" BKT TRAINING — fitting parameters from quiz logs")
    print("=" * 60)
    by_concept = load_sequences_from_db()
    if not by_concept:
        print("No quiz interaction logs found yet. Take some quizzes first,")
        print("then re-run. The model keeps its default parameters meanwhile.")
        return

    fitted: dict[str, dict[str, float]] = {}
    for cid, sequences in sorted(by_concept.items()):
        if len(sequences) < MIN_SEQUENCES:
            print(f"  {cid:34} {len(sequences):3} seq  -> skipped (need >= {MIN_SEQUENCES})")
            continue
        params = fit_concept(sequences)
        fitted[cid] = params
        print(f"  {cid:34} {len(sequences):3} seq  -> {params}")

    out = Path(__file__).resolve().parents[1] / "app" / "data" / "bkt_params.json"
    out.write_text(json.dumps(fitted, indent=2), encoding="utf-8")
    print("-" * 60)
    print(f"Fitted {len(fitted)} concept(s). Saved to {out}")
    print("Restart the backend to load the new parameters.")


if __name__ == "__main__":
    main()
