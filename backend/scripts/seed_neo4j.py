#!/usr/bin/env python3
"""
Neo4j Seed Script for Adaptive Learning Platform PFE
Populates the knowledge graph with numerical analysis concepts.

SCOPE V1 (final — April 21, 2026):
  Module 1 — Interpolation
  Module 2 — Numerical Integration
  Module 3 — Polynomial Approximation & Optimization   <-- replaces ODEs (deferred to V2)

Changes vs. previous version (backup kept as seed_neo4j.py.bak_20260421):
  - Module "ODEs" renamed to "Polynomial Approximation & Optimization" (id: module_approximation)
  - 5 ODE concepts (initial_value, taylor_series, euler, improved_euler, rk4) replaced by:
      * concept_least_squares             (Least Squares Approximation)
      * concept_orthogonal_polynomials    (Chebyshev / Legendre)
      * concept_minimax_approximation     (Best L-infinity approximation)
      * concept_gradient_descent          (Gradient Descent)
      * concept_newton_optimization       (Newton's Method for optimization)
  - REQUIRES relationships now include cross-module edges that reuse Module 1 (polynomials)
    and Module 2 (integrals) as prerequisites for Module 3.
  - Resources resource_euler_video / resource_rk4_exercise replaced by:
      * resource_gradient_video           (Gradient Descent video tutorial)
      * resource_newton_optim_exercise    (Newton's Method optimization problems)
  - REMEDIATES_TO updated accordingly.

Total after seeding: 26 nodes (3 Module + 15 Concept + 8 Resource) and 37 relationships
  (15 COVERS + 14 REQUIRES + 8 REMEDIATES_TO).
"""

import logging

