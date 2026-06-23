from __future__ import annotations

import hashlib
import json
import logging
import random
import re
import time
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from app.models.quiz import Quiz
from app.schemas.quiz_dynamic import GeneratedQuestion
from app.services.llm_service import llm_service
from app.services.quiz_localization import (
    localize_bank_question,
    normalize_quiz_language,
    true_false_labels,
)
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)


QUIZ_SYSTEM_PROMPT_FR = """Genere {n_questions} questions QCM sur "{concept_name}" niveau {difficulty_label} (etudiant a {mastery}% de maitrise). Seed: {seed}. {difficulty_instruction}

JSON requis (rien d'autre) :
{{"questions":[{{"id":1,"type":"mcq","question":"...","options":["A","B","C","D"],"correct_answer":"A","explanation":"...","difficulty":"{difficulty_label}"}}]}}

Regles : 4 options distinctes, LaTeX en $...$ si formule, explanation courte (1 phrase), correct_answer = texte exact d'une option."""

QUIZ_SYSTEM_PROMPT_EN = """Generate {n_questions} multiple-choice questions about "{concept_name}" for a {difficulty_label} learner (current mastery: {mastery}%). Seed: {seed}. {difficulty_instruction}

Required JSON only:
{{"questions":[{{"id":1,"type":"mcq","question":"...","options":["A","B","C","D"],"correct_answer":"A","explanation":"...","difficulty":"{difficulty_code}"}}]}}

Rules: all question, option and explanation text must be in English; use LaTeX in $...$ for formulas; keep explanations short; correct_answer must exactly match one option."""


