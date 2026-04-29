from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, hacher_mot_de_passe
from app.models.etudiant import Etudiant
from app.schemas.etudiant import EtudiantResponse, EtudiantUpdate

router = APIRouter(prefix="/etudiants", tags=["etudiants"])


@router.get("/", response_model=list[EtudiantResponse])
def lire_tous_les_etudiants(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    return db.query(Etudiant).all()


@router.get("/{etudiant_id}", response_model=EtudiantResponse)
def lire_un_etudiant(
    etudiant_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    etudiant = db.query(Etudiant).filter(Etudiant.id == etudiant_id).first()
    if etudiant is None:
        raise HTTPException(status_code=404, detail="Étudiant introuvable.")
    return etudiant


@router.put("/{etudiant_id}", response_model=EtudiantResponse)
def modifier_etudiant(
    etudiant_id: int,
    modifications: EtudiantUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    # Un étudiant ne peut modifier que son propre profil
    if current_user_id != etudiant_id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez modifier que votre propre profil.")

    etudiant = db.query(Etudiant).filter(Etudiant.id == etudiant_id).first()
    if etudiant is None:
        raise HTTPException(status_code=404, detail="Étudiant introuvable.")

    if modifications.nom_complet is not None:
        etudiant.nom_complet = modifications.nom_complet
    if modifications.email is not None:
        etudiant.email = modifications.email
    if modifications.mot_de_passe is not None:
        etudiant.mot_de_passe = hacher_mot_de_passe(modifications.mot_de_passe)
    if modifications.niveau_actuel is not None:
        etudiant.niveau_actuel = modifications.niveau_actuel
    if modifications.langue_preferee is not None:
        etudiant.langue_preferee = modifications.langue_preferee

    db.commit()
    db.refresh(etudiant)
    return etudiant


@router.delete("/{etudiant_id}")
def supprimer_etudiant(
    etudiant_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    # Un étudiant ne peut supprimer que son propre compte
    if current_user_id != etudiant_id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez supprimer que votre propre compte.")

    etudiant = db.query(Etudiant).filter(Etudiant.id == etudiant_id).first()
    if etudiant is None:
        raise HTTPException(status_code=404, detail="Étudiant introuvable.")
    db.delete(etudiant)
    db.commit()
    return {"message": f"Étudiant {etudiant_id} supprimé avec succès."}
