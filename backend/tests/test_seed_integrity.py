"""
Integrity test for the Neo4j knowledge graph (V1 + Module 4, May 2026).

This test is executed by the `graph-integrity` job of the CI pipeline,
AFTER `scripts/seed_neo4j.py` has successfully populated a Neo4j service
container.  It guarantees that every time we merge to main, the graph
that the adaptive engine depends on has exactly the expected shape:

    4  Modules     (Interpolation, Integration, Approximation & Optim.,
                    Solving Non-linear Equations)
    19 Concepts    (5 + 5 + 5 + 4)
    10 Resources
    ---
    19 COVERS          (Module -> Concept)
    20 REQUIRES        (Concept -> Concept), 3 cross-module M1<->M2<->M3
                       + 6 intra/cross-module for Module 4
    10 REMEDIATES_TO   (Concept -> Resource)
    ---
    49 relationships total

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
        assert _count(s, "MATCH (m:Module) RETURN count(m)") == 4


def test_concept_count(driver):
    with driver.session() as s:
        assert _count(s, "MATCH (c:Concept) RETURN count(c)") == 19


def test_resource_count(driver):
    with driver.session() as s:
        assert _count(s, "MATCH (r:Resource) RETURN count(r)") == 10


# ------------------------------------------------------------------
# Relationship counts
# ------------------------------------------------------------------
def test_covers_count(driver):
    with driver.session() as s:
        assert _count(
            s, "MATCH (:Module)-[r:COVERS]->(:Concept) RETURN count(r)"
        ) == 19


def test_requires_count(driver):
    with driver.session() as s:
        assert _count(
            s, "MATCH (:Concept)-[r:REQUIRES]->(:Concept) RETURN count(r)"
        ) == 20


def test_remediates_count(driver):
    with driver.session() as s:
        assert _count(
            s,
            "MATCH (:Concept)-[r:REMEDIATES_TO]->(:Resource) RETURN count(r)",
        ) == 10


def test_total_relationship_count(driver):
    """Verifie le nombre de relations CORE du graphe (COVERS + REQUIRES +
    REMEDIATES_TO = 49). On exclut volontairement HAS_CONTENT qui est
    ajoutee par les scripts seed_content_*.py au-dela du seed initial,
    et qui fait varier le total selon ce qui a ete charge en local.
    """
    with driver.session() as s:
        n = _count(
            s,
            "MATCH ()-[r:COVERS|REQUIRES|REMEDIATES_TO]->() RETURN count(r)",
        )
        assert n == 49, (
            f"Attendu 49 relations COVERS+REQUIRES+REMEDIATES_TO, trouve {n}. "
            "Si tu as ajoute/retire des concepts ou des prerequis dans "
            "seed_neo4j.py, mets a jour cette assertion."
        )


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
# Module 4 (Solving Non-linear Equations) is present with its 4 concepts
# ------------------------------------------------------------------
def test_module4_root_finding_present(driver):
    with driver.session() as s:
        row = s.run(
            "MATCH (m:Module {id:'module_root_finding'}) RETURN m.name AS name"
        ).single()
        assert row is not None, "module_root_finding is missing from the graph"
        assert row["name"] == "Solving Non-linear Equations"


def test_module4_has_4_concepts(driver):
    with driver.session() as s:
        n = _count(
            s,
            "MATCH (:Module {id:'module_root_finding'})-[:COVERS]->(c:Concept) RETURN count(c)",
        )
        assert n == 4, f"Module 4 must have exactly 4 concepts, got {n}"


def test_module4_concepts_exist(driver):
    """The 4 expected concept ids of Module 4 must all exist."""
    with driver.session() as s:
        expected = {
            "concept_bissection",
            "concept_fixed_point",
            "concept_newton_raphson",
            "concept_secant",
        }
        for concept_id in expected:
            n = _count(
                s,
                f"MATCH (c:Concept {{id:'{concept_id}'}}) RETURN count(c)",
            )
            assert n == 1, f"Concept {concept_id} missing from graph"


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


# ------------------------------------------------------------------
# Bilingual fields (added for FR/EN platform support)
# ------------------------------------------------------------------
def test_concepts_have_french_names(driver):
    """Every concept must have a non-empty `name_fr` for bilingual UI."""
    with driver.session() as s:
        row = s.run(
            "MATCH (c:Concept) WHERE c.name_fr IS NULL OR c.name_fr = '' "
            "RETURN count(c) AS missing"
        ).single()
        assert row["missing"] == 0, (
            f"{row['missing']} concept(s) missing name_fr — bilingual UI will fall back to English"
        )


def test_modules_have_french_names(driver):
    """Every module must have a non-empty `name_fr`."""
    with driver.session() as s:
        row = s.run(
            "MATCH (m:Module) WHERE m.name_fr IS NULL OR m.name_fr = '' "
            "RETURN count(m) AS missing"
        ).single()
        assert row["missing"] == 0, f"{row['missing']} module(s) missing name_fr"