class QuizService:
    @staticmethod
    def _make_seed() -> str:
        raw = f"{time.time()}:{random.random()}"
        return hashlib.sha256(raw.encode()).hexdigest()[:12]

    @staticmethod
    def _difficulty_for_mastery(mastery: float, override: str = "auto") -> str:
        if override != "auto":
            return override
        if mastery < 30:
            return "facile"
        if mastery < 70:
            return "moyen"
        return "difficile"

    @staticmethod
    def _difficulty_label(difficulty: str, language: str) -> str:
        if language == "en":
            return {
                "facile": "easy",
                "moyen": "medium",
                "difficile": "hard",
            }.get(difficulty, difficulty)
        return difficulty

    @staticmethod
    def _difficulty_instruction(difficulty: str, language: str = "fr") -> str:
        if language == "en":
            if difficulty == "facile":
                return "Use recall questions and simple numerical values."
            if difficulty == "moyen":
                return "Mix conceptual understanding with short applications."
            return "Include analysis questions about error order, stability or edge cases."
        if difficulty == "facile":
            return "Questions de rappel, valeurs simples."
        if difficulty == "moyen":
            return "Melange comprehension et application."
        return "Analyse : erreurs d'ordre, stabilite, cas limite."

    @staticmethod
    def _normalize_question_types(question_types: list[str] | None) -> list[str]:
        supported = {"mcq", "true_false", "open", "numeric"}
        cleaned = [qtype for qtype in (question_types or []) if qtype in supported]
        return cleaned or ["mcq"]

    @staticmethod
    def _type_for_bank_question(
        question_types: list[str],
        index: int,
    ) -> str:
        # Bank questions are MCQ-based, so we only cycle through the NON-numeric
        # formats here. Numeric questions come from a separate verified set
        # (numeric_questions.py) and are handled outside this helper.
        usable = [t for t in question_types if t != "numeric"] or ["mcq"]
        return usable[(index - 1) % len(usable)]

    @staticmethod
    def _numeric_to_payload(
        raw: dict,
        idx: int,
        language: str,
        concept_id: str | None,
        difficulty: str,
    ) -> dict:
        """Convert a numeric_questions.py entry into a quiz question payload.

        The expected answer is stored as a string in correct_answer, with the
        per-question tolerance. Graded deterministically by feedback_service
        (no AI)."""
        question = raw.get("question_fr") if language == "fr" else raw.get("question_en")
        explanation = raw.get("explanation_fr") if language == "fr" else raw.get("explanation_en")
        return {
            "id": idx,
            "type": "numeric",
            "question": question or raw.get("question_en", ""),
            "options": None,
            "correct_answer": str(raw.get("answer")),
            "explanation": explanation or "",
            "concept_id": concept_id,
            "tolerance": float(raw.get("tolerance", 0.05)),
            "difficulty": difficulty,
            "language": language,
        }

    @staticmethod
    def _bank_question_to_payload(
        q: dict[str, Any],
        idx: int,
        qtype: str,
        language: str,
        rng: random.Random,
        concept_id: str | None,
        difficulty: str,
    ) -> dict[str, Any]:
        base_payload = {
            "id": idx,
            "type": qtype,
            "question": q["question"],
            "correct_answer": q["correct_answer"],
            "explanation": q.get("explanation", ""),
            "concept_id": concept_id,
            "difficulty": difficulty,
            "language": language,
        }

        if qtype == "open":
            return {**base_payload, "options": None}

        if qtype == "true_false":
            true_label, false_label = true_false_labels(language)
            options = list(q.get("options") or [])
            correct = str(q.get("correct_answer", ""))
            distractors = [opt for opt in options if opt != correct]
            use_true_statement = not distractors or rng.random() >= 0.45
            candidate = correct if use_true_statement else rng.choice(distractors)
            answer = true_label if use_true_statement else false_label

            if language == "fr":
                statement = (
                    f'Vrai ou faux : la reponse a "{q["question"]}" est '
                    f'"{candidate}".'
                )
                if use_true_statement:
                    explanation = (
                        f"L'affirmation est vraie : {candidate} est la bonne reponse. "
                        f"{q.get('explanation', '')}"
                    )
                else:
                    explanation = (
                        f"L'affirmation est fausse : la bonne reponse est {correct}. "
                        f"{q.get('explanation', '')}"
                    )
            else:
                statement = (
                    f'True or false: the answer to "{q["question"]}" is '
                    f'"{candidate}".'
                )
                if use_true_statement:
                    explanation = (
                        f"The statement is true: {candidate} is the correct answer. "
                        f"{q.get('explanation', '')}"
                    )
                else:
                    explanation = (
                        f"The statement is false: the correct answer is {correct}. "
                        f"{q.get('explanation', '')}"
                    )

            return {
                **base_payload,
                "question": statement,
                "options": [true_label, false_label],
                "correct_answer": answer,
                "explanation": explanation.strip(),
            }

        return {**base_payload, "type": "mcq", "options": q.get("options") or []}

    @staticmethod
    def _extract_json(raw: str) -> dict[str, Any]:
        cleaned = raw.strip()
        fence_re = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)
        cleaned = fence_re.sub("", cleaned).strip()
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("Aucun JSON")
        blob = cleaned[start : end + 1]
        try:
            return json.loads(blob)
        except json.JSONDecodeError:
            blob2 = re.sub(r",(\s*[}\]])", r"\1", blob)
            return json.loads(blob2)

    async def _ask_llm_for_json_parsed(self, system_prompt, human_prompt):
        """
        Call Ollama (gemma-numerical-e2b) with format='json' to
        force a valid JSON output via the local Ollama model.
        """
        messages = [SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)]

        if llm_service.llm is None:
            raise RuntimeError(
                f"LLM indisponible (provider={llm_service.provider}). "
                "Si Ollama : lancez 'ollama serve' et verifiez le modele. "
                "Si OpenAI : verifiez OPENAI_API_KEY dans .env."
            )

        try:
            logger.info("Appel %s (%s) en mode JSON...", llm_service.provider, llm_service.model_name)
            t0 = time.time()
            # bind_json() unifies the two providers (Ollama: format=json,
            # OpenAI: response_format=json_object) to force a valid JSON output.
            llm_json = llm_service.bind_json()
            response = await llm_json.ainvoke(messages)
            raw = response.content
            logger.info("Ollama repondu en %.1fs (%d chars)", time.time() - t0, len(raw))
            try:
                return self._extract_json(raw)
            except (ValueError, json.JSONDecodeError) as exc:
                logger.error("Ollama JSON invalide. Raw: %s", raw[:500])
                raise RuntimeError(f"Ollama JSON invalide : {exc}") from exc
        except RuntimeError:
            raise
        except Exception as exc:
            logger.error("Ollama erreur : %s", exc)
            raise RuntimeError(f"Ollama erreur : {exc}") from exc

    async def generate_quiz(self, db, etudiant_id, concept_id=None, topic=None,
                            n_questions=5, difficulty_override="auto",
                            question_types=None, use_llm=False,
                            language="en", mode="adaptive"):
        """
        Generate a quiz for a given concept.

        - use_llm=False (DEFAULT): randomly draws 5 questions from
          quiz_question_bank.py (75 hand-curated questions, instant).
        - use_llm=True: calls Gemma E2B to generate dynamically
          (experimental AI variants, ~30s, variable quality).
        """
        language = normalize_quiz_language(language)
        question_types = self._normalize_question_types(question_types)

        if concept_id:
            context = rag_service.build_context(
                db=db, etudiant_id=etudiant_id, question=topic or "", concept_id=concept_id)
        else:
            context = rag_service.build_context(
                db=db, etudiant_id=etudiant_id, question=topic or "Analyse numerique")

        concept_name = context.concept_name or "Analyse numerique"
        module_name = context.module_name or "Numerical Analysis"
        # Difficulty driven by the student's GLOBAL level (niveau_actuel),
        # not by the mastery of this specific concept.
        mastery = llm_service.mastery_from_level(getattr(context, "student_level", "beginner"))
        difficulty = self._difficulty_for_mastery(mastery, difficulty_override)
        seed = self._make_seed()

        # ─── BANK MODE (default, instant) ─────────────────
        if not use_llm:
            from app.data.numeric_questions import get_numeric_questions
            from app.data.quiz_question_bank import get_questions_for_concept

            rng = random.Random(seed)
            validated = []
            idx = 1

            # 1) Numeric questions (deterministic, no AI) if requested.
            if "numeric" in question_types:
                for raw_num in get_numeric_questions(
                    context.concept_id, n=min(2, n_questions), rng=rng
                ):
                    payload = self._numeric_to_payload(
                        raw_num, idx, language, context.concept_id, difficulty
                    )
                    try:
                        validated.append(GeneratedQuestion(**payload))
                        idx += 1
                    except Exception as exc:
                        logger.warning("Question numerique invalide : %s", exc)

            # 2) Fill the remaining slots with MCQ/TF/open bank questions.
            remaining = max(n_questions - len(validated), 0)
            pool_questions = (
                get_questions_for_concept(context.concept_id, n=remaining, rng=rng)
                if remaining
                else []
            )

            if pool_questions or validated:
                logger.info(
                    "Quiz banque : %d numeriques + %d banque pour %s",
                    len(validated), len(pool_questions), context.concept_id,
                )
                for raw_question in pool_questions:
                    q = localize_bank_question(raw_question, language)
                    qtype = self._type_for_bank_question(question_types, idx)
                    payload = self._bank_question_to_payload(
                        q=q,
                        idx=idx,
                        qtype=qtype,
                        language=language,
                        rng=rng,
                        concept_id=context.concept_id,
                        difficulty=difficulty,
                    )
                    try:
                        validated.append(GeneratedQuestion(**payload))
                        idx += 1
                    except Exception as exc:
                        logger.warning("Question banque invalide : %s", exc)

                if len(validated) >= 2:
                    # The title reflects the mode so the history makes it visible.
                    if mode == "practice":
                        title_prefix = "Practice Quiz" if language == "en" else "Quiz d'entrainement"
                    else:
                        title_prefix = "Adaptive Quiz" if language == "en" else "Quiz adaptatif"
                    quiz = Quiz(
                        titre=f"{title_prefix} - {concept_name}",
                        module=module_name,
                        difficulte=difficulty,
                        questions=[q.model_dump() for q in validated],
                        source="generated",
                        etudiant_generateur_id=etudiant_id,
                        concept_neo4j_id=context.concept_id,
                        seed=seed,
                        mode=mode,
                    )
                    db.add(quiz)
                    db.commit()
                    db.refresh(quiz)
                    logger.info(
                        "Quiz banque cree : id=%d, %d questions, instantane",
                        quiz.id, len(validated),
                    )
                    return quiz
            # If there are no bank questions for this concept, we fall back to the LLM
            logger.warning(
                "Aucune question en banque pour %s, fallback LLM",
                context.concept_id,
            )

        # ─── LLM MODE (use_llm=True or fallback) ──────────────

        difficulty_label = self._difficulty_label(difficulty, language)
        system_template = QUIZ_SYSTEM_PROMPT_EN if language == "en" else QUIZ_SYSTEM_PROMPT_FR
        system_prompt = system_template.format(
            n_questions=n_questions,
            concept_name=concept_name,
            difficulty_label=difficulty_label,
            difficulty_code=difficulty,
            mastery=f"{mastery:.0f}",
            seed=seed,
            difficulty_instruction=self._difficulty_instruction(difficulty, language),
        )
        human_prompt = (
            (
                f"Generate {n_questions} questions about '{concept_name}' at "
                f"{difficulty} level. Seed: {seed}. Return ONLY JSON. "
                "All question, option and explanation text must be in English."
            )
            if language == "en"
            else
            f"Genere {n_questions} questions sur '{concept_name}' au niveau "
            f"{difficulty}. Seed : {seed}. Retourne UNIQUEMENT le JSON. "
            "Tout le texte doit etre en francais."
        )

        try:
            payload = await self._ask_llm_for_json_parsed(system_prompt, human_prompt)
        except RuntimeError as exc:
            logger.error("Echec generation : %s", exc)
            raise RuntimeError("Le modele n'a pas genere un quiz valide. Reessayer.") from exc

        raw_questions = payload.get("questions", [])
        if not raw_questions:
            raise RuntimeError("Aucune question generee.")

        validated = []
        for idx, q in enumerate(raw_questions[:n_questions], start=1):
            q.setdefault("id", idx)
            q.setdefault("concept_id", context.concept_id)
            q.setdefault("difficulty", difficulty)
            q.setdefault("language", language)
            try:
                validated.append(GeneratedQuestion(**q))
            except Exception as exc:
                logger.warning("Question %d invalide : %s", idx, exc)
                continue

        if len(validated) < 2:
            raise RuntimeError(f"Trop peu de questions valides ({len(validated)})")

        quiz = Quiz(
            titre=f"AI Quiz - {concept_name}" if language == "en" else f"Quiz IA - {concept_name}",
            module=module_name,
            difficulte=difficulty,
            questions=[q.model_dump() for q in validated],
            source="generated",
            etudiant_generateur_id=etudiant_id,
            concept_neo4j_id=context.concept_id,
            seed=seed,
            mode=mode,
        )
        db.add(quiz)
        db.commit()
        db.refresh(quiz)

        logger.info("Quiz cree : id=%d, %d questions", quiz.id, len(validated))
        return quiz

    # ----------------------------------------------------------
    # Multi-concept diagnostic quiz (onboarding)
    # ----------------------------------------------------------
    async def generate_diagnostic_quiz(self, db, etudiant_id, n_concepts=5, language="en"):
        """
        Generate a diagnostic quiz from the pre-written QUESTION BANK
        (app/data/diagnostic_questions.py).

        Why not the LLM?
        The fine-tuned Gemma E2B model (2B params) sometimes generates MCQs
        where the correct answer is missing from the options or where several
        options are synonyms. Result: score 0 while the student reasoned
        correctly, and frustration. With a hand-crafted bank we guarantee:
        - 4 plausible but clearly wrong distractors
        - Correct answer always among the options
        - Pedagogical explanation for each question
        - Generation < 50ms (vs 30-60s for the LLM)

        Drawing strategy:
        - We group the 30 questions by module_id
        - We draw n_concepts questions evenly distributed across the 3
          modules (Interpolation, Integration, Approximation/Optim)
        - The seed (timestamp + random) guarantees that each student receives
          a different quiz every time

        Parameters:
            db: SQLAlchemy session
            etudiant_id: the student's id
            n_concepts: number of questions to draw (default 5)

        Returns:
            Quiz persisted with source="generated", module="Diagnostic",
            each question attached to its Neo4j concept_id.
        """
        from app.data.diagnostic_questions import (
            DIAGNOSTIC_QUESTION_BANK,
            get_questions_by_module,
        )

        language = normalize_quiz_language(language)

        if not DIAGNOSTIC_QUESTION_BANK:
            raise RuntimeError("Banque de questions diagnostiques vide.")

        # 1. Drawing: distribute n_concepts across the 3 modules
        # (e.g. n=5 -> 2/2/1, n=6 -> 2/2/2, n=4 -> 2/1/1)
        seed = self._make_seed()
        rng = random.Random(seed)  # deterministic generator per seed

        by_module = get_questions_by_module()
        module_ids = sorted(by_module.keys())

        # Even distribution
        base = n_concepts // len(module_ids)
        extra = n_concepts % len(module_ids)
        # We shuffle the order of the modules so the module that receives
        # an extra slot varies from one quiz to another
        rng.shuffle(module_ids)

        selected_questions: list[dict] = []
        for i, mod_id in enumerate(module_ids):
            count = base + (1 if i < extra else 0)
            pool = list(by_module[mod_id])
            rng.shuffle(pool)
            selected_questions.extend(pool[:count])

        # We shuffle the final order so the modules are not
        # presented as a block
        rng.shuffle(selected_questions)

        if len(selected_questions) < 3:
            raise RuntimeError(
                f"Pas assez de questions piochees ({len(selected_questions)}). "
                "Verifiez la banque diagnostic_questions.py."
            )

        # 2. Pydantic validation and adding sequential ids
        validated = []
        localized_selected = [
            localize_bank_question(q, language)
            for q in selected_questions[:n_concepts]
        ]

        for idx, q in enumerate(localized_selected, start=1):
            payload = {
                "id": idx,
                "type": "mcq",
                "question": q["question"],
                "options": q["options"],
                "correct_answer": q["correct_answer"],
                "explanation": q["explanation"],
                "concept_id": q["concept_id"],
                "difficulty": q.get("difficulty", "facile"),
                "language": language,
            }
            try:
                validated.append(GeneratedQuestion(**payload))
            except Exception as exc:
                logger.warning(
                    "Question diagnostique %d invalide pour concept %s : %s",
                    idx, q["concept_id"], exc,
                )
                continue

        if len(validated) < 3:
            raise RuntimeError(
                f"Trop peu de questions valides apres pydantic ({len(validated)})."
            )

        # 3. Persistence (same schema as before for compat with the router)
        quiz = Quiz(
            titre="Diagnostic Quiz - Welcome" if language == "en" else "Quiz Diagnostique - Bienvenue",
            module="Diagnostic",
            difficulte="facile",
            questions=[q.model_dump() for q in validated],
            source="generated",
            etudiant_generateur_id=etudiant_id,
            concept_neo4j_id=None,  # multi-concepts
            seed=seed,
        )
        db.add(quiz)
        db.commit()
        db.refresh(quiz)

        modules_covered = sorted({q["module_name"] for q in selected_questions[:n_concepts]})
        logger.info(
            "Quiz diagnostique cree (BANQUE) : id=%d, %d questions sur %d concepts (modules: %s)",
            quiz.id,
            len(validated),
            len(selected_questions[:n_concepts]),
            ", ".join(modules_covered),
        )
        return quiz


quiz_service = QuizService()
