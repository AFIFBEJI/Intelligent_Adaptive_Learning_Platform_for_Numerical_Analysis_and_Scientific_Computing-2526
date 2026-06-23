"""
Bayesian Knowledge Tracing (BKT) — the adaptive ML model.

WHY THIS FILE?
=============
The PFE proposal criticises existing systems for "Static Adaptation:
predominantly rule-based systems lacking dynamic graph reasoning".

This service replaces the old rule (mastery = 0.6*old + 0.4*new) with a
real probabilistic model of learning: Bayesian Knowledge Tracing.

THE MODEL (in plain words)
=========================
BKT estimates, as a PROBABILITY, the chance that a student has MASTERED a
concept, and updates it after every answer using Bayes' rule. It accounts
for two realities that a simple average ignores:
  - SLIP  (p_S): the student knows but answers wrong by mistake.
  - GUESS (p_G): the student does not know but guesses right (likely on MCQ).

Four parameters per concept:
  - p_L0 : prior probability the student already knows the concept.
  - p_T  : probability of LEARNING the concept between two questions.
  - p_S  : slip probability.
  - p_G  : guess probability.

After observing a response (correct/incorrect), we compute the posterior
P(known | response) with Bayes, then apply the learning transition p_T.

The 4 parameters can be FITTED from real interaction logs by EM
(see scripts/fit_bkt.py); until then we use sensible defaults.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Sensible defaults (4-choice MCQ => guess ~ 0.25). Standard BKT priors.
DEFAULT_PARAMS: dict[str, float] = {
    "p_L0": 0.20,   # prior knowledge
    "p_T": 0.15,    # learning rate
    "p_S": 0.10,    # slip
    "p_G": 0.25,    # guess (4 options)
}

# Per-concept fitted parameters, produced by scripts/fit_bkt.py.
_PARAMS_FILE = Path(__file__).resolve().parents[1] / "data" / "bkt_params.json"


def _load_fitted_params() -> dict[str, dict[str, float]]:
    try:
        if _PARAMS_FILE.exists():
            data = json.loads(_PARAMS_FILE.read_text(encoding="utf-8"))
            logger.info("BKT: %d fitted concept params loaded", len(data))
            return data
    except Exception as exc:  # noqa: BLE001
        logger.warning("BKT: could not read fitted params (%s), using defaults", exc)
    return {}


_FITTED: dict[str, dict[str, float]] = _load_fitted_params()


def get_params(concept_id: str | None) -> dict[str, float]:
    """Return the BKT parameters for a concept (fitted if available, else default)."""
    if concept_id and concept_id in _FITTED:
        merged = dict(DEFAULT_PARAMS)
        merged.update(_FITTED[concept_id])
        return merged
    return dict(DEFAULT_PARAMS)


def _clamp(p: float) -> float:
    return max(1e-4, min(1.0 - 1e-4, p))


def posterior_after_obs(p_known: float, correct: bool, params: dict[str, float]) -> float:
    """One BKT step: Bayes update from a single observation, then learning.

    Returns the new P(known) in [0, 1].
    """
    s, g = params["p_S"], params["p_G"]
    p = _clamp(p_known)
    if correct:
        num = p * (1.0 - s)
        den = p * (1.0 - s) + (1.0 - p) * g
    else:
        num = p * s
        den = p * s + (1.0 - p) * (1.0 - g)
    p_post = (num / den) if den > 1e-9 else p
    # Learning transition: the student may have learnt the concept now.
    p_next = p_post + (1.0 - p_post) * params["p_T"]
    return _clamp(p_next)


def update_mastery(concept_id: str | None, prior_p: float | None, observations: list[bool]) -> float:
    """Run sequential BKT updates over a list of correct/incorrect observations.

    prior_p : current P(known) in [0,1] (None -> use p_L0).
    Returns the updated P(known) in [0, 1].
    """
    params = get_params(concept_id)
    p = params["p_L0"] if prior_p is None else _clamp(prior_p)
    for correct in observations:
        p = posterior_after_obs(p, bool(correct), params)
    return p


def predict_correct(concept_id: str | None, p_known: float) -> float:
    """P(next answer correct) given the current mastery probability.

    P(correct) = P(known)*(1 - slip) + P(not known)*guess.
    """
    params = get_params(concept_id)
    p = _clamp(p_known)
    return p * (1.0 - params["p_S"]) + (1.0 - p) * params["p_G"]
