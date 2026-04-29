# ============================================================
# Schemas Pydantic — Quiz Dynamique + Carte de Feedback
# ============================================================
# Ce fichier définit la "forme" des données échangées entre le
# frontend et le backend pour le module QUIZ DYNAMIQUE.
#
# Différence avec l'ancien quiz.py (statique) :
# - Ici les questions sont GÉNÉRÉES par l'IA à chaque appel
# - La réponse de soumission contient une CARTE DE FEEDBACK
#   détaillée qui explique les erreurs de l'étudiant
# ============================================================
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# ============================================================
# 1. QUESTION GÉNÉRÉE PAR L'IA
# ============================================================
class GeneratedQuestion(BaseModel):
    """
    Une question produite par le LLM.

    Deux formats supportés :
    - QCM : 4 options, une seule correcte (type="mcq")
    - Ouverte : réponse libre, évaluée par le LLM (type="open")
    """

    id: int = Field(..., description="Identifiant séquentiel (1..N)")
    type: Literal["mcq", "open", "true_false"] = Field(
        "mcq", description="Format de la question"
    )
    question: str = Field(..., description="Énoncé de la question (LaTeX autorisé)")
    options: list[str] | None = Field(
        None, description="Options pour QCM (4 en général)"
    )
    # correct_answer et explanation sont CACHÉS au frontend pendant le quiz
    correct_answer: str | None = Field(
        None, description="Réponse correcte (uniquement dans le backend)"
    )
    explanation: str | None = Field(
        None, description="Explication pédagogique (après soumission)"
    )
    concept_id: str | None = Field(
        None, description="ID Neo4j du concept ciblé"
    )
    difficulty: Literal["facile", "moyen", "difficile"] = "moyen"
    language: Literal["en", "fr"] = "en"


class StudentFacingQuestion(BaseModel):
    """Question envoyée au frontend, SANS la réponse correcte."""

    id: int
    type: Literal["mcq", "open", "true_false"]
    question: str
    options: list[str] | None = None
    difficulty: Literal["facile", "moyen", "difficile"] = "moyen"
    language: Literal["en", "fr"] = "en"


# ============================================================
# 2. REQUÊTES ENTRANTES
# ============================================================
class QuizGenerateRequest(BaseModel):
    """POST /quiz-ai/generate — paramètres de génération."""

    concept_id: str | None = Field(
        None,
        description="ID Neo4j du concept ciblé (si omis, on devine depuis topic)",
    )
    topic: str | None = Field(
        None,
        description="Sujet en langue naturelle si concept_id non fourni",
    )
    n_questions: int = Field(
        5, ge=3, le=10, description="Nombre de questions (3 à 10)"
    )
    difficulty: Literal["auto", "facile", "moyen", "difficile"] = Field(
        "auto",
        description="'auto' = déduit depuis la maîtrise de l'étudiant",
    )
    question_types: list[Literal["mcq", "open", "true_false"]] = Field(
        default_factory=lambda: ["mcq", "true_false"],
        description="Types de questions à mélanger",
    )
    use_llm: bool = Field(
        False,
        description="Si True, genere via Gemma (lent ~30s, variantes experimentales). Si False (defaut), pioche dans la banque hand-curated (instantane).",
    )
    language: Literal["en", "fr"] | None = None


class StudentAnswer(BaseModel):
    """Une réponse étudiant pour une question."""

    question_id: int
    answer: str = Field(..., description="Réponse brute (texte ou option cliquée)")


class QuizSubmitRequest(BaseModel):
    """POST /quiz-ai/{quiz_id}/submit — soumission d'un quiz."""

    answers: list[StudentAnswer]
    language: Literal["en", "fr"] | None = None
    temps_reponse: int = Field(
        ..., ge=0, description="Durée totale en secondes"
    )


# ============================================================
# 3. RÉPONSES SORTANTES
# ============================================================
class QuizGenerateResponse(BaseModel):
    """Quiz frais généré — envoyé au frontend pour affichage."""

    quiz_id: int
    titre: str
    module: str
    difficulte: str
    concept_id: str | None
    concept_name: str | None
    questions: list[StudentFacingQuestion]
    n_questions: int
    language: Literal["en", "fr"] = "en"
    date_creation: datetime

    model_config = {"from_attributes": True}


class QuestionEvaluation(BaseModel):
    """Évaluation détaillée d'une question après soumission."""

    question_id: int
    question: str
    student_answer: str
    correct_answer: str
    is_correct: bool
    partial_credit: float = Field(0.0, ge=0.0, le=1.0)
    explanation: str = ""
    concept_id: str | None = None


class FeedbackCard(BaseModel):
    """
    La carte de feedback post-quiz.

    C'est le livrable pédagogique le plus important : elle explique
    À L'ÉTUDIANT pourquoi il s'est trompé, sur quels concepts il a
    des lacunes, et quoi réviser ensuite.
    """

    score: float = Field(..., ge=0.0, le=100.0, description="Score sur 100")
    n_correct: int
    n_total: int
    temps_reponse: int
    grade_label: str  # "Excellent", "Bien", "À revoir", etc.
    summary: str  # Résumé en 2-3 phrases
    strengths: list[str] = Field(
        default_factory=list, description="Concepts bien maîtrisés"
    )
    weaknesses: list[str] = Field(
        default_factory=list, description="Concepts à revoir"
    )
    mistakes_detail: list[str] = Field(
        default_factory=list,
        description="Explication pédagogique par erreur",
    )
    next_steps: list[str] = Field(
        default_factory=list, description="Actions recommandées"
    )
    recommended_concepts: list[str] = Field(
        default_factory=list, description="IDs Neo4j à réviser"
    )


class QuizSubmitResponse(BaseModel):
    """Réponse après soumission : carte feedback + détail par question."""

    attempt_id: int
    quiz_id: int
    score: float
    feedback_card: FeedbackCard
    evaluations: list[QuestionEvaluation]
    date_tentative: datetime


class AttemptSummary(BaseModel):
    """Ligne d'historique (liste des tentatives)."""

    id: int
    quiz_id: int
    quiz_titre: str
    score: float
    temps_reponse: int
    date_tentative: datetime
    grade_label: str | None = None

    model_config = {"from_attributes": True}
