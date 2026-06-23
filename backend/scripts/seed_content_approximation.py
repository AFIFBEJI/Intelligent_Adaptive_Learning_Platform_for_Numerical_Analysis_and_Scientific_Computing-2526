"""
Complement de seed_content.py : ajoute les contenus pedagogiques pour
les 5 concepts du module Approximation Polynomiale & Optimisation que
l'ancien script (focus ODEs) ne couvrait pas.

Concepts ajoutes (3 niveaux chacun = 15 noeuds Content) :
  - concept_least_squares
  - concept_orthogonal_polynomials
  - concept_minimax_approximation
  - concept_gradient_descent
  - concept_newton_optimization

Usage : python scripts/seed_content_approximation.py
"""
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.graph.neo4j_connection import neo4j_conn

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


CONTENTS = [
    # ─── concept_least_squares ───────────────────────────────
    {
        "concept_id": "concept_least_squares",
        "level": "simplified",
        "title": "Moindres carrés (intuition)",
        "body": (
            "## Idée centrale\n\n"
            "On a un nuage de points et on cherche **la droite (ou courbe polynomiale) qui passe au plus près** de tous les points.\n\n"
            "**Exemple** : tu as les notes des élèves d'une promo et leurs heures d'étude. Tu veux tracer la droite qui résume la tendance.\n\n"
            "## Comment ?\n\n"
            "Pour chaque point $(x_i, y_i)$, on calcule la distance verticale entre le point et la droite : c'est l'**erreur**.\n\n"
            "On choisit la droite qui **minimise la somme des carrés des erreurs**.\n\n"
            "$$ \\min \\sum_{i=1}^{n} (y_i - p(x_i))^2 $$\n\n"
            "## Pourquoi des carrés ?\n\n"
            "- Pour pénaliser les grosses erreurs plus que les petites.\n"
            "- Pour avoir une formule mathématique propre (les valeurs absolues sont moins pratiques)."
        ),
    },
    {
        "concept_id": "concept_least_squares",
        "level": "standard",
        "title": "Méthode des moindres carrés",
        "body": (
            "## Problème\n\n"
            "Étant donnés $n$ points $(x_i, y_i)$ et un polynôme $p(x) = a_0 + a_1 x + \\dots + a_d x^d$ de degré $d$,\n"
            "on cherche les coefficients $(a_0, \\dots, a_d)$ qui minimisent :\n\n"
            "$$ S(a) = \\sum_{i=1}^{n} (y_i - p(x_i))^2 $$\n\n"
            "## Équations normales\n\n"
            "On forme la matrice de Vandermonde $A \\in \\mathbb{R}^{n \\times (d+1)}$ avec $A_{ij} = x_i^j$.\n\n"
            "Le minimum de $\\|A a - y\\|^2$ vérifie :\n\n"
            "$$ A^T A \\, a = A^T y $$\n\n"
            "## Cas linéaire ($d = 1$)\n\n"
            "On obtient les formules classiques :\n\n"
            "$$ a_1 = \\frac{n \\sum x_i y_i - \\sum x_i \\sum y_i}{n \\sum x_i^2 - (\\sum x_i)^2}, \\quad a_0 = \\bar{y} - a_1 \\bar{x} $$"
        ),
    },
    {
        "concept_id": "concept_least_squares",
        "level": "rigorous",
        "title": "Moindres carrés : théorie",
        "body": (
            "## Théorème (existence et unicité)\n\n"
            "Soit $A \\in \\mathbb{R}^{n \\times m}$ avec $n \\ge m$ et $\\mathrm{rang}(A) = m$. Alors le problème\n\n"
            "$$ \\min_{a \\in \\mathbb{R}^m} \\|A a - y\\|_2^2 $$\n\n"
            "admet une **unique** solution donnée par les équations normales :\n\n"
            "$$ a^* = (A^T A)^{-1} A^T y $$\n\n"
            "## Décomposition QR (méthode numérique stable)\n\n"
            "On décompose $A = Q R$ avec $Q$ orthogonale et $R$ triangulaire supérieure. La solution est\n\n"
            "$$ R a = Q^T y $$\n\n"
            "résolue par substitution arrière en $O(m^2)$.\n\n"
            "## Conditionnement\n\n"
            "Le nombre de conditionnement de $A^T A$ est $\\kappa(A^T A) = \\kappa(A)^2$. Pour des données mal conditionnées,\n"
            "préférer **QR** ou **SVD** aux équations normales pour éviter l'amplification des erreurs."
        ),
    },

    # ─── concept_orthogonal_polynomials ──────────────────────
    {
        "concept_id": "concept_orthogonal_polynomials",
        "level": "simplified",
        "title": "Polynômes orthogonaux (intuition)",
        "body": (
            "## L'idée\n\n"
            "Deux polynômes $P$ et $Q$ sont **orthogonaux** sur $[a,b]$ si leur \"produit\" intégré vaut zéro :\n\n"
            "$$ \\int_a^b P(x) Q(x) w(x) dx = 0 $$\n\n"
            "où $w(x)$ est une fonction de poids.\n\n"
            "## Pourquoi c'est utile ?\n\n"
            "Comme une base orthogonale en algèbre linéaire (les vecteurs $\\vec{i}, \\vec{j}, \\vec{k}$), les polynômes orthogonaux\n"
            "permettent de **décomposer une fonction en somme de morceaux indépendants** :\n\n"
            "$$ f(x) \\approx c_0 P_0(x) + c_1 P_1(x) + \\dots + c_n P_n(x) $$\n\n"
            "## Exemples célèbres\n\n"
            "- **Legendre** : sur $[-1, 1]$ avec $w(x) = 1$\n"
            "- **Tchebychev** : sur $[-1, 1]$ avec $w(x) = 1/\\sqrt{1-x^2}$\n"
            "- **Hermite** : sur $\\mathbb{R}$ avec $w(x) = e^{-x^2}$"
        ),
    },
    {
        "concept_id": "concept_orthogonal_polynomials",
        "level": "standard",
        "title": "Familles classiques de polynômes orthogonaux",
        "body": (
            "## Définition formelle\n\n"
            "Une famille $\\{P_n\\}_{n \\ge 0}$ avec $\\deg P_n = n$ est **orthogonale** par rapport à un poids $w$ sur $[a,b]$ si :\n\n"
            "$$ \\langle P_i, P_j \\rangle = \\int_a^b P_i(x) P_j(x) w(x) dx = h_i \\delta_{ij} $$\n\n"
            "## Polynômes de Legendre $P_n$\n\n"
            "Sur $[-1, 1]$ avec $w \\equiv 1$. Récurrence à 3 termes :\n\n"
            "$$ (n+1) P_{n+1}(x) = (2n+1) x P_n(x) - n P_{n-1}(x) $$\n\n"
            "Les premiers : $P_0 = 1$, $P_1 = x$, $P_2 = \\frac{1}{2}(3x^2 - 1)$.\n\n"
            "## Polynômes de Tchebychev $T_n$\n\n"
            "Sur $[-1, 1]$ avec $w(x) = 1/\\sqrt{1-x^2}$. Définition simple :\n\n"
            "$$ T_n(\\cos \\theta) = \\cos(n \\theta) $$\n\n"
            "Propriété clé : minimisent l'erreur maximale $\\|f - p\\|_\\infty$ (théorème de Tchebychev).\n\n"
            "## Décomposition d'une fonction\n\n"
            "$$ f(x) = \\sum_{n=0}^{\\infty} c_n P_n(x), \\quad c_n = \\frac{\\langle f, P_n \\rangle}{\\langle P_n, P_n \\rangle} $$"
        ),
    },
    {
        "concept_id": "concept_orthogonal_polynomials",
        "level": "rigorous",
        "title": "Polynômes orthogonaux : théorie complète",
        "body": (
            "## Existence (Gram-Schmidt)\n\n"
            "Pour tout poids $w > 0$ intégrable sur $[a, b]$, l'orthogonalisation de Gram-Schmidt appliquée à $\\{1, x, x^2, \\dots\\}$ produit une famille orthogonale unique (à constante multiplicative près).\n\n"
            "## Théorème (zéros)\n\n"
            "Si $\\{P_n\\}$ est une famille de polynômes orthogonaux sur $[a, b]$ pour le poids $w$, alors $P_n$ admet exactement $n$ **zéros simples** dans $[a, b]$.\n\n"
            "*Application* : ces zéros sont les nœuds optimaux de la quadrature de Gauss.\n\n"
            "## Récurrence à 3 termes (théorème de Favard)\n\n"
            "Toute famille orthogonale $\\{P_n\\}$ avec $\\deg P_n = n$ vérifie :\n\n"
            "$$ P_{n+1}(x) = (\\alpha_n x + \\beta_n) P_n(x) + \\gamma_n P_{n-1}(x) $$\n\n"
            "où $(\\alpha_n, \\beta_n, \\gamma_n)$ se calculent à partir des moments $\\int x^k w(x) dx$.\n\n"
            "## Quadrature de Gauss-Legendre\n\n"
            "Si $x_1, \\dots, x_n$ sont les zéros de $P_n$ (Legendre), alors la formule de quadrature\n\n"
            "$$ \\int_{-1}^{1} f(x) dx \\approx \\sum_{i=1}^n w_i f(x_i) $$\n\n"
            "est exacte pour tous les polynômes de degré $\\le 2n - 1$."
        ),
    },

    # ─── concept_minimax_approximation ───────────────────────
    {
        "concept_id": "concept_minimax_approximation",
        "level": "simplified",
        "title": "Approximation minimax (intuition)",
        "body": (
            "## Le problème\n\n"
            "On a une fonction $f$ compliquée et on veut la remplacer par un polynôme $p$ simple.\n\n"
            "Mais comment mesurer la qualité de l'approximation ?\n\n"
            "## Deux options\n\n"
            "**Option 1 — Moindres carrés** : minimiser la somme des carrés des erreurs.\n"
            "→ marche bien en moyenne, mais peut avoir des **pics d'erreur** localisés.\n\n"
            "**Option 2 — Minimax (Tchebychev)** : minimiser **la pire erreur** (la plus grande sur tout l'intervalle).\n\n"
            "$$ \\min_{p} \\max_{x \\in [a,b]} |f(x) - p(x)| $$\n\n"
            "## Pourquoi minimax ?\n\n"
            "Quand tu **garantis une erreur maximale** (en aérospatial, finance, ingénierie critique), tu veux savoir le **pire cas**.\n\n"
            "Le polynôme minimax est la meilleure approximation au sens de la norme $L^\\infty$."
        ),
    },
    {
        "concept_id": "concept_minimax_approximation",
        "level": "standard",
        "title": "Approximation minimax (Tchebychev)",
        "body": (
            "## Problème de Tchebychev\n\n"
            "Trouver le polynôme $p^* \\in \\mathcal{P}_n$ qui minimise :\n\n"
            "$$ \\|f - p^*\\|_\\infty = \\sup_{x \\in [a,b]} |f(x) - p^*(x)| $$\n\n"
            "## Théorème d'équi-oscillation\n\n"
            "$p^*$ est l'unique polynôme minimax de degré $\\le n$ ssi l'erreur $e(x) = f(x) - p^*(x)$ atteint sa valeur extrême $\\pm \\|e\\|_\\infty$ en **au moins $n+2$ points** $x_0 < x_1 < \\dots < x_{n+1}$ avec **alternance de signe** :\n\n"
            "$$ e(x_i) = (-1)^i \\|e\\|_\\infty, \\quad i = 0, 1, \\dots, n+1 $$\n\n"
            "## Algorithme de Remez\n\n"
            "Pour calculer $p^*$ numériquement, on utilise l'algorithme itératif de **Remez** :\n\n"
            "1. Choisir $n+2$ points initiaux.\n"
            "2. Résoudre un système linéaire pour faire osciller l'erreur sur ces points.\n"
            "3. Trouver le nouveau maximum d'erreur, ajuster les points.\n"
            "4. Itérer jusqu'à convergence.\n\n"
            "## Approximation par Tchebychev (simple)\n\n"
            "Une approximation **proche du minimax** est obtenue par troncature de la série de Tchebychev de $f$. Souvent suffisant en pratique."
        ),
    },
    {
        "concept_id": "concept_minimax_approximation",
        "level": "rigorous",
        "title": "Théorie de l'approximation minimax",
        "body": (
            "## Théorème d'existence\n\n"
            "Pour toute fonction $f$ continue sur $[a, b]$ et tout entier $n \\ge 0$, il existe un unique polynôme $p^* \\in \\mathcal{P}_n$ tel que\n\n"
            "$$ \\|f - p^*\\|_\\infty = \\inf_{p \\in \\mathcal{P}_n} \\|f - p\\|_\\infty $$\n\n"
            "## Caractérisation (Tchebychev, 1854)\n\n"
            "$p^* \\in \\mathcal{P}_n$ est minimax ssi $\\exists\\, n+2$ points $\\{x_i\\}_{i=0}^{n+1}$ dans $[a,b]$ tels que\n\n"
            "$$ f(x_i) - p^*(x_i) = \\sigma (-1)^i E^*, \\quad \\sigma \\in \\{-1, +1\\} $$\n\n"
            "où $E^* = \\|f - p^*\\|_\\infty$.\n\n"
            "## Borne d'erreur (Jackson)\n\n"
            "Pour $f \\in C^k([a,b])$ avec $f^{(k)}$ continue par morceaux,\n\n"
            "$$ E_n(f) := \\inf_p \\|f - p\\|_\\infty \\le \\frac{C_k \\|f^{(k)}\\|_\\infty (b-a)^k}{n^k} $$\n\n"
            "## Lien avec les nœuds de Tchebychev\n\n"
            "Pour interpoler $f$ par un polynôme de degré $n$, choisir comme nœuds les zéros de $T_{n+1}$ (Tchebychev) donne une erreur d'interpolation **proche du minimax**, contrairement à des nœuds équidistants (phénomène de Runge).\n\n"
            "## Algorithme de Remez (convergence)\n\n"
            "L'algorithme de Remez converge **quadratiquement** sous des conditions techniques (point critique non dégénéré). En pratique, $\\sim 5\\text{-}10$ itérations suffisent pour la précision machine."
        ),
    },

    # ─── concept_gradient_descent ────────────────────────────
    {
        "concept_id": "concept_gradient_descent",
        "level": "simplified",
        "title": "Descente de gradient (intuition)",
        "body": (
            "## L'analogie\n\n"
            "Imagine que tu es dans la montagne dans le brouillard et que tu veux descendre dans la vallée.\n\n"
            "Tu ne vois pas loin, mais tu peux sentir la **pente sous tes pieds**.\n\n"
            "**Stratégie** : à chaque pas, tu vas dans la direction qui descend le plus.\n\n"
            "## En maths\n\n"
            "Le **gradient** $\\nabla f$ pointe vers la plus forte montée.\n\n"
            "Pour descendre, tu vas dans la direction **opposée** :\n\n"
            "$$ \\theta_{k+1} = \\theta_k - \\eta \\, \\nabla f(\\theta_k) $$\n\n"
            "où $\\eta$ (eta) est ton **pas** (taille du pas).\n\n"
            "## Le piège\n\n"
            "- Si $\\eta$ est trop petit → tu descends très lentement.\n"
            "- Si $\\eta$ est trop grand → tu sautes par-dessus la vallée.\n\n"
            "Trouver le bon $\\eta$ est le compromis classique en optimisation."
        ),
    },
    {
        "concept_id": "concept_gradient_descent",
        "level": "standard",
        "title": "Descente de gradient",
        "body": (
            "## Formulation\n\n"
            "Pour minimiser $f : \\mathbb{R}^n \\to \\mathbb{R}$ différentiable, on itère :\n\n"
            "$$ \\theta_{k+1} = \\theta_k - \\eta_k \\, \\nabla f(\\theta_k) $$\n\n"
            "avec $\\nabla f(\\theta) = \\left( \\frac{\\partial f}{\\partial \\theta_1}, \\dots, \\frac{\\partial f}{\\partial \\theta_n} \\right)$.\n\n"
            "## Choix du learning rate $\\eta$\n\n"
            "- **$\\eta$ constant** : simple, mais peu robuste.\n"
            "- **$\\eta$ décroissant** : $\\eta_k = \\eta_0 / (1 + k)$, classique en SGD.\n"
            "- **Line search** (Armijo) : choisir $\\eta$ qui satisfait $f(\\theta - \\eta \\nabla f) \\le f(\\theta) - c \\eta \\|\\nabla f\\|^2$.\n\n"
            "## Convergence\n\n"
            "Pour $f$ **convexe** et $\\nabla f$ $L$-lipschitzien, avec $\\eta = 1/L$ :\n\n"
            "$$ f(\\theta_k) - f(\\theta^*) \\le \\frac{\\|\\theta_0 - \\theta^*\\|^2}{2 \\eta k} = O(1/k) $$\n\n"
            "## Variantes\n\n"
            "- **SGD** : on calcule $\\nabla f$ sur un échantillon (mini-batch).\n"
            "- **Momentum** : $v_{k+1} = \\beta v_k + \\nabla f$, $\\theta_{k+1} = \\theta_k - \\eta v_{k+1}$.\n"
            "- **Adam** : adapte $\\eta$ par paramètre via les moments du gradient."
        ),
    },
    {
        "concept_id": "concept_gradient_descent",
        "level": "rigorous",
        "title": "Descente de gradient : analyse",
        "body": (
            "## Hypothèses standards\n\n"
            "- $f : \\mathbb{R}^n \\to \\mathbb{R}$ est $L$-smooth : $\\|\\nabla f(x) - \\nabla f(y)\\| \\le L \\|x - y\\|$.\n"
            "- $f$ convexe (parfois $\\mu$-fortement convexe).\n\n"
            "## Théorème (cas convexe lisse)\n\n"
            "Pour $\\eta \\le 1/L$, la descente de gradient produit une suite vérifiant :\n\n"
            "$$ f(\\theta_k) - f(\\theta^*) \\le \\frac{\\|\\theta_0 - \\theta^*\\|^2}{2 \\eta k} $$\n\n"
            "Donc $O(1/k)$ — sous-linéaire.\n\n"
            "## Théorème (cas $\\mu$-fortement convexe)\n\n"
            "$$ \\|\\theta_k - \\theta^*\\|^2 \\le \\left(1 - \\eta \\mu\\right)^k \\|\\theta_0 - \\theta^*\\|^2 $$\n\n"
            "Donc convergence **linéaire** (géométrique) avec taux $1 - \\eta \\mu$.\n\n"
            "## Borne inférieure (Nesterov)\n\n"
            "Pour les méthodes du premier ordre sur fonctions $L$-smooth et $\\mu$-fortement convexes,\n\n"
            "$$ f(\\theta_k) - f(\\theta^*) \\ge \\Omega\\left(\\left(\\frac{\\sqrt{\\kappa} - 1}{\\sqrt{\\kappa} + 1}\\right)^{2k}\\right), \\quad \\kappa = L/\\mu $$\n\n"
            "atteinte par la méthode du gradient accéléré de Nesterov.\n\n"
            "## Cas non-convexe\n\n"
            "On garantit seulement la convergence vers un **point critique** ($\\nabla f = 0$), pas vers le minimum global. Avec $\\eta < 2/L$ :\n\n"
            "$$ \\min_{k \\le K} \\|\\nabla f(\\theta_k)\\|^2 \\le \\frac{2 L (f(\\theta_0) - f^*)}{K} $$"
        ),
    },

    # ─── concept_newton_optimization ─────────────────────────
    {
        "concept_id": "concept_newton_optimization",
        "level": "simplified",
        "title": "Méthode de Newton pour l'optimisation (intuition)",
        "body": (
            "## L'idée\n\n"
            "La descente de gradient regarde **la pente** $\\nabla f$. Newton va plus loin : il regarde aussi la **courbure** (la dérivée seconde, ou hessienne $H$).\n\n"
            "## Comparaison\n\n"
            "**Descente de gradient** : \"je descends d'un pas constant dans la direction de la plus forte pente\".\n\n"
            "**Newton** : \"je modélise la fonction par une parabole locale et je saute directement au minimum de cette parabole\".\n\n"
            "## Formule\n\n"
            "$$ \\theta_{k+1} = \\theta_k - H(\\theta_k)^{-1} \\nabla f(\\theta_k) $$\n\n"
            "où $H$ est la matrice hessienne (dérivées secondes).\n\n"
            "## Avantage / Inconvénient\n\n"
            "- ✅ **Beaucoup plus rapide** près du minimum (convergence quadratique).\n"
            "- ❌ **Plus cher** par itération (calcul + inversion de $H$, $O(n^3)$ en dimension $n$)."
        ),
    },
    {
        "concept_id": "concept_newton_optimization",
        "level": "standard",
        "title": "Méthode de Newton pour l'optimisation",
        "body": (
            "## Principe\n\n"
            "Pour minimiser $f : \\mathbb{R}^n \\to \\mathbb{R}$ deux fois différentiable, on approche $f$ près de $\\theta_k$ par sa série de Taylor d'ordre 2 :\n\n"
            "$$ f(\\theta) \\approx f(\\theta_k) + \\nabla f(\\theta_k)^T (\\theta - \\theta_k) + \\frac{1}{2} (\\theta - \\theta_k)^T H_k (\\theta - \\theta_k) $$\n\n"
            "Le minimum de cette approximation quadratique est :\n\n"
            "$$ \\theta_{k+1} = \\theta_k - H_k^{-1} \\nabla f(\\theta_k) $$\n\n"
            "## Convergence\n\n"
            "**Quadratique** près d'un minimum local non dégénéré (matrice hessienne définie positive) :\n\n"
            "$$ \\|\\theta_{k+1} - \\theta^*\\| \\le C \\|\\theta_k - \\theta^*\\|^2 $$\n\n"
            "Cela double le nombre de chiffres exacts à chaque itération. Très rapide près de l'optimum.\n\n"
            "## Coût par itération\n\n"
            "- Calcul de $\\nabla f$ : $O(n)$\n"
            "- Calcul de $H$ : $O(n^2)$\n"
            "- Résolution de $H d = -\\nabla f$ : $O(n^3)$ (factorisation LU/Cholesky)\n\n"
            "Total : $O(n^3)$ par itération, vs $O(n)$ pour la descente de gradient.\n\n"
            "## Variantes pratiques\n\n"
            "- **Newton modifié** : régularise $H$ si non définie positive : $H \\to H + \\lambda I$.\n"
            "- **Quasi-Newton (BFGS, L-BFGS)** : approxime $H^{-1}$ sans la calculer, $O(n^2)$ par itération.\n"
            "- **Gauss-Newton** : pour les moindres carrés, approxime $H \\approx J^T J$ où $J$ est la jacobienne."
        ),
    },
    {
        "concept_id": "concept_newton_optimization",
        "level": "rigorous",
        "title": "Méthode de Newton : analyse",
        "body": (
            "## Convergence locale (théorème de Kantorovich)\n\n"
            "Soit $f \\in C^2$ et $\\theta^*$ tel que $\\nabla f(\\theta^*) = 0$ et $H(\\theta^*) \\succ 0$ (définie positive). Si $H$ est $L$-lipschitzienne au voisinage de $\\theta^*$ et si $\\theta_0$ est suffisamment proche de $\\theta^*$, alors la suite $\\{\\theta_k\\}$ converge vers $\\theta^*$ avec :\n\n"
            "$$ \\|\\theta_{k+1} - \\theta^*\\| \\le \\frac{L}{2 \\sigma_{\\min}(H(\\theta^*))} \\|\\theta_k - \\theta^*\\|^2 $$\n\n"
            "où $\\sigma_{\\min}$ est la plus petite valeur propre de $H$.\n\n"
            "## Globalisation par line search\n\n"
            "La convergence quadratique est **locale**. Pour la convergence globale, on combine Newton avec une **recherche linéaire** (Armijo, Wolfe) :\n\n"
            "$$ \\theta_{k+1} = \\theta_k - \\alpha_k H_k^{-1} \\nabla f(\\theta_k), \\quad \\alpha_k \\in (0, 1] $$\n\n"
            "## Régularisation (Levenberg-Marquardt)\n\n"
            "Si $H_k \\not\\succ 0$, on régularise :\n\n"
            "$$ \\theta_{k+1} = \\theta_k - (H_k + \\lambda_k I)^{-1} \\nabla f(\\theta_k) $$\n\n"
            "Pour $\\lambda \\to 0$ on retrouve Newton ; pour $\\lambda \\to \\infty$ on retrouve la descente de gradient.\n\n"
            "## Quasi-Newton (BFGS)\n\n"
            "On maintient une approximation $B_k \\approx H_k^{-1}$ mise à jour par :\n\n"
            "$$ B_{k+1} = (I - \\rho s y^T) B_k (I - \\rho y s^T) + \\rho s s^T $$\n\n"
            "où $s = \\theta_{k+1} - \\theta_k$, $y = \\nabla f_{k+1} - \\nabla f_k$, $\\rho = 1/(y^T s)$.\n\n"
            "Convergence super-linéaire. **L-BFGS** stocke seulement les $m$ dernières paires $(s, y)$ : mémoire $O(mn)$ au lieu de $O(n^2)$, idéal pour les grandes dimensions (deep learning)."
        ),
    },
]


