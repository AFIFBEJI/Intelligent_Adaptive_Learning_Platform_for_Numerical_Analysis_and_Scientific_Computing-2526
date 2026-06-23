import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.i18n import http_msg, lang_from_request
from app.core.rate_limit import AUTH_EMAIL_LIMIT, AUTH_LOGIN_LIMIT, limiter
from app.core.security import (
    create_reset_password_token,
    create_verification_token,
    creer_token,
    decode_reset_password_token,
    decode_verification_token,
    get_current_user,
    hacher_mot_de_passe,
    verifier_mot_de_passe,
)
from app.models.etudiant import Etudiant
from app.schemas.etudiant import (
    EmailRequest,
    EtudiantCreate,
    EtudiantLanguageUpdate,
    EtudiantResponse,
    MessageResponse,
    ResetPasswordRequest,
    Token,
)
from app.services.mail_service import (
    send_reset_password_email,
    send_verification_email,
)

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/auth", tags=["auth"])


# ============================================================
# Internal helpers (sending emails + verifications)
# ============================================================
def _send_verification_for(student: Etudiant) -> None:
    """Generate a verification token + send the email. Updates
    verification_sent_at for the DB-side rate-limit. The caller must call
    db.commit() afterwards."""
    token = create_verification_token(student.id)
    link = f"{settings.FRONTEND_URL.rstrip('/')}/verify-email/{token}"
    try:
        send_verification_email(
            to_email=student.email,
            name=student.nom_complet or "",
            link=link,
            language=student.langue_preferee or "en",
        )
    except Exception as exc:  # noqa: BLE001
        # We do NOT block registration if the email fails. The user
        # will be able to request a resend via /auth/request-verification.
        logger.exception("Echec envoi email verification : %s", exc)
    student.verification_sent_at = datetime.now(UTC)


def _send_reset_for(student: Etudiant) -> None:
    """Same for the password reset."""
    token = create_reset_password_token(student.id)
    link = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password/{token}"
    try:
        send_reset_password_email(
            to_email=student.email,
            name=student.nom_complet or "",
            link=link,
            language=student.langue_preferee or "en",
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Echec envoi email reset : %s", exc)


@router.post("/register", response_model=Token)
@limiter.limit(AUTH_EMAIL_LIMIT)
def register(etudiant_data: EtudiantCreate, request: Request, db: Session = Depends(get_db)):
    """Create a new student account + send a verification email.

    Rate-limited (AUTH_EMAIL_LIMIT) to prevent mass account creation and
    email-relay abuse: each registration triggers a verification email.
    """
    # The language of the error response follows the language chosen at registration,
    # otherwise the Accept-Language header.
    lang = etudiant_data.langue_preferee or lang_from_request(request)

    if db.query(Etudiant).filter(Etudiant.email == etudiant_data.email).first():
        raise HTTPException(status_code=400, detail=http_msg("auth.email_taken", lang))

    # Create the student. is_verified defaults to False (cf. model).
    nouvel_etudiant = Etudiant(
        nom_complet=etudiant_data.nom_complet,
        email=etudiant_data.email,
        mot_de_passe=hacher_mot_de_passe(etudiant_data.mot_de_passe),
        niveau_actuel=etudiant_data.niveau_actuel,
        langue_preferee=etudiant_data.langue_preferee,
    )
    db.add(nouvel_etudiant)
    db.commit()
    db.refresh(nouvel_etudiant)

    # Phase 3: send the verification email automatically.
    # Does not block registration on failure.
    _send_verification_for(nouvel_etudiant)
    db.commit()

    # Return the JWT token (the user can already log in,
    # but their is_verified stays False until they click the link).
    token = creer_token(data={"sub": nouvel_etudiant.id})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
@limiter.limit(AUTH_LOGIN_LIMIT)
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """SECURITY: rate-limited to 10/min/IP to block brute-force.
    Beyond that we return 429 + Retry-After."""
    lang = lang_from_request(request)
    etudiant = db.query(Etudiant).filter(Etudiant.email == form_data.username).first()
    if not etudiant or not verifier_mot_de_passe(form_data.password, etudiant.mot_de_passe):
        raise HTTPException(status_code=401, detail=http_msg("auth.invalid_credentials", lang))
    token = creer_token(data={"sub": etudiant.id})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=EtudiantResponse)
