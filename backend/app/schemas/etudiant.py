from typing import Literal

from pydantic import BaseModel, EmailStr, Field

Langue = Literal["en", "fr"]


class EtudiantCreate(BaseModel):
    """Payload pour POST /auth/register.

    SECURITY (12/05/2026): on impose desormais EmailStr (regex RFC 5322 + check
    syntactique) et un mot de passe d'au moins 8 caracteres. Avant ce durcissement
    un user pouvait s'inscrire avec email='foo' / mot_de_passe='a', ce qui :
      - cassait l'envoi SMTP en cascade (adresses invalides),
      - laissait des comptes vulnerables au brute force.
    """
    nom_complet: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    mot_de_passe: str = Field(..., min_length=8, max_length=128,
                              description="Min 8 caracteres pour resister au brute force")
    niveau_actuel: str = "beginner"
    # Langue obligatoire : aucun défaut, doit être explicitement fournie ('en' ou 'fr').
    langue_preferee: Langue = Field(..., description="Langue d'apprentissage choisie au moment de l'inscription. Obligatoire.")


class EtudiantResponse(BaseModel):
    id: int
    nom_complet: str
    email: str
    niveau_actuel: str
    langue_preferee: Langue = "en"
    # Phase 3 : etat de verification de l'email. Le frontend peut
    # afficher un bandeau "verifie ton email" dans le dashboard tant
    # que c'est False.
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
# Phase 3 : verification email + reset password
# ============================================================
class EmailRequest(BaseModel):
    """Body pour /auth/request-verification et /auth/forgot-password.

    On accepte juste un email. Volontairement on ne demande PAS le mot de
    passe : si l'utilisateur a oublie son mot de passe il ne peut pas le
    fournir, et meme pour la verification c'est inutile (on identifie par
    email).
    """
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Body pour /auth/reset-password : token + nouveau mot de passe."""
    token: str
    new_password: str = Field(..., min_length=8, description="Nouveau mot de passe (min 8 caracteres)")


class MessageResponse(BaseModel):
    """Reponse generique 'message' pour les endpoints qui ne retournent
    pas de donnees structurees."""
    message: str
    detail: str | None = None
