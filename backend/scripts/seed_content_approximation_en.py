"""
English companion to seed_content_approximation.py: writes the same Module 3
(Polynomial Approximation & Optimization) content in ENGLISH on the SAME
Content nodes (matched by id = "content_<concept_short>_<level>").

Each Content node ends up with:
  - title    / body    : default fields (kept as legacy fallback)
  - title_en / body_en : English version (this script)
  - title_fr / body_fr : French version (seed_content_approximation.py)

The router /graph/concepts/{id}/content?lang=... picks the right pair via
COALESCE(title_<lang>, title).

Concepts covered (3 levels each = 15 Content nodes):
  - concept_least_squares
  - concept_orthogonal_polynomials
  - concept_minimax_approximation
  - concept_gradient_descent
  - concept_newton_optimization

Usage: python scripts/seed_content_approximation_en.py
"""
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.graph.neo4j_connection import neo4j_conn

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


CONTENTS = [
    # --- concept_least_squares -----------------------------------------
    {
        "concept_id": "concept_least_squares",
        "level": "simplified",
        "title": "Least squares (intuition)",
        "body": (
            "## Core idea\n\n"
            "We have a cloud of points and we want **the line (or polynomial curve) that passes as closely as possible** to all of them.\n\n"
            "**Example**: you have the grades of a class and the hours each student studied. You want to draw the line that summarises the trend.\n\n"
            "## How?\n\n"
            "For each point $(x_i, y_i)$ we compute the vertical distance between the point and the line: this is the **error**.\n\n"
            "We pick the line that **minimises the sum of squared errors**.\n\n"
            "$$ \\min \\sum_{i=1}^{n} (y_i - p(x_i))^2 $$\n\n"
            "## Why squares?\n\n"
            "- To penalise large errors more than small ones.\n"
            "- To get a clean mathematical formula (absolute values are less convenient)."
        ),
    },
    {
        "concept_id": "concept_least_squares",
        "level": "standard",
        "title": "Least squares method",
        "body": (
            "## Problem\n\n"
            "Given $n$ points $(x_i, y_i)$ and a polynomial $p(x) = a_0 + a_1 x + \\dots + a_d x^d$ of degree $d$,\n"
            "find the coefficients $(a_0, \\dots, a_d)$ that minimise:\n\n"
            "$$ S(a) = \\sum_{i=1}^{n} (y_i - p(x_i))^2 $$\n\n"
            "## Normal equations\n\n"
            "Build the Vandermonde matrix $A \\in \\mathbb{R}^{n \\times (d+1)}$ with $A_{ij} = x_i^j$.\n\n"
            "The minimum of $\\|A a - y\\|^2$ satisfies:\n\n"
            "$$ A^T A \\, a = A^T y $$\n\n"
            "## Linear case ($d = 1$)\n\n"
            "The classical formulas:\n\n"
            "$$ a_1 = \\frac{n \\sum x_i y_i - \\sum x_i \\sum y_i}{n \\sum x_i^2 - (\\sum x_i)^2}, \\quad a_0 = \\bar{y} - a_1 \\bar{x} $$"
        ),
    },
    {
        "concept_id": "concept_least_squares",
        "level": "rigorous",
        "title": "Least squares: theory",
        "body": (
            "## Theorem (existence and uniqueness)\n\n"
            "Let $A \\in \\mathbb{R}^{n \\times m}$ with $n \\ge m$ and $\\mathrm{rank}(A) = m$. Then the problem\n\n"
            "$$ \\min_{a \\in \\mathbb{R}^m} \\|A a - y\\|_2^2 $$\n\n"
            "has a **unique** solution given by the normal equations:\n\n"
            "$$ a^* = (A^T A)^{-1} A^T y $$\n\n"
            "## QR decomposition (numerically stable method)\n\n"
            "Factor $A = Q R$ with $Q$ orthogonal and $R$ upper triangular. The solution is\n\n"
            "$$ R a = Q^T y $$\n\n"
            "solved by back-substitution in $O(m^2)$.\n\n"
            "## Conditioning\n\n"
            "The condition number of $A^T A$ is $\\kappa(A^T A) = \\kappa(A)^2$. For ill-conditioned data,\n"
            "prefer **QR** or **SVD** over the normal equations to avoid amplifying errors."
        ),
    },

    # --- concept_orthogonal_polynomials ---------------------------------
    {
        "concept_id": "concept_orthogonal_polynomials",
        "level": "simplified",
        "title": "Orthogonal polynomials (intuition)",
        "body": (
            "## The idea\n\n"
            "Two polynomials $P$ and $Q$ are **orthogonal** on $[a,b]$ if their integrated \"product\" is zero:\n\n"
            "$$ \\int_a^b P(x) Q(x) w(x) dx = 0 $$\n\n"
            "where $w(x)$ is a weight function.\n\n"
            "## Why is this useful?\n\n"
            "Like an orthogonal basis in linear algebra (the vectors $\\vec{i}, \\vec{j}, \\vec{k}$), orthogonal polynomials\n"
            "let us **decompose a function into a sum of independent pieces**:\n\n"
            "$$ f(x) \\approx c_0 P_0(x) + c_1 P_1(x) + \\dots + c_n P_n(x) $$\n\n"
            "## Famous families\n\n"
            "- **Legendre**: on $[-1, 1]$ with $w(x) = 1$\n"
            "- **Chebyshev**: on $[-1, 1]$ with $w(x) = 1/\\sqrt{1-x^2}$\n"
            "- **Hermite**: on $\\mathbb{R}$ with $w(x) = e^{-x^2}$"
        ),
    },
    {
        "concept_id": "concept_orthogonal_polynomials",
        "level": "standard",
        "title": "Classical families of orthogonal polynomials",
        "body": (
            "## Formal definition\n\n"
            "A family $\\{P_n\\}_{n \\ge 0}$ with $\\deg P_n = n$ is **orthogonal** with respect to a weight $w$ on $[a,b]$ if:\n\n"
            "$$ \\langle P_i, P_j \\rangle = \\int_a^b P_i(x) P_j(x) w(x) dx = h_i \\delta_{ij} $$\n\n"
            "## Legendre polynomials $P_n$\n\n"
            "On $[-1, 1]$ with $w \\equiv 1$. Three-term recurrence:\n\n"
            "$$ (n+1) P_{n+1}(x) = (2n+1) x P_n(x) - n P_{n-1}(x) $$\n\n"
            "First few: $P_0 = 1$, $P_1 = x$, $P_2 = \\frac{1}{2}(3x^2 - 1)$.\n\n"
            "## Chebyshev polynomials $T_n$\n\n"
            "On $[-1, 1]$ with $w(x) = 1/\\sqrt{1-x^2}$. Simple definition:\n\n"
            "$$ T_n(\\cos \\theta) = \\cos(n \\theta) $$\n\n"
            "Key property: minimise the maximum error $\\|f - p\\|_\\infty$ (Chebyshev's theorem).\n\n"
            "## Decomposing a function\n\n"
            "$$ f(x) = \\sum_{n=0}^{\\infty} c_n P_n(x), \\quad c_n = \\frac{\\langle f, P_n \\rangle}{\\langle P_n, P_n \\rangle} $$"
        ),
    },
    {
        "concept_id": "concept_orthogonal_polynomials",
        "level": "rigorous",
        "title": "Orthogonal polynomials: complete theory",
        "body": (
            "## Existence (Gram-Schmidt)\n\n"
            "For any positive integrable weight $w > 0$ on $[a, b]$, Gram-Schmidt orthogonalisation applied to $\\{1, x, x^2, \\dots\\}$ produces a unique orthogonal family (up to a multiplicative constant).\n\n"
            "## Theorem (zeros)\n\n"
            "If $\\{P_n\\}$ is an orthogonal polynomial family on $[a, b]$ for the weight $w$, then $P_n$ has exactly $n$ **simple zeros** in $[a, b]$.\n\n"
            "*Application*: these zeros are the optimal nodes for Gaussian quadrature.\n\n"
            "## Three-term recurrence (Favard's theorem)\n\n"
            "Every orthogonal family $\\{P_n\\}$ with $\\deg P_n = n$ satisfies:\n\n"
            "$$ P_{n+1}(x) = (\\alpha_n x + \\beta_n) P_n(x) + \\gamma_n P_{n-1}(x) $$\n\n"
            "where $(\\alpha_n, \\beta_n, \\gamma_n)$ are computed from the moments $\\int x^k w(x) dx$.\n\n"
            "## Gauss-Legendre quadrature\n\n"
            "If $x_1, \\dots, x_n$ are the zeros of $P_n$ (Legendre), then the quadrature formula\n\n"
            "$$ \\int_{-1}^{1} f(x) dx \\approx \\sum_{i=1}^n w_i f(x_i) $$\n\n"
            "is exact for all polynomials of degree $\\le 2n - 1$."
        ),
    },

    # --- concept_minimax_approximation ----------------------------------
    {
        "concept_id": "concept_minimax_approximation",
        "level": "simplified",
        "title": "Minimax approximation (intuition)",
        "body": (
            "## The problem\n\n"
            "We have a complicated function $f$ and we want to replace it with a simple polynomial $p$.\n\n"
            "But how do we measure the quality of the approximation?\n\n"
            "## Two options\n\n"
            "**Option 1 - Least squares**: minimise the sum of squared errors.\n"
            "-> works well on average, but can have **localised error spikes**.\n\n"
            "**Option 2 - Minimax (Chebyshev)**: minimise **the worst error** (the largest one over the whole interval).\n\n"
            "$$ \\min_{p} \\max_{x \\in [a,b]} |f(x) - p(x)| $$\n\n"
            "## Why minimax?\n\n"
            "When you must **guarantee a maximum error** (aerospace, finance, safety-critical engineering), you care about the **worst case**.\n\n"
            "The minimax polynomial is the best approximation in the $L^\\infty$ norm."
        ),
    },
    {
        "concept_id": "concept_minimax_approximation",
        "level": "standard",
        "title": "Minimax approximation (Chebyshev)",
        "body": (
            "## Chebyshev's problem\n\n"
            "Find the polynomial $p^* \\in \\mathcal{P}_n$ that minimises:\n\n"
            "$$ \\|f - p^*\\|_\\infty = \\sup_{x \\in [a,b]} |f(x) - p^*(x)| $$\n\n"
            "## Equi-oscillation theorem\n\n"
            "$p^*$ is the unique minimax polynomial of degree $\\le n$ iff the error $e(x) = f(x) - p^*(x)$ reaches its extreme value $\\pm \\|e\\|_\\infty$ at **at least $n+2$ points** $x_0 < x_1 < \\dots < x_{n+1}$ with **alternating signs**:\n\n"
            "$$ e(x_i) = (-1)^i \\|e\\|_\\infty, \\quad i = 0, 1, \\dots, n+1 $$\n\n"
            "## Remez algorithm\n\n"
            "To compute $p^*$ numerically, use the iterative **Remez** algorithm:\n\n"
            "1. Pick $n+2$ initial points.\n"
            "2. Solve a linear system to make the error oscillate at those points.\n"
            "3. Find the new error maximum, update the points.\n"
            "4. Iterate to convergence.\n\n"
            "## Chebyshev approximation (simple)\n\n"
            "An approximation **close to minimax** is obtained by truncating the Chebyshev series of $f$. Often good enough in practice."
        ),
    },
    {
        "concept_id": "concept_minimax_approximation",
        "level": "rigorous",
        "title": "Minimax approximation theory",
        "body": (
            "## Existence theorem\n\n"
            "For every continuous function $f$ on $[a, b]$ and every integer $n \\ge 0$, there is a unique polynomial $p^* \\in \\mathcal{P}_n$ such that\n\n"
            "$$ \\|f - p^*\\|_\\infty = \\inf_{p \\in \\mathcal{P}_n} \\|f - p\\|_\\infty $$\n\n"
            "## Characterisation (Chebyshev, 1854)\n\n"
            "$p^* \\in \\mathcal{P}_n$ is minimax iff there exist $n+2$ points $\\{x_i\\}_{i=0}^{n+1}$ in $[a,b]$ such that\n\n"
            "$$ f(x_i) - p^*(x_i) = \\sigma (-1)^i E^*, \\quad \\sigma \\in \\{-1, +1\\} $$\n\n"
            "where $E^* = \\|f - p^*\\|_\\infty$.\n\n"
            "## Error bound (Jackson)\n\n"
            "For $f \\in C^k([a,b])$ with piecewise continuous $f^{(k)}$,\n\n"
            "$$ E_n(f) := \\inf_p \\|f - p\\|_\\infty \\le \\frac{C_k \\|f^{(k)}\\|_\\infty (b-a)^k}{n^k} $$\n\n"
            "## Link with Chebyshev nodes\n\n"
            "To interpolate $f$ by a polynomial of degree $n$, choosing the zeros of $T_{n+1}$ (Chebyshev) as nodes yields an interpolation error **close to the minimax**, unlike equispaced nodes (Runge phenomenon).\n\n"
            "## Remez algorithm (convergence)\n\n"
            "The Remez algorithm converges **quadratically** under technical conditions (non-degenerate critical point). In practice, $\\sim 5\\text{-}10$ iterations are enough for machine precision."
        ),
    },

    # --- concept_gradient_descent ---------------------------------------
    {
        "concept_id": "concept_gradient_descent",
        "level": "simplified",
        "title": "Gradient descent (intuition)",
        "body": (
            "## The analogy\n\n"
            "Picture yourself in the mountains in fog, wanting to reach the valley.\n\n"
            "You can't see far, but you can feel the **slope under your feet**.\n\n"
            "**Strategy**: at each step, head in the direction that goes down the most.\n\n"
            "## In math\n\n"
            "The **gradient** $\\nabla f$ points in the direction of steepest ascent.\n\n"
            "To go down, walk in the **opposite** direction:\n\n"
            "$$ \\theta_{k+1} = \\theta_k - \\eta \\, \\nabla f(\\theta_k) $$\n\n"
            "where $\\eta$ (eta) is your **step size**.\n\n"
            "## The trap\n\n"
            "- If $\\eta$ is too small -> you descend very slowly.\n"
            "- If $\\eta$ is too large -> you overshoot the valley.\n\n"
            "Picking the right $\\eta$ is the classical optimisation tradeoff."
        ),
    },
    {
        "concept_id": "concept_gradient_descent",
        "level": "standard",
        "title": "Gradient descent",
        "body": (
            "## Formulation\n\n"
            "To minimise a differentiable $f : \\mathbb{R}^n \\to \\mathbb{R}$, iterate:\n\n"
            "$$ \\theta_{k+1} = \\theta_k - \\eta_k \\, \\nabla f(\\theta_k) $$\n\n"
            "with $\\nabla f(\\theta) = \\left( \\frac{\\partial f}{\\partial \\theta_1}, \\dots, \\frac{\\partial f}{\\partial \\theta_n} \\right)$.\n\n"
            "## Choosing the learning rate $\\eta$\n\n"
            "- **constant $\\eta$**: simple but not robust.\n"
            "- **decaying $\\eta$**: $\\eta_k = \\eta_0 / (1 + k)$, classic in SGD.\n"
            "- **line search** (Armijo): pick $\\eta$ satisfying $f(\\theta - \\eta \\nabla f) \\le f(\\theta) - c \\eta \\|\\nabla f\\|^2$.\n\n"
            "## Convergence\n\n"
            "For **convex** $f$ with $L$-Lipschitz $\\nabla f$, choosing $\\eta = 1/L$:\n\n"
            "$$ f(\\theta_k) - f(\\theta^*) \\le \\frac{\\|\\theta_0 - \\theta^*\\|^2}{2 \\eta k} = O(1/k) $$\n\n"
            "## Variants\n\n"
            "- **SGD**: compute $\\nabla f$ on a sample (mini-batch).\n"
            "- **Momentum**: $v_{k+1} = \\beta v_k + \\nabla f$, $\\theta_{k+1} = \\theta_k - \\eta v_{k+1}$.\n"
            "- **Adam**: adapts $\\eta$ per parameter using the gradient moments."
        ),
    },
    {
        "concept_id": "concept_gradient_descent",
        "level": "rigorous",
        "title": "Gradient descent: analysis",
        "body": (
            "## Standard assumptions\n\n"
            "- $f : \\mathbb{R}^n \\to \\mathbb{R}$ is $L$-smooth: $\\|\\nabla f(x) - \\nabla f(y)\\| \\le L \\|x - y\\|$.\n"
            "- $f$ convex (sometimes $\\mu$-strongly convex).\n\n"
            "## Theorem (smooth convex case)\n\n"
            "For $\\eta \\le 1/L$, gradient descent produces a sequence satisfying:\n\n"
            "$$ f(\\theta_k) - f(\\theta^*) \\le \\frac{\\|\\theta_0 - \\theta^*\\|^2}{2 \\eta k} $$\n\n"
            "Hence $O(1/k)$ - sublinear.\n\n"
            "## Theorem ($\\mu$-strongly convex case)\n\n"
            "$$ \\|\\theta_k - \\theta^*\\|^2 \\le \\left(1 - \\eta \\mu\\right)^k \\|\\theta_0 - \\theta^*\\|^2 $$\n\n"
            "Hence **linear** (geometric) convergence with rate $1 - \\eta \\mu$.\n\n"
            "## Lower bound (Nesterov)\n\n"
            "For first-order methods on $L$-smooth and $\\mu$-strongly-convex functions,\n\n"
            "$$ f(\\theta_k) - f(\\theta^*) \\ge \\Omega\\left(\\left(\\frac{\\sqrt{\\kappa} - 1}{\\sqrt{\\kappa} + 1}\\right)^{2k}\\right), \\quad \\kappa = L/\\mu $$\n\n"
            "achieved by Nesterov's accelerated gradient method.\n\n"
            "## Non-convex case\n\n"
            "We only guarantee convergence to a **critical point** ($\\nabla f = 0$), not to the global minimum. With $\\eta < 2/L$:\n\n"
            "$$ \\min_{k \\le K} \\|\\nabla f(\\theta_k)\\|^2 \\le \\frac{2 L (f(\\theta_0) - f^*)}{K} $$"
        ),
    },

    # --- concept_newton_optimization ------------------------------------
    {
        "concept_id": "concept_newton_optimization",
        "level": "simplified",
        "title": "Newton's method for optimisation (intuition)",
        "body": (
            "## The idea\n\n"
            "Gradient descent looks at **the slope** $\\nabla f$. Newton goes further: it also looks at the **curvature** (the second derivative, or Hessian $H$).\n\n"
            "## Comparison\n\n"
            "**Gradient descent**: \"I take a fixed step along the steepest slope\".\n\n"
            "**Newton**: \"I model the function as a local parabola and jump straight to the minimum of that parabola\".\n\n"
            "## Formula\n\n"
            "$$ \\theta_{k+1} = \\theta_k - H(\\theta_k)^{-1} \\nabla f(\\theta_k) $$\n\n"
            "where $H$ is the Hessian matrix (second derivatives).\n\n"
            "## Pros / cons\n\n"
            "- Pros: **much faster** near the minimum (quadratic convergence).\n"
            "- Cons: **more expensive** per iteration (computing and inverting $H$, $O(n^3)$ in dimension $n$)."
        ),
    },
    {
        "concept_id": "concept_newton_optimization",
        "level": "standard",
        "title": "Newton's method for optimisation",
        "body": (
            "## Principle\n\n"
            "To minimise a twice-differentiable $f : \\mathbb{R}^n \\to \\mathbb{R}$, approximate $f$ near $\\theta_k$ by its second-order Taylor expansion:\n\n"
            "$$ f(\\theta) \\approx f(\\theta_k) + \\nabla f(\\theta_k)^T (\\theta - \\theta_k) + \\frac{1}{2} (\\theta - \\theta_k)^T H_k (\\theta - \\theta_k) $$\n\n"
            "The minimum of this quadratic approximation is:\n\n"
            "$$ \\theta_{k+1} = \\theta_k - H_k^{-1} \\nabla f(\\theta_k) $$\n\n"
            "## Convergence\n\n"
            "**Quadratic** near a non-degenerate local minimum (positive-definite Hessian):\n\n"
            "$$ \\|\\theta_{k+1} - \\theta^*\\| \\le C \\|\\theta_k - \\theta^*\\|^2 $$\n\n"
            "This doubles the number of correct digits at every iteration. Very fast near the optimum.\n\n"
            "## Cost per iteration\n\n"
            "- Computing $\\nabla f$: $O(n)$\n"
            "- Computing $H$: $O(n^2)$\n"
            "- Solving $H d = -\\nabla f$: $O(n^3)$ (LU/Cholesky factorisation)\n\n"
            "Total: $O(n^3)$ per iteration, vs $O(n)$ for gradient descent.\n\n"
            "## Practical variants\n\n"
            "- **Modified Newton**: regularise $H$ if not positive definite: $H \\to H + \\lambda I$.\n"
            "- **Quasi-Newton (BFGS, L-BFGS)**: approximate $H^{-1}$ without computing it, $O(n^2)$ per iteration.\n"
            "- **Gauss-Newton**: for least squares, approximates $H \\approx J^T J$ where $J$ is the Jacobian."
        ),
    },
    {
        "concept_id": "concept_newton_optimization",
        "level": "rigorous",
        "title": "Newton's method: analysis",
        "body": (
            "## Local convergence (Kantorovich's theorem)\n\n"
            "Let $f \\in C^2$ and $\\theta^*$ such that $\\nabla f(\\theta^*) = 0$ and $H(\\theta^*) \\succ 0$ (positive definite). If $H$ is $L$-Lipschitz near $\\theta^*$ and $\\theta_0$ is close enough to $\\theta^*$, then the sequence $\\{\\theta_k\\}$ converges to $\\theta^*$ with:\n\n"
            "$$ \\|\\theta_{k+1} - \\theta^*\\| \\le \\frac{L}{2 \\sigma_{\\min}(H(\\theta^*))} \\|\\theta_k - \\theta^*\\|^2 $$\n\n"
            "where $\\sigma_{\\min}$ is the smallest eigenvalue of $H$.\n\n"
            "## Globalisation via line search\n\n"
            "Quadratic convergence is **local**. For global convergence, combine Newton with a **line search** (Armijo, Wolfe):\n\n"
            "$$ \\theta_{k+1} = \\theta_k - \\alpha_k H_k^{-1} \\nabla f(\\theta_k), \\quad \\alpha_k \\in (0, 1] $$\n\n"
            "## Regularisation (Levenberg-Marquardt)\n\n"
            "If $H_k \\not\\succ 0$, regularise:\n\n"
            "$$ \\theta_{k+1} = \\theta_k - (H_k + \\lambda_k I)^{-1} \\nabla f(\\theta_k) $$\n\n"
            "For $\\lambda \\to 0$ we recover Newton; for $\\lambda \\to \\infty$ we recover gradient descent.\n\n"
            "## Quasi-Newton (BFGS)\n\n"
            "We maintain an approximation $B_k \\approx H_k^{-1}$ updated by:\n\n"
            "$$ B_{k+1} = (I - \\rho s y^T) B_k (I - \\rho y s^T) + \\rho s s^T $$\n\n"
            "where $s = \\theta_{k+1} - \\theta_k$, $y = \\nabla f_{k+1} - \\nabla f_k$, $\\rho = 1/(y^T s)$.\n\n"
            "Super-linear convergence. **L-BFGS** stores only the last $m$ pairs $(s, y)$: memory $O(mn)$ instead of $O(n^2)$, ideal for large dimensions (deep learning)."
        ),
    },
]


