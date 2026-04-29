# ============================================================
# Router Quiz Dynamique — /quiz-ai
# ============================================================
# Endpoints :
#   POST   /quiz-ai/generate            → génère un quiz frais
#   GET    /quiz-ai/{quiz_id}           → (re)récupère un quiz en cours
#   POST   /quiz-ai/{quiz_id}/submit    → soumet + reçoit carte feedback
#   GET    /quiz-ai/attempts            → historique des tentatives
#   GET    /quiz-ai/attempts/{id}       → détail d'une tentative + feedback
#
# Protection IDOR : l'étudiant ne voit QUE ses propres tentatives, et ne
# peut soumettre que des quiz qu'il a lui-même générés.
# ============================================================
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.etudiant import Etudiant
from app.models.quiz import Quiz, QuizResult
from app.schemas.quiz_dynamic import (
    AttemptSummary,
    FeedbackCard,
    QuestionEvaluation,
    QuizGenerateRequest,
    QuizGenerateResponse,
    QuizSubmitRequest,
    QuizSubmitResponse,
    StudentFacingQuestion,
)
from app.services.feedback_service import feedback_service
from app.services.quiz_localization import normalize_quiz_language
from app.services.quiz_service import quiz_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/quiz-ai",
    tags=["Quiz IA Dynamique"],
)


def _user_language(db: Session, etudiant_id: int) -> str:
    student = db.query(Etudiant).filter(Etudiant.id == etudiant_id).first()
    return normalize_quiz_language(getattr(student, "langue_preferee", "en"))


# ============================================================
# Helpers
# ============================================================
def _strip_questions_for_student(
    questions: list[dict],
) -> list[StudentFacingQuestion]:
    """Retire correct_answer et explanation avant envoi au frontend."""
    return [
        StudentFacingQuestion(
            id=q.get("id"),
            type=q.get("type", "mcq"),
            question=q.get("question", ""),
            options=q.get("options"),
            difficulty=q.get("difficulty", "moyen"),
            language=q.get("language", "en") if q.get("language") in {"en", "fr"} else "en",
        )
        for q in questions
    ]


def _quiz_language(quiz: Quiz, fallback: str = "en") -> str:
    if fallback not in {"en", "fr"}:
        fallback = "en"
    for question in quiz.questions or []:
        lang = question.get("language")
        if lang in {"en", "fr"}:
            return lang
    return fallback


def _concept_name_from_id(concept_id: str | None) -> str | None:
    """Récupère le nom du concept depuis Neo4j (best-effort)."""
    if not concept_id:
        return None
    try:
        from app.graph.neo4j_connection import neo4j_conn

        rows = neo4j_conn.run_query(
            "MATCH (c:Concept {id: $cid}) RETURN c.name AS name",
            {"cid": concept_id},
        )
        return rows[0]["name"] if rows else None
    except Exception:  # noqa: BLE001
        return None


def _get_accessible_quiz(db: Session, quiz_id: int, etudiant_id: int) -> Quiz:
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz {quiz_id} introuvable.",
        )

    is_private_generated = (
        quiz.source == "generated"
        and quiz.etudiant_generateur_id
        and quiz.etudiant_generateur_id != etudiant_id
    )
    if is_private_generated:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ce quiz ne vous appartient pas.",
        )

    return quiz


# ============================================================
# ENDPOINT 1 : Générer un quiz dynamique
# ============================================================
@router.post(
    "/generate",
    response_model=QuizGenerateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Générer un quiz dynamique personnalisé",
)
async def generate_quiz(
    request: QuizGenerateRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """
    Génère un quiz frais via LLM adapté au niveau de l'étudiant.

    Chaque appel produit des questions différentes (seed temporel).
    """
    try:
        quiz = await quiz_service.generate_quiz(
            db=db,
            etudiant_id=current_user_id,
            concept_id=request.concept_id,
            topic=request.topic,
            n_questions=request.n_questions,
            difficulty_override=request.difficulty,
            question_types=request.question_types,
            use_llm=request.use_llm,
            language=request.language or _user_language(db, current_user_id),
        )
    except RuntimeError as exc:
        logger.error("Échec génération quiz : %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Le tuteur IA n'a pas pu générer le quiz : {exc}",
        ) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Erreur inattendue génération quiz")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne : {exc}",
        ) from exc

    return QuizGenerateResponse(
        quiz_id=quiz.id,
        titre=quiz.titre,
        module=quiz.module,
        difficulte=quiz.difficulte,
        concept_id=quiz.concept_neo4j_id,
        concept_name=_concept_name_from_id(quiz.concept_neo4j_id),
        questions=_strip_questions_for_student(quiz.questions or []),
        n_questions=len(quiz.questions or []),
        language=_quiz_language(quiz, request.language or _user_language(db, current_user_id)),
        date_creation=quiz.date_creation,
    )


