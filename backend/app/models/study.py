"""SQLAlchemy models for Phase 4 / user study.

A `StudyParticipant` is created at the moment a student enrolls in the
study. One row per student + per study (if there are several waves we will
increment `study_wave`). The pre/post scores are stored denormalized here
to allow pandas/scipy analyses without having to re-join all the tables on
every export.

A `StudyEvent` is a usage trace : login, quiz attempted, question to the
tutor, etc. This is the raw material for engagement graphs and for
`time_to_mastery`. Append-only, we never update it.

The two tables are independent of `Etudiant` (FK to etudiants.id) so as
not to pollute the main table with fields specific to experimentation.
"""
from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class StudyParticipant(Base):
    """One row per student enrolled in the user study.

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
    # Opaque pseudonym for the exports (P001, P002, ...). Generated at
    # enrollment, never modified. This is the identifier that appears in
    # the paper.
    participant_code = Column(String(16), nullable=False, unique=True, index=True)

    # Phase 4 - study wave. 1 by default. Allows launching a 2nd wave
    # later with adjusted protocols without mixing the data.
    study_wave = Column(Integer, nullable=False, default=1)

    # Stratified random allocation : "adaptive" or "control". Determined
    # after the pre-test by the stratification algorithm (cf. routers/study.py).
    group_assigned = Column(String(16), nullable=True, index=True)

    # Pre/post counter-balancing : "A_then_B" or "B_then_A".
    test_version = Column(String(16), nullable=False)

    # Normalized scores 0-100. NULL as long as the test has not been taken.
    pre_score = Column(Float, nullable=True)
    post_score = Column(Float, nullable=True)
    # Adapted System Usability Scale score (6-30).
    sus_score = Column(Float, nullable=True)

    # Raw answers (for reanalyses) in JSON.
    pre_answers = Column(JSON, nullable=True)
    post_answers = Column(JSON, nullable=True)
    sus_answers = Column(JSON, nullable=True)
    # Free post-test answers : "what helped you ?", etc.
    open_feedback = Column(JSON, nullable=True)

    # Timestamps of each step - useful to compute time_to_mastery and
    # spot the drop-outs.
    enrolled_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    pre_test_started_at = Column(DateTime, nullable=True)
    pre_test_done_at = Column(DateTime, nullable=True)
    intervention_started_at = Column(DateTime, nullable=True)
    post_test_done_at = Column(DateTime, nullable=True)
    withdrawn_at = Column(DateTime, nullable=True)
    withdrawal_reason = Column(String(255), nullable=True)

    # Relationships
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
    """Append-only trace of participant actions.

    Many events are ALREADY derivable from the existing QuizResult and
    TutorMessage. This table is used for the events **that do not exist
    elsewhere** (login, session_end, intervention_phase_start, etc.) and
    to have a single aggregation point at the moment of the CSV export.
    """
    __tablename__ = "study_events"

    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(
        Integer, ForeignKey("study_participants.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    # Short, indexable event type.
    # Expected values : enroll, pretest_start, pretest_submit,
    # intervention_start, posttest_submit, sus_submit, withdraw,
    # session_start, session_end, quiz_attempt, tutor_question.
    event_type = Column(String(32), nullable=False, index=True)
    # Free JSON payload (score, concept_id, duration_s, etc.).
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
