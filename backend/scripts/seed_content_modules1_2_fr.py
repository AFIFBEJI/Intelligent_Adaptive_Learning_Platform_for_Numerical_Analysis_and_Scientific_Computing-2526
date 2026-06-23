"""
Contenu FR pour les Modules 1 (Interpolation) et 2 (Integration numerique).

Ecrit dans `title_fr` / `body_fr` sur les MEMES noeuds Content que la version
EN cree par seed_content.py. Cle alignee : id = "content_<concept_short>_<level>".

Concepts couverts (10 concepts x 3 niveaux = 30 noeuds Content) :
  Module 1 :
    - concept_polynomial_basics
    - concept_lagrange
    - concept_divided_differences
    - concept_newton_interpolation
    - concept_spline_interpolation
  Module 2 :
    - concept_riemann_sums
    - concept_definite_integrals
    - concept_trapezoidal
    - concept_simpson
    - concept_gaussian_quadrature

Usage : python scripts/seed_content_modules1_2_fr.py
"""
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.graph.neo4j_connection import neo4j_conn

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


CONTENTS = [
    # ============================================================
    # MODULE 1 : INTERPOLATION
    # ============================================================

    # --- Polynomial Basics ---
    {
        "concept_id": "concept_polynomial_basics",
        "level": "simplified",
        "title": "Les polynomes en simple",
        "body": """# Polynomes - Version simplifiee

Un **polynome** est une expression mathematique avec $x$ eleve a des puissances entieres.

**Exemple :** $P(x) = 3x^2 + 2x - 5$

- Le **degre** est la plus grande puissance de $x$. Ici le degre vaut **2**.
- Les **coefficients** sont les nombres devant $x$ : ici 3, 2 et -5.

**A retenir :** un polynome de degre $n$ a exactement $n+1$ coefficients et peut passer par $n+1$ points.
""",
    },
    {
        "concept_id": "concept_polynomial_basics",
        "level": "standard",
        "title": "Notions fondamentales sur les polynomes",
        "body": """# Notions fondamentales sur les polynomes

Un polynome de degre $n$ s'ecrit :

$$P(x) = a_n x^n + a_{n-1} x^{n-1} + \\dots + a_1 x + a_0$$

ou $a_n \\ne 0$.

## Operations
- **Addition** : on additionne les coefficients de meme degre.
- **Multiplication** : pour $P$ de degre $n$ et $Q$ de degre $m$, $PQ$ est de degre $n + m$.
- **Composition** : $(P \\circ Q)(x) = P(Q(x))$ a pour degre $n \\cdot m$.

## Theoreme fondamental de l'algebre
Tout polynome de degre $n \\ge 1$ admet exactement $n$ racines dans $\\mathbb{C}$ (avec multiplicite).
""",
    },
    {
        "concept_id": "concept_polynomial_basics",
        "level": "rigorous",
        "title": "Theorie du polynome d'interpolation",
        "body": """# Theorie du polynome d'interpolation

## Theoreme d'unicite
Etant donnes $n+1$ points distincts $(x_0, y_0), \\dots, (x_n, y_n)$ avec $x_i \\ne x_j$ pour $i \\ne j$, il existe un **unique** polynome $P$ de degre $\\le n$ tel que $P(x_i) = y_i$ pour tout $i = 0, \\dots, n$.

## Demonstration (esquisse)
On considere l'application lineaire $T : \\mathbb{P}_n \\to \\mathbb{R}^{n+1}$ qui a $P$ associe $(P(x_0), \\dots, P(x_n))$. Sa matrice dans la base $\\{1, x, \\dots, x^n\\}$ est la matrice de Vandermonde :

$$V = \\begin{pmatrix} 1 & x_0 & x_0^2 & \\cdots & x_0^n \\\\ 1 & x_1 & x_1^2 & \\cdots & x_1^n \\\\ \\vdots & & & & \\vdots \\\\ 1 & x_n & x_n^2 & \\cdots & x_n^n \\end{pmatrix}$$

Le determinant de Vandermonde vaut $\\prod_{i < j} (x_j - x_i) \\ne 0$, donc $T$ est bijective.

## Borne d'erreur
Si $f \\in C^{n+1}([a, b])$ et $P$ interpole $f$ aux noeuds $x_0, \\dots, x_n \\in [a, b]$, alors pour tout $x \\in [a, b]$ il existe $\\xi \\in (a, b)$ tel que :

$$f(x) - P(x) = \\frac{f^{(n+1)}(\\xi)}{(n+1)!} \\prod_{i=0}^{n} (x - x_i)$$
""",
    },

    # --- Lagrange ---
    {
        "concept_id": "concept_lagrange",
        "level": "simplified",
        "title": "Lagrange en simple",
        "body": """# Interpolation de Lagrange - Version simplifiee

**But** : trouver une courbe lisse qui passe par tous les points donnes.

**Idee** : pour chaque point $(x_i, y_i)$, on construit un mini-polynome $L_i(x)$ qui :
- vaut **1** en $x_i$
- vaut **0** aux autres $x_j$

**Le polynome final** : $P(x) = y_0 L_0(x) + y_1 L_1(x) + \\dots + y_n L_n(x)$.

C'est comme une **moyenne ponderee** ou les poids dependent de l'endroit ou on regarde.
""",
    },
    {
        "concept_id": "concept_lagrange",
        "level": "standard",
        "title": "Methode d'interpolation de Lagrange",
        "body": """# Methode de Lagrange

## Polynomes de base
Pour $n+1$ points $(x_0, y_0), \\dots, (x_n, y_n)$, on definit :

$$L_i(x) = \\prod_{j=0,\\, j \\ne i}^{n} \\frac{x - x_j}{x_i - x_j}$$

**Propriete cle** : $L_i(x_j) = \\delta_{ij}$ (1 si $i = j$, 0 sinon).

## Polynome interpolateur
$$P(x) = \\sum_{i=0}^{n} y_i \\, L_i(x)$$

## Exemple (3 points)
Pour $(0, 1), (1, 3), (2, 2)$ :

$$L_0(x) = \\frac{(x-1)(x-2)}{(0-1)(0-2)} = \\frac{(x-1)(x-2)}{2}$$

$$L_1(x) = \\frac{(x-0)(x-2)}{(1-0)(1-2)} = -x(x-2)$$

$$L_2(x) = \\frac{(x-0)(x-1)}{(2-0)(2-1)} = \\frac{x(x-1)}{2}$$

D'ou $P(x) = 1 \\cdot L_0(x) + 3 \\cdot L_1(x) + 2 \\cdot L_2(x)$.
""",
    },
    {
        "concept_id": "concept_lagrange",
        "level": "rigorous",
        "title": "Analyse de l'interpolation de Lagrange",
        "body": """# Analyse de l'interpolation de Lagrange

## Erreur d'interpolation
Pour $f \\in C^{n+1}([a, b])$ interpolee par $P_n$ aux noeuds $x_0, \\dots, x_n \\in [a, b]$ :

$$f(x) - P_n(x) = \\frac{f^{(n+1)}(\\xi(x))}{(n+1)!} \\, w_n(x), \\quad w_n(x) = \\prod_{i=0}^{n} (x - x_i)$$

## Phenomene de Runge
Pour des noeuds equidistants, $\\|w_n\\|_\\infty$ explose pour les fonctions a forte variation. **Solution** : utiliser les **noeuds de Tchebychev** :

$$x_i = \\frac{a+b}{2} + \\frac{b-a}{2} \\cos\\!\\left( \\frac{(2i+1)\\pi}{2(n+1)} \\right)$$

qui minimisent $\\|w_n\\|_\\infty$.

## Stabilite numerique
La forme de Lagrange est **mal conditionnee** pour de grands $n$ : ajouter un point recalcule TOUT. La forme de Newton est plus adaptee aux mises a jour incrementales.

## Constante de Lebesgue
$\\Lambda_n = \\max_{x \\in [a,b]} \\sum_{i=0}^{n} |L_i(x)|$ mesure la stabilite ; pour des noeuds de Tchebychev, $\\Lambda_n \\sim \\log n$ ; pour des noeuds equidistants, croissance exponentielle.
""",
    },

    # --- Divided Differences ---
    {
        "concept_id": "concept_divided_differences",
        "level": "simplified",
        "title": "Differences divisees en simple",
        "body": """# Differences divisees - Version simplifiee

**But** : calculer rapidement les coefficients d'un polynome qui passe par des points donnes.

**Difference divisee d'ordre 1** : pente entre deux points
$$f[x_0, x_1] = \\frac{f(x_1) - f(x_0)}{x_1 - x_0}$$

**Difference divisee d'ordre 2** : derivee de la pente
$$f[x_0, x_1, x_2] = \\frac{f[x_1, x_2] - f[x_0, x_1]}{x_2 - x_0}$$

On construit une **table triangulaire** : on commence par les valeurs $f(x_i)$, puis on calcule les differences successives.

**Avantage majeur** : si on ajoute un nouveau point, on rajoute juste une ligne (pas de recalcul total).
""",
    },
    {
        "concept_id": "concept_divided_differences",
        "level": "standard",
        "title": "Methode des differences divisees",
        "body": """# Differences divisees

## Definition recursive
- Ordre 0 : $f[x_i] = f(x_i)$.
- Ordre $k$ :
$$f[x_0, x_1, \\dots, x_k] = \\frac{f[x_1, \\dots, x_k] - f[x_0, \\dots, x_{k-1}]}{x_k - x_0}$$

## Table de Newton
On organise les calculs en triangle :

| $x_0$ | $f(x_0)$ |             |               |
|-------|----------|-------------|---------------|
| $x_1$ | $f(x_1)$ | $f[x_0,x_1]$ |              |
| $x_2$ | $f(x_2)$ | $f[x_1,x_2]$ | $f[x_0,x_1,x_2]$ |

## Proprietes
- **Symetrie** : $f[x_0, \\dots, x_n]$ est invariante par permutation des $x_i$.
- **Lien avec les derivees** : si $f \\in C^n$, alors $f[x_0, \\dots, x_n] = \\frac{f^{(n)}(\\xi)}{n!}$ pour un certain $\\xi \\in [\\min x_i, \\max x_i]$.
""",
    },
    {
        "concept_id": "concept_divided_differences",
        "level": "rigorous",
        "title": "Theorie des differences divisees",
        "body": """# Theorie des differences divisees

## Formule de Genocchi-Hermite
Pour $f \\in C^n([a, b])$ et $x_0, \\dots, x_n \\in [a, b]$ :

$$f[x_0, \\dots, x_n] = \\int_0^1 \\int_0^{t_1} \\cdots \\int_0^{t_{n-1}} f^{(n)}(x_0 + t_1(x_1-x_0) + \\dots) \\, dt_n \\dots dt_1$$

## Lien avec la base de Newton
Le polynome interpolateur en forme de Newton est :

$$P_n(x) = f[x_0] + \\sum_{k=1}^{n} f[x_0, \\dots, x_k] \\prod_{j=0}^{k-1} (x - x_j)$$

## Propriete fondamentale
Si $\\{f_i\\} = \\{f(x_i)\\}$ sont les valeurs d'un polynome $f$ de degre $\\le n$, alors $f[x_0, \\dots, x_n] = $ coefficient dominant ; et $f[x_0, \\dots, x_{n+1}] = 0$.

## Stabilite
La formulation par differences divisees est **plus stable** numeriquement que les equations normales pour la base monomiale, surtout pour des grilles non equidistantes.
""",
    },

    # --- Newton Interpolation ---
    {
        "concept_id": "concept_newton_interpolation",
        "level": "simplified",
        "title": "Interpolation de Newton en simple",
        "body": """# Interpolation de Newton - Version simplifiee

**Idee** : on construit le polynome **morceau par morceau** au lieu d'un coup.

$$P(x) = c_0 + c_1(x - x_0) + c_2(x - x_0)(x - x_1) + \\dots$$

Les coefficients $c_k$ sont les **differences divisees** $f[x_0, \\dots, x_k]$.

**Avantage** : si on ajoute un point, on calcule juste un nouveau coefficient — les anciens restent inchanges.
""",
    },
    {
        "concept_id": "concept_newton_interpolation",
        "level": "standard",
        "title": "Forme de Newton du polynome interpolateur",
        "body": """# Forme de Newton

## Formule
$$P_n(x) = f[x_0] + f[x_0, x_1](x - x_0) + f[x_0, x_1, x_2](x - x_0)(x - x_1) + \\dots$$

soit, plus compactement :

$$P_n(x) = \\sum_{k=0}^{n} f[x_0, \\dots, x_k] \\, \\omega_k(x), \\quad \\omega_k(x) = \\prod_{j=0}^{k-1} (x - x_j)$$

## Schema d'evaluation (Horner)
Pour evaluer $P_n(x)$, on remonte de bas en haut :

```
v <- f[x_0, ..., x_n]
for k = n-1 downto 0:
    v <- v * (x - x_k) + f[x_0, ..., x_k]
```

Cout : $O(n)$ multiplications.

## Mise a jour incrementale
Si on ajoute un point $(x_{n+1}, y_{n+1})$ :
$$P_{n+1}(x) = P_n(x) + f[x_0, \\dots, x_{n+1}] \\, \\omega_{n+1}(x)$$

Pas de recalcul des coefficients precedents.
""",
    },
    {
        "concept_id": "concept_newton_interpolation",
        "level": "rigorous",
        "title": "Analyse de la forme de Newton",
        "body": """# Analyse de la forme de Newton

## Equivalence avec Lagrange
Lagrange et Newton produisent le **meme polynome interpolateur** (theoreme d'unicite). Seules les bases different : la base de Newton $\\{\\omega_k\\}$ est triangulaire dans les $(x_i)$.

## Erreur d'interpolation incrementale
Si $P_n$ interpole aux noeuds $x_0, \\dots, x_n$, l'erreur s'ecrit :

$$f(x) - P_n(x) = f[x_0, \\dots, x_n, x] \\cdot \\omega_{n+1}(x)$$

ce qui generalise la formule classique de Cauchy.

## Conditionnement
Le conditionnement de la base de Newton depend de la **distance maximale** entre noeuds successifs. Sur des noeuds de Tchebychev, le conditionnement est $O(n^2)$ ; sur des noeuds equidistants, il est exponentiel en $n$.

## Remarque pratique
Pour de grands $n$ et des donnees bruitees, la forme **barycentrique** (Berrut-Trefethen) est preferee : evaluation $O(n)$ stable, sensible aux poids et non aux coefficients.
""",
    },

    # --- Spline Interpolation ---
    {
        "concept_id": "concept_spline_interpolation",
        "level": "simplified",
        "title": "Splines en simple",
        "body": """# Splines - Version simplifiee

**Probleme** : un polynome de tres haut degre est instable (oscille beaucoup, phenomene de Runge).

**Solution** : on coupe l'intervalle en petits morceaux et on met un **petit polynome simple sur chaque morceau**.

Pour les **splines cubiques**, chaque morceau est un polynome de degre 3, et on s'assure que :
- les morceaux se rejoignent bien (continuite),
- les pentes coincident aux jonctions (derivee continue),
- la courbure aussi (derivee seconde continue).

Resultat : une courbe **lisse, naturelle, sans oscillations**.
""",
    },
    {
        "concept_id": "concept_spline_interpolation",
        "level": "standard",
        "title": "Interpolation par splines cubiques",
        "body": """# Splines cubiques

## Definition
Sur les noeuds $x_0 < x_1 < \\dots < x_n$, une **spline cubique** $S$ verifie :
- $S$ est polynomiale de degre $\\le 3$ sur chaque $[x_i, x_{i+1}]$.
- $S(x_i) = y_i$ pour $i = 0, \\dots, n$.
- $S \\in C^2([x_0, x_n])$ : continuite de $S$, $S'$ et $S''$.

## Conditions aux bords
Le systeme a $4n$ inconnues et $4n - 2$ equations ; il faut deux conditions supplementaires :
- **Naturelle** : $S''(x_0) = S''(x_n) = 0$.
- **Serree** : $S'(x_0)$ et $S'(x_n)$ donnees.
- **Periodique** : $S(x_0) = S(x_n)$ et derivees egales.

## Resolution
Le systeme se reduit a un systeme **tridiagonal** sur les $S''(x_i)$ : resolution en $O(n)$ par l'algorithme de Thomas.
""",
    },
    {
        "concept_id": "concept_spline_interpolation",
        "level": "rigorous",
        "title": "Theorie des splines cubiques",
        "body": """# Theorie des splines cubiques

## Theoreme (proprite extremale)
La spline cubique **naturelle** interpolant $(x_i, y_i)$ minimise la fonctionnelle de courbure :

$$J(g) = \\int_{x_0}^{x_n} (g''(x))^2 dx$$

parmi toutes les fonctions $g \\in C^2$ verifiant $g(x_i) = y_i$.

## Convergence
Pour $f \\in C^4([a, b])$ et $h = \\max(x_{i+1} - x_i)$, la spline cubique satisfait :

$$\\|f - S\\|_\\infty \\le C \\, h^4 \\, \\|f^{(4)}\\|_\\infty$$

## B-splines
La base **B-spline** est plus stable que la base monomiale : support local (chaque B-spline est non nulle sur 4 intervalles successifs), partition de l'unite, recurrence de Cox-de Boor.

## Application
Les splines sont la base des courbes de Bezier (CAO), des polices vectorielles (TrueType) et de l'animation 3D.
""",
    },

    # ============================================================
    # MODULE 2 : INTEGRATION NUMERIQUE
    # ============================================================

    # --- Riemann Sums ---
    {
        "concept_id": "concept_riemann_sums",
        "level": "simplified",
        "title": "Sommes de Riemann en simple",
        "body": """# Sommes de Riemann - Version simplifiee

**But** : calculer une integrale $\\int_a^b f(x) dx$ approximativement.

**Idee** : on decoupe $[a, b]$ en $n$ petits intervalles, on dessine des rectangles de hauteur $f(x_i)$ et on somme leurs aires.

$$S_n = \\sum_{i=0}^{n-1} f(x_i) \\, \\Delta x, \\quad \\Delta x = \\frac{b-a}{n}$$

Plus $n$ est grand, plus l'approximation est precise. Quand $n \\to \\infty$, $S_n \\to \\int_a^b f(x) dx$.

**Variantes** : rectangle a gauche, a droite, ou au milieu (le plus precis).
""",
    },
    {
        "concept_id": "concept_riemann_sums",
        "level": "standard",
        "title": "Sommes de Riemann",
        "body": """# Sommes de Riemann

## Trois variantes
Pour $h = (b - a)/n$ et $x_i = a + ih$ :

- **Rectangles a gauche** : $R_g = h \\sum_{i=0}^{n-1} f(x_i)$.
- **Rectangles a droite** : $R_d = h \\sum_{i=1}^{n} f(x_i)$.
- **Point milieu** : $R_m = h \\sum_{i=0}^{n-1} f\\!\\left(x_i + h/2\\right)$.

## Erreur
Pour $f \\in C^1$ : $|R_g - I| = O(h)$ et $|R_d - I| = O(h)$.
Pour $f \\in C^2$ : $|R_m - I| = O(h^2)$ — le **point milieu est deux fois plus precis** que gauche/droite.

## Exemple
$\\int_0^1 x^2 dx = 1/3 \\approx 0.333$ avec $n = 4$ et milieu :

$$R_m = 0.25 (0.125^2 + 0.375^2 + 0.625^2 + 0.875^2) = 0.328$$
""",
    },
    {
        "concept_id": "concept_riemann_sums",
        "level": "rigorous",
        "title": "Analyse des sommes de Riemann",
        "body": """# Analyse des sommes de Riemann

## Convergence
Pour $f$ continue sur $[a, b]$, et toute partition de pas $\\to 0$, $S_n \\to \\int_a^b f(x) dx$. C'est la definition meme de l'integrale de Riemann.

## Borne d'erreur (rectangles a gauche)
Pour $f \\in C^1([a, b])$ :

$$|R_g - I| \\le \\frac{(b-a)^2}{2n} \\|f'\\|_\\infty$$

## Borne d'erreur (point milieu)
Pour $f \\in C^2([a, b])$ :

$$|R_m - I| \\le \\frac{(b-a)^3}{24 n^2} \\|f''\\|_\\infty$$

## Limite philosophique
Les sommes de Riemann sont la **definition** mais des methodes plus efficaces (trapezes $O(h^2)$, Simpson $O(h^4)$, Gauss $O(h^{2n})$) sont preferees en pratique pour des $n$ donnes.
""",
    },

    # --- Definite Integrals ---
    {
        "concept_id": "concept_definite_integrals",
        "level": "simplified",
        "title": "Integrales definies en simple",
        "body": """# Integrales definies - Version simplifiee

L'**integrale definie** $\\int_a^b f(x) dx$ represente l'**aire signee** sous la courbe de $f$ entre $x = a$ et $x = b$.

- Si $f > 0$ : aire positive (au-dessus de l'axe).
- Si $f < 0$ : aire negative (en dessous).

**Exemple** : $\\int_0^1 x \\, dx = 1/2$ : c'est l'aire du triangle de hauteur 1 et de base 1.

**Theoreme fondamental** : si $F'(x) = f(x)$, alors $\\int_a^b f(x) dx = F(b) - F(a)$.
""",
    },
    {
        "concept_id": "concept_definite_integrals",
        "level": "standard",
        "title": "Integrales definies : fondations",
        "body": """# Integrales definies

## Definition (Riemann)
Pour $f$ bornee sur $[a, b]$, on definit :

$$\\int_a^b f(x) dx = \\lim_{|P| \\to 0} \\sum_{i=0}^{n-1} f(\\xi_i) (x_{i+1} - x_i)$$

ou $P = \\{x_0 = a < x_1 < \\dots < x_n = b\\}$ et $\\xi_i \\in [x_i, x_{i+1}]$.

## Theoreme fondamental du calcul
Si $f$ est continue sur $[a, b]$ et $F$ est une primitive de $f$, alors :

$$\\int_a^b f(x) dx = F(b) - F(a)$$

## Proprietes
- **Linearite** : $\\int (\\alpha f + \\beta g) = \\alpha \\int f + \\beta \\int g$.
- **Chasles** : $\\int_a^c f = \\int_a^b f + \\int_b^c f$.
- **Positivite** : $f \\ge 0 \\Rightarrow \\int_a^b f \\ge 0$.
""",
    },
    {
        "concept_id": "concept_definite_integrals",
        "level": "rigorous",
        "title": "Theorie de l'integration",
        "body": """# Theorie de l'integration

## Sommes de Darboux
Soit $P = \\{x_0, \\dots, x_n\\}$ une partition de $[a, b]$, $m_i = \\inf_{[x_{i-1}, x_i]} f$, $M_i = \\sup f$.

$$L(f, P) = \\sum_{i=1}^n m_i (x_i - x_{i-1}), \\quad U(f, P) = \\sum_{i=1}^n M_i (x_i - x_{i-1})$$

$f$ est **Riemann-integrable** ssi $\\sup_P L(f, P) = \\inf_P U(f, P)$.

## Theoreme (Lebesgue)
$f$ bornee est Riemann-integrable ssi l'ensemble de ses points de discontinuite est de mesure nulle.

## Generalisations
- **Integrale de Lebesgue** : etend la classe des fonctions integrables.
- **Integrales impropres** : intervalles non bornes ou fonctions non bornees, traitees par limite.
- **Integrales de Stieltjes** : par rapport a une mesure.
""",
    },

    # --- Trapezoidal ---
    {
        "concept_id": "concept_trapezoidal",
        "level": "simplified",
        "title": "Methode des trapezes en simple",
        "body": """# Methode des trapezes - Version simplifiee

**Idee** : au lieu de rectangles, on utilise des **trapezes** pour approximer l'aire sous la courbe.

Aire d'un trapeze : moyenne des hauteurs $\\times$ largeur.

$$\\int_a^b f(x) dx \\approx \\frac{h}{2} \\left[ f(x_0) + 2 f(x_1) + 2 f(x_2) + \\dots + 2 f(x_{n-1}) + f(x_n) \\right]$$

avec $h = (b-a)/n$.

**Pourquoi mieux que les rectangles ?** Les trapezes suivent la pente locale de $f$, donc l'approximation est plus precise pour la meme valeur de $n$.
""",
    },
    {
        "concept_id": "concept_trapezoidal",
        "level": "standard",
        "title": "Methode des trapezes",
        "body": """# Methode des trapezes

## Formule simple
Pour $n+1$ noeuds equidistants $x_i = a + ih$ avec $h = (b-a)/n$ :

$$T_n = \\frac{h}{2} \\left[ f(x_0) + 2 \\sum_{i=1}^{n-1} f(x_i) + f(x_n) \\right]$$

## Erreur
Pour $f \\in C^2([a, b])$ :

$$T_n - I = -\\frac{(b-a)^3}{12 n^2} f''(\\eta), \\quad \\eta \\in (a, b)$$

donc l'erreur est $O(h^2)$.

## Exactitude
La methode des trapezes est **exacte** pour les polynomes de degre $\\le 1$ (les segments).

## Remarque
Pour des fonctions periodiques avec une periode integrale entiere, la methode des trapezes est **exponentiellement convergente** (super-precision !).
""",
    },
    {
        "concept_id": "concept_trapezoidal",
        "level": "rigorous",
        "title": "Analyse de la methode des trapezes",
        "body": """# Analyse de la methode des trapezes

## Formule d'Euler-Maclaurin
$$\\sum_{i=0}^{n} f(x_i) = \\frac{1}{h} \\int_a^b f \\, dx + \\frac{f(a) + f(b)}{2} + \\sum_{k=1}^{p} \\frac{B_{2k}}{(2k)!} \\, h^{2k-1} (f^{(2k-1)}(b) - f^{(2k-1)}(a)) + R_p$$

ou $B_{2k}$ sont les nombres de Bernoulli. Cela revele pourquoi le **schema de Romberg** (acceleration de convergence par extrapolation) fonctionne.

## Romberg
On note $T_n^{(0)} = T_n$ (trapeze sur $n$ sous-intervalles). On extrapole :

$$T_n^{(k)} = T_n^{(k-1)} + \\frac{T_n^{(k-1)} - T_{n/2}^{(k-1)}}{4^k - 1}$$

Apres $k$ etapes, l'erreur passe de $O(h^2)$ a $O(h^{2k+2})$.

## Choix des noeuds
Sur des **noeuds non uniformes** (bord raffine pour les singularites), la methode des trapezes peut etre transformee en quadrature adaptative.
""",
    },

    # --- Simpson ---
    {
        "concept_id": "concept_simpson",
        "level": "simplified",
        "title": "Methode de Simpson en simple",
        "body": """# Methode de Simpson - Version simplifiee

**Idee** : au lieu de droites (trapezes), on utilise des **paraboles** pour approximer la courbe.

Sur trois points $(x_0, x_1, x_2)$ avec $x_1$ au milieu, on calcule l'aire sous la parabole passant par ces points :

$$\\int_{x_0}^{x_2} f(x) dx \\approx \\frac{h}{3} \\left[ f(x_0) + 4 f(x_1) + f(x_2) \\right]$$

C'est **beaucoup plus precis** que les trapezes : pour le meme $n$, l'erreur est en $O(h^4)$ au lieu de $O(h^2)$.

**Contrainte** : $n$ doit etre **pair** (on travaille par paires d'intervalles).
""",
    },
    {
        "concept_id": "concept_simpson",
        "level": "standard",
        "title": "Methode de Simpson 1/3",
        "body": """# Simpson 1/3

## Formule composite
Pour $n+1$ noeuds equidistants avec $n$ pair :

$$S_n = \\frac{h}{3} \\left[ f(x_0) + 4 \\sum_{i=1,3,5,\\dots}^{n-1} f(x_i) + 2 \\sum_{i=2,4,\\dots}^{n-2} f(x_i) + f(x_n) \\right]$$

## Origine
Sur trois points consecutifs, on integre la parabole de Lagrange passant par eux :

$$\\int_{x_{i}}^{x_{i+2}} P_2(x) dx = \\frac{h}{3} (f(x_i) + 4 f(x_{i+1}) + f(x_{i+2}))$$

## Erreur
Pour $f \\in C^4([a, b])$ :

$$S_n - I = -\\frac{(b-a)^5}{180 n^4} f^{(4)}(\\eta)$$

donc l'erreur est $O(h^4)$.

## Variante 3/8
Pour $n$ multiple de 3, on peut utiliser **Simpson 3/8** qui regroupe les noeuds par paquets de 4 :

$$\\int_{x_i}^{x_{i+3}} f \\approx \\frac{3h}{8} (f_i + 3 f_{i+1} + 3 f_{i+2} + f_{i+3})$$
""",
    },
    {
        "concept_id": "concept_simpson",
        "level": "rigorous",
        "title": "Analyse de la methode de Simpson",
        "body": """# Analyse de Simpson

## Exactitude
Simpson est **exacte** pour les polynomes de degre $\\le 3$ (et pas seulement de degre 2 comme on pourrait le croire) : c'est une consequence de la symetrie sur l'intervalle $[x_0, x_2]$.

## Theoreme d'erreur
Pour $f \\in C^4([a, b])$ :

$$|S_n - I| \\le \\frac{(b-a)}{180} \\, h^4 \\, \\|f^{(4)}\\|_\\infty$$

## Quadrature adaptative
On evalue $S_n$ sur l'intervalle complet, puis $S_n$ sur les deux moities. Si $|S_{\\text{moities}} - S_{\\text{complet}}| < \\epsilon$, on accepte ; sinon on recurse.

## Comparaison Simpson vs Gauss
| Methode | Precision sur polynomes degre <= | Erreur |
|---------|------------------------------------|--------|
| Trapezes | 1 | $O(h^2)$ |
| Simpson | 3 | $O(h^4)$ |
| Gauss-Legendre $n$ noeuds | $2n - 1$ | $O(h^{2n})$ |

Gauss bat Simpson en regle generale, sauf si $f$ est periodique.
""",
    },

    # --- Gaussian Quadrature ---
    {
        "concept_id": "concept_gaussian_quadrature",
        "level": "simplified",
        "title": "Quadrature de Gauss en simple",
        "body": """# Quadrature de Gauss - Version simplifiee

**Idee** : Simpson met les noeuds aux endroits **fixes** (gauche, milieu, droite). Mais on peut faire mieux !

**Gauss** : on choisit les **endroits optimaux** (et les poids optimaux) pour que la formule soit exacte sur des polynomes de tres haut degre.

Avec $n$ noeuds bien choisis, la formule est exacte pour tous les polynomes de degre $\\le 2n - 1$ — soit deux fois mieux que Simpson !

**Inconvenient** : les noeuds optimaux sont les zeros des polynomes de Legendre — pas tres intuitifs, mais tabules dans tous les codes numeriques.
""",
    },
    {
        "concept_id": "concept_gaussian_quadrature",
        "level": "standard",
        "title": "Quadrature de Gauss-Legendre",
        "body": """# Gauss-Legendre

## Principe
On cherche $n$ noeuds $x_i \\in [-1, 1]$ et $n$ poids $w_i$ tels que :

$$\\int_{-1}^{1} f(x) dx \\approx \\sum_{i=1}^{n} w_i f(x_i)$$

soit exacte pour tout polynome de degre $\\le 2n - 1$.

## Theoreme
Les noeuds optimaux $x_i$ sont les **racines du polynome de Legendre $P_n$**, et les poids sont :

$$w_i = \\frac{2}{(1 - x_i^2) (P_n'(x_i))^2}$$

## Tableau ($n$ petits)

| n | noeuds | poids |
|---|--------|-------|
| 1 | $0$ | $2$ |
| 2 | $\\pm 1/\\sqrt{3}$ | $1, 1$ |
| 3 | $0, \\pm \\sqrt{3/5}$ | $8/9, 5/9, 5/9$ |

## Changement d'intervalle
Pour $\\int_a^b f(x) dx$ on substitue $x = \\frac{b-a}{2} t + \\frac{a+b}{2}$ ; le facteur $(b-a)/2$ multiplie les poids.
""",
    },
    {
        "concept_id": "concept_gaussian_quadrature",
        "level": "rigorous",
        "title": "Theorie de la quadrature de Gauss",
        "body": """# Theorie de Gauss

## Theoreme fondamental
Pour tout poids $w(x) > 0$ integrable sur $[a, b]$, la quadrature gaussienne est **unique** et atteint le degre d'exactitude maximal $2n - 1$. Les noeuds sont les zeros du polynome orthogonal $P_n$ de la famille associee a $w$.

## Convergence
Pour $f$ continue sur $[a, b]$, la suite des quadratures de Gauss converge vers $\\int_a^b f w$ (theoreme de Stieltjes).

## Erreur
Si $f \\in C^{2n}([a, b])$ :

$$E_n = \\frac{(b-a)^{2n+1} (n!)^4}{(2n+1) ((2n)!)^3} \\, f^{(2n)}(\\eta)$$

Convergence super-algebrique pour des $f$ analytiques.

## Variantes
- **Gauss-Lobatto** : impose les bords $a, b$ comme noeuds (utile pour ajustement). Degre d'exactitude $2n - 3$.
- **Gauss-Tchebychev** : poids $w(x) = 1/\\sqrt{1-x^2}$, noeuds equirepartis sur le cercle.
- **Gauss-Hermite** : sur $\\mathbb{R}$ avec $w(x) = e^{-x^2}$, utile en physique statistique.

## Quadrature adaptative
**Gauss-Kronrod** : on ajoute $n+1$ noeuds aux $n$ noeuds de Gauss pour obtenir un estimateur d'erreur sans recalculer ; c'est le coeur des integrateurs de QUADPACK.
""",
    },
]


def main() -> None:
    inserted = 0
    for c in CONTENTS:
        rows = neo4j_conn.run_query(
            "MATCH (c:Concept {id: $cid}) RETURN c.id AS id",
            {"cid": c["concept_id"]},
        )
        if not rows:
            logger.warning("Concept %s not found, skip", c["concept_id"])
            continue

        # Le contenu francais est stocke dans title_fr / body_fr sur le MEME
        # noeud Content que la version anglaise. La cle est alignee sur
        # seed_content.py / seed_content_approximation_en.py.
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

    logger.info("Total FR contents (modules 1+2) inserted/updated : %d", inserted)


if __name__ == "__main__":
    main()
