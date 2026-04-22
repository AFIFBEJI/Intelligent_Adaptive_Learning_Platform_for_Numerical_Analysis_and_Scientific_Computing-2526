"""
Integrity test for the Neo4j knowledge graph (V1 scope, April 21, 2026).

This test is executed by the `graph-integrity` job of the CI pipeline,
AFTER `scripts/seed_neo4j.py` has successfully populated a Neo4j service
container.  It guarantees that every time we merge to main, the graph
that the adaptive engine depends on has exactly the expected shape:

    3 Modules          (Interpolation, Integration, Approximation & Optim.)
    15 Concepts
    8  Resources
    ---
    15 COVERS          (Module -> Concept)
    14 REQUIRES        (Concept -> Concept), 3 of which are cross-module
    8  REMEDIATES_TO   (Concept -> Resource)
    ---
    37 relationships total

If any of these invariants breaks (e.g. somebody accidentally deletes a
Concept from seed_neo4j.py), the test fails and the PR is blocked.
"""
import os

import pytest
from neo4j import GraphDatabase


# ------------------------------------------------------------------
# Fixture: a Neo4j driver shared by every test in this module
# ------------------------------------------------------------------
@pytest.fixture(scope="module")
def driver():
    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "ci-password-123")
    drv = GraphDatabase.driver(uri, auth=(user, password))
    yield drv
    drv.close()


def _count(session, query: str) -> int:
    """Helper: run a COUNT Cypher query and return the first scalar."""
    result = session.run(query).single()
    return int(result[0]) if result else 0


# ------------------------------------------------------------------
# Node counts
# ------------------------------------------------------------------
def test_module_count(driver):
    with driver.session() as s:
        assert _count(s, "MATCH (m:Module) RETURN count(m)") == 3


def test_concept_count(driver):
    with driver.session() as s:
        assert _count(s, "MATCH (c:Concept) RETURN count(c)") == 15


def test_resource_count(driver):
    with driver.session() as s:
        assert _count(s, "MATCH (r:Resource) RETURN count(r)") == 8


# ------------------------------------------------------------------
# Relationship counts
# ------------------------------------------------------------------
def test_covers_count(driver):
    with driver.session() as s:
        assert _count(
            s, "MATCH (:Module)-[r:COVERS]->(:Concept) RETURN count(r)"
        ) == 15


def test_requires_count(driver):
    with driver.session() as s:
        assert _count(
            s, "MATCH (:Concept)-[r:REQUIRES]->(:Concept) RETURN count(r)"
        ) == 14


def test_remediates_count(driver):
    with driver.session() as s:
        assert _count(
            s,
            "MATCH (:Concept)-[r:REMEDIATES_TO]->(:Resource) RETURN count(r)",
        ) == 8


def test_total_relationship_count(driver):
    with driver.session() as s:
        assert _count(s, "MATCH ()-[r]->() RETURN count(r)") == 37


# ------------------------------------------------------------------
# Module 3 is "Polynomial Approximation & Optimization", NOT "ODEs"
# ------------------------------------------------------------------
def test_module3_is_approximation(driver):
    with driver.session() as s:
        row = s.run(
            "MATCH (m:Module {id:'module_approximation'}) RETURN m.name AS name"
        ).single()
        assert row is not None, "module_approximation is missing from the graph"
        assert row["name"] == "Polynomial Approximation & Optimization"


def test_no_ode_module_present(driver):
    """Make sure no ODE-related module id accidentally sneaks back in."""
    with driver.session() as s:
        forbidden_ids = [
            "module_odes",
            "module_ode",
            "module_euler",
        ]
        for forbidden in forbidden_ids:
            row = s.run(
                "MATCH (m:Module {id:$id}) RETURN count(m) AS n", id=forbidden
            ).single()
            assert row["n"] == 0, f"Forbidden legacy module still present: {forbidden}"


# ------------------------------------------------------------------
# Cross-module prerequisites (the 3 REQUIRES edges that bind Module 3
# to Modules 1 & 2) are non-negotiable for the adaptive engine.
# ------------------------------------------------------------------
def test_cross_module_requires_edges(driver):
    """Concepts from Module 3 must REQUIRE at least 3 concepts owned by
    another Module (Module 1 polynomial_basics and Module 2 trapezoidal).
    """
    with driver.session() as s:
        row = s.run(
            """
            MATCH (m3:Module {id:'module_approximation'})-[:COVERS]->(c3:Concept)
            MATCH (c3)-[:REQUIRES]->(c_pre:Concept)
            MATCH (m_other:Module)-[:COVERS]->(c_pre)
            WHERE m_other.id <> 'module_approximation'
            RETURN count(DISTINCT c_pre) AS prerequisites
            """
        ).single()
        assert row["prerequisites"] >= 3, (
            f"Expected >=3 cross-module prerequisites for Module 3, "
            f"got {row['prerequisites']}"
        )
