#!/usr/bin/env python3
"""
Phase 2 — Sprint 1: Question Bank
Populates the quiz table with MCQs covering the 15 numerical analysis concepts.

Usage:
    cd backend
    venv\\Scripts\\activate
    python scripts/seed_quizzes.py

Prerequisites:
    - PostgreSQL running (docker-compose up -d)
    - Backend started at least once (tables created)
    - .env configured
"""

import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), "../../.env")
load_dotenv(dotenv_path)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================
# QUESTION BANK — 15 Quizzes (1 per concept) + 4 Mixed Quizzes
# ============================================================

QUIZZES = [
    # ============================================================
    # MODULE 1: INTERPOLATION
    # ============================================================
    {
        "titre": "Polynomial Basics",
        "module": "Interpolation",
        "difficulte": "facile",
        "questions": [
            {
                "id": 1,
                "question": "What is the degree of the polynomial P(x) = 3x⁴ + 2x² - 5?",
                "options": ["2", "3", "4", "5"],
                "correct_index": 2,
                "points": 1
            },
            {
                "id": 2,
                "question": "How many roots (real or complex) does a polynomial of degree n have at most?",
                "options": ["n - 1", "n", "n + 1", "2n"],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 3,
                "question": "If P(x) is a polynomial of degree 3, how many coefficients are needed to fully define it?",
                "options": ["3", "4", "5", "6"],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 4,
                "question": "What is the general form of a degree-2 polynomial?",
                "options": ["ax + b", "ax² + bx + c", "ax³ + bx² + cx + d", "a/x + b"],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 5,
                "question": "An interpolating polynomial of degree n passes through how many points?",
                "options": ["n - 1", "n", "n + 1", "2n"],
                "correct_index": 2,
                "points": 1
            }
        ]
    },
    {
        "titre": "Lagrange Interpolation",
        "module": "Interpolation",
        "difficulte": "moyen",
        "questions": [
            {
                "id": 1,
                "question": "In the Lagrange formula, what is the value of the basis polynomial Lᵢ(xᵢ)?",
                "options": ["0", "1", "xᵢ", "n"],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 2,
                "question": "For n+1 distinct points, what is the maximum degree of the Lagrange polynomial?",
                "options": ["n - 1", "n", "n + 1", "2n"],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 3,
                "question": "What is the value of Lᵢ(xⱼ) when i ≠ j?",
                "options": ["0", "1", "-1", "xⱼ"],
                "correct_index": 0,
                "points": 1
            },
            {
                "id": 4,
                "question": "What is the main drawback of Lagrange interpolation when adding a new point?",
                "options": [
                    "The polynomial becomes unstable",
                    "All basis polynomials must be recalculated",
                    "The degree does not change",
                    "The coefficients remain identical"
                ],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 5,
                "question": "Lagrange interpolation guarantees that the polynomial passes through:",
                "options": [
                    "Only some of the points",
                    "All given points exactly",
                    "No point exactly",
                    "Only the endpoints"
                ],
                "correct_index": 1,
                "points": 1
            }
        ]
    },
    {
        "titre": "Divided Differences",
        "module": "Interpolation",
        "difficulte": "moyen",
        "questions": [
            {
                "id": 1,
                "question": "The first-order divided difference f[xᵢ, xᵢ₊₁] is defined as:",
                "options": [
                    "f(xᵢ₊₁) - f(xᵢ)",
                    "(f(xᵢ₊₁) - f(xᵢ)) / (xᵢ₊₁ - xᵢ)",
                    "f(xᵢ) × f(xᵢ₊₁)",
                    "(xᵢ₊₁ - xᵢ) / (f(xᵢ₊₁) - f(xᵢ))"
                ],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 2,
                "question": "Divided differences are primarily used to construct:",
                "options": [
                    "The Lagrange polynomial",
                    "The Newton polynomial",
                    "Cubic splines",
                    "Gaussian quadrature"
                ],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 3,
                "question": "How are divided differences organized for computation?",
                "options": [
                    "In a square matrix",
                    "In a triangular table",
                    "In a linear vector",
                    "In a binary tree"
                ],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 4,
                "question": "A divided difference of order k uses how many points?",
                "options": ["k", "k + 1", "k - 1", "2k"],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 5,
                "question": "If all points are equally spaced (constant h), divided differences simplify to:",
                "options": [
                    "Finite differences divided by powers of h",
                    "Exact derivatives",
                    "Numerical integrals",
                    "Constant values"
                ],
                "correct_index": 0,
                "points": 1
            }
        ]
    },
    {
        "titre": "Newton Interpolation",
        "module": "Interpolation",
        "difficulte": "moyen",
        "questions": [
            {
                "id": 1,
                "question": "What advantage does Newton's form have over Lagrange's form?",
                "options": [
                    "It is more accurate",
                    "You can add a point without recalculating everything",
                    "It uses less memory",
                    "It always converges"
                ],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 2,
                "question": "In Newton's form, P(x) = f[x₀] + f[x₀,x₁](x-x₀) + ... The term f[x₀,x₁,...,xₙ] is:",
                "options": [
                    "A derivative",
                    "A divided difference of order n",
                    "A Lagrange coefficient",
                    "An integral"
                ],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 3,
                "question": "Newton's polynomial of degree n requires computing how many divided differences in total?",
                "options": [
                    "n",
                    "n + 1",
                    "n(n+1)/2",
                    "n²"
                ],
                "correct_index": 2,
                "points": 1
            },
            {
                "id": 4,
                "question": "For 4 data points, Newton's polynomial will have degree:",
                "options": ["2", "3", "4", "5"],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 5,
                "question": "Newton's forward form uses divided differences starting from:",
                "options": [
                    "The end of the table",
                    "The middle of the table",
                    "The beginning of the table (x₀)",
                    "Any arbitrary point"
                ],
                "correct_index": 2,
                "points": 1
            }
        ]
    },
    {
        "titre": "Spline Interpolation",
        "module": "Interpolation",
        "difficulte": "difficile",
        "questions": [
            {
                "id": 1,
                "question": "Why do we use splines instead of a high-degree polynomial?",
                "options": [
                    "Splines are faster to compute",
                    "High-degree polynomials oscillate (Runge's phenomenon)",
                    "Splines use less memory",
                    "Polynomials do not pass through the points"
                ],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 2,
                "question": "A cubic spline is a polynomial of degree __ on each interval.",
                "options": ["1", "2", "3", "4"],
                "correct_index": 2,
                "points": 1
            },
            {
                "id": 3,
                "question": "What continuity condition does a cubic spline satisfy at interior knots?",
                "options": [
                    "Continuity of the function only",
                    "Continuity of the function and first derivative",
                    "Continuity of the function, first derivative, and second derivative",
                    "Continuity up to the third derivative"
                ],
                "correct_index": 2,
                "points": 1
            },
            {
                "id": 4,
                "question": "Natural splines impose what condition at the endpoints?",
                "options": [
                    "First derivative = 0",
                    "Second derivative = 0",
                    "The function = 0",
                    "Third derivative = 0"
                ],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 5,
                "question": "For n+1 points, how many cubic polynomial pieces does a cubic spline contain?",
                "options": ["n - 1", "n", "n + 1", "2n"],
                "correct_index": 1,
                "points": 1
            }
        ]
    },

    # ============================================================
    # MODULE 2: NUMERICAL INTEGRATION
    # ============================================================
    {
        "titre": "Riemann Sums",
        "module": "Numerical Integration",
        "difficulte": "facile",
        "questions": [
            {
                "id": 1,
                "question": "The principle of Riemann sums is to approximate the integral using:",
                "options": ["Triangles", "Rectangles", "Parabolas", "Circles"],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 2,
                "question": "When the number of sub-intervals n → ∞, the Riemann sum converges to:",
                "options": ["Zero", "Infinity", "The exact definite integral", "The derivative of the function"],
                "correct_index": 2,
                "points": 1
            },
            {
                "id": 3,
                "question": "In the left Riemann sum, the function is evaluated at:",
                "options": [
                    "The midpoint of each interval",
                    "The left endpoint of each interval",
                    "The right endpoint of each interval",
                    "Both endpoints"
                ],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 4,
                "question": "If h is the width of each sub-interval and n is the number of sub-intervals, then h =",
                "options": ["(b-a)/n", "(b+a)/n", "n/(b-a)", "(b-a)×n"],
                "correct_index": 0,
                "points": 1
            },
            {
                "id": 5,
                "question": "The error of Riemann sums is of order:",
                "options": ["O(h)", "O(h²)", "O(h³)", "O(h⁴)"],
                "correct_index": 0,
                "points": 1
            }
        ]
    },
    {
        "titre": "Definite Integrals — Foundations",
        "module": "Numerical Integration",
        "difficulte": "facile",
        "questions": [
            {
                "id": 1,
                "question": "The definite integral ∫ₐᵇ f(x)dx geometrically represents:",
                "options": [
                    "The slope of f",
                    "The area under the curve of f between a and b",
                    "The maximum value of f",
                    "The length of the curve"
                ],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 2,
                "question": "If f(x) < 0 on [a,b], the definite integral is:",
                "options": ["Positive", "Negative", "Zero", "Undefined"],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 3,
                "question": "∫ₐᵃ f(x)dx = ?",
                "options": ["f(a)", "1", "0", "∞"],
                "correct_index": 2,
                "points": 1
            },
            {
                "id": 4,
                "question": "The property ∫ₐᵇ f(x)dx = -∫ᵇₐ f(x)dx is called:",
                "options": ["Linearity", "Antisymmetry of bounds", "Additivity", "Positivity"],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 5,
                "question": "Why do we need numerical methods to compute integrals?",
                "options": [
                    "Computers do not understand integrals",
                    "Many functions have no known analytical antiderivative",
                    "Integrals are always approximate",
                    "It is faster than exact computation"
                ],
                "correct_index": 1,
                "points": 1
            }
        ]
    },
    {
        "titre": "Trapezoidal Rule",
        "module": "Numerical Integration",
        "difficulte": "moyen",
        "questions": [
            {
                "id": 1,
                "question": "The trapezoidal rule approximates the function on each interval by:",
                "options": ["A constant", "A straight line (segment)", "A parabola", "A cubic polynomial"],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 2,
                "question": "The error of the composite trapezoidal rule is of order:",
                "options": ["O(h)", "O(h²)", "O(h³)", "O(h⁴)"],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 3,
                "question": "The simple trapezoidal formula between a and b is:",
                "options": [
                    "(b-a) × f(a)",
                    "(b-a) × (f(a) + f(b)) / 2",
                    "(b-a) × f((a+b)/2)",
                    "(b-a)² × f'(a)"
                ],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 4,
                "question": "For a linear function f(x) = mx + p, the trapezoidal rule gives:",
                "options": [
                    "An approximation with error",
                    "The exact result",
                    "Always zero",
                    "A negative value"
                ],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 5,
                "question": "If we double the number of sub-intervals n, the trapezoidal error:",
                "options": [
                    "Is divided by 2",
                    "Is divided by 4",
                    "Is divided by 8",
                    "Stays the same"
                ],
                "correct_index": 1,
                "points": 1
            }
        ]
    },
    {
        "titre": "Simpson's Rule",
        "module": "Numerical Integration",
        "difficulte": "moyen",
        "questions": [
            {
                "id": 1,
                "question": "Simpson's rule approximates the function on each interval by:",
                "options": ["A segment", "A parabola", "A cubic polynomial", "An exponential"],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 2,
                "question": "The convergence order of Simpson's rule is:",
                "options": ["O(h²)", "O(h³)", "O(h⁴)", "O(h⁵)"],
                "correct_index": 2,
                "points": 1
            },
            {
                "id": 3,
                "question": "Simpson's rule requires the number of sub-intervals to be:",
                "options": ["Any", "Even", "Odd", "A multiple of 3"],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 4,
                "question": "The simple Simpson 1/3 formula uses how many points?",
                "options": ["2", "3", "4", "5"],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 5,
                "question": "Simpson's rule is exact for polynomials of degree ≤:",
                "options": ["1", "2", "3", "4"],
                "correct_index": 2,
                "points": 1
            }
        ]
    },
    {
        "titre": "Gaussian Quadrature",
        "module": "Numerical Integration",
        "difficulte": "difficile",
        "questions": [
            {
                "id": 1,
                "question": "What is the main advantage of Gaussian quadrature over trapezoids/Simpson?",
                "options": [
                    "It is simpler to program",
                    "It achieves maximum accuracy with minimum points",
                    "It only works on infinite intervals",
                    "It requires no computation"
                ],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 2,
                "question": "The nodes of Gauss-Legendre quadrature are the roots of:",
                "options": [
                    "Taylor polynomials",
                    "Lagrange polynomials",
                    "Legendre polynomials",
                    "Chebyshev polynomials"
                ],
                "correct_index": 2,
                "points": 1
            },
            {
                "id": 3,
                "question": "With n points, Gaussian quadrature is exact for polynomials of degree ≤:",
                "options": ["n", "n + 1", "2n - 1", "2n"],
                "correct_index": 2,
                "points": 1
            },
            {
                "id": 4,
                "question": "The standard interval for Gauss-Legendre quadrature is:",
                "options": ["[0, 1]", "[-1, 1]", "[0, ∞]", "[-∞, ∞]"],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 5,
                "question": "To apply Gauss-Legendre on any [a, b], we use:",
                "options": [
                    "A linear change of variable",
                    "A logarithmic transformation",
                    "Taylor's formula",
                    "No transformation"
                ],
                "correct_index": 0,
                "points": 1
            }
        ]
    },

    # ============================================================
    # MODULE 3: ORDINARY DIFFERENTIAL EQUATIONS (ODEs)
    # ============================================================
    {
        "titre": "Initial Value Problems",
        "module": "ODEs",
        "difficulte": "facile",
        "questions": [
            {
                "id": 1,
                "question": "An initial value problem (IVP) is defined by:",
                "options": [
                    "A differential equation + a boundary condition",
                    "A differential equation + an initial condition y(t₀) = y₀",
                    "Two differential equations",
                    "An integral + a derivative"
                ],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 2,
                "question": "In y' = f(t, y), y(0) = 1, what does y' represent?",
                "options": [
                    "The value of y",
                    "The derivative of y with respect to t",
                    "The integral of y",
                    "The square of y"
                ],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 3,
                "question": "Why do we solve ODEs numerically rather than analytically?",
                "options": [
                    "It is always more accurate",
                    "Many ODEs have no known analytical solution",
                    "Analytical solutions are always wrong",
                    "Computers prefer numbers"
                ],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 4,
                "question": "The time step h in numerical ODE methods represents:",
                "options": [
                    "The height of the curve",
                    "The interval between two points of the discrete solution",
                    "The maximum error",
                    "The number of iterations"
                ],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 5,
                "question": "If we reduce the step h, the numerical solution generally becomes:",
                "options": [
                    "Less accurate",
                    "More accurate but more computationally expensive",
                    "Identical",
                    "Unstable"
                ],
                "correct_index": 1,
                "points": 1
            }
        ]
    },
    {
        "titre": "Taylor Series",
        "module": "ODEs",
        "difficulte": "moyen",
        "questions": [
            {
                "id": 1,
                "question": "The Taylor expansion of f(x) around x₀ uses:",
                "options": [
                    "The integrals of f",
                    "The successive derivatives of f at x₀",
                    "The roots of f",
                    "The values of f at integer points"
                ],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 2,
                "question": "The n-th order Taylor term is proportional to:",
                "options": ["(x - x₀)ⁿ", "xⁿ", "1/n", "eⁿ"],
                "correct_index": 0,
                "points": 1
            },
            {
                "id": 3,
                "question": "The first-order Taylor approximation of f(x₀ + h) is:",
                "options": [
                    "f(x₀)",
                    "f(x₀) + h × f'(x₀)",
                    "f(x₀) + h² × f''(x₀)/2",
                    "h × f(x₀)"
                ],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 4,
                "question": "The remainder (truncation error) of an order-n Taylor expansion is of order:",
                "options": ["O(hⁿ)", "O(hⁿ⁺¹)", "O(h)", "O(1/n)"],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 5,
                "question": "The Taylor method for ODEs is rarely used in practice because:",
                "options": [
                    "It always diverges",
                    "It requires computing higher-order derivatives of f",
                    "It is less accurate than Euler",
                    "It does not work with computers"
                ],
                "correct_index": 1,
                "points": 1
            }
        ]
    },
    {
        "titre": "Euler's Method",
        "module": "ODEs",
        "difficulte": "moyen",
        "questions": [
            {
                "id": 1,
                "question": "The explicit Euler formula is:",
                "options": [
                    "yₙ₊₁ = yₙ + h × f(tₙ, yₙ)",
                    "yₙ₊₁ = yₙ × h + f(tₙ, yₙ)",
                    "yₙ₊₁ = yₙ - h × f(tₙ, yₙ)",
                    "yₙ₊₁ = h × f(tₙ₊₁, yₙ₊₁)"
                ],
                "correct_index": 0,
                "points": 1
            },
            {
                "id": 2,
                "question": "The local truncation error of Euler's method is of order:",
                "options": ["O(h)", "O(h²)", "O(h³)", "O(h⁴)"],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 3,
                "question": "The global error of Euler's method is of order:",
                "options": ["O(h)", "O(h²)", "O(h³)", "O(h⁴)"],
                "correct_index": 0,
                "points": 1
            },
            {
                "id": 4,
                "question": "Euler's method is derived from the Taylor expansion by keeping:",
                "options": [
                    "Only the order-0 term",
                    "The order-0 and order-1 terms",
                    "Terms up to order 2",
                    "All terms"
                ],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 5,
                "question": "Geometrically, Euler's method follows:",
                "options": [
                    "The tangent line to the solution curve at each point",
                    "The normal to the curve",
                    "A circular arc",
                    "A parabola"
                ],
                "correct_index": 0,
                "points": 1
            }
        ]
    },
    {
        "titre": "Improved Euler (Heun's Method)",
        "module": "ODEs",
        "difficulte": "moyen",
        "questions": [
            {
                "id": 1,
                "question": "Heun's method uses how many evaluations of f per step?",
                "options": ["1", "2", "3", "4"],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 2,
                "question": "The convergence order of Heun's method is:",
                "options": ["1", "2", "3", "4"],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 3,
                "question": "Heun's method is also called:",
                "options": [
                    "Implicit Euler",
                    "The trapezoidal method for ODEs",
                    "Simpson's method for ODEs",
                    "Backward Euler"
                ],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 4,
                "question": "In Heun's method, the final slope is computed as:",
                "options": [
                    "The slope at the beginning",
                    "The slope at the end (prediction)",
                    "The average of the slopes at the beginning and end",
                    "The product of the slopes"
                ],
                "correct_index": 2,
                "points": 1
            },
            {
                "id": 5,
                "question": "Compared to simple Euler, Heun is:",
                "options": [
                    "Less accurate but faster",
                    "More accurate thanks to slope correction",
                    "Identical in accuracy",
                    "Faster but less stable"
                ],
                "correct_index": 1,
                "points": 1
            }
        ]
    },
    {
        "titre": "Runge-Kutta Method (RK4)",
        "module": "ODEs",
        "difficulte": "difficile",
        "questions": [
            {
                "id": 1,
                "question": "How many evaluations of f does the classical RK4 method perform per step?",
                "options": ["2", "3", "4", "5"],
                "correct_index": 2,
                "points": 1
            },
            {
                "id": 2,
                "question": "The local error of RK4 is of order:",
                "options": ["O(h²)", "O(h³)", "O(h⁴)", "O(h⁵)"],
                "correct_index": 3,
                "points": 1
            },
            {
                "id": 3,
                "question": "In the RK4 formula, yₙ₊₁ = yₙ + (h/6)(k₁ + 2k₂ + 2k₃ + k₄), the weights (1,2,2,1) mean:",
                "options": [
                    "All slopes have equal weight",
                    "The midpoint slopes count double",
                    "The first slope is most important",
                    "The last slope is most important"
                ],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 4,
                "question": "RK4 is preferred over order-4 Taylor method because:",
                "options": [
                    "RK4 is more accurate",
                    "RK4 does not require computing partial derivatives of f",
                    "RK4 uses fewer evaluations",
                    "Order-4 Taylor does not exist"
                ],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 5,
                "question": "The global error of RK4 is of order:",
                "options": ["O(h²)", "O(h³)", "O(h⁴)", "O(h⁵)"],
                "correct_index": 2,
                "points": 1
            }
        ]
    },

    # ============================================================
    # MIXED QUIZZES — Cross-topic assessments
    # ============================================================
    {
        "titre": "Mixed Quiz — Complete Interpolation",
        "module": "Interpolation",
        "difficulte": "difficile",
        "questions": [
            {
                "id": 1,
                "question": "Runge's phenomenon occurs when using:",
                "options": [
                    "Cubic splines",
                    "A high-degree polynomial with equidistant points",
                    "Simpson's rule",
                    "Gaussian quadrature"
                ],
                "correct_index": 1,
                "points": 2
            },
            {
                "id": 2,
                "question": "The uniqueness theorem for polynomial interpolation states that for n+1 distinct points, there exists:",
                "options": [
                    "No polynomial",
                    "Exactly one polynomial of degree ≤ n",
                    "Multiple polynomials of degree ≤ n",
                    "A polynomial of degree exactly n"
                ],
                "correct_index": 1,
                "points": 2
            },
            {
                "id": 3,
                "question": "Lagrange, Newton, and divided differences produce:",
                "options": [
                    "Different polynomials",
                    "The same polynomial written differently",
                    "Approximations of different accuracy",
                    "Incompatible results"
                ],
                "correct_index": 1,
                "points": 2
            }
        ]
    },
    {
        "titre": "Mixed Quiz — Complete Integration",
        "module": "Numerical Integration",
        "difficulte": "difficile",
        "questions": [
            {
                "id": 1,
                "question": "Rank these methods by increasing accuracy:",
                "options": [
                    "Simpson < Trapezoidal < Riemann",
                    "Riemann < Trapezoidal < Simpson",
                    "Trapezoidal < Riemann < Simpson",
                    "Riemann < Simpson < Trapezoidal"
                ],
                "correct_index": 1,
                "points": 2
            },
            {
                "id": 2,
                "question": "If h is halved, Simpson's error is divided by:",
                "options": ["2", "4", "8", "16"],
                "correct_index": 3,
                "points": 2
            },
            {
                "id": 3,
                "question": "Gauss quadrature with 2 points is exact for polynomials of degree ≤:",
                "options": ["1", "2", "3", "4"],
                "correct_index": 2,
                "points": 2
            }
        ]
    },
    {
        "titre": "Mixed Quiz — Complete ODEs",
        "module": "ODEs",
        "difficulte": "difficile",
        "questions": [
            {
                "id": 1,
                "question": "Rank these methods by increasing accuracy:",
                "options": [
                    "RK4 < Heun < Euler",
                    "Euler < Heun < RK4",
                    "Heun < Euler < RK4",
                    "Euler < RK4 < Heun"
                ],
                "correct_index": 1,
                "points": 2
            },
            {
                "id": 2,
                "question": "If h is halved, Euler's global error is divided by:",
                "options": ["2", "4", "8", "16"],
                "correct_index": 0,
                "points": 2
            },
            {
                "id": 3,
                "question": "If h is halved, RK4's global error is divided by:",
                "options": ["2", "4", "8", "16"],
                "correct_index": 3,
                "points": 2
            }
        ]
    },
    {
        "titre": "Diagnostic Assessment — General Prerequisites",
        "module": "Prerequisites",
        "difficulte": "facile",
        "questions": [
            {
                "id": 1,
                "question": "The derivative of f(x) = x³ is:",
                "options": ["x²", "3x²", "3x³", "x⁴/4"],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 2,
                "question": "∫ 2x dx = ?",
                "options": ["2x²", "x²", "x² + C", "2x² + C"],
                "correct_index": 2,
                "points": 1
            },
            {
                "id": 3,
                "question": "In Python, how do you create a NumPy array of 10 zeros?",
                "options": [
                    "np.array(10)",
                    "np.zeros(10)",
                    "np.empty(10)",
                    "np.zero(10)"
                ],
                "correct_index": 1,
                "points": 1
            },
            {
                "id": 4,
                "question": "The absolute value of -7 is:",
                "options": ["-7", "0", "7", "49"],
                "correct_index": 2,
                "points": 1
            },
            {
                "id": 5,
                "question": "A 3×3 matrix has how many elements?",
                "options": ["3", "6", "9", "27"],
                "correct_index": 2,
                "points": 1
            }
        ]
    }
]