# ============================================================
# ENDPOINT 1 BIS : Quiz diagnostique (onboarding nouvel etudiant)
# ============================================================
@router.post(
    "/diagnostic",
    response_model=QuizGenerateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generer un quiz diagnostique multi-concepts (onboarding)",
)
async def generate_diagnostic(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """
    Genere un quiz diagnostique de 5 questions sur 5 concepts fondamentaux
    differents, repartis sur les 3 modules de la plateforme.

    Appele typiquement juste apres l'inscription pour mesurer le niveau
    initial de l'etudiant et amorcer ses concept_mastery dans PostgreSQL.

    Le quiz a `module="Diagnostic"`, `concept_id=None` (multi-concepts).
    Chaque question est ratachee a un concept_id Neo4j precis pour que
    feedback_service.update_mastery_from_evaluations() puisse creer les
    lignes ConceptMastery initiales a la soumission.

    Aucun parametre — la selection des concepts est faite cote serveur
    pour garantir la coherence et eviter les attaques d'enumeration.
    """
    try:
        quiz = await quiz_service.generate_diagnostic_quiz(
            db=db,
            etudiant_id=current_user_id,
            n_concepts=5,
            language=_user_language(db, current_user_id),
        )
    except RuntimeError as exc:
        logger.error("Echec generation quiz diagnostique : %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Le tuteur IA n'a pas pu generer le quiz diagnostique : {exc}",
        ) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Erreur inattendue quiz diagnostique")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne : {exc}",
        ) from exc

    return QuizGenerateResponse(
        quiz_id=quiz.id,
        titre=quiz.titre,
        module=quiz.module,
        difficulte=quiz.difficulte,
        concept_id=None,
        concept_name=None,  # multi-concepts : pas de concept unique
        questions=_strip_questions_for_student(quiz.questions or []),
        n_questions=len(quiz.questions or []),
        language=_quiz_language(quiz, _user_language(db, current_user_id)),
        date_creation=quiz.date_creation,
    )


# ============================================================
# ENDPOINT 2 : Récupérer un quiz dynamique (sans réponses)
# ============================================================
@router.get(
    "/{quiz_id}",
    response_model=QuizGenerateResponse,
    summary="Récupérer un quiz dynamique (reprise de session)",
)
async def get_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    quiz = _get_accessible_quiz(db, quiz_id, current_user_id)

    return QuizGenerateResponse(
        quiz_id=quiz.id,
        titre=quiz.titre,
        module=quiz.module,
        difficulte=quiz.difficulte,
        concept_id=quiz.concept_neo4j_id,
        concept_name=_concept_name_from_id(quiz.concept_neo4j_id),
        questions=_strip_questions_for_student(quiz.questions or []),
        n_questions=len(quiz.questions or []),
        language=_quiz_language(quiz, _user_language(db, current_user_id)),
        date_creation=quiz.date_creation,
    )


