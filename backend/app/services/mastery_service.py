"""Single source of truth for updating the mastery level.

Why this service?
=================
Before May 12, 2026, the logic for updating `ConceptMastery` was
DUPLICATED in two places:

1. `routers/quiz.py:update_mastery` (EWMA formula 0.6 * old + 0.4 * new)
2. `services/feedback_service.py:update_mastery_from_evaluations`
   (same formula + aggregation of partial_credits per concept)

Risk: if the formula changes (e.g. moving average, time decay), one must
remember to maintain both places. This is the classic source of silent
divergence and regressions that are hard to diagnose.

The senior audit of 05/12/2026 flagged this duplication as P1 debt.
This module is the solution: a single computation function, two APIs
(unitary + aggregator) that share the implementation.

Canonical formula
=================
For each concept, mastery is updated with a weighted average:

    new_mastery = round(0.6 * old + 0.4 * new_score, 1)

If the student had no ConceptMastery row for this concept, one is
created initialized with `new_score`.

Formula choice (justified in the upcoming ADR):
- 60% historical weight: prevents mastery from oscillating too much on an
  isolated failed quiz (a bad day does not sink the progression).
- 40% on the new score: still reactive to real progress.
- Rounded to 1 decimal: avoids float pollution over long
  series (`32.07000000001` -> `32.1`).
"""
from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.mastery import ConceptMastery

# ============================================================
# Constants (centralized for future tuning via ADR)
# ============================================================
OLD_WEIGHT = 0.6
NEW_WEIGHT = 0.4

# Sanity check: the two weights must sum to 1.0 (otherwise we no longer
# compute a weighted average but a drift). If you change the values,
# always keep this property.
assert OLD_WEIGHT + NEW_WEIGHT == 1.0, "OLD_WEIGHT + NEW_WEIGHT doit egaler 1.0"


# ============================================================
# API 1 — Unitary application (one concept, one score)
# ============================================================
def apply_mastery_delta(
    db: Session,
    etudiant_id: int,
    concept_id: str,
    new_score: float,
) -> ConceptMastery:
    """Update (or create) a student's ConceptMastery row.

    new_score: 0-100 (the score perceived by the student on this concept).

    This function DOES NOT COMMIT. The caller is responsible for the commit
    (often at the end of a quiz/evaluation transaction to group several
    updates).

    Returns the ConceptMastery object (created or modified). Useful for
    tests that want to assert on the resulting state.
    """
    mastery = (
        db.query(ConceptMastery)
        .filter(
            ConceptMastery.etudiant_id == etudiant_id,
            ConceptMastery.concept_neo4j_id == concept_id,
        )
        .first()
    )
    now = datetime.now(UTC)
    if mastery is None:
        mastery = ConceptMastery(
            etudiant_id=etudiant_id,
            concept_neo4j_id=concept_id,
            niveau_maitrise=round(new_score, 1),
            derniere_mise_a_jour=now,
        )
        db.add(mastery)
    else:
        mastery.niveau_maitrise = round(
            mastery.niveau_maitrise * OLD_WEIGHT + new_score * NEW_WEIGHT,
            1,
        )
        mastery.derniere_mise_a_jour = now
    return mastery


# ============================================================
# API 2 — Aggregator from a list of quiz evaluations
# ============================================================
def update_mastery_from_evaluations(
    db: Session,
    etudiant_id: int,
    evaluations,  # list[QuestionEvaluation] - avoid the circular import
) -> dict[str, float]:
    """Update the mastery from a list of question evaluations using
    Bayesian Knowledge Tracing (BKT).

    Each evaluation has a `concept_id` and an `is_correct` flag. For every
    concept we replay the correct/incorrect observations through the BKT
    model (services/bkt_service.py), starting from the student's CURRENT
    mastery as the prior. The stored mastery becomes P(known) * 100.

    This replaces the former rule-based average (0.6*old + 0.4*new): BKT
    models slip and guess, so a lucky guess or a careless slip no longer
    moves the mastery as if it were certain knowledge.

    Returns {concept_id: new_mastery_percent} for the concepts touched.
    """
    from app.services import bkt_service

    # Group the correct/incorrect observations per concept (in answer order).
    by_concept: dict[str, list[bool]] = {}
    for e in evaluations:
        if not getattr(e, "concept_id", None):
            continue
        by_concept.setdefault(e.concept_id, []).append(
            bool(getattr(e, "is_correct", False))
        )

    now = datetime.now(UTC)
    updated: dict[str, float] = {}
    for concept_id, observations in by_concept.items():
        row = (
            db.query(ConceptMastery)
            .filter(
                ConceptMastery.etudiant_id == etudiant_id,
                ConceptMastery.concept_neo4j_id == concept_id,
            )
            .first()
        )
        prior_p = (row.niveau_maitrise / 100.0) if row else None
        p_known = bkt_service.update_mastery(concept_id, prior_p, observations)
        new_pct = round(p_known * 100.0, 1)

        if row is None:
            row = ConceptMastery(
                etudiant_id=etudiant_id,
                concept_neo4j_id=concept_id,
                niveau_maitrise=new_pct,
                derniere_mise_a_jour=now,
            )
            db.add(row)
        else:
            row.niveau_maitrise = new_pct
            row.derniere_mise_a_jour = now
        updated[concept_id] = new_pct
    return updated
