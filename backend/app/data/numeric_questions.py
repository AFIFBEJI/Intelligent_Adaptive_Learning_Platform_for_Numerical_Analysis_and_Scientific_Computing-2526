"""
Numeric calculation questions (deterministic grading, NO AI).

Each question asks the student to TYPE A SINGLE NUMBER. The answer is graded
by comparing the typed number to the expected one within a tolerance, in
pure Python (see feedback_service._eval_numeric). This is reliable, instant
and well suited to mathematics: the student types a value, not a formula.

All expected answers were verified programmatically.
Structure per question:
    question_fr / question_en : the wording (math in $...$ for KaTeX)
    answer                    : the expected numeric value (float)
    tolerance                 : accepted absolute gap
    explanation_fr / _en      : short explanation shown in the feedback
"""
from __future__ import annotations

import random

# concept_id -> list of numeric questions
NUMERIC_QUESTIONS: dict[str, list[dict]] = {
    "concept_polynomial_basics": [
        {
            "question_fr": "Soit $p(x) = 0.3x^3 - 1.2x^2 + x + 2$. Calcule $p(2)$.",
            "question_en": "Let $p(x) = 0.3x^3 - 1.2x^2 + x + 2$. Compute $p(2)$.",
            "answer": 1.6, "tolerance": 0.05,
            "explanation_fr": "$p(2) = 0.3(8) - 1.2(4) + 2 + 2 = 1.6$.",
            "explanation_en": "$p(2) = 0.3(8) - 1.2(4) + 2 + 2 = 1.6$.",
        },
    ],
    "concept_lagrange": [
        {
            "question_fr": "Points $(0,1),(1,3),(2,2)$. Donne la valeur de l'interpolant de Lagrange $P(0.5)$.",
            "question_en": "Points $(0,1),(1,3),(2,2)$. Give the Lagrange interpolant value $P(0.5)$.",
            "answer": 2.375, "tolerance": 0.02,
            "explanation_fr": "En combinant les bases de Lagrange : $P(0.5) = 2.375$.",
            "explanation_en": "Combining the Lagrange bases: $P(0.5) = 2.375$.",
        },
    ],
    "concept_divided_differences": [
        {
            "question_fr": "Points $(0,1),(1,3)$. Calcule la difference divisee $f[x_0,x_1] = \\frac{y_1-y_0}{x_1-x_0}$.",
            "question_en": "Points $(0,1),(1,3)$. Compute the divided difference $f[x_0,x_1] = \\frac{y_1-y_0}{x_1-x_0}$.",
            "answer": 2.0, "tolerance": 0.05,
            "explanation_fr": "$f[x_0,x_1] = (3-1)/(1-0) = 2$.",
            "explanation_en": "$f[x_0,x_1] = (3-1)/(1-0) = 2$.",
        },
    ],
    "concept_newton_interpolation": [
        {
            "question_fr": "Points $(1,3),(2,2)$. Calcule $f[x_1,x_2] = \\frac{2-3}{2-1}$.",
            "question_en": "Points $(1,3),(2,2)$. Compute $f[x_1,x_2] = \\frac{2-3}{2-1}$.",
            "answer": -1.0, "tolerance": 0.05,
            "explanation_fr": "$f[x_1,x_2] = (2-3)/(2-1) = -1$.",
            "explanation_en": "$f[x_1,x_2] = (2-3)/(2-1) = -1$.",
        },
    ],
    "concept_spline_interpolation": [
        {
            "question_fr": "Pour une spline cubique NATURELLE, quelle valeur impose-t-on a la derivee seconde aux deux bords ?",
            "question_en": "For a NATURAL cubic spline, which value is imposed on the second derivative at both ends?",
            "answer": 0.0, "tolerance": 0.001,
            "explanation_fr": "La condition naturelle impose $S''=0$ aux extremites.",
            "explanation_en": "The natural condition imposes $S''=0$ at the endpoints.",
        },
    ],
    "concept_riemann_sums": [
        {
            "question_fr": "$f(x)=x^2$ sur $[0,2]$, $n=4$ (pas $h=0.5$). Calcule la somme de Riemann a GAUCHE $L_4$.",
            "question_en": "$f(x)=x^2$ on $[0,2]$, $n=4$ (step $h=0.5$). Compute the LEFT Riemann sum $L_4$.",
            "answer": 1.75, "tolerance": 0.02,
            "explanation_fr": "$L_4 = 0.5(0 + 0.25 + 1 + 2.25) = 1.75$.",
            "explanation_en": "$L_4 = 0.5(0 + 0.25 + 1 + 2.25) = 1.75$.",
        },
    ],
    "concept_definite_integrals": [
        {
            "question_fr": "Calcule $\\int_0^2 (x^2 - 1)\\,dx$.",
            "question_en": "Compute $\\int_0^2 (x^2 - 1)\\,dx$.",
            "answer": 0.6667, "tolerance": 0.02,
            "explanation_fr": "$\\int_0^2 (x^2-1)dx = 8/3 - 2 = 2/3 \\approx 0.667$.",
            "explanation_en": "$\\int_0^2 (x^2-1)dx = 8/3 - 2 = 2/3 \\approx 0.667$.",
        },
    ],
    "concept_trapezoidal": [
        {
            "question_fr": "$f(x)=x^2$ sur $[0,2]$, $n=2$ (h=1). Calcule la regle du trapeze $T_2 = \\frac{h}{2}(f_0 + 2f_1 + f_2)$.",
            "question_en": "$f(x)=x^2$ on $[0,2]$, $n=2$ (h=1). Compute the trapezoidal rule $T_2 = \\frac{h}{2}(f_0 + 2f_1 + f_2)$.",
            "answer": 3.0, "tolerance": 0.05,
            "explanation_fr": "$T_2 = \\tfrac{1}{2}(0 + 2(1) + 4) = 3$.",
            "explanation_en": "$T_2 = \\tfrac{1}{2}(0 + 2(1) + 4) = 3$.",
        },
    ],
    "concept_simpson": [
        {
            "question_fr": "$f(x)=x^3-2x^2+2$ sur $[0,2]$, $n=2$ (h=1). Calcule Simpson $S_2 = \\frac{h}{3}(f_0 + 4f_1 + f_2)$.",
            "question_en": "$f(x)=x^3-2x^2+2$ on $[0,2]$, $n=2$ (h=1). Compute Simpson $S_2 = \\frac{h}{3}(f_0 + 4f_1 + f_2)$.",
            "answer": 2.6667, "tolerance": 0.03,
            "explanation_fr": "$S_2 = \\tfrac{1}{3}(2 + 4(1) + 2) = 8/3 \\approx 2.667$.",
            "explanation_en": "$S_2 = \\tfrac{1}{3}(2 + 4(1) + 2) = 8/3 \\approx 2.667$.",
        },
    ],
    "concept_gaussian_quadrature": [
        {
            "question_fr": "Quadrature de Gauss-Legendre a 2 points sur $[-1,1]$. Donne la valeur POSITIVE du noeud $x = 1/\\sqrt{3}$ (4 decimales).",
            "question_en": "2-point Gauss-Legendre quadrature on $[-1,1]$. Give the POSITIVE node value $x = 1/\\sqrt{3}$ (4 decimals).",
            "answer": 0.5774, "tolerance": 0.01,
            "explanation_fr": "Les noeuds sont $\\pm 1/\\sqrt{3} \\approx \\pm 0.5774$.",
            "explanation_en": "The nodes are $\\pm 1/\\sqrt{3} \\approx \\pm 0.5774$.",
        },
    ],
    "concept_least_squares": [
        {
            "question_fr": "Points $(0,1),(1,2),(2,2),(3,4)$. Calcule la pente $a$ de la droite des moindres carres.",
            "question_en": "Points $(0,1),(1,2),(2,2),(3,4)$. Compute the slope $a$ of the least-squares line.",
            "answer": 0.9, "tolerance": 0.05,
            "explanation_fr": "$a = (4\\cdot 18 - 6\\cdot 9)/(4\\cdot 14 - 36) = 0.9$.",
            "explanation_en": "$a = (4\\cdot 18 - 6\\cdot 9)/(4\\cdot 14 - 36) = 0.9$.",
        },
    ],
    "concept_orthogonal_polynomials": [
        {
            "question_fr": "Produit scalaire de Legendre sur $[-1,1]$ : calcule $\\langle P_1,P_1\\rangle = \\int_{-1}^{1} x^2\\,dx$.",
            "question_en": "Legendre inner product on $[-1,1]$: compute $\\langle P_1,P_1\\rangle = \\int_{-1}^{1} x^2\\,dx$.",
            "answer": 0.6667, "tolerance": 0.02,
            "explanation_fr": "$\\int_{-1}^{1} x^2 dx = 2/3 \\approx 0.667$.",
            "explanation_en": "$\\int_{-1}^{1} x^2 dx = 2/3 \\approx 0.667$.",
        },
    ],
    "concept_minimax_approximation": [
        {
            "question_fr": "D'apres le theoreme d'equioscillation, combien de points d'alternance pour la meilleure approximation par une DROITE ?",
            "question_en": "By the equioscillation theorem, how many alternation points for the best approximation by a LINE?",
            "answer": 3.0, "tolerance": 0.001,
            "explanation_fr": "Pour un polynome de degre $n$, il faut $n+2$ points ; pour une droite ($n=1$) : 3.",
            "explanation_en": "For a degree-$n$ polynomial you need $n+2$ points; for a line ($n=1$): 3.",
        },
    ],
    "concept_gradient_descent": [
        {
            "question_fr": "$f(x)=x^2-4x+5$, $x_0=0$, pas $\\alpha=0.25$. Calcule $x_1 = x_0 - \\alpha f'(x_0)$ avec $f'(x)=2x-4$.",
            "question_en": "$f(x)=x^2-4x+5$, $x_0=0$, step $\\alpha=0.25$. Compute $x_1 = x_0 - \\alpha f'(x_0)$ with $f'(x)=2x-4$.",
            "answer": 1.0, "tolerance": 0.05,
            "explanation_fr": "$x_1 = 0 - 0.25(-4) = 1$.",
            "explanation_en": "$x_1 = 0 - 0.25(-4) = 1$.",
        },
    ],
    "concept_newton_optimization": [
        {
            "question_fr": "$f(x)=x^2-4x+5$, $x_0=0$. Newton pour l'optimisation : $x_1 = x_0 - f'(x_0)/f''(x_0)$, $f''=2$. Calcule $x_1$.",
            "question_en": "$f(x)=x^2-4x+5$, $x_0=0$. Newton for optimization: $x_1 = x_0 - f'(x_0)/f''(x_0)$, $f''=2$. Compute $x_1$.",
            "answer": 2.0, "tolerance": 0.05,
            "explanation_fr": "$x_1 = 0 - (-4)/2 = 2$ : le minimum est atteint en un pas.",
            "explanation_en": "$x_1 = 0 - (-4)/2 = 2$: the minimum is reached in one step.",
        },
    ],
    "concept_bissection": [
        {
            "question_fr": "$f(x)=x^2-2$ sur $[1,2]$. Calcule le milieu $m = \\frac{1+2}{2}$ de la premiere iteration de dichotomie.",
            "question_en": "$f(x)=x^2-2$ on $[1,2]$. Compute the midpoint $m = \\frac{1+2}{2}$ of the first bisection step.",
            "answer": 1.5, "tolerance": 0.02,
            "explanation_fr": "$m = (1+2)/2 = 1.5$.",
            "explanation_en": "$m = (1+2)/2 = 1.5$.",
        },
    ],
    "concept_fixed_point": [
        {
            "question_fr": "$f(x)=x^2-2$ reecrite $x=g(x)=\\frac{1}{2}(x + 2/x)$ (Heron), $x_0=2$. Calcule $x_1 = g(2)$.",
            "question_en": "$f(x)=x^2-2$ rewritten $x=g(x)=\\frac{1}{2}(x + 2/x)$ (Heron), $x_0=2$. Compute $x_1 = g(2)$.",
            "answer": 1.5, "tolerance": 0.02,
            "explanation_fr": "$x_1 = \\tfrac{1}{2}(2 + 1) = 1.5$.",
            "explanation_en": "$x_1 = \\tfrac{1}{2}(2 + 1) = 1.5$.",
        },
    ],
    "concept_newton_raphson": [
        {
            "question_fr": "$f(x)=x^2-2$, $f'(x)=2x$, $x_0=2$. Calcule $x_1 = x_0 - f(x_0)/f'(x_0)$.",
            "question_en": "$f(x)=x^2-2$, $f'(x)=2x$, $x_0=2$. Compute $x_1 = x_0 - f(x_0)/f'(x_0)$.",
            "answer": 1.5, "tolerance": 0.02,
            "explanation_fr": "$x_1 = 2 - 2/4 = 1.5$.",
            "explanation_en": "$x_1 = 2 - 2/4 = 1.5$.",
        },
    ],
    "concept_secant": [
        {
            "question_fr": "$f(x)=x^2-2$, $x_0=2$, $x_1=1.5$. Calcule $x_2 = x_1 - f(x_1)\\frac{x_1-x_0}{f(x_1)-f(x_0)}$ (4 decimales).",
            "question_en": "$f(x)=x^2-2$, $x_0=2$, $x_1=1.5$. Compute $x_2 = x_1 - f(x_1)\\frac{x_1-x_0}{f(x_1)-f(x_0)}$ (4 decimals).",
            "answer": 1.4286, "tolerance": 0.01,
            "explanation_fr": "$x_2 = 1.5 - 0.25\\cdot(-0.5)/(0.25-2) \\approx 1.4286$.",
            "explanation_en": "$x_2 = 1.5 - 0.25\\cdot(-0.5)/(0.25-2) \\approx 1.4286$.",
        },
    ],
}


def get_numeric_questions(concept_id: str, n: int = 1, rng: random.Random | None = None) -> list[dict]:
    """Return up to `n` numeric questions for a concept (empty list if none)."""
    pool = NUMERIC_QUESTIONS.get(concept_id, [])
    if not pool:
        return []
    rng = rng or random.Random()
    if n >= len(pool):
        return list(pool)
    return rng.sample(pool, n)
