from typing import Literal

from pydantic import BaseModel, EmailStr, Field

Langue = Literal["en", "fr"]


class EtudiantCreate(BaseModel):
    """Payload for POST /auth/register.

    SECURITY (12/05/2026): we now enforce EmailStr (RFC 5322 regex + syntactic
    check) and a password of at least 8 characters. Before this hardening a
    user could register with email='foo' / mot_de_passe='a', which :
      - broke SMTP sending in cascade (invalid addresses),
      - left accounts vulnerable to brute force.
    """
    nom_complet: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    mot_de_passe: str = Field(..., min_length=8, max_length=128,
                              description="Min 8 caracteres pour resister au brute force")
    niveau_actuel: str = "beginner"
    # Language required : no default, must be explicitly provided ('en' or 'fr').
    langue_preferee: Langue = Field(..., description="Langue d'apprentissage choisie au moment de l'inscription. Obligatoire.")


class EtudiantResponse(BaseModel):
    id: int
    nom_complet: str
    email: str
    niveau_actuel: str
    langue_preferee: Langue = "en"
    # Phase 3 : email verification state. The frontend can display a
    # "verify your email" banner in the dashboard as long as this is
    # False.
    is_verified: bool = False

    class Config:
        from_attributes = True


class EtudiantUpdate(BaseModel):
    nom_complet: str | None = None
    email: str | None = None
    mot_de_passe: str | None = None
    niveau_actuel: str | None = None
    langue_preferee: Langue | None = None


class EtudiantLanguageUpdate(BaseModel):
    langue_preferee: Langue = Field("en", description="Preferred UI and learning language.")


class LoginRequest(BaseModel):
    email: str
    mot_de_passe: str


class Token(BaseModel):
    access_token: str
    token_type: str


# ============================================================
# Phase 3 : email verification + reset password
# ============================================================
class EmailRequest(BaseModel):
    """Body for /auth/request-verification and /auth/forgot-password.

    We accept just an email. Intentionally we do NOT ask for the password :
    if the user forgot their password they cannot provide it, and even for
    verification it is useless (we identify by email).
    """
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Body for /auth/reset-password : token + new password."""
    token: str
    new_password: str = Field(..., min_length=8, description="Nouveau mot de passe (min 8 caracteres)")


class MessageResponse(BaseModel):
    """Generic 'message' response for endpoints that do not return
    structured data."""
    message: str
    detail: str | None = None
