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
    """SECURITY: returns ONLY the logged-in user's profile.

    Before 12/05/2026 this endpoint returned all students to any
    logged-in user (IDOR + GDPR leak: emails of all users exposed).
    We reduce it to a 1-element array to preserve the API signature
    while removing the leak. If one day we have a real admin role
    we can reactivate it via `if user.is_admin: return db.query(...).all()`.
    """
    etudiant = db.query(Etudiant).filter(Etudiant.id == current_user_id).first()
    return [etudiant] if etudiant else []


@router.get("/{etudiant_id}", response_model=EtudiantResponse)
def lire_un_etudiant(
    etudiant_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """SECURITY: a student can only view their own profile.

    Without this check, any logged-in user could read the data
    (email, level) of any other student by varying the ID.
    """
    lang = lang_from_user(db, current_user_id)
    if current_user_id != etudiant_id:
        raise HTTPException(status_code=403, detail=http_msg("etudiant.modify_self_only", lang))
    etudiant = db.query(Etudiant).filter(Etudiant.id == etudiant_id).first()
    if etudiant is None:
        raise HTTPException(status_code=404, detail=http_msg("etudiant.not_found", lang))
    return etudiant


# Human-readable labels for the risk factors (Brique IA 4).
_FACTOR_LABELS = {
    "avg_score": {"fr": "Score moyen faible", "en": "Low average score"},
    "quizzes_count": {"fr": "Peu de quiz réalisés", "en": "Few quizzes taken"},
    "avg_time_min": {"fr": "Temps par quiz inhabituel", "en": "Unusual time per quiz"},
    "days_since_last": {"fr": "Inactivité récente", "en": "Recent inactivity"},
    "score_trend": {"fr": "Scores en baisse", "en": "Declining scores"},
    "avg_mastery": {"fr": "Maîtrise globale faible", "en": "Low overall mastery"},
    "low_mastery_ratio": {"fr": "Beaucoup de concepts non maîtrisés",
                          "en": "Many unmastered concepts"},
    "error_rate": {"fr": "Taux d'erreurs élevé", "en": "High error rate"},
}


@router.get("/{etudiant_id}/risk")
def evaluer_risque_etudiant(
    etudiant_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """Brique IA 4 — early-warning risk assessment for a student.

    SECURITY: a student can only assess their own risk (self-only),
    same rule as the profile endpoints.

    Returns the risk verdict, probability, the explanatory top factors,
    and the underlying features. If the model is unavailable or the
    student has no quiz history yet, returns {"available": false}.
    """
    lang = lang_from_user(db, current_user_id)
    if current_user_id != etudiant_id:
        raise HTTPException(status_code=403, detail=http_msg("etudiant.modify_self_only", lang))

    from app.services import risk_service

    assessment = risk_service.assess(db, etudiant_id)
    if assessment is None:
        return {"available": False}

    assessment["available"] = True
    assessment["factor_labels"] = [
        _FACTOR_LABELS.get(f, {}).get(lang, f) for f in assessment["top_factors"]
    ]
    return assessment


@router.put("/{etudiant_id}", response_model=EtudiantResponse)
def modifier_etudiant(
    etudiant_id: int,
    modifications: EtudiantUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    lang = lang_from_user(db, current_user_id)

    # A student can only modify their own profile
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

    # A student can only delete their own account
    if current_user_id != etudiant_id:
        raise HTTPException(status_code=403, detail=http_msg("etudiant.delete_self_only", lang))

    etudiant = db.query(Etudiant).filter(Etudiant.id == etudiant_id).first()
    if etudiant is None:
        raise HTTPException(status_code=404, detail=http_msg("etudiant.not_found", lang))
    db.delete(etudiant)
    db.commit()
    return {"message": http_msg("etudiant.deleted", lang, id=etudiant_id)}
