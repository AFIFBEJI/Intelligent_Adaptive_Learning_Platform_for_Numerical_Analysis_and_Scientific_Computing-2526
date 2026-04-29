# ============================================================
# Tests unitaires — Quiz IA dynamique + service feedback
# ============================================================
# Ces tests utilisent des mocks pour ne pas appeler Gemini/Ollama.
# Ils valident la logique métier : extraction JSON, normalisation,
# seuils de difficulté, grade labels, évaluation MCQ.
# ============================================================
from __future__ import annotations

import pytest

from app.schemas.quiz_dynamic import GeneratedQuestion, StudentAnswer
from app.services.feedback_service import FeedbackService
from app.services.quiz_localization import localize_bank_question, true_false_labels
from app.services.quiz_service import QuizService


# ============================================================
# QuizService helpers
# ============================================================
class TestQuizServiceHelpers:
    def test_make_seed_unique(self):
        s1 = QuizService._make_seed()
        s2 = QuizService._make_seed()
        assert s1 != s2
        assert len(s1) == 12
        assert len(s2) == 12

    def test_difficulty_from_mastery(self):
        assert QuizService._difficulty_for_mastery(0) == "facile"
        assert QuizService._difficulty_for_mastery(29.9) == "facile"
        assert QuizService._difficulty_for_mastery(30) == "moyen"
        assert QuizService._difficulty_for_mastery(69.9) == "moyen"
        assert QuizService._difficulty_for_mastery(70) == "difficile"
        assert QuizService._difficulty_for_mastery(100) == "difficile"

    def test_difficulty_override(self):
        # override bypasses mastery
        assert QuizService._difficulty_for_mastery(10, "difficile") == "difficile"
        assert QuizService._difficulty_for_mastery(95, "facile") == "facile"

    def test_extract_json_plain(self):
        raw = '{"questions": [{"id": 1, "question": "test"}]}'
        parsed = QuizService._extract_json(raw)
        assert len(parsed["questions"]) == 1

    def test_extract_json_with_markdown_fences(self):
        raw = '```json\n{"questions": [{"id": 1}]}\n```'
        parsed = QuizService._extract_json(raw)
        assert parsed["questions"][0]["id"] == 1

    def test_extract_json_with_surrounding_text(self):
        raw = 'Voici le JSON :\n{"questions": [{"id": 1}]}\nFin.'
        parsed = QuizService._extract_json(raw)
        assert parsed["questions"][0]["id"] == 1

    def test_extract_json_tolerates_trailing_comma(self):
        raw = '{"questions": [{"id": 1,},]}'
        parsed = QuizService._extract_json(raw)
        assert parsed["questions"][0]["id"] == 1

    def test_extract_json_empty_fails(self):
        with pytest.raises(ValueError):
            QuizService._extract_json("pas de json ici")

    def test_difficulty_instruction_levels(self):
        easy = QuizService._difficulty_instruction("facile")
        hard = QuizService._difficulty_instruction("difficile")
        assert "rappel" in easy.lower()
        assert "piège" in hard.lower() or "ordre" in hard.lower()


# ============================================================
# FeedbackService helpers
# ============================================================
class TestFeedbackServiceHelpers:
    def test_normalize(self):
        assert FeedbackService._normalize("ABC") == "abc"
        assert FeedbackService._normalize("  Hello World  ") == "helloworld"
        assert FeedbackService._normalize("") == ""
        assert FeedbackService._normalize(None) == ""  # type: ignore[arg-type]

    def test_grade_label(self):
        fs = FeedbackService()
        assert fs._grade_label(95) == "Excellent"
        assert fs._grade_label(85) == "Very good"
        assert fs._grade_label(70) == "Good"
        assert fs._grade_label(50) == "Needs consolidation"
        assert fs._grade_label(20) == "Needs review"
        assert fs._grade_label(70, "fr") == "Bien"

    def test_eval_exact_match(self):
        fs = FeedbackService()
        assert fs._eval_exact("Option A", "option a") == (True, 1.0)
        assert fs._eval_exact("Vrai", "Vrai") == (True, 1.0)
        assert fs._eval_exact("Vrai", "True") == (True, 1.0)
        assert fs._eval_exact("False", "Faux") == (True, 1.0)
        assert fs._eval_exact("Faux", "Vrai") == (False, 0.0)
        assert fs._eval_exact("", "answer") == (False, 0.0)


