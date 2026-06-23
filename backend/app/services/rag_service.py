# ============================================================
# RAG Service — Retrieval-Augmented Generation
# ============================================================
# What is this file?
#
# It is the "brain" that SEARCHES for the relevant information
# BEFORE asking the question to the AI (the LLM).
#
# Without RAG: "Explain Lagrange" -> generic answer
# With RAG: "Explain Lagrange" -> we first look at:
#   - Lagrange's prerequisites in Neo4j
#   - The student's mastery level in PostgreSQL
#   - The resources available for this concept
#   -> answer PERSONALIZED to the student's level
#
# This is the "Graph" in "GraphRAG": we use the Neo4j
# knowledge GRAPH to enrich the AI's answers.
# ============================================================

import logging
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.graph.neo4j_connection import neo4j_conn
from app.models.mastery import ConceptMastery
from app.services import embedding_service

# Minimum cosine similarity for a SEMANTIC match to be trusted. Below this
# the meanings are too far apart, so we fall back to the keyword scoring.
_SEMANTIC_MIN_SIM = 0.30

logger = logging.getLogger(__name__)
settings = get_settings()


def _normalize_lang(lang: str | None) -> str:
    """Limit to 'fr' or 'en'. Default 'en'."""
    return "fr" if (lang or "").lower() == "fr" else "en"


import re as _re

# Tokens too short or too generic that we ignore in the RAG scoring
# (otherwise "de", "la", "the" match everywhere and skew the score).
_STOP_WORDS = frozenset({
    # FR
    "de", "la", "le", "les", "des", "un", "une", "et", "ou", "a", "au",
    "aux", "du", "en", "ce", "ces", "cette", "tu", "moi", "toi", "il",
    "elle", "se", "sa", "son", "ses", "pour", "par", "avec", "sans",
    "dans", "sur", "sous", "que", "qui", "quoi", "comment", "explique",
    "explique-moi", "explique-toi", "comprend", "comprends", "donne",
    "donne-moi", "peux", "peux-tu", "veux", "veux-tu", "est-ce", "est",
    "etre", "fait", "faut",
    # EN
    "the", "a", "an", "of", "in", "on", "at", "to", "for", "with", "by",
    "and", "or", "is", "are", "was", "were", "be", "been", "being",
    "you", "me", "my", "your", "we", "us", "they", "them",
    "explain", "tell", "show", "give", "what", "how", "when", "why",
    "where", "this", "that", "these", "those",
})

# Strong keywords that indicate a question about **solving
# nonlinear equations** (Module 4). When we detect them, we
# boost the Module 4 concepts to avoid a weak match
# toward Newton interpolation winning by default.
_ROOT_FINDING_KEYWORDS = frozenset({
    # FR
    "racine", "racines", "zero", "zeros", "zéro", "zéros",
    "resoudre", "résoudre", "annule", "annuler", "raphson",
    "bissection", "bisection", "secante", "sécante",
    # EN
    "root", "roots", "solve", "solving", "raphson", "bisection",
    "secant", "find",
})

_ROOT_FINDING_CONCEPTS = frozenset({
    "concept_bissection",
    "concept_fixed_point",
    "concept_newton_raphson",
    "concept_secant",
})


def _tokenize(text: str) -> set[str]:
    """Tokenize a string into lowercase words, splitting on spaces,
    dashes, punctuation and apostrophes. Filter out stop-words and
    tokens shorter than 3 characters.

    Examples:
      "Newton-Raphson Method"   -> {"newton", "raphson", "method"}
      "Methode de Newton"       -> {"methode", "newton"}
      "f(x)=0"                  -> set() (too short)
    """
    if not text:
        return set()
    # split on any non-alphanumeric character (handles FR/EN)
    raw = _re.split(r"[^a-zA-Z0-9À-ſ]+", text.lower())
    return {t for t in raw if len(t) >= 3 and t not in _STOP_WORDS}


