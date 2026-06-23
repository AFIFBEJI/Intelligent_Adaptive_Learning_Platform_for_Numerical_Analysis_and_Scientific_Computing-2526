"""Helpers de localisation des messages d'erreur HTTP cote backend.

La langue est determinee dans cet ordre :
  1. Header HTTP `Accept-Language` (`en` ou `fr`).
  2. Profil utilisateur (`Etudiant.langue_preferee`) si on a un user_id.
  3. Defaut : `en`.

Usage typique dans un router :

    from fastapi import Request
    from app.core.i18n import http_msg, lang_from_request

    @router.get(...)
    def handler(request: Request, ...):
        lang = lang_from_request(request)
        raise HTTPException(404, http_msg("etudiant.not_found", lang))

Pour eviter d'avoir a injecter Request partout, on peut aussi recuperer la
langue via le helper `_user_language(db, etudiant_id)` deja present dans
quiz_dynamic.py.
"""
from __future__ import annotations

from typing import Optional

# Cle -> {"en": "...", "fr": "..."}
MESSAGES: dict[str, dict[str, str]] = {
    # Auth
    "auth.email_taken": {
        "en": "Email already in use.",
        "fr": "Email deja utilise.",
    },
    "auth.invalid_credentials": {
        "en": "Invalid email or password.",
        "fr": "Email ou mot de passe incorrect.",
    },
    "auth.student_not_found": {
        "en": "Student not found.",
        "fr": "Etudiant non trouve.",
    },
    # Etudiants
    "etudiant.not_found": {
        "en": "Student not found.",
        "fr": "Etudiant introuvable.",
    },
    "etudiant.modify_self_only": {
        "en": "You can only modify your own profile.",
        "fr": "Vous ne pouvez modifier que votre propre profil.",
    },
    "etudiant.delete_self_only": {
        "en": "You can only delete your own account.",
        "fr": "Vous ne pouvez supprimer que votre propre compte.",
    },
    "etudiant.deleted": {
        "en": "Student {id} deleted successfully.",
        "fr": "Etudiant {id} supprime avec succes.",
    },
    # Graph / contenu
    "graph.neo4j_unavailable": {
        "en": "Neo4j unavailable: {error}",
        "fr": "Neo4j inaccessible : {error}",
    },
    "graph.module_not_found": {
        "en": "Module '{id}' not found or empty.",
        "fr": "Module '{id}' introuvable ou sans concepts.",
    },
    "graph.concept_not_found": {
        "en": "Concept '{id}' not found or has no resources.",
        "fr": "Concept '{id}' introuvable ou sans ressources.",
    },
    "graph.no_content": {
        "en": "No content found for '{id}'.",
        "fr": "Pas de contenu pour '{id}'.",
    },
    "graph.no_remediation": {
        "en": "No remediation for '{id}'.",
        "fr": "Pas de remediation pour '{id}'.",
    },
    # Quiz
    "quiz.not_found": {
        "en": "Quiz {id} not found.",
        "fr": "Quiz {id} introuvable.",
    },
    "quiz.attempt_not_found": {
        "en": "Attempt {id} not found.",
        "fr": "Tentative {id} introuvable.",
    },
    "tutor.session_not_found": {
        "en": "Session {id} not found.",
        "fr": "Session {id} introuvable.",
    },
    "tutor.session_forbidden": {
        "en": "This session does not belong to you.",
        "fr": "Cette session ne vous appartient pas.",
    },
}


def _normalize(lang: Optional[str]) -> str:
    """Limite a 'fr' ou 'en'. Defaut 'en'."""
    if not lang:
        return "en"
    short = lang.lower().split(",")[0].split("-")[0].strip()
    return "fr" if short == "fr" else "en"


def http_msg(key: str, lang: Optional[str] = "en", **fmt) -> str:
    """Retourne le message localise pour la cle donnee, avec interpolation.

    Si la cle est inconnue, retourne la cle brute (utile pour debug).
    """
    lang = _normalize(lang)
    bundle = MESSAGES.get(key)
    if not bundle:
        return key
    template = bundle.get(lang) or bundle.get("en") or key
    if fmt:
        try:
            return template.format(**fmt)
        except (KeyError, IndexError):
            return template
    return template


def lang_from_request(request) -> str:
    """Detecte la langue a partir du header `Accept-Language`."""
    if request is None:
        return "en"
    raw = request.headers.get("accept-language") or request.headers.get("x-app-lang")
    return _normalize(raw)


def lang_from_user(db, etudiant_id: Optional[int]) -> str:
    """Detecte la langue a partir du profil utilisateur (PostgreSQL)."""
    if not etudiant_id:
        return "en"
    try:
        from app.models.etudiant import Etudiant
        e = db.query(Etudiant).filter(Etudiant.id == etudiant_id).first()
        if e and e.langue_preferee in ("en", "fr"):
            return e.langue_preferee
    except Exception:
        pass
    return "en"
