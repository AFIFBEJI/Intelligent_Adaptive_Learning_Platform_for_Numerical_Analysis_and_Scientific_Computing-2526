"""Modeles SQLAlchemy pour la Phase 4 / user study.

Une `StudyParticipant` est cree au moment de l'enrollment d'un etudiant
dans l'etude. Une ligne par etudiant + par etude (s'il y a plusieurs vagues
on incrementera `study_wave`). Les pre/post scores sont stockes denormalises
ici pour permettre les analyses pandas/scipy sans avoir a re-joindre toutes
les tables a chaque export.

Une `StudyEvent` est une trace d'usage : connexion, quiz tente, question
au tuteur, etc. C'est la matiere brute pour les graphes d'engagement et
pour `time_to_mastery`. Append-only, on ne update jamais.

Les deux tables sont independantes de `Etudiant` (FK vers etudiants.id)
pour ne pas polluer la table principale avec des champs specifiques a
l'experimentation.
"""
from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class StudyParticipant(Base):
    """Une ligne par etudiant inscrit a l'etude utilisateur.

    Created at: POST /study/enroll
    Updated at:
      - POST /study/pretest  -> pre_score, pre_test_started_at, pre_test_done_at
      - POST /study/posttest -> post_score, post_test_done_at
      - POST /study/sus      -> sus_score
    """
    __tablename__ = "study_participants"

    id = Column(Integer, primary_key=True, index=True)
    etudiant_id = Column(
        Integer, ForeignKey("etudiants.id", ondelete="CASCADE"),
        nullable=False, unique=True, index=True,
    )
    # Pseudonyme opaque pour les exports (P001, P002, ...). Genere a
    # l'enrollment, jamais modifie. C'est cet identifiant qui apparait
    # dans le paper.
    participant_code = Column(String(16), nullable=False, unique=True, index=True)

    # Phase 4 - vague de l'etude. 1 par defaut. Permet de lancer une 2e
    # vague plus tard avec des protocoles ajustes sans melanger les data.
    study_wave = Column(Integer, nullable=False, default=1)

    # Allocation aleatoire stratifiee : "adaptive" ou "control". Determinee
    # apres le pre-test par l'algo de stratification (cf. routers/study.py).
    group_assigned = Column(String(16), nullable=True, index=True)

    # Contre-balancing pre/post : "A_then_B" ou "B_then_A".
    test_version = Column(String(16), nullable=False)

    # Scores normalises 0-100. NULL tant que le test n'est pas passe.
    pre_score = Column(Float, nullable=True)
    post_score = Column(Float, nullable=True)
    # Score System Usability Scale adapte (6-30).
    sus_score = Column(Float, nullable=True)

    # Reponses brutes (pour reanalyses) en JSON.
    pre_answers = Column(JSON, nullable=True)
    post_answers = Column(JSON, nullable=True)
    sus_answers = Column(JSON, nullable=True)
    # Reponses libres post-test : "qu'est-ce qui t'a aide ?", etc.
    open_feedback = Column(JSON, nullable=True)

    # Timestamps de chaque etape - utile pour calculer time_to_mastery
    # et reperer les drop-outs.
    enrolled_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    pre_test_started_at = Column(DateTime, nullable=True)
    pre_test_done_at = Column(DateTime, nullable=True)
    intervention_started_at = Column(DateTime, nullable=True)
    post_test_done_at = Column(DateTime, nullable=True)
    withdrawn_at = Column(DateTime, nullable=True)
    withdrawal_reason = Column(String(255), nullable=True)

    # Relations
    events = relationship(
        "StudyEvent",
        back_populates="participant",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<StudyParticipant(code={self.participant_code}, "
            f"group={self.group_assigned}, pre={self.pre_score}, "
            f"post={self.post_score})>"
        )


class StudyEvent(Base):
    """Trace append-only des actions des participants.

    Beaucoup d'evenements sont DEJA derivables de QuizResult et de
    TutorMessage existants. Cette table sert pour les evenements **qui
    n'existent pas ailleurs** (login, session_end, intervention_phase_start,
    etc.) et pour avoir un point unique d'agregation au moment de
    l'export CSV.
    """
    __tablename__ = "study_events"

    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(
        Integer, ForeignKey("study_participants.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    # Type d'event court, indexable.
    # Valeurs attendues : enroll, pretest_start, pretest_submit,
    # intervention_start, posttest_submit, sus_submit, withdraw,
    # session_start, session_end, quiz_attempt, tutor_question.
    event_type = Column(String(32), nullable=False, index=True)
    # Charge utile JSON libre (score, concept_id, duration_s, etc.).
    payload = Column(JSON, nullable=True)
    timestamp = Column(
        DateTime, default=lambda: datetime.now(UTC),
        nullable=False, index=True,
    )

    participant = relationship("StudyParticipant", back_populates="events")

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<StudyEvent(type={self.event_type}, "
            f"participant_id={self.participant_id}, ts={self.timestamp})>"
        )