class TestQuizLocalization:
    def test_true_false_labels_follow_language(self):
        assert true_false_labels("en") == ("True", "False")
        assert true_false_labels("fr") == ("Vrai", "Faux")

    def test_localize_bank_question_to_english(self):
        localized = localize_bank_question(
            {
                "question": "Quel est le degre du polynome $p(x)$ ?",
                "options": ["2", "3", "4", "5"],
                "correct_answer": "4",
                "explanation": "Le degre est la plus grande puissance.",
            },
            "en",
        )
        assert localized["language"] == "en"
        assert localized["question"].startswith("What is the degree")
        assert localized["correct_answer"] == "4"


# ============================================================
# Evaluation flow (sans LLM)
# ============================================================
class _FakeQuiz:
    """Minimal quiz stub pour les tests d'évaluation."""

    def __init__(self, questions: list[dict]):
        self.titre = "Test Quiz"
        self.questions = questions


@pytest.mark.asyncio
async def test_evaluate_answers_mcq_all_correct():
    """Toutes bonnes réponses → 100% de partial_credit."""
    fs = FeedbackService()
    quiz = _FakeQuiz(
        [
            {
                "id": 1,
                "type": "mcq",
                "question": "Q1",
                "correct_answer": "A",
                "options": ["A", "B", "C", "D"],
                "explanation": "parce que A",
            },
            {
                "id": 2,
                "type": "true_false",
                "question": "Q2",
                "correct_answer": "Vrai",
                "explanation": "vrai",
            },
        ]
    )
    answers = [
        StudentAnswer(question_id=1, answer="A"),
        StudentAnswer(question_id=2, answer="Vrai"),
    ]
    evals = await fs.evaluate_answers(quiz, answers)
    assert len(evals) == 2
    assert all(e.is_correct for e in evals)
    assert all(e.partial_credit == 1.0 for e in evals)


@pytest.mark.asyncio
async def test_evaluate_answers_mcq_mixed():
    """1 bonne, 1 mauvaise → is_correct 50/50, partial_credit moyen."""
    fs = FeedbackService()
    quiz = _FakeQuiz(
        [
            {"id": 1, "type": "mcq", "question": "Q1", "correct_answer": "A"},
            {"id": 2, "type": "mcq", "question": "Q2", "correct_answer": "B"},
        ]
    )
    answers = [
        StudentAnswer(question_id=1, answer="A"),  # bon
        StudentAnswer(question_id=2, answer="C"),  # mauvais
    ]
    evals = await fs.evaluate_answers(quiz, answers)
    assert evals[0].is_correct is True
    assert evals[1].is_correct is False
    assert "bonne réponse était" in evals[1].explanation.lower() or \
           "la bonne réponse" in evals[1].explanation.lower()


@pytest.mark.asyncio
async def test_evaluate_answers_missing_answer():
    """Question non répondue → faux."""
    fs = FeedbackService()
    quiz = _FakeQuiz(
        [{"id": 1, "type": "mcq", "question": "Q1", "correct_answer": "A"}]
    )
    answers: list[StudentAnswer] = []  # aucune réponse fournie
    evals = await fs.evaluate_answers(quiz, answers)
    assert len(evals) == 1
    assert evals[0].is_correct is False
    assert evals[0].student_answer == ""


# ============================================================
# Schema validation
# ============================================================
class TestGeneratedQuestionSchema:
    def test_valid_mcq(self):
        q = GeneratedQuestion(
            id=1,
            type="mcq",
            question="Combien font 2+2 ?",
            options=["3", "4", "5", "6"],
            correct_answer="4",
        )
        assert q.id == 1
        assert q.difficulty == "moyen"  # valeur par défaut

    def test_invalid_type_rejected(self):
        with pytest.raises(Exception):
            GeneratedQuestion(
                id=1, type="quiz_bizarre", question="?", correct_answer="x"  # type: ignore[arg-type]
            )

    def test_invalid_difficulty_rejected(self):
        with pytest.raises(Exception):
            GeneratedQuestion(
                id=1,
                type="mcq",
                question="?",
                correct_answer="x",
                difficulty="extreme",  # type: ignore[arg-type]
            )
