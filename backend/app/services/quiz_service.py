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
        supported = {"mcq", "true_false", "open"}
        cleaned = [qtype for qtype in (question_types or []) if qtype in supported]
        return cleaned or ["mcq"]

    @staticmethod
    def _type_for_bank_question(
        question_types: list[str],
        index: int,
    ) -> str:
        # Cycle through the selected types so the quiz respects the learner's
        # requested format mix even when questions come from the deterministic bank.
        return question_types[(index - 1) % len(question_types)]

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
        Appelle Ollama (gemma-numerical-e2b) avec format='json' pour
        forcer une sortie JSON valide via le modele local Ollama.
        """
        messages = [SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)]

        if llm_service.ollama_llm is None:
            raise RuntimeError(
                "Ollama indisponible. Lancez 'ollama serve' et verifiez "
                "que le modele 'gemma-numerical-e2b' est installe "
                "(voir Module de Math/Modelfile_E2B)."
            )

        try:
            logger.info("Appel Ollama (gemma-numerical-e2b) avec format=json...")
            t0 = time.time()
            # bind() retourne un nouveau llm avec ces parametres pour cet appel
            # - format='json' : Ollama force la sortie au format JSON valide
            # - num_predict est defini dans le constructeur ChatOllama (LLM_MAX_TOKENS)
            #   car le client Ollama recent n'accepte plus num_predict via .bind()
            ollama_json = llm_service.ollama_llm.bind(format="json")
            response = await ollama_json.ainvoke(messages)
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
                            language="en"):
        """
        Genere un quiz pour un concept donne.

        - use_llm=False (DEFAULT) : pioche 5 questions au hasard depuis
          quiz_question_bank.py (75 questions hand-curated, instantane).
        - use_llm=True : appelle Gemma E2B pour generer dynamiquement
          (variantes IA experimentales, ~30s, qualite variable).
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
        mastery = context.student_mastery or 0.0
        difficulty = self._difficulty_for_mastery(mastery, difficulty_override)
        seed = self._make_seed()

        # ─── MODE BANQUE (defaut, instantane) ─────────────────
        if not use_llm:
            from app.data.quiz_question_bank import get_questions_for_concept

            rng = random.Random(seed)
            pool_questions = get_questions_for_concept(
                context.concept_id, n=n_questions, rng=rng,
            )

            if pool_questions:
                logger.info(
                    "Quiz banque : %d questions piochees pour %s",
                    len(pool_questions), context.concept_id,
                )
                validated = []
                for idx, raw_question in enumerate(pool_questions, start=1):
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
                    except Exception as exc:
                        logger.warning("Question banque invalide : %s", exc)

                if len(validated) >= 2:
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
                    )
                    db.add(quiz)
                    db.commit()
                    db.refresh(quiz)
                    logger.info(
                        "Quiz banque cree : id=%d, %d questions, instantane",
                        quiz.id, len(validated),
                    )
                    return quiz
            # Si pas de questions en banque pour ce concept, on tombe sur le LLM
            logger.warning(
                "Aucune question en banque pour %s, fallback LLM",
                context.concept_id,
            )

        # ─── MODE LLM (use_llm=True ou fallback) ──────────────

        prereqs_lines = []
        for p in context.prerequisites[:5]:
            status = "OK" if p.get("status") == "mastered" else "FAIBLE"
            prereqs_lines.append(f"  [{status}] {p['name']} - {p.get('mastery', 0):.0f}%")
        prereqs_block = (
            "PREREQUIS :\n" + "\n".join(prereqs_lines) if prereqs_lines else "PREREQUIS : aucun."
        )

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
        )
        db.add(quiz)
        db.commit()
        db.refresh(quiz)

        logger.info("Quiz cree : id=%d, %d questions", quiz.id, len(validated))
        return quiz

    # ----------------------------------------------------------
    # Quiz diagnostique multi-concepts (onboarding)
    # ----------------------------------------------------------
    async def generate_diagnostic_quiz(self, db, etudiant_id, n_concepts=5, language="en"):
        """
        Genere un quiz diagnostique a partir de la BANQUE DE QUESTIONS
        pre-ecrites (app/data/diagnostic_questions.py).

        Pourquoi pas le LLM ?
        Le modele fine-tune Gemma E2B (2B params) genere parfois des QCM
        ou la bonne reponse est absente des options ou ou plusieurs options
        sont synonymes. Resultat : score 0 alors que l'etudiant a raisonne
        correctement, et frustration. Avec une banque hand-crafted on garantit :
        - 4 distracteurs plausibles mais clairement faux
        - Bonne reponse toujours dans les options
        - Explication pedagogique pour chaque question
        - Generation < 50ms (vs 30-60s pour le LLM)

        Strategie de tirage :
        - On regroupe les 30 questions par module_id
        - On pioche n_concepts questions reparties equitablement sur les 3
          modules (Interpolation, Integration, Approximation/Optim)
        - Le seed (timestamp + random) garantit que chaque etudiant recoit
          un quiz different a chaque fois

        Parametres :
            db : session SQLAlchemy
            etudiant_id : id de l'etudiant
            n_concepts : nombre de questions a tirer (defaut 5)

        Retourne :
            Quiz persiste avec source="generated", module="Diagnostic",
            chaque question rattachee a son concept_id Neo4j.
        """
        from app.data.diagnostic_questions import (
            DIAGNOSTIC_QUESTION_BANK,
            get_questions_by_module,
        )

        language = normalize_quiz_language(language)

        if not DIAGNOSTIC_QUESTION_BANK:
            raise RuntimeError("Banque de questions diagnostiques vide.")

        # 1. Tirage : repartir n_concepts sur les 3 modules
        # (ex. n=5 -> 2/2/1, n=6 -> 2/2/2, n=4 -> 2/1/1)
        seed = self._make_seed()
        rng = random.Random(seed)  # generateur deterministe par seed

        by_module = get_questions_by_module()
        module_ids = sorted(by_module.keys())

        # Repartition equitable
        base = n_concepts // len(module_ids)
        extra = n_concepts % len(module_ids)
        # On melange l'ordre des modules pour que le module qui recoit
        # un slot supplementaire varie d'un quiz a l'autre
        rng.shuffle(module_ids)

        selected_questions: list[dict] = []
        for i, mod_id in enumerate(module_ids):
            count = base + (1 if i < extra else 0)
            pool = list(by_module[mod_id])
            rng.shuffle(pool)
            selected_questions.extend(pool[:count])

        # On melange l'ordre final pour que les modules ne soient pas
        # presentes en bloc
        rng.shuffle(selected_questions)

        if len(selected_questions) < 3:
            raise RuntimeError(
                f"Pas assez de questions piochees ({len(selected_questions)}). "
                "Verifiez la banque diagnostic_questions.py."
            )

        # 2. Validation Pydantic et ajout d'ids sequentiels
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

        # 3. Persistance (meme schema qu'avant pour compat avec le router)
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
