# ============================================================
# Service RAG — Retrieval-Augmented Generation
# ============================================================
# C'est quoi ce fichier ?
#
# C'est le "cerveau" qui va CHERCHER les informations pertinentes
# AVANT de poser la question à l'IA (le LLM).
#
# Sans RAG : "Explique Lagrange" → réponse générique
# Avec RAG : "Explique Lagrange" → on regarde d'abord :
#   - Les prérequis de Lagrange dans Neo4j
#   - Le niveau de maîtrise de l'étudiant dans PostgreSQL
#   - Les ressources disponibles pour ce concept
#   → réponse PERSONNALISÉE au niveau de l'étudiant
#
# C'est ça le "Graph" dans "GraphRAG" : on utilise le GRAPHE
# de connaissances Neo4j pour enrichir les réponses de l'IA.
# ============================================================

import logging
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.graph.neo4j_connection import neo4j_conn
from app.models.mastery import ConceptMastery

logger = logging.getLogger(__name__)
settings = get_settings()


def _normalize_lang(lang: str | None) -> str:
    """Limite a 'fr' ou 'en'. Defaut 'en'."""
    return "fr" if (lang or "").lower() == "fr" else "en"


import re as _re

# Tokens trop courts ou trop generiques qu'on ignore dans le scoring du RAG
# (sinon "de", "la", "the" matchent partout et faussent le score).
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

# Mots-cles forts qui indiquent une question sur la **resolution
# d'equations non-lineaires** (Module 4). Quand on les detecte, on
# booste les concepts du Module 4 pour eviter qu'un match faible
# vers Newton interpolation gagne par defaut.
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
    """Tokenize une chaine en mots minuscules, decoupant sur espaces,
    tirets, ponctuation et apostrophes. Filtre les stop-words et les
    tokens de moins de 3 caracteres.

    Exemples :
      "Newton-Raphson Method"   -> {"newton", "raphson", "method"}
      "Methode de Newton"       -> {"methode", "newton"}
      "f(x)=0"                  -> set() (trop court)
    """
    if not text:
        return set()
    # split sur tout caractere non-alphanumerique (gere FR/EN)
    raw = _re.split(r"[^a-zA-Z0-9À-ſ]+", text.lower())
    return {t for t in raw if len(t) >= 3 and t not in _STOP_WORDS}


class ConceptContext:
    """
    Contient TOUT le contexte d'un concept pour un étudiant donné.

    C'est comme un "dossier" qu'on prépare avant d'appeler l'IA.
    Il contient :
    - Les infos du concept (nom, description, difficulté)
    - Le niveau de maîtrise de l'étudiant sur ce concept
    - Les prérequis (ce que l'étudiant doit savoir avant)
    - La maîtrise de l'étudiant sur chaque prérequis
    - Les ressources de remédiation disponibles
    """

    def __init__(self):
        self.concept_id: str = ""
        self.concept_name: str = ""
        self.description: str = ""
        self.difficulty: str = ""
        self.module_name: str = ""
        self.student_mastery: float = 0.0
        self.prerequisites: list[dict[str, Any]] = []
        self.resources: list[dict[str, Any]] = []


