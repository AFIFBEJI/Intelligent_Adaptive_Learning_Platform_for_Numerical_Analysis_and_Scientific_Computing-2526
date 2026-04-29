# ============================================================
# Banque de questions diagnostiques - Quiz d'onboarding
# ============================================================
# 30 QCM ecrites a la main (2 par concept Neo4j) pour le quiz
# diagnostique post-inscription.
#
# Pourquoi pas un LLM ? Le modele fine-tune Gemma E2B est trop petit
# (2B params effectifs) pour generer des QCM avec 4 distracteurs
# coherents ET la vraie bonne reponse. Il invente des questions
# dont la bonne reponse manque, ce qui est demoralisant pour
# l'etudiant et fausse la calibration de son niveau.
#
# Cette banque garantit :
# - Couverture systematique des 15 concepts du graphe Neo4j
# - Bonne reponse dans les options (validee a la main)
# - Distracteurs plausibles mais clairement faux
# - Explication pedagogique pour chaque erreur
#
# A la generation du quiz diagnostique, on pioche 5 questions au
# hasard reparties sur les 3 modules (1-2 par module) avec un seed
# par etudiant + timestamp pour garantir la diversite.
# ============================================================

# Format : liste de dict avec
#   concept_id     : ID Neo4j du concept (doit matcher seed_neo4j.py)
#   module_id      : ID Neo4j du module
#   module_name    : Nom lisible du module
#   question       : Enonce (LaTeX autorise via $...$)
#   options        : 4 strings distincts
#   correct_answer : Texte EXACT de la bonne option
#   explanation    : Pourquoi c'est la bonne reponse (pedagogique)
#   difficulty     : "facile" pour le diagnostique