def get_me(
    request: Request,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """View the profile of the logged-in student."""
    etudiant = db.query(Etudiant).filter(Etudiant.id == current_user_id).first()
    if not etudiant:
        lang = lang_from_request(request)
        raise HTTPException(status_code=404, detail=http_msg("auth.student_not_found", lang))
    return etudiant


@router.put("/me/language", response_model=EtudiantResponse)
def update_my_language(
    payload: EtudiantLanguageUpdate,
    request: Request,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Persist the student's preferred language for UI, tutor, content and quiz flows."""
    etudiant = db.query(Etudiant).filter(Etudiant.id == current_user_id).first()
    if not etudiant:
        # We use the language they are precisely trying to set, otherwise the header.
        lang = payload.langue_preferee or lang_from_request(request)
        raise HTTPException(status_code=404, detail=http_msg("auth.student_not_found", lang))

    etudiant.langue_preferee = payload.langue_preferee
    db.commit()
    db.refresh(etudiant)
    return etudiant


# ============================================================
# PHASE 3: email verification + password reset
# ============================================================

@router.post("/request-verification", response_model=MessageResponse)
@limiter.limit(AUTH_EMAIL_LIMIT)
def request_verification(request: Request, payload: EmailRequest, db: Session = Depends(get_db)):
    """Resend the verification email.

    Security: we ALWAYS return the same response whether the email exists
    or not, to avoid user enumeration. If the account exists and is not
    already verified, we send. Rate limit: no more than one send per
    EMAIL_VERIFICATION_RESEND_COOLDOWN_SEC seconds.
    """
    student = db.query(Etudiant).filter(Etudiant.email == payload.email).first()
    if student and not student.is_verified:
        # Rate limit
        if student.verification_sent_at:
            elapsed = (datetime.now(UTC) - student.verification_sent_at.replace(tzinfo=UTC)).total_seconds()
            if elapsed < settings.EMAIL_VERIFICATION_RESEND_COOLDOWN_SEC:
                wait = int(settings.EMAIL_VERIFICATION_RESEND_COOLDOWN_SEC - elapsed)
                raise HTTPException(
                    status_code=429,
                    detail=f"Patiente {wait}s avant de redemander un email de verification.",
                )
        _send_verification_for(student)
        db.commit()
    # Generic response: do not reveal whether the email exists or not.
    return MessageResponse(
        message="Si ce compte existe et n'est pas verifie, un email de verification a ete envoye.",
    )


@router.get("/verify-email/{token}", response_model=MessageResponse)
def verify_email(token: str, db: Session = Depends(get_db)):
    """Target endpoint of the link sent by email. Validates the token and sets
    is_verified=True on the account. Idempotent: re-verifying breaks nothing."""
    user_id = decode_verification_token(token)
    student = db.query(Etudiant).filter(Etudiant.id == user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Compte introuvable")

    if student.is_verified:
        return MessageResponse(
            message="Compte deja verifie",
            detail="Tu peux te connecter normalement.",
        )

    student.is_verified = True
    student.email_verified_at = datetime.now(UTC)
    db.commit()
    logger.info("Compte etudiant id=%d verifie via email", student.id)
    return MessageResponse(
        message="Compte verifie avec succes",
        detail="Tu peux maintenant te connecter.",
    )


@router.post("/forgot-password", response_model=MessageResponse)
@limiter.limit(AUTH_EMAIL_LIMIT)
def forgot_password(request: Request, payload: EmailRequest, db: Session = Depends(get_db)):
    """Send an email with a password reset link.

    Product choice: we explicitly REVEAL whether the email exists or not, for
    a better UX (the user knows whether they need to create an account or just
    mistyped their email). We thus accept the risk of user enumeration
    through this page (an attacker can test which emails have an account).
    If security becomes a concern later, we can revert to a neutral message;
    in the meantime the UX friction disappears.
    """
    student = db.query(Etudiant).filter(Etudiant.email == payload.email).first()
    if not student:
        # Non-existent account: we explicitly say they need to register.
        raise HTTPException(
            status_code=404,
            detail="No account found with this email. Please create one first.",
        )

    _send_reset_for(student)
    return MessageResponse(
        message="Reset email sent! Check your inbox.",
        detail="The link is valid for 1 hour.",
    )


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Accept a reset token + new password. Updates the hash."""
    user_id = decode_reset_password_token(payload.token)
    student = db.query(Etudiant).filter(Etudiant.id == user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Compte introuvable")

    student.mot_de_passe = hacher_mot_de_passe(payload.new_password)
    # Welcome side effect: a user who can reset their password
    # necessarily has access to their email -> we can consider their email verified.
    if not student.is_verified:
        student.is_verified = True
        student.email_verified_at = datetime.now(UTC)
    db.commit()
    logger.info("Password reset reussi pour etudiant id=%d", student.id)
    return MessageResponse(
        message="Mot de passe reinitialise avec succes",
        detail="Tu peux maintenant te connecter avec ton nouveau mot de passe.",
    )
