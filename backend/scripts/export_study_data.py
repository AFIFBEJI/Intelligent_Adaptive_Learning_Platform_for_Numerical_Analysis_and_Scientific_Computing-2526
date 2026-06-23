"""Pseudonymized export of the user study data for statistical analysis.

Usage:
    cd backend
    python -m scripts.export_study_data --out ../analysis/study_data.csv

The produced CSV contains ONLY the `participant_code` (no email,
no name). The columns are aligned with the statistical analysis plan
defined in docs/phase4/01_PROTOCOLE_USER_STUDY.md.

Columns produced:
    participant_code, group_assigned, test_version, pre_score, post_score,
    learning_gain, normalized_gain, sus_score, sus_normalized,
    enrolled_at, pre_test_done_at, post_test_done_at, withdrawn,
    n_sessions, n_quiz_attempts, n_tutor_questions, avg_quiz_score
"""
from __future__ import annotations

import argparse
import csv
import logging
import sys
from pathlib import Path

# Add the `backend/` directory to PYTHONPATH if the script is run
# directly (not via `python -m`).
_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from app.core.database import SessionLocal  # noqa: E402
from app.models.quiz import QuizResult  # noqa: E402
from app.models.study import StudyEvent, StudyParticipant  # noqa: E402
from app.models.tutor import TutorMessage, TutorSession  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def _safe_iso(dt) -> str:
    return dt.isoformat() if dt else ""


def export_to_csv(out_path: Path) -> dict:
    """Write the CSV to out_path. Return a dict of summary stats."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    db = SessionLocal()
    try:
        participants = (
            db.query(StudyParticipant)
            .order_by(StudyParticipant.id)
            .all()
        )
        if not participants:
            logger.warning("Aucun participant en DB. CSV vide.")
            with open(out_path, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(["participant_code"])
            return {"n": 0}

        rows = []
        for p in participants:
            # Aggregations on the student side
            quiz_rows = (
                db.query(QuizResult)
                .filter(QuizResult.etudiant_id == p.etudiant_id)
                .all()
            )
            n_quiz_attempts = len(quiz_rows)
            avg_quiz_score = (
                round(sum(r.score for r in quiz_rows) / n_quiz_attempts, 2)
                if n_quiz_attempts else 0.0
            )
            n_tutor_questions = (
                db.query(TutorMessage)
                .join(TutorSession, TutorSession.id == TutorMessage.session_id)
                .filter(TutorSession.etudiant_id == p.etudiant_id)
                .filter(TutorMessage.role == "student")
                .count()
            )
            n_sessions = (
                db.query(StudyEvent)
                .filter(StudyEvent.participant_id == p.id)
                .filter(StudyEvent.event_type == "session_start")
                .count()
            )
            # Derived calculations
            learning_gain = None
            norm_gain = None
            if p.pre_score is not None and p.post_score is not None:
                learning_gain = round(p.post_score - p.pre_score, 2)
                if p.pre_score < 100:
                    norm_gain = round(
                        (p.post_score - p.pre_score) / (100 - p.pre_score), 4
                    )
            sus_normalized = None
            if p.sus_score is not None:
                sus_normalized = round((p.sus_score - 6) / 24 * 100, 2)

            rows.append({
                "participant_code": p.participant_code,
                "group_assigned": p.group_assigned or "",
                "test_version": p.test_version,
                "pre_score": p.pre_score if p.pre_score is not None else "",
                "post_score": p.post_score if p.post_score is not None else "",
                "learning_gain": learning_gain if learning_gain is not None else "",
                "normalized_gain": norm_gain if norm_gain is not None else "",
                "sus_score": p.sus_score if p.sus_score is not None else "",
                "sus_normalized": sus_normalized if sus_normalized is not None else "",
                "enrolled_at": _safe_iso(p.enrolled_at),
                "pre_test_done_at": _safe_iso(p.pre_test_done_at),
                "post_test_done_at": _safe_iso(p.post_test_done_at),
                "withdrawn": "1" if p.withdrawn_at else "0",
                "n_sessions": n_sessions,
                "n_quiz_attempts": n_quiz_attempts,
                "n_tutor_questions": n_tutor_questions,
                "avg_quiz_score": avg_quiz_score,
            })

        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        logger.info("Export ecrit dans %s (%d lignes)", out_path, len(rows))
        return {
            "n": len(rows),
            "n_completed_pre": sum(1 for r in rows if r["pre_score"] != ""),
            "n_completed_post": sum(1 for r in rows if r["post_score"] != ""),
            "n_withdrawn": sum(1 for r in rows if r["withdrawn"] == "1"),
        }
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export pseudonymise des donnees user study en CSV"
    )
    parser.add_argument(
        "--out", type=Path,
        default=Path(__file__).resolve().parent.parent.parent
        / "analysis" / "study_data.csv",
        help="Chemin de sortie du CSV",
    )
    args = parser.parse_args()
    stats = export_to_csv(args.out)
    logger.info("Resume : %s", stats)


if __name__ == "__main__":
    main()
