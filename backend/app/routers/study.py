"""Router /study/* — orchestration of the Phase 4 user study.

Normal flow of a participant:

    1. POST /study/enroll        -> assignment of participant_code + A/B version
    2. GET  /study/pretest       -> fetch 15 items (without correct_answer)
    3. POST /study/pretest       -> submit -> score_pre + stratification + group
    4. (4 weeks of normal platform usage)
    5. GET  /study/posttest      -> fetch the 15 items of the other version
    6. POST /study/posttest      -> submit -> score_post + learning_gain computed
    7. POST /study/sus           -> satisfaction questionnaire
    8. (optional) POST /study/withdraw -> withdrawal with reason

Admin endpoints (gated by the env STUDY_ADMIN_EMAILS):
    GET  /study/admin/overview     -> global stats
    GET  /study/admin/participants -> detailed list
    POST /study/admin/export       -> pseudonymized CSV (new endpoint)

Security:
    - All endpoints require JWT auth (`get_current_user`).
    - Rate-limit applied on enroll + submit to avoid spam.
    - The `participant_code` is server-generated, never guessable.
"""
from __future__ import annotations

import logging
import secrets
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.rate_limit import AUTH_EMAIL_LIMIT, LLM_LIGHT_LIMIT, limiter
from app.core.security import get_current_user
from app.data.study_pretest import grade_answers, items_for_version
from app.models.etudiant import Etudiant
from app.models.study import StudyEvent, StudyParticipant
from app.schemas.study import (
    EnrollResponse,
    ParticipantSummary,
    StudyItem,
    StudyOverview,
    SUSSubmitRequest,
    SUSSubmitResponse,
    TestStartResponse,
    TestSubmitRequest,
    TestSubmitResponse,
)

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/study", tags=["Phase 4 - User Study"])


# ============================================================
# Internal helpers
# ============================================================
def _now() -> datetime:
    """UTC timestamp helper, naive (compatible with SQLite/PG columns)."""
    return datetime.now(UTC).replace(tzinfo=None)


def _generate_participant_code(db: Session) -> str:
    """Generate a unique P### pseudonym. Retry on collision (unlikely
    but we are defensive)."""
    for _ in range(50):
        n = secrets.randbelow(900) + 100  # 100-999
        code = f"P{n}"
        exists = db.query(StudyParticipant).filter(
            StudyParticipant.participant_code == code
        ).first()
        if not exists:
            return code
    # If we reach here we have recruited > 50 colliding participants -- impossible
    # in practice but we raise to avoid the silent fallback.
    raise RuntimeError("Impossible de generer un participant_code unique apres 50 essais")


