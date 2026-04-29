# ============================================================
# Banque etendue de questions par concept — Quiz IA
# ============================================================
# 5 questions hand-crafted par concept × 15 concepts = 75 questions.
# Sert le quiz adaptatif (/quiz-ai/generate) sans appel LLM :
# - instantane (< 50ms)
# - questions validees pedagogiquement
# - tirage aleatoire avec seed -> differentes a chaque fois
#
# Le LLM Gemma E2B reste optionnel via le flag use_llm=true pour
# ceux qui veulent des "variantes IA experimentales", mais le defaut
# pro = banque hand-curated.
# ============================================================

# Format : meme structure que diagnostic_questions.py
# Les 2 premieres questions par concept proviennent de diagnostic_questions
# (reutilisees), les 3 suivantes sont nouvelles pour avoir une variete.

QUESTION_BANK_BY_CONCEPT: dict[str, list[dict]] = {
    # ─── MODULE 1 : INTERPOLATION ────────────────────────
    "concept_polynomial_basics": [
        {
            "question": "Quel est le degre du polynome $p(x) = 3x^4 - 2x^2 + 5$ ?",
            "options": ["2", "3", "4", "5"],
            "correct_answer": "4",
            "explanation": "Le degre d'un polynome $p(x) = a_n x^n + ... + a_1 x + a_0$ est l'exposant le plus eleve dont le coefficient $a_n$ est non nul. Dans $3x^4 - 2x^2 + 5$, les coefficients sont $a_4=3, a_3=0, a_2=-2, a_1=0, a_0=5$ : la plus grande puissance avec coefficient non nul est $x^4$, donc le degre vaut $4$.",
        },
        {
            "question": "Combien de coefficients faut-il pour definir un polynome de degre 3 ?",
            "options": ["2", "3", "4", "5"],
            "correct_answer": "4",
            "explanation": "Un polynome de degre $n$ s'ecrit $p(x) = a_n x^n + a_{n-1} x^{n-1} + ... + a_1 x + a_0$, ce qui donne $n+1$ coefficients (de $a_0$ jusqu'a $a_n$ inclus). Pour le degre 3, cela fait donc $a_0, a_1, a_2, a_3$ soit 4 coefficients. C'est aussi pourquoi il faut 4 points pour interpoler un polynome de degre 3 (un coefficient par point).",
        },
        {
            "question": "Que vaut $p(2)$ pour $p(x) = x^3 - 2x + 1$ ?",
            "options": ["3", "5", "7", "9"],
            "correct_answer": "5",
            "explanation": "On evalue le polynome en $x=2$ : $p(2) = (2)^3 - 2 \cdot (2) + 1 = 8 - 4 + 1 = 5$. Cette evaluation s'appelle aussi la 'valuation' du polynome au point 2 et se calcule efficacement avec le schema de Horner pour des polynomes de haut degre.",
        },
        {
            "question": "Le polynome $p(x) = (x-1)(x+2)(x-3)$ a quels zeros ?",
            "options": ["$1, -2, 3$", "$-1, 2, -3$", "$1, 2, 3$", "$0, 1, 2$"],
            "correct_answer": "$1, -2, 3$",
            "explanation": "Quand un polynome est sous forme factorisee $p(x) = (x - r_1)(x - r_2)...(x - r_n)$, ses zeros (racines) sont les $r_i$. Pour $p(x) = (x-1)(x+2)(x-3)$ on lit directement : $x-1=0 \Rightarrow x=1$, $x+2=0 \Rightarrow x=-2$, $x-3=0 \Rightarrow x=3$. C'est le theoreme de factorisation : tout polynome de $\mathbb{C}[x]$ se factorise en produit de termes lineaires.",
        },
        {
            "question": "Combien de zeros au plus peut avoir un polynome de degre $n$ ?",
            "options": ["$n-1$", "$n$", "$n+1$", "$2n$"],
            "correct_answer": "$n$",
            "explanation": "Theoreme fondamental de l'algebre : un polynome de degre $n$ a exactement $n$ zeros (avec multiplicite, dans $\\mathbb{C}$).",
        },
    ],
    "concept_lagrange": [
        {
            "question": "Combien faut-il de points pour construire un polynome de Lagrange unique de degre au plus $n$ ?",
            "options": ["$n$", "$n+1$", "$2n$", "$n-1$"],
            "correct_answer": "$n+1$",
            "explanation": "Avec $n+1$ points distincts, un unique polynome interpolateur de degre $\\le n$ existe.",
        },
        {
            "question": "Le polynome de base $L_i(x)$ de Lagrange a quelle propriete cle ?",
            "options": [
                "Il vaut 1 partout",
                "Il vaut 1 en $x_i$ et 0 aux autres $x_j$",
                "Il vaut 0 en $x_i$ et 1 ailleurs",
                "Il est egal a $x^i$",
            ],
            "correct_answer": "Il vaut 1 en $x_i$ et 0 aux autres $x_j$",
            "explanation": "Propriete d'interpolation : $L_i(x_j) = \\delta_{ij}$.",
        },
        {
            "question": "Pour 3 points $(x_0, y_0), (x_1, y_1), (x_2, y_2)$, le polynome de Lagrange est de degre :",
            "options": ["1", "2 au plus", "3", "Indetermine"],
            "correct_answer": "2 au plus",
            "explanation": "Avec $n+1 = 3$ points, le polynome interpolateur unique est de degre au plus $n = 2$ (parabole). Il PEUT etre de degre inferieur si les points sont alignes (alors c'est une droite, degre 1), mais en regle generale c'est une parabole. Cette regle '3 points = degre 2' est le coeur de la regle de Simpson en integration numerique.",
        },
        {
            "question": "Quelle est la formule du polynome de Lagrange ?",
            "options": [
                "$p(x) = \\sum y_i x^i$",
                "$p(x) = \\sum y_i L_i(x)$",
                "$p(x) = \\prod (x - x_i)$",
                "$p(x) = \\int f(x) dx$",
            ],
            "correct_answer": "$p(x) = \\sum y_i L_i(x)$",
            "explanation": "La formule de Lagrange est $p(x) = \sum_{i=0}^n y_i \, L_i(x)$ : on prend les valeurs $y_i$ qu'on veut atteindre, et on les pondere par les polynomes de base $L_i$. Comme $L_i(x_k) = \delta_{ik}$, evaluer $p$ en n'importe quel $x_k$ donne $y_k$ par construction. Cette formule explicite est l'avantage majeur de Lagrange (pas de systeme lineaire a resoudre).",
        },
        {
            "question": "Inconvenient principal du polynome de Lagrange par rapport a Newton :",
            "options": [
                "Plus precis",
                "Recalcul total si on ajoute un point",
                "Necessite des points equidistants",
                "Ne fonctionne que pour des polynomes lineaires",
            ],
            "correct_answer": "Recalcul total si on ajoute un point",
            "explanation": "Si on calcule $p(x)$ avec Lagrange sur $n+1$ points, puis qu'on ajoute un $(n+2)$eme point, il faut TOUT recommencer : chaque $L_i$ change car le produit inclut maintenant un facteur supplementaire $(x - x_{n+1})/(x_i - x_{n+1})$. Avec Newton, on ajoute juste un terme $f[x_0,...,x_{n+1}] \prod (x - x_i)$ a la formule existante. Pour des donnees qui arrivent en flux (mesures successives), Newton est donc bien plus adapte.",
        },
    ],
    "concept_divided_differences": [
        {
            "question": "La table des differences divisees sert principalement a :",
            "options": [
                "Calculer des derivees exactes",
                "Construire le polynome de Newton",
                "Resoudre des equations differentielles",
                "Trouver les racines d'un polynome",
            ],
            "correct_answer": "Construire le polynome de Newton",
            "explanation": "Les differences divisees sont les coefficients du polynome de Newton.",
        },
        {
            "question": "La difference divisee d'ordre 0, $f[x_0]$, vaut :",
            "options": ["$f'(x_0)$", "$f(x_0)$", "$0$", "$x_0$"],
            "correct_answer": "$f(x_0)$",
            "explanation": "Par definition $f[x_i] = f(x_i)$ ; les ordres superieurs sont recursifs.",
        },
        {
            "question": "La difference divisee d'ordre 1 $f[x_0, x_1]$ vaut :",
            "options": [
                "$\\frac{f(x_1) - f(x_0)}{x_1 - x_0}$",
                "$f(x_1) \\cdot f(x_0)$",
                "$f(x_1) + f(x_0)$",
                "$\\frac{x_1 - x_0}{f(x_1) - f(x_0)}$",
            ],
            "correct_answer": "$\\frac{f(x_1) - f(x_0)}{x_1 - x_0}$",
            "explanation": "$f[x_0, x_1] = \frac{f(x_1) - f(x_0)}{x_1 - x_0}$ est le taux d'accroissement de $f$ entre $x_0$ et $x_1$, exactement la pente de la corde reliant $(x_0, f(x_0))$ a $(x_1, f(x_1))$. Lorsque $x_1 \to x_0$, ce rapport converge vers $f'(x_0)$ : c'est la definition meme de la derivee. Les differences divisees sont donc une version 'discrete' des derivees.",
        },
        {
            "question": "Les differences divisees sont-elles symetriques ?",
            "options": [
                "Non, l'ordre des points compte",
                "Oui, $f[x_0, x_1] = f[x_1, x_0]$",
                "Seulement pour l'ordre 1",
                "Seulement pour les polynomes",
            ],
            "correct_answer": "Oui, $f[x_0, x_1] = f[x_1, x_0]$",
            "explanation": "On peut le voir avec $f[x_0, x_1] = (f(x_1) - f(x_0))/(x_1 - x_0)$ et $f[x_1, x_0] = (f(x_0) - f(x_1))/(x_0 - x_1)$ : numerateur et denominateur changent tous les deux de signe, donc le rapport reste identique. Cette propriete se generalise a tout ordre : l'ordre des arguments est sans importance, ce qui simplifie beaucoup les calculs.",
        },
        {
            "question": "Lien entre differences divisees et derivee :",
            "options": [
                "Aucun",
                "$f[x_0, x_1] \\to f'(x_0)$ quand $x_1 \\to x_0$",
                "$f[x_0, x_1] = f''(x_0)$",
                "Inversement proportionnels",
            ],
            "correct_answer": "$f[x_0, x_1] \\to f'(x_0)$ quand $x_1 \\to x_0$",
            "explanation": "La difference divisee $f[x_0, x_1] = (f(x_1) - f(x_0))/(x_1 - x_0)$ est exactement le taux d'accroissement, ou la 'pente' de la corde entre les deux points. Quand $x_1$ se rapproche de $x_0$, ce rapport converge vers $f'(x_0)$ par definition de la derivee : $f'(x_0) = \lim_{h \to 0} (f(x_0+h) - f(x_0))/h$. C'est ce lien qui fait des differences divisees l'analogue discret des derivees, et qui justifie leur usage dans les schemas de differences finies.",
        },
    ],
    "concept_newton_interpolation": [
        {
            "question": "L'avantage principal de l'interpolation de Newton par rapport a Lagrange :",
            "options": [
                "Plus precise mathematiquement",
                "Forme incrementale (ajouter un point ne refait pas tout le calcul)",
                "Pas besoin de table de differences",
                "Fonctionne uniquement avec des points equidistants",
            ],
            "correct_answer": "Forme incrementale (ajouter un point ne refait pas tout le calcul)",
            "explanation": "Le polynome de Newton se construit progressivement : $p_n(x) = p_{n-1}(x) + f[x_0,...,x_n] \prod_{i=0}^{n-1}(x-x_i)$. Quand un nouveau point $(x_{n+1}, y_{n+1})$ arrive, on calcule juste la nouvelle difference divisee et on ajoute UN terme. Avec Lagrange, chaque polynome de base $L_i$ depend de TOUS les autres points, donc l'ajout d'un point oblige a tout recalculer. Newton est donc preferable quand les donnees arrivent en flux.",
        },
        {
            "question": "Pour interpoler 3 points avec Newton, combien de differences divisees calcule-t-on ?",
            "options": [
                "1 seule (l'ordre 0)",
                "3 (ordres 0, 1, 2)",
                "9 (table complete)",
                "Aucune",
            ],
            "correct_answer": "3 (ordres 0, 1, 2)",
            "explanation": "$f[x_0]$, $f[x_0, x_1]$ et $f[x_0, x_1, x_2]$ comme coefficients.",
        },
        {
            "question": "La forme generale du polynome de Newton est :",
            "options": [
                "$p(x) = \\sum_{i=0}^n f[x_0,...,x_i] \\prod_{j=0}^{i-1}(x - x_j)$",
                "$p(x) = \\sum_{i=0}^n y_i x^i$",
                "$p(x) = \\sum_{i=0}^n y_i L_i(x)$",
                "$p(x) = \\prod_{i=0}^n (x - x_i)$",
            ],
            "correct_answer": "$p(x) = \\sum_{i=0}^n f[x_0,...,x_i] \\prod_{j=0}^{i-1}(x - x_j)$",
            "explanation": "Forme \"differences progressives\" du polynome de Newton.",
        },
        {
            "question": "L'interpolation de Newton et de Lagrange donnent :",
            "options": [
                "Des polynomes differents",
                "Le meme polynome (formes equivalentes)",
                "Newton est toujours superieur",
                "Lagrange ne fonctionne qu'en 1D",
            ],
            "correct_answer": "Le meme polynome (formes equivalentes)",
            "explanation": "Le theoreme d'unicite garantit que pour des points $x_i$ tous distincts, il existe un seul polynome de degre $\le n$ qui passe par ces $n+1$ points. Lagrange et Newton sont juste deux ECRITURES differentes de CE MEME polynome unique. Si on les developpe et regroupe les termes, on tombe exactement sur les memes coefficients dans la base canonique $\{1, x, x^2, ...\}$.",
        },
        {
            "question": "Newton est plus efficace que Lagrange quand :",
            "options": [
                "On a beaucoup de points equidistants",
                "On veut ajouter des points dynamiquement",
                "On evalue en un seul point",
                "Jamais",
            ],
            "correct_answer": "On veut ajouter des points dynamiquement",
            "explanation": "Newton est particulierement utile pour des applications iteratives : raffinement progressif d'une approximation, mesures qui arrivent en flux (capteurs), ou tout scenario ou on veut estimer une approximation puis la raffiner. La formule de Newton permet de PARTIR du polynome existant et d'ajouter un terme correctif sans recalculer les anciens coefficients. Lagrange, lui, est plus adapte quand le set de points est fixe et qu'on doit juste evaluer le polynome.",
        },
    ],
    "concept_spline_interpolation": [
        {
            "question": "Une spline cubique est :",
            "options": [
                "Un polynome de degre 3 sur tout l'intervalle",
                "Un assemblage de polynomes de degre 3 par morceaux",
                "Une fonction trigonometrique",
                "Un polynome de Lagrange a 4 points",
            ],
            "correct_answer": "Un assemblage de polynomes de degre 3 par morceaux",
            "explanation": "Une spline cubique est une fonction definie par MORCEAUX : sur chaque intervalle $[x_i, x_{i+1}]$, on definit un polynome cubique $s_i(x)$. Aux jonctions $x_i$ (les 'noeuds'), on impose la continuite de $s$, $s'$ et $s''$ : c'est ce qu'on appelle la classe $C^2$. Resultat : une courbe lisse sans cassure visible, ideale pour l'animation, le design (Photoshop, AutoCAD), et l'interpolation de donnees experimentales.",
        },
        {
            "question": "Le phenomene de Runge se manifeste quand :",
            "options": [
                "Les splines convergent trop vite",
                "Un polynome interpolateur global de haut degre oscille fortement aux extremites",
                "L'integration numerique diverge",
                "La descente de gradient s'arrete prematurement",
            ],
            "correct_answer": "Un polynome interpolateur global de haut degre oscille fortement aux extremites",
            "explanation": "Avec des points equidistants et un grand $n$, le polynome interpolateur explose aux bords.",
        },
        {
            "question": "Une spline cubique naturelle impose comme condition aux bords :",
            "options": [
                "$s'(a) = s'(b) = 0$",
                "$s''(a) = s''(b) = 0$",
                "$s(a) = s(b) = 0$",
                "Aucune condition",
            ],
            "correct_answer": "$s''(a) = s''(b) = 0$",
            "explanation": "Une spline cubique sur $n$ intervalles a $4n$ coefficients (4 par cubique). Les conditions de continuite et de derivabilite aux noeuds donnent $4n - 2$ equations ; il manque 2 conditions pour fermer le systeme. Les splines NATURELLES imposent $s''(a) = s''(b) = 0$ aux bords (analogue physique : pas de moment flexion aux extremites d'une regle souple). D'autres choix existent : splines clamped ($s'$ donnee aux bords) ou periodiques ($s$, $s'$, $s''$ identiques aux 2 bords).",
        },
        {
            "question": "Continuite minimale d'une spline cubique :",
            "options": ["$C^0$", "$C^1$", "$C^2$", "$C^3$"],
            "correct_answer": "$C^2$",
            "explanation": "$C^2$ signifie 'differentiable 2 fois avec derivee seconde continue'. Pour une spline cubique, on impose explicitement : (1) $s_i(x_{i+1}) = s_{i+1}(x_{i+1})$ (continuite $C^0$), (2) $s_i'(x_{i+1}) = s_{i+1}'(x_{i+1})$ (continuite des tangentes), (3) $s_i''(x_{i+1}) = s_{i+1}''(x_{i+1})$ (continuite des courbures). C'est cette regularite qui rend les splines visuellement lisses.",
        },
        {
            "question": "Avantage des splines vs interpolation polynomiale globale :",
            "options": [
                "Plus rapide a calculer",
                "Evite les oscillations (Runge), bonne approximation locale",
                "Plus precise sur tout l'intervalle",
                "Plus simple a implementer",
            ],
            "correct_answer": "Evite les oscillations (Runge), bonne approximation locale",
            "explanation": "Le phenomene de Runge montre qu'un polynome global de haut degre est instable. Les splines resolvent ce probleme en utilisant des polynomes de petit degre (3 dans le cas cubique), chacun valable seulement sur un petit intervalle. L'erreur locale reste bornee partout, et la qualite de l'approximation s'AMELIORE quand on ajoute des points (contrairement au polynome global qui se DEGRADE). C'est pourquoi splines sont l'outil par defaut pour l'interpolation de donnees experimentales.",
        },
    ],

    # ─── MODULE 2 : INTEGRATION NUMERIQUE ────────────────
    "concept_riemann_sums": [
        {
            "question": "Une somme de Riemann approxime l'integrale d'une fonction par :",
            "options": [
                "Une somme de rectangles",
                "Une somme de triangles",
                "Un developpement de Taylor",
                "Une serie de Fourier",
            ],
            "correct_answer": "Une somme de rectangles",
            "explanation": "On decoupe l'intervalle $[a,b]$ en $n$ sous-intervalles et on remplace l'aire reelle par la somme des aires de rectangles $\\sum_i f(x_i^*) \\Delta x_i$. C'est l'idee fondatrice de l'integrale : approcher une aire courbe par un assemblage de rectangles. Plus $\\Delta x \\to 0$, meilleure est l'approximation, jusqu'a la limite qui est l'integrale exacte.",
        },
        {
            "question": "Une somme de Riemann a droite (right Riemann sum) utilise :",
            "options": [
                "$f$ evalue au debut de chaque sous-intervalle",
                "$f$ evalue a la fin de chaque sous-intervalle",
                "$f$ evalue au milieu",
                "La moyenne de $f$ sur l'intervalle",
            ],
            "correct_answer": "$f$ evalue a la fin de chaque sous-intervalle",
            "explanation": "La somme de Riemann a droite evalue $f$ a l'extremite droite de chaque sous-intervalle, soit $f(x_{i+1})$ sur $[x_i, x_{i+1}]$. Visuellement, le rectangle a pour hauteur la valeur de $f$ a son bord droit. Pour une fonction croissante, cela donne une SURESTIMATION ; pour une decroissante, une SOUS-ESTIMATION : c'est l'inverse de la somme a gauche.",
        },
        {
            "question": "La somme de Riemann milieu utilise :",
            "options": [
                "$f$ evaluee aux extremites",
                "$f$ evaluee au milieu de chaque sous-intervalle",
                "La moyenne des extremites",
                "$f^2$ aux extremites",
            ],
            "correct_answer": "$f$ evaluee au milieu de chaque sous-intervalle",
            "explanation": "La regle du milieu evalue $f$ au CENTRE de chaque sous-intervalle, $f((x_i + x_{i+1})/2)$. Geometriquement, l'erreur de surestimation d'un cote du rectangle compense partiellement la sous-estimation de l'autre cote. Resultat : l'erreur est en $O(h^2)$ contre $O(h)$ pour les sommes a gauche/droite — deux fois meilleur en ordre de convergence.",
        },
        {
            "question": "Une somme de Riemann CONVERGE vers l'integrale exacte si :",
            "options": [
                "$\\Delta x \\to 0$ (ou $n \\to \\infty$)",
                "$\\Delta x \\to \\infty$",
                "$n$ est pair",
                "$f$ est positive",
            ],
            "correct_answer": "$\\Delta x \\to 0$ (ou $n \\to \\infty$)",
            "explanation": "Par definition, l'integrale $\\int_a^b f(x)\\,dx$ est la LIMITE des sommes de Riemann quand le pas $\\Delta x \\to 0$ (ou $n \\to \\infty$). C'est le passage du discret au continu : on raffine indefiniment le decoupage jusqu'a ce que les rectangles epousent parfaitement la courbe. Cette convergence est garantie pour toute fonction Riemann-integrable (continue par morceaux et bornee).",
        },
        {
            "question": "L'erreur d'une somme de Riemann (left/right) sur fonction lipschitzienne est en :",
            "options": ["$O(1)$", "$O(h)$", "$O(h^2)$", "$O(h^3)$"],
            "correct_answer": "$O(h)$",
            "explanation": "Pour une fonction lipschitzienne (donc continue avec derivee bornee), l'erreur des sommes a gauche/droite est en $O(h)$ ou $h = (b-a)/n$ : doubler le nombre de points divise l'erreur par 2. Les schemas plus malins comme la regle du milieu et les trapezes atteignent $O(h^2)$ : doubler $n$ divise l'erreur par 4. C'est pourquoi en pratique on n'utilise quasiment jamais Riemann gauche/droite hors enseignement.",
        },
    ],
    "concept_definite_integrals": [
        {
            "question": "L'integrale definie $\\int_a^b f(x) dx$ represente geometriquement :",
            "options": [
                "La pente de $f$ en $x = a$",
                "L'aire algebrique sous la courbe entre $a$ et $b$",
                "La valeur maximum de $f$ sur $[a, b]$",
                "La derivee seconde de $F$",
            ],
            "correct_answer": "L'aire algebrique sous la courbe entre $a$ et $b$",
            "explanation": "Geometriquement, $\\int_a^b f(x)\\,dx$ est l'aire ALGEBRIQUE comprise entre la courbe $y=f(x)$ et l'axe des abscisses, entre $x=a$ et $x=b$. Quand $f \\ge 0$, c'est l'aire usuelle ; quand $f \\le 0$, l'integrale est NEGATIVE (l'aire est comptee avec un signe). C'est cette signature qui permet, par exemple, a une integrale de cosinus sur une periode complete d'etre nulle.",
        },
        {
            "question": "Le theoreme fondamental du calcul dit que $\\int_a^b f(x) dx$ vaut :",
            "options": [
                "$F(a) - F(b)$",
                "$F(b) - F(a)$ ou $F$ est une primitive de $f$",
                "$f(b) - f(a)$",
                "$f'(b) - f'(a)$",
            ],
            "correct_answer": "$F(b) - F(a)$ ou $F$ est une primitive de $f$",
            "explanation": "Le theoreme fondamental du calcul etablit que derivation et integration sont des operations INVERSES : si $F'(x) = f(x)$ alors $\\int_a^b f(x)\\,dx = F(b) - F(a)$. Cela transforme un calcul d'aire (a priori difficile) en un simple calcul de difference de primitive. C'est la cle qui rend pratique la majorite des integrales analytiques (polynomes, exp, log, trig).",
        },
        {
            "question": "La propriete de linearite de l'integrale dit :",
            "options": [
                "$\\int (f + g) = \\int f \\cdot \\int g$",
                "$\\int (\\alpha f + \\beta g) = \\alpha \\int f + \\beta \\int g$",
                "$\\int (f \\cdot g) = \\int f + \\int g$",
                "$\\int f^2 = (\\int f)^2$",
            ],
            "correct_answer": "$\\int (\\alpha f + \\beta g) = \\alpha \\int f + \\beta \\int g$",
            "explanation": "L'operateur d'integration est LINEAIRE : pour toutes constantes $\\alpha, \\beta$ et fonctions integrables $f, g$, on a $\\int (\\alpha f + \\beta g) = \\alpha \\int f + \\beta \\int g$. Cette propriete decoule directement de la linearite des sommes de Riemann. En pratique, elle permet de decomposer une integrale compliquee en somme d'integrales plus simples — un outil de base utilise constamment.",
        },
        {
            "question": "$\\int_a^a f(x) dx$ vaut :",
            "options": ["$f(a)$", "$0$", "$\\infty$", "Indefini"],
            "correct_answer": "$0$",
            "explanation": "Sur l'intervalle $[a, a]$ de longueur nulle, peu importe la fonction, il n'y a aucune aire a comptabiliser : $\\int_a^a f(x)\\,dx = 0$. C'est aussi une consequence directe du theoreme fondamental : $F(a) - F(a) = 0$. Cette convention est essentielle pour faire fonctionner la relation de Chasles $\\int_a^c = \\int_a^b + \\int_b^c$ meme quand $b = a$ ou $b = c$.",
        },
        {
            "question": "Si $f \\ge 0$ sur $[a, b]$ et $\\int_a^b f = 0$, alors :",
            "options": [
                "$f$ est strictement positive",
                "$f$ est nulle presque partout sur $[a, b]$",
                "$f(a) = f(b) = 0$ uniquement",
                "$f$ est constante",
            ],
            "correct_answer": "$f$ est nulle presque partout sur $[a, b]$",
            "explanation": "Si $f \\ge 0$ sur $[a,b]$ et que $\\int_a^b f = 0$, alors $f$ est nulle PRESQUE PARTOUT (sauf eventuellement sur un ensemble de mesure nulle, comme un nombre fini de points). Intuitivement : aucune aire ne peut s'accumuler sans que la fonction prenne des valeurs strictement positives sur un ensemble de longueur strictement positive. Si en plus $f$ est continue, alors $f \\equiv 0$ partout.",
        },
    ],
    "concept_trapezoidal": [
        {
            "question": "La methode des trapezes approche $f$ sur chaque sous-intervalle par :",
            "options": ["Une constante", "Une droite", "Une parabole", "Un polynome de degre 3"],
            "correct_answer": "Une droite",
            "explanation": "Sur chaque sous-intervalle $[x_i, x_{i+1}]$, la methode des trapezes remplace la courbe par le SEGMENT DE DROITE reliant $(x_i, f(x_i))$ a $(x_{i+1}, f(x_{i+1}))$. L'aire sous ce segment forme un trapeze rectangle dont l'aire vaut $\\frac{h}{2}(f(x_i) + f(x_{i+1}))$. C'est exactement l'interpolation lineaire de $f$ aux deux bornes, integree analytiquement.",
        },
        {
            "question": "L'erreur de la methode des trapezes composee sur $n$ sous-intervalles est en :",
            "options": ["$O(h)$", "$O(h^2)$", "$O(h^4)$", "$O(1)$"],
            "correct_answer": "$O(h^2)$",
            "explanation": "L'erreur de la methode des trapezes composee est $E = -\\frac{(b-a)h^2}{12}\\,f''(\\xi)$ pour un certain $\\xi \\in [a,b]$, donc en $O(h^2)$. Concretement : doubler le nombre de sous-intervalles divise l'erreur par 4. C'est un GROS progres par rapport a Riemann en $O(h)$, mais reste insuffisant pour des fonctions lisses ou Simpson en $O(h^4)$ ou Gauss font beaucoup mieux.",
        },
        {
            "question": "Formule du trapeze simple sur $[a, b]$ :",
            "options": [
                "$\\frac{b-a}{2} (f(a) + f(b))$",
                "$\\frac{b-a}{6} (f(a) + 4 f(m) + f(b))$",
                "$(b-a) \\cdot f(\\frac{a+b}{2})$",
                "$\\sum f(x_i) (x_i - x_{i-1})$",
            ],
            "correct_answer": "$\\frac{b-a}{2} (f(a) + f(b))$",
            "explanation": "Un trapeze rectangle de base $b-a$ et de hauteurs $f(a)$ et $f(b)$ a pour aire $\\frac{(b-a)}{2}(f(a) + f(b))$ — c'est la formule classique d'aire du trapeze appliquee a la geometrie sous la courbe. Dans la version composee, on additionne les aires de tous les petits trapezes : les valeurs interieures apparaissent deux fois (fin d'un trapeze = debut du suivant), d'ou la formule $h\\bigl(\\frac{f(x_0)+f(x_n)}{2} + \\sum_{i=1}^{n-1} f(x_i)\\bigr)$.",
        },
        {
            "question": "Pour $f$ concave, la methode des trapezes :",
            "options": [
                "Surestime l'integrale",
                "Sous-estime l'integrale",
                "Donne la valeur exacte",
                "Diverge",
            ],
            "correct_answer": "Sous-estime l'integrale",
            "explanation": "Pour une fonction CONCAVE, par definition la corde reliant deux points de la courbe est SOUS la courbe — donc l'aire du trapeze (sous la corde) est inferieure a l'aire reelle (sous la courbe). Resultat : la methode des trapezes SOUS-ESTIME l'integrale. Pour une fonction CONVEXE (comme $x^2$), c'est l'inverse : surestimation. Cette analyse de signe d'erreur, basee sur la convexite, permet d'encadrer l'integrale exacte entre deux methodes.",
        },
        {
            "question": "Methode des trapezes : exacte pour quels polynomes ?",
            "options": [
                "Constants seulement",
                "De degre $\\le 1$",
                "De degre $\\le 2$",
                "De tout degre",
            ],
            "correct_answer": "De degre $\\le 1$",
            "explanation": "Comme la methode interpole $f$ par un polynome de DEGRE 1 (une droite passant par les deux extremites), elle est EXACTE des que $f$ est elle-meme affine — sur une droite, il n'y a aucune erreur d'interpolation. Pour un polynome de degre 2 ou plus, la corde s'ecarte de la courbe et l'erreur apparait. On dit que les trapezes ont un DEGRE DE PRECISION egal a 1.",
        },
    ],
    "concept_simpson": [
        {
            "question": "La regle de Simpson approche $f$ sur chaque paire de sous-intervalles par :",
            "options": ["Une droite", "Une parabole", "Une constante", "Une exponentielle"],
            "correct_answer": "Une parabole",
            "explanation": "La regle de Simpson regroupe les sous-intervalles par PAIRES et fait passer une parabole (polynome de degre 2) par les 3 points consecutifs $(x_i, f(x_i)), (x_{i+1}, f(x_{i+1})), (x_{i+2}, f(x_{i+2}))$. L'integrale de cette parabole sur $[x_i, x_{i+2}]$ s'ecrit analytiquement et donne $\\frac{h}{3}(f_i + 4f_{i+1} + f_{i+2})$. C'est plus precis que les trapezes (droites) car une parabole epouse mieux les courbes lisses.",
        },
        {
            "question": "La methode de Simpson composee necessite un nombre de sous-intervalles :",
            "options": ["Pair", "Impair", "Premier", "Quelconque"],
            "correct_answer": "Pair",
            "explanation": "Chaque parabole de Simpson couvre EXACTEMENT 2 sous-intervalles (3 points). Si $n$ est impair, il reste un sous-intervalle solitaire qu'aucune parabole ne couvre proprement. C'est pourquoi on impose $n$ PAIR. En pratique, si on doit traiter $n$ impair, on bascule sur Simpson 3/8 (qui utilise 4 points) pour les 3 derniers sous-intervalles — c'est la regle de Simpson 1/3 + 3/8 combinee.",
        },
        {
            "question": "Erreur de Simpson composee :",
            "options": ["$O(h)$", "$O(h^2)$", "$O(h^4)$", "$O(h^5)$"],
            "correct_answer": "$O(h^4)$",
            "explanation": "L'erreur de Simpson composee est $E = -\\frac{(b-a)h^4}{180}\\,f^{(4)}(\\xi)$, donc en $O(h^4)$. En pratique, doubler $n$ divise l'erreur par 16 (vs par 4 pour les trapezes). Pour atteindre une meme precision que les trapezes, Simpson a besoin de bien moins de points : c'est l'algorithme par defaut pour les integrations de routine en ingenierie quand la fonction n'est pas tres oscillante.",
        },
        {
            "question": "Formule de Simpson 1/3 simple sur $[a, b]$ avec $m = (a+b)/2$ :",
            "options": [
                "$\\frac{b-a}{6} (f(a) + 4 f(m) + f(b))$",
                "$\\frac{b-a}{2} (f(a) + f(b))$",
                "$(b-a) \\cdot f(m)$",
                "$\\frac{b-a}{3} (f(a) + f(b) + f(m))$",
            ],
            "correct_answer": "$\\frac{b-a}{6} (f(a) + 4 f(m) + f(b))$",
            "explanation": "La formule simple de Simpson 1/3 sur $[a,b]$ avec milieu $m=(a+b)/2$ est $\\frac{b-a}{6}(f(a) + 4f(m) + f(b))$. Le coefficient 4 sur le milieu, 1 aux extremites, et le facteur $1/6$ proviennent de l'integration analytique du polynome de Lagrange de degre 2 passant par les 3 points. Ces poids $(1, 4, 1)/6$ sont une signature universelle de Simpson 1/3.",
        },
        {
            "question": "Simpson est exacte pour les polynomes de degre :",
            "options": ["$\\le 1$", "$\\le 2$", "$\\le 3$", "$\\le 4$"],
            "correct_answer": "$\\le 3$",
            "explanation": "Bien que Simpson interpole avec une PARABOLE (degre 2), elle est exacte aussi pour les CUBIQUES (degre 3) — un 'bonus' inattendu. Cela vient de la symetrie autour du milieu : pour un polynome impair par rapport a $m$, l'erreur d'interpolation au-dessus annule celle en-dessous lors de l'integration. C'est pourquoi le degre de precision de Simpson est 3 et non 2 — et pourquoi son erreur depend de $f^{(4)}$ et pas de $f^{(3)}$.",
        },
    ],
    "concept_gaussian_quadrature": [
        {
            "question": "L'avantage de la quadrature de Gauss-Legendre :",
            "options": [
                "Elle utilise des points equidistants",
                "Elle est exacte pour les polynomes jusqu'a un degre eleve avec peu de points",
                "Elle est plus simple a implementer que les trapezes",
                "Elle fonctionne uniquement sur $[0,1]$",
            ],
            "correct_answer": "Elle est exacte pour les polynomes jusqu'a un degre eleve avec peu de points",
            "explanation": "Avec seulement $n$ points soigneusement choisis (les noeuds de Gauss), la quadrature integre EXACTEMENT tout polynome de degre $\\le 2n-1$ : c'est le double du degre realisable avec des points imposes (Newton-Cotes). Par exemple : 3 points Gauss = exact jusqu'au degre 5, alors que Simpson (3 points equidistants) plafonne au degre 3. Ce gain provient de l'optimisation simultanee des positions ET des poids.",
        },
        {
            "question": "Les noeuds de Gauss-Legendre sur $[-1, 1]$ sont :",
            "options": [
                "Equidistants",
                "Les racines des polynomes de Legendre",
                "Les racines de $\\cos(\\pi x)$",
                "Les entiers de $-1$ a $1$",
            ],
            "correct_answer": "Les racines des polynomes de Legendre",
            "explanation": "Pour $w(x)=1$ sur $[-1,1]$, les noeuds optimaux sont les ZEROS du polynome de Legendre $P_n$. Cette caracterisation provient de la theorie des polynomes orthogonaux : $P_n$ est orthogonal a tout polynome de degre $< n$ pour le produit scalaire $\\int_{-1}^1 fg$. Pour d'autres poids, on utilise d'autres familles : Tchebychev pour $1/\\sqrt{1-x^2}$, Hermite pour $e^{-x^2}$, Laguerre pour $e^{-x}$ sur $[0,\\infty)$.",
        },
        {
            "question": "Avec 3 points de Gauss, on integre exactement les polynomes de degre :",
            "options": ["$\\le 2$", "$\\le 3$", "$\\le 5$", "$\\le 6$"],
            "correct_answer": "$\\le 5$",
            "explanation": "Avec $n=3$ noeuds de Gauss-Legendre (les zeros de $P_3$), la formule integre exactement tout polynome de degre $\\le 2 \\cdot 3 - 1 = 5$. A titre de comparaison, Simpson avec 3 points n'atteint que le degre 3. C'est pourquoi Gauss devient incontournable des qu'on a une fonction couteuse a evaluer (simulations physiques, integrales en plusieurs dimensions) : moins d'evaluations pour la meme precision.",
        },
        {
            "question": "Pour integrer sur $[a, b]$ avec Gauss-Legendre, on :",
            "options": [
                "Ne peut pas, c'est seulement sur $[-1, 1]$",
                "Fait un changement de variable affine vers $[-1, 1]$",
                "Approche par developpement de Taylor",
                "Multiplie par $b-a$",
            ],
            "correct_answer": "Fait un changement de variable affine vers $[-1, 1]$",
            "explanation": "Gauss-Legendre est tabule sur $[-1, 1]$. Pour integrer sur $[a, b]$, on fait le CHANGEMENT DE VARIABLE affine $x = \\frac{b-a}{2} t + \\frac{a+b}{2}$ avec $dx = \\frac{b-a}{2}\\,dt$ : ainsi $\\int_a^b f(x)\\,dx = \\frac{b-a}{2}\\int_{-1}^1 f\\bigl(\\frac{b-a}{2}t + \\frac{a+b}{2}\\bigr)\\,dt$. On applique alors la formule standard avec les noeuds $t_i$ et poids $w_i$ tabules.",
        },
        {
            "question": "Gauss vs Simpson : pour la meme precision,",
            "options": [
                "Simpson est toujours plus rapide",
                "Gauss necessite moins de points",
                "Ils sont equivalents",
                "Simpson n'a pas d'erreur",
            ],
            "correct_answer": "Gauss necessite moins de points",
            "explanation": "A nombre d'evaluations egal, Gauss atteint un degre de precision DOUBLE par rapport a Simpson : 3 points Gauss = degre 5 vs Simpson = degre 3. En pratique, pour atteindre une meme tolerance, Gauss demande typiquement 2 a 3 fois moins d'evaluations de $f$. C'est l'algorithme dominant des qu'evaluer $f$ est couteux : simulations CFD, calculs d'elements finis, integrales multidimensionnelles dans un solveur.",
        },
    ],

    # ─── MODULE 3 : APPROXIMATION & OPTIMISATION ─────────
    "concept_least_squares": [
        {
            "question": "La methode des moindres carres minimise :",
            "options": [
                "L'erreur maximale",
                "La somme des erreurs absolues",
                "La somme des carres des erreurs",
                "L'erreur mediane",
            ],
            "correct_answer": "La somme des carres des erreurs",
            "explanation": "Les moindres carres minimisent la somme des CARRES des residus $\\sum_i (y_i - p(x_i))^2$. Le choix du carre n'est pas neutre : il pondere fortement les grandes erreurs (1 erreur de 10 = 100, vs 10 erreurs de 1 = 10), et surtout sa derivee est lineaire en les coefficients, ce qui donne un systeme LINEAIRE (les equations normales). C'est cette tractabilite analytique qui a fait son succes (Gauss, 1809).",
        },
        {
            "question": "Les equations normales du moindres carres pour $Ax = b$ s'ecrivent :",
            "options": [
                "$A^T A\\, x = A^T b$",
                "Une equation differentielle",
                "Une integrale",
                "Une serie infinie",
            ],
            "correct_answer": "$A^T A\\, x = A^T b$",
            "explanation": "En posant le probleme sous forme matricielle $\\min_x \\|Ax - b\\|_2^2$ et en derivant par rapport a $x$, on obtient les EQUATIONS NORMALES $A^T A\\,x = A^T b$. La matrice $A^T A$ est carree, symetrique et semi-definie positive : on peut la factoriser par Cholesky pour resoudre efficacement. Geometriquement, $Ax^*$ est la PROJECTION ORTHOGONALE de $b$ sur le sous-espace image de $A$.",
        },
        {
            "question": "Pourquoi minimiser des CARRES plutot que des valeurs absolues ?",
            "options": [
                "C'est plus precis",
                "On obtient un systeme lineaire (calculs propres)",
                "C'est moins sensible aux outliers",
                "Les carres sont toujours positifs",
            ],
            "correct_answer": "On obtient un systeme lineaire (calculs propres)",
            "explanation": "Le carre $u^2$ a pour derivee $2u$ : LINEAIRE. La somme $\\sum (y_i - p(x_i))^2$ derivee par rapport aux coefficients donne donc un systeme lineaire — simple, direct, unique solution. Avec la valeur absolue $|u|$, la derivee est $\\pm 1$ (non lisse en 0) : cela mene a un probleme de programmation lineaire (regression LAD) plus robuste aux outliers mais sans formule fermee. Les moindres carres trichent en quelque sorte : ils sont CALCULABLEMENT simples au prix d'une sensibilite aux valeurs aberrantes.",
        },
        {
            "question": "Pour eviter les problemes de conditionnement de $A^T A$, on prefere :",
            "options": [
                "La methode QR ou SVD",
                "Inverser $A^T A$ a la main",
                "Utiliser plus de points",
                "Reduire le degre du polynome",
            ],
            "correct_answer": "La methode QR ou SVD",
            "explanation": "Construire $A^T A$ ECARTE le conditionnement : $\\kappa(A^T A) = \\kappa(A)^2$. Si $A$ est mal conditionnee ($\\kappa = 10^4$), alors $A^T A$ devient catastrophique ($\\kappa = 10^8$) et la solution numerique perd de la precision. La decomposition QR ($A = QR$ avec $Q$ orthogonale) ou la SVD ($A = U\\Sigma V^T$) resolvent le probleme directement sur $A$, sans former $A^T A$, et restent stables meme pour des matrices proches de la rang-deficience.",
        },
        {
            "question": "Les moindres carres sont le **meilleur estimateur** au sens de :",
            "options": [
                "Une norme quelconque",
                "La norme $L^2$ (euclidienne)",
                "La norme $L^\\infty$",
                "La norme $L^1$",
            ],
            "correct_answer": "La norme $L^2$ (euclidienne)",
            "explanation": "Les moindres carres minimisent specifiquement la norme $L^2$ (euclidienne) du vecteur d'erreur. Pour la norme $L^1$ (somme des valeurs absolues), on parle de regression LAD — plus robuste aux outliers. Pour la norme $L^\\infty$ (erreur maximale), c'est le minimax / Tchebychev — utile en design de filtres ou en approximation de fonctions. Chaque norme correspond a une intuition statistique differente : $L^2$ suppose un bruit gaussien.",
        },
    ],
    "concept_orthogonal_polynomials": [
        {
            "question": "Les polynomes orthogonaux (Legendre, Tchebychev) sont surtout utilises pour :",
            "options": [
                "Resoudre des equations differentielles uniquement",
                "Faciliter l'approximation et la quadrature",
                "Calculer des derivees",
                "Tracer des courbes en 3D",
            ],
            "correct_answer": "Faciliter l'approximation et la quadrature",
            "explanation": "Une famille $\\{P_0, P_1, ...\\}$ est ORTHOGONALE pour le produit scalaire $\\langle f, g\\rangle = \\int_a^b f(x)g(x)w(x)\\,dx$ si $\\langle P_i, P_j\\rangle = 0$ pour $i \\ne j$. Cela rend les coefficients d'une projection $f \\approx \\sum c_i P_i$ INDEPENDANTS : chaque $c_i = \\langle f, P_i\\rangle / \\langle P_i, P_i\\rangle$ se calcule isolement, sans systeme lineaire couple. C'est aussi la cle de la quadrature de Gauss et de la stabilite numerique des bases polynomiales.",
        },
        {
            "question": "Sur $[-1, 1]$ avec poids $w(x) = 1$, les polynomes orthogonaux sont ceux de :",
            "options": ["Tchebychev de 1ere espece", "Legendre", "Hermite", "Laguerre"],
            "correct_answer": "Legendre",
            "explanation": "Sur $[-1, 1]$ avec POIDS UNIFORME $w(x) = 1$, les polynomes orthogonaux sont ceux de Legendre $P_n$. Avec un poids different, on obtient une autre famille : $w(x) = 1/\\sqrt{1-x^2}$ donne les Tchebychev $T_n$ (lies aux cosinus), $w(x) = e^{-x^2}$ sur $\\mathbb{R}$ donne les Hermite (mecanique quantique), $w(x) = e^{-x}$ sur $[0,\\infty)$ donne les Laguerre (theorie des files d'attente). Le poids encode 'quelle region de l'intervalle on veut bien approximer'.",
        },
        {
            "question": "Combien de zeros distincts a un polynome de degre $n$ d'une famille orthogonale ?",
            "options": ["0", "$n-1$", "Exactement $n$ dans l'intervalle", "Infini"],
            "correct_answer": "Exactement $n$ dans l'intervalle",
            "explanation": "Theoreme classique : les $n$ zeros d'un polynome orthogonal $P_n$ sont tous REELS, SIMPLES (multiplicite 1), et tous strictement DANS l'intervalle d'orthogonalite $(a, b)$. Cette propriete est cruciale pour la quadrature de Gauss : on est sur que les noeuds tombent toujours dans le domaine d'integration. Elle entraine aussi le phenomene d'entrelacement : entre deux zeros consecutifs de $P_{n+1}$ se trouve toujours exactement un zero de $P_n$.",
        },
        {
            "question": "$T_n(\\cos\\theta) =$ pour Tchebychev :",
            "options": ["$\\cos(n\\theta)$", "$\\sin(n\\theta)$", "$n\\cos\\theta$", "$\\theta^n$"],
            "correct_answer": "$\\cos(n\\theta)$",
            "explanation": "Les polynomes de Tchebychev de premiere espece $T_n$ ont une definition trigonometrique remarquable : $T_n(\\cos\\theta) = \\cos(n\\theta)$. Cela explique pourquoi $T_n$ oscille entre $-1$ et $+1$ sur $[-1,1]$ avec exactement $n+1$ extremums, et pourquoi ses zeros (les noeuds de Tchebychev) sont $\\cos\\bigl(\\frac{(2k-1)\\pi}{2n}\\bigr)$. C'est aussi cette propriete qui les rend optimaux pour l'approximation polynomiale au sens minimax.",
        },
        {
            "question": "Recurrence a 3 termes (Favard) : tous les polynomes orthogonaux verifient :",
            "options": [
                "$P_{n+1} = (\\alpha_n x + \\beta_n) P_n + \\gamma_n P_{n-1}$",
                "$P_{n+1} = P_n + P_{n-1}$",
                "$P_{n+1} = x \\cdot P_n$",
                "Aucune relation generale",
            ],
            "correct_answer": "$P_{n+1} = (\\alpha_n x + \\beta_n) P_n + \\gamma_n P_{n-1}$",
            "explanation": "Toute famille de polynomes orthogonaux satisfait une RECURRENCE A 3 TERMES de la forme $P_{n+1}(x) = (\\alpha_n x + \\beta_n) P_n(x) + \\gamma_n P_{n-1}(x)$. Le theoreme de Favard etablit la reciproque : toute famille satisfaisant une telle recurrence (avec $\\gamma_n < 0$) est orthogonale pour un certain produit scalaire. En pratique, cette recurrence permet de calculer $P_n$ rapidement sans developpement, et est a la base d'algorithmes numeriques stables pour evaluer la quadrature de Gauss.",
        },
    ],
    "concept_minimax_approximation": [
        {
            "question": "L'approximation minimax (Tchebychev) cherche a minimiser :",
            "options": [
                "La somme des carres des erreurs",
                "L'erreur maximale $\\|f - p\\|_\\infty$",
                "Le nombre de coefficients",
                "Le degre du polynome",
            ],
            "correct_answer": "L'erreur maximale $\\|f - p\\|_\\infty$",
            "explanation": "L'approximation minimax (ou de Tchebychev) minimise l'erreur MAXIMALE $\\|f - p\\|_\\infty = \\max_{x \\in [a,b]} |f(x) - p(x)|$, contrairement aux moindres carres qui minimisent une moyenne. Ce critere est crucial quand on a besoin d'une garantie POINT PAR POINT : l'erreur ne depasse jamais un certain seuil. C'est le cas en design de filtres numeriques, en synthese audio, en aerospatial — partout ou un pic d'erreur peut etre catastrophique.",
        },
        {
            "question": "Theoreme d'equi-oscillation : la meilleure approximation polynomiale de degre $n$ atteint son extremum en signe alterne :",
            "options": ["1 fois", "2 fois", "Au moins $n+2$ fois", "Jamais"],
            "correct_answer": "Au moins $n+2$ fois",
            "explanation": "Le theoreme d'EQUI-OSCILLATION de Tchebychev caracterise la meilleure approximation polynomiale de degre $n$ de $f$ : la fonction d'erreur $e(x) = f(x) - p^*(x)$ atteint son extremum $\\pm \\|e\\|_\\infty$ avec des SIGNES ALTERNES en au moins $n+2$ points distincts. Cette caracterisation fournit a la fois une condition necessaire ET suffisante d'optimalite, et c'est elle qu'exploite l'algorithme de Remez pour iterer vers la solution.",
        },
        {
            "question": "L'algorithme qui calcule numeriquement le polynome minimax s'appelle :",
            "options": ["Gauss-Newton", "Remez", "Romberg", "Adams-Bashforth"],
            "correct_answer": "Remez",
            "explanation": "L'algorithme de Remez (1934) construit iterativement le polynome minimax. A chaque iteration, on choisit $n+2$ points, on calcule le polynome qui equi-oscille sur ces points (systeme lineaire), puis on actualise les points en cherchant les extremums de l'erreur. La convergence est QUADRATIQUE : le nombre de chiffres exacts double a chaque iteration. C'est l'algorithme implemente dans les outils de design de filtres comme les Parks-McClellan.",
        },
        {
            "question": "Une approximation **proche** du minimax sans algorithme complexe est obtenue par :",
            "options": [
                "Interpolation aux noeuds equidistants",
                "Troncature de la serie de Tchebychev",
                "Moindres carres",
                "Differences finies",
            ],
            "correct_answer": "Troncature de la serie de Tchebychev",
            "explanation": "La SERIE TRONQUEE de Tchebychev $\\sum_{k=0}^n c_k T_k(x)$ est tres proche du polynome minimax exact — typiquement a quelques pourcents pres. Avantage : ses coefficients $c_k = \\frac{2}{\\pi}\\int_{-1}^1 \\frac{f(x)T_k(x)}{\\sqrt{1-x^2}}\\,dx$ se calculent par FFT sur les noeuds de Tchebychev, en $O(n \\log n)$, sans iteration. C'est l'astuce des bibliotheques d'approximation de fonctions speciales (Chebfun, etc.).",
        },
        {
            "question": "Pour interpoler $f$ par un polynome de degre $n$ avec une erreur proche du minimax, on choisit comme noeuds :",
            "options": [
                "Des points equidistants",
                "Les racines de $T_{n+1}$ (Tchebychev)",
                "Les entiers naturels",
                "Aleatoirement",
            ],
            "correct_answer": "Les racines de $T_{n+1}$ (Tchebychev)",
            "explanation": "L'erreur d'interpolation polynomiale contient un facteur $\\prod_i (x - x_i)$ : pour la minimiser au sens $L^\\infty$, il faut choisir les noeuds $x_i$ qui minimisent le sup de ce produit. Reponse mathematique : les ZEROS de $T_{n+1}$, soit $x_k = \\cos\\bigl(\\frac{(2k-1)\\pi}{2(n+1)}\\bigr)$. Ces points se concentrent pres des bords de l'intervalle, ce qui evite l'explosion oscillatoire du phenomene de Runge observee avec des noeuds equidistants.",
        },
    ],
    "concept_gradient_descent": [
        {
            "question": "La descente de gradient met a jour les parametres dans la direction :",
            "options": [
                "Du gradient (pour maximiser)",
                "Opposee au gradient (pour minimiser)",
                "Perpendiculaire au gradient",
                "Aleatoire",
            ],
            "correct_answer": "Opposee au gradient (pour minimiser)",
            "explanation": "Le gradient $\\nabla f$ pointe vers la direction de plus forte CROISSANCE de $f$. Pour MINIMISER, on se deplace dans la direction OPPOSEE $-\\nabla f$ : c'est l'idee fondatrice de la descente de gradient. Chaque pas est local : on n'utilise que l'information du premier ordre (la pente locale), pas la courbure. C'est le squelette de tous les algorithmes d'apprentissage en ML moderne (SGD, Adam, RMSprop).",
        },
        {
            "question": "Si le learning rate $\\eta$ est trop grand, la descente de gradient :",
            "options": [
                "Converge plus vite",
                "Risque de diverger ou d'osciller",
                "Trouve toujours le minimum global",
                "N'a aucun effet",
            ],
            "correct_answer": "Risque de diverger ou d'osciller",
            "explanation": "Si le pas $\\eta$ (learning rate) est TROP GRAND, on saute de l'autre cote du minimum a chaque iteration et l'algorithme oscille, voire diverge ($\\theta_k$ part a l'infini). S'il est TROP PETIT, la convergence est tres lente. En pratique, on calibre $\\eta$ par tatonnement (typiquement $10^{-3}$ a $10^{-1}$ en deep learning), ou on utilise des schedulers (decroissance, warmup) ou des optimiseurs adaptatifs comme Adam qui ajustent $\\eta$ par parametre.",
        },
        {
            "question": "Mise a jour de la descente de gradient :",
            "options": [
                "$\\theta_{k+1} = \\theta_k + \\eta \\nabla f(\\theta_k)$",
                "$\\theta_{k+1} = \\theta_k - \\eta \\nabla f(\\theta_k)$",
                "$\\theta_{k+1} = \\eta \\nabla f(\\theta_k)$",
                "$\\theta_{k+1} = \\theta_k - \\eta H \\theta_k$",
            ],
            "correct_answer": "$\\theta_{k+1} = \\theta_k - \\eta \\nabla f(\\theta_k)$",
            "explanation": "La regle de mise a jour de la descente de gradient est $\\theta_{k+1} = \\theta_k - \\eta\\,\\nabla f(\\theta_k)$. Le SIGNE MOINS est essentiel — c'est lui qui transforme la 'montee de gradient' (maximisation) en descente. Le coefficient $\\eta$ controle la TAILLE du pas. Cette formule simple sert de base a tous les variants : SGD (gradient sur mini-batch), Momentum (ajoute une inertie), Adam (taux par parametre).",
        },
        {
            "question": "Le gradient stochastique (SGD) :",
            "options": [
                "Calcule le gradient sur tout le dataset",
                "Calcule le gradient sur un mini-batch",
                "Ne calcule jamais de gradient",
                "Inverse une matrice",
            ],
            "correct_answer": "Calcule le gradient sur un mini-batch",
            "explanation": "Le SGD (Stochastic Gradient Descent) approxime le gradient sur un MINI-BATCH (typiquement 32 a 512 exemples) au lieu de l'ensemble du dataset. Avantages : (1) iterations beaucoup plus rapides, (2) le bruit stochastique aide a echapper aux minima locaux et points-selles. Inconvenient : le gradient est bruite donc la convergence n'est plus monotone. C'est la methode de fait pour entrainer les reseaux de neurones modernes ou un epoch complet sur des millions d'exemples serait inefficace.",
        },
        {
            "question": "Adam est un optimiseur qui :",
            "options": [
                "Adapte le learning rate par parametre",
                "Calcule la hessienne",
                "Inverse une matrice",
                "Ne fonctionne pas",
            ],
            "correct_answer": "Adapte le learning rate par parametre",
            "explanation": "Adam (Kingma & Ba, 2014) combine deux idees : (1) un MOMENT premier (moyenne mobile du gradient, comme momentum) qui amortit les oscillations, et (2) un MOMENT SECOND (moyenne des carres du gradient) qui adapte le learning rate par parametre — plus le gradient varie pour ce parametre, plus le pas effectif diminue. Resultat : convergence rapide et robuste sur la plupart des architectures profondes, sans avoir a regler finement $\\eta$. C'est l'optimiseur par defaut en deep learning.",
        },
    ],
    "concept_newton_optimization": [
        {
            "question": "La methode de Newton pour l'optimisation utilise :",
            "options": [
                "Seulement le gradient",
                "Le gradient et la matrice hessienne",
                "Seulement la fonction de cout",
                "La transformee de Fourier",
            ],
            "correct_answer": "Le gradient et la matrice hessienne",
            "explanation": "La methode de Newton pour l'optimisation utilise a la fois le GRADIENT $\\nabla f$ (information du premier ordre) ET la matrice HESSIENNE $H = \\nabla^2 f$ (courbure, second ordre). La regle de mise a jour est $\\theta_{k+1} = \\theta_k - H^{-1}\\,\\nabla f(\\theta_k)$ : on resout une approximation quadratique locale de $f$. Concretement, Newton prend en compte la 'forme du paysage' (vallee etroite, plateau) au lieu de juste regarder la pente.",
        },
        {
            "question": "Comparee a la descente de gradient, la methode de Newton :",
            "options": [
                "Converge plus lentement",
                "Converge plus vite pres de l'optimum mais coute plus par iteration",
                "Ne necessite aucun calcul de derivee",
                "Est exclusivement utilisee en cryptographie",
            ],
            "correct_answer": "Converge plus vite pres de l'optimum mais coute plus par iteration",
            "explanation": "Newton converge QUADRATIQUEMENT pres de l'optimum (le nombre de chiffres exacts double a chaque iteration), contre une convergence LINEAIRE pour la descente de gradient. Mais chaque iteration coute cher : il faut calculer la hessienne $H$ ($O(n^2)$ entrees) puis l'inverser ou la factoriser ($O(n^3)$). En grande dimension ($n > 10^4$, typique en ML), c'est prohibitif. D'ou le compromis : descente de gradient bon marche en haute dimension, Newton ou ses variantes en faible dimension.",
        },
        {
            "question": "Convergence quadratique de Newton signifie :",
            "options": [
                "Le nombre d'iterations double a chaque pas",
                "Le nombre de chiffres exacts double a chaque iteration",
                "L'erreur est proportionnelle au carre du temps",
                "On ne converge pas",
            ],
            "correct_answer": "Le nombre de chiffres exacts double a chaque iteration",
            "explanation": "La convergence quadratique signifie que l'erreur a l'iteration $k+1$ est MAJOREE par une constante fois le CARRE de l'erreur a l'iteration $k$ : $\\|e_{k+1}\\| \\le C\\|e_k\\|^2$. Concretement, si on est a $10^{-2}$ de la solution, on passe a $\\sim 10^{-4}$, puis $10^{-8}$, puis $10^{-16}$ — le nombre de chiffres exacts DOUBLE a chaque pas. C'est pourquoi Newton converge typiquement en 5-6 iterations quand il converge.",
        },
        {
            "question": "Pour eviter le calcul couteux de $H$, on peut utiliser :",
            "options": [
                "Quasi-Newton (BFGS)",
                "Multiplication matricielle",
                "Methode de la secante",
                "Algorithme genetique",
            ],
            "correct_answer": "Quasi-Newton (BFGS)",
            "explanation": "Les methodes QUASI-NEWTON comme BFGS approximent l'inverse de la hessienne $H^{-1}$ a partir de l'historique des gradients, sans jamais calculer $H$ explicitement. Le cout par iteration tombe a $O(n^2)$, et on garde une convergence SUPER-LINEAIRE (entre lineaire et quadratique). En tres grande dimension, on utilise L-BFGS (limited memory) qui ne stocke que les $m$ derniers gradients ($O(mn)$). C'est l'algorithme standard pour l'optimisation deterministe en ML classique (avant le deep learning).",
        },
        {
            "question": "Si la hessienne $H$ n'est pas definie positive, Newton :",
            "options": [
                "Converge plus vite",
                "Peut diverger ou aller vers un point selle",
                "Donne automatiquement le maximum",
                "Reste inchange",
            ],
            "correct_answer": "Peut diverger ou aller vers un point selle",
            "explanation": "Newton suppose implicitement que $H$ est DEFINIE POSITIVE — ce qui est vrai pres d'un minimum strict. Loin de l'optimum, ou pres d'un point-selle, $H$ peut avoir des valeurs propres negatives : Newton peut alors aller vers un MAXIMUM ou diverger. La parade classique est LEVENBERG-MARQUARDT : on utilise $(H + \\lambda I)^{-1}$ avec $\\lambda > 0$ ajuste — cela force la positivite et interpole entre Newton ($\\lambda \\to 0$) et descente de gradient ($\\lambda \\to \\infty$).",
        },
    ],
}


def get_questions_for_concept(concept_id: str, n: int = 5, rng=None) -> list[dict]:
    """
    Retourne n questions tirees au hasard pour un concept donne.
    Si la banque a moins de n questions, retourne tout ce qu'on a.
    """
    pool = QUESTION_BANK_BY_CONCEPT.get(concept_id, [])
    if not pool:
        return []
    if rng is None:
        import random as _rng
        rng = _rng
    n = min(n, len(pool))
    return rng.sample(pool, n)


def total_questions() -> int:
    """Nombre total de questions dans la banque."""
    return sum(len(qs) for qs in QUESTION_BANK_BY_CONCEPT.values())