from neo4j import GraphDatabase

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Neo4jSeeder:
    """Handles Neo4j database seeding and graph population."""

    def __init__(self, uri, user, password):
        """Initialize Neo4j connection."""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.session = None

    def close(self):
        """Close the database connection."""
        if self.driver:
            self.driver.close()

    # ------------------------------------------------------------------
    # Cleaning + constraints
    # ------------------------------------------------------------------
    def clear_database(self):
        """Clear all existing nodes and relationships."""
        logger.info("Clearing existing data...")
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        logger.info("Database cleared successfully")

    def create_constraints(self):
        """Create database constraints (uniqueness on node ids)."""
        logger.info("Creating constraints...")
        with self.driver.session() as session:
            session.run("CREATE CONSTRAINT concept_id IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE")
            session.run("CREATE CONSTRAINT module_id IF NOT EXISTS FOR (m:Module) REQUIRE m.id IS UNIQUE")
            session.run("CREATE CONSTRAINT resource_id IF NOT EXISTS FOR (r:Resource) REQUIRE r.id IS UNIQUE")
        logger.info("Constraints created")

    # ------------------------------------------------------------------
    # Modules
    # ------------------------------------------------------------------
    def create_modules(self):
        """Create Module nodes (3 modules of the V1 scope)."""
        logger.info("Creating Module nodes...")
        modules = [
            {
                "id": "module_interpolation",
                "name": "Interpolation",
                "description": "Techniques for estimating values between known data points using polynomial methods."
            },
            {
                "id": "module_integration",
                "name": "Numerical Integration",
                "description": "Methods for computing definite integrals numerically."
            },
            {
                # ---------------- NEW MODULE 3 ----------------
                "id": "module_approximation",
                "name": "Polynomial Approximation & Optimization",
                "description": (
                    "Approximating functions by polynomials (least squares, orthogonal families, "
                    "minimax) and optimization algorithms (gradient descent, Newton's method) to "
                    "solve the resulting minimization problems."
                )
            }
        ]

        with self.driver.session() as session:
            for module in modules:
                session.run(
                    """
                    CREATE (m:Module {
                        id: $id,
                        name: $name,
                        description: $description
                    })
                    """,
                    id=module["id"],
                    name=module["name"],
                    description=module["description"]
                )
        logger.info(f"Created {len(modules)} modules")
        return modules

    # ------------------------------------------------------------------
    # Concepts (15 total: 5 per module)
    # ------------------------------------------------------------------
    def create_concepts(self):
        """Create Concept nodes for all three modules."""
        logger.info("Creating Concept nodes...")

        concepts = [
            # ---------- Module 1: Interpolation (unchanged) ----------
            {
                "id": "concept_polynomial_basics",
                "name": "Polynomial Basics",
                "description": "Fundamental concepts of polynomial functions, degree, operations, factorization.",
                "difficulty": "beginner",
                "module_id": "module_interpolation"
            },
            {
                "id": "concept_lagrange",
                "name": "Lagrange Interpolation",
                "description": "Method of constructing a polynomial from known values using Lagrange basis polynomials.",
                "difficulty": "intermediate",
                "module_id": "module_interpolation"
            },
            {
                "id": "concept_divided_differences",
                "name": "Divided Differences",
                "description": "Technique for computing coefficients in the Newton form of the interpolating polynomial.",
                "difficulty": "intermediate",
                "module_id": "module_interpolation"
            },
            {
                "id": "concept_newton_interpolation",
                "name": "Newton Interpolation",
                "description": "Constructing interpolating polynomials using divided differences (incremental form).",
                "difficulty": "intermediate",
                "module_id": "module_interpolation"
            },
            {
                "id": "concept_spline_interpolation",
                "name": "Spline Interpolation",
                "description": "Using piecewise polynomial functions (cubic splines) for smooth interpolation.",
                "difficulty": "advanced",
                "module_id": "module_interpolation"
            },

            # ---------- Module 2: Numerical Integration (unchanged) ----------
            {
                "id": "concept_riemann_sums",
                "name": "Riemann Sums",
                "description": "Approximating integrals using sums of rectangle areas (left, right, midpoint).",
                "difficulty": "beginner",
                "module_id": "module_integration"
            },
            {
                "id": "concept_definite_integrals",
                "name": "Definite Integrals",
                "description": "Theoretical foundations of definite integrals and their properties.",
                "difficulty": "beginner",
                "module_id": "module_integration"
            },
            {
                "id": "concept_trapezoidal",
                "name": "Trapezoidal Rule",
                "description": "Numerical integration method using trapezoid approximations; composite formula; O(h^2) error.",
                "difficulty": "intermediate",
                "module_id": "module_integration"
            },
            {
                "id": "concept_simpson",
                "name": "Simpson's Rule",
                "description": "Integration method using parabolic (1/3) and cubic (3/8) approximations; O(h^4) error.",
                "difficulty": "intermediate",
                "module_id": "module_integration"
            },
            {
                "id": "concept_gaussian_quadrature",
                "name": "Gaussian Quadrature",
                "description": "Advanced integration method using optimal node placement and weights from Legendre polynomials.",
                "difficulty": "advanced",
                "module_id": "module_integration"
            },

            # ---------- Module 3: Polynomial Approximation & Optimization (NEW) ----------
            {
                "id": "concept_least_squares",
                "name": "Least Squares Approximation",
                "description": (
                    "Find the polynomial p of degree <= n that minimizes sum((y_i - p(x_i))^2). "
                    "Solved via normal equations; foundational for regression and data fitting."
                ),
                "difficulty": "intermediate",
                "module_id": "module_approximation"
            },
            {
                "id": "concept_orthogonal_polynomials",
                "name": "Orthogonal Polynomials",
                "description": (
                    "Families of polynomials (Chebyshev, Legendre) orthogonal for an inner product "
                    "integral(p_i * p_j * w dx) = 0. Used for stable approximation and Gaussian quadrature nodes."
                ),
                "difficulty": "advanced",
                "module_id": "module_approximation"
            },
            {
                "id": "concept_minimax_approximation",
                "name": "Best (Minimax) Approximation",
                "description": (
                    "Polynomial approximation under the L^inf norm: minimize max|f(x) - p(x)|. "
                    "Chebyshev equi-oscillation theorem; near-optimal via Chebyshev truncation."
                ),
                "difficulty": "advanced",
                "module_id": "module_approximation"
            },
            {
                "id": "concept_gradient_descent",
                "name": "Gradient Descent",
                "description": (
                    "Iterative optimization x_{k+1} = x_k - alpha * grad f(x_k). Step size selection, "
                    "convergence for convex functions; foundation of many ML training algorithms."
                ),
                "difficulty": "intermediate",
                "module_id": "module_approximation"
            },
            {
                "id": "concept_newton_optimization",
                "name": "Newton's Method for Optimization",
                "description": (
                    "Iterative optimization x_{k+1} = x_k - H(x_k)^{-1} * grad f(x_k) using the Hessian. "
                    "Local quadratic convergence; cost of Hessian inversion discussed."
                ),
                "difficulty": "advanced",
                "module_id": "module_approximation"
            }
        ]

        with self.driver.session() as session:
            for concept in concepts:
                concept.pop("module_id")  # kept out of Neo4j payload (relation created later)
                session.run(
                    """
                    CREATE (c:Concept {
                        id: $id,
                        name: $name,
                        description: $description,
                        difficulty: $difficulty
                    })
                    """,
                    **concept
                )
        logger.info(f"Created {len(concepts)} concepts")
        return concepts

    # ------------------------------------------------------------------
    # Resources (8 total)
    # ------------------------------------------------------------------
    def create_resources(self):
        """Create Resource nodes (remediation material)."""
        logger.info("Creating Resource nodes...")

        resources = [
            # Interpolation resources (unchanged)
            {
                "id": "resource_lagrange_video",
                "name": "Lagrange Interpolation Video Tutorial",
                "type": "video",
                "url": "https://www.example.com/lagrange-interpolation"
            },
            {
                "id": "resource_newton_exercise",
                "name": "Newton Interpolation Practice Problems",
                "type": "exercise",
                "url": "https://www.example.com/newton-exercises"
            },
            {
                "id": "resource_spline_tutorial",
                "name": "Spline Interpolation Tutorial",
                "type": "tutorial",
                "url": "https://www.example.com/spline-tutorial"
            },
            # Integration resources (unchanged)
            {
                "id": "resource_trapezoidal_video",
                "name": "Trapezoidal Rule Video",
                "type": "video",
                "url": "https://www.example.com/trapezoidal-rule"
            },
            {
                "id": "resource_simpson_exercise",
                "name": "Simpson's Rule Exercises",
                "type": "exercise",
                "url": "https://www.example.com/simpson-exercises"
            },
            {
                "id": "resource_gaussian_tutorial",
                "name": "Gaussian Quadrature Deep Dive",
                "type": "tutorial",
                "url": "https://www.example.com/gaussian-quadrature"
            },
            # Approximation & Optimization resources (NEW — replace ODE resources)
            {
                "id": "resource_gradient_video",
                "name": "Gradient Descent Visualized",
                "type": "video",
                "url": "https://www.example.com/gradient-descent-video"
            },
            {
                "id": "resource_newton_optim_exercise",
                "name": "Newton's Method (Optimization) Exercises",
                "type": "exercise",
                "url": "https://www.example.com/newton-optimization-exercises"
            }
        ]

        with self.driver.session() as session:
            for resource in resources:
                session.run(
                    """
                    CREATE (r:Resource {
                        id: $id,
                        name: $name,
                        type: $type,
                        url: $url
                    })
                    """,
                    **resource
                )
        logger.info(f"Created {len(resources)} resources")
        return resources

    # ------------------------------------------------------------------
    # COVERS relations (Module --> Concept)  : 15 relations
    # ------------------------------------------------------------------
    def create_module_covers_relationships(self):
        """Create Module-COVERS-Concept relationships."""
        logger.info("Creating Module COVERS Concept relationships...")

        relationships = [
            # Module 1: Interpolation
            ("module_interpolation", "concept_polynomial_basics"),
            ("module_interpolation", "concept_lagrange"),
            ("module_interpolation", "concept_divided_differences"),
            ("module_interpolation", "concept_newton_interpolation"),
            ("module_interpolation", "concept_spline_interpolation"),

            # Module 2: Numerical Integration
            ("module_integration", "concept_riemann_sums"),
            ("module_integration", "concept_definite_integrals"),
            ("module_integration", "concept_trapezoidal"),
            ("module_integration", "concept_simpson"),
            ("module_integration", "concept_gaussian_quadrature"),

            # Module 3: Polynomial Approximation & Optimization (NEW)
            ("module_approximation", "concept_least_squares"),
            ("module_approximation", "concept_orthogonal_polynomials"),
            ("module_approximation", "concept_minimax_approximation"),
            ("module_approximation", "concept_gradient_descent"),
            ("module_approximation", "concept_newton_optimization"),
        ]

        with self.driver.session() as session:
            for module_id, concept_id in relationships:
                session.run(
                    """
                    MATCH (m:Module {id: $module_id})
                    MATCH (c:Concept {id: $concept_id})
                    CREATE (m)-[:COVERS]->(c)
                    """,
                    module_id=module_id,
                    concept_id=concept_id
                )
        logger.info(f"Created {len(relationships)} Module-COVERS-Concept relationships")

    # ------------------------------------------------------------------
    # REQUIRES relations (Concept --> Concept) : 14 relations (up from 12)
    # Edge direction : dependent --REQUIRES--> prerequisite
    # ------------------------------------------------------------------
    def create_concept_requires_relationships(self):
        """Create Concept-REQUIRES-Concept prerequisite relationships."""
        logger.info("Creating Concept REQUIRES relationships...")

        # Each pair is (prerequisite_id, dependent_id).
        # The Cypher below creates (dependent)-[:REQUIRES]->(prerequisite).
        # Each pair is (prerequisite_id, dependent_id).
        # The Cypher below creates (dependent)-[:REQUIRES]->(prerequisite).
        prerequisites = [
            # ----- Module 1: Interpolation (intra-module) -----
            ("concept_polynomial_basics", "concept_lagrange"),
            ("concept_polynomial_basics", "concept_newton_interpolation"),
            ("concept_divided_differences", "concept_newton_interpolation"),
            ("concept_lagrange", "concept_spline_interpolation"),

            # ----- Module 2: Integration (intra-module) -----
            ("concept_riemann_sums", "concept_trapezoidal"),
            ("concept_definite_integrals", "concept_trapezoidal"),
            ("concept_trapezoidal", "concept_simpson"),
            ("concept_simpson", "concept_gaussian_quadrature"),

            # ----- Module 3: Approximation & Optimization (intra-module) -----
            ("concept_least_squares", "concept_orthogonal_polynomials"),
            ("concept_orthogonal_polynomials", "concept_minimax_approximation"),
            ("concept_gradient_descent", "concept_newton_optimization"),

            # ----- CROSS-MODULE prerequisites (3 edges, 3 distinct source concepts) -----
            # Least squares approximation needs polynomial manipulation (Module 1)
            ("concept_polynomial_basics", "concept_least_squares"),
            # Orthogonal polynomials (Chebyshev, Legendre) are defined by an
            # inner product that is an INTEGRAL, so they need Module 2 concepts
            # (definite integrals for the inner-product definition, trapezoidal
            # rule for the numerical computation of those integrals).
            ("concept_definite_integrals", "concept_orthogonal_polynomials"),
            ("concept_trapezoidal", "concept_orthogonal_polynomials"),
        ]

        with self.driver.session() as session:
            for prerequisite_id, dependent_id in prerequisites:
                session.run(
                    """
                    MATCH (c1:Concept {id: $prerequisite_id})
                    MATCH (c2:Concept {id: $dependent_id})
                    CREATE (c2)-[:REQUIRES]->(c1)
                    """,
                    prerequisite_id=prerequisite_id,
                    dependent_id=dependent_id,
                )
        logger.info(f"Created {len(prerequisites)} Concept REQUIRES relationships")

    # ------------------------------------------------------------------
    # REMEDIATES_TO relations (Concept --> Resource) : 8 relations
    # ------------------------------------------------------------------
    def create_remediation_relationships(self):
        """Create Concept-REMEDIATES_TO-Resource relationships."""
        logger.info("Creating Concept REMEDIATES_TO Resource relationships...")

        remediations = [
            # Module 1 - Interpolation
            ("concept_lagrange", "resource_lagrange_video"),
            ("concept_newton_interpolation", "resource_newton_exercise"),
            ("concept_spline_interpolation", "resource_spline_tutorial"),
            # Module 2 - Integration
            ("concept_trapezoidal", "resource_trapezoidal_video"),
            ("concept_simpson", "resource_simpson_exercise"),
            ("concept_gaussian_quadrature", "resource_gaussian_tutorial"),
            # Module 3 - Approximation & Optimization (replaces ODE remediations)
            ("concept_gradient_descent", "resource_gradient_video"),
            ("concept_newton_optimization", "resource_newton_optim_exercise"),
        ]

        with self.driver.session() as session:
            for concept_id, resource_id in remediations:
                session.run(
                    """
                    MATCH (c:Concept {id: $concept_id})
                    MATCH (r:Resource {id: $resource_id})
                    CREATE (c)-[:REMEDIATES_TO]->(r)
                    """,
                    concept_id=concept_id,
                    resource_id=resource_id,
                )
        logger.info(f"Created {len(remediations)} Concept REMEDIATES_TO Resource relationships")

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------
    def verify_graph(self):
        """Verify the created graph and print statistics."""
        logger.info("\n" + "=" * 60)
        logger.info("GRAPH VERIFICATION")
        logger.info("=" * 60)

        with self.driver.session() as session:
            total_nodes = 0
            logger.info("\nNode Counts:")
            for label in ["Module", "Concept", "Resource"]:
                count = session.run(
                    f"MATCH (n:{label}) RETURN count(n) AS count"
                ).single()["count"]
                total_nodes += count
                logger.info(f"  - {label}: {count}")
            logger.info(f"  Total nodes: {total_nodes}")

            total_rels = 0
            logger.info("\nRelationship Counts:")
            for rel in ["COVERS", "REQUIRES", "REMEDIATES_TO"]:
                count = session.run(
                    f"MATCH ()-[r:{rel}]->() RETURN count(r) AS count"
                ).single()["count"]
                total_rels += count
                logger.info(f"  - {rel}: {count}")
            logger.info(f"  Total relationships: {total_rels}")

        logger.info("=" * 60)

    # ------------------------------------------------------------------
    # Pipeline orchestrator
    # ------------------------------------------------------------------
    def seed(self):
        """Run the full seeding pipeline."""
        try:
            self.clear_database()
            self.create_constraints()
            self.create_modules()
            self.create_concepts()
            self.create_resources()
            self.create_module_covers_relationships()
            self.create_concept_requires_relationships()
            self.create_remediation_relationships()
            self.verify_graph()
            logger.info("Seeding completed successfully!")
        except Exception as e:
            logger.error(f"Error during seeding: {e}")
            raise
        finally:
            self.close()


def main():
    """Entry point: read env and seed Neo4j."""
    import os
    from dotenv import load_dotenv

    here = os.path.dirname(os.path.abspath(__file__))
    load_dotenv(os.path.join(here, "..", "..", ".env"))

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")

    if not password:
        raise SystemExit("NEO4J_PASSWORD is not set (check your .env file)")

    logger.info(f"Connecting to Neo4j at {uri} as {user}")
    Neo4jSeeder(uri, user, password).seed()


if __name__ == "__main__":
    main()
