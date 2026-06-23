"""Hand-curated bank of 30 items for the Phase 4 pre/post-test.

See `docs/phase4/03_PRE_POST_TEST.md` for the complete pedagogical grid,
the mathematical justifications and the A/B equivalence strategy.

Structure : 15 "A" items (pre-test) + 15 "B" items (post-test), isomorphic
pairwise. 5 target concepts × 3 difficulties × 2 versions = 30 items.

Format unified with `quiz_question_bank.py` to allow reuse of the
feedback_service.eval_exact helpers if needed.

Each item :
  id           stable identifier (used for the CSV exports)
  version      "A" (pre) or "B" (post)
  concept_id   Neo4j id (concept_lagrange, concept_simpson, ...)
  difficulty   "easy" / "medium" / "hard"
  question_fr  statement in French
  question_en  statement in English
  options      list[str] (None for open "computation" questions)
  correct      0-based index in options, or str for open question
  points       1 (MCQ) or 2 (free computation, hard only)
"""
from __future__ import annotations

# === Concept 1 : Lagrange Interpolation ===
LAGRANGE_ITEMS = [
    {
        "id": "A1", "version": "A", "concept_id": "concept_lagrange",
        "difficulty": "easy", "points": 1,
        "question_fr": "Soient les points (0, 1) et (2, 5). Quelle est la "
                       "valeur de l'interpolant lineaire de Lagrange P(x) en x = 1 ?",
        "question_en": "Given the points (0, 1) and (2, 5), what is the value "
                       "of the Lagrange linear interpolant P(x) at x = 1?",
        "options": ["1", "2", "3", "5"],
        "correct": 2,
    },
    {
        "id": "B1", "version": "B", "concept_id": "concept_lagrange",
        "difficulty": "easy", "points": 1,
        "question_fr": "Soient les points (1, 3) et (4, 9). Quelle est la "
                       "valeur de l'interpolant lineaire de Lagrange P(x) en x = 2 ?",
        "question_en": "Given the points (1, 3) and (4, 9), what is the value "
                       "of the Lagrange linear interpolant P(x) at x = 2?",
        "options": ["4", "5", "6", "7"],
        "correct": 1,
    },
    {
        "id": "A2", "version": "A", "concept_id": "concept_lagrange",
        "difficulty": "medium", "points": 1,
        "question_fr": "Combien de polynomes d'interpolation de degre au plus 3 "
                       "passent par 4 points distincts en abscisse ?",
        "question_en": "How many interpolation polynomials of degree at most 3 "
                       "pass through 4 distinct x-coordinates?",
        "options": ["0", "1", "4", "Une infinite"],
        "correct": 1,
    },
    {
        "id": "B2", "version": "B", "concept_id": "concept_lagrange",
        "difficulty": "medium", "points": 1,
        "question_fr": "Combien de polynomes d'interpolation de degre au plus n "
                       "passent par n+1 points distincts en abscisse ?",
        "question_en": "How many interpolation polynomials of degree at most n "
                       "pass through n+1 distinct x-coordinates?",
        "options": ["0", "1", "n", "Une infinite"],
        "correct": 1,
    },
    {
        "id": "A3", "version": "A", "concept_id": "concept_lagrange",
        "difficulty": "hard", "points": 2,
        "question_fr": "Donnez l'expression du polynome de Lagrange de degre 2 "
                       "passant par (-1, 0), (0, 1), (1, 0). Forme developpee.",
        "question_en": "Give the Lagrange polynomial of degree 2 going through "
                       "(-1, 0), (0, 1), (1, 0). Expanded form.",
        "options": None,
        "correct": "1 - x**2",  # SymPy normalisera (-x**2 + 1)
    },
    {
        "id": "B3", "version": "B", "concept_id": "concept_lagrange",
        "difficulty": "hard", "points": 2,
        "question_fr": "Donnez l'expression du polynome de Lagrange de degre 2 "
                       "passant par (-2, 0), (0, 4), (2, 0). Forme developpee.",
        "question_en": "Give the Lagrange polynomial of degree 2 going through "
                       "(-2, 0), (0, 4), (2, 0). Expanded form.",
        "options": None,
        "correct": "4 - x**2",
    },
]

