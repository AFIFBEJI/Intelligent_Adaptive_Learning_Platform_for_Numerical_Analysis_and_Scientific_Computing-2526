"""Pydantic schemas pour les endpoints /study/*.

Conventions :
- Inputs : `*Request` (POST body).
- Outputs : `*Response` (200 / 201 body).
- `StudyItem` : item etudiant-facing, SANS le champ `correct` pour ne pas
  spoiler les reponses.
"""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

# ============================================================
# Enrollment
# ============================================================
class EnrollResponse(BaseModel):
    """Retour de POST /study/enroll."""
    participant_code: str = Field(..., description="Pseudonyme opaque P001-P999")
    test_version: Literal["A_then_B", "B_then_A"] = Field(
        ..., description="Ordre des versions pre/post (contre-balancing)",
    )
    pretest_version: Literal["A", "B"] = Field(
        ..., description="Version a passer en pre-test",
    )
    already_enrolled: bool = Field(
        False,
        description="True si l'etudiant est deja inscrit (idempotent)",
    )


# ============================================================
# Pretest / Posttest items (etudiant-facing)
# ============================================================
class StudyItem(BaseModel):
    """Item presente a l'etudiant (SANS la reponse correcte)."""
    id: str
    concept_id: str
    difficulty: Literal["easy", "medium", "hard"]
    points: int
    question_fr: str
    question_en: str
    options: list[str] | None = Field(
        None,
        description="None pour les questions ouvertes (calcul libre)",
    )


class TestStartResponse(BaseModel):
    """Retour de GET /study/pretest ou /study/posttest."""
    participant_code: str
    phase: Literal["pretest", "posttest"]
    version: Literal["A", "B"]
    items: list[StudyItem]
    started_at: datetime


# ============================================================
# Pretest / Posttest submission
# ============================================================
class TestSubmitRequest(BaseModel):
    """Body de POST /study/pretest et /study/posttest.

    `answers` : map {item_id: index (int pour QCM) ou string (calcul libre)}.
    """
    answers: dict[str, int | str] = Field(..., description="Reponses par item_id")
    duration_seconds: int = Field(
        ..., ge=0, le=3600,
        description="Temps total pour completer le test (0 a 60 min)",
    )


class TestSubmitResponse(BaseModel):
    """Retour de POST /study/pretest et /study/posttest.

    `per_item` : pour debug (mode pilote) ; en prod on peut le retirer si
    on veut blinder contre le retro-engineering des items entre pre et post.
    """
    participant_code: str
    phase: Literal["pretest", "posttest"]
    score: float = Field(..., ge=0, le=100)
    raw: int
    max: int
    per_item: list[dict]
    group_assigned: str | None = Field(
        None,
        description="Groupe assigne (apres pretest uniquement) : adaptive / control",
    )


# ============================================================
# SUS questionnaire post-etude
# ============================================================
class SUSSubmitRequest(BaseModel):
    """Body de POST /study/sus.

    `likert` : 6 items Likert 1-5 (cf. paper). Indices 0-5.
    `open_responses` : 3 questions ouvertes textuelles.
    """
    likert: list[int] = Field(
        ..., min_length=6, max_length=6,
        description="6 valeurs Likert 1-5",
    )
    open_responses: dict[str, str] = Field(
        default_factory=dict,
        description="Map {key: text} pour les questions ouvertes",
    )


class SUSSubmitResponse(BaseModel):
    participant_code: str
    sus_score: float = Field(..., ge=6, le=30, description="Score brut 6-30")
    sus_score_normalized: float = Field(
        ..., ge=0, le=100,
        description="Score normalise 0-100 (SUS-adapted)",
    )


# ============================================================
# Admin / monitoring
# ============================================================
class ParticipantSummary(BaseModel):
    """Vue admin pour /study/admin/participants."""
    participant_code: str
    group_assigned: str | None
    pre_score: float | None
    post_score: float | None
    sus_score: float | None
    learning_gain: float | None = Field(
        None,
        description="post - pre (None tant qu'un des deux est manquant)",
    )
    normalized_gain: float | None = Field(
        None,
        description="Hake's normalized gain : (post-pre)/(100-pre)",
    )
    enrolled_at: datetime
    pre_test_done_at: datetime | None
    post_test_done_at: datetime | None
    withdrawn: bool


class StudyOverview(BaseModel):
    """Vue admin agregee pour /study/admin/overview."""
    total_enrolled: int
    total_completed_pretest: int
    total_completed_posttest: int
    total_completed_sus: int
    total_withdrawn: int
    by_group: dict[str, int] = Field(
        default_factory=dict,
        description="Repartition par groupe (adaptive/control/None)",
    )
