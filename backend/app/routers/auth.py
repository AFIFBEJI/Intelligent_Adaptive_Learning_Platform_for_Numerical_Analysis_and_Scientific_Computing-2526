import logging
from datetime import UTC, datetime, timedelta

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
# Helpers internes (envoi mails + verifications)
# ============================================================
def _send_verification_for(student: Etudiant) -> None:
    """Genere un token de verification + envoie l'email. Met a jour
    verification_sent_at pour le rate-limit cote DB. Le caller doit faire
    db.commit() apres."""
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
        # On NE bloque PAS l'inscription si le mail rate. L'utilisateur
        # pourra demander un renvoi via /auth/request-verification.
        logger.exception("Echec envoi email verification : %s", exc)
    student.verification_sent_at = datetime.now(UTC)


def _send_reset_for(student: Etudiant) -> None:
    """Idem pour le reset password."""
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
def register(etudiant_data: EtudiantCreate, request: Request, db: Session = Depends(get_db)):
    """Creer un nouveau compte etudiant + envoyer email de verification."""
    # La langue de la reponse d'erreur suit la langue choisie a l'inscription,
    # sinon le header Accept-Language.
    lang = etudiant_data.langue_preferee or lang_from_request(request)

    if db.query(Etudiant).filter(Etudiant.email == etudiant_data.email).first():
        raise HTTPException(status_code=400, detail=http_msg("auth.email_taken", lang))

    # Créer l'étudiant. is_verified default False (cf. modele).
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

    # Phase 3 : envoyer email de verification automatiquement.
    # Ne bloque pas l'inscription en cas d'echec.
    _send_verification_for(nouvel_etudiant)
    db.commit()

    # Retourner le token JWT (l'utilisateur peut deja se connecter,
    # mais son is_verified est False jusqu'a ce qu'il clique le lien).
    token = creer_token(data={"sub": nouvel_etudiant.id})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
@limiter.limit(AUTH_LOGIN_LIMIT)
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """SECURITY: rate-limite a 10/min/IP pour bloquer le brute-force.
    Au-dela on retourne 429 + Retry-After."""
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
    """Voir le profil de l'etudiant connecte."""
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
        # On utilise la langue qu'il essaie justement de definir, sinon le header.
        lang = payload.langue_preferee or lang_from_request(request)
        raise HTTPException(status_code=404, detail=http_msg("auth.student_not_found", lang))

    etudiant.langue_preferee = payload.langue_preferee
    db.commit()
    db.refresh(etudiant)
    return etudiant


# ============================================================
# PHASE 3 : verification email + reset password
# ============================================================

@router.post("/request-verification", response_model=MessageResponse)
@limiter.limit(AUTH_EMAIL_LIMIT)
def request_verification(request: Request, payload: EmailRequest, db: Session = Depends(get_db)):
    """Renvoyer l'email de verification.

    Securite : on retourne TOUJOURS la meme reponse que l'email existe ou
    pas, pour eviter le user enumeration. Si le compte existe et n'est
    pas deja verifie, on envoie. Rate limit : pas plus d'un envoi par
    EMAIL_VERIFICATION_RESEND_COOLDOWN_SEC secondes.
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
    # Reponse generique : ne pas reveler si l'email existe ou pas.
    return MessageResponse(
        message="Si ce compte existe et n'est pas verifie, un email de verification a ete envoye.",
    )


@router.get("/verify-email/{token}", response_model=MessageResponse)
def verify_email(token: str, db: Session = Depends(get_db)):
    """Endpoint cible du lien envoye par email. Valide le token et passe
    is_verified=True sur le compte. Idempotent : reverifier ne casse rien."""
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
    """Envoyer un email avec un lien de reset password.

    Choix produit : on REVELE explicitement si l'email existe ou non, pour
    une meilleure UX (l'utilisateur sait s'il doit creer un compte ou s'il
    a juste mal tape son email). On accepte ainsi le risque d'user
    enumeration par cette page (un attaquant peut tester quels emails ont
    un compte). Si la securite devient un enjeu plus tard, on pourra revenir
    a un message neutre ; en attendant la friction UX disparait.
    """
    student = db.query(Etudiant).filter(Etudiant.email == payload.email).first()
    if not student:
        # Compte inexistant : on dit explicitement qu'il faut s'inscrire.
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
    """Accepte un token de reset + nouveau mot de passe. Met a jour le hash."""
    user_id = decode_reset_password_token(payload.token)
    student = db.query(Etudiant).filter(Etudiant.id == user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Compte introuvable")

    student.mot_de_passe = hacher_mot_de_passe(payload.new_password)
    # Side effect bienvenu : un user qui sait reset son mot de passe a
    # forcement acces a son email -> on peut considerer son email verifie.
    if not student.is_verified:
        student.is_verified = True
        student.email_verified_at = datetime.now(UTC)
    db.commit()
    logger.info("Password reset reussi pour etudiant id=%d", student.id)
    return MessageResponse(
        message="Mot de passe reinitialise avec succes",
        detail="Tu peux maintenant te connecter avec ton nouveau mot de passe.",
    )
