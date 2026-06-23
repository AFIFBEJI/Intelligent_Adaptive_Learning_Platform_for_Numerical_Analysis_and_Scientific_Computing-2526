#!/usr/bin/env python3
"""
Phase 2 — Sprint 3: Multi-Level Content
Adds Content nodes to Neo4j with 3 levels per concept.
Each content is in Markdown with LaTeX for future RAG indexing.

Usage:
    cd backend
    venv\\Scripts\\activate
    python scripts/seed_content.py
"""

import logging
import os
import sys

from dotenv import load_dotenv
from neo4j import GraphDatabase

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CONTENTS = [
    # ============================================================
    # MODULE 1: INTERPOLATION
    # ============================================================

    # --- Polynomial Basics ---
    {
        "concept_id": "concept_polynomial_basics",
        "level": "simplified",
        "title": "Polynomials made simple",
        "body": """# Polynomials — Simplified Version

A **polynomial** is a math expression with $x$ raised to whole-number powers.

**Example:** $P(x) = 3x^2 + 2x - 5$

- The **degree** is the highest power of $x$. Here the degree is **2**.
- The **coefficients** are the numbers in front of $x$: here 3, 2, and -5.

**Key takeaway:** A polynomial of degree $n$ has exactly $n+1$ coefficients and can pass through $n+1$ points.
"""
    },
    {
        "concept_id": "concept_polynomial_basics",
        "level": "standard",
        "title": "Polynomial fundamentals",
        "body": """# Polynomial Fundamentals

## Formal definition
A polynomial of degree $n$ is a function of the form:
$$P(x) = a_n x^n + a_{n-1} x^{n-1} + \\cdots + a_1 x + a_0$$
where $a_n \\neq 0$ and the $a_i$ are real coefficients.

## Key properties
- **Fundamental Theorem of Algebra**: A polynomial of degree $n$ has exactly $n$ roots (real or complex).
- **Uniqueness**: For $n+1$ distinct points $(x_i, y_i)$, there exists a unique polynomial of degree $\\leq n$ passing through all these points.

## Application to interpolation
Polynomial interpolation consists of finding $P(x)$ such that $P(x_i) = y_i$ for $i = 0, 1, \\ldots, n$.
"""
    },
    {
        "concept_id": "concept_polynomial_basics",
        "level": "rigorous",
        "title": "Interpolation polynomial theory",
        "body": """# Interpolation Polynomial Theory

## Vector space $\\mathbb{P}_n$
The set of polynomials of degree $\\leq n$ forms a vector space of dimension $n+1$ over $\\mathbb{R}$, denoted $\\mathbb{P}_n$.

The canonical basis is $\\{1, x, x^2, \\ldots, x^n\\}$.

## Existence and uniqueness theorem
**Theorem:** Let $(x_0, y_0), \\ldots, (x_n, y_n)$ with distinct $x_i$. There exists a unique $P \\in \\mathbb{P}_n$ such that $P(x_i) = y_i$.

**Proof:** The Vandermonde matrix $V_{ij} = x_i^j$ is invertible if and only if the $x_i$ are distinct, since $\\det(V) = \\prod_{0 \\leq i < j \\leq n}(x_j - x_i) \\neq 0$.

## Interpolation error
$$f(x) - P_n(x) = \\frac{f^{(n+1)}(\\xi)}{(n+1)!} \\prod_{i=0}^{n}(x - x_i)$$
where $\\xi \\in [\\min(x_0,\\ldots,x_n,x), \\max(x_0,\\ldots,x_n,x)]$.
"""
    },

    # --- Lagrange ---
    {
        "concept_id": "concept_lagrange",
        "level": "simplified",
        "title": "Lagrange made simple",
        "body": """# Lagrange Interpolation — Simplified Version

**Idea:** We build a polynomial that passes exactly through given points.

For each point, we create a "basis polynomial" $L_i(x)$ that equals:
- **1** at point $x_i$
- **0** at all other points

Then we combine: $P(x) = y_0 L_0(x) + y_1 L_1(x) + \\cdots + y_n L_n(x)$

**Example with 2 points:** $(1, 3)$ and $(2, 5)$
$$P(x) = 3 \\cdot \\frac{x-2}{1-2} + 5 \\cdot \\frac{x-1}{2-1} = -3(x-2) + 5(x-1) = 2x + 1$$
"""
    },
    {
        "concept_id": "concept_lagrange",
        "level": "standard",
        "title": "Lagrange interpolation method",
        "body": """# Lagrange Interpolation

## Formula
For $n+1$ points $(x_0, y_0), \\ldots, (x_n, y_n)$:
$$P(x) = \\sum_{i=0}^{n} y_i L_i(x)$$

where the Lagrange basis polynomials are:
$$L_i(x) = \\prod_{j=0, j \\neq i}^{n} \\frac{x - x_j}{x_i - x_j}$$

## Properties
- $L_i(x_i) = 1$ and $L_i(x_j) = 0$ for $j \\neq i$
- The resulting polynomial has degree $\\leq n$
- **Drawback**: if a new point is added, everything must be recalculated

## Complexity
Direct computation requires $O(n^2)$ operations.
"""
    },
    {
        "concept_id": "concept_lagrange",
        "level": "rigorous",
        "title": "Lagrange interpolation analysis",
        "body": """# Lagrange Interpolation Analysis

## Rigorous construction
The basis polynomials $\\{L_i\\}_{i=0}^n$ form a basis of $\\mathbb{P}_n$ dual to the evaluation functionals $\\delta_{x_i} : P \\mapsto P(x_i)$.

$$L_i \\in \\mathbb{P}_n, \\quad \\delta_{x_j}(L_i) = \\delta_{ij}$$

## Error bound
For $f \\in C^{n+1}[a,b]$:
$$\\|f - P_n\\|_\\infty \\leq \\frac{\\|f^{(n+1)}\\|_\\infty}{(n+1)!} \\|\\omega_{n+1}\\|_\\infty$$

where $\\omega_{n+1}(x) = \\prod_{i=0}^n (x-x_i)$.

## Runge's phenomenon
For equidistant nodes on $[-5,5]$ with $f(x) = \\frac{1}{1+x^2}$:
$$\\lim_{n \\to \\infty} \\|f - P_n\\|_\\infty = \\infty$$

This phenomenon motivates the use of Chebyshev nodes or splines.
"""
    },

    # --- Divided Differences ---
    {
        "concept_id": "concept_divided_differences",
        "level": "simplified",
        "title": "Divided differences made simple",
        "body": """# Divided Differences — Simplified Version

**Divided differences** are a way to compute coefficients for Newton interpolation.

**First-order divided difference:**
$$f[x_0, x_1] = \\frac{f(x_1) - f(x_0)}{x_1 - x_0}$$

It's simply the **slope** between two points!

**Second order:**
$$f[x_0, x_1, x_2] = \\frac{f[x_1, x_2] - f[x_0, x_1]}{x_2 - x_0}$$

We build a **triangular table** from top to bottom.
"""
    },
    {
        "concept_id": "concept_divided_differences",
        "level": "standard",
        "title": "Divided differences method",
        "body": """# Divided Differences

## Recursive definition
$$f[x_i] = f(x_i)$$
$$f[x_i, \\ldots, x_{i+k}] = \\frac{f[x_{i+1}, \\ldots, x_{i+k}] - f[x_i, \\ldots, x_{i+k-1}]}{x_{i+k} - x_i}$$

## Divided differences table
The computation is organized in a triangular table:

| $x_i$ | $f[x_i]$ | Order 1 | Order 2 | Order 3 |
|--------|-----------|---------|---------|---------|
| $x_0$  | $f[x_0]$ | $f[x_0,x_1]$ | $f[x_0,x_1,x_2]$ | $f[x_0,x_1,x_2,x_3]$ |
| $x_1$  | $f[x_1]$ | $f[x_1,x_2]$ | $f[x_1,x_2,x_3]$ | |
| $x_2$  | $f[x_2]$ | $f[x_2,x_3]$ | | |
| $x_3$  | $f[x_3]$ | | | |

Newton's coefficients are the **first row** of the table.
"""
    },
    {
        "concept_id": "concept_divided_differences",
        "level": "rigorous",
        "title": "Divided differences theory",
        "body": """# Divided Differences Theory

## Symmetry property
Divided differences are symmetric functions of their arguments:
$$f[x_0, \\ldots, x_n] = \\sum_{j=0}^{n} \\frac{f(x_j)}{\\prod_{k \\neq j}(x_j - x_k)}$$

## Connection to derivatives
If $x_0 = x_1 = \\cdots = x_n = x$, then:
$$f[x, x, \\ldots, x] = \\frac{f^{(n)}(x)}{n!}$$

## Generalized Leibniz formula
$$f[x_0, \\ldots, x_n] = \\frac{1}{2\\pi i} \\oint_\\Gamma \\frac{f(z)}{\\prod_{j=0}^n (z - x_j)} dz$$

This integral representation proves the continuity of divided differences with respect to their arguments.
"""
    },

    # --- Newton ---
    {
        "concept_id": "concept_newton_interpolation",
        "level": "simplified",
        "title": "Newton interpolation made simple",
        "body": """# Newton Interpolation — Simplified Version

**Advantage over Lagrange:** You can add a new point without recalculating everything!

Newton's formula uses divided differences:
$$P(x) = f[x_0] + f[x_0,x_1](x-x_0) + f[x_0,x_1,x_2](x-x_0)(x-x_1) + \\cdots$$

Each term adds a factor $(x - x_i)$ multiplied by a divided difference.

**Tip:** To add a point $x_3$, just compute $f[x_0,x_1,x_2,x_3]$ and add one term.
"""
    },
    {
        "concept_id": "concept_newton_interpolation",
        "level": "standard",
        "title": "Newton form of interpolating polynomial",
        "body": """# Newton Interpolation

## Formula
$$P_n(x) = \\sum_{k=0}^{n} f[x_0, \\ldots, x_k] \\prod_{j=0}^{k-1}(x - x_j)$$

## Horner's algorithm (efficient evaluation)
$$P_n(x) = f[x_0] + (x-x_0)(f[x_0,x_1] + (x-x_1)(f[x_0,x_1,x_2] + \\cdots))$$

Complexity: $O(n)$ for evaluation (after computing coefficients in $O(n^2)$).

## Incremental advantage
Adding a point $(x_{n+1}, y_{n+1})$ only requires:
1. Computing $f[x_0, \\ldots, x_{n+1}]$ — one column of the table
2. Adding one term to the polynomial
"""
    },
    {
        "concept_id": "concept_newton_interpolation",
        "level": "rigorous",
        "title": "Newton form analysis",
        "body": """# Newton Form Analysis

## Equivalence with Lagrange
Newton and Lagrange forms produce the **same polynomial** $P_n \\in \\mathbb{P}_n$.

**Proof:** By uniqueness of the interpolating polynomial, both constructions coincide.

## Numerical stability
Newton's form with Horner's algorithm is numerically more stable than direct Lagrange evaluation, as it avoids catastrophic cancellations in the products $\\prod(x_i - x_j)$.

## Hermite interpolation
By allowing node coalescence ($x_i \\to x_j$), Newton's form naturally extends to Hermite interpolation including derivative constraints.
"""
    },

    # --- Splines ---
    {
        "concept_id": "concept_spline_interpolation",
        "level": "simplified",
        "title": "Splines made simple",
        "body": """# Splines — Simplified Version

**Problem:** High-degree polynomials oscillate (Runge's phenomenon).

**Solution:** Instead of one large polynomial, we use **several small degree-3 polynomials** (cubics) joined together.

Each piece is a cubic polynomial that:
- Passes through the endpoints
- Joins "smoothly" (no breaks) with the neighboring piece

It's like drawing a smooth curve with a flexible ruler (a physical "spline").
"""
    },
    {
        "concept_id": "concept_spline_interpolation",
        "level": "standard",
        "title": "Cubic spline interpolation",
        "body": """# Cubic Splines

## Definition
On each interval $[x_i, x_{i+1}]$, the spline is a cubic polynomial $S_i(x)$.

## Conditions (for $n+1$ points, $n$ intervals)
1. **Interpolation**: $S_i(x_i) = y_i$ and $S_i(x_{i+1}) = y_{i+1}$
2. **$C^1$ continuity**: $S_i'(x_{i+1}) = S_{i+1}'(x_{i+1})$
3. **$C^2$ continuity**: $S_i''(x_{i+1}) = S_{i+1}''(x_{i+1})$
4. **Boundary conditions** (natural spline): $S_0''(x_0) = 0$ and $S_{n-1}''(x_n) = 0$

## Linear system
The conditions lead to a **tridiagonal** system of size $n-1$, solved in $O(n)$.
"""
    },
    {
        "concept_id": "concept_spline_interpolation",
        "level": "rigorous",
        "title": "Cubic spline theory",
        "body": """# Cubic Spline Theory

## Optimality
**Theorem:** Among all functions $g \\in C^2[a,b]$ interpolating the data, the natural cubic spline $S$ minimizes:
$$\\int_a^b [g''(x)]^2 dx$$

It is the "smoothest" curve passing through the points (minimum curvature).

## Convergence
For $f \\in C^4[a,b]$ and uniform step $h$:
$$\\|f - S\\|_\\infty = O(h^4), \\quad \\|f' - S'\\|_\\infty = O(h^3), \\quad \\|f'' - S''\\|_\\infty = O(h^2)$$

## B-splines
B-splines form a basis for the spline space with compact support, offering numerical stability and computational efficiency.
"""
    },

    # ============================================================
    # MODULE 2: NUMERICAL INTEGRATION
    # ============================================================

    # --- Riemann ---
    {
        "concept_id": "concept_riemann_sums",
        "level": "simplified",
        "title": "Riemann sums made simple",
        "body": """# Riemann Sums — Simplified Version

**Idea:** Compute the area under a curve by slicing it into **rectangles**.

1. Divide the interval $[a, b]$ into $n$ equal pieces of width $h = \\frac{b-a}{n}$
2. Compute each rectangle's height (value of $f$ at left, right, or midpoint)
3. Add up the areas: $\\text{Area} \\approx h \\times [f(x_0) + f(x_1) + \\cdots + f(x_{n-1})]$

The more rectangles ($n$ large), the more accurate!
"""
    },
    {
        "concept_id": "concept_riemann_sums",
        "level": "standard",
        "title": "Riemann sums",
        "body": """# Riemann Sums

## Three variants
For $h = (b-a)/n$ and $x_i = a + ih$:

- **Left:** $R_L = h \\sum_{i=0}^{n-1} f(x_i)$
- **Right:** $R_R = h \\sum_{i=1}^{n} f(x_i)$
- **Midpoint:** $R_M = h \\sum_{i=0}^{n-1} f\\left(\\frac{x_i + x_{i+1}}{2}\\right)$

## Error
The error is $O(h)$ for left/right sums and $O(h^2)$ for the midpoint sum.

## Convergence
$$\\lim_{n \\to \\infty} R = \\int_a^b f(x) dx$$
for any continuous function on $[a,b]$.
"""
    },
    {
        "concept_id": "concept_riemann_sums",
        "level": "rigorous",
        "title": "Riemann sums analysis",
        "body": """# Riemann Sums Analysis

## Euler-Maclaurin formula
$$\\sum_{i=0}^{n-1} f(x_i) h = \\int_a^b f(x)dx + \\frac{h}{2}[f(a) - f(b)] + \\sum_{k=1}^{p} \\frac{B_{2k}}{(2k)!} h^{2k}[f^{(2k-1)}(b) - f^{(2k-1)}(a)] + R_p$$

where $B_{2k}$ are Bernoulli numbers and $R_p = O(h^{2p+2})$.

## Precise error bound
For the left sum, if $f \\in C^1[a,b]$:
$$\\left|\\int_a^b f(x)dx - R_L\\right| \\leq \\frac{(b-a)^2}{2n} \\|f'\\|_\\infty$$
"""
    },

    # --- Definite Integrals ---
    {
        "concept_id": "concept_definite_integrals",
        "level": "simplified",
        "title": "Definite integrals made simple",
        "body": """# Definite Integrals — Simplified Version

$\\int_a^b f(x) dx$ represents the **area** under the curve $f(x)$ between $a$ and $b$.

**Basic properties:**
- If $f(x) > 0$, the area is positive
- If $f(x) < 0$, the area is negative
- $\\int_a^a f(x) dx = 0$ (no interval = no area)
- $\\int_a^b f(x) dx = -\\int_b^a f(x) dx$ (reversing bounds changes sign)
"""
    },
    {
        "concept_id": "concept_definite_integrals",
        "level": "standard",
        "title": "Definite integrals foundations",
        "body": """# Definite Integrals

## Fundamental Theorem of Calculus
If $F'(x) = f(x)$, then:
$$\\int_a^b f(x) dx = F(b) - F(a)$$

## Properties
- **Linearity**: $\\int_a^b [\\alpha f + \\beta g] = \\alpha \\int_a^b f + \\beta \\int_a^b g$
- **Additivity**: $\\int_a^b f + \\int_b^c f = \\int_a^c f$
- **Positivity**: If $f \\geq 0$ on $[a,b]$, then $\\int_a^b f \\geq 0$

## Why numerical methods?
Many functions have no known analytical antiderivative: $e^{-x^2}$, $\\frac{\\sin x}{x}$, etc.
"""
    },
    {
        "concept_id": "concept_definite_integrals",
        "level": "rigorous",
        "title": "Integration theory",
        "body": """# Integration Theory

## Riemann integral
$f$ is Riemann-integrable on $[a,b]$ if and only if its set of discontinuity points has Lebesgue measure zero.

## Mean Value Theorem for integrals
If $f$ is continuous on $[a,b]$, there exists $\\xi \\in (a,b)$ such that:
$$\\int_a^b f(x) dx = f(\\xi)(b-a)$$

## Quadrature formulas
Every numerical quadrature formula has the form:
$$\\int_a^b f(x) dx \\approx \\sum_{i=0}^n w_i f(x_i)$$
where $w_i$ are the weights and $x_i$ the nodes. The **degree of exactness** is the largest $d$ such that the formula is exact for all $P \\in \\mathbb{P}_d$.
"""
    },

    # --- Trapezoidal ---
    {
        "concept_id": "concept_trapezoidal",
        "level": "simplified",
        "title": "Trapezoidal rule made simple",
        "body": """# Trapezoidal Rule — Simplified Version

Instead of rectangles, we use **trapezoids** — more accurate because we follow the curve's slope.

**Simple formula:**
$$\\int_a^b f(x) dx \\approx \\frac{b-a}{2} [f(a) + f(b)]$$

**Composite formula** (with $n$ trapezoids):
$$\\int_a^b f(x) dx \\approx \\frac{h}{2} [f(x_0) + 2f(x_1) + 2f(x_2) + \\cdots + 2f(x_{n-1}) + f(x_n)]$$

**Tip:** Endpoints count once, interior points count twice.
"""
    },
    {
        "concept_id": "concept_trapezoidal",
        "level": "standard",
        "title": "Trapezoidal rule",
        "body": """# Trapezoidal Rule

## Derivation
We approximate $f$ by a line segment on each interval:
$$\\int_{x_i}^{x_{i+1}} f(x) dx \\approx \\frac{h}{2}[f(x_i) + f(x_{i+1})]$$

## Composite formula
$$T_n = \\frac{h}{2}\\left[f(x_0) + 2\\sum_{i=1}^{n-1} f(x_i) + f(x_n)\\right]$$

## Error
$$E_T = -\\frac{(b-a)h^2}{12} f''(\\xi), \\quad \\xi \\in (a,b)$$

The error is $O(h^2)$: doubling $n$ divides the error by 4.

## Exactness
The method is exact for polynomials of degree $\\leq 1$ (linear functions).
"""
    },
    {
        "concept_id": "concept_trapezoidal",
        "level": "rigorous",
        "title": "Trapezoidal rule analysis",
        "body": """# Trapezoidal Rule Analysis

## Euler-Maclaurin expansion
$$T_n = \\int_a^b f(x)dx + \\sum_{k=1}^{p} \\frac{B_{2k}}{(2k)!} h^{2k}[f^{(2k-1)}(b) - f^{(2k-1)}(a)] + O(h^{2p+2})$$

This expansion shows the error contains only **even** powers of $h$.

## Richardson extrapolation
By exploiting the error structure, we can combine:
$$I \\approx \\frac{4T_{2n} - T_n}{3}$$
This yields Simpson's rule! This is the principle behind Romberg extrapolation.

## Periodic functions
For periodic $C^\\infty$ functions, the trapezoidal rule converges **exponentially** fast — a remarkable result.
"""
    },

    # --- Simpson ---
    {
        "concept_id": "concept_simpson",
        "level": "simplified",
        "title": "Simpson's rule made simple",
        "body": """# Simpson's Rule — Simplified Version

Instead of straight lines (trapezoids), we use **parabolas** to follow the curve.

**Simple formula** (3 points):
$$\\int_a^b f(x) dx \\approx \\frac{b-a}{6} [f(a) + 4f(m) + f(b)]$$
where $m = \\frac{a+b}{2}$ is the midpoint.

**1-4-1 rule:** The midpoint counts **4 times** more than the endpoints.

Much more accurate than trapezoids: the error decreases **16 times** when doubling $n$.
"""
    },
    {
        "concept_id": "concept_simpson",
        "level": "standard",
        "title": "Simpson's 1/3 rule",
        "body": """# Simpson's Rule

## Composite formula
For even $n$, with $h = (b-a)/n$:
$$S_n = \\frac{h}{3}[f(x_0) + 4f(x_1) + 2f(x_2) + 4f(x_3) + \\cdots + 4f(x_{n-1}) + f(x_n)]$$

Coefficient pattern: $1, 4, 2, 4, 2, \\ldots, 4, 1$

## Error
$$E_S = -\\frac{(b-a)h^4}{180} f^{(4)}(\\xi)$$

The error is $O(h^4)$: doubling $n$ divides the error by **16**.

## Exactness
Simpson's rule is exact for polynomials of degree $\\leq 3$ (not just 2!).
"""
    },
    {
        "concept_id": "concept_simpson",
        "level": "rigorous",
        "title": "Simpson's rule analysis",
        "body": """# Simpson's Rule Analysis

## Superconvergence
Although Simpson uses a parabolic approximation (degree 2), it is exact for degree-3 polynomials. This **superconvergence** is explained by the formula's symmetry.

## Error proof
By Taylor expansion around the midpoint $m$:
$$E_S = -\\frac{h^5}{90} f^{(4)}(\\xi)$$
for the simple formula, and $-\\frac{(b-a)h^4}{180} f^{(4)}(\\xi)$ for the composite.

## Newton-Cotes formulas
Simpson is the $n=2$ case of closed Newton-Cotes formulas:
$$\\int_a^b f(x) dx \\approx \\sum_{i=0}^n w_i f(x_i)$$
with weights determined by integrating Lagrange polynomials.
"""
    },

    # --- Gauss ---
    {
        "concept_id": "concept_gaussian_quadrature",
        "level": "simplified",
        "title": "Gaussian quadrature made simple",
        "body": """# Gaussian Quadrature — Simplified Version

**Idea:** Instead of choosing evenly spaced points, we choose the **best possible points** to maximize accuracy.

With just **2 well-chosen points**, Gauss is as accurate as Simpson which uses 3!

The optimal points are roots of **Legendre polynomials**, computed on the interval $[-1, 1]$.

For any interval $[a, b]$, we apply a change of variable.
"""
    },
    {
        "concept_id": "concept_gaussian_quadrature",
        "level": "standard",
        "title": "Gauss-Legendre quadrature",
        "body": """# Gauss-Legendre Quadrature

## Formula
$$\\int_{-1}^{1} f(t) dt \\approx \\sum_{i=1}^{n} w_i f(t_i)$$

The nodes $t_i$ are roots of the Legendre polynomial $P_n(t)$ and weights $w_i = \\frac{2}{(1-t_i^2)[P_n'(t_i)]^2}$.

## Degree of exactness
With $n$ points, the formula is exact for polynomials of degree $\\leq 2n-1$.

## Change of variable
For any $[a,b]$: $x = \\frac{b-a}{2}t + \\frac{a+b}{2}$
$$\\int_a^b f(x) dx = \\frac{b-a}{2} \\sum_{i=1}^n w_i f\\left(\\frac{b-a}{2}t_i + \\frac{a+b}{2}\\right)$$
"""
    },
    {
        "concept_id": "concept_gaussian_quadrature",
        "level": "rigorous",
        "title": "Gaussian quadrature theory",
        "body": """# Gaussian Quadrature Theory

## Optimality
**Theorem:** Among all quadrature formulas with $n$ nodes, Gauss-Legendre quadrature achieves the maximum degree of exactness $2n-1$.

**Proof:** For $n$ nodes, a formula has $2n$ parameters (nodes + weights), so it can satisfy at most $2n$ exactness conditions, corresponding to polynomials of degree $\\leq 2n-1$.

## Convergence
For continuous $f$ on $[-1,1]$:
$$\\lim_{n \\to \\infty} \\sum_{i=1}^n w_i f(t_i) = \\int_{-1}^1 f(t) dt$$

## Extensions
- **Gauss-Hermite**: $\\int_{-\\infty}^{\\infty} f(x) e^{-x^2} dx$ (Gaussian weight)
- **Gauss-Laguerre**: $\\int_0^{\\infty} f(x) e^{-x} dx$ (semi-infinite interval)
"""
    },

    # ============================================================
    # MODULE 3: ODEs
    # ============================================================

    # --- IVP ---
    {
        "concept_id": "concept_initial_value",
        "level": "simplified",
        "title": "Initial value problems made simple",
        "body": """# Initial Value Problems — Simplified Version

An **ODE** (Ordinary Differential Equation) relates a function $y(t)$ to its derivative $y'(t)$.

**Example:** $y'(t) = 2t$, with $y(0) = 1$

This means: "the rate of change of $y$ is $2t$, and initially $y$ equals 1."

The solution is $y(t) = t^2 + 1$. But many ODEs have **no exact solution** — so we use numerical methods.
"""
    },
    {
        "concept_id": "concept_initial_value",
        "level": "standard",
        "title": "Initial value problems",
        "body": """# Initial Value Problems (IVP)

## Formulation
Find $y(t)$ such that:
$$y'(t) = f(t, y(t)), \\quad y(t_0) = y_0$$

## Existence and uniqueness (Picard-Lindelof Theorem)
If $f$ is continuous and Lipschitz in $y$:
$$|f(t, y_1) - f(t, y_2)| \\leq L|y_1 - y_2|$$
then the solution exists and is unique on an interval $[t_0, t_0 + \\alpha]$.

## Discretization
We seek approximations $y_n \\approx y(t_n)$ at points $t_n = t_0 + nh$, where $h$ is the time step.
"""
    },
    {
        "concept_id": "concept_initial_value",
        "level": "rigorous",
        "title": "IVP theory",
        "body": """# Initial Value Problem Theory

## Picard-Lindelof Theorem (existence and uniqueness)
Under the Lipschitz condition $|f(t,y_1) - f(t,y_2)| \\leq L|y_1-y_2|$, the Picard iterates:
$$y^{(k+1)}(t) = y_0 + \\int_{t_0}^t f(s, y^{(k)}(s)) ds$$
converge uniformly to the unique solution.

## Stability and conditioning
The problem is well-conditioned if the Lipschitz constant $L$ is moderate. For stiff problems ($L \\gg 1$), explicit methods require $h < 2/L$ for stability.

## ODE systems
Any $p$-th order ODE reduces to a system of $p$ first-order ODEs:
$$y^{(p)} = g(t, y, y', \\ldots, y^{(p-1)}) \\Rightarrow \\mathbf{Y}' = \\mathbf{F}(t, \\mathbf{Y})$$
"""
    },

    # --- Taylor ---
    {
        "concept_id": "concept_taylor_series",
        "level": "simplified",
        "title": "Taylor series made simple",
        "body": """# Taylor Series — Simplified Version

Taylor series let you **approximate a function** with a polynomial around a point.

**Idea:** If you know $f(a)$, $f'(a)$, $f''(a)$, etc., you can predict $f(a+h)$:
$$f(a+h) \\approx f(a) + h \\cdot f'(a) + \\frac{h^2}{2} \\cdot f''(a) + \\cdots$$

The more terms you keep, the more accurate the approximation.

**Link to ODEs:** Euler's method uses just the first 2 terms!
"""
    },
    {
        "concept_id": "concept_taylor_series",
        "level": "standard",
        "title": "Taylor series for ODEs",
        "body": """# Taylor Series

## Taylor's formula
$$f(x_0 + h) = \\sum_{k=0}^{n} \\frac{h^k}{k!} f^{(k)}(x_0) + \\frac{h^{n+1}}{(n+1)!} f^{(n+1)}(\\xi)$$

## Application to ODEs
For $y' = f(t, y)$, we can compute successive derivatives:
- $y' = f(t, y)$
- $y'' = f_t + f_y \\cdot f$ (total derivative)
- $y''' = \\ldots$ (increasingly complex)

## Taylor method of order $p$
$$y_{n+1} = y_n + h y_n' + \\frac{h^2}{2} y_n'' + \\cdots + \\frac{h^p}{p!} y_n^{(p)}$$

Local error: $O(h^{p+1})$. Rarely used because higher-order derivatives are hard to compute.
"""
    },
    {
        "concept_id": "concept_taylor_series",
        "level": "rigorous",
        "title": "Taylor analysis for numerical methods",
        "body": """# Taylor Analysis for Numerical Methods

## Fundamental role
Taylor expansion is the main tool for:
1. **Deriving** numerical methods (Euler, RK, etc.)
2. **Analyzing** their truncation error
3. **Proving** their convergence order

## Local Truncation Error (LTE)
For a one-step method $y_{n+1} = y_n + h\\Phi(t_n, y_n, h)$:
$$\\text{LTE} = y(t_{n+1}) - y(t_n) - h\\Phi(t_n, y(t_n), h)$$

The method is order $p$ if $\\text{LTE} = O(h^{p+1})$.

## From local to global
By Gronwall's lemma, if $\\text{LTE} = O(h^{p+1})$ and the method is stable, then the global error is $O(h^p)$.
"""
    },

    # --- Euler ---
    {
        "concept_id": "concept_euler",
        "level": "simplified",
        "title": "Euler's method made simple",
        "body": """# Euler's Method — Simplified Version

**The simplest method** to solve an ODE numerically.

**Idea:** Follow the tangent line step by step.

At each step:
$$y_{\\text{next}} = y_{\\text{current}} + h \\times \\text{slope}$$

In formula: $y_{n+1} = y_n + h \\cdot f(t_n, y_n)$

**Example:** $y' = y$, $y(0) = 1$, $h = 0.1$
- $y_1 = 1 + 0.1 \\times 1 = 1.1$
- $y_2 = 1.1 + 0.1 \\times 1.1 = 1.21$
- Exact solution: $e^{0.2} \\approx 1.2214$ — small error!
"""
    },
    {
        "concept_id": "concept_euler",
        "level": "standard",
        "title": "Explicit Euler method",
        "body": """# Euler's Method

## Formula
$$y_{n+1} = y_n + h f(t_n, y_n)$$

Derived from the order-1 Taylor expansion: $y(t+h) = y(t) + hy'(t) + O(h^2)$.

## Errors
- **Local error**: $O(h^2)$ per step
- **Global error**: $O(h)$ over the total interval — order 1 method

## Stability
For the test equation $y' = \\lambda y$ ($\\lambda < 0$), Euler is stable if:
$$|1 + h\\lambda| < 1 \\quad \\Rightarrow \\quad h < \\frac{2}{|\\lambda|}$$

## Limitations
- Low accuracy (order 1)
- Can be unstable for stiff problems
- Conceptual basis for more advanced methods
"""
    },
    {
        "concept_id": "concept_euler",
        "level": "rigorous",
        "title": "Euler convergence analysis",
        "body": """# Euler's Method Convergence Analysis

## Local truncation error
$$\\tau_n = \\frac{y(t_{n+1}) - y(t_n)}{h} - f(t_n, y(t_n)) = \\frac{h}{2}y''(\\xi_n) = O(h)$$

## Convergence theorem
If $f$ is Lipschitz in $y$ with constant $L$, then:
$$\\max_n |y(t_n) - y_n| \\leq \\frac{\\tau h}{2L}(e^{L(b-a)} - 1)$$

where $\\tau = \\max_n |\\tau_n| = O(h)$.

## Absolute stability region
For $y' = \\lambda y$, $\\lambda \\in \\mathbb{C}$, Euler is stable if $|1 + h\\lambda| \\leq 1$, i.e., the disk centered at $(-1, 0)$ with radius 1 in the $h\\lambda$ plane.
"""
    },

    # --- Heun ---
    {
        "concept_id": "concept_improved_euler",
        "level": "simplified",
        "title": "Heun's method made simple",
        "body": """# Heun's Method — Simplified Version

**Euler's problem:** We use the slope at the **beginning** of the interval, but it changes!

**Heun's solution:** Compute **two slopes** and average them.

1. **Prediction** (slope at start): $\\tilde{y} = y_n + h \\cdot f(t_n, y_n)$
2. **Correction** (average slopes): $y_{n+1} = y_n + \\frac{h}{2}[f(t_n, y_n) + f(t_{n+1}, \\tilde{y})]$

It's like looking both ways before crossing — much more accurate than Euler!
"""
    },
    {
        "concept_id": "concept_improved_euler",
        "level": "standard",
        "title": "Heun's method (improved Euler)",
        "body": """# Heun's Method

## Algorithm (predictor-corrector)
1. $k_1 = f(t_n, y_n)$
2. $k_2 = f(t_n + h, y_n + h k_1)$
3. $y_{n+1} = y_n + \\frac{h}{2}(k_1 + k_2)$

## Interpretation
- $k_1$ = slope at the beginning
- $k_2$ = slope at the end (predicted by Euler)
- Average of both = better approximation

## Properties
- **Order 2**: global error $O(h^2)$
- **2 evaluations** of $f$ per step
- Also called the "trapezoidal method" for ODEs
"""
    },
    {
        "concept_id": "concept_improved_euler",
        "level": "rigorous",
        "title": "Heun's method analysis",
        "body": """# Heun's Method Analysis

## Butcher tableau
$$\\begin{array}{c|cc} 0 & & \\\\ 1 & 1 & \\\\ \\hline & 1/2 & 1/2 \\end{array}$$

## Order conditions
Heun satisfies the order-2 conditions for Runge-Kutta methods:
$$\\sum b_i = 1, \\quad \\sum b_i c_i = 1/2$$

## Local truncation error
$$\\tau_{n+1} = \\frac{h^2}{6}[f_{tt} + 2f_{ty}f + f_{yy}f^2 + f_y f_t + f_y^2 f] + O(h^3)$$

## Stability region
For $y' = \\lambda y$: $|1 + h\\lambda + \\frac{(h\\lambda)^2}{2}| \\leq 1$, larger than Euler's.
"""
    },

    # --- RK4 ---
    {
        "concept_id": "concept_rk4",
        "level": "simplified",
        "title": "RK4 made simple",
        "body": """# Runge-Kutta RK4 — Simplified Version

The **most popular method** for solving ODEs. It computes **4 slopes**:

1. $k_1$ = slope at the beginning
2. $k_2$ = slope at the midpoint (using $k_1$)
3. $k_3$ = slope at the midpoint (using $k_2$)
4. $k_4$ = slope at the end (using $k_3$)

Then the weighted average: $y_{n+1} = y_n + \\frac{h}{6}(k_1 + 2k_2 + 2k_3 + k_4)$

Midpoint slopes count **double** because they are more representative.

Very accurate: error decreases **16 times** when halving $h$.
"""
    },
    {
        "concept_id": "concept_rk4",
        "level": "standard",
        "title": "Classical Runge-Kutta method (RK4)",
        "body": """# Runge-Kutta RK4 Method

## Algorithm
$$k_1 = f(t_n, y_n)$$
$$k_2 = f(t_n + h/2, y_n + h k_1/2)$$
$$k_3 = f(t_n + h/2, y_n + h k_2/2)$$
$$k_4 = f(t_n + h, y_n + h k_3)$$
$$y_{n+1} = y_n + \\frac{h}{6}(k_1 + 2k_2 + 2k_3 + k_4)$$

## Properties
- **Order 4**: global error $O(h^4)$
- **4 evaluations** of $f$ per step
- No need to compute derivatives of $f$
- Excellent accuracy/cost ratio

## Comparison
| Method | Order | Eval/step | Error if $h/2$ |
|--------|-------|-----------|-----------------|
| Euler  | 1     | 1         | / 2             |
| Heun   | 2     | 2         | / 4             |
| RK4    | 4     | 4         | / 16            |
"""
    },
    {
        "concept_id": "concept_rk4",
        "level": "rigorous",
        "title": "RK4 analysis",
        "body": """# RK4 Analysis

## Butcher tableau
$$\\begin{array}{c|cccc} 0 & & & & \\\\ 1/2 & 1/2 & & & \\\\ 1/2 & 0 & 1/2 & & \\\\ 1 & 0 & 0 & 1 & \\\\ \\hline & 1/6 & 1/3 & 1/3 & 1/6 \\end{array}$$

## Order conditions
RK4 satisfies all 8 order conditions for Butcher trees up to order 4. This is the maximum order achievable with 4 stages.

## Butcher barrier
For $s$ stages, the maximum achievable order is:
- $s \\leq 4$: order $= s$
- $s = 5$: order $= 4$ (not 5!)
- $s = 6$: order $= 5$

## Truncation error
$$y(t_{n+1}) - y_{n+1} = \\frac{h^5}{120}[y^{(5)}(t_n)] + O(h^6)$$

## Adaptive methods (Fehlberg, Dormand-Prince)
By combining two RK methods of different orders ($p$ and $p+1$), we estimate the local error and adjust $h$ automatically.
"""
    },
]


