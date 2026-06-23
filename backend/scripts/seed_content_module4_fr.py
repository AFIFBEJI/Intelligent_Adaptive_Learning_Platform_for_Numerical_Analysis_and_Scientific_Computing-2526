"""
Contenu FR pour le Module 4 (Resolution d'equations non-lineaires).

Ecrit dans `title_fr` / `body_fr` sur les MEMES noeuds Content que la
version EN. Cle alignee : id = "content_<concept_short>_<level>".

Concepts couverts (4 concepts x 3 niveaux = 12 noeuds Content) :
  - concept_bissection
  - concept_fixed_point
  - concept_newton_raphson
  - concept_secant

Usage : python scripts/seed_content_module4_fr.py
"""
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.graph.neo4j_connection import neo4j_conn

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


CONTENTS = [
    # --- concept_bissection ---
    {
        "concept_id": "concept_bissection",
        "level": "simplified",
        "title": "Bissection (intuition)",
        "body": """# Methode de la bissection - Version simplifiee

**But** : trouver une racine de $f(x) = 0$, c'est-a-dire un nombre $x$ tel que $f(x) = 0$.

## L'idee de base

Si $f$ est continue et que $f(a)$ et $f(b)$ ont des **signes opposes**, alors il y a au moins une racine entre $a$ et $b$ (theoreme des valeurs intermediaires).

**Strategie** : on coupe l'intervalle en deux et on garde la moitie ou il y a la racine.

## Algorithme en 3 etapes

1. Calculer le milieu $m = (a + b) / 2$
2. Regarder le signe de $f(m)$ :
   - Si $f(m) = 0$, on a trouve la racine
   - Si $f(a)$ et $f(m)$ ont des signes opposes, la racine est dans $[a, m]$
   - Sinon elle est dans $[m, b]$
3. Recommencer avec le nouvel intervalle plus petit

## Exemple

Trouver la racine de $f(x) = x^2 - 2$ (qui vaut $\\sqrt{2} \\approx 1.414$) :
- $a = 1$, $b = 2$, $f(1) = -1 < 0$, $f(2) = 2 > 0$ -> racine entre 1 et 2
- $m = 1.5$, $f(1.5) = 0.25 > 0$ -> racine entre 1 et 1.5
- $m = 1.25$, $f(1.25) = -0.4375 < 0$ -> racine entre 1.25 et 1.5
- ... on s'approche de 1.414

## Avantages / Inconvenients

- ✅ **Toujours convergente** si $f$ est continue
- ✅ Tres simple a programmer
- ❌ **Lente** : on gagne 1 bit par iteration (~10 iterations pour 3 chiffres)
""",
    },
    {
        "concept_id": "concept_bissection",
        "level": "standard",
        "title": "Methode de la bissection",
        "body": """# Methode de la bissection

## Hypotheses

Soit $f : [a, b] \\to \\mathbb{R}$ une fonction **continue** verifiant $f(a) \\cdot f(b) < 0$. Le theoreme des valeurs intermediaires garantit l'existence d'au moins une racine $x^* \\in (a, b)$.

## Algorithme

```
Tant que (b - a) > tolerance :
    m <- (a + b) / 2
    si f(m) = 0 : retourner m
    si f(a) * f(m) < 0 : b <- m
    sinon            : a <- m
Retourner (a + b) / 2
```

## Convergence

A l'iteration $k$, l'intervalle a une largeur $(b - a)/2^k$. L'erreur est donc bornee par :

$$|x_k - x^*| \\le \\frac{b - a}{2^{k+1}}$$

C'est une **convergence lineaire** : on gagne un facteur 2 a chaque iteration, soit environ **1 bit par iteration** (3.3 iterations pour 1 chiffre decimal).

## Nombre d'iterations pour une precision $\\epsilon$

$$k \\ge \\log_2\\!\\left(\\frac{b - a}{\\epsilon}\\right) - 1$$

Exemple : pour $\\epsilon = 10^{-6}$ sur $[0, 1]$, il faut environ 20 iterations.

## Limitations

- Necessite un **encadrement** initial $[a, b]$ avec changement de signe
- **Lente** comparee a Newton-Raphson (qui est quadratique)
- Ne marche pas pour les racines doubles ($f$ ne change pas de signe)
""",
    },
    {
        "concept_id": "concept_bissection",
        "level": "rigorous",
        "title": "Bissection : analyse rigoureuse",
        "body": """# Bissection : analyse rigoureuse

## Theoreme de convergence

**Theoreme** : Si $f \\in C^0([a, b])$ avec $f(a) f(b) < 0$, alors la suite $(c_k)$ generee par bissection ou $c_k = (a_k + b_k)/2$ verifie :

$$\\lim_{k \\to \\infty} c_k = x^*, \\quad |c_k - x^*| \\le \\frac{b - a}{2^{k+1}}$$

ou $x^*$ est une racine de $f$ dans $[a, b]$.

**Demonstration** : les suites $(a_k)$ et $(b_k)$ sont monotones et bornees, donc convergentes vers la meme limite $x^*$ (car $b_k - a_k \\to 0$). Par continuite et conservation du signe, $f(x^*) = 0$.

## Comparaison avec Newton-Raphson

| Methode | Ordre de convergence | Hypotheses |
|---------|---------------------|------------|
| Bissection | Lineaire ($q = 2$) | $f$ continue, encadrement |
| Newton-Raphson | Quadratique | $f \\in C^2$, $f'(x^*) \\ne 0$, $x_0$ proche |
| Secante | Super-lineaire ($q \\approx 1.618$) | $f \\in C^2$, deux iteres initiaux |

## Variantes optimisees

- **Regula falsi** (fausse position) : interpolation lineaire entre $f(a)$ et $f(b)$ au lieu du milieu. Convergence plus rapide en pratique mais peut stagner.
- **Methode d'Illinois** : variante de regula falsi qui evite la stagnation.
- **Methode de Brent** : combine bissection + secante + interpolation quadratique inverse. Algorithme par defaut dans `scipy.optimize.brentq`.

## Critere d'arret

Plusieurs choix possibles :
- **Largeur de l'intervalle** : $b_k - a_k < \\epsilon$ (le plus sur)
- **Erreur relative** : $|c_{k+1} - c_k| / |c_k| < \\epsilon$
- **Residu** : $|f(c_k)| < \\delta$ (attention : ne suffit pas seul pour les fonctions a derivee faible)

## Robustesse vs vitesse

La bissection est l'algorithme **le plus robuste** pour les fonctions reelles continues : elle converge **toujours**. Cependant, pour des problemes mal conditionnes, on prefere la coupler avec Newton-Raphson (algorithmes hybrides).
""",
    },

    # --- concept_fixed_point ---
    {
        "concept_id": "concept_fixed_point",
        "level": "simplified",
        "title": "Iteration du point fixe (intuition)",
        "body": """# Iteration du point fixe - Version simplifiee

**Idee** : Au lieu de resoudre $f(x) = 0$ directement, on **transforme** le probleme.

On reecrit l'equation sous la forme $x = g(x)$ pour une fonction $g$ bien choisie. Une solution s'appelle un **point fixe** de $g$ : un nombre qui ne change pas quand on lui applique $g$.

## Algorithme

On choisit un point de depart $x_0$ et on itere :

$$x_{k+1} = g(x_k)$$

Si $g$ est bien choisie, la suite converge vers le point fixe $x^*$ tel que $x^* = g(x^*)$.

## Exemple

Pour resoudre $x^2 - 2 = 0$ (donc $x = \\sqrt{2}$), on peut reecrire :
$$x = g(x) = \\frac{1}{2}\\left(x + \\frac{2}{x}\\right)$$

(c'est la formule de Heron, vieille de 2000 ans)

Avec $x_0 = 1$ :
- $x_1 = 0.5(1 + 2) = 1.5$
- $x_2 = 0.5(1.5 + 1.333) = 1.4166$
- $x_3 = 1.41421...$ (deja $\\sqrt{2}$ a 5 chiffres !)

## Quand ca marche / ca marche pas

**Ca converge** si la pente $|g'(x^*)| < 1$ pres du point fixe.
**Ca diverge** si $|g'(x^*)| > 1$ : la suite s'eloigne au lieu de s'approcher.

C'est pour ca que **le choix de $g$ est crucial** : la meme equation $f(x) = 0$ peut donner plusieurs $g$ possibles, certaines convergent, d'autres pas.
""",
    },
    {
        "concept_id": "concept_fixed_point",
        "level": "standard",
        "title": "Iteration du point fixe",
        "body": """# Iteration du point fixe

## Definition

Un **point fixe** de $g : I \\to I$ est un point $x^* \\in I$ tel que $g(x^*) = x^*$.

Pour resoudre $f(x) = 0$, on reformule : $x = g(x)$ avec $g(x) = x - h(x) \\cdot f(x)$ ou $h$ est une fonction non nulle.

## Theoreme du point fixe (Banach contraction)

Si $g$ est **contractante** sur $[a, b]$, c'est-a-dire qu'il existe $L \\in [0, 1)$ tel que :

$$|g(x) - g(y)| \\le L |x - y| \\quad \\forall x, y \\in [a, b]$$

alors :
1. Il existe un **unique** point fixe $x^* \\in [a, b]$
2. La suite $x_{k+1} = g(x_k)$ converge vers $x^*$ pour tout $x_0 \\in [a, b]$
3. L'erreur verifie $|x_k - x^*| \\le L^k |x_0 - x^*|$

## Critere pratique

Pour $g \\in C^1$ : si $|g'(x^*)| < 1$, le point fixe est **localement attractif**.

- Si $|g'(x^*)| < 1$ : convergence (avec ordre lineaire)
- Si $|g'(x^*)| > 1$ : divergence
- Si $|g'(x^*)| = 1$ : cas limite (peut converger ou non)

## Exemple : equation $x = \\cos(x)$

Soit $g(x) = \\cos(x)$. On a $g'(x) = -\\sin(x)$.

Le point fixe est $x^* \\approx 0.7391$ (intersection de $y = x$ et $y = \\cos x$).

$g'(x^*) = -\\sin(0.7391) \\approx -0.674$, donc $|g'(x^*)| < 1$ : ca converge.

```
x0 = 1
x1 = cos(1) = 0.5403
x2 = cos(0.5403) = 0.8576
x3 = cos(0.8576) = 0.6543
...
xn -> 0.7391
```

## Vitesse de convergence

L'ordre de convergence est **lineaire** avec un facteur $|g'(x^*)|$. Plus $|g'(x^*)|$ est petit, plus la convergence est rapide.

Cas particulier : si $g'(x^*) = 0$, la convergence devient **quadratique** (c'est exactement ce qui se passe pour Newton-Raphson, qui est un cas particulier de point fixe).
""",
    },
    {
        "concept_id": "concept_fixed_point",
        "level": "rigorous",
        "title": "Theorie du point fixe",
        "body": """# Theorie du point fixe

## Theoreme de Banach (point fixe contractant)

Soit $(X, d)$ un espace metrique **complet**. Si $T : X \\to X$ est une **contraction** (existe $L < 1$ tel que $d(T(x), T(y)) \\le L d(x, y)$ pour tous $x, y$), alors :

1. **Existence et unicite** : il existe un unique $x^* \\in X$ tel que $T(x^*) = x^*$
2. **Convergence globale** : pour tout $x_0$, la suite $x_{k+1} = T(x_k)$ converge vers $x^*$
3. **Vitesse** : $d(x_k, x^*) \\le \\frac{L^k}{1 - L} d(x_1, x_0)$

## Convergence locale (cas $C^1$)

Si $g \\in C^1$ avec $|g'(x^*)| < 1$, il existe un voisinage $V$ de $x^*$ stable par $g$ tel que la suite $x_{k+1} = g(x_k)$ converge vers $x^*$ pour tout $x_0 \\in V$.

**Demonstration** : par continuite de $g'$, il existe $\\delta > 0$ tel que $|g'(x)| \\le L < 1$ sur $V = [x^* - \\delta, x^* + \\delta]$. Alors $g$ est contractante sur $V$ : on applique Banach.

## Ordre de convergence

Soit $e_k = x_k - x^*$. Pour $g \\in C^p$ avec $g'(x^*) = g''(x^*) = \\dots = g^{(p-1)}(x^*) = 0$ et $g^{(p)}(x^*) \\ne 0$ :

$$e_{k+1} \\sim \\frac{g^{(p)}(x^*)}{p!} \\, e_k^p$$

Convergence **d'ordre $p$**.

- $p = 1$ : lineaire (cas generique)
- $p = 2$ : quadratique (Newton-Raphson)
- $p = 3$ : cubique (methode de Halley)

## Application a Newton-Raphson

Newton-Raphson est l'iteration $x_{k+1} = x_k - f(x_k)/f'(x_k)$, soit le point fixe de :

$$g(x) = x - \\frac{f(x)}{f'(x)}$$

Calculons $g'$ :

$$g'(x) = 1 - \\frac{f'(x)^2 - f(x) f''(x)}{f'(x)^2} = \\frac{f(x) f''(x)}{f'(x)^2}$$

A la racine $x^*$, $f(x^*) = 0$, donc $g'(x^*) = 0$. **C'est ce qui rend Newton quadratique.**

## Acceleration : algorithme d'Aitken

Si $(x_k)$ converge lineairement vers $x^*$, la suite acceleree par **Aitken** :

$$y_k = x_k - \\frac{(x_{k+1} - x_k)^2}{x_{k+2} - 2 x_{k+1} + x_k}$$

converge plus rapidement vers $x^*$. Combine avec une iteration de point fixe, on obtient la **methode de Steffensen** (convergence quadratique).
""",
    },

    # --- concept_newton_raphson ---
    {
        "concept_id": "concept_newton_raphson",
        "level": "simplified",
        "title": "Newton-Raphson (intuition)",
        "body": """# Methode de Newton-Raphson - Version simplifiee

**But** : trouver une racine de $f(x) = 0$ tres rapidement.

## L'idee geometrique

A partir d'un point $x_k$, on regarde la **tangente** a la courbe $y = f(x)$ en ce point. Cette tangente est une droite. On regarde **ou cette droite coupe l'axe des x**, et on appelle ce point $x_{k+1}$.

C'est notre nouvel essai. On recommence depuis $x_{k+1}$.

## La formule

$$x_{k+1} = x_k - \\frac{f(x_k)}{f'(x_k)}$$

## Pourquoi ca marche ?

La tangente a la courbe au point $(x_k, f(x_k))$ a pour equation :
$$y = f(x_k) + f'(x_k)(x - x_k)$$

Elle coupe l'axe des $x$ quand $y = 0$, ce qui donne $x = x_k - f(x_k)/f'(x_k)$.

## Exemple : $\\sqrt{2}$

On veut $f(x) = x^2 - 2 = 0$. La derivee est $f'(x) = 2x$.

Iteration : $x_{k+1} = x_k - \\frac{x_k^2 - 2}{2 x_k} = \\frac{x_k}{2} + \\frac{1}{x_k}$

Avec $x_0 = 1$ :
- $x_1 = 0.5 + 1 = 1.5$
- $x_2 = 0.75 + 0.667 = 1.4167$
- $x_3 = 1.41421...$ ✓

**3 iterations** pour 5 chiffres exacts. Beaucoup plus rapide que la bissection.

## Avantages / Inconvenients

- ✅ **Tres rapide** : convergence quadratique (le nombre de chiffres exacts double a chaque iteration)
- ❌ Necessite **calculer la derivee** $f'$
- ❌ Peut **diverger** si $x_0$ est mal choisi
- ❌ Probleme si $f'(x_k) = 0$ (division par zero)
""",
    },
    {
        "concept_id": "concept_newton_raphson",
        "level": "standard",
        "title": "Methode de Newton-Raphson",
        "body": """# Newton-Raphson

## Formule

$$x_{k+1} = x_k - \\frac{f(x_k)}{f'(x_k)}$$

## Derivation

On cherche un zero de $f$. Au voisinage de $x_k$, le developpement de Taylor donne :

$$f(x) \\approx f(x_k) + f'(x_k)(x - x_k)$$

Resoudre cette approximation lineaire donne $x = x_k - f(x_k)/f'(x_k)$, qui devient la nouvelle iteration.

## Convergence quadratique

**Theoreme** : Si $f \\in C^2$ au voisinage d'une racine simple $x^*$ ($f(x^*) = 0$, $f'(x^*) \\ne 0$), et si $x_0$ est suffisamment proche de $x^*$, alors :

$$|x_{k+1} - x^*| \\le C |x_k - x^*|^2 \\quad \\text{ou} \\quad C = \\frac{|f''(x^*)|}{2 |f'(x^*)|}$$

**Conclusion** : le nombre de chiffres exacts **double** a chaque iteration. Typiquement, 5-7 iterations suffisent pour la precision machine.

## Critere d'arret

Plusieurs criteres possibles :
- **Erreur relative** : $|x_{k+1} - x_k| / |x_{k+1}| < \\epsilon$
- **Residu** : $|f(x_{k+1})| < \\delta$
- **Combine** : les deux

## Cas problematiques

| Probleme | Symptome | Solution |
|----------|----------|----------|
| $f'(x_k) = 0$ | Division par zero | Methode hybride (bissection + Newton) |
| Racine double | Convergence lineaire au lieu de quadratique | Newton modifie : $x_{k+1} = x_k - 2 f / f'$ |
| Mauvaise initialisation | Divergence ou cycle | Encadrement bissection puis Newton |
| Oscillation | Boucle infinie | Damping : $x_{k+1} = x_k - \\alpha f / f'$ avec $\\alpha < 1$ |

## Variante : Newton-Raphson modifie

Pour les racines de multiplicite $m$, la convergence quadratique est restauree par :

$$x_{k+1} = x_k - m \\frac{f(x_k)}{f'(x_k)}$$
""",
    },
    {
        "concept_id": "concept_newton_raphson",
        "level": "rigorous",
        "title": "Newton-Raphson : analyse",
        "body": """# Newton-Raphson : analyse complete

## Theoreme de convergence locale

Soit $f \\in C^2$ au voisinage d'une racine simple $x^*$ (i.e. $f(x^*) = 0$ et $f'(x^*) \\ne 0$). Alors il existe $\\delta > 0$ tel que pour tout $x_0 \\in [x^* - \\delta, x^* + \\delta]$, la suite definie par $x_{k+1} = x_k - f(x_k)/f'(x_k)$ verifie :

$$|x_{k+1} - x^*| \\le C |x_k - x^*|^2, \\quad C = \\frac{|f''(x^*)|}{2 |f'(x^*)|}$$

## Demonstration

Developpement de Taylor de $f$ a l'ordre 2 autour de $x_k$ :

$$0 = f(x^*) = f(x_k) + f'(x_k)(x^* - x_k) + \\frac{f''(\\xi_k)}{2}(x^* - x_k)^2$$

avec $\\xi_k$ entre $x_k$ et $x^*$. Donc :

$$x^* - x_k = -\\frac{f(x_k)}{f'(x_k)} - \\frac{f''(\\xi_k)}{2 f'(x_k)}(x^* - x_k)^2$$

Et $x_{k+1} = x_k - f(x_k)/f'(x_k)$, donc :

$$x_{k+1} - x^* = \\frac{f''(\\xi_k)}{2 f'(x_k)} (x_k - x^*)^2$$

Ce qui prouve la convergence quadratique pres de $x^*$.

## Theoreme de Kantorovich (convergence semi-locale)

Plus puissant que la convergence locale : ne suppose pas la connaissance de $x^*$.

Si $f \\in C^2$ et il existe $x_0$, $\\beta$, $\\eta$, $L$ avec :
- $|f(x_0) / f'(x_0)| \\le \\eta$
- $|f''(x)| \\le L$ pour $|x - x_0| \\le 2\\eta$
- $|f'(x_0)| \\ge \\beta > 0$
- $h := \\beta L \\eta < 1/2$

alors la suite Newton converge vers une racine $x^*$ avec $|x_k - x^*| \\le 2\\eta (2h)^{2^k - 1}$.

## Bassin d'attraction et chaos

Pour des polynomes complexes, le **bassin d'attraction** de chaque racine forme une fractale (ensembles de Newton). Exemple : $z^3 - 1 = 0$ produit la celebre fractale de Newton avec 3 bassins entrelaces.

## Methodes derivees

### Newton modifie (racines multiples)

Pour une racine de multiplicite $m$ : $x_{k+1} = x_k - m f / f'$. Convergence quadratique restauree.

### Methode de Halley (ordre 3)

Utilise aussi $f''$ :
$$x_{k+1} = x_k - \\frac{2 f f'}{2 (f')^2 - f f''}$$

Convergence cubique mais cout par iteration plus eleve.

### Quasi-Newton (Broyden)

Approxime $f'$ par differences divisees pour eviter le calcul analytique. Generalise la secante en multidimensionnel.

## Application en optimisation

Pour minimiser $g$, on cherche $g'(x) = 0$ et on applique Newton :
$$x_{k+1} = x_k - \\frac{g'(x_k)}{g''(x_k)}$$

C'est la methode de Newton **pour l'optimisation** (cf. Module 3).
""",
    },

    # --- concept_secant ---
    {
        "concept_id": "concept_secant",
        "level": "simplified",
        "title": "Methode de la secante (intuition)",
        "body": """# Methode de la secante - Version simplifiee

**Probleme avec Newton-Raphson** : il faut calculer $f'(x)$. Parfois, $f'$ est :
- Tres compliquee a calculer
- Pas accessible (par exemple si $f$ est donnee par un programme)

**Idee de la secante** : remplacer la derivee par une **approximation** utilisant deux points precedents.

## La formule

Au lieu de la tangente (Newton), on utilise la **droite secante** entre deux points $(x_{k-1}, f(x_{k-1}))$ et $(x_k, f(x_k))$.

L'approximation de la pente est :
$$f'(x_k) \\approx \\frac{f(x_k) - f(x_{k-1})}{x_k - x_{k-1}}$$

D'ou la formule :

$$x_{k+1} = x_k - f(x_k) \\cdot \\frac{x_k - x_{k-1}}{f(x_k) - f(x_{k-1})}$$

## Comparaison avec Newton

| | Newton | Secante |
|---|---|---|
| Derivee $f'$ | Necessaire | **Pas besoin** |
| Initialisation | 1 point | 2 points |
| Convergence | Quadratique (ordre 2) | Super-lineaire (ordre $\\sim 1.618$) |
| Vitesse pratique | Plus rapide | Un peu plus lente |

## Pourquoi le nombre d'or ?

L'ordre de convergence de la secante est $\\varphi = (1 + \\sqrt{5})/2 \\approx 1.618$, le **nombre d'or**. C'est un peu moins bon que Newton (ordre 2) mais bien mieux que la bissection (ordre 1).

En pratique, comme on n'a pas a calculer $f'$, **chaque iteration coute moins cher** : la secante peut etre globalement **plus efficace** que Newton si le calcul de $f'$ est couteux.

## Exemple

Pour $f(x) = x^2 - 2 = 0$ avec $x_0 = 1$, $x_1 = 2$ :
- $x_2 = 2 - (4 - 2)(2 - 1)/(4 - (-1)) = 2 - 0.4 = 1.6$
- $x_3 = 1.6 - (0.56)(1.6 - 2)/(0.56 - 2) = 1.4286$
- $x_4 = 1.4146$ etc.

Convergence vers $\\sqrt{2}$ presque aussi vite que Newton.
""",
    },
    {
        "concept_id": "concept_secant",
        "level": "standard",
        "title": "Methode de la secante",
        "body": """# Methode de la secante

## Formule

A partir de deux iteres consecutifs $x_{k-1}$ et $x_k$ :

$$x_{k+1} = x_k - f(x_k) \\frac{x_k - x_{k-1}}{f(x_k) - f(x_{k-1})}$$

## Interpretation geometrique

C'est la racine de la droite passant par les points $(x_{k-1}, f(x_{k-1}))$ et $(x_k, f(x_k))$ — d'ou le nom **secante** (qui coupe la courbe).

## Convergence super-lineaire

**Theoreme** : Si $f \\in C^2$ au voisinage d'une racine simple $x^*$, et si les iteres initiaux sont assez proches de $x^*$, alors la secante converge avec un ordre $\\varphi = (1 + \\sqrt{5})/2 \\approx 1.618$ :

$$|x_{k+1} - x^*| \\sim C |x_k - x^*|^{\\varphi}$$

C'est entre lineaire (1) et quadratique (2).

## Comparaison avec Newton-Raphson

| Critere | Secante | Newton |
|---------|---------|--------|
| Cout par iteration | 1 evaluation $f$ | 1 eval $f$ + 1 eval $f'$ |
| Ordre | $\\sim 1.618$ | 2 |
| **Cout total pour precision $\\epsilon$** | Souvent plus bas | Plus haut si $f'$ est cher |

Si l'evaluation de $f$ est rapide mais $f'$ tres couteuse, **la secante bat Newton**.

## Lien avec les differences divisees

La pente approximee $\\frac{f(x_k) - f(x_{k-1})}{x_k - x_{k-1}}$ est la **difference divisee d'ordre 1** $f[x_{k-1}, x_k]$. La methode de la secante est donc :

$$x_{k+1} = x_k - \\frac{f(x_k)}{f[x_{k-1}, x_k]}$$

C'est l'analogue discret de Newton-Raphson.

## Variantes

- **Regula falsi** (fausse position) : combine secante avec encadrement (garde toujours un changement de signe). Plus robuste mais peut stagner.
- **Methode de Steffensen** : $x_{k+1} = x_k - f(x_k)^2 / (f(x_k + f(x_k)) - f(x_k))$, ordre 2 sans calculer $f'$.
- **Methode de Muller** : utilise 3 points et fait passer une parabole. Convergence ordre $\\approx 1.84$.

## Implementation pratique

```python
def secant(f, x0, x1, tol=1e-10, max_iter=50):
    f0, f1 = f(x0), f(x1)
    for k in range(max_iter):
        if abs(f1 - f0) < 1e-15:
            break  # eviter division par zero
        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
        if abs(x2 - x1) < tol:
            return x2
        x0, f0 = x1, f1
        x1, f1 = x2, f(x2)
    return x1
```
""",
    },
    {
        "concept_id": "concept_secant",
        "level": "rigorous",
        "title": "Secante : analyse rigoureuse",
        "body": """# Secante : analyse rigoureuse

## Theoreme de convergence

Soit $f \\in C^2$ au voisinage d'une racine simple $x^*$ ($f(x^*) = 0$, $f'(x^*) \\ne 0$). Si $x_0, x_1$ sont assez proches de $x^*$, la suite secante verifie :

$$|x_{k+1} - x^*| \\sim \\left|\\frac{f''(x^*)}{2 f'(x^*)}\\right|^{(\\varphi - 1)/(\\varphi + 1)} |x_k - x^*|^{\\varphi}$$

ou $\\varphi = (1 + \\sqrt{5})/2$ est le nombre d'or.

## Derivation de l'ordre

L'erreur $e_k = x_k - x^*$ satisfait approximativement :

$$e_{k+1} \\approx C \\, e_k \\, e_{k-1}$$

Si $e_{k+1} \\sim e_k^p$, on a $e_k^p \\sim e_k \\cdot e_{k-1}$, soit $e_k^{p-1} \\sim e_{k-1}$, soit $e_k \\sim e_{k-1}^{1/(p-1)}$. Or $e_k \\sim e_{k-1}^p$. D'ou $p = 1/(p - 1)$, soit $p^2 - p - 1 = 0$, $p = \\varphi$.

## Cout asymptotique

Le **cout amorti** pour une precision $\\epsilon$ avec une evaluation de $f$ par iteration est :

$$\\text{cout total} \\sim \\frac{\\log(1/\\epsilon)}{\\log \\varphi} \\approx \\frac{\\log(1/\\epsilon)}{0.481}$$

Pour Newton avec eval $f$ + $f'$ par iteration :

$$\\text{cout total} \\sim 2 \\cdot \\frac{\\log(1/\\epsilon)}{\\log 2} \\approx \\frac{\\log(1/\\epsilon)}{0.347}$$

**La secante est plus efficace** si $f'$ coute plus que $0.44 \\cdot $ le cout de $f$.

## Methodes hybrides

Algorithmes pratiques combinent plusieurs methodes :

### Methode de Brent

Utilise dans `scipy.optimize.brentq` :
1. Garde un encadrement [a, b] avec changement de signe (bissection)
2. Tente une etape de **secante** ou **interpolation quadratique inverse** si le pas est dans l'encadrement
3. Sinon, fait une bissection (garantit convergence)

Combine la **fiabilite de la bissection** avec la **vitesse de la secante**.

### Methode de Dekker

Variante anterieure de Brent. Memes principes.

### Algorithme de Ridders

Combine secante avec une transformation exponentielle pour ameliorer la convergence pres des racines.

## Generalisation multidimensionnelle : Broyden

Pour resoudre $F(\\mathbf{x}) = \\mathbf{0}$ avec $F : \\mathbb{R}^n \\to \\mathbb{R}^n$, la methode de **Broyden** approxime la jacobienne $J$ a partir des iteres precedents (mise a jour rang-1) :

$$B_{k+1} = B_k + \\frac{(\\Delta F_k - B_k \\Delta x_k) \\Delta x_k^T}{\\Delta x_k^T \\Delta x_k}$$

ou $\\Delta x_k = x_{k+1} - x_k$ et $\\Delta F_k = F(x_{k+1}) - F(x_k)$.

C'est la generalisation multidimensionnelle de la secante. Convergence super-lineaire, cout $O(n^2)$ par iteration au lieu de $O(n^3)$ pour Newton multidimensionnel.

## Lien avec les Krylov

En tres grande dimension (millions de variables), on utilise des methodes de **Krylov** (GMRES, Bi-CGSTAB) qui ne stockent jamais $J$ explicitement et n'utilisent que des produits matrice-vecteur. Ces methodes sont des generalisations de la secante adaptees aux systemes lineaires geants issus de la linearisation.
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

    logger.info("Total FR contents (Module 4) inserted/updated : %d", inserted)


if __name__ == "__main__":
    main()