def main() -> None:
    inserted = 0
    for c in CONTENTS:
        # Make sure the concept exists.
        rows = neo4j_conn.run_query(
            "MATCH (c:Concept {id: $cid}) RETURN c.id AS id",
            {"cid": c["concept_id"]},
        )
        if not rows:
            logger.warning("Concept %s not found, skip", c["concept_id"])
            continue

        # English content stored on the SAME Content node as the French version,
        # in title_en / body_en. Node id = "content_<concept_short>_<level>"
        # to stay aligned with seed_content.py and seed_content_approximation.py.
        content_id = f"content_{c['concept_id'].replace('concept_', '')}_{c['level']}"

        neo4j_conn.run_write_query(
            """
            MATCH (c:Concept {id: $cid})
            MERGE (ct:Content {id: $content_id})
            ON CREATE SET
                ct.level = $level,
                ct.title_en = $title,
                ct.body_en = $body,
                ct.title = $title,
                ct.body = $body
            ON MATCH SET
                ct.level = $level,
                ct.title_en = $title,
                ct.body_en = $body
            MERGE (c)-[:HAS_CONTENT]->(ct)
            """,
            {
                "cid": c["concept_id"],
                "content_id": content_id,
                "level": c["level"],
                "title": c["title"],
                "body": c["body"],
            },
        )
        inserted += 1
        logger.info("Inserted EN content for %s (%s)", c["concept_id"], c["level"])

    logger.info("Total EN contents inserted/updated : %d", inserted)


if __name__ == "__main__":
    main()
