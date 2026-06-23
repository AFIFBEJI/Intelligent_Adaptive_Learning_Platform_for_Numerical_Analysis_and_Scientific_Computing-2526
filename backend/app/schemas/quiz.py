from datetime import datetime
from typing import Any

from pydantic import BaseModel


class QuestionSchema(BaseModel):
    """Schema for a quiz question."""
    id: int
    question: str
    type: str  # multiple_choice, short_answer, true_false
    options: list[str] | None = None
    correct_answer: str | None = None
    points: int = 1


class QuizCreate(BaseModel):
    """Schema for creating a new quiz."""
    titre: str
    module: str
    difficulte: str  # easy, medium, hard
    questions: list[dict[str, Any]]


class QuizResponse(BaseModel):
    """Schema for returning quiz information."""
    id: int
    titre: str
    module: str
    difficulte: str
    questions: list[dict[str, Any]]
    date_creation: datetime

    class Config:
        from_attributes = True


class QuizResultCreate(BaseModel):
    """Schema for submitting quiz results."""
    score: float
    temps_reponse: int
    reponses: Any | None = None


class QuizResultResponse(BaseModel):
    """Schema for returning quiz result information."""
    id: int
    etudiant_id: int
    quiz_id: int
    score: float
    temps_reponse: int
    reponses: Any | None = None
    date_tentative: datetime

    class Config:
        from_attributes = True
