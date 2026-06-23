import logging
from typing import Any

from sqlalchemy.orm import Session

from app.graph.neo4j_connection import Neo4jConnection

logger = logging.getLogger(__name__)


class GraphService:
    """
    Service for managing knowledge graph operations with Neo4j.
    Handles concept retrieval, prerequisites, learning paths, and remediation.
    """

    def __init__(self, neo4j: Neo4jConnection, db: Session | None = None):
        """
        Initialize the service.

        Args:
            neo4j: Neo4j connection instance
            db: Optional SQLAlchemy database session
        """
        self.neo4j = neo4j
        self.db = db

    def get_all_concepts(self) -> list[dict[str, Any]]:
        """
        Retrieve all concepts from the knowledge graph.

        Returns:
            List of concept nodes with properties
        """
        query = """
        MATCH (c:Concept)
        RETURN c.id as id, c.name as name, c.description as description,
               c.level as level, c.category as category
        ORDER BY c.level, c.name
        """

        results = self.neo4j.run_query(query)
        return results

    def get_prerequisites(self, concept_id: str) -> list[dict[str, Any]]:
        """
        Get all prerequisite concepts for a given concept.

        Args:
            concept_id: The concept ID to find prerequisites for

        Returns:
            List of prerequisite concepts
        """
        query = """
        MATCH (c:Concept {id: $concept_id})<-[:PREREQUISITE]-(p:Concept)
        RETURN p.id as id, p.name as name, p.description as description,
               p.level as level
        ORDER BY p.level
        """

        results = self.neo4j.run_query(query, {"concept_id": concept_id})
        return results

    def generate_learning_path(self, etudiant_id: int, lang: str = "en") -> dict[str, Any] | None:
        """DEPRECATED (05/12/2026) — delegates to services.path_service.generate_learning_path.

        This method was DEAD CODE (zero callers in the repo, verified by
        the audit of 05/12/2026). We keep the signature so as not to break a
        potential external caller or legacy test, but all the logic is
        centralized in path_service. See docs/AUDIT_SENIOR_12mai2026.md.
        """
        if not self.db:
            return None
        from app.services.path_service import generate_learning_path
        return generate_learning_path(self.db, etudiant_id, lang)

    def get_remediation(self, concept_id: str) -> list[dict[str, Any]]:
        """
        Get remediation resources for a concept.

        Args:
            concept_id: The concept ID to find remediation for

        Returns:
            List of remediation resources (videos, articles, practice problems)
        """
        query = """
        MATCH (c:Concept {id: $concept_id})-[:HAS_RESOURCE]->(r:Resource)
        RETURN r.id as id, r.title as title, r.type as type,
               r.url as url, r.difficulty as difficulty
        ORDER BY r.difficulty
        """

        results = self.neo4j.run_query(query, {"concept_id": concept_id})
        return results

    def add_concept_to_graph(self, concept_data: dict[str, Any]) -> bool:
        """
        Add a new concept to the knowledge graph.

        Args:
            concept_data: Dictionary containing concept properties
                         (id, name, description, level, category)

        Returns:
            True if successful, False otherwise
        """
        query = """
        CREATE (c:Concept {
            id: $id,
            name: $name,
            description: $description,
            level: $level,
            category: $category
        })
        RETURN c.id as id
        """

        try:
            self.neo4j.run_write_query(query, concept_data)
            return True
        except Exception as e:
            logger.error("Error adding concept: %s", e)
            return False

    def add_prerequisite_relationship(self, concept_id: str, prerequisite_id: str) -> bool:
        """
        Add a prerequisite relationship between two concepts.

        Args:
            concept_id: The concept that has a prerequisite
            prerequisite_id: The prerequisite concept

        Returns:
            True if successful, False otherwise
        """
        query = """
        MATCH (c:Concept {id: $concept_id}), (p:Concept {id: $prerequisite_id})
        CREATE (c)<-[:PREREQUISITE]-(p)
        """

        try:
            self.neo4j.run_write_query(
                query,
                {"concept_id": concept_id, "prerequisite_id": prerequisite_id}
            )
            return True
        except Exception as e:
            logger.error("Error adding prerequisite: %s", e)
            return False
