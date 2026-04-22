# ============================================================
# Service RAG — Retrieval-Augmented Generation
# ============================================================
# C'est quoi ce fichier ?
#
# C'est le "cerveau" qui va CHERCHER les informations pertinentes
# AVANT de poser la question à l'IA (Gemini).
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
    qu'on injectera dans le prompt de Gemini.
    """

    # ----------------------------------------------------------
    # MÉTHODE 1 : Trouver le concept lié à la question
    # ----------------------------------------------------------
    def find_concept(self, query: str) -> dict[str, Any] | None:
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
        # On met la question en minuscules pour comparer sans souci de casse
        query_lower = query.lower()

        # Requête Cypher : on récupère TOUS les concepts avec leur module
        # MATCH = "trouve-moi"
        # (m:Module)-[:COVERS]->(c:Concept) = un Module qui COUVRE un Concept
        # RETURN = "retourne-moi ces infos"
        result = neo4j_conn.run_query(
            """
            MATCH (m:Module)-[:COVERS]->(c:Concept)
            RETURN c.id AS id, c.name AS name, c.description AS description,
                   c.difficulty AS difficulty, m.name AS module_name
            """
        )

        # On cherche le concept dont le nom ou la description contient
        # un mot de la question de l'étudiant
        best_match = None
        best_score = 0

        for concept in result:
            score = 0
            concept_name = (concept.get("name") or "").lower()
            concept_desc = (concept.get("description") or "").lower()

            # On découpe le nom du concept en mots
            # Ex: "Lagrange Interpolation" → ["lagrange", "interpolation"]
            for word in concept_name.split():
                if word in query_lower:
                    score += 2  # Le nom est plus important que la description

            for word in concept_desc.split():
                if len(word) > 4 and word in query_lower:  # Ignore les petits mots
                    score += 1

            # On garde le concept avec le meilleur score
            if score > best_score:
                best_score = score
                best_match = concept

        if best_match:
            logger.info(f"Concept trouvé : {best_match['name']} (score: {best_score})")
        else:
            logger.warning(f"Aucun concept trouvé pour la question : {query[:50]}...")

        return best_match

    # ----------------------------------------------------------
    # MÉTHODE 2 : Récupérer les prérequis du concept
    # ----------------------------------------------------------
    def get_prerequisites(
        self, concept_id: str, depth: int = None
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

        # Requête Cypher avec profondeur variable
        # *1..{depth} signifie : suivre la relation REQUIRES
        # entre 1 et {depth} fois (récursivement)
        #
        # Exemple avec depth=3 et concept_rk4 :
        #   concept_rk4 → improved_euler (niveau 1)
        #   concept_rk4 → euler (niveau 2, via improved_euler)
        #   concept_rk4 → taylor_series (niveau 3, via euler)
        result = neo4j_conn.run_query(
            f"""
            MATCH (c:Concept {{id: $concept_id}})-[:REQUIRES*1..{depth}]->(prereq:Concept)
            RETURN DISTINCT prereq.id AS id, prereq.name AS name,
                   prereq.difficulty AS difficulty,
                   prereq.description AS description
            ORDER BY prereq.difficulty
            """,
            {"concept_id": concept_id}
        )

        logger.info(f"Trouvé {len(result)} prérequis pour {concept_id}")
        return result

    # ----------------------------------------------------------
    # MÉTHODE 3 : Récupérer les ressources de remédiation
    # ----------------------------------------------------------
    def get_resources(self, concept_id: str) -> list[dict[str, Any]]:
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
        result = neo4j_conn.run_query(
            """
            MATCH (c:Concept {id: $concept_id})-[:REMEDIATES_TO]->(r:Resource)
            RETURN r.id AS id, r.name AS title, r.type AS type, r.url AS url
            """,
            {"concept_id": concept_id}
        )

        logger.info(f"Trouvé {len(result)} ressources pour {concept_id}")
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
        self, db: Session, etudiant_id: int, concept_id: str
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
        prerequisites = self.get_prerequisites(concept_id)
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
        concept_id: str = None
    ) -> ConceptContext:
        """
        Méthode principale — Construit le contexte COMPLET pour le tuteur IA.

        C'est cette méthode qui est appelée par le router /tutor/ask.
        Elle orchestre toutes les autres méthodes pour créer un "dossier"
        complet qu'on enverra à Gemini.

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

        # --- Étape 1 : Trouver le concept ---
        if concept_id:
            # L'étudiant a choisi un concept précis dans l'interface
            concept = neo4j_conn.run_query(
                """
                MATCH (m:Module)-[:COVERS]->(c:Concept {id: $concept_id})
                RETURN c.id AS id, c.name AS name, c.description AS description,
                       c.difficulty AS difficulty, m.name AS module_name
                """,
                {"concept_id": concept_id}
            )
            concept = concept[0] if concept else None
        else:
            # On devine le concept depuis la question
            concept = self.find_concept(question)

        if not concept:
            # Aucun concept trouvé → contexte vide, Gemini répondra
            # de manière générale sur l'analyse numérique
            logger.warning("Aucun concept identifié, contexte vide")
            context.concept_name = "Analyse Numérique (général)"
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
            db, etudiant_id, concept["id"]
        )

        # --- Étape 5 : Ressources de remédiation ---
        context.resources = self.get_resources(concept["id"])

        logger.info(
            f"Contexte construit : concept={context.concept_name}, "
            f"maîtrise={context.student_mastery}%, "
            f"prérequis={len(context.prerequisites)}, "
            f"ressources={len(context.resources)}"
        )

        return context


# Instance globale (réutilisée partout dans l'application)
rag_service = RAGService()
