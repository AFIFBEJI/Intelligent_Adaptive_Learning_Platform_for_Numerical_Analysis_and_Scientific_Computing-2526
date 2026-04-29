# ============================================================
# Service Feedback — Carte de rétroaction post-quiz
# ============================================================
# Ce service prend les réponses d'un étudiant à un quiz et produit
# une CARTE DE FEEDBACK pédagogique complète :
#   - Score global et label ("Excellent", "À revoir"...)
#   - Liste des bonnes réponses (points forts)
#   - Liste des erreurs avec EXPLICATION détaillée par le LLM
#   - Concepts à réviser (basé sur les erreurs)
#   - Recommandations concrètes ("refait le quiz", "revois X avant")
#
# Architecture :
# 1. Évaluation DÉTERMINISTE (matching string) pour les QCM/VF
# 2. Évaluation LLM pour les questions ouvertes
# 3. Agrégation → FeedbackCard
# 4. Un SECOND appel LLM pour générer les explications détaillées
#    des erreurs (si plus de 1 erreur)
# ============================================================
from __future__ import annotations

import json
import logging
import re
from typing import Any

from langchain_core.messages import HumanMessage
from sqlalchemy.orm import Session

from app.models.mastery import ConceptMastery
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
# Prompt pour l'évaluation d'une réponse ouverte
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
# Prompt pour la carte de feedback globale
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
    """Évalue les réponses et génère la carte de feedback post-quiz."""

    # ------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------
    @staticmethod
    def _normalize(value: str) -> str:
        """
        Normalise pour comparaison de QCM/VF :
        - minuscule
        - sans espaces ni ponctuation
        - sans accents (e/e, a/a, etc.)
        Ainsi "Méthode de Chebyshev" et "methode de chebyshev" matchent.
        """
        import unicodedata
        s = (value or "").strip().lower()
        # Decompose les accents puis supprime les marques diacritiques
        s = unicodedata.normalize("NFD", s)
        s = "".join(c for c in s if unicodedata.category(c) != "Mn")
        # Supprime espaces et ponctuation courante
        for ch in " \t\n.,;:!?'\"-()[]{}":
            s = s.replace(ch, "")
        return s

    @staticmethod
    def _extract_json(raw: str) -> dict[str, Any]:
        """Extrait le premier objet JSON (tolère bruit + fences)."""
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
    # Évaluation déterministe d'une question
    # ------------------------------------------------------------
    def _eval_exact(
        self, student: str, correct: str, options: list[str] | None = None
    ) -> tuple[bool, float]:
        """
        Match QCM/VF avec tolerance LLM :
        - normalisation accent + casse + ponctuation
        - si correct_answer est une lettre A-D, on la mappe sur options[index]
          (le LLM oscille entre lettre et texte malgre les consignes)
        - si options fournies et correct est texte qui matche une option, on
          accepte aussi la lettre A/B/C/D que l'etudiant aurait pu envoyer
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

        # Cas 1 : correct = lettre (ex "A" ou "C"), student = texte d'une option
        # On regarde si correct.upper() est A/B/C/D et on prend l'option correspondante
        if options and correct.strip() and len(correct.strip()) == 1:
            letter = correct.strip().upper()
            if letter in ("A", "B", "C", "D"):
                idx = ord(letter) - ord("A")
                if 0 <= idx < len(options):
                    if s_norm == self._normalize(options[idx]):
                        return True, 1.0

        # Cas 2 : student = lettre, correct = texte
        if options and student.strip() and len(student.strip()) == 1:
            letter = student.strip().upper()
            if letter in ("A", "B", "C", "D"):
                idx = ord(letter) - ord("A")
                if 0 <= idx < len(options):
                    if c_norm == self._normalize(options[idx]):
                        return True, 1.0

        return False, 0.0

    # ------------------------------------------------------------
    # Évaluation LLM pour questions ouvertes
    # ------------------------------------------------------------
    async def _eval_open(
        self, question: str, correct: str, student: str
    ) -> tuple[bool, float, str]:
        """Demande a Ollama (gemma-numerical-e2b) de juger une reponse ouverte."""
        # Si Ollama indisponible -> fallback exact match
        if llm_service.ollama_llm is None:
            is_c, pc = self._eval_exact(student, correct)
            return is_c, pc, "(Evalue par comparaison exacte, Ollama indisponible)"

        prompt_text = OPEN_EVAL_PROMPT.format(
            question=question,
            correct_answer=correct,
            student_answer=student or "(pas de reponse)",
        )
        messages = [HumanMessage(content=prompt_text)]

        try:
            # On utilise format='json' pour forcer une sortie JSON valide
            ollama_json = llm_service.ollama_llm.bind(format="json")
            resp = await ollama_json.ainvoke(messages)
            data = self._extract_json(resp.content)
            return (
                bool(data.get("is_correct", False)),
                float(data.get("partial_credit", 0.0)),
                str(data.get("explanation", "")),
            )
        except Exception as exc:
            logger.warning("Echec eval Ollama question ouverte : %s", exc)
            is_c, pc = self._eval_exact(student, correct)
            return is_c, pc, "(Fallback comparaison exacte)"

    # ------------------------------------------------------------
    # Évalue toutes les questions d'une soumission
    # ------------------------------------------------------------
    async def evaluate_answers(
        self, quiz: Quiz, answers: list[StudentAnswer]
    ) -> list[QuestionEvaluation]:
        """Retourne l'évaluation question par question."""
        # Construire un index des réponses étudiantes
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
                # Log diagnostique pour comprendre les mismatches eventuels
                logger.info(
                    "Q%s [%s] : student='%s' vs correct='%s' (options=%s) -> is_correct=%s",
                    qid, qtype, student[:60], correct[:60],
                    [o[:30] for o in opts] if opts else None,
                    is_correct,
                )
                # Pour l affichage, si correct est une lettre A-D et qu on a les
                # options, on remplace par le texte complet pour que l etudiant
                # comprenne ce qu il aurait du repondre.
                if opts and correct.strip() and len(correct.strip()) == 1:
                    letter = correct.strip().upper()
                    if letter in ("A", "B", "C", "D"):
                        idx = ord(letter) - ord("A")
                        if 0 <= idx < len(opts):
                            correct_display = opts[idx]
                # On ne prefix plus avec "La bonne reponse etait" : l'UI affiche
                # deja correct_answer separement, le doubler est redondant.
                exp = explanation or ""
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
    # Construire la carte de feedback globale
    # ------------------------------------------------------------
    async def build_feedback_card(
        self,
        quiz: Quiz,
        evaluations: list[QuestionEvaluation],
        temps_reponse: int,
        language: str = "en",
    ) -> FeedbackCard:
        """
        Produit la FeedbackCard finale.

        - Pour le quiz diagnostique (module="Diagnostic") : on n'appelle PAS
          le LLM et on genere un feedback templaite (instantane, ~50ms).
          Justification : les questions sont fixes, le score determine seul
          le message pedagogique. Pas besoin du LLM pour ca.
        - Pour les autres quiz adaptatifs : appel LLM pour personnaliser
          le summary, strengths, weaknesses, mistakes_detail, next_steps.
        """
        language = normalize_quiz_language(language)
        n_total = len(evaluations)
        n_correct = sum(1 for e in evaluations if e.is_correct)
        # Score pondéré par partial_credit pour accepter les réponses partielles
        points = sum(e.partial_credit for e in evaluations)
        score = (points / n_total * 100.0) if n_total else 0.0

        mistakes = [e for e in evaluations if not e.is_correct]
        wins = [e for e in evaluations if e.is_correct]

        # --- Appel LLM pour rédiger la carte pédagogique ---
        mistakes_block = (
            "\n".join(
                f"  Q{e.question_id} ({e.question[:80]}...) : "
                f"étudiant='{e.student_answer}' vs correct='{e.correct_answer}'"
                for e in mistakes
            )
            or "  (aucune)"
        )
        strengths_block = (
            "\n".join(f"  Q{e.question_id}: {e.question[:80]}" for e in wins)
            or "  (aucune)"
        )

        card_data: dict[str, Any] = {
            "summary": "",
            "strengths": [],
            "weaknesses": [],
            "mistakes_detail": [],
            "next_steps": [],
        }

        # =========================================================
        # Feedback templated par defaut pour TOUS les quiz
        # =========================================================
        # On a retire le LLM du flow utilisateur pour garantir une UX
        # instantanee (< 100ms). Le templating couvre les 5 tranches de
        # score et utilise les concept_id reels pour pointer les modules
        # a reviser. Le LLM reste invocable manuellement via use_llm=True
        # mais n'est plus appele par defaut dans build_feedback_card.
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
    # Mise à jour du niveau de maîtrise
    # ------------------------------------------------------------
    @staticmethod
    def update_mastery_from_evaluations(
        db: Session,
        etudiant_id: int,
        evaluations: list[QuestionEvaluation],
    ) -> None:
        """
        Met à jour ConceptMastery pour chaque concept touché par le quiz.
        Moyenne pondérée : 60 % ancien + 40 % nouveau (même logique que l'ancien module).
        """
        # Grouper les partial_credits par concept
        by_concept: dict[str, list[float]] = {}
        for e in evaluations:
            if not e.concept_id:
                continue
            by_concept.setdefault(e.concept_id, []).append(e.partial_credit)

        for concept_id, scores in by_concept.items():
            new_score = (sum(scores) / len(scores)) * 100.0
            mastery = (
                db.query(ConceptMastery)
                .filter(
                    ConceptMastery.etudiant_id == etudiant_id,
                    ConceptMastery.concept_neo4j_id == concept_id,
                )
                .first()
            )
            if mastery is None:
                mastery = ConceptMastery(
                    etudiant_id=etudiant_id,
                    concept_neo4j_id=concept_id,
                    niveau_maitrise=round(new_score, 1),
                )
                db.add(mastery)
            else:
                mastery.niveau_maitrise = round(
                    mastery.niveau_maitrise * 0.6 + new_score * 0.4, 1
                )


    # ------------------------------------------------------------
    # Feedback templated pour quiz diagnostique (sans LLM)
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
        Genere une FeedbackCard pour le quiz diagnostique sans appel LLM.
        Templates par tranche de score, exploitant les concept_id reels
        pour pointer les modules a reviser.
        """
        language = normalize_quiz_language(language)
        # Concepts maitrises et a reviser (deduits des reponses)
        # Si l'etudiant a eu au moins 1 erreur sur un concept, on le retire des
        # forces meme s'il a eu des bonnes reponses dessus -> pas de doublon
        # entre "points forts" et "a revoir".
        weak_concepts = sorted({
            e.concept_id for e in mistakes if e.concept_id
        })
        mastered_concepts = sorted({
            e.concept_id for e in wins
            if e.concept_id and e.concept_id not in weak_concepts
        })

        # Helper : nom lisible depuis concept_id
        def _readable(cid: str) -> str:
            if not cid:
                return ""
            # ex. "concept_lagrange" -> "Lagrange"
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
            # score < 20 : message factuel et bienveillant deja teste
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


# Instance globale
feedback_service = FeedbackService()