# ============================================================
# ENDPOINT 3 : Soumettre un quiz
# ============================================================
@router.post(
    "/{quiz_id}/submit",
    response_model=QuizSubmitResponse,
    summary="Soumettre un quiz et recevoir la carte de feedback",
)
async def submit_quiz(
    quiz_id: int,
    request: QuizSubmitRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """
    Évalue les réponses, construit la carte pédagogique, met à jour
    la maîtrise des concepts touchés, puis persiste la tentative.
    """
    quiz = _get_accessible_quiz(db, quiz_id, current_user_id)
    response_language = request.language or _user_language(db, current_user_id)

    # --- Évaluation question par question ---
    evaluations = await feedback_service.evaluate_answers(quiz, request.answers)

    # --- Carte de feedback (LLM) ---
    try:
        card = await feedback_service.build_feedback_card(
            quiz=quiz,
            evaluations=evaluations,
            temps_reponse=request.temps_reponse,
            language=response_language,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Construction carte feedback échouée")
        # Fallback minimal
        n_total = len(evaluations)
        n_correct = sum(1 for e in evaluations if e.is_correct)
        points = sum(e.partial_credit for e in evaluations)
        score = (points / n_total * 100.0) if n_total else 0.0
        card = FeedbackCard(
            score=round(score, 1),
            n_correct=n_correct,
            n_total=n_total,
            temps_reponse=request.temps_reponse,
            grade_label=feedback_service._grade_label(score, response_language),
            summary=(
                f"Score {score:.0f}/100. Detailed feedback is unavailable."
                if response_language == "en"
                else f"Score {score:.0f}/100. (Feedback detaille indisponible)"
            ),
        )

    # --- Persistance de la tentative ---
    attempt = QuizResult(
        etudiant_id=current_user_id,
        quiz_id=quiz_id,
        score=card.score,
        temps_reponse=request.temps_reponse,
        reponses=[a.model_dump() for a in request.answers],
        evaluation_detaillee=[e.model_dump() for e in evaluations],
        feedback_card=card.model_dump(),
    )
    db.add(attempt)

    # --- Mise à jour des maîtrises ---
    feedback_service.update_mastery_from_evaluations(
        db=db,
        etudiant_id=current_user_id,
        evaluations=evaluations,
    )

    # --- Calibration du niveau global de l'etudiant (quiz diagnostique) ---
    # Quand c'est le quiz diagnostique d'onboarding (module="Diagnostic"),
    # on met a jour Etudiant.niveau_actuel selon le score moyen objectif :
    #   score >= 70 -> "Avancé"
    #   score >= 40 -> "Intermédiaire"
    #   score < 40  -> "Débutant"
    # C'est l'auto-calibration qui remplace le selecteur manuel sur la page
    # d'inscription (l'auto-evaluation est trop biaisee — Dunning-Kruger).
    if quiz.module == "Diagnostic":
        student = (
            db.query(Etudiant).filter(Etudiant.id == current_user_id).first()
        )
        if student is not None:
            if card.score >= 70:
                student.niveau_actuel = "advanced"
            elif card.score >= 40:
                student.niveau_actuel = "intermediate"
            else:
                student.niveau_actuel = "beginner"
            logger.info(
                "Niveau etudiant %d calibre par diagnostic : %s (score %.1f)",
                current_user_id,
                student.niveau_actuel,
                card.score,
            )

    db.commit()
    db.refresh(attempt)

    logger.info(
        "Quiz %d soumis par étudiant %d : score=%.1f, %d/%d",
        quiz_id,
        current_user_id,
        card.score,
        card.n_correct,
        card.n_total,
    )

    return QuizSubmitResponse(
        attempt_id=attempt.id,
        quiz_id=quiz_id,
        score=card.score,
        feedback_card=card,
        evaluations=evaluations,
        date_tentative=attempt.date_tentative,
    )


# ============================================================
# ENDPOINT 4 : Historique des tentatives
# ============================================================
@router.get(
    "/attempts/list",
    response_model=list[AttemptSummary],
    summary="Lister mes tentatives de quiz IA",
)
async def list_attempts(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    rows = (
        db.query(QuizResult, Quiz)
        .join(Quiz, QuizResult.quiz_id == Quiz.id)
        .filter(QuizResult.etudiant_id == current_user_id)
        .order_by(QuizResult.date_tentative.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    summaries: list[AttemptSummary] = []
    for attempt, quiz in rows:
        grade = None
        if attempt.feedback_card and isinstance(attempt.feedback_card, dict):
            grade = attempt.feedback_card.get("grade_label")
        summaries.append(
            AttemptSummary(
                id=attempt.id,
                quiz_id=quiz.id,
                quiz_titre=quiz.titre,
                score=attempt.score,
                temps_reponse=attempt.temps_reponse,
                date_tentative=attempt.date_tentative,
                grade_label=grade,
            )
        )
    return summaries


# ============================================================
# ENDPOINT 5 : Détail d'une tentative
# ============================================================
@router.get(
    "/attempts/{attempt_id}",
    response_model=QuizSubmitResponse,
    summary="Détail complet d'une tentative (feedback + evaluations)",
)
async def get_attempt(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    attempt = db.query(QuizResult).filter(QuizResult.id == attempt_id).first()
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tentative {attempt_id} introuvable.",
        )
    if attempt.etudiant_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cette tentative ne vous appartient pas.",
        )

    fb_raw = attempt.feedback_card or {}
    # Reconstruire la FeedbackCard depuis le JSON stocké
    fb = FeedbackCard(**fb_raw) if fb_raw else FeedbackCard(
        score=attempt.score,
        n_correct=0,
        n_total=0,
        temps_reponse=attempt.temps_reponse,
        grade_label=feedback_service._grade_label(attempt.score, _user_language(db, current_user_id)),
        summary="Feedback non disponible pour cette tentative.",
    )

    evals = attempt.evaluation_detaillee or []
    evaluations = [QuestionEvaluation(**e) for e in evals] if evals else []

    return QuizSubmitResponse(
        attempt_id=attempt.id,
        quiz_id=attempt.quiz_id,
        score=attempt.score,
        feedback_card=fb,
        evaluations=evaluations,
        date_tentative=attempt.date_tentative,
    )