# === Concept 2 : Simpson 1/3 Method ===
SIMPSON_ITEMS = [
    {
        "id": "A4", "version": "A", "concept_id": "concept_simpson",
        "difficulty": "easy", "points": 1,
        "question_fr": "La formule de Simpson 1/3 sur [a, b] approxime "
                       "l'integrale de f par :",
        "question_en": "The Simpson 1/3 formula on [a, b] approximates the "
                       "integral of f by:",
        "options": [
            "(b-a) * f((a+b)/2)",
            "(b-a)/6 * [f(a) + 4 f((a+b)/2) + f(b)]",
            "(b-a)/2 * [f(a) + f(b)]",
            "(b-a) * f(a)",
        ],
        "correct": 1,
    },
    {
        "id": "B4", "version": "B", "concept_id": "concept_simpson",
        "difficulty": "easy", "points": 1,
        "question_fr": "La methode de Simpson 1/3 est exacte pour les polynomes "
                       "de degre au plus :",
        "question_en": "Simpson's 1/3 rule is exact for polynomials of degree "
                       "at most:",
        "options": ["1", "2", "3", "4"],
        "correct": 2,
    },
    {
        "id": "A5", "version": "A", "concept_id": "concept_simpson",
        "difficulty": "medium", "points": 1,
        "question_fr": "Soit f(x) = x^2. Calculer l'approximation de Simpson 1/3 "
                       "de l'integrale de 0 a 2 de f.",
        "question_en": "Given f(x) = x^2, compute Simpson 1/3 of the integral of "
                       "f from 0 to 2.",
        "options": ["2", "2.5", "8/3 (~2.667)", "4"],
        "correct": 2,
    },
    {
        "id": "B5", "version": "B", "concept_id": "concept_simpson",
        "difficulty": "medium", "points": 1,
        "question_fr": "Soit f(x) = x^3. Calculer l'approximation de Simpson 1/3 "
                       "de l'integrale de 0 a 2 de f.",
        "question_en": "Given f(x) = x^3, compute Simpson 1/3 of the integral of "
                       "f from 0 to 2.",
        "options": ["2", "4", "6", "8/3"],
        "correct": 1,
    },
    {
        "id": "A6", "version": "A", "concept_id": "concept_simpson",
        "difficulty": "hard", "points": 1,
        "question_fr": "L'erreur de la methode de Simpson composite avec n "
                       "sous-intervalles sur [a,b] est en O(h^k). Quelle est "
                       "la valeur de k ?",
        "question_en": "The error of composite Simpson with n subintervals on "
                       "[a,b] is O(h^k). What is k?",
        "options": ["1", "2", "4", "6"],
        "correct": 2,
    },
    {
        "id": "B6", "version": "B", "concept_id": "concept_simpson",
        "difficulty": "hard", "points": 1,
        "question_fr": "Quel ordre de precision (en h) apporte la methode de "
                       "Simpson par rapport aux trapezes pour une fonction lisse ?",
        "question_en": "What precision gain (in h) does Simpson offer over the "
                       "trapezoidal rule for a smooth function?",
        "options": [
            "Meme ordre",
            "2 ordres de mieux (h^4 vs h^2)",
            "1 ordre de mieux",
            "4 ordres de mieux",
        ],
        "correct": 1,
    },
]

