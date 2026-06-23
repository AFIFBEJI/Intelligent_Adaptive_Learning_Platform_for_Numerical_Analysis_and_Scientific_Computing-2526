# Pré-test / Post-test — Banque de 30 items

> **Couverture** : 5 concepts cibles × 6 questions chacun (2 easy + 2 medium + 2 hard).
> **Allocation** : 15 items → pré-test (version A), 15 items → post-test (version B).
> **Durée prévue** : 20 minutes par version.
> **Format** : QCM 4 options + 1 question ouverte courte par concept (calcul).
> **Notation** : 1 point par QCM correct, 2 points par calcul correct, max 100% normalisé.

---

## Concepts ciblés (alignés avec le KG Neo4j)

| ID Neo4j | Concept | Module |
|---|---|---|
| `concept_lagrange` | Interpolation de Lagrange | 1 |
| `concept_simpson` | Méthode de Simpson (intégration) | 2 |
| `concept_least_squares` | Approximation par moindres carrés | 3 |
| `concept_newton_raphson` | Newton-Raphson (root-finding) | 4 |
| `concept_bissection` | Bissection (root-finding) | 4 |

**Pourquoi ces 5 ?** Ils couvrent les 4 modules, sont enseignés dans tous les
cours d'analyse numérique de niveau ESPRIT, et ont chacun ≥ 5 questions
hand-curated dans la banque existante (`quiz_question_bank.py`).

---

## Stratégie de construction (équivalence A/B)

Pour chaque concept × difficulté on prépare **2 items isomorphes** :
même structure, mêmes nombres d'opérations, mais valeurs/contexte différents.
Cela garantit qu'un étudiant qui tombe sur item-A en pré et item-B en post
ne mesure pas un effet d'apprentissage du test lui-même.

**Exemple d'isomorphes** :
- A (easy, Lagrange) : "Donnez P(1) pour les points (0,1), (2,5)."
- B (easy, Lagrange) : "Donnez P(2) pour les points (1,3), (4,9)."

Mêmes opérations, valeurs différentes, même réponse attendue (interpolation linéaire = formule).

---

## Banque complète : 30 items

> 🇫🇷 Version française ici. Pour le bilingue, ajouter `_en` à chaque item
> (la plateforme expose déjà `q.question_fr` / `q.question_en` partout).

### Concept 1 : Interpolation de Lagrange

#### A1 (easy) — Pré-test
> Soient les points (0, 1) et (2, 5). Quelle est la valeur de l'interpolant
> linéaire de Lagrange P(x) en x = 1 ?
- a) 1  •  b) 2  •  c) **3** ✓  •  d) 5
- *Justification : P(1) = (1−2)/(0−2)·1 + (1−0)/(2−0)·5 = 0.5·1 + 0.5·5 = 3.*
- Concept : `concept_lagrange` | Difficulté : easy

#### B1 (easy) — Post-test
> Soient les points (1, 3) et (4, 9). Quelle est la valeur de l'interpolant
> linéaire de Lagrange P(x) en x = 2 ?
- a) 4  •  b) **5** ✓  •  c) 6  •  d) 7
- *Justification : P(2) = (2−4)/(1−4)·3 + (2−1)/(4−1)·9 = (2/3)·3 + (1/3)·9 = 2 + 3 = 5.*

#### A2 (medium) — Pré-test
> Combien de polynômes d'interpolation de degré au plus 3 passent par
> 4 points distincts en abscisse ?
- a) 0  •  b) **1** ✓  •  c) 4  •  d) Une infinité
- *Théorème d'unicité de Lagrange.*

#### B2 (medium) — Post-test
> Combien de polynômes d'interpolation de degré au plus n passent par
> n+1 points distincts en abscisse ?
- a) 0  •  b) **1** ✓  •  c) n  •  d) Une infinité

#### A3 (hard, calcul) — Pré-test
> Donnez l'expression du polynôme de Lagrange de degré 2 passant par
> (−1, 0), (0, 1), (1, 0). (Forme développée attendue.)
- **Réponse : P(x) = 1 − x²** (équivalent à −x² + 1, accepter aussi −0,5(x−1)(x+1)... mais SymPy normalise)
- Notation : 2 points si correct, 1 si forme non-développée mais correcte.

#### B3 (hard, calcul) — Post-test
> Donnez l'expression du polynôme de Lagrange de degré 2 passant par
> (−2, 0), (0, 4), (2, 0). (Forme développée attendue.)
- **Réponse : P(x) = 4 − x²**

---

### Concept 2 : Méthode de Simpson (1/3)

#### A4 (easy) — Pré-test
> La formule de Simpson 1/3 sur [a, b] approxime ∫ₐᵇ f(x)dx par :
- a) (b−a)·f((a+b)/2)
- b) **(b−a)/6 · [f(a) + 4·f((a+b)/2) + f(b)]** ✓
- c) (b−a)/2 · [f(a) + f(b)]
- d) (b−a) · f(a)

