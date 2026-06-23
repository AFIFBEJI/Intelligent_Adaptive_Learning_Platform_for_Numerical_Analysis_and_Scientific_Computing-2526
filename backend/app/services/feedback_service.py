# ============================================================
# Feedback Service — Post-quiz feedback card
# ============================================================
# This service takes a student's answers to a quiz and produces
# a complete pedagogical FEEDBACK CARD:
#   - Global score and label ("Excellent", "Needs review"...)
#   - List of correct answers (strengths)
#   - List of mistakes with a detailed EXPLANATION by the LLM
#   - Concepts to review (based on the mistakes)
#   - Concrete recommendations ("retake the quiz", "review X first")
#
# Architecture:
# 1. DETERMINISTIC evaluation (string matching) for the MCQ/TF
# 2. LLM evaluation for the open questions
# 3. Aggregation -> FeedbackCard
# 4. A SECOND LLM call to generate the detailed explanations
#    of the mistakes (if more than 1 mistake)
# ============================================================
from __future__ import annotations

import json
import logging
import re
from typing import Any

from langchain_core.messages import HumanMessage
from sqlalchemy.orm import Session

from app.models.quiz import Quiz
from app.schemas.quiz_dynamic import (
    FeedbackCard,
    QuestionEvaluation,
    StudentAnswer,
)
from app.services.llm_service import llm_service
from app.services.quiz_localization import normalize_quiz_language

logger = logging.getLogger(__name__)


# ============================================================
# Prompt for evaluating an open-ended answer
# ============================================================
OPEN_EVAL_PROMPT = """Tu es un correcteur d'examen en Analyse Numérique.

QUESTION : {question}
RÉPONSE ATTENDUE : {correct_answer}
RÉPONSE DE L'ÉTUDIANT : {student_answer}

TA TÂCHE : évaluer la réponse de l'étudiant et retourner UNIQUEMENT \
ce JSON (sans balises markdown) :

{{
  "is_correct": true/false,
  "partial_credit": 0.0 à 1.0,
  "explanation": "Courte explication de l'évaluation (1-2 phrases)"
}}

Règles :
- is_correct=true si la réponse est équivalente à la bonne (à la notation près)
- partial_credit=1.0 si parfait, 0.5 si partiellement correct, 0 si faux
- Tolère les différences de notation (ex: 3.14 vs π, x^2 vs x**2)
- Sois strict sur les valeurs numériques (±1% tolérance)
"""


# ============================================================
# Prompt for the global feedback card
# ============================================================
FEEDBACK_CARD_PROMPT = """Tu es un coach pédagogique bienveillant en \
Analyse Numérique. Un étudiant vient de terminer un quiz.

CONCEPT DU QUIZ : {concept_name}
SCORE : {score:.0f}/100 ({n_correct}/{n_total} questions correctes)
TEMPS : {temps_reponse} secondes

DÉTAIL DES ERREURS :
{mistakes_block}

BONNES RÉPONSES :
{strengths_block}

TA TÂCHE : produire une carte de rétroaction au format JSON (sans \
balises markdown, sans texte avant/après) avec cette structure exacte :

{{
  "summary": "Résumé global en 2-3 phrases, ton encourageant",
  "strengths": ["point fort 1", "point fort 2"],
  "weaknesses": ["lacune 1", "lacune 2"],
  "mistakes_detail": [
    "Erreur Q2 : tu as répondu X mais la bonne était Y parce que ...",
    "Erreur Q4 : tu as confondu A et B, la différence est que ..."
  ],
  "next_steps": [
    "Révise le concept X avant de refaire un quiz",
    "Entraîne-toi sur un exercice sur Y"
  ]
}}

Règles STRICTES (à respecter à la lettre) :
- Écris en FRANÇAIS
- Sois HONNÊTE — ne fabrique pas de qualités que l'étudiant n'a pas démontrées
- IMPORTANT : si score == 0/100, NE DIS PAS "tu as montré une certaine familiarité"
  ou "tu connais déjà certains concepts" — c'est FAUX et démoralisant car contradictoire.
  Dis plutôt : "Tu démarres de zéro sur ces concepts, c'est un point de départ honnête,
  pas un échec. Le parcours adaptatif est conçu exactement pour ça."
- Si score < 30 : ton encourageant MAIS factuel. Pas de fausse flatterie.
  Insiste sur les prérequis à acquérir avant d'aller plus loin.
- Si score 30-60 : ton de coach honnête. Identifie clairement les lacunes.
- Si score 60-80 : ton positif. Liste les forces réelles + 1-2 points à consolider.
- Si score >= 80 : célèbre, laisse weaknesses vide.
- Utilise LaTeX pour les formules : $...$
- mistakes_detail doit être PÉDAGOGIQUE : explique le POURQUOI de l'erreur
- next_steps doit proposer 2-4 actions CONCRÈTES adaptées au score réel
"""


