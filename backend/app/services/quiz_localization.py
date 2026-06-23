from __future__ import annotations

import re
from copy import deepcopy
from typing import Any

SUPPORTED_LANGUAGES = {"en", "fr"}


def normalize_quiz_language(language: str | None) -> str:
    """Return a supported quiz language, defaulting to English."""
    return "fr" if language == "fr" else "en"


def true_false_labels(language: str | None) -> tuple[str, str]:
    return ("Vrai", "Faux") if normalize_quiz_language(language) == "fr" else ("True", "False")


_EXACT_EN = {
    "Vrai": "True",
    "Faux": "False",
    "Aucune": "None",
    "Aucun": "None",
    "Jamais": "Never",
    "Plus precis": "More accurate",
    "Plus precise mathematiquement": "Mathematically more accurate",
    "Il vaut 1 partout": "It is 1 everywhere",
    "Il vaut 1 en $x_i$ et 0 aux autres $x_j$": "It is 1 at $x_i$ and 0 at the other $x_j$",
    "Il vaut 0 en $x_i$ et 1 ailleurs": "It is 0 at $x_i$ and 1 elsewhere",
    "Il est egal a $x^i$": "It is equal to $x^i$",
    "Forme incrementale (ajouter un point ne refait pas tout le calcul)": "Incremental form (adding a point does not recompute everything)",
    "Pas besoin de table de differences": "No divided-difference table needed",
    "Fonctionne uniquement avec des points equidistants": "Only works with equally spaced points",
    "Le meme polynome (formes equivalentes)": "The same polynomial (equivalent forms)",
    "Des polynomes differents": "Different polynomials",
    "Newton est toujours superieur": "Newton is always better",
    "Lagrange ne fonctionne qu'en 1D": "Lagrange only works in 1D",
    "On veut ajouter des points dynamiquement": "We want to add points dynamically",
    "On evalue en un seul point": "We evaluate at a single point",
    "Un assemblage de polynomes de degre 3 par morceaux": "A piecewise assembly of degree-3 polynomials",
    "Un polynome de degre 3 sur tout l'intervalle": "A degree-3 polynomial over the whole interval",
    "Une fonction trigonometrique": "A trigonometric function",
    "Un polynome de Lagrange a 4 points": "A Lagrange polynomial with 4 points",
    "Construire le polynome de Newton": "Build the Newton interpolation polynomial",
    "Calculer des derivees exactes": "Compute exact derivatives",
    "Resoudre des equations differentielles": "Solve differential equations",
    "Trouver les racines d'un polynome": "Find the roots of a polynomial",
    "Une somme de rectangles": "A sum of rectangles",
    "Une somme de triangles": "A sum of triangles",
    "Un developpement de Taylor": "A Taylor expansion",
    "Une serie de Fourier": "A Fourier series",
    "L'aire algebrique sous la courbe entre $a$ et $b$": "The signed area under the curve between $a$ and $b$",
    "La pente de $f$ en $x=a$": "The slope of $f$ at $x=a$",
    "La valeur maximum de $f$ sur $[a,b]$": "The maximum value of $f$ on $[a,b]$",
    "La derivee seconde de $F$": "The second derivative of $F$",
    "2 au plus": "At most 2",
    "Indetermine": "Undetermined",
    "Recalcul total si on ajoute un point": "Full recomputation when adding a point",
    "Necessite des points equidistants": "Requires equally spaced points",
    "Ne fonctionne que pour des polynomes lineaires": "Only works for linear polynomials",
    "Non, l'ordre des points compte": "No, the order of points matters",
    "Oui, $f[x_0, x_1] = f[x_1, x_0]$": "Yes, $f[x_0, x_1] = f[x_1, x_0]$",
    "Seulement pour l'ordre 1": "Only for order 1",
    "Seulement pour les polynomes": "Only for polynomials",
    "Inversement proportionnels": "Inversely proportional",
    "Les splines convergent trop vite": "Splines converge too quickly",
    "Un polynome interpolateur global de haut degre oscille fortement aux extremites": "A high-degree global interpolating polynomial oscillates strongly near the endpoints",
    "L'integration numerique diverge": "Numerical integration diverges",
    "La descente de gradient s'arrete prematurement": "Gradient descent stops too early",
    "Aucune condition": "No condition",
    "Evite les oscillations (Runge), bonne approximation locale": "Avoids oscillations (Runge), good local approximation",
    "Plus rapide a calculer": "Faster to compute",
    "Plus precise sur tout l'intervalle": "More accurate over the whole interval",
    "Plus simple a implementer": "Easier to implement",
    "$f$ evalue au debut de chaque sous-intervalle": "$f$ evaluated at the start of each subinterval",
    "$f$ evalue a la fin de chaque sous-intervalle": "$f$ evaluated at the end of each subinterval",
    "$f$ evaluee au milieu de chaque sous-intervalle": "$f$ evaluated at the midpoint of each subinterval",
    "$f$ evalue au milieu": "$f$ evaluated at the midpoint",
    "La moyenne de $f$ sur l'intervalle": "The average of $f$ over the interval",
    "Une droite": "A line",
    "Une parabole": "A parabola",
    "Une constante": "A constant",
    "Une exponentielle": "An exponential",
    "Pair": "Even",
    "Impair": "Odd",
    "Premier": "Prime",
    "Quelconque": "Any",
    "Sous-estime l'integrale": "Underestimates the integral",
    "Surestime l'integrale": "Overestimates the integral",
    "De degre $\\le 1$": "Of degree $\\le 1$",
    "De degre $\\le 2$": "Of degree $\\le 2$",
    "Elle utilise des points equidistants": "It uses equally spaced points",
    "Elle est exacte pour les polynomes jusqu'a un degre eleve avec peu de points": "It is exact for high-degree polynomials with few points",
    "Elle est plus simple a implementer que les trapezes": "It is easier to implement than the trapezoidal rule",
    "Elle fonctionne uniquement sur $[0,1]$": "It only works on $[0,1]$",
    "Equidistants": "Equally spaced",
    "Les racines des polynomes de Legendre": "The roots of Legendre polynomials",
    "Les racines de $\\cos(\\pi x)$": "The roots of $\\cos(\\pi x)$",
    "Les entiers de $-1$ a $1$": "The integers from $-1$ to $1$",
    "Fait un changement de variable affine vers $[-1, 1]$": "Makes an affine change of variable to $[-1, 1]$",
    "Gauss necessite moins de points": "Gauss needs fewer points",
    "La somme des carres des erreurs": "The sum of squared errors",
    "La somme des erreurs absolues": "The sum of absolute errors",
    "L'erreur mediane": "The median error",
    "Une equation differentielle": "A differential equation",
    "Une integrale": "An integral",
    "Une serie infinie": "An infinite series",
    "On obtient un systeme lineaire (calculs propres)": "It gives a linear system (clean computations)",
    "Le probleme devient non lineaire": "The problem becomes nonlinear",
    "On perd toute solution": "All solutions are lost",
    "La methode QR ou SVD": "The QR method or SVD",
    "Former $A^T A$ explicitement": "Form $A^T A$ explicitly",
    "Augmenter le bruit": "Increase the noise",
    "Reduire le degre du polynome": "Reduce the polynomial degree",
    "Une norme quelconque": "Any norm",
    "La norme $L^2$ (euclidienne)": "The $L^2$ norm (Euclidean)",
    "La norme $L^\\infty$": "The $L^\\infty$ norm",
    "La norme $L^1$": "The $L^1$ norm",
    "Tchebychev de 1ere espece": "Chebyshev of the first kind",
    "Legendre": "Legendre",
    "Hermite": "Hermite",
    "Laguerre": "Laguerre",
    "Exactement $n$ dans l'intervalle": "Exactly $n$ in the interval",
    "Infini": "Infinitely many",
    "Aucune relation generale": "No general relation",
    "L'erreur maximale $\\|f - p\\|_\\infty$": "The maximum error $\\|f - p\\|_\\infty$",
    "Le nombre de coefficients": "The number of coefficients",
    "Le degre du polynome": "The polynomial degree",
    "Au moins $n+2$ fois": "At least $n+2$ times",
    "1 fois": "Once",
    "2 fois": "Twice",
    "Remez": "Remez",
    "Troncature de la serie de Tchebychev": "Truncation of the Chebyshev series",
    "Differences finies": "Finite differences",
    "Les racines de $T_{n+1}$ (Tchebychev)": "The roots of $T_{n+1}$ (Chebyshev)",
    "Des points equidistants": "Equally spaced points",
    "Les entiers naturels": "Natural numbers",
    "Aleatoirement": "Randomly",
    "Du gradient (pour maximiser)": "Along the gradient (to maximize)",
    "Opposee au gradient (pour minimiser)": "Opposite the gradient (to minimize)",
    "Perpendiculaire au gradient": "Perpendicular to the gradient",
    "Aleatoire": "Random",
    "Converge plus vite": "Converges faster",
    "Risque de diverger ou d'osciller": "May diverge or oscillate",
    "Trouve toujours le minimum global": "Always finds the global minimum",
    "N'a aucun effet": "Has no effect",
    "Calcule le gradient sur tout le dataset": "Computes the gradient on the full dataset",
    "Calcule le gradient sur un mini-batch": "Computes the gradient on a mini-batch",
    "Ne calcule jamais de gradient": "Never computes a gradient",
    "Inverse une matrice": "Inverts a matrix",
    "Adapte le learning rate par parametre": "Adapts the learning rate per parameter",
    "Calcule la hessienne": "Computes the Hessian",
    "Ne fonctionne pas": "Does not work",
    "Seulement le gradient": "Only the gradient",
    "Le gradient et la matrice hessienne": "The gradient and the Hessian matrix",
    "Seulement la fonction de cout": "Only the cost function",
    "La transformee de Fourier": "The Fourier transform",
    "Converge plus lentement": "Converges more slowly",
    "Converge plus vite pres de l'optimum mais coute plus par iteration": "Converges faster near the optimum but costs more per iteration",
    "Ne necessite aucun calcul de derivee": "Requires no derivative computation",
    "Est exclusivement utilisee en cryptographie": "Is used exclusively in cryptography",
    "Le nombre d'iterations double a chaque pas": "The number of iterations doubles at each step",
    "Le nombre de chiffres exacts double a chaque iteration": "The number of correct digits doubles at each iteration",
    "L'erreur est proportionnelle au carre du temps": "The error is proportional to the square of time",
    "On ne converge pas": "It does not converge",
    "Quasi-Newton (BFGS)": "Quasi-Newton (BFGS)",
    "Multiplication matricielle": "Matrix multiplication",
    "Methode de la secante": "Secant method",
    "Algorithme genetique": "Genetic algorithm",
    "Peut diverger ou aller vers un point selle": "May diverge or move toward a saddle point",
    "Donne automatiquement le maximum": "Automatically gives the maximum",
    "Reste inchange": "Remains unchanged",
}