#### B4 (easy) — Post-test
> La méthode de Simpson 1/3 est exacte pour les polynômes de degré au plus :
- a) 1  •  b) 2  •  c) **3** ✓  •  d) 4
- *Précision : Simpson 1/3 intègre exactement les polynômes de degré ≤ 3, malgré ses 3 points.*

#### A5 (medium) — Pré-test
> Soit f(x) = x². Calculer l'approximation de Simpson 1/3 de ∫₀² x² dx.
- a) 2  •  b) 2.5  •  c) **8/3 ≈ 2.667** ✓  •  d) 4
- *S = (2−0)/6·[0 + 4·1 + 4] = (1/3)·8 = 8/3. Et c'est exact car deg ≤ 3.*

#### B5 (medium) — Post-test
> Soit f(x) = x³. Calculer l'approximation de Simpson 1/3 de ∫₀² x³ dx.
- a) 2  •  b) **4** ✓  •  c) 6  •  d) 8/3
- *S = (2/6)·[0 + 4·1 + 8] = (1/3)·12 = 4. Exact.*

#### A6 (hard) — Pré-test
> L'erreur de la méthode de Simpson composite avec n sous-intervalles
> sur [a,b] est en O(h^k) où h = (b−a)/n. Quelle est la valeur de k ?
- a) 1  •  b) 2  •  c) **4** ✓  •  d) 6
- *Erreur composite = O(h⁴) — d'où l'efficacité.*

#### B6 (hard) — Post-test
> Quel ordre de précision (en h) apporte la méthode de Simpson par
> rapport à la méthode des trapèzes pour une fonction lisse ?
- a) Même ordre
- b) **2 ordres de mieux (h⁴ vs h²)** ✓
- c) 1 ordre de mieux
- d) 4 ordres de mieux

---

### Concept 3 : Approximation par moindres carrés

#### A7 (easy) — Pré-test
> Dans la régression linéaire des moindres carrés y = ax + b, on minimise :
- a) Σ |yᵢ − (axᵢ + b)|
- b) **Σ (yᵢ − (axᵢ + b))²** ✓
- c) max(|yᵢ − (axᵢ + b)|)
- d) Σ (yᵢ − xᵢ)

#### B7 (easy) — Post-test
> Le système normal des moindres carrés s'écrit (XᵀX)·θ = ... :
- a) Xᵀ
- b) X·y
- c) **Xᵀ·y** ✓
- d) X⁻¹·y

#### A8 (medium) — Pré-test
> On cherche la droite de régression y = ax + b sur les points
> (0,1), (1,2), (2,4). La pente a vaut :
- a) 1  •  b) **1.5** ✓  •  c) 2  •  d) 2.5
- *a = ((Σxy − n·x̄·ȳ) / (Σx² − n·x̄²) = (10 − 3·1·7/3)/(5−3·1) = (10−7)/2 = 1.5.*

#### B8 (medium) — Post-test
> On cherche la droite de régression y = ax + b sur les points
> (1,2), (2,3), (3,5). La pente a vaut :
- a) 1  •  b) 1.25  •  c) **1.5** ✓  •  d) 2
- *Même structure, a = 1.5.*

#### A9 (hard) — Pré-test
> Si la matrice XᵀX est singulière, alors :
- a) Il n'existe aucune solution
- b) **La solution n'est pas unique (problème mal posé)** ✓
- c) La solution est nécessairement nulle
- d) On change de méthode pour Newton

#### B9 (hard) — Post-test
> La régularisation de Tikhonov (ridge) modifie le système normal en :
- a) (XᵀX)·θ = Xᵀy
- b) **(XᵀX + λI)·θ = Xᵀy** ✓
- c) (XᵀX − λI)·θ = Xᵀy
- d) X·θ = y + λI

---

### Concept 4 : Newton-Raphson

#### A10 (easy) — Pré-test
> L'itération de Newton-Raphson pour trouver une racine de f(x) = 0 est :
- a) xₙ₊₁ = xₙ − f(xₙ)
- b) **xₙ₊₁ = xₙ − f(xₙ)/f'(xₙ)** ✓
- c) xₙ₊₁ = xₙ + f(xₙ)/f'(xₙ)
- d) xₙ₊₁ = (xₙ + xₙ₋₁)/2

#### B10 (easy) — Post-test
> Quelle est la condition principale pour appliquer Newton-Raphson en xₙ ?
- a) f(xₙ) = 0
- b) **f'(xₙ) ≠ 0** ✓
- c) f''(xₙ) ≠ 0
- d) xₙ > 0

#### A11 (medium) — Pré-test
> Pour f(x) = x² − 2, partant de x₀ = 1, donnez x₁ par Newton-Raphson.
- a) 1.0  •  b) 1.25  •  c) **1.5** ✓  •  d) 2.0
- *x₁ = 1 − (1−2)/(2·1) = 1 + 0.5 = 1.5.*