# ============================================================
# Service
# ============================================================
class FeedbackService:
    """Evaluates the answers and generates the post-quiz feedback card."""

    # ------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------
    @staticmethod
    def _normalize(value: str) -> str:
        """
        Normalize for MCQ/TF comparison:
        - lowercase
        - without spaces or punctuation
        - without accents (e/e, a/a, etc.)
        So "Méthode de Chebyshev" and "methode de chebyshev" match.
        """
        import unicodedata
        s = (value or "").strip().lower()
        # Decompose the accents then remove the diacritical marks
        s = unicodedata.normalize("NFD", s)
        s = "".join(c for c in s if unicodedata.category(c) != "Mn")
        # Remove spaces and common punctuation
        for ch in " \t\n.,;:!?'\"-()[]{}":
            s = s.replace(ch, "")
        return s

    @staticmethod
    def _extract_json(raw: str) -> dict[str, Any]:
        """Extract the first JSON object (tolerates noise + fences)."""
        cleaned = re.sub(
            r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.MULTILINE
        ).strip()
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("Aucun JSON trouvé")
        blob = cleaned[start : end + 1]
        try:
            return json.loads(blob)
        except json.JSONDecodeError:
            blob = re.sub(r",(\s*[}\]])", r"\1", blob)
            return json.loads(blob)

    @staticmethod
    def _grade_label(score: float, language: str = "en") -> str:
        language = normalize_quiz_language(language)
        if language == "fr":
            if score >= 90:
                return "Excellent"
            if score >= 75:
                return "Très bien"
            if score >= 60:
                return "Bien"
            if score >= 40:
                return "Passable - à consolider"
            return "À revoir"

        if score >= 90:
            return "Excellent"
        if score >= 75:
            return "Very good"
        if score >= 60:
            return "Good"
        if score >= 40:
            return "Needs consolidation"
        return "Needs review"

    # ------------------------------------------------------------
    # Deterministic evaluation of a question
    # ------------------------------------------------------------
    def _eval_exact(
        self, student: str, correct: str, options: list[str] | None = None
    ) -> tuple[bool, float]:
        """
        MCQ/TF match with LLM tolerance:
        - accent + case + punctuation normalization
        - if correct_answer is a letter A-D, we map it onto options[index]
          (the LLM oscillates between letter and text despite the instructions)
        - if options are provided and correct is text that matches an option, we
          also accept the letter A/B/C/D that the student might have sent
        """
        s_norm = self._normalize(student)
        c_norm = self._normalize(correct)
        truth_aliases = {
            "true": "true",
            "vrai": "true",
            "false": "false",
            "faux": "false",
        }
        if truth_aliases.get(s_norm) and truth_aliases.get(s_norm) == truth_aliases.get(c_norm):
            return True, 1.0
        if s_norm == c_norm:
            return True, 1.0

        # Case 1: correct = letter (e.g. "A" or "C"), student = text of an option
        # We check whether correct.upper() is A/B/C/D and take the matching option
        if options and correct.strip() and len(correct.strip()) == 1:
            letter = correct.strip().upper()
            if letter in ("A", "B", "C", "D"):
                idx = ord(letter) - ord("A")
                if 0 <= idx < len(options):
                    if s_norm == self._normalize(options[idx]):
                        return True, 1.0

        # Case 2: student = letter, correct = text
        if options and student.strip() and len(student.strip()) == 1:
            letter = student.strip().upper()
            if letter in ("A", "B", "C", "D"):
                idx = ord(letter) - ord("A")
                if 0 <= idx < len(options):
                    if c_norm == self._normalize(options[idx]):
                        return True, 1.0

        return False, 0.0

    # ------------------------------------------------------------
    # Deterministic evaluation for NUMERIC questions (no AI)
    # ------------------------------------------------------------
    @staticmethod
    def _parse_number(text: str) -> float | None:
        """Parse a typed number. Accepts a decimal comma, surrounding spaces,
        and a simple fraction 'a/b'. Returns None if it is not a number."""
        if text is None:
            return None
        s = str(text).strip().replace(",", ".").replace(" ", "")
        if not s:
            return None
        try:
            return float(s)
        except ValueError:
            pass
        if "/" in s:  # simple fraction like "8/3"
            try:
                num, den = s.split("/", 1)
                return float(num) / float(den)
            except (ValueError, ZeroDivisionError):
                return None
        return None

    def _eval_numeric(self, student: str, correct: str, tolerance: float) -> tuple[bool, float]:
        """Grade a numeric answer WITHOUT any AI.

        The student typed a number; we accept it if it lands within `tolerance`
        of the expected value (or within a 1% relative gap for large values).
        100% deterministic and reliable.
        """
        s = self._parse_number(student)
        c = self._parse_number(correct)
        if s is None or c is None:
            return False, 0.0
        tol = max(abs(tolerance), abs(c) * 0.01)
        ok = abs(s - c) <= tol
        return ok, (1.0 if ok else 0.0)

    # ------------------------------------------------------------
    # LLM evaluation for open questions
    # ------------------------------------------------------------
    async def _eval_open(
        self, question: str, correct: str, student: str
    ) -> tuple[bool, float, str]:
        """Ask the LLM (Ollama OR OpenAI) to judge an open-ended answer."""
        # If the LLM is unavailable (regardless of the provider) -> fallback exact match
        if llm_service.llm is None:
            is_c, pc = self._eval_exact(student, correct)
            return is_c, pc, f"(Evalue par comparaison exacte, {llm_service.provider} indisponible)"

        prompt_text = OPEN_EVAL_PROMPT.format(
            question=question,
            correct_answer=correct,
            student_answer=student or "(pas de reponse)",
        )
        messages = [HumanMessage(content=prompt_text)]

        try:
            # bind_json() forces valid JSON output regardless of the provider
            # (Ollama: format=json, OpenAI: response_format=json_object).
            llm_json = llm_service.bind_json()
            resp = await llm_json.ainvoke(messages)
            data = self._extract_json(resp.content)
            return (
                bool(data.get("is_correct", False)),
                float(data.get("partial_credit", 0.0)),
                str(data.get("explanation", "")),
            )
        except Exception as exc:
            logger.warning("Echec eval %s question ouverte : %s", llm_service.provider, exc)
            is_c, pc = self._eval_exact(student, correct)
            return is_c, pc, "(Fallback comparaison exacte)"

    # ------------------------------------------------------------
    # Evaluates all the questions of a submission
    # ------------------------------------------------------------
    async def evaluate_answers(
        self, quiz: Quiz, answers: list[StudentAnswer]
    ) -> list[QuestionEvaluation]:
        """Return the question-by-question evaluation."""
        # Build an index of the student answers
        ans_by_id = {a.question_id: a.answer for a in answers}

        evaluations: list[QuestionEvaluation] = []

        for q in quiz.questions:
            qid = q.get("id")
            qtype = q.get("type", "mcq")
            question_text = q.get("question", "")
            correct = str(q.get("correct_answer", ""))
            correct_display = correct
            explanation = q.get("explanation", "")
            student = str(ans_by_id.get(qid, ""))

            if qtype in ("mcq", "true_false"):
                opts = q.get("options") or None
                is_correct, pc = self._eval_exact(student, correct, opts)
                # Diagnostic log to understand possible mismatches
                logger.info(
                    "Q%s [%s] : student='%s' vs correct='%s' (options=%s) -> is_correct=%s",
                    qid, qtype, student[:60], correct[:60],
                    [o[:30] for o in opts] if opts else None,
                    is_correct,
                )
                # For display, if correct is a letter A-D and we have the
                # options, we replace it with the full text so the student
                # understands what they should have answered.
                if opts and correct.strip() and len(correct.strip()) == 1:
                    letter = correct.strip().upper()
                    if letter in ("A", "B", "C", "D"):
                        idx = ord(letter) - ord("A")
                        if 0 <= idx < len(opts):
                            correct_display = opts[idx]
                # We no longer prefix with "The correct answer was": the UI already
                # displays correct_answer separately, duplicating it is redundant.
                exp = explanation or ""
            elif qtype == "numeric":
                # Deterministic numeric grading (no AI, instant, reliable).
                tol = float(q.get("tolerance", 0.05) or 0.05)
                is_correct, pc = self._eval_numeric(student, correct, tol)
                exp = explanation
            else:  # open
                is_correct, pc, llm_exp = await self._eval_open(
                    question_text, correct, student
                )
                exp = llm_exp or explanation

            evaluations.append(
                QuestionEvaluation(
                    question_id=qid,
                    question=question_text,
                    student_answer=student,
                    correct_answer=correct_display,
                    is_correct=is_correct,
                    partial_credit=pc,
                    explanation=exp,
                    concept_id=q.get("concept_id"),
                )
            )

        return evaluations

    # ------------------------------------------------------------
    # Build the global feedback card
    # ------------------------------------------------------------
    async def build_feedback_card(
        self,
        quiz: Quiz,
        evaluations: list[QuestionEvaluation],
        temps_reponse: int,
        language: str = "en",
    ) -> FeedbackCard:
        """
        Produce the final FeedbackCard.

        - For the diagnostic quiz (module="Diagnostic"): we do NOT call
          the LLM and we generate a templated feedback (instant, ~50ms).
          Rationale: the questions are fixed, the score alone determines
          the pedagogical message. No need for the LLM for that.
        - For the other adaptive quizzes: LLM call to personalize
          the summary, strengths, weaknesses, mistakes_detail, next_steps.
        """
        language = normalize_quiz_language(language)
        n_total = len(evaluations)
        n_correct = sum(1 for e in evaluations if e.is_correct)
        # Score weighted by partial_credit to accept partial answers
        points = sum(e.partial_credit for e in evaluations)
        score = (points / n_total * 100.0) if n_total else 0.0

        mistakes = [e for e in evaluations if not e.is_correct]
        wins = [e for e in evaluations if e.is_correct]

        # =========================================================
        # Templated feedback by default for ALL quizzes
        # =========================================================
        # We removed the LLM from the user flow to guarantee an instant
        # UX (< 100ms). The templating covers the 5 score brackets
        # and uses the real concept_id to point to the modules
        # to review. The LLM remains manually invocable via use_llm=True
        # but is no longer called by default in build_feedback_card.
        return self._build_diagnostic_feedback_templated(
            evaluations=evaluations,
            temps_reponse=temps_reponse,
            score=score,
            n_correct=n_correct,
            n_total=n_total,
            mistakes=mistakes,
            wins=wins,
            language=language,
        )

    # ------------------------------------------------------------
    # Updating the mastery level
    # ------------------------------------------------------------
    # DEPRECATED inline (05/12/2026): the logic is centralized in
    # services/mastery_service.py to avoid divergence with
    # routers/quiz.py:update_mastery. We keep the static method here
    # for compatibility with the quiz_dynamic.py router which calls
    # `feedback_service.update_mastery_from_evaluations(...)`. This is a
    # simple forward, not a duplication of logic.
    @staticmethod
    def update_mastery_from_evaluations(
        db: Session,
        etudiant_id: int,
        evaluations: list[QuestionEvaluation],
    ) -> None:
        """Update ConceptMastery for each concept touched by the quiz.

        Delegates to `mastery_service.update_mastery_from_evaluations` (single
        source). EWMA formula documented over there.
        """
        # Local import to avoid any potential cycle with other services.
        from app.services.mastery_service import (
            update_mastery_from_evaluations as _do_update,
        )
        _do_update(db, etudiant_id, evaluations)


    # ------------------------------------------------------------
    # Templated feedback for the diagnostic quiz (without LLM)
    # ------------------------------------------------------------
    def _build_diagnostic_feedback_templated(
        self,
        evaluations: list[QuestionEvaluation],
        temps_reponse: int,
        score: float,
        n_correct: int,
        n_total: int,
        mistakes: list[QuestionEvaluation],
        wins: list[QuestionEvaluation],
        language: str = "en",
    ) -> FeedbackCard:
        """
        Generate a FeedbackCard for the diagnostic quiz without an LLM call.
        Templates per score bracket, exploiting the real concept_id
        to point to the modules to review.
        """
        language = normalize_quiz_language(language)
        # Mastered and to-review concepts (deduced from the answers)
        # If the student had at least 1 mistake on a concept, we remove it from
        # the strengths even if they had correct answers on it -> no duplicate
        # between "strengths" and "to review".
        weak_concepts = sorted({
            e.concept_id for e in mistakes if e.concept_id
        })
        mastered_concepts = sorted({
            e.concept_id for e in wins
            if e.concept_id and e.concept_id not in weak_concepts
        })

        # Helper: readable name from concept_id
        def _readable(cid: str) -> str:
            if not cid:
                return ""
            # e.g. "concept_lagrange" -> "Lagrange"
            base = cid.replace("concept_", "").replace("_", " ").strip()
            return base.title()

        if language != "fr":
            if score >= 80:
                summary = (
                    f"Excellent. You scored {score:.0f}/100 ({n_correct}/{n_total}). "
                    "Your numerical-analysis foundations are solid, so you can move "
                    "toward more advanced material."
                )
                strengths = [_readable(c) for c in mastered_concepts[:5]] or ["General mastery"]
                weaknesses = []
                mistakes_detail = []
                next_steps = [
                    "Continue from the dashboard with the next recommended concept.",
                    "Take an adaptive quiz on an advanced concept to challenge yourself.",
                ]
            elif score >= 60:
                summary = (
                    f"Good work. You scored {score:.0f}/100 ({n_correct}/{n_total}). "
                    "You understand the basics, with a few points still to consolidate."
                )
                strengths = [_readable(c) for c in mastered_concepts[:4]]
                weaknesses = [_readable(c) for c in weak_concepts[:3]]
                mistakes_detail = [
                    f"Q{e.question_id}: the expected answer was '{e.correct_answer}'. {e.explanation}"
                    for e in mistakes[:3]
                ]
                next_steps = [
                    "Review the concepts marked for consolidation.",
                    "Retake a targeted quiz after revising those weak points.",
                ]
            elif score >= 40:
                summary = (
                    f"You scored {score:.0f}/100 ({n_correct}/{n_total}). "
                    "You have some foundations, but several gaps remain. "
                    "The adaptive path will guide you concept by concept."
                )
                strengths = [_readable(c) for c in mastered_concepts[:3]]
                weaknesses = [_readable(c) for c in weak_concepts[:5]]
                mistakes_detail = [
                    f"Q{e.question_id}: the expected answer was '{e.correct_answer}'. {e.explanation}"
                    for e in mistakes[:4]
                ]
                next_steps = [
                    "Start with Interpolation, which supports the other modules.",
                    "Use the AI tutor for concepts that feel unclear.",
                    "Retake targeted quizzes on weak concepts.",
                ]
            elif score >= 20:
                summary = (
                    f"You scored {score:.0f}/100 ({n_correct}/{n_total}). "
                    "Your foundations are still fragile, which is normal at the start. "
                    "The platform will build them step by step."
                )
                strengths = [_readable(c) for c in mastered_concepts[:2]]
                weaknesses = [_readable(c) for c in weak_concepts[:5]]
                mistakes_detail = [
                    f"Q{e.question_id}: the expected answer was '{e.correct_answer}'. {e.explanation}"
                    for e in mistakes[:5]
                ]
                next_steps = [
                    "Begin with simplified Interpolation content.",
                    "Read simplified explanations before taking quizzes.",
                    "Ask the AI tutor when a prerequisite is unclear.",
                ]
            else:
                summary = (
                    f"You scored {score:.0f}/100 ({n_correct}/{n_total}). "
                    "You are starting from the foundations. That is a useful baseline, "
                    "not a failure. The adaptive path is designed exactly for this."
                )
                strengths = []
                weaknesses = [_readable(c) for c in weak_concepts[:5]]
                mistakes_detail = [
                    f"Q{e.question_id}: the expected answer was '{e.correct_answer}'. {e.explanation}"
                    for e in mistakes[:5]
                ]
                next_steps = [
                    "Start with simplified Interpolation content.",
                    "Use the AI tutor whenever a step feels blocked.",
                    "Retake a diagnostic after one or two weeks of practice.",
                ]

            return FeedbackCard(
                score=round(score, 1),
                n_correct=n_correct,
                n_total=n_total,
                temps_reponse=temps_reponse,
                grade_label=self._grade_label(score, language),
                summary=summary,
                strengths=strengths,
                weaknesses=weaknesses,
                mistakes_detail=mistakes_detail,
                next_steps=next_steps,
                recommended_concepts=weak_concepts,
            )

        if score >= 80:
            summary = (
                f"Excellent ! Tu as obtenu {score:.0f}/100 ({n_correct}/{n_total}). "
                "Tes bases en analyse numerique sont solides — tu peux directement "
                "attaquer les contenus de niveau avance."
            )
            strengths = [_readable(c) for c in mastered_concepts[:5]] or ["Maitrise generale"]
            weaknesses = []
            mistakes_detail = []
            next_steps = [
                "Explore le module qui t'interesse le plus depuis le tableau de bord.",
                "Lance un quiz adaptatif sur un concept avance pour te challenger.",
            ]
        elif score >= 60:
            summary = (
                f"Bien ! Tu as obtenu {score:.0f}/100 ({n_correct}/{n_total}). "
                "Tu maitrises les bases mais il reste quelques points a consolider "
                "avant d'attaquer les concepts avances."
            )
            strengths = [_readable(c) for c in mastered_concepts[:4]]
            weaknesses = [_readable(c) for c in weak_concepts[:3]]
            mistakes_detail = [
                f"Q{e.question_id} : la bonne reponse etait '{e.correct_answer}'. {e.explanation}"
                for e in mistakes[:3]
            ]
            next_steps = [
                "Revois les concepts marques comme a consolider.",
                "Refais le diagnostic dans une semaine pour mesurer ta progression.",
            ]
        elif score >= 40:
            summary = (
                f"Tu as obtenu {score:.0f}/100 ({n_correct}/{n_total}). "
                "Tu as quelques bases mais il reste plusieurs lacunes a combler. "
                "Le parcours adaptatif va te guider concept par concept."
            )
            strengths = [_readable(c) for c in mastered_concepts[:3]]
            weaknesses = [_readable(c) for c in weak_concepts[:5]]
            mistakes_detail = [
                f"Q{e.question_id} : la bonne reponse etait '{e.correct_answer}'. {e.explanation}"
                for e in mistakes[:4]
            ]
            next_steps = [
                "Commence par le module Interpolation (prerequis aux autres).",
                "Utilise le tuteur IA pour les concepts ou tu te sens perdu.",
                "Refais des quiz cibles sur les concepts faibles.",
            ]
        elif score >= 20:
            summary = (
                f"Tu as obtenu {score:.0f}/100 ({n_correct}/{n_total}). "
                "Les bases sont fragiles, c'est normal en debut de parcours. "
                "On va construire tes connaissances etape par etape."
            )
            strengths = [_readable(c) for c in mastered_concepts[:2]] or []
            weaknesses = [_readable(c) for c in weak_concepts[:5]]
            mistakes_detail = [
                f"Q{e.question_id} : la bonne reponse etait '{e.correct_answer}'. {e.explanation}"
                for e in mistakes[:5]
            ]
            next_steps = [
                "Demarre par le module Interpolation au niveau debutant.",
                "Lis les contenus en mode 'simplifie' avant de tenter les quiz.",
                "Pose des questions au tuteur IA — il s'adapte a ton niveau.",
            ]
        else:
            # score < 20: factual and kind message already tested
            summary = (
                f"Tu as obtenu {score:.0f}/100 ({n_correct}/{n_total}). "
                "Tu demarres de zero sur ces concepts — c'est un point de depart "
                "honnete, pas un echec. Le parcours adaptatif est concu exactement "
                "pour ca : on va commencer par les prerequis fondamentaux."
            )
            strengths = []
            weaknesses = [_readable(c) for c in weak_concepts[:5]]
            mistakes_detail = [
                f"Q{e.question_id} : la bonne reponse etait '{e.correct_answer}'. {e.explanation}"
                for e in mistakes[:5]
            ]
            next_steps = [
                "Demarre par les contenus simplifies du module Interpolation.",
                "Utilise le tuteur IA des que tu te sens bloque — il explique a ton niveau.",
                "Refais le diagnostic dans 1-2 semaines pour mesurer ta progression.",
            ]

        return FeedbackCard(
            score=round(score, 1),
            n_correct=n_correct,
            n_total=n_total,
            temps_reponse=temps_reponse,
            grade_label=self._grade_label(score, language),
            summary=summary,
            strengths=strengths,
            weaknesses=weaknesses,
            mistakes_detail=mistakes_detail,
            next_steps=next_steps,
            recommended_concepts=weak_concepts,
        )


# Global instance
feedback_service = FeedbackService()