# === Concept 3 : Least Squares ===
LEAST_SQUARES_ITEMS = [
    {
        "id": "A7", "version": "A", "concept_id": "concept_least_squares",
        "difficulty": "easy", "points": 1,
        "question_fr": "Dans la regression lineaire des moindres carres "
                       "y = ax + b, on minimise :",
        "question_en": "In linear least-squares regression y = ax + b, we minimize:",
        "options": [
            "Somme des |y_i - (a x_i + b)|",
            "Somme des (y_i - (a x_i + b))^2",
            "max(|y_i - (a x_i + b)|)",
            "Somme des (y_i - x_i)",
        ],
        "correct": 1,
    },
    {
        "id": "B7", "version": "B", "concept_id": "concept_least_squares",
        "difficulty": "easy", "points": 1,
        "question_fr": "Le systeme normal des moindres carres s'ecrit "
                       "(X^T X) theta = ... :",
        "question_en": "The normal equations for least squares are "
                       "(X^T X) theta = ... :",
        "options": ["X^T", "X y", "X^T y", "X^-1 y"],
        "correct": 2,
    },
    {
        "id": "A8", "version": "A", "concept_id": "concept_least_squares",
        "difficulty": "medium", "points": 1,
        "question_fr": "On cherche la droite de regression y = ax + b sur les "
                       "points (0,1), (1,2), (2,4). La pente a vaut :",
        "question_en": "Fit y = ax + b on (0,1), (1,2), (2,4). The slope a is:",
        "options": ["1", "1.5", "2", "2.5"],
        "correct": 1,
    },
    {
        "id": "B8", "version": "B", "concept_id": "concept_least_squares",
        "difficulty": "medium", "points": 1,
        "question_fr": "On cherche la droite de regression y = ax + b sur les "
                       "points (1,2), (2,3), (3,5). La pente a vaut :",
        "question_en": "Fit y = ax + b on (1,2), (2,3), (3,5). The slope a is:",
        "options": ["1", "1.25", "1.5", "2"],
        "correct": 2,
    },
    {
        "id": "A9", "version": "A", "concept_id": "concept_least_squares",
        "difficulty": "hard", "points": 1,
        "question_fr": "Si la matrice X^T X est singuliere, alors :",
        "question_en": "If the matrix X^T X is singular, then:",
        "options": [
            "Il n'existe aucune solution",
            "La solution n'est pas unique (probleme mal pose)",
            "La solution est necessairement nulle",
            "On change de methode pour Newton",
        ],
        "correct": 1,
    },
    {
        "id": "B9", "version": "B", "concept_id": "concept_least_squares",
        "difficulty": "hard", "points": 1,
        "question_fr": "La regularisation de Tikhonov (ridge) modifie le "
                       "systeme normal en :",
        "question_en": "Tikhonov (ridge) regularization modifies the normal "
                       "equations to:",
        "options": [
            "(X^T X) theta = X^T y",
            "(X^T X + lambda I) theta = X^T y",
            "(X^T X - lambda I) theta = X^T y",
            "X theta = y + lambda I",
        ],
        "correct": 1,
    },
]

