"""Router /study/* — orchestration de l'etude utilisateur Phase 4.

Flow normal d'un participant :

    1. POST /study/enroll        -> assignation participant_code + version A/B
    2. GET  /study/pretest       -> recupere 15 items (sans correct_answer)
    3. POST /study/pretest       -> submit -> score_pre + stratification + group
    4. (4 semaines d'usage de la plateforme normale)
    5. GET  /study/posttest      -> recupere les 15 items de l'autre version
    6. POST /study/posttest      -> submit -> score_post + learning_gain calcule
    7. POST /study/sus           -> questionnaire de satisfaction
    8. (optionnel) POST /study/withdraw -> retrait avec raison

Endpoints admin (gated par l'env STUDY_ADMIN_EMAILS) :
    GET  /study/admin/overview     -> stats globales
    GET  /study/admin/participants -> liste detaillee
    POST /study/admin/export       -> CSV pseudonymise (nouvel endpoint)

Securite :
    - Tous les endpoints requierent auth JWT (`get_current_user`).
    - Rate-limit applique sur enroll + submit pour eviter spam.
    - Le `participant_code` est genere serveur, jamais devinable.
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
# Helpers internes
# ============================================================
def _now() -> datetime:
    """UTC timestamp helper, naive (compatible avec les colonnes SQLite/PG)."""
    return datetime.now(UTC).replace(tzinfo=None)


def _generate_participant_code(db: Session) -> str:
    """Genere un pseudonyme P### unique. Retry sur collision (peu probable
    mais on est defensif)."""
    for _ in range(50):
        n = secrets.randbelow(900) + 100  # 100-999
        code = f"P{n}"
        exists = db.query(StudyParticipant).filter(
            StudyParticipant.participant_code == code
        ).first()
        if not exists:
            return code
    # Si on arrive ici on a recrute > 50 participants colliding -- impossible
    # en pratique mais on raise pour eviter le silent fallback.
    raise RuntimeError("Impossible de generer un participant_code unique apres 50 essais")


def _ensure_admin(current_user_id: int, db: Session) -> Etudiant:
    """Verifie que l'utilisateur courant est admin (whitelist via .env).

    Phase 4 : pas de role en DB pour ne pas alourdir le schema. On utilise
    une variable d'env STUDY_ADMIN_EMAILS = "alice@x.com,bob@y.com".
    """
    user = db.query(Etudiant).filter(Etudiant.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User introuvable")
    admin_emails = getattr(settings, "STUDY_ADMIN_EMAILS", "") or ""
    if user.email not in {e.strip() for e in admin_emails.split(",") if e.strip()}:
        raise HTTPException(status_code=403, detail="Reserve aux admins de l'etude")
    return user


def _stratify_group(pre_score: float, db: Session) -> str:
    """Allocation stratifiee aleatoire.

    3 strates par niveau initial : low (< 40), mid (40-70), high (>= 70).
    Dans chaque strate, on alloue alternativement adaptive / control pour
    tendre vers un equilibre 1:1 sans dependre du hasard pur. On regarde
    combien de participants existent deja dans la meme strate et on les
    flippe.
    """
    if pre_score < 40:
        stratum = "low"
    elif pre_score < 70:
        stratum = "mid"
    else:
        stratum = "high"

    # Compter combien dans la meme strate (approx : on lit ceux dont le
    # pre_score est dans la meme bin).
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
    # Alterner pair -> adaptive, impair -> control.
    return "adaptive" if count_in_stratum % 2 == 0 else "control"


def _log_event(
    db: Session, participant: StudyParticipant, event_type: str, payload: dict | None = None,
) -> None:
    """Helper pour append une trace dans study_events."""
    ev = StudyEvent(
        participant_id=participant.id,
        event_type=event_type,
        payload=payload or {},
        timestamp=_now(),
    )
    db.add(ev)
    # Le caller fait le commit final.


# ============================================================
# 1. Enrollment
# ============================================================
@router.post("/enroll", response_model=EnrollResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(AUTH_EMAIL_LIMIT)  # 3/min - on ne s'inscrit qu'une fois
def enroll(
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """Inscrit l'etudiant courant a l'etude utilisateur.

    Idempotent : si deja inscrit, retourne le code existant avec
    `already_enrolled=True`. Cela permet au frontend de simplement appeler
    `enroll` au premier accees a `/study` sans avoir a verifier l'etat.
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
    # Contre-balancing : alterne A_then_B / B_then_A en fonction du nb
    # actuels d'inscrits. Pair -> A_then_B, impair -> B_then_A.
    total = db.query(StudyParticipant).count()
    test_version = "A_then_B" if total % 2 == 0 else "B_then_A"

    participant = StudyParticipant(
        etudiant_id=current_user_id,
        participant_code=code,
        test_version=test_version,
        enrolled_at=_now(),
    )
    db.add(participant)
    db.flush()  # pour avoir participant.id
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
# 2. Pre-test : GET items
# ============================================================
@router.get("/pretest", response_model=TestStartResponse)
def get_pretest(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """Renvoie les 15 items du pre-test (sans correct_answer)."""
    participant = db.query(StudyParticipant).filter(
        StudyParticipant.etudiant_id == current_user_id
    ).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Pas inscrit a l'etude")

    version = "A" if participant.test_version == "A_then_B" else "B"
    items = items_for_version(version)
    # Log le start si premier acces
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
# 3. Pre-test : POST submit
# ============================================================
@router.post("/pretest", response_model=TestSubmitResponse)
@limiter.limit(LLM_LIGHT_LIMIT)
def submit_pretest(
    request: Request,
    payload: TestSubmitRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """Soumet les reponses du pre-test, calcule le score, assigne le groupe."""
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
    # Stratification + allocation aleatoire.
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
# 4. Post-test : GET items (utilise la version inverse)
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
# 5. Post-test : POST submit
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
# 6. SUS questionnaire post-etude
# ============================================================
@router.post("/sus", response_model=SUSSubmitResponse)
@limiter.limit(LLM_LIGHT_LIMIT)
def submit_sus(
    request: Request,
    payload: SUSSubmitRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """Recoit le score SUS-adapte (6 items Likert) + 3 questions ouvertes."""
    participant = db.query(StudyParticipant).filter(
        StudyParticipant.etudiant_id == current_user_id
    ).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Pas inscrit a l'etude")

    # Validation : chaque Likert doit etre dans [1, 5].
    for i, v in enumerate(payload.likert):
        if not (1 <= v <= 5):
            raise HTTPException(
                status_code=422,
                detail=f"Likert[{i}]={v} hors plage [1,5]",
            )
    raw_sum = sum(payload.likert)  # 6 a 30
    # Normalisation 0-100 : (raw - 6) / (30 - 6) * 100
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
    """Permet a un participant de se retirer de l'etude.

    Conforme RGPD art. 17. Marque withdrawn_at + raison ; les data brutes
    restent en DB pour analyse en intent-to-treat mais sont exclues du
    per-protocol. Pour suppression definitive, appeler ensuite DELETE
    /study/me (a implementer si demande explicite).
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
    """Vue agregee pour suivre l'etude en temps reel. Admin only."""
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
    """Liste detaillee des participants. Admin only.

    Note : on retourne le participant_code, PAS l'etudiant_id ni l'email.
    Pour la table de correspondance, faire un export separe limite.
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
