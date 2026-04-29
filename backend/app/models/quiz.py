from datetime import UTC, datetime

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Quiz(Base):
    """
    Quiz model storing quiz information and questions.

    Supports both STATIC quizzes (seeded in DB, reused for all students)
    and DYNAMIC quizzes (generated on-demand by the LLM for a specific
    student and concept). The `source` column distinguishes the two.
    """
    __tablename__ = "quiz"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(255), nullable=False)
    module = Column(String(255), nullable=False, index=True)
    difficulte = Column(String(50), nullable=False)  # facile, moyen, difficile
    questions = Column(JSON, nullable=False)  # Array of question objects
    date_creation = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    # --- Dynamic-quiz columns (NEW for Phase 2 Étape 1) ---
    # source = "static" (seeded)  ou  "generated" (produit par le LLM)
    source = Column(String(20), nullable=False, default="static", index=True)
    # Si source="generated" : étudiant qui a demandé la génération.
    # Nullable car les quiz statiques n'ont pas de propriétaire.
    etudiant_generateur_id = Column(
        Integer, ForeignKey("etudiants.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )
    # Concept Neo4j ciblé par le quiz (ex: "concept_lagrange")
    concept_neo4j_id = Column(String(255), nullable=True, index=True)
    # Graine utilisée pour la diversité (timestamp ou hash)
    seed = Column(String(64), nullable=True)

    # Relationships
    resultats = relationship("QuizResult", back_populates="quiz", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Quiz(id={self.id}, titre={self.titre}, module={self.module}, source={self.source})>"


class QuizResult(Base):
    """
    Quiz result model storing student quiz attempts.
    """
    __tablename__ = "quiz_resultats"

    id = Column(Integer, primary_key=True, index=True)
    etudiant_id = Column(Integer, ForeignKey("etudiants.id", ondelete="CASCADE"), nullable=False, index=True)
    quiz_id = Column(Integer, ForeignKey("quiz.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Float, nullable=False)  # 0-100
    temps_reponse = Column(Integer, nullable=False)  # in seconds
    reponses = Column(JSON, nullable=True)  # Detailed student answers
    date_tentative = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False, index=True)

    # --- Dynamic-feedback columns (NEW for Phase 2 Étape 1) ---
    # Évaluation détaillée par question : [{question_id, is_correct, ...}]
    evaluation_detaillee = Column(JSON, nullable=True)
    # Carte de feedback générée par le LLM après soumission
    feedback_card = Column(JSON, nullable=True)

    # Relationships
    quiz = relationship("Quiz", back_populates="resultats")

    def __repr__(self):
        return f"<QuizResult(id={self.id}, etudiant_id={self.etudiant_id}, quiz_id={self.quiz_id}, score={self.score})>"