# === Concept 4 : Newton-Raphson ===
NEWTON_ITEMS = [
    {
        "id": "A10", "version": "A", "concept_id": "concept_newton_raphson",
        "difficulty": "easy", "points": 1,
        "question_fr": "L'iteration de Newton-Raphson pour trouver une racine "
                       "de f(x) = 0 est :",
        "question_en": "The Newton-Raphson iteration for solving f(x) = 0 is:",
        "options": [
            "x_{n+1} = x_n - f(x_n)",
            "x_{n+1} = x_n - f(x_n)/f'(x_n)",
            "x_{n+1} = x_n + f(x_n)/f'(x_n)",
            "x_{n+1} = (x_n + x_{n-1})/2",
        ],
        "correct": 1,
    },
    {
        "id": "B10", "version": "B", "concept_id": "concept_newton_raphson",
        "difficulty": "easy", "points": 1,
        "question_fr": "Quelle est la condition principale pour appliquer "
                       "Newton-Raphson en x_n ?",
        "question_en": "What is the main condition to apply Newton-Raphson at x_n?",
        "options": [
            "f(x_n) = 0",
            "f'(x_n) != 0",
            "f''(x_n) != 0",
            "x_n > 0",
        ],
        "correct": 1,
    },
    {
        "id": "A11", "version": "A", "concept_id": "concept_newton_raphson",
        "difficulty": "medium", "points": 1,
        "question_fr": "Pour f(x) = x^2 - 2, partant de x_0 = 1, donnez x_1 "
                       "par Newton-Raphson.",
        "question_en": "For f(x) = x^2 - 2, starting from x_0 = 1, give x_1 "
                       "by Newton-Raphson.",
        "options": ["1.0", "1.25", "1.5", "2.0"],
        "correct": 2,
    },
    {
        "id": "B11", "version": "B", "concept_id": "concept_newton_raphson",
        "difficulty": "medium", "points": 1,
        "question_fr": "Pour f(x) = x^2 - 3, partant de x_0 = 2, donnez x_1 "
                       "par Newton-Raphson.",
        "question_en": "For f(x) = x^2 - 3, starting from x_0 = 2, give x_1 "
                       "by Newton-Raphson.",
        "options": ["1.5", "1.6667", "1.75", "2.0"],
        "correct": 2,
    },
    {
        "id": "A12", "version": "A", "concept_id": "concept_newton_raphson",
        "difficulty": "hard", "points": 1,
        "question_fr": "L'ordre de convergence de Newton-Raphson, sous les "
                       "conditions classiques, est :",
        "question_en": "The order of convergence of Newton-Raphson under "
                       "standard conditions is:",
        "options": [
            "Lineaire (1)",
            "Quadratique (2)",
            "Cubique (3)",
            "Exponentiel",
        ],
        "correct": 1,
    },
    {
        "id": "B12", "version": "B", "concept_id": "concept_newton_raphson",
        "difficulty": "hard", "points": 1,
        "question_fr": "Si f'(alpha) = 0 ou alpha est la racine (racine "
                       "multiple), l'ordre de convergence de Newton-Raphson "
                       "tombe a :",
        "question_en": "If f'(alpha) = 0 where alpha is the root (multiple "
                       "root), the convergence order of Newton-Raphson drops to:",
        "options": [
            "Lineaire (1)",
            "Quadratique (2)",
            "Cubique (3)",
            "Pas de convergence",
        ],
        "correct": 0,
    },
]

# === Concept 5 : Bisection ===
BISECTION_ITEMS = [
    {
        "id": "A13", "version": "A", "concept_id": "concept_bissection",
        "difficulty": "easy", "points": 1,
        "question_fr": "La methode de bissection necessite, sur [a, b], que :",
        "question_en": "The bisection method requires, on [a, b], that:",
        "options": [
            "f(a) = f(b)",
            "f(a) * f(b) < 0",
            "f(a) * f(b) > 0",
            "f'(a) != 0",
        ],
        "correct": 1,
    },
    {
        "id": "B13", "version": "B", "concept_id": "concept_bissection",
        "difficulty": "easy", "points": 1,
        "question_fr": "Si f est continue sur [a,b] avec f(a) = -2 et "
                       "f(b) = 3, alors la bissection :",
        "question_en": "If f is continuous on [a,b] with f(a) = -2 and "
                       "f(b) = 3, then bisection:",
        "options": [
            "Ne fonctionne pas",
            "Trouve une racine en 1 iteration",
            "Trouve une racine apres un nombre fini d'iterations",
            "Diverge",
        ],
        "correct": 2,
    },
    {
        "id": "A14", "version": "A", "concept_id": "concept_bissection",
        "difficulty": "medium", "points": 1,
        "question_fr": "L'erreur apres n iterations de bissection sur [a, b] "
                       "est majoree par :",
        "question_en": "The error after n bisection iterations on [a, b] is "
                       "bounded by:",
        "options": [
            "(b - a) / n",
            "(b - a) / 2^n",
            "(b - a) * 2^n",
            "(b - a) / (n + 1)",
        ],
        "correct": 1,
    },
    {
        "id": "B14", "version": "B", "concept_id": "concept_bissection",
        "difficulty": "medium", "points": 1,
        "question_fr": "Combien d'iterations de bissection sur [0, 1] sont "
                       "necessaires pour garantir une erreur < 10^-3 ?",
        "question_en": "How many bisection iterations on [0, 1] are needed "
                       "to guarantee error < 10^-3?",
        "options": ["5", "8", "10", "20"],
        "correct": 2,
    },
    {
        "id": "A15", "version": "A", "concept_id": "concept_bissection",
        "difficulty": "hard", "points": 1,
        "question_fr": "Comparee a Newton-Raphson, la bissection est :",
        "question_en": "Compared to Newton-Raphson, bisection is:",
        "options": [
            "Plus rapide mais moins fiable",
            "Plus fiable mais plus lente (convergence lineaire vs quadratique)",
            "Plus rapide et plus fiable",
            "Equivalente",
        ],
        "correct": 1,
    },
    {
        "id": "B15", "version": "B", "concept_id": "concept_bissection",
        "difficulty": "hard", "points": 1,
        "question_fr": "Pourquoi prefere-t-on parfois la methode de la "
                       "secante a Newton-Raphson ?",
        "question_en": "Why is the secant method sometimes preferred over "
                       "Newton-Raphson?",
        "options": [
            "Convergence plus rapide",
            "Pas besoin de calculer la derivee",
            "Garantit la convergence",
            "Aucune des trois",
        ],
        "correct": 1,
    },
]

