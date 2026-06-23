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

Total after seeding (V1 + Module 4) :
  Nodes : 33 (4 Module + 19 Concept + 10 Resource)
  Relations : 49 (19 COVERS + 20 REQUIRES + 10 REMEDIATES_TO)

Module 4 (added May 2026) covers root-finding for f(x)=0 :
  - concept_bissection
  - concept_fixed_point
  - concept_newton_raphson
  - concept_secant
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
        """Create Module nodes (3 modules of the V1 scope).

        Bilingual fields: `name` / `description` are kept (English, default and
        backward-compatible). `name_fr` / `description_fr` carry the French
        translation. Routers use coalesce(field_<lang>, field) to pick the
        right language when serving content.
        """
        logger.info("Creating Module nodes...")
        modules = [
            {
                "id": "module_interpolation",
                "name": "Interpolation",
                "name_fr": "Interpolation",
                "description": "Techniques for estimating values between known data points using polynomial methods.",
                "description_fr": "Techniques pour estimer des valeurs entre des points connus avec des methodes polynomiales.",
            },
            {
                "id": "module_integration",
                "name": "Numerical Integration",
                "name_fr": "Integration numerique",
                "description": "Methods for computing definite integrals numerically.",
                "description_fr": "Methodes pour calculer numeriquement des integrales definies.",
            },
            {
                # ---------------- NEW MODULE 3 ----------------
                "id": "module_approximation",
                "name": "Polynomial Approximation & Optimization",
                "name_fr": "Approximation polynomiale et optimisation",
                "description": (
                    "Approximating functions by polynomials (least squares, orthogonal families, "
                    "minimax) and optimization algorithms (gradient descent, Newton's method) to "
                    "solve the resulting minimization problems."
                ),
                "description_fr": (
                    "Approximation de fonctions par des polynomes (moindres carres, familles "
                    "orthogonales, minimax) et algorithmes d'optimisation (descente de gradient, "
                    "methode de Newton) pour resoudre les problemes de minimisation associes."
                ),
            },
            {
                # ---------------- NEW MODULE 4 (root finding) ----------------
                "id": "module_root_finding",
                "name": "Solving Non-linear Equations",
                "name_fr": "Resolution d'equations non-lineaires",
                "description": (
                    "Iterative methods to find roots of f(x) = 0: bisection, fixed-point "
                    "iteration, Newton-Raphson and the secant method. Foundation of many "
                    "engineering and scientific solvers."
                ),
                "description_fr": (
                    "Methodes iteratives pour trouver les racines de f(x) = 0 : bissection, "
                    "iteration du point fixe, Newton-Raphson et methode de la secante. "
                    "Fondement de nombreux solveurs en ingenierie et en science."
                ),
            }
        ]

        with self.driver.session() as session:
            for module in modules:
                session.run(
                    """
                    CREATE (m:Module {
                        id: $id,
                        name: $name,
                        name_fr: $name_fr,
                        description: $description,
                        description_fr: $description_fr
                    })
                    """,
                    id=module["id"],
                    name=module["name"],
                    name_fr=module["name_fr"],
                    description=module["description"],
                    description_fr=module["description_fr"],
                )
        logger.info(f"Created {len(modules)} modules (bilingual EN/FR)")
        return modules

    # ------------------------------------------------------------------
    # Concepts (15 total: 5 per module)
    # ------------------------------------------------------------------
    def create_concepts(self):
        """Create Concept nodes for all three modules."""
        logger.info("Creating Concept nodes...")

        concepts = [
            # ---------- Module 1: Interpolation ----------
            {
                "id": "concept_polynomial_basics",
                "name": "Polynomial Basics",
                "name_fr": "Bases des polynomes",
                "description": "Fundamental concepts of polynomial functions, degree, operations, factorization.",
                "description_fr": "Concepts fondamentaux des fonctions polynomiales : degre, operations, factorisation.",
                "difficulty": "beginner",
                "module_id": "module_interpolation"
            },
            {
                "id": "concept_lagrange",
                "name": "Lagrange Interpolation",
                "name_fr": "Interpolation de Lagrange",
                "description": "Method of constructing a polynomial from known values using Lagrange basis polynomials.",
                "description_fr": "Methode pour construire un polynome a partir de valeurs connues via les polynomes de la base de Lagrange.",
                "difficulty": "intermediate",
                "module_id": "module_interpolation"
            },
            {
                "id": "concept_divided_differences",
                "name": "Divided Differences",
                "name_fr": "Differences divisees",
                "description": "Technique for computing coefficients in the Newton form of the interpolating polynomial.",
                "description_fr": "Technique de calcul des coefficients de la forme de Newton du polynome d'interpolation.",
                "difficulty": "intermediate",
                "module_id": "module_interpolation"
            },
            {
                "id": "concept_newton_interpolation",
                "name": "Newton Interpolation",
                "name_fr": "Interpolation de Newton",
                "description": "Constructing interpolating polynomials using divided differences (incremental form).",
                "description_fr": "Construction de polynomes d'interpolation via les differences divisees (forme incrementale).",
                "difficulty": "intermediate",
                "module_id": "module_interpolation"
            },
            {
                "id": "concept_spline_interpolation",
                "name": "Spline Interpolation",
                "name_fr": "Interpolation par splines",
                "description": "Using piecewise polynomial functions (cubic splines) for smooth interpolation.",
                "description_fr": "Utilisation de fonctions polynomiales par morceaux (splines cubiques) pour une interpolation lisse.",
                "difficulty": "advanced",
                "module_id": "module_interpolation"
            },

            # ---------- Module 2: Numerical Integration ----------
            {
                "id": "concept_riemann_sums",
                "name": "Riemann Sums",
                "name_fr": "Sommes de Riemann",
                "description": "Approximating integrals using sums of rectangle areas (left, right, midpoint).",
                "description_fr": "Approximation d'integrales par des sommes d'aires de rectangles (gauche, droite, milieu).",
                "difficulty": "beginner",
                "module_id": "module_integration"
            },
            {
                "id": "concept_definite_integrals",
                "name": "Definite Integrals",
                "name_fr": "Integrales definies",
                "description": "Theoretical foundations of definite integrals and their properties.",
                "description_fr": "Fondements theoriques des integrales definies et leurs proprietes.",
                "difficulty": "beginner",
                "module_id": "module_integration"
            },
            {
                "id": "concept_trapezoidal",
                "name": "Trapezoidal Rule",
                "name_fr": "Methode des trapezes",
                "description": "Numerical integration method using trapezoid approximations; composite formula; O(h^2) error.",
                "description_fr": "Methode d'integration numerique par approximation par des trapezes ; formule composite ; erreur O(h^2).",
                "difficulty": "intermediate",
                "module_id": "module_integration"
            },
            {
                "id": "concept_simpson",
                "name": "Simpson's Rule",
                "name_fr": "Methode de Simpson",
                "description": "Integration method using parabolic (1/3) and cubic (3/8) approximations; O(h^4) error.",
                "description_fr": "Methode d'integration utilisant des approximations paraboliques (1/3) et cubiques (3/8) ; erreur O(h^4).",
                "difficulty": "intermediate",
                "module_id": "module_integration"
            },
            {
                "id": "concept_gaussian_quadrature",
                "name": "Gaussian Quadrature",
                "name_fr": "Quadrature de Gauss",
                "description": "Advanced integration method using optimal node placement and weights from Legendre polynomials.",
                "description_fr": "Methode d'integration avancee utilisant le placement optimal des noeuds et des poids issus des polynomes de Legendre.",
                "difficulty": "advanced",
                "module_id": "module_integration"
            },

            # ---------- Module 3: Polynomial Approximation & Optimization ----------
            {
                "id": "concept_least_squares",
                "name": "Least Squares Approximation",
                "name_fr": "Approximation par moindres carres",
                "description": (
                    "Find the polynomial p of degree <= n that minimizes sum((y_i - p(x_i))^2). "
                    "Solved via normal equations; foundational for regression and data fitting."
                ),
                "description_fr": (
                    "Trouver le polynome p de degre <= n qui minimise sum((y_i - p(x_i))^2). "
                    "Resolu par les equations normales ; fondamental pour la regression et l'ajustement de donnees."
                ),
                "difficulty": "intermediate",
                "module_id": "module_approximation"
            },
            {
                "id": "concept_orthogonal_polynomials",
                "name": "Orthogonal Polynomials",
                "name_fr": "Polynomes orthogonaux",
                "description": (
                    "Families of polynomials (Chebyshev, Legendre) orthogonal for an inner product "
                    "integral(p_i * p_j * w dx) = 0. Used for stable approximation and Gaussian quadrature nodes."
                ),
                "description_fr": (
                    "Familles de polynomes (Tchebychev, Legendre) orthogonaux pour un produit scalaire "
                    "integrale(p_i * p_j * w dx) = 0. Utilises pour des approximations stables et les noeuds de quadrature de Gauss."
                ),
                "difficulty": "advanced",
                "module_id": "module_approximation"
            },
            {
                "id": "concept_minimax_approximation",
                "name": "Best (Minimax) Approximation",
                "name_fr": "Meilleure approximation (minimax)",
                "description": (
                    "Polynomial approximation under the L^inf norm: minimize max|f(x) - p(x)|. "
                    "Chebyshev equi-oscillation theorem; near-optimal via Chebyshev truncation."
                ),
                "description_fr": (
                    "Approximation polynomiale sous la norme L^inf : minimiser max|f(x) - p(x)|. "
                    "Theoreme d'equi-oscillation de Tchebychev ; presque optimal via troncature de Tchebychev."
                ),
                "difficulty": "advanced",
                "module_id": "module_approximation"
            },
            {
                "id": "concept_gradient_descent",
                "name": "Gradient Descent",
                "name_fr": "Descente de gradient",
                "description": (
                    "Iterative optimization x_{k+1} = x_k - alpha * grad f(x_k). Step size selection, "
                    "convergence for convex functions; foundation of many ML training algorithms."
                ),
                "description_fr": (
                    "Optimisation iterative x_{k+1} = x_k - alpha * grad f(x_k). Choix du pas, "
                    "convergence pour les fonctions convexes ; fondement de nombreux algorithmes d'apprentissage."
                ),
                "difficulty": "intermediate",
                "module_id": "module_approximation"
            },
            {
                "id": "concept_newton_optimization",
                "name": "Newton's Method for Optimization",
                "name_fr": "Methode de Newton pour l'optimisation",
                "description": (
                    "Iterative optimization x_{k+1} = x_k - H(x_k)^{-1} * grad f(x_k) using the Hessian. "
                    "Local quadratic convergence; cost of Hessian inversion discussed."
                ),
                "description_fr": (
                    "Optimisation iterative x_{k+1} = x_k - H(x_k)^{-1} * grad f(x_k) en utilisant la hessienne. "
                    "Convergence quadratique locale ; cout d'inversion de la hessienne discute."
                ),
                "difficulty": "advanced",
                "module_id": "module_approximation"
            },

            # ---------- Module 4: Solving Non-linear Equations (NEW) ----------
            {
                "id": "concept_bissection",
                "name": "Bisection Method",
                "name_fr": "Methode de la bissection",
                "description": (
                    "Bracketing method that halves an interval [a, b] where f(a) f(b) < 0 "
                    "until convergence. Linear convergence (1 bit per iteration) but always "
                    "converges if f is continuous."
                ),
                "description_fr": (
                    "Methode d'encadrement qui reduit de moitie un intervalle [a, b] ou f(a) f(b) < 0 "
                    "jusqu'a convergence. Convergence lineaire (1 bit par iteration) mais converge "
                    "toujours si f est continue."
                ),
                "difficulty": "beginner",
                "module_id": "module_root_finding"
            },
            {
                "id": "concept_fixed_point",
                "name": "Fixed-Point Iteration",
                "name_fr": "Iteration du point fixe",
                "description": (
                    "Solve f(x) = 0 by rewriting as x = g(x) and iterating x_{k+1} = g(x_k). "
                    "Converges if |g'(x*)| < 1 near the fixed point. Foundation of many root-finding methods."
                ),
                "description_fr": (
                    "Resoudre f(x) = 0 en reecrivant sous la forme x = g(x) et en iterant x_{k+1} = g(x_k). "
                    "Converge si |g'(x*)| < 1 pres du point fixe. Fondement de nombreuses methodes de "
                    "recherche de racines."
                ),
                "difficulty": "beginner",
                "module_id": "module_root_finding"
            },
            {
                "id": "concept_newton_raphson",
                "name": "Newton-Raphson Method",
                "name_fr": "Methode de Newton-Raphson",
                "description": (
                    "Iterative root-finding method using the formula x_{k+1} = x_k - f(x_k)/f'(x_k). "
                    "Quadratic convergence near simple roots; requires f' to be available."
                ),
                "description_fr": (
                    "Methode iterative pour trouver les racines : x_{k+1} = x_k - f(x_k)/f'(x_k). "
                    "Convergence quadratique pres des racines simples ; necessite f' calculable."
                ),
                "difficulty": "intermediate",
                "module_id": "module_root_finding"
            },
            {
                "id": "concept_secant",
                "name": "Secant Method",
                "name_fr": "Methode de la secante",
                "description": (
                    "Approximates Newton-Raphson without computing f' by using two previous iterates: "
                    "x_{k+1} = x_k - f(x_k) (x_k - x_{k-1}) / (f(x_k) - f(x_{k-1})). "
                    "Super-linear convergence (golden ratio ~1.618)."
                ),
                "description_fr": (
                    "Approxime Newton-Raphson sans calculer f' en utilisant deux iterations precedentes : "
                    "x_{k+1} = x_k - f(x_k) (x_k - x_{k-1}) / (f(x_k) - f(x_{k-1})). "
                    "Convergence super-lineaire (nombre d'or ~1.618)."
                ),
                "difficulty": "intermediate",
                "module_id": "module_root_finding"
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
                        name_fr: $name_fr,
                        description: $description,
                        description_fr: $description_fr,
                        difficulty: $difficulty
                    })
                    """,
                    **concept
                )
        logger.info(f"Created {len(concepts)} concepts (bilingual EN/FR)")
        return concepts

    # ------------------------------------------------------------------
    # Resources (8 total)
    # ------------------------------------------------------------------
    def create_resources(self):
        """Create Resource nodes (remediation material)."""
        logger.info("Creating Resource nodes...")

        resources = [
            # Interpolation resources
            {
                "id": "resource_lagrange_video",
                "name": "Lagrange Interpolation Video Tutorial",
                "name_fr": "Tutoriel video sur l'interpolation de Lagrange",
                "type": "video",
                "url": "https://www.example.com/lagrange-interpolation"
            },
            {
                "id": "resource_newton_exercise",
                "name": "Newton Interpolation Practice Problems",
                "name_fr": "Exercices d'interpolation de Newton",
                "type": "exercise",
                "url": "https://www.example.com/newton-exercises"
            },
            {
                "id": "resource_spline_tutorial",
                "name": "Spline Interpolation Tutorial",
                "name_fr": "Tutoriel sur l'interpolation par splines",
                "type": "tutorial",
                "url": "https://www.example.com/spline-tutorial"
            },
            # Integration resources
            {
                "id": "resource_trapezoidal_video",
                "name": "Trapezoidal Rule Video",
                "name_fr": "Video sur la methode des trapezes",
                "type": "video",
                "url": "https://www.example.com/trapezoidal-rule"
            },
            {
                "id": "resource_simpson_exercise",
                "name": "Simpson's Rule Exercises",
                "name_fr": "Exercices sur la methode de Simpson",
                "type": "exercise",
                "url": "https://www.example.com/simpson-exercises"
            },
            {
                "id": "resource_gaussian_tutorial",
                "name": "Gaussian Quadrature Deep Dive",
                "name_fr": "Approfondissement sur la quadrature de Gauss",
                "type": "tutorial",
                "url": "https://www.example.com/gaussian-quadrature"
            },
            # Approximation & Optimization resources
            {
                "id": "resource_gradient_video",
                "name": "Gradient Descent Visualized",
                "name_fr": "Descente de gradient en images",
                "type": "video",
                "url": "https://www.example.com/gradient-descent-video"
            },
            {
                "id": "resource_newton_optim_exercise",
                "name": "Newton's Method (Optimization) Exercises",
                "name_fr": "Exercices : methode de Newton (optimisation)",
                "type": "exercise",
                "url": "https://www.example.com/newton-optimization-exercises"
            },
            # Module 4: Solving Non-linear Equations resources
            {
                "id": "resource_newton_raphson_video",
                "name": "Newton-Raphson Visual Explanation",
                "name_fr": "Explication visuelle de Newton-Raphson",
                "type": "video",
                "url": "https://www.example.com/newton-raphson-video"
            },
            {
                "id": "resource_bissection_exercise",
                "name": "Bisection Method Practice Problems",
                "name_fr": "Exercices : methode de la bissection",
                "type": "exercise",
                "url": "https://www.example.com/bisection-exercises"
            }
        ]

        with self.driver.session() as session:
            for resource in resources:
                session.run(
                    """
                    CREATE (r:Resource {
                        id: $id,
                        name: $name,
                        name_fr: $name_fr,
                        type: $type,
                        url: $url
                    })
                    """,
                    **resource
                )
        logger.info(f"Created {len(resources)} resources (bilingual EN/FR)")
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

            # Module 3: Polynomial Approximation & Optimization
            ("module_approximation", "concept_least_squares"),
            ("module_approximation", "concept_orthogonal_polynomials"),
            ("module_approximation", "concept_minimax_approximation"),
            ("module_approximation", "concept_gradient_descent"),
            ("module_approximation", "concept_newton_optimization"),

            # Module 4: Solving Non-linear Equations (NEW)
            ("module_root_finding", "concept_bissection"),
            ("module_root_finding", "concept_fixed_point"),
            ("module_root_finding", "concept_newton_raphson"),
            ("module_root_finding", "concept_secant"),
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

            # ----- Module 4: Solving Non-linear Equations (intra + cross-module) -----
            # Newton-Raphson uses derivatives, secante uses two prior iterates,
            # tous reposent sur la manipulation polynomiale de base.
            # Bissection est le plus simple et sert de prerequis pedagogique
            # pour Newton-Raphson (on enseigne d'abord la convergence garantie).
            ("concept_polynomial_basics", "concept_bissection"),
            ("concept_polynomial_basics", "concept_fixed_point"),
            ("concept_bissection", "concept_newton_raphson"),
            ("concept_polynomial_basics", "concept_newton_raphson"),
            # Secante = Newton sans derivee : on enseigne Newton-Raphson d'abord.
            ("concept_newton_raphson", "concept_secant"),
            ("concept_divided_differences", "concept_secant"),
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
            # Module 3 - Approximation & Optimization
            ("concept_gradient_descent", "resource_gradient_video"),
            ("concept_newton_optimization", "resource_newton_optim_exercise"),
            # Module 4 - Solving Non-linear Equations
            ("concept_newton_raphson", "resource_newton_raphson_video"),
            ("concept_bissection", "resource_bissection_exercise"),
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