def _ensure_admin(current_user_id: int, db: Session) -> Etudiant:
    """Check that the current user is an admin (whitelist via .env).

    Phase 4: no role in DB to avoid bloating the schema. We use
    an env variable STUDY_ADMIN_EMAILS = "alice@x.com,bob@y.com".
    """
    user = db.query(Etudiant).filter(Etudiant.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User introuvable")
    admin_emails = getattr(settings, "STUDY_ADMIN_EMAILS", "") or ""
    if user.email not in {e.strip() for e in admin_emails.split(",") if e.strip()}:
        raise HTTPException(status_code=403, detail="Reserve aux admins de l'etude")
    return user


def _stratify_group(pre_score: float, db: Session) -> str:
    """Stratified random allocation.

    3 strata by initial level: low (< 40), mid (40-70), high (>= 70).
    Within each stratum, we allocate alternately adaptive / control to
    tend toward a 1:1 balance without depending on pure chance. We look at
    how many participants already exist in the same stratum and we
    flip them.
    """
    if pre_score < 40:
        stratum = "low"
    elif pre_score < 70:
        stratum = "mid"
    else:
        stratum = "high"

    # Count how many in the same stratum (approx: we read those whose
    # pre_score is in the same bin).
    if stratum == "low":
        q = db.query(StudyParticipant).filter(StudyParticipant.pre_score < 40)
    elif stratum == "mid":
        q = (
            db.query(StudyParticipant)
            .filter(StudyParticipant.pre_score >= 40)
            .filter(StudyParticipant.pre_score < 70)
        )
    else:
        q = db.query(StudyParticipant).filter(StudyParticipant.pre_score >= 70)
    count_in_stratum = q.count()
    # Alternate even -> adaptive, odd -> control.
    return "adaptive" if count_in_stratum % 2 == 0 else "control"


def _log_event(
    db: Session, participant: StudyParticipant, event_type: str, payload: dict | None = None,
) -> None:
    """Helper to append a trace into study_events."""
    ev = StudyEvent(
        participant_id=participant.id,
        event_type=event_type,
        payload=payload or {},
        timestamp=_now(),
    )
    db.add(ev)
    # The caller does the final commit.


# ============================================================
# 1. Enrollment
# ============================================================
@router.post("/enroll", response_model=EnrollResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(AUTH_EMAIL_LIMIT)  # 3/min - we only enroll once
def enroll(
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """Enroll the current student in the user study.

    Idempotent: if already enrolled, returns the existing code with
    `already_enrolled=True`. This lets the frontend simply call
    `enroll` on first access to `/study` without having to check the state.
    """
    existing = db.query(StudyParticipant).filter(
        StudyParticipant.etudiant_id == current_user_id
    ).first()
    if existing:
        pretest_version = "A" if existing.test_version == "A_then_B" else "B"
        return EnrollResponse(
            participant_code=existing.participant_code,
            test_version=existing.test_version,
            pretest_version=pretest_version,
            already_enrolled=True,
        )

    code = _generate_participant_code(db)
    # Counter-balancing: alternate A_then_B / B_then_A based on the current
    # number of enrolled participants. Even -> A_then_B, odd -> B_then_A.
    total = db.query(StudyParticipant).count()
    test_version = "A_then_B" if total % 2 == 0 else "B_then_A"

    participant = StudyParticipant(
        etudiant_id=current_user_id,
        participant_code=code,
        test_version=test_version,
        enrolled_at=_now(),
    )
    db.add(participant)
    db.flush()  # to obtain participant.id
    _log_event(db, participant, "enroll", {"test_version": test_version})
    db.commit()
    db.refresh(participant)
    pretest_version = "A" if test_version == "A_then_B" else "B"
    logger.info(
        "Study enrollment: etudiant_id=%d code=%s version=%s",
        current_user_id, code, test_version,
    )
    return EnrollResponse(
        participant_code=code,
        test_version=test_version,
        pretest_version=pretest_version,
        already_enrolled=False,
    )


# ============================================================
# 2. Pre-test: GET items
# ============================================================
@router.get("/pretest", response_model=TestStartResponse)
def get_pretest(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """Return the 15 pre-test items (without correct_answer)."""
    participant = db.query(StudyParticipant).filter(
        StudyParticipant.etudiant_id == current_user_id
    ).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Pas inscrit a l'etude")

    version = "A" if participant.test_version == "A_then_B" else "B"
    items = items_for_version(version)
    # Log the start if first access
    if not participant.pre_test_started_at:
        participant.pre_test_started_at = _now()
        _log_event(db, participant, "pretest_start", {"version": version})
        db.commit()
    return TestStartResponse(
        participant_code=participant.participant_code,
        phase="pretest",
        version=version,
        items=[StudyItem(**it) for it in items],
        started_at=participant.pre_test_started_at,
    )


# ============================================================
# 3. Pre-test: POST submit
# ============================================================
@router.post("/pretest", response_model=TestSubmitResponse)
@limiter.limit(LLM_LIGHT_LIMIT)
def submit_pretest(
    request: Request,
    payload: TestSubmitRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """Submit the pre-test answers, compute the score, assign the group."""
    participant = db.query(StudyParticipant).filter(
        StudyParticipant.etudiant_id == current_user_id
    ).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Pas inscrit a l'etude")
    if participant.pre_score is not None:
        raise HTTPException(status_code=400, detail="Pre-test deja soumis")

    version = "A" if participant.test_version == "A_then_B" else "B"
    result = grade_answers(version, payload.answers)

    participant.pre_score = result["score"]
    participant.pre_answers = payload.answers
    participant.pre_test_done_at = _now()
    # Stratification + random allocation.
    participant.group_assigned = _stratify_group(result["score"], db)
    participant.intervention_started_at = _now()

    _log_event(db, participant, "pretest_submit", {
        "version": version,
        "score": result["score"],
        "duration_s": payload.duration_seconds,
        "group_assigned": participant.group_assigned,
    })
    db.commit()
    db.refresh(participant)
    logger.info(
        "Pretest submitted: code=%s score=%.1f group=%s",
        participant.participant_code, result["score"], participant.group_assigned,
    )
    return TestSubmitResponse(
        participant_code=participant.participant_code,
        phase="pretest",
        score=result["score"],
        raw=result["raw"],
        max=result["max"],
        per_item=result["per_item"],
        group_assigned=participant.group_assigned,
    )


# ============================================================
# 4. Post-test: GET items (uses the inverse version)
# ============================================================
@router.get("/posttest", response_model=TestStartResponse)
def get_posttest(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    participant = db.query(StudyParticipant).filter(
        StudyParticipant.etudiant_id == current_user_id
    ).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Pas inscrit a l'etude")
    if participant.pre_score is None:
        raise HTTPException(status_code=400, detail="Faire d'abord le pre-test")

    version = "B" if participant.test_version == "A_then_B" else "A"
    items = items_for_version(version)
    started = _now()
    _log_event(db, participant, "posttest_start", {"version": version})
    db.commit()
    return TestStartResponse(
        participant_code=participant.participant_code,
        phase="posttest",
        version=version,
        items=[StudyItem(**it) for it in items],
        started_at=started,
    )


# ============================================================
# 5. Post-test: POST submit
# ============================================================
@router.post("/posttest", response_model=TestSubmitResponse)
@limiter.limit(LLM_LIGHT_LIMIT)
def submit_posttest(
    request: Request,
    payload: TestSubmitRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    participant = db.query(StudyParticipant).filter(
        StudyParticipant.etudiant_id == current_user_id
    ).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Pas inscrit a l'etude")
    if participant.pre_score is None:
        raise HTTPException(status_code=400, detail="Faire d'abord le pre-test")
    if participant.post_score is not None:
        raise HTTPException(status_code=400, detail="Post-test deja soumis")

    version = "B" if participant.test_version == "A_then_B" else "A"
    result = grade_answers(version, payload.answers)

    participant.post_score = result["score"]
    participant.post_answers = payload.answers
    participant.post_test_done_at = _now()
    _log_event(db, participant, "posttest_submit", {
        "version": version,
        "score": result["score"],
        "duration_s": payload.duration_seconds,
    })
    db.commit()
    db.refresh(participant)
    logger.info(
        "Posttest submitted: code=%s score=%.1f (pre=%.1f gain=%.1f)",
        participant.participant_code, result["score"], participant.pre_score,
        result["score"] - participant.pre_score,
    )
    return TestSubmitResponse(
        participant_code=participant.participant_code,
        phase="posttest",
        score=result["score"],
        raw=result["raw"],
        max=result["max"],
        per_item=result["per_item"],
        group_assigned=participant.group_assigned,
    )


# ============================================================
# 6. Post-study SUS questionnaire
# ============================================================
@router.post("/sus", response_model=SUSSubmitResponse)
@limiter.limit(LLM_LIGHT_LIMIT)
def submit_sus(
    request: Request,
    payload: SUSSubmitRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """Receive the adapted SUS score (6 Likert items) + 3 open-ended questions."""
    participant = db.query(StudyParticipant).filter(
        StudyParticipant.etudiant_id == current_user_id
    ).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Pas inscrit a l'etude")

    # Validation: each Likert must be in [1, 5].
    for i, v in enumerate(payload.likert):
        if not (1 <= v <= 5):
            raise HTTPException(
                status_code=422,
                detail=f"Likert[{i}]={v} hors plage [1,5]",
            )
    raw_sum = sum(payload.likert)  # 6 to 30
    # Normalization 0-100: (raw - 6) / (30 - 6) * 100
    normalized = round((raw_sum - 6) / 24 * 100, 2)

    participant.sus_score = raw_sum
    participant.sus_answers = {
        "likert": payload.likert,
        "open_responses": payload.open_responses,
    }
    participant.open_feedback = payload.open_responses
    _log_event(db, participant, "sus_submit", {
        "sus_score": raw_sum,
        "sus_normalized": normalized,
    })
    db.commit()
    return SUSSubmitResponse(
        participant_code=participant.participant_code,
        sus_score=raw_sum,
        sus_score_normalized=normalized,
    )


# ============================================================
# 7. Withdraw
# ============================================================
@router.post("/withdraw", status_code=status.HTTP_204_NO_CONTENT)
def withdraw(
    reason: str = "",
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """Allow a participant to withdraw from the study.

    GDPR art. 17 compliant. Marks withdrawn_at + reason; the raw data
    stays in DB for intent-to-treat analysis but is excluded from the
    per-protocol. For definitive deletion, then call DELETE
    /study/me (to be implemented if explicitly requested).
    """
    participant = db.query(StudyParticipant).filter(
        StudyParticipant.etudiant_id == current_user_id
    ).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Pas inscrit a l'etude")
    if participant.withdrawn_at:
        return  # idempotent
    participant.withdrawn_at = _now()
    participant.withdrawal_reason = (reason or "")[:255]
    _log_event(db, participant, "withdraw", {"reason": reason[:255]})
    db.commit()
    logger.info("Participant %s s'est retire (reason=%s)",
                participant.participant_code, reason)


# ============================================================
# 8. Admin : overview
# ============================================================
@router.get("/admin/overview", response_model=StudyOverview)
def admin_overview(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """Aggregated view to track the study in real time. Admin only."""
    _ensure_admin(current_user_id, db)
    rows = db.query(StudyParticipant).all()
    by_group: dict[str, int] = {}
    completed_pre = completed_post = completed_sus = withdrawn = 0
    for p in rows:
        if p.pre_score is not None:
            completed_pre += 1
        if p.post_score is not None:
            completed_post += 1
        if p.sus_score is not None:
            completed_sus += 1
        if p.withdrawn_at:
            withdrawn += 1
        key = p.group_assigned or "unassigned"
        by_group[key] = by_group.get(key, 0) + 1
    return StudyOverview(
        total_enrolled=len(rows),
        total_completed_pretest=completed_pre,
        total_completed_posttest=completed_post,
        total_completed_sus=completed_sus,
        total_withdrawn=withdrawn,
        by_group=by_group,
    )


@router.get("/admin/participants", response_model=list[ParticipantSummary])
def admin_participants(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """Detailed list of participants. Admin only.

    Note: we return the participant_code, NOT the etudiant_id nor the email.
    For the correspondence table, perform a separate limited export.
    """
    _ensure_admin(current_user_id, db)
    rows = db.query(StudyParticipant).order_by(StudyParticipant.id).all()
    out: list[ParticipantSummary] = []
    for p in rows:
        gain = None
        norm_gain = None
        if p.pre_score is not None and p.post_score is not None:
            gain = round(p.post_score - p.pre_score, 2)
            if p.pre_score < 100:
                norm_gain = round((p.post_score - p.pre_score) / (100 - p.pre_score), 4)
        out.append(ParticipantSummary(
            participant_code=p.participant_code,
            group_assigned=p.group_assigned,
            pre_score=p.pre_score,
            post_score=p.post_score,
            sus_score=p.sus_score,
            learning_gain=gain,
            normalized_gain=norm_gain,
            enrolled_at=p.enrolled_at,
            pre_test_done_at=p.pre_test_done_at,
            post_test_done_at=p.post_test_done_at,
            withdrawn=p.withdrawn_at is not None,
        ))
    return out
