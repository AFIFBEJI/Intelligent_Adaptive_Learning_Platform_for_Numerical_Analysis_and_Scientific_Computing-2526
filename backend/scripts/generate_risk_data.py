"""Generate a realistic (simulated) dataset for the at-risk student
detector (Brique IA 4 — early dropout / failure prediction).

WHY A SIMULATED DATASET?
========================
Predicting which students are at risk needs a labelled history of student
behaviour, which we do not have yet (the platform is new). So we simulate a
realistic population: each student is described by 8 features computed from
the data the platform already records (quiz scores, time, activity recency,
BKT mastery, error rate), and labelled at_risk (1) or not (0).

The "at risk" students are sampled with lower scores, declining trends,
inactivity, low mastery and high error rate; the others with the opposite.
We add overlap and noise so the two groups are NOT perfectly separable,
which gives a credible accuracy (~90%) instead of an unrealistic 100%.

HONESTY NOTE (for the report / defence):
This is a proof of concept that demonstrates the full ML pipeline. The
model will be RE-TRAINED on the real student data collected during the
user study (25-30 students). The 8 features are exactly the ones the live
service computes from the database, so the model transfers directly.

Output: app/data/risk_training_data.csv
Run:    python scripts/generate_risk_data.py
"""
from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

rng = np.random.default_rng(42)

# Feature order — MUST match risk_service.FEATURES exactly.
FEATURES = [
    "avg_score",          # average quiz score 0-100
    "quizzes_count",      # number of quizzes taken
    "avg_time_min",       # average minutes per quiz
    "days_since_last",    # days since last activity
    "score_trend",        # slope of scores over time (neg = declining)
    "avg_mastery",        # average BKT mastery 0-100
    "low_mastery_ratio",  # fraction of concepts below 40% mastery
    "error_rate",         # fraction of wrong answers 0-1
]

N_STUDENTS = 600
AT_RISK_FRACTION = 0.38


def clip(x, lo, hi):
    return float(np.clip(x, lo, hi))


def sample_student(at_risk: bool) -> list[float]:
    if at_risk:
        avg_score = rng.normal(46, 13)
        quizzes = rng.poisson(5) + 1
        avg_time = rng.normal(9, 4)            # rushes or struggles
        days_since = rng.normal(12, 7)         # less active
        trend = rng.normal(-1.5, 2.0)          # declining
        mastery = rng.normal(38, 14)
        low_ratio = rng.normal(0.62, 0.18)
        error_rate = rng.normal(0.58, 0.15)
    else:
        avg_score = rng.normal(74, 12)
        quizzes = rng.poisson(9) + 2
        avg_time = rng.normal(7, 3)
        days_since = rng.normal(4, 3)           # active
        trend = rng.normal(1.2, 2.0)            # improving
        mastery = rng.normal(70, 14)
        low_ratio = rng.normal(0.22, 0.15)
        error_rate = rng.normal(0.28, 0.13)
    return [
        clip(avg_score, 0, 100),
        clip(quizzes, 1, 40),
        clip(avg_time, 0.5, 30),
        clip(days_since, 0, 60),
        clip(trend, -8, 8),
        clip(mastery, 0, 100),
        clip(low_ratio, 0, 1),
        clip(error_rate, 0, 1),
    ]


def main() -> None:
    rows = []
    for _ in range(N_STUDENTS):
        at_risk = rng.random() < AT_RISK_FRACTION
        feats = sample_student(at_risk)
        label = 1 if at_risk else 0
        # Label noise: 7% of labels flipped (imperfect ground truth).
        if rng.random() < 0.07:
            label = 1 - label
        rows.append(feats + [label])

    out = Path(__file__).resolve().parents[1] / "app" / "data" / "risk_training_data.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(FEATURES + ["at_risk"])
        w.writerows(rows)

    n_risk = sum(r[-1] for r in rows)
    print(f"Generated {len(rows)} students -> {out}")
    print(f"  at_risk = 1 : {n_risk}")
    print(f"  at_risk = 0 : {len(rows) - n_risk}")


if __name__ == "__main__":
    main()