_PHRASES_EN = [
    ("Quel est le degre du polynome", "What is the degree of the polynomial"),
    ("Combien de coefficients faut-il pour definir", "How many coefficients are needed to define"),
    ("Combien faut-il de points pour construire", "How many points are needed to build"),
    ("Combien de zeros au plus peut avoir", "At most how many zeros can"),
    ("Que vaut", "What is"),
    ("a quels zeros", "has which zeros"),
    ("Quel est", "What is"),
    ("Quelle est", "What is"),
    ("Combien faut-il de", "How many"),
    ("Combien de", "How many"),
    ("a quelle propriete cle", "has which key property"),
    ("sert principalement a", "is mainly used to"),
    ("represente geometriquement", "represents geometrically"),
    ("L'avantage principal", "The main advantage"),
    ("Inconvenient principal", "Main drawback"),
    ("par rapport a", "compared with"),
    ("est de degre", "has degree"),
    ("de degre au plus", "of degree at most"),
    ("de degre", "of degree"),
    ("du polynome", "of the polynomial"),
    ("un polynome", "a polynomial"),
    ("le polynome", "the polynomial"),
    ("Le polynome", "The polynomial"),
    ("La formule", "The formula"),
    ("la formule", "the formula"),
    ("difference divisee", "divided difference"),
    ("differences divisees", "divided differences"),
    ("derivees exactes", "exact derivatives"),
    ("derivee", "derivative"),
    ("integrale definie", "definite integral"),
    ("integration numerique", "numerical integration"),
    ("somme de Riemann", "Riemann sum"),
    ("sommes de Riemann", "Riemann sums"),
    ("methode", "method"),
    ("methode de Newton", "Newton's method"),
    ("regle du trapeze", "trapezoidal rule"),
    ("regle de Simpson", "Simpson's rule"),
    ("quadrature de Gauss", "Gaussian quadrature"),
    ("descente de gradient", "gradient descent"),
    ("polynomes orthogonaux", "orthogonal polynomials"),
    ("moindres carres", "least squares"),
    ("approximation", "approximation"),
    ("interpolation", "interpolation"),
    ("spline cubique", "cubic spline"),
    ("splines cubiques", "cubic splines"),
    ("phenomene de Runge", "Runge phenomenon"),
    ("condition aux bords", "boundary condition"),
    ("continuite minimale", "minimum continuity"),
    ("points distincts", "distinct points"),
    ("points equidistants", "equally spaced points"),
    ("noeuds equidistants", "equally spaced nodes"),
    ("noeuds de Gauss-Legendre", "Gauss-Legendre nodes"),
    ("Les noeuds", "The nodes"),
    ("noeuds", "nodes"),
    ("fonction", "function"),
    ("courbe", "curve"),
    ("coefficient", "coefficient"),
    ("coefficients", "coefficients"),
    ("racines", "roots"),
    ("zeros", "zeros"),
    ("zero", "zero"),
    ("erreur", "error"),
    ("converge", "converges"),
    ("convergence", "convergence"),
    ("oscille fortement", "oscillates strongly"),
    ("aux extremites", "near the endpoints"),
    ("Bonne reponse", "Correct answer"),
    ("la bonne reponse", "the correct answer"),
    ("la vraie bonne reponse", "the true correct answer"),
    ("plus grande puissance", "highest power"),
    ("coefficient non nul", "non-zero coefficient"),
    ("valeurs propres", "eigenvalues"),
    ("produit scalaire", "inner product"),
    ("orthogonal", "orthogonal"),
    ("orthogonaux", "orthogonal"),
    ("famille orthogonale", "orthogonal family"),
    ("solution optimale", "optimal solution"),
    ("minimum global", "global minimum"),
    ("minimum local", "local minimum"),
    ("cas limite", "edge case"),
    ("condition initiale", "initial condition"),
    ("pas d'integration", "integration step"),
    ("l'intervalle", "the interval"),
    ("sur tout l'intervalle", "over the whole interval"),
    ("par morceaux", "piecewise"),
    ("un assemblage de", "an assembly of"),
    ("La table", "The table"),
    ("la table", "the table"),
    ("La difference", "The difference"),
    ("la difference", "the difference"),
    ("Les differences", "The differences"),
    ("les differences", "the differences"),
    ("ordre 0", "order 0"),
    ("ordre 1", "order 1"),
    ("ordre", "order"),
    ("sont-elles symetriques", "are symmetric"),
    ("Lien entre", "Link between"),
    ("donne", "give"),
    ("donnent", "give"),
    ("Comparaison", "Comparison"),
    ("Comparee", "Compared"),
    ("convergence quadratique", "quadratic convergence"),
    ("signifie", "means"),
    ("pour l'optimisation", "for optimization"),
    ("pour minimiser", "to minimize"),
    ("pour maximiser", "to maximize"),
    ("met a jour", "updates"),
    ("direction", "direction"),
    ("parametres", "parameters"),
    ("trop grand", "too large"),
    ("utilise", "uses"),
    ("utilisee", "used"),
    ("necessite", "requires"),
    ("necessite un nombre", "requires a number"),
    ("approche", "approximates"),
    ("approxime", "approximates"),
    ("cherche a minimiser", "seeks to minimize"),
    ("calcule numeriquement", "computes numerically"),
    ("s'appelle", "is called"),
    ("choisit comme", "chooses as"),
    ("on choisit", "we choose"),
    ("on peut utiliser", "one can use"),
    ("au sens de", "in the sense of"),
    ("en signe alterne", "with alternating sign"),
    ("atteint son extremum", "reaches its extremum"),
    ("Les", "The"),
    ("les", "the"),
    ("des", "of"),
    ("Des", "Of"),
    ("aux autres", "at the other"),
    ("partout", "everywhere"),
    ("ailleurs", "elsewhere"),
    ("egal a", "equal to"),
    ("vaut", "is equal to"),
    ("utilise", "uses"),
    ("calcule", "computes"),
    ("calculer", "compute"),
    ("evaluer", "evaluate"),
    ("evalue", "evaluated"),
    ("evaluee", "evaluated"),
    ("au debut", "at the beginning"),
    ("a la fin", "at the end"),
    ("au milieu", "at the midpoint"),
    ("la moyenne", "the average"),
    ("de chaque sous-intervalle", "of each subinterval"),
    ("sur l'intervalle", "on the interval"),
    ("ajouter un point", "adding a point"),
    ("ne refait pas tout le calcul", "does not recompute everything"),
    ("recalcul total", "full recomputation"),
    ("Ne fonctionne que", "Only works"),
    ("Fonctionne uniquement", "Only works"),
    ("Pas besoin", "No need"),
    ("plus efficace", "more efficient"),
    ("plus adapte", "more suitable"),
    ("on veut", "we want to"),
    ("on ajoute", "we add"),
    ("quand", "when"),
    ("avec", "with"),
    ("sans", "without"),
    ("pour", "to"),
    ("et", "and"),
    ("ou", "or"),
    ("mais", "but"),
    ("donc", "therefore"),
    ("si", "if"),
]


