from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.i18n import http_msg, lang_from_user
from app.core.security import get_current_user, hacher_mot_de_passe
from app.models.etudiant import Etudiant
from app.schemas.etudiant import EtudiantResponse, EtudiantUpdate

router = APIRouter(prefix="/etudiants", tags=["etudiants"])


@router.get("/", response_model=list[EtudiantResponse])
def lire_tous_les_etudiants(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """SECURITY: ne retourne QUE le profil de l'utilisateur connecte.

    Avant le 12/05/2026 cet endpoint retournait tous les etudiants a tout
    user connecte (IDOR + fuite RGPD : emails de tous les users exposes).
    On reduit a un tableau de 1 element pour preserver la signature de
    l'API tout en supprimant le leak. Si un jour on a un vrai role admin
    on pourra reactiver via `if user.is_admin: return db.query(...).all()`.
    """
    etudiant = db.query(Etudiant).filter(Etudiant.id == current_user_id).first()
    return [etudiant] if etudiant else []


@router.get("/{etudiant_id}", response_model=EtudiantResponse)
def lire_un_etudiant(
    etudiant_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """SECURITY: un etudiant ne peut consulter que son propre profil.

    Sans ce check, n'importe quel user connecte pouvait lire les donnees
    (email, niveau) de tout autre etudiant en faisant varier l'ID.
    """
    lang = lang_from_user(db, current_user_id)
    if current_user_id != etudiant_id:
        raise HTTPException(status_code=403, detail=http_msg("etudiant.modify_self_only", lang))
    etudiant = db.query(Etudiant).filter(Etudiant.id == etudiant_id).first()
    if etudiant is None:
        raise HTTPException(status_code=404, detail=http_msg("etudiant.not_found", lang))
    return etudiant


@router.put("/{etudiant_id}", response_model=EtudiantResponse)
def modifier_etudiant(
    etudiant_id: int,
    modifications: EtudiantUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    lang = lang_from_user(db, current_user_id)

    # Un etudiant ne peut modifier que son propre profil
    if current_user_id != etudiant_id:
        raise HTTPException(status_code=403, detail=http_msg("etudiant.modify_self_only", lang))

    etudiant = db.query(Etudiant).filter(Etudiant.id == etudiant_id).first()
    if etudiant is None:
        raise HTTPException(status_code=404, detail=http_msg("etudiant.not_found", lang))

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
    lang = lang_from_user(db, current_user_id)

    # Un etudiant ne peut supprimer que son propre compte
    if current_user_id != etudiant_id:
        raise HTTPException(status_code=403, detail=http_msg("etudiant.delete_self_only", lang))

    etudiant = db.query(Etudiant).filter(Etudiant.id == etudiant_id).first()
    if etudiant is None:
        raise HTTPException(status_code=404, detail=http_msg("etudiant.not_found", lang))
    db.delete(etudiant)
    db.commit()
    return {"message": http_msg("etudiant.deleted", lang, id=etudiant_id)}
