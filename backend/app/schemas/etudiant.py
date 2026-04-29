from typing import Literal

from pydantic import BaseModel, Field

Langue = Literal["en", "fr"]


class EtudiantCreate(BaseModel):
    nom_complet: str
    email: str
    mot_de_passe: str
    niveau_actuel: str = "beginner"
    langue_preferee: Langue = "en"


class EtudiantResponse(BaseModel):
    id: int
    nom_complet: str
    email: str
    niveau_actuel: str
    langue_preferee: Langue = "en"

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