def seed_content():
    dotenv_path = os.path.join(os.path.dirname(__file__), "../../.env")
    load_dotenv(dotenv_path)

    NEO4J_URI = os.getenv("NEO4J_URI")
    NEO4J_USER = os.getenv("NEO4J_USER")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

    if not all([NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD]):
        logger.error("Missing Neo4j variables in .env")
        sys.exit(1)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    try:
        with driver.session() as session:
            session.run("MATCH (ct:Content) DETACH DELETE ct")
            logger.info("Old content deleted")

            session.run("CREATE CONSTRAINT content_id IF NOT EXISTS FOR (ct:Content) REQUIRE ct.id IS UNIQUE")

            for i, content in enumerate(CONTENTS):
                content_id = f"content_{content['concept_id'].replace('concept_', '')}_{content['level']}"

                # English content stored in title_en / body_en (and also in
                # title / body as a fallback for older readers).
                # The French companion script (seed_content_approximation.py)
                # writes to title_fr / body_fr for the same nodes.
                session.run(
                    """
                    MATCH (c:Concept {id: $concept_id})
                    MERGE (ct:Content {id: $content_id})
                    ON CREATE SET
                        ct.level = $level,
                        ct.title = $title,
                        ct.body = $body,
                        ct.title_en = $title,
                        ct.body_en = $body
                    ON MATCH SET
                        ct.level = $level,
                        ct.title_en = $title,
                        ct.body_en = $body,
                        ct.title = coalesce(ct.title, $title),
                        ct.body = coalesce(ct.body, $body)
                    MERGE (c)-[:HAS_CONTENT]->(ct)
                    """,
                    concept_id=content["concept_id"],
                    content_id=content_id,
                    level=content["level"],
                    title=content["title"],
                    body=content["body"]
                )
                logger.info(f"  {i+1}/{len(CONTENTS)}: {content['title']} ({content['level']}) [EN]")

            result = session.run("MATCH (ct:Content) RETURN count(ct) AS count")
            total = result.single()["count"]
            result2 = session.run("MATCH ()-[r:HAS_CONTENT]->() RETURN count(r) AS count")
            rels = result2.single()["count"]

            logger.info(f"\n{'='*60}")
            logger.info("MULTI-LEVEL CONTENT CREATED SUCCESSFULLY")
            logger.info(f"{'='*60}")
            logger.info(f"  Contents created   : {total}")
            logger.info(f"  HAS_CONTENT rels   : {rels}")
            logger.info("  Levels             : simplified, standard, rigorous")
            logger.info("  Concepts covered   : 15")
            logger.info(f"{'='*60}\n")

    finally:
        driver.close()


if __name__ == "__main__":
    seed_content()