# === Aggregation ===
ALL_ITEMS: list[dict] = (
    LAGRANGE_ITEMS + SIMPSON_ITEMS + LEAST_SQUARES_ITEMS
    + NEWTON_ITEMS + BISECTION_ITEMS
)

# Index by version for fast distribution.
ITEMS_VERSION_A: list[dict] = [it for it in ALL_ITEMS if it["version"] == "A"]
ITEMS_VERSION_B: list[dict] = [it for it in ALL_ITEMS if it["version"] == "B"]

# Sanity check at load : we must have 15 + 15 = 30.
assert len(ITEMS_VERSION_A) == 15, f"Got {len(ITEMS_VERSION_A)} items in A"
assert len(ITEMS_VERSION_B) == 15, f"Got {len(ITEMS_VERSION_B)} items in B"
assert len(ALL_ITEMS) == 30


def items_for_version(version: str) -> list[dict]:
    """Returns the 15 items of a version (A or B), in 'student' form :
    options displayed but `correct` removed so as not to spoil."""
    src = ITEMS_VERSION_A if version == "A" else ITEMS_VERSION_B
    out = []
    for it in src:
        clean = {k: v for k, v in it.items() if k != "correct"}
        out.append(clean)
    return out


def grade_answers(version: str, answers: dict[str, str | int]) -> dict:
    """Computes the normalized score 0-100.

    answers : map {item_id: int (option index) | str (free computation)}.
    Returns dict {score: float, max: int, raw: int, per_item: list[dict]}.
    """
    src = ITEMS_VERSION_A if version == "A" else ITEMS_VERSION_B
    raw = 0
    max_pts = 0
    per_item = []
    for it in src:
        max_pts += it["points"]
        user_ans = answers.get(it["id"])
        is_correct = False
        if it["options"] is None:
            # Open question : normalized string comparison.
            # We let SymPy do the comparison if available, otherwise a
            # literal comparison (no spaces, lowercase). For the pre/post-test
            # we accept this approximation : the bank is small, we will have
            # very few disputable cases to handle by hand.
            if isinstance(user_ans, str):
                norm_user = user_ans.replace(" ", "").lower()
                norm_correct = str(it["correct"]).replace(" ", "").lower()
                is_correct = norm_user == norm_correct
        else:
            # MCQ : expected index.
            try:
                is_correct = int(user_ans) == it["correct"]
            except (TypeError, ValueError):
                is_correct = False
        if is_correct:
            raw += it["points"]
        per_item.append({
            "id": it["id"],
            "concept_id": it["concept_id"],
            "difficulty": it["difficulty"],
            "is_correct": is_correct,
            "points_earned": it["points"] if is_correct else 0,
            "points_max": it["points"],
        })
    score = round((raw / max_pts) * 100, 2) if max_pts else 0.0
    return {"score": score, "raw": raw, "max": max_pts, "per_item": per_item}