#### B11 (medium) — Post-test
> Pour f(x) = x² − 3, partant de x₀ = 2, donnez x₁ par Newton-Raphson.
- a) 1.5  •  b) 1.6667  •  c) **1.75** ✓  •  d) 2.0
- *x₁ = 2 − (4−3)/(2·2) = 2 − 0.25 = 1.75.*

#### A12 (hard) — Pré-test
> L'ordre de convergence de Newton-Raphson, lorsque les conditions
> classiques sont remplies, est :
- a) Linéaire (1)
- b) **Quadratique (2)** ✓
- c) Cubique (3)
- d) Exponentiel

#### B12 (hard) — Post-test
> Si f'(α) = 0 où α est la racine (racine multiple), l'ordre de convergence
> de Newton-Raphson tombe à :
- a) **Linéaire (1)** ✓
- b) Quadratique (2)
- c) Cubique (3)
- d) Pas de convergence

---

### Concept 5 : Bissection

#### A13 (easy) — Pré-test
> La méthode de bissection nécessite, sur [a, b], que :
- a) f(a) = f(b)
- b) **f(a)·f(b) < 0** ✓
- c) f(a)·f(b) > 0
- d) f'(a) ≠ 0

#### B13 (easy) — Post-test
> Si f est continue sur [a,b] avec f(a) = −2 et f(b) = 3, alors la bissection :
- a) Ne fonctionne pas
- b) Trouve une racine en 1 itération
- c) **Trouve une racine après un nombre fini d'itérations** ✓
- d) Diverge

#### A14 (medium) — Pré-test
> L'erreur après n itérations de bissection sur [a, b] est majorée par :
- a) (b−a)/n
- b) **(b−a)/2ⁿ** ✓
- c) (b−a)·2ⁿ
- d) (b−a)/(n+1)

#### B14 (medium) — Post-test
> Combien d'itérations de bissection sur [0,1] sont nécessaires pour
> garantir une erreur inférieure à 10⁻³ ?
- a) 5  •  b) 8  •  c) **10** ✓  •  d) 20
- *2ⁿ > 1000 → n ≥ ⌈log₂(1000)⌉ = 10.*

#### A15 (hard) — Pré-test
> Comparée à Newton-Raphson, la bissection est :
- a) Plus rapide mais moins fiable
- b) **Plus fiable mais plus lente (convergence linéaire vs quadratique)** ✓
- c) Plus rapide et plus fiable
- d) Équivalente

#### B15 (hard) — Post-test
> Pourquoi préfère-t-on parfois la méthode de la sécante à Newton-Raphson ?
- a) Convergence plus rapide
- b) **Pas besoin de calculer la dérivée** ✓
- c) Garantit la convergence
- d) Aucune des trois

---

## Allocation aux 2 versions

| Version | Items (15 par version) | Distribution difficulté |
|---|---|---|
| **A (pré-test)** | A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, A11, A12, A13, A14, A15 | 5 easy + 5 medium + 5 hard |
| **B (post-test)** | B1, B2, B3, B4, B5, B6, B7, B8, B9, B10, B11, B12, B13, B14, B15 | 5 easy + 5 medium + 5 hard |

**Contre-balancing** : 50% des participants A→B, 50% B→A (assigné par parité de l'ID participant).

---

## Grille de correction (notation 0-100)

```
Score brut = nb_QCM_correct × 1 + nb_calcul_correct × 2
Max brut    = 13 × 1 + 2 × 2 = 17 points (15 QCM dont 2 calculs en hard A3/B3)

Note normalisée = (score_brut / 17) × 100

Bornes :
  0-39  → faible
  40-69 → moyen
  70-100→ fort
```

---

## Implémentation technique

Ces 30 items doivent être ajoutés à `backend/app/data/study_pretest.py`
(nouveau fichier, structure identique à `diagnostic_questions.py`).
Le router `/study/pretest` (à créer) tirera 15 items selon la version A/B
assignée au participant et renverra un quiz scellé (pas d'aide LLM, pas
de feedback détaillé, juste le score final).

Pseudo-flow :

```
1. POST /study/enroll      → assigne group + version (A ou B) en pré
2. GET  /study/pretest     → retourne 15 items (sans correct_answer)
3. POST /study/pretest     → submit + calcule score_pre
4. [phase intervention 4 semaines]
5. GET  /study/posttest    → retourne les 15 items de l'autre version
6. POST /study/posttest    → submit + calcule score_post + lance le questionnaire SUS
```

---

## Pilote (semaine -1)

Avant le lancement, faire passer pré-test + post-test à **5 étudiants
volontaires** (non participants à l'étude finale). Mesurer :

1. Score moyen A vs B → ils doivent être équivalents (±5 points). Sinon
   rééquilibrer en remplaçant les items "trop faciles" ou "trop durs" dans
   la version déviante.
2. Temps moyen → cible 20 min. Si > 25, retirer 1-2 items.
3. Feedback qualitatif sur les items : énoncés ambigus, fautes de frappe, etc.

---

**Version** : 1.0 — 12 mai 2026
**Prochaine révision** : après pilote (cible 22 mai)