def seed_quizzes():
    """Insert all quizzes into PostgreSQL."""
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        logger.error("DATABASE_URL missing from .env")
        sys.exit(1)

    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Important : on importe TOUS les modeles dont Quiz depend via FK
        # (etudiant, mastery, tutor) sinon SQLAlchemy ne peut pas resoudre
        # la foreign key quiz.etudiant_generateur_id -> etudiants.id et leve
        # NoReferencedTableError. C'est une subtilite des scripts standalone :
        # contrairement au backend FastAPI qui importe tous les modeles via
        # `from app.routers import ...`, ici on doit le faire manuellement.
        from app.models import etudiant, mastery, quiz as quiz_module, tutor  # noqa: F401
        from app.models.quiz import Quiz

        existing = session.query(Quiz).count()
        if existing > 0:
            logger.warning(f"{existing} quizzes already in DB. Deleting and recreating...")
            session.query(Quiz).delete()
            session.commit()

        for i, quiz_data in enumerate(QUIZZES):
            quiz = Quiz(
                titre=quiz_data["titre"],
                module=quiz_data["module"],
                difficulte=quiz_data["difficulte"],
                questions=quiz_data["questions"]
            )
            session.add(quiz)
            logger.info(f"  Quiz {i+1}/{len(QUIZZES)}: {quiz_data['titre']} ({quiz_data['module']}, {quiz_data['difficulte']}, {len(quiz_data['questions'])} questions)")

        session.commit()

        total_quizzes = len(QUIZZES)
        total_questions = sum(len(q["questions"]) for q in QUIZZES)
        modules = set(q["module"] for q in QUIZZES)

        logger.info(f"\n{'='*60}")
        logger.info("QUESTION BANK POPULATED SUCCESSFULLY")
        logger.info(f"{'='*60}")
        logger.info(f"  Quizzes created  : {total_quizzes}")
        logger.info(f"  Total questions  : {total_questions}")
        logger.info(f"  Modules covered  : {', '.join(sorted(modules))}")
        logger.info("  Difficulties     : facile, moyen, difficile")
        logger.info(f"{'='*60}\n")

    except Exception as e:
        session.rollback()
        logger.error(f"Error: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_quizzes()