def _clean_spacing(text: str) -> str:
    text = re.sub(r"\s+([?.!,;:])", r"\1", text)
    text = re.sub(r"\s{2,}", " ", text)
    text = text.replace(" ?","?")
    text = text.replace(" ,", ",")
    return text.strip()


def translate_fr_to_en(text: str | None) -> str | None:
    if text is None:
        return None
    if text in _EXACT_EN:
        return _EXACT_EN[text]

    translated = text
    for source, target in sorted(_PHRASES_EN, key=lambda item: len(item[0]), reverse=True):
        if re.fullmatch(r"[A-Za-z']+", source) and len(source) <= 4:
            pattern = rf"\b{re.escape(source)}\b"
        else:
            pattern = re.escape(source)
        translated = re.sub(pattern, target, translated, flags=re.IGNORECASE)

    # Small grammar cleanup after phrase replacement.
    translated = re.sub(r"\bdu\b", "of the", translated, flags=re.IGNORECASE)
    translated = re.sub(r"\bde la\b", "of the", translated, flags=re.IGNORECASE)
    translated = re.sub(r"\bde l'", "of the ", translated, flags=re.IGNORECASE)
    translated = re.sub(r"\bd'un\b", "of a", translated, flags=re.IGNORECASE)
    translated = re.sub(r"\bd'une\b", "of a", translated, flags=re.IGNORECASE)
    translated = re.sub(r"\ble\b", "the", translated, flags=re.IGNORECASE)
    translated = re.sub(r"\bla\b", "the", translated, flags=re.IGNORECASE)
    translated = re.sub(r"\bl'\b", "the ", translated, flags=re.IGNORECASE)
    translated = re.sub(r"\bun\b", "a", translated, flags=re.IGNORECASE)
    translated = re.sub(r"\bune\b", "a", translated, flags=re.IGNORECASE)
    translated = re.sub(r"\bthe\s+the\b", "the", translated, flags=re.IGNORECASE)
    translated = re.sub(r"\ba\s+a\b", "a", translated, flags=re.IGNORECASE)
    translated = translated.replace("How many coefficients faut-il to define", "How many coefficients are needed to define")
    translated = translated.replace("How many points to build", "How many points are needed to build")
    translated = translated.replace("How many zeros at most can have", "At most how many zeros can")
    translated = translated.replace("What is the degree of the polynomial", "What is the degree of the polynomial")
    translated = translated.replace("The polynomial de base", "The basis polynomial")
    translated = translated.replace("a which key property", "which key property")
    translated = translated.replace("The divided difference d'ordre", "The divided difference of order")
    translated = translated.replace("d'ordre", "of order")
    translated = translated.replace("au plus", "at most")
    translated = translated.replace("degree at most", "degree at most")
    translated = translated.replace("the correct answer etait", "the correct answer was")
    translated = translated.replace("exact derivativeses", "exact derivatives")
    translated = translated.replace("equations differentielles", "differential equations")
    translated = translated.replace("racines", "roots")
    translated = translated.replace("matrice hessienne", "Hessian matrix")
    translated = translated.replace("hessienne", "Hessian")
    translated = translated.replace("cout", "cost")
    translated = translated.replace("transformee", "transform")
    translated = translated.replace("Fourier", "Fourier")
    translated = re.sub(r"\betait\b", "was", translated, flags=re.IGNORECASE)
    translated = re.sub(r"\best\b", "is", translated, flags=re.IGNORECASE)
    translated = re.sub(r"\bsont\b", "are", translated, flags=re.IGNORECASE)
    translated = re.sub(r"\bdit\b", "says", translated, flags=re.IGNORECASE)
    translated = translated.replace("Dans", "In")
    translated = translated.replace("Ici", "Here")
    translated = translated.replace("C'est", "This is")
    translated = translated.replace("c'est", "this is")
    translated = translated.replace("the degre", "the degree")
    translated = translated.replace("degre", "degree")
    translated = translated.replace("polynome", "polynomial")
    translated = translated.replace("reponse", "answer")
    translated = translated.replace("maitrise", "mastery")
    translated = translated.replace("avance", "advanced")
    translated = translated.replace("debut", "beginning")
    translated = translated.replace("debutant", "beginner")
    translated = translated.replace("inferieur", "lower")
    translated = translated.replace("superieur", "higher")
    return _clean_spacing(translated)


def localize_bank_question(question: dict[str, Any], language: str) -> dict[str, Any]:
    language = normalize_quiz_language(language)
    localized = deepcopy(question)
    if language != "en":
        localized["language"] = "fr"
        return localized

    if "question_en" in localized:
        localized["question"] = localized["question_en"]
    else:
        localized["question"] = translate_fr_to_en(localized.get("question", "")) or ""

    original_options = list(localized.get("options") or [])
    if "options_en" in localized:
        localized["options"] = localized["options_en"]
    else:
        localized["options"] = [translate_fr_to_en(option) or "" for option in original_options]

    original_answer = localized.get("correct_answer")
    if "correct_answer_en" in localized:
        localized["correct_answer"] = localized["correct_answer_en"]
    elif original_answer in original_options:
        localized["correct_answer"] = localized["options"][original_options.index(original_answer)]
    else:
        localized["correct_answer"] = translate_fr_to_en(original_answer) or original_answer

    if "explanation_en" in localized:
        localized["explanation"] = localized["explanation_en"]
    else:
        localized["explanation"] = translate_fr_to_en(localized.get("explanation", "")) or ""

    localized["language"] = "en"
    return localized
