from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    creer_token,
    get_current_user,
    hacher_mot_de_passe,
    verifier_mot_de_passe,
)
from app.models.etudiant import Etudiant
from app.schemas.etudiant import (
    EtudiantCreate,
    EtudiantLanguageUpdate,
    EtudiantResponse,
    Token,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token)
def register(etudiant_data: EtudiantCreate, db: Session = Depends(get_db)):
    """Créer un nouveau compte étudiant."""
    # Vérifier si email existe déjà
    if db.query(Etudiant).filter(Etudiant.email == etudiant_data.email).first():
        raise HTTPException(status_code=400, detail="Email déjà utilisé.")

    # Créer l'étudiant
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

    # Retourner le token JWT
    token = creer_token(data={"sub": nouvel_etudiant.id})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    etudiant = db.query(Etudiant).filter(Etudiant.email == form_data.username).first()
    if not etudiant or not verifier_mot_de_passe(form_data.password, etudiant.mot_de_passe):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect.")
    token = creer_token(data={"sub": etudiant.id})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=EtudiantResponse)
def get_me(
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Voir le profil de l'étudiant connecté."""
    etudiant = db.query(Etudiant).filter(Etudiant.id == current_user_id).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé.")
    return etudiant


@router.put("/me/language", response_model=EtudiantResponse)
def update_my_language(
    payload: EtudiantLanguageUpdate,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Persist the student's preferred language for UI, tutor, content and quiz flows."""
    etudiant = db.query(Etudiant).filter(Etudiant.id == current_user_id).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé.")

    etudiant.langue_preferee = payload.langue_preferee
    db.commit()
    db.refresh(etudiant)
    return etudiant