class ConceptContext:
    """
    Contains ALL the context of a concept for a given student.

    It is like a "file" we prepare before calling the AI.
    It contains:
    - The concept info (name, description, difficulty)
    - The student's mastery level on this concept
    - The prerequisites (what the student must know first)
    - The student's mastery on each prerequisite
    - The available remediation resources
    """

    def __init__(self):
        self.concept_id: str = ""
        self.concept_name: str = ""
        self.description: str = ""
        self.difficulty: str = ""
        self.module_name: str = ""
        self.student_mastery: float = 0.0
        # Student's GLOBAL level (beginner / intermediate / advanced), used to
        # adapt the tutor and quizzes by overall level rather than per concept.
        self.student_level: str = "beginner"
        self.prerequisites: list[dict[str, Any]] = []
        self.resources: list[dict[str, Any]] = []


class RAGService:
    """
    Main RAG service.

    Its role: fetch ALL the necessary information
    in Neo4j and PostgreSQL to build a rich context
    that we inject into the LLM's prompt.
    """

    # ----------------------------------------------------------
    # METHOD 1: Find the concept related to the question
    # ----------------------------------------------------------
    def find_concept(self, query: str, lang: str = "en") -> dict[str, Any] | None:
        """
        Find the Neo4j concept that matches the student's question.

        How does it work?
        We search the names and descriptions of the Neo4j concepts
        for a matching word from the question.

        Example:
        - Question: "How does Lagrange work?"
        - We search "lagrange" in the concept names
        - We find: concept_lagrange (Lagrange Interpolation)

        Parameters:
            query: the student's question (e.g. "Explain Euler's method")

        Returns:
            A dictionary with the found concept's info, or None
        """
        lang = _normalize_lang(lang)

        # Tokenize the question: "Explique-moi la methode de Newton pour
        # resoudre f(x)=0" -> {"explique", "methode", "newton", "resoudre"}
        query_tokens = _tokenize(query)

        # Detect whether the question is about SOLVING EQUATIONS (Module 4)
        # If so, we boost the root-finding concepts to avoid a
        # weak match toward Newton interpolation winning by default.
        has_root_finding_intent = bool(query_tokens & _ROOT_FINDING_KEYWORDS)

        # Cypher query: all the concepts with their module and name in
        # all languages (we score on FR + EN so a word like "Newton"
        # matches even if the user is in FR).
        result = neo4j_conn.run_query(
            """
            MATCH (m:Module)-[:COVERS]->(c:Concept)
            RETURN c.id AS id,
                   CASE WHEN $lang = 'fr' THEN coalesce(c.name_fr, c.name) ELSE c.name END AS name,
                   c.name AS name_default,
                   coalesce(c.name_fr, '') AS name_fr,
                   c.name AS name_en,
                   CASE WHEN $lang = 'fr' THEN coalesce(c.description_fr, c.description) ELSE c.description END AS description,
                   coalesce(c.description_fr, '') AS description_fr,
                   coalesce(c.description, '') AS description_en,
                   c.difficulty AS difficulty,
                   CASE WHEN $lang = 'fr' THEN coalesce(m.name_fr, m.name) ELSE m.name END AS module_name,
                   m.id AS module_id
            """,
            {"lang": lang}
        )

        # Materialize once so we can iterate twice (semantic + keyword).
        concepts = list(result)

        # ----------------------------------------------------------
        # SEMANTIC SEARCH (Brique IA 2) — match by MEANING, not words
        # ----------------------------------------------------------
        # We embed the question and each concept (name + description,
        # FR+EN) and pick the closest by cosine similarity. This catches
        # paraphrases the keyword scoring misses, e.g.
        #   "where does the curve cross zero?" -> Bisection / Newton-Raphson.
        # If embeddings are unavailable, or the best match is too weak, we
        # fall through to the keyword scoring below (graceful degradation).
        if embedding_service.is_available() and concepts:
            # When the question is clearly about solving equations, restrict
            # the candidates to the root-finding concepts so the domain
            # heuristic is preserved even with semantic search.
            if has_root_finding_intent:
                pool = [c for c in concepts if c.get("id") in _ROOT_FINDING_CONCEPTS] or concepts
            else:
                pool = concepts

            by_id = {c["id"]: c for c in pool}
            candidates = [
                (
                    c["id"],
                    " ".join(
                        s for s in (
                            c.get("name_en", ""),
                            c.get("name_fr", ""),
                            c.get("description_en", ""),
                            c.get("description_fr", ""),
                        ) if s
                    ),
                )
                for c in pool
            ]
            match = embedding_service.best_match(query, candidates)
            if match is not None and match[1] >= _SEMANTIC_MIN_SIM:
                best = by_id[match[0]]
                logger.info(
                    "Concept trouve (semantique) : %s (similarite: %.3f, "
                    "root_finding_intent=%s)",
                    best["name"], match[1], has_root_finding_intent,
                )
                return best
            logger.info(
                "Semantique trop faible (sim=%.3f) -> repli mots-cles",
                match[1] if match else -1.0,
            )

        # ----------------------------------------------------------
        # KEYWORD SEARCH (fallback) — shared-word scoring
        # ----------------------------------------------------------
        best_match = None
        best_score = 0

        for concept in concepts:
            # Name tokens (FR + EN) — we add everything together so as not to
            # miss a keyword that a FR user would use in EN or vice versa.
            name_tokens = (
                _tokenize(concept.get("name", ""))
                | _tokenize(concept.get("name_fr", ""))
                | _tokenize(concept.get("name_en", ""))
            )
            desc_tokens = (
                _tokenize(concept.get("description", ""))
                | _tokenize(concept.get("description_fr", ""))
                | _tokenize(concept.get("description_en", ""))
            )

            score = 0
            # Strong match on the name tokens (weight x4)
            score += 4 * len(query_tokens & name_tokens)
            # Weak match on the description tokens (weight x1)
            score += 1 * len(query_tokens & desc_tokens)

            # Root-finding bonus: if the question is about "resoudre",
            # "racine", "raphson" etc., we strongly boost the Module 4
            # concepts to make them win against Newton interpolation.
            if has_root_finding_intent and concept.get("id") in _ROOT_FINDING_CONCEPTS:
                score += 8

            # Penalty: if the question is NOT about root-finding and
            # we are on a root-finding concept, we do not penalize.
            # (the concepts exist for good reasons)

            if score > best_score:
                best_score = score
                best_match = concept

        if best_match:
            logger.info(
                "Concept trouve : %s (score: %d, root_finding_intent=%s)",
                best_match["name"], best_score, has_root_finding_intent,
            )
        else:
            logger.warning(f"Aucun concept trouvé pour la question : {query[:50]}...")

        return best_match

    # ----------------------------------------------------------
    # METHOD 2: Retrieve the concept's prerequisites
    # ----------------------------------------------------------
    def get_prerequisites(
        self, concept_id: str, depth: int = None, lang: str = "en"
    ) -> list[dict[str, Any]]:
        """
        Retrieve a concept's prerequisites by walking up the Neo4j tree.

        What is a prerequisite?
        To understand "Runge-Kutta (RK4)", you must first understand
        "Improved Euler", which itself requires "Euler",
        which requires "Taylor Series" and "Initial Value Problems".

        In Neo4j, these links are modeled by the REQUIRES relationship:
            RK4 -[REQUIRES]-> Improved Euler -[REQUIRES]-> Euler

        The "depth" parameter says how far up to walk.
        depth=1: only the direct prerequisites
        depth=3: we walk up 3 levels (recommended)

        Parameters:
            concept_id: the concept ID (e.g. "concept_rk4")
            depth: number of levels to walk up (default: config)

        Returns:
            List of prerequisites with their name and difficulty
        """
        if depth is None:
            depth = settings.RAG_PREREQUISITE_DEPTH
        lang = _normalize_lang(lang)

        # Cypher query with variable depth + localized fields.
        result = neo4j_conn.run_query(
            f"""
            MATCH (c:Concept {{id: $concept_id}})-[:REQUIRES*1..{depth}]->(prereq:Concept)
            RETURN DISTINCT prereq.id AS id,
                   CASE WHEN $lang = 'fr' THEN coalesce(prereq.name_fr, prereq.name) ELSE prereq.name END AS name,
                   prereq.difficulty AS difficulty,
                   CASE WHEN $lang = 'fr' THEN coalesce(prereq.description_fr, prereq.description) ELSE prereq.description END AS description
            ORDER BY prereq.difficulty
            """,
            {"concept_id": concept_id, "lang": lang}
        )

        logger.info(f"Trouvé {len(result)} prérequis pour {concept_id}")
        return result

    # ----------------------------------------------------------
    # METHOD 3: Retrieve the remediation resources
    # ----------------------------------------------------------
    def get_resources(self, concept_id: str, lang: str = "en") -> list[dict[str, Any]]:
        """
        Retrieve the pedagogical resources linked to a concept.

        In Neo4j, each concept can have remediation resources:
            Concept -[REMEDIATES_TO]-> Resource

        These are videos, exercises, tutorials we can suggest
        to the student if they struggle with a concept.

        Parameters:
            concept_id: the concept ID (e.g. "concept_euler")

        Returns:
            List of resources with title, type and URL
        """
        lang = _normalize_lang(lang)
        result = neo4j_conn.run_query(
            """
            MATCH (c:Concept {id: $concept_id})-[:REMEDIATES_TO]->(r:Resource)
            RETURN r.id AS id,
                   CASE WHEN $lang = 'fr' THEN coalesce(r.name_fr, r.name) ELSE r.name END AS title,
                   r.type AS type,
                   r.url AS url
            """,
            {"concept_id": concept_id, "lang": lang}
        )

        logger.info(f"Trouve {len(result)} ressources pour {concept_id}")
        return result

    # ----------------------------------------------------------
    # METHOD 4: Retrieve the student's mastery
    # ----------------------------------------------------------
    def get_student_mastery(
        self, db: Session, etudiant_id: int, concept_id: str
    ) -> float:
        """
        Retrieve a student's mastery level on a concept.

        The mastery is stored in PostgreSQL (table concept_mastery)
        and ranges from 0 to 100:
        - 0% = the student has never seen this concept
        - 30% = beginner, needs simple explanations
        - 70% = competent, can receive standard explanations
        - 90% = expert, can receive rigorous proofs

        Parameters:
            db: SQLAlchemy session (PostgreSQL connection)
            etudiant_id: the student's ID
            concept_id: the Neo4j concept's ID

        Returns:
            A float between 0 and 100 (0 if no data)
        """
        mastery = db.query(ConceptMastery).filter(
            ConceptMastery.etudiant_id == etudiant_id,
            ConceptMastery.concept_neo4j_id == concept_id
        ).first()

        if mastery:
            return mastery.niveau_maitrise
        return 0.0

    # ----------------------------------------------------------
    # METHOD 5: Retrieve the mastery on the prerequisites
    # ----------------------------------------------------------
    def get_prerequisites_with_mastery(
        self, db: Session, etudiant_id: int, concept_id: str, lang: str = "en"
    ) -> list[dict[str, Any]]:
        """
        Retrieve the prerequisites WITH the student's mastery level
        on each of them.

        This is crucial for the AI tutor: if the student asks a question
        about Simpson but only has 20% on Trapezoidal (prerequisite),
        the tutor must first help them with Trapezoidal.

        Returns a list like:
        [
            {"name": "Trapezoidal Rule", "mastery": 20.0, "status": "weak"},
            {"name": "Definite Integrals", "mastery": 85.0, "status": "mastered"}
        ]
        """
        prerequisites = self.get_prerequisites(concept_id, lang=lang)
        result = []

        for prereq in prerequisites:
            mastery = self.get_student_mastery(db, etudiant_id, prereq["id"])

            # Determine the status
            if mastery >= settings.MASTERY_THRESHOLD:
                status = "mastered"       # Mastered
            elif mastery > 0:
                status = "in_progress"    # In progress
            else:
                status = "not_started"    # Not started

            result.append({
                "id": prereq["id"],
                "name": prereq["name"],
                "difficulty": prereq.get("difficulty", "unknown"),
                "mastery": mastery,
                "status": status
            })

        return result

    # ----------------------------------------------------------
    # MAIN METHOD: Build the complete context
    # ----------------------------------------------------------
    def build_context(
        self, db: Session, etudiant_id: int, question: str,
        concept_id: str = None, lang: str = "en"
    ) -> ConceptContext:
        """
        Main method — Builds the COMPLETE context for the AI tutor.

        This is the method called by the /tutor/ask router.
        It orchestrates all the other methods to create a complete
        "file" that we will send to the LLM.

        Flow:
        1. Find the concept (either provided, or guessed from the question)
        2. Retrieve the student's mastery
        3. Retrieve the prerequisites with their mastery
        4. Retrieve the remediation resources
        5. Wrap everything in a ConceptContext object

        Parameters:
            db: PostgreSQL session
            etudiant_id: the connected student's ID
            question: the question asked by the student
            concept_id: (optional) if the student chose a specific concept

        Returns:
            A ConceptContext filled with all the info
        """
        context = ConceptContext()
        lang = _normalize_lang(lang)

        # --- Step 1: Find the concept ---
        if concept_id:
            # The student chose a specific concept in the interface
            concept = neo4j_conn.run_query(
                """
                MATCH (m:Module)-[:COVERS]->(c:Concept {id: $concept_id})
                RETURN c.id AS id,
                       CASE WHEN $lang = 'fr' THEN coalesce(c.name_fr, c.name) ELSE c.name END AS name,
                       CASE WHEN $lang = 'fr' THEN coalesce(c.description_fr, c.description) ELSE c.description END AS description,
                       c.difficulty AS difficulty,
                       CASE WHEN $lang = 'fr' THEN coalesce(m.name_fr, m.name) ELSE m.name END AS module_name
                """,
                {"concept_id": concept_id, "lang": lang}
            )
            concept = concept[0] if concept else None
        else:
            # We guess the concept from the question
            concept = self.find_concept(question, lang=lang)

        if not concept:
            # No concept found -> empty context, the LLM will answer
            # in a general way about numerical analysis.
            logger.warning("Aucun concept identifie, contexte vide")
            context.concept_name = (
                "Analyse Numerique (general)" if lang == "fr" else "Numerical Analysis (general)"
            )
            return context

        # --- Step 2: Fill in the concept info ---
        context.concept_id = concept["id"]
        context.concept_name = concept["name"]
        context.description = concept.get("description", "")
        context.difficulty = concept.get("difficulty", "intermediate")
        context.module_name = concept.get("module_name", "")

        # --- Step 3: Student's mastery (on this concept) ---
        context.student_mastery = self.get_student_mastery(
            db, etudiant_id, concept["id"]
        )

        # --- Step 3 bis: Student's GLOBAL level (niveau_actuel) ---
        # Drives the adaptation by overall level rather than per concept.
        from app.models.etudiant import Etudiant
        _student = db.query(Etudiant).filter(Etudiant.id == etudiant_id).first()
        context.student_level = (getattr(_student, "niveau_actuel", None) or "beginner").lower()

        # --- Step 4: Prerequisites with mastery ---
        context.prerequisites = self.get_prerequisites_with_mastery(
            db, etudiant_id, concept["id"], lang=lang
        )

        # --- Step 5: Remediation resources ---
        context.resources = self.get_resources(concept["id"], lang=lang)

        logger.info(
            f"Contexte construit : concept={context.concept_name}, "
            f"maîtrise={context.student_mastery}%, "
            f"prérequis={len(context.prerequisites)}, "
            f"ressources={len(context.resources)}"
        )

        return context


# Global instance (reused everywhere in the application)
rag_service = RAGService()
