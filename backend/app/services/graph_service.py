import logging
from typing import Any

from sqlalchemy.orm import Session

from app.graph.neo4j_connection import Neo4jConnection
from app.models.mastery import ConceptMastery

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

    def generate_learning_path(self, etudiant_id: int) -> dict[str, Any] | None:
        """
        Generate a personalized learning path for a student based on their mastery levels.

        The algorithm:
        1. Get student's current mastery levels
        2. Find concepts with mastery < 70% (need improvement)
        3. Get next-level concepts (prerequisites met, not yet mastered)
        4. Recommend top 5 concepts by priority and difficulty

        Args:
            etudiant_id: The student ID

        Returns:
            Dictionary containing the learning path with recommendations
        """
        if not self.db:
            return None

        # Get student's current mastery data
        mastery_records = self.db.query(ConceptMastery).filter(
            ConceptMastery.etudiant_id == etudiant_id
        ).all()

        mastery_dict = {m.concept_neo4j_id: m.niveau_maitrise for m in mastery_records}

        # Get all concepts
        all_concepts = self.get_all_concepts()

        if not all_concepts:
            return None

        # Find concepts needing improvement and recommended next concepts
        concepts_to_improve = []
        next_recommended = []

        for concept in all_concepts:
            concept_id = concept.get("id")
            current_mastery = mastery_dict.get(concept_id, 0)

            if 0 < current_mastery < 70:
                concepts_to_improve.append({
                    "id": concept_id,
                    "name": concept.get("name"),
                    "mastery": current_mastery,
                    "status": "in_progress"
                })
            elif current_mastery == 0:
                # Check if prerequisites are met
                prerequisites = self.get_prerequisites(concept_id)
                prerequisites_met = True

                for prereq in prerequisites:
                    prereq_id = prereq.get("id")
                    prereq_mastery = mastery_dict.get(prereq_id, 0)
                    if prereq_mastery < 70:
                        prerequisites_met = False
                        break

                if prerequisites_met:
                    next_recommended.append({
                        "id": concept_id,
                        "name": concept.get("name"),
                        "level": concept.get("level"),
                        "category": concept.get("category"),
                        "difficulty": concept.get("level", "intermediate")
                    })

        return {
            "etudiant_id": etudiant_id,
            "concepts_to_improve": concepts_to_improve,
            "next_recommended": next_recommended[:5],  # Top 5 recommendations
            "overall_progress": {
                "total_concepts": len(all_concepts),
                "mastered": len([c for c in all_concepts if mastery_dict.get(c.get("id"), 0) >= 70]),
                "in_progress": len(concepts_to_improve)
            }
        }

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