def main() -> None:
    inserted = 0
    for c in CONTENTS:
        # Verifier que le concept existe
        rows = neo4j_conn.run_query(
            "MATCH (c:Concept {id: $cid}) RETURN c.id AS id",
            {"cid": c["concept_id"]},
        )
        if not rows:
            logger.warning("Concept %s introuvable, skip", c["concept_id"])
            continue

        # Le contenu francais est stocke dans title_fr / body_fr
        # sur le MEME noeud Content que la version anglaise (cle: id base sur
        # concept_id + level pour rester aligne avec seed_content.py).
        content_id = f"content_{c['concept_id'].replace('concept_', '')}_{c['level']}"

        neo4j_conn.run_write_query(
            """
            MATCH (c:Concept {id: $cid})
            MERGE (ct:Content {id: $content_id})
            ON CREATE SET
                ct.level = $level,
                ct.title_fr = $title,
                ct.body_fr = $body,
                ct.title = $title,
                ct.body = $body
            ON MATCH SET
                ct.level = $level,
                ct.title_fr = $title,
                ct.body_fr = $body
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
        logger.info("Inserted FR content for %s (%s)", c["concept_id"], c["level"])

    logger.info("Total FR contents inserted/updated : %d", inserted)


if __name__ == "__main__":
    main()