class RAGService:
    """
    Service principal du RAG.

    Son rôle : aller chercher TOUTES les informations nécessaires
    dans Neo4j et PostgreSQL pour construire un contexte riche
    qu'on injectera dans le prompt de le LLM.
    """

    # ----------------------------------------------------------
    # MÉTHODE 1 : Trouver le concept lié à la question
    # ----------------------------------------------------------
    def find_concept(self, query: str, lang: str = "en") -> dict[str, Any] | None:
        """
        Trouve le concept Neo4j qui correspond à la question de l'étudiant.

        Comment ça marche ?
        On cherche dans les noms et descriptions des concepts Neo4j
        si un mot de la question correspond.

        Exemple :
        - Question : "Comment fonctionne Lagrange ?"
        - On cherche "lagrange" dans les noms des concepts
        - On trouve : concept_lagrange (Lagrange Interpolation)

        Paramètres :
            query : la question de l'étudiant (ex: "Explique la méthode d'Euler")

        Retourne :
            Un dictionnaire avec les infos du concept trouvé, ou None
        """
        lang = _normalize_lang(lang)

        # Tokenize la question : "Explique-moi la methode de Newton pour
        # resoudre f(x)=0" -> {"explique", "methode", "newton", "resoudre"}
        query_tokens = _tokenize(query)

        # Detecte si la question parle de RESOLUTION D'EQUATIONS (Module 4)
        # Si oui, on bonifie les concepts root-finding pour eviter qu'un
        # match faible vers Newton interpolation gagne par defaut.
        has_root_finding_intent = bool(query_tokens & _ROOT_FINDING_KEYWORDS)

        # Requête Cypher : tous les concepts avec leur module et nom dans
        # toutes les langues (on score sur FR + EN pour qu'un mot "Newton"
        # match meme si l'utilisateur est en FR).
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

        best_match = None
        best_score = 0

        for concept in result:
            # Tokens du nom (FR + EN) — on additionne tout pour ne pas
            # rater un mot-cle qu'un utilisateur FR utiliserait en EN ou vice-versa.
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
            # Match fort sur les tokens du nom (poids x4)
            score += 4 * len(query_tokens & name_tokens)
            # Match faible sur les tokens de la description (poids x1)
            score += 1 * len(query_tokens & desc_tokens)

            # Bonus root-finding : si la question parle de "resoudre",
            # "racine", "raphson" etc., on booste fortement les concepts
            # du Module 4 pour les faire gagner contre Newton interpolation.
            if has_root_finding_intent and concept.get("id") in _ROOT_FINDING_CONCEPTS:
                score += 8

            # Penalite : si la question NE parle PAS de root-finding et
            # qu'on est sur un concept root-finding, on ne penalise pas.
            # (les concepts existent pour de bonnes raisons)

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
    # MÉTHODE 2 : Récupérer les prérequis du concept
    # ----------------------------------------------------------
    def get_prerequisites(
        self, concept_id: str, depth: int = None, lang: str = "en"
    ) -> list[dict[str, Any]]:
        """
        Récupère les prérequis d'un concept en remontant l'arbre Neo4j.

        C'est quoi un prérequis ?
        Pour comprendre "Runge-Kutta (RK4)", il faut d'abord comprendre
        "Improved Euler", qui lui-même nécessite "Euler",
        qui nécessite "Taylor Series" et "Initial Value Problems".

        Dans Neo4j, ces liens sont modélisés par la relation REQUIRES :
            RK4 -[REQUIRES]-> Improved Euler -[REQUIRES]-> Euler

        Le paramètre "depth" dit jusqu'où remonter.
        depth=1 : seulement les prérequis directs
        depth=3 : on remonte 3 niveaux (recommandé)

        Paramètres :
            concept_id : l'ID du concept (ex: "concept_rk4")
            depth : nombre de niveaux à remonter (défaut: config)

        Retourne :
            Liste de prérequis avec leur nom et difficulté
        """
        if depth is None:
            depth = settings.RAG_PREREQUISITE_DEPTH
        lang = _normalize_lang(lang)

        # Requête Cypher avec profondeur variable + champs localises.
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
    # MÉTHODE 3 : Récupérer les ressources de remédiation
    # ----------------------------------------------------------
    def get_resources(self, concept_id: str, lang: str = "en") -> list[dict[str, Any]]:
        """
        Récupère les ressources pédagogiques liées à un concept.

        Dans Neo4j, chaque concept peut avoir des ressources de remédiation :
            Concept -[REMEDIATES_TO]-> Resource

        Ce sont des vidéos, exercices, tutoriels qu'on peut suggérer
        à l'étudiant s'il a du mal avec un concept.

        Paramètres :
            concept_id : l'ID du concept (ex: "concept_euler")

        Retourne :
            Liste de ressources avec titre, type et URL
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
    # MÉTHODE 4 : Récupérer la maîtrise de l'étudiant
    # ----------------------------------------------------------
    def get_student_mastery(
        self, db: Session, etudiant_id: int, concept_id: str
    ) -> float:
        """
        Récupère le niveau de maîtrise d'un étudiant sur un concept.

        La maîtrise est stockée dans PostgreSQL (table concept_mastery)
        et va de 0 à 100 :
        - 0% = l'étudiant n'a jamais vu ce concept
        - 30% = débutant, a besoin d'explications simples
        - 70% = compétent, peut recevoir des explications standard
        - 90% = expert, peut recevoir des preuves rigoureuses

        Paramètres :
            db : session SQLAlchemy (connexion PostgreSQL)
            etudiant_id : l'ID de l'étudiant
            concept_id : l'ID du concept Neo4j

        Retourne :
            Un float entre 0 et 100 (0 si pas de donnée)
        """
        mastery = db.query(ConceptMastery).filter(
            ConceptMastery.etudiant_id == etudiant_id,
            ConceptMastery.concept_neo4j_id == concept_id
        ).first()

        if mastery:
            return mastery.niveau_maitrise
        return 0.0

    # ----------------------------------------------------------
    # MÉTHODE 5 : Récupérer la maîtrise sur les prérequis
    # ----------------------------------------------------------
    def get_prerequisites_with_mastery(
        self, db: Session, etudiant_id: int, concept_id: str, lang: str = "en"
    ) -> list[dict[str, Any]]:
        """
        Récupère les prérequis AVEC le niveau de maîtrise de l'étudiant
        sur chacun d'eux.

        C'est crucial pour le tuteur IA : si l'étudiant demande une question
        sur Simpson mais n'a que 20% sur Trapezoidal (prérequis),
        le tuteur doit d'abord l'aider avec Trapezoidal.

        Retourne une liste comme :
        [
            {"name": "Trapezoidal Rule", "mastery": 20.0, "status": "weak"},
            {"name": "Definite Integrals", "mastery": 85.0, "status": "mastered"}
        ]
        """
        prerequisites = self.get_prerequisites(concept_id, lang=lang)
        result = []

        for prereq in prerequisites:
            mastery = self.get_student_mastery(db, etudiant_id, prereq["id"])

            # Déterminer le statut
            if mastery >= settings.MASTERY_THRESHOLD:
                status = "mastered"       # ✅ Maîtrisé
            elif mastery > 0:
                status = "in_progress"    # 🔄 En cours
            else:
                status = "not_started"    # ❌ Pas commencé

            result.append({
                "id": prereq["id"],
                "name": prereq["name"],
                "difficulty": prereq.get("difficulty", "unknown"),
                "mastery": mastery,
                "status": status
            })

        return result

    # ----------------------------------------------------------
    # MÉTHODE PRINCIPALE : Construire le contexte complet
    # ----------------------------------------------------------
    def build_context(
        self, db: Session, etudiant_id: int, question: str,
        concept_id: str = None, lang: str = "en"
    ) -> ConceptContext:
        """
        Méthode principale — Construit le contexte COMPLET pour le tuteur IA.

        C'est cette méthode qui est appelée par le router /tutor/ask.
        Elle orchestre toutes les autres méthodes pour créer un "dossier"
        complet qu'on enverra à le LLM.

        Flux :
        1. Trouver le concept (soit fourni, soit deviné depuis la question)
        2. Récupérer la maîtrise de l'étudiant
        3. Récupérer les prérequis avec leur maîtrise
        4. Récupérer les ressources de remédiation
        5. Tout emballer dans un objet ConceptContext

        Paramètres :
            db : session PostgreSQL
            etudiant_id : l'ID de l'étudiant connecté
            question : la question posée par l'étudiant
            concept_id : (optionnel) si l'étudiant a choisi un concept précis

        Retourne :
            Un ConceptContext rempli avec toutes les infos
        """
        context = ConceptContext()
        lang = _normalize_lang(lang)

        # --- Étape 1 : Trouver le concept ---
        if concept_id:
            # L'etudiant a choisi un concept precis dans l'interface
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
            # On devine le concept depuis la question
            concept = self.find_concept(question, lang=lang)

        if not concept:
            # Aucun concept trouve -> contexte vide, le LLM repondra
            # de maniere generale sur l'analyse numerique.
            logger.warning("Aucun concept identifie, contexte vide")
            context.concept_name = (
                "Analyse Numerique (general)" if lang == "fr" else "Numerical Analysis (general)"
            )
            return context

        # --- Étape 2 : Remplir les infos du concept ---
        context.concept_id = concept["id"]
        context.concept_name = concept["name"]
        context.description = concept.get("description", "")
        context.difficulty = concept.get("difficulty", "intermediate")
        context.module_name = concept.get("module_name", "")

        # --- Étape 3 : Maîtrise de l'étudiant ---
        context.student_mastery = self.get_student_mastery(
            db, etudiant_id, concept["id"]
        )

        # --- Étape 4 : Prérequis avec maîtrise ---
        context.prerequisites = self.get_prerequisites_with_mastery(
            db, etudiant_id, concept["id"], lang=lang
        )

        # --- Étape 5 : Ressources de remédiation ---
        context.resources = self.get_resources(concept["id"], lang=lang)

        logger.info(
            f"Contexte construit : concept={context.concept_name}, "
            f"maîtrise={context.student_mastery}%, "
            f"prérequis={len(context.prerequisites)}, "
            f"ressources={len(context.resources)}"
        )

        return context


# Instance globale (réutilisée partout dans l'application)
rag_service = RAGService()