DIAGNOSTIC_QUESTION_BANK: list[dict] = [
    # ============================================================
    # MODULE 1 — INTERPOLATION
    # ============================================================
    # --- concept_polynomial_basics ---
    {
        "concept_id": "concept_polynomial_basics",
        "module_id": "module_interpolation",
        "module_name": "Interpolation",
        "question": "Quel est le degre du polynome $p(x) = 3x^4 - 2x^2 + 5$ ?",
        "options": ["2", "3", "4", "5"],
        "correct_answer": "4",
        "explanation": "Le degre d'un polynome est la plus grande puissance de $x$ avec un coefficient non nul. Ici c'est $x^4$, donc degre 4.",
        "difficulty": "facile",
    },
    {
        "concept_id": "concept_polynomial_basics",
        "module_id": "module_interpolation",
        "module_name": "Interpolation",
        "question": "Combien de coefficients faut-il pour definir un polynome de degre 3 ?",
        "options": ["2", "3", "4", "5"],
        "correct_answer": "4",
        "explanation": "Un polynome de degre $n$ a $n+1$ coefficients ($a_0, a_1, ..., a_n$). Donc 4 coefficients pour le degre 3.",
        "difficulty": "facile",
    },
    # --- concept_lagrange ---
    {
        "concept_id": "concept_lagrange",
        "module_id": "module_interpolation",
        "module_name": "Interpolation",
        "question": "Combien faut-il de points pour construire un polynome de Lagrange unique de degre au plus $n$ ?",
        "options": ["$n$", "$n+1$", "$2n$", "$n-1$"],
        "correct_answer": "$n+1$",
        "explanation": "Avec $n+1$ points distincts, il existe un unique polynome interpolateur de degre au plus $n$ (theoreme d'unicite).",
        "difficulty": "facile",
    },
    {
        "concept_id": "concept_lagrange",
        "module_id": "module_interpolation",
        "module_name": "Interpolation",
        "question": "Le polynome de base $L_i(x)$ de Lagrange a quelle propriete cle ?",
        "options": [
            "Il vaut 1 partout",
            "Il vaut 1 en $x_i$ et 0 aux autres $x_j$",
            "Il vaut 0 en $x_i$ et 1 ailleurs",
            "Il est egal a $x^i$",
        ],
        "correct_answer": "Il vaut 1 en $x_i$ et 0 aux autres $x_j$",
        "explanation": "C'est la propriete d'interpolation : $L_i(x_j) = \\delta_{ij}$. Elle rend la formule $p(x) = \\sum y_i L_i(x)$ directe.",
        "difficulty": "facile",
    },
    # --- concept_divided_differences ---
    {
        "concept_id": "concept_divided_differences",
        "module_id": "module_interpolation",
        "module_name": "Interpolation",
        "question": "La table des differences divisees sert principalement a :",
        "options": [
            "Calculer des derivees exactes",
            "Construire le polynome de Newton",
            "Resoudre des equations differentielles",
            "Trouver les racines d'un polynome",
        ],
        "correct_answer": "Construire le polynome de Newton",
        "explanation": "Les differences divisees sont les coefficients du polynome interpolateur de Newton, methode equivalente a Lagrange mais incrementale.",
        "difficulty": "facile",
    },
    {
        "concept_id": "concept_divided_differences",
        "module_id": "module_interpolation",
        "module_name": "Interpolation",
        "question": "La difference divisee d'ordre 0, $f[x_0]$, vaut :",
        "options": ["$f'(x_0)$", "$f(x_0)$", "$0$", "$x_0$"],
        "correct_answer": "$f(x_0)$",
        "explanation": "Par definition, $f[x_i] = f(x_i)$. Les differences d'ordre superieur sont calculees recursivement a partir de la.",
        "difficulty": "facile",
    },
    # --- concept_newton_interpolation ---
    {
        "concept_id": "concept_newton_interpolation",
        "module_id": "module_interpolation",
        "module_name": "Interpolation",
        "question": "L'avantage principal de l'interpolation de Newton par rapport a Lagrange est :",
        "options": [
            "Plus precise mathematiquement",
            "Forme incrementale (ajouter un point ne refait pas tout le calcul)",
            "Pas besoin de table de differences",
            "Fonctionne uniquement avec des points equidistants",
        ],
        "correct_answer": "Forme incrementale (ajouter un point ne refait pas tout le calcul)",
        "explanation": "Newton permet d'ajouter un nouveau point sans recalculer les coefficients precedents, contrairement a Lagrange qui reprend a zero.",
        "difficulty": "facile",
    },
    {
        "concept_id": "concept_newton_interpolation",
        "module_id": "module_interpolation",
        "module_name": "Interpolation",
        "question": "Pour interpoler 3 points avec Newton, combien de differences divisees calcule-t-on ?",
        "options": [
            "1 seule (l'ordre 0)",
            "3 (ordres 0, 1, 2)",
            "9 (table complete)",
            "Aucune",
        ],
        "correct_answer": "3 (ordres 0, 1, 2)",
        "explanation": "Pour 3 points on utilise $f[x_0]$, $f[x_0,x_1]$ et $f[x_0,x_1,x_2]$ comme coefficients du polynome de degre 2.",
        "difficulty": "facile",
    },
    # --- concept_spline_interpolation ---
    {
        "concept_id": "concept_spline_interpolation",
        "module_id": "module_interpolation",
        "module_name": "Interpolation",
        "question": "Une spline cubique est :",
        "options": [
            "Un polynome de degre 3 sur tout l'intervalle",
            "Un assemblage de polynomes de degre 3 par morceaux",
            "Une fonction trigonometrique",
            "Un polynome de Lagrange a 4 points",
        ],
        "correct_answer": "Un assemblage de polynomes de degre 3 par morceaux",
        "explanation": "Les splines cubiques interpolent par morceaux avec des polynomes de degre 3, raccordes en classe $C^2$. Elles evitent le phenomene de Runge.",
        "difficulty": "facile",
    },
    {
        "concept_id": "concept_spline_interpolation",
        "module_id": "module_interpolation",
        "module_name": "Interpolation",
        "question": "Le phenomene de Runge se manifeste quand :",
        "options": [
            "Les splines convergent trop vite",
            "Un polynome interpolateur global de haut degre oscille fortement aux extremites",
            "L'integration numerique diverge",
            "La descente de gradient s'arrete prematurement",
        ],
        "correct_answer": "Un polynome interpolateur global de haut degre oscille fortement aux extremites",
        "explanation": "Avec des points equidistants et un grand $n$, l'interpolation polynomiale globale produit des oscillations enormes pres des bords. Les splines evitent ce probleme.",
        "difficulty": "facile",
    },

    # ============================================================
    # MODULE 2 — INTEGRATION NUMERIQUE
    # ============================================================
    # --- concept_riemann_sums ---
    {
        "concept_id": "concept_riemann_sums",
        "module_id": "module_integration",
        "module_name": "Numerical Integration",
        "question": "Une somme de Riemann approxime l'integrale d'une fonction par :",
        "options": [
            "Une somme de rectangles",
            "Une somme de triangles",
            "Un developpement de Taylor",
            "Une serie de Fourier",
        ],
        "correct_answer": "Une somme de rectangles",
        "explanation": "On decoupe l'intervalle $[a,b]$ en sous-intervalles et on somme les aires de rectangles $f(x_i) \\times \\Delta x$.",
        "difficulty": "facile",
    },
    {
        "concept_id": "concept_riemann_sums",
        "module_id": "module_integration",
        "module_name": "Numerical Integration",
        "question": "Une somme de Riemann a droite (right Riemann sum) utilise :",
        "options": [
            "$f$ evalue au debut de chaque sous-intervalle",
            "$f$ evalue a la fin de chaque sous-intervalle",
            "$f$ evalue au milieu",
            "La moyenne de $f$ sur l'intervalle",
        ],
        "correct_answer": "$f$ evalue a la fin de chaque sous-intervalle",
        "explanation": "Right Riemann : sur $[x_i, x_i+h]$ on prend $f(x_i+h)$. A gauche on prendrait $f(x_i)$.",
        "difficulty": "facile",
    },
    # --- concept_definite_integrals ---
    {
        "concept_id": "concept_definite_integrals",
        "module_id": "module_integration",
        "module_name": "Numerical Integration",
        "question": "L'integrale definie $\\int_a^b f(x)\\,dx$ represente geometriquement :",
        "options": [
            "La pente de $f$ en $x=a$",
            "L'aire algebrique sous la courbe entre $a$ et $b$",
            "La valeur maximum de $f$ sur $[a,b]$",
            "La derivee seconde de $F$",
        ],
        "correct_answer": "L'aire algebrique sous la courbe entre $a$ et $b$",
        "explanation": "Aire signee : positive au-dessus de l'axe $Ox$, negative en-dessous. C'est ce que mesure l'integrale definie.",
        "difficulty": "facile",
    },
    {
        "concept_id": "concept_definite_integrals",
        "module_id": "module_integration",
        "module_name": "Numerical Integration",
        "question": "Le theoreme fondamental du calcul dit que $\\int_a^b f(x)\\,dx$ vaut :",
        "options": [
            "$F(a) - F(b)$",
            "$F(b) - F(a)$ ou $F$ est une primitive de $f$",
            "$f(b) - f(a)$",
            "$f'(b) - f'(a)$",
        ],
        "correct_answer": "$F(b) - F(a)$ ou $F$ est une primitive de $f$",
        "explanation": "Si $F'=f$, alors $\\int_a^b f(x)\\,dx = F(b)-F(a)$. C'est la base de l'integration symbolique.",
        "difficulty": "facile",
    },
    # --- concept_trapezoidal ---
    {
        "concept_id": "concept_trapezoidal",
        "module_id": "module_integration",
        "module_name": "Numerical Integration",
        "question": "La methode des trapezes approche $f$ sur chaque sous-intervalle par :",
        "options": [
            "Une constante",
            "Une droite",
            "Une parabole",
            "Un polynome de degre 3",
        ],
        "correct_answer": "Une droite",
        "explanation": "On relie $f(a)$ et $f(b)$ par une droite et on calcule l'aire du trapeze. L'erreur est en $O(h^2)$.",
        "difficulty": "facile",
    },
    {
        "concept_id": "concept_trapezoidal",
        "module_id": "module_integration",
        "module_name": "Numerical Integration",
        "question": "L'erreur de la methode des trapezes composee sur $n$ sous-intervalles est en :",
        "options": ["$O(h)$", "$O(h^2)$", "$O(h^4)$", "$O(1)$"],
        "correct_answer": "$O(h^2)$",
        "explanation": "Avec $h = (b-a)/n$, l'erreur globale decroit comme $h^2$. Simpson fait mieux avec $O(h^4)$.",
        "difficulty": "facile",
    },
    # --- concept_simpson ---
    {
        "concept_id": "concept_simpson",
        "module_id": "module_integration",
        "module_name": "Numerical Integration",
        "question": "La regle de Simpson approche $f$ sur chaque paire de sous-intervalles par :",
        "options": [
            "Une droite",
            "Une parabole",
            "Une constante",
            "Une exponentielle",
        ],
        "correct_answer": "Une parabole",
        "explanation": "Simpson utilise un polynome de degre 2 ajuste sur 3 points consecutifs. Erreur en $O(h^4)$, plus precis que les trapezes.",
        "difficulty": "facile",
    },
    {
        "concept_id": "concept_simpson",
        "module_id": "module_integration",
        "module_name": "Numerical Integration",
        "question": "La methode de Simpson composee necessite un nombre de sous-intervalles :",
        "options": ["Pair", "Impair", "Premier", "Quelconque"],
        "correct_answer": "Pair",
        "explanation": "Chaque parabole couvre 2 sous-intervalles consecutifs ; il en faut donc un nombre pair pour la formule composee.",
        "difficulty": "facile",
    },
    # --- concept_gaussian_quadrature ---
    {
        "concept_id": "concept_gaussian_quadrature",
        "module_id": "module_integration",
        "module_name": "Numerical Integration",
        "question": "L'avantage de la quadrature de Gauss-Legendre est :",
        "options": [
            "Elle utilise des points equidistants",
            "Elle est exacte pour les polynomes jusqu'a un degre eleve avec peu de points",
            "Elle est plus simple a implementer que les trapezes",
            "Elle fonctionne uniquement sur $[0,1]$",
        ],
        "correct_answer": "Elle est exacte pour les polynomes jusqu'a un degre eleve avec peu de points",
        "explanation": "Avec $n$ points de Gauss, on integre exactement les polynomes de degre $\\le 2n-1$ — bien mieux que Newton-Cotes.",
        "difficulty": "facile",
    },
    {
        "concept_id": "concept_gaussian_quadrature",
        "module_id": "module_integration",
        "module_name": "Numerical Integration",
        "question": "Les noeuds de Gauss-Legendre sur $[-1,1]$ sont :",
        "options": [
            "Equidistants",
            "Les racines des polynomes de Legendre",
            "Les racines de $\\cos(\\pi x)$",
            "Les entiers de $-1$ a $1$",
        ],
        "correct_answer": "Les racines des polynomes de Legendre",
        "explanation": "Les $n$ noeuds sont les $n$ racines de $P_n$ (polynome de Legendre de degre $n$) sur $[-1,1]$.",
        "difficulty": "facile",
    },

    # ============================================================
    # MODULE 3 — APPROXIMATION POLYNOMIALE & OPTIMISATION
    # ============================================================
    # --- concept_least_squares ---
    {
        "concept_id": "concept_least_squares",
        "module_id": "module_approximation",
        "module_name": "Polynomial Approximation & Optimization",
        "question": "La methode des moindres carres minimise :",
        "options": [
            "L'erreur maximale",
            "La somme des erreurs absolues",
            "La somme des carres des erreurs",
            "L'erreur mediane",
        ],
        "correct_answer": "La somme des carres des erreurs",
        "explanation": "Minimiser $\\sum (y_i - p(x_i))^2$ donne un systeme lineaire (equations normales) facile a resoudre.",
        "difficulty": "facile",
    },
    {
        "concept_id": "concept_least_squares",
        "module_id": "module_approximation",
        "module_name": "Polynomial Approximation & Optimization",
        "question": "Les equations normales du moindres carres pour $Ax = b$ s'ecrivent :",
        "options": [
            "$A^T A\\, x = A^T b$",
            "Une equation differentielle",
            "Une integrale",
            "Une serie infinie",
        ],
        "correct_answer": "$A^T A\\, x = A^T b$",
        "explanation": "Pour minimiser $\\|Ax - b\\|^2$, on resout le systeme symetrique $A^T A x = A^T b$ (les equations normales).",
        "difficulty": "facile",
    },
    # --- concept_orthogonal_polynomials ---
    {
        "concept_id": "concept_orthogonal_polynomials",
        "module_id": "module_approximation",
        "module_name": "Polynomial Approximation & Optimization",
        "question": "Les polynomes orthogonaux (Legendre, Tchebychev, etc.) sont surtout utilises pour :",
        "options": [
            "Resoudre des equations differentielles uniquement",
            "Faciliter l'approximation et la quadrature",
            "Calculer des derivees",
            "Tracer des courbes en 3D",
        ],
        "correct_answer": "Faciliter l'approximation et la quadrature",
        "explanation": "Leur orthogonalite ($\\int P_i P_j w = 0$ si $i \\ne j$) decoupe le probleme d'approximation en projections independantes.",
        "difficulty": "facile",
    },
    {
        "concept_id": "concept_orthogonal_polynomials",
        "module_id": "module_approximation",
        "module_name": "Polynomial Approximation & Optimization",
        "question": "Sur $[-1,1]$ avec poids $w(x) = 1$, les polynomes orthogonaux sont ceux de :",
        "options": [
            "Tchebychev de 1ere espece",
            "Legendre",
            "Hermite",
            "Laguerre",
        ],
        "correct_answer": "Legendre",
        "explanation": "Tchebychev a un poids $1/\\sqrt{1-x^2}$, Hermite est sur $\\mathbb{R}$ avec poids gaussien, Laguerre sur $[0,\\infty)$. Legendre = poids 1 sur $[-1,1]$.",
        "difficulty": "facile",
    },
    # --- concept_minimax_approximation ---
    {
        "concept_id": "concept_minimax_approximation",
        "module_id": "module_approximation",
        "module_name": "Polynomial Approximation & Optimization",
        "question": "L'approximation minimax (Tchebychev) cherche a minimiser :",
        "options": [
            "La somme des carres des erreurs",
            "L'erreur maximale $\\|f - p\\|_\\infty$",
            "Le nombre de coefficients",
            "Le degre du polynome",
        ],
        "correct_answer": "L'erreur maximale $\\|f - p\\|_\\infty$",
        "explanation": "On minimise $\\sup |f(x) - p(x)|$ sur l'intervalle. La solution est caracterisee par le theoreme d'equi-oscillation.",
        "difficulty": "facile",
    },
    {
        "concept_id": "concept_minimax_approximation",
        "module_id": "module_approximation",
        "module_name": "Polynomial Approximation & Optimization",
        "question": "Le theoreme d'equi-oscillation de Tchebychev dit que la meilleure approximation polynomiale de degre $n$ atteint son extremum en signe alterne :",
        "options": [
            "1 fois",
            "2 fois",
            "Au moins $n+2$ fois",
            "Jamais",
        ],
        "correct_answer": "Au moins $n+2$ fois",
        "explanation": "C'est cette propriete qui caracterise l'unique polynome minimax de degre $n$ : l'erreur oscille en signe au moins $n+2$ fois.",
        "difficulty": "facile",
    },
    # --- concept_gradient_descent ---
    {
        "concept_id": "concept_gradient_descent",
        "module_id": "module_approximation",
        "module_name": "Polynomial Approximation & Optimization",
        "question": "La descente de gradient met a jour les parametres dans la direction :",
        "options": [
            "Du gradient (pour maximiser)",
            "Opposee au gradient (pour minimiser)",
            "Perpendiculaire au gradient",
            "Aleatoire",
        ],
        "correct_answer": "Opposee au gradient (pour minimiser)",
        "explanation": "Le gradient pointe vers la plus forte montee ; pour descendre on prend la direction opposee : $\\theta \\leftarrow \\theta - \\eta \\nabla f(\\theta)$.",
        "difficulty": "facile",
    },
    {
        "concept_id": "concept_gradient_descent",
        "module_id": "module_approximation",
        "module_name": "Polynomial Approximation & Optimization",
        "question": "Si le learning rate $\\eta$ est trop grand, la descente de gradient :",
        "options": [
            "Converge plus vite",
            "Risque de diverger ou d'osciller",
            "Trouve toujours le minimum global",
            "N'a aucun effet",
        ],
        "correct_answer": "Risque de diverger ou d'osciller",
        "explanation": "$\\eta$ trop grand $\\rightarrow$ on saute par-dessus le minimum. Trop petit $\\rightarrow$ convergence lente. Compromis classique.",
        "difficulty": "facile",
    },
    # --- concept_newton_optimization ---
    {
        "concept_id": "concept_newton_optimization",
        "module_id": "module_approximation",
        "module_name": "Polynomial Approximation & Optimization",
        "question": "La methode de Newton pour l'optimisation utilise :",
        "options": [
            "Seulement le gradient",
            "Le gradient et la matrice hessienne",
            "Seulement la fonction de cout",
            "La transformee de Fourier",
        ],
        "correct_answer": "Le gradient et la matrice hessienne",
        "explanation": "$\\theta \\leftarrow \\theta - H^{-1} \\nabla f$. Convergence quadratique pres de l'optimum mais necessite calcul (et inversion) de la hessienne.",
        "difficulty": "facile",
    },
    {
        "concept_id": "concept_newton_optimization",
        "module_id": "module_approximation",
        "module_name": "Polynomial Approximation & Optimization",
        "question": "Comparee a la descente de gradient, la methode de Newton :",
        "options": [
            "Converge plus lentement",
            "Converge plus vite pres de l'optimum mais coute plus par iteration",
            "Ne necessite aucun calcul de derivee",
            "Est exclusivement utilisee en cryptographie",
        ],
        "correct_answer": "Converge plus vite pres de l'optimum mais coute plus par iteration",
        "explanation": "Convergence quadratique vs lineaire pour le gradient, mais inversion de hessienne en $O(d^3)$ par iteration en dimension $d$.",
        "difficulty": "facile",
    },
]


def get_questions_by_module() -> dict[str, list[dict]]:
    """Regroupe les questions par module_id pour le tirage equitable."""
    by_module: dict[str, list[dict]] = {}
    for q in DIAGNOSTIC_QUESTION_BANK:
        by_module.setdefault(q["module_id"], []).append(q)
    return by_module
