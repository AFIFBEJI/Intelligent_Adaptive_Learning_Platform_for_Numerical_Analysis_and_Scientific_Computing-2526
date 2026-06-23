/**
 * Guided scenarios — Module: Approximation & Optimization.
 *
 * Same philosophy as guided_scripts_rootfinding.ts: each script
 * links the CONCEPT (least squares, orthogonality, equioscillation,
 * gradient descent, Newton's method) to its APPLICATION. The
 * data are FIXED by the lesson; the student DECIDES (choices) and
 * COMPUTES it themselves (inputs) with an immediate graphical effect.
 */

import {
  GScript, GStep, PlotSpec,
  ORANGE, GREEN, TEAL, BLUE, PURPLE, MUTED,
  fmt,
} from './guided_core'

// ==================================================================
// 1. Least squares — fit a line to 4 points
// ==================================================================
function buildLeastSquares(): GScript {
  const pts: [number, number][] = [[0, 1], [1, 2], [2, 2], [3, 4]]
  const n = pts.length
  const Sx = pts.reduce((s, p) => s + p[0], 0)            // 6
  const Sy = pts.reduce((s, p) => s + p[1], 0)            // 9
  const Sxx = pts.reduce((s, p) => s + p[0] * p[0], 0)    // 14
  const Sxy = pts.reduce((s, p) => s + p[0] * p[1], 0)    // 18
  const aStar = (n * Sxy - Sx * Sy) / (n * Sxx - Sx * Sx) // 0.9
  const bStar = (Sy - aStar * Sx) / n                      // 0.9

  const dataPts = pts.map(([x, y]) => ({ x, y, color: BLUE }))
  const basePlot: PlotSpec = { xMin: -0.5, xMax: 3.5, yMin: 0, yMax: 5, points: dataPts }

  // 3 candidate lines: the good one and two less good ones
  const candidates: { a: number; b: number; color: string }[] = [
    { a: 0.5, b: 1.5, color: PURPLE },
    { a: aStar, b: bStar, color: GREEN },
    { a: 1.2, b: 0.2, color: ORANGE },
  ]
  const sumSq = (a: number, b: number): number =>
    pts.reduce((s, [x, y]) => s + (y - (a * x + b)) ** 2, 0)
  const residSegs = (a: number, b: number, color: string) =>
    pts.map(([x, y]) => ({ x1: x, y1: y, x2: x, y2: a * x + b, color, dash: '4 3', width: 2 }))
  const linePlot = (a: number, b: number, color: string): PlotSpec => ({
    ...basePlot,
    fns: [{ fn: (x: number) => a * x + b, color }],
    segs: residSegs(a, b, color),
  })

  const steps: GStep[] = []

  steps.push({
    plot: basePlot,
    instruction: {
      en: `The course fixes 4 measured points: $(0,1)$, $(1,2)$, $(2,2)$, $(3,4)$. CONCEPT: the least-squares line $y = ax + b$ is the one that minimizes the sum of SQUARED vertical gaps $S(a,b) = \\sum_{i} (y_i - a x_i - b)^2$. Let us APPLY it.`,
      fr: `Le cours fixe 4 points mesures : $(0,1)$, $(1,2)$, $(2,2)$, $(3,4)$. CONCEPT : la droite des moindres carres $y = ax + b$ est celle qui minimise la somme des ecarts verticaux au CARRE $S(a,b) = \\sum_{i} (y_i - a x_i - b)^2$. APPLIQUONS-le.`,
    },
  })

  steps.push({
    plot: basePlot,
    instruction: {
      en: 'Three candidate lines are proposed. Click each one: the dashed segments show ITS vertical residuals $y_i - (a x_i + b)$. Then pick the line with the smallest $S$.',
      fr: 'Trois droites candidates sont proposees. Cliquez chacune : les segments pointilles montrent SES residus verticaux $y_i - (a x_i + b)$. Puis choisissez la droite de plus petit $S$.',
    },
    choice: {
      prompt: { en: 'Which line minimizes the sum of squared residuals $S$?',
                fr: 'Quelle droite minimise la somme des carres des residus $S$ ?' },
      choices: candidates.map(c => {
        const S = sumSq(c.a, c.b)
        const correct = Math.abs(c.a - aStar) < 1e-9 && Math.abs(c.b - bStar) < 1e-9
        return {
          label: { en: `$y = ${fmt(c.a)}x + ${fmt(c.b)}$`, fr: `$y = ${fmt(c.a)}x + ${fmt(c.b)}$` },
          correct,
          plot: linePlot(c.a, c.b, c.color),
          feedback: correct
            ? { en: `Yes! For this line $S = ${fmt(S)}$ — the smallest possible. Look how its dashed residuals stay short and balanced around the line.`,
                fr: `Oui ! Pour cette droite $S = ${fmt(S)}$ — le plus petit possible. Regardez comme ses residus pointilles restent courts et equilibres autour de la droite.` }
            : { en: `Look at YOUR line on the graph: its residuals give $S = ${fmt(S)}$, which is larger. Try another line.`,
                fr: `Regardez VOTRE droite sur le graphe : ses residus donnent $S = ${fmt(S)}$, c'est plus grand. Essayez une autre droite.` },
        }
      }),
    },
  })

  steps.push({
    plot: linePlot(aStar, bStar, GREEN),
    instruction: {
      en: `To find this optimum WITHOUT trying lines, we solve the normal equations. First gather the sums from the data: $n = ${n}$, $\\sum x_i = ${Sx}$, $\\sum y_i = ${Sy}$, $\\sum x_i^2 = ${Sxx}$, $\\sum x_i y_i = ${Sxy}$.`,
      fr: `Pour trouver cet optimum SANS essayer des droites, on resout les equations normales. D'abord les sommes issues des donnees : $n = ${n}$, $\\sum x_i = ${Sx}$, $\\sum y_i = ${Sy}$, $\\sum x_i^2 = ${Sxx}$, $\\sum x_i y_i = ${Sxy}$.`,
    },
  })

  steps.push({
    plot: basePlot,
    instruction: {
      en: `APPLY the slope formula yourself: $a = \\dfrac{n \\sum x_i y_i - \\sum x_i \\sum y_i}{n \\sum x_i^2 - (\\sum x_i)^2}$. Type the value of $a$.`,
      fr: `APPLIQUEZ vous-meme la formule de la pente : $a = \\dfrac{n \\sum x_i y_i - \\sum x_i \\sum y_i}{n \\sum x_i^2 - (\\sum x_i)^2}$. Tapez la valeur de $a$.`,
    },
    input: {
      label: '$a =$', expected: aStar, tol: 0.01,
      ok: { en: `Correct: $a = \\frac{4 \\cdot 18 - 6 \\cdot 9}{4 \\cdot 14 - 36} = \\frac{18}{20} = ${fmt(aStar)}$. The graph shows the slope direction through the mean point.`,
            fr: `Exact : $a = \\frac{4 \\cdot 18 - 6 \\cdot 9}{4 \\cdot 14 - 36} = \\frac{18}{20} = ${fmt(aStar)}$. Le graphe montre la direction de pente par le point moyen.` },
      hint: { en: 'Not quite. Plug the sums in: numerator $4 \\cdot 18 - 6 \\cdot 9$, denominator $4 \\cdot 14 - 6^2$.',
              fr: 'Pas tout a fait. Injectez les sommes : numerateur $4 \\cdot 18 - 6 \\cdot 9$, denominateur $4 \\cdot 14 - 6^2$.' },
      reveal: { en: `Full computation: $a = \\frac{72 - 54}{56 - 36} = \\frac{18}{20} = ${fmt(aStar)}$. Type this value.`,
                fr: `Calcul complet : $a = \\frac{72 - 54}{56 - 36} = \\frac{18}{20} = ${fmt(aStar)}$. Tapez cette valeur.` },
      plotOnOk: {
        ...basePlot,
        segs: [{ x1: 0.5, y1: Sy / n + aStar * (0.5 - Sx / n), x2: 2.5, y2: Sy / n + aStar * (2.5 - Sx / n), color: GREEN, dash: '6 4', width: 2.5 }],
        points: [...dataPts, { x: Sx / n, y: Sy / n, color: GREEN, label: 'mean' }],
      },
    },
  })

  steps.push({
    plot: basePlot,
    instruction: {
      en: `Now the intercept: $b = \\dfrac{\\sum y_i - a \\sum x_i}{n}$ with your $a = ${fmt(aStar)}$. Type $b$.`,
      fr: `Maintenant l'ordonnee a l'origine : $b = \\dfrac{\\sum y_i - a \\sum x_i}{n}$ avec votre $a = ${fmt(aStar)}$. Tapez $b$.`,
    },
    input: {
      label: '$b =$', expected: bStar, tol: 0.01,
      ok: { en: `Correct: $b = \\frac{9 - 0.9 \\cdot 6}{4} = \\frac{3.6}{4} = ${fmt(bStar)}$. YOUR line $y = ${fmt(aStar)}x + ${fmt(bStar)}$ now appears with its residuals.`,
            fr: `Exact : $b = \\frac{9 - 0.9 \\cdot 6}{4} = \\frac{3.6}{4} = ${fmt(bStar)}$. VOTRE droite $y = ${fmt(aStar)}x + ${fmt(bStar)}$ apparait avec ses residus.` },
      hint: { en: 'Not quite. Compute $9 - 0.9 \\cdot 6$ first, then divide by $4$.',
              fr: 'Pas tout a fait. Calculez d\'abord $9 - 0.9 \\cdot 6$, puis divisez par $4$.' },
      reveal: { en: `Full computation: $b = \\frac{9 - 5.4}{4} = \\frac{3.6}{4} = ${fmt(bStar)}$. Type this value.`,
                fr: `Calcul complet : $b = \\frac{9 - 5.4}{4} = \\frac{3.6}{4} = ${fmt(bStar)}$. Tapez cette valeur.` },
      plotOnOk: linePlot(aStar, bStar, GREEN),
    },
  })

  steps.push({
    plot: linePlot(aStar, bStar, GREEN),
    instruction: {
      en: 'One last conceptual check before the summary.',
      fr: 'Un dernier controle conceptuel avant le bilan.',
    },
    choice: {
      prompt: { en: 'Why square the residuals instead of just summing them?',
                fr: 'Pourquoi mettre les residus au carre plutot que de simplement les sommer ?' },
      choices: [
        {
          label: { en: 'Positive and negative gaps would cancel out', fr: 'Les ecarts positifs et negatifs se compenseraient' },
          correct: true,
          feedback: { en: 'Exactly. Squaring keeps every gap positive (and makes $S$ differentiable, so we can solve $\\partial S / \\partial a = 0$).',
                      fr: 'Exactement. Le carre garde chaque ecart positif (et rend $S$ derivable, donc on peut resoudre $\\partial S / \\partial a = 0$).' },
        },
        {
          label: { en: 'Squares are faster to compute', fr: 'Les carres sont plus rapides a calculer' },
          correct: false,
          feedback: { en: 'No — speed is not the point. Think about a residual of $+1$ and another of $-1$: their plain sum is $0$ even though the fit is bad.',
                      fr: 'Non — la vitesse n\'est pas la question. Pensez a un residu de $+1$ et un autre de $-1$ : leur somme simple vaut $0$ alors que l\'ajustement est mauvais.' },
        },
      ],
    },
  })

  const Sbest = sumSq(aStar, bStar)
  return {
    title: { en: 'Fit a least-squares line yourself', fr: 'Ajustez vous-meme une droite des moindres carres' },
    steps,
    done: {
      intro: { en: 'You APPLIED the least-squares concept: you compared candidate lines by their squared residuals, then computed the optimal coefficients yourself:',
               fr: 'Vous avez APPLIQUE le concept des moindres carres : vous avez compare des droites candidates par leurs residus au carre, puis calcule vous-meme les coefficients optimaux :' },
      eqTex: `y = ${fmt(aStar)}\\,x + ${fmt(bStar)}`,
      table: {
        cols: [
          { en: 'quantity', fr: 'quantite' },
          { en: 'formula', fr: 'formule' },
          { en: 'your value', fr: 'votre valeur' },
        ],
        rows: [
          ['$a$', '$\\frac{n\\sum x_i y_i - \\sum x_i \\sum y_i}{n\\sum x_i^2 - (\\sum x_i)^2}$', `$${fmt(aStar)}$`],
          ['$b$', '$\\frac{\\sum y_i - a\\sum x_i}{n}$', `$${fmt(bStar)}$`],
          ['$S_{min}$', '$\\sum_i (y_i - a x_i - b)^2$', `$${fmt(Sbest)}$`],
        ],
      },
      plot: linePlot(aStar, bStar, GREEN),
      outro: { en: `Concept &#8594; application: minimizing $S$ leads to the normal equations, whose solution is YOUR line $y = ${fmt(aStar)}x + ${fmt(bStar)}$ with $S_{min} = ${fmt(Sbest)}$. Any other line makes the dashed residuals — hence $S$ — larger.`,
               fr: `Concept &#8594; application : minimiser $S$ conduit aux equations normales, dont la solution est VOTRE droite $y = ${fmt(aStar)}x + ${fmt(bStar)}$ avec $S_{min} = ${fmt(Sbest)}$. Toute autre droite rend les residus pointilles — donc $S$ — plus grands.` },
    },
  }
}

// ==================================================================
// 2. Orthogonal polynomials (Legendre on [-1, 1])
// ==================================================================
function buildOrthogonal(): GScript {
  const P0 = (_x: number) => 1
  const P1 = (x: number) => x
  const P2 = (x: number) => (3 * x * x - 1) / 2
  const ip11 = 2 / 3   // <P1, P1> = int_{-1}^{1} x^2 dx

  const base: PlotSpec = { xMin: -1.2, xMax: 1.2, yMin: -1.5, yMax: 1.8, interval: [-1, 1] }

  // signed area of x on [-1,1]: two opposite triangles
  const oddAreaPlot: PlotSpec = {
    ...base,
    fns: [{ fn: P1, color: BLUE }],
    polys: [
      { pts: [[-1, 0], [-1, -1], [0, 0]], fill: ORANGE, opacity: 0.3 },
      { pts: [[0, 0], [1, 1], [1, 0]], fill: GREEN, opacity: 0.3 },
    ],
  }
  // area of x^2 (positive everywhere)
  const sqPts: [number, number][] = []
  for (let i = 0; i <= 40; i++) { const x = -1 + i / 20; sqPts.push([x, x * x]) }
  const evenAreaPlot: PlotSpec = {
    ...base, yMin: -0.5, yMax: 1.5,
    fns: [{ fn: (x: number) => x * x, color: PURPLE }],
    polys: [{ pts: [[-1, 0], ...sqPts, [1, 0]], fill: PURPLE, opacity: 0.25 }],
  }
  const legendrePlot: PlotSpec = {
    ...base,
    fns: [
      { fn: P0, color: TEAL },
      { fn: P1, color: BLUE },
      { fn: P2, color: ORANGE },
    ],
  }

  const steps: GStep[] = []

  steps.push({
    plot: { ...base, fns: [{ fn: P0, color: TEAL }, { fn: P1, color: BLUE }] },
    instruction: {
      en: `CONCEPT: two polynomials $p$ and $q$ are ORTHOGONAL on $[-1,1]$ when $\\langle p, q \\rangle = \\int_{-1}^{1} p(x)\\,q(x)\\,dx = 0$. The course fixes the Legendre family: $P_0 = 1$ (teal), $P_1 = x$ (blue), $P_2 = \\frac{3x^2 - 1}{2}$. Let us APPLY the definition.`,
      fr: `CONCEPT : deux polynomes $p$ et $q$ sont ORTHOGONAUX sur $[-1,1]$ quand $\\langle p, q \\rangle = \\int_{-1}^{1} p(x)\\,q(x)\\,dx = 0$. Le cours fixe la famille de Legendre : $P_0 = 1$ (teal), $P_1 = x$ (bleu), $P_2 = \\frac{3x^2 - 1}{2}$. APPLIQUONS la definition.`,
    },
  })

  steps.push({
    plot: { ...base, fns: [{ fn: P1, color: BLUE }] },
    instruction: {
      en: `Test $\\langle P_0, P_1 \\rangle = \\int_{-1}^{1} 1 \\cdot x \\, dx$. Look at the graph of $x$ on $[-1,1]$ before answering.`,
      fr: `Testez $\\langle P_0, P_1 \\rangle = \\int_{-1}^{1} 1 \\cdot x \\, dx$. Regardez le graphe de $x$ sur $[-1,1]$ avant de repondre.`,
    },
    choice: {
      prompt: { en: 'What is the value of $\\int_{-1}^{1} x \\, dx$?',
                fr: 'Que vaut $\\int_{-1}^{1} x \\, dx$ ?' },
      choices: [
        {
          label: { en: '$0$', fr: '$0$' },
          correct: true,
          plot: oddAreaPlot,
          feedback: { en: 'Yes! $x$ is an ODD function: the orange area (negative, left) exactly cancels the green area (positive, right). So $P_0 \\perp P_1$.',
                      fr: 'Oui ! $x$ est une fonction IMPAIRE : l\'aire orange (negative, a gauche) compense exactement l\'aire verte (positive, a droite). Donc $P_0 \\perp P_1$.' },
        },
        {
          label: { en: '$1$', fr: '$1$' },
          correct: false,
          plot: oddAreaPlot,
          feedback: { en: 'No. Look at the two shaded triangles: they have the same size but OPPOSITE signs. Their sum is...',
                      fr: 'Non. Regardez les deux triangles colores : meme taille mais signes OPPOSES. Leur somme vaut...' },
        },
        {
          label: { en: '$2$', fr: '$2$' },
          correct: false,
          plot: oddAreaPlot,
          feedback: { en: 'No — that would be $\\int_{-1}^{1} 1 \\, dx$. Here the integrand is $x$, an odd function: the signed areas cancel.',
                      fr: 'Non — ce serait $\\int_{-1}^{1} 1 \\, dx$. Ici l\'integrande est $x$, une fonction impaire : les aires signees se compensent.' },
        },
      ],
    },
  })

  steps.push({
    plot: oddAreaPlot,
    instruction: {
      en: `Orthogonality does NOT mean zero norm. APPLY the norm computation: $\\langle P_1, P_1 \\rangle = \\int_{-1}^{1} x^2 \\, dx = \\left[\\frac{x^3}{3}\\right]_{-1}^{1}$. Type the value (4 decimals or a fraction as decimal).`,
      fr: `Orthogonalite ne veut PAS dire norme nulle. APPLIQUEZ le calcul de norme : $\\langle P_1, P_1 \\rangle = \\int_{-1}^{1} x^2 \\, dx = \\left[\\frac{x^3}{3}\\right]_{-1}^{1}$. Tapez la valeur (4 decimales ou la fraction en decimal).`,
    },
    input: {
      label: '$\\langle P_1,P_1\\rangle =$', expected: ip11, tol: 0.007,
      ok: { en: `Correct: $\\frac{1}{3} - \\left(-\\frac{1}{3}\\right) = \\frac{2}{3} \\approx ${fmt(ip11)}$. Now the integrand $x^2$ is EVEN: both halves add up (purple area).`,
            fr: `Exact : $\\frac{1}{3} - \\left(-\\frac{1}{3}\\right) = \\frac{2}{3} \\approx ${fmt(ip11)}$. Cette fois l'integrande $x^2$ est PAIR : les deux moities s'additionnent (aire violette).` },
      hint: { en: 'Not quite. Antiderivative of $x^2$ is $\\frac{x^3}{3}$; evaluate at $1$ and $-1$ and subtract.',
              fr: 'Pas tout a fait. La primitive de $x^2$ est $\\frac{x^3}{3}$ ; evaluez en $1$ et $-1$ puis soustrayez.' },
      reveal: { en: `Full computation: $\\frac{1^3}{3} - \\frac{(-1)^3}{3} = \\frac{2}{3} \\approx ${fmt(ip11)}$. Type this value.`,
                fr: `Calcul complet : $\\frac{1^3}{3} - \\frac{(-1)^3}{3} = \\frac{2}{3} \\approx ${fmt(ip11)}$. Tapez cette valeur.` },
      plotOnOk: evenAreaPlot,
    },
  })

  steps.push({
    plot: legendrePlot,
    instruction: {
      en: `Here is the whole family: $P_0$ (teal), $P_1$ (blue), $P_2$ (orange) — pairwise orthogonal. To approximate $f$ we write $f \\approx \\sum_k c_k P_k$ with $c_k = \\frac{\\langle f, P_k \\rangle}{\\langle P_k, P_k \\rangle}$.`,
      fr: `Voici toute la famille : $P_0$ (teal), $P_1$ (bleu), $P_2$ (orange) — orthogonaux deux a deux. Pour approcher $f$ on ecrit $f \\approx \\sum_k c_k P_k$ avec $c_k = \\frac{\\langle f, P_k \\rangle}{\\langle P_k, P_k \\rangle}$.`,
    },
    choice: {
      prompt: { en: 'Why does orthogonality make each coefficient $c_k$ INDEPENDENT of the others?',
                fr: 'Pourquoi l\'orthogonalite rend-elle chaque coefficient $c_k$ INDEPENDANT des autres ?' },
      choices: [
        {
          label: { en: 'Cross terms $\\langle P_j, P_k \\rangle$ vanish for $j \\neq k$', fr: 'Les termes croises $\\langle P_j, P_k \\rangle$ s\'annulent pour $j \\neq k$' },
          correct: true,
          plot: legendrePlot,
          feedback: { en: 'Exactly. Projecting $f \\approx \\sum_j c_j P_j$ onto $P_k$ kills every term except $c_k \\langle P_k, P_k \\rangle$ — so adding $P_3$ later never changes $c_0, c_1, c_2$.',
                      fr: 'Exactement. Projeter $f \\approx \\sum_j c_j P_j$ sur $P_k$ tue tous les termes sauf $c_k \\langle P_k, P_k \\rangle$ — ajouter $P_3$ plus tard ne change donc jamais $c_0, c_1, c_2$.' },
        },
        {
          label: { en: 'Because the $P_k$ all have the same degree', fr: 'Parce que les $P_k$ ont tous le meme degre' },
          correct: false,
          feedback: { en: 'No — their degrees are $0, 1, 2, \\dots$ The key is the inner product: what happens to $\\langle P_j, P_k \\rangle$ when $j \\neq k$?',
                      fr: 'Non — leurs degres sont $0, 1, 2, \\dots$ La cle est le produit scalaire : que vaut $\\langle P_j, P_k \\rangle$ quand $j \\neq k$ ?' },
        },
        {
          label: { en: 'Because they are all bounded by 1', fr: 'Parce qu\'ils sont tous bornes par 1' },
          correct: false,
          feedback: { en: 'No — boundedness is not the point. With a NON-orthogonal basis (like $1, x, x^2$) every coefficient depends on all the others through a linear system.',
                      fr: 'Non — la borne n\'est pas la question. Avec une base NON orthogonale (comme $1, x, x^2$) chaque coefficient depend de tous les autres via un systeme lineaire.' },
        },
      ],
    },
  })

  steps.push({
    plot: legendrePlot,
    instruction: {
      en: 'Compare with the monomial basis $1, x, x^2$: the normal equations couple ALL coefficients (Hilbert matrix, badly conditioned). With Legendre, each $c_k$ is one independent integral. That is why orthogonal polynomials are the workhorse of approximation.',
      fr: 'Comparez avec la base monomiale $1, x, x^2$ : les equations normales couplent TOUS les coefficients (matrice de Hilbert, mal conditionnee). Avec Legendre, chaque $c_k$ est une integrale independante. C\'est pourquoi les polynomes orthogonaux sont l\'outil central de l\'approximation.',
    },
  })

  return {
    title: { en: 'Discover orthogonal polynomials yourself', fr: 'Decouvrez vous-meme les polynomes orthogonaux' },
    steps,
    done: {
      intro: { en: 'You APPLIED the orthogonality concept on the Legendre family: you checked an inner product graphically and computed a norm yourself:',
               fr: 'Vous avez APPLIQUE le concept d\'orthogonalite sur la famille de Legendre : vous avez verifie un produit scalaire graphiquement et calcule une norme vous-meme :' },
      eqTex: '\\langle p, q \\rangle = \\int_{-1}^{1} p(x)\\,q(x)\\,dx',
      table: {
        cols: [
          { en: 'inner product', fr: 'produit scalaire' },
          { en: 'integrand', fr: 'integrande' },
          { en: 'your value', fr: 'votre valeur' },
          { en: 'meaning', fr: 'signification' },
        ],
        rows: [
          ['$\\langle P_0, P_1 \\rangle$', '$x$ (odd / impair)', '$0$', '$P_0 \\perp P_1$'],
          ['$\\langle P_1, P_1 \\rangle$', '$x^2$ (even / pair)', `$\\frac{2}{3} \\approx ${fmt(ip11)}$`, '$\\|P_1\\|^2 > 0$'],
        ],
      },
      plot: legendrePlot,
      outro: { en: 'Concept &#8594; application: because $\\langle P_j, P_k \\rangle = 0$ for $j \\neq k$, each coefficient $c_k = \\langle f, P_k \\rangle / \\|P_k\\|^2$ is computed alone — no linear system, no coupling. Adding more terms refines the approximation without redoing anything.',
               fr: 'Concept &#8594; application : comme $\\langle P_j, P_k \\rangle = 0$ pour $j \\neq k$, chaque coefficient $c_k = \\langle f, P_k \\rangle / \\|P_k\\|^2$ se calcule seul — pas de systeme lineaire, pas de couplage. Ajouter des termes raffine l\'approximation sans rien recalculer.' },
    },
  }
}

// ==================================================================
// 3. Minimax approximation (equioscillation) — e^x by a line
// ==================================================================
function buildMinimax(): GScript {
  const f = Math.exp
  const a = Math.E - 1                    // pente : 1.7183
  const c = Math.log(a)                   // interior point: 0.5413
  const b = (a * (1 - c) + 1) / 2         // 0.8941
  const E = 1 - b                          // 0.1059
  const L = (x: number) => a * x + b
  const err = (x: number) => f(x) - L(x)

  const mainPlot: PlotSpec = {
    xMin: -0.1, xMax: 1.1, yMin: 0.5, yMax: 3,
    fns: [{ fn: f, color: BLUE }, { fn: L, color: GREEN }],
    interval: [0, 1],
  }
  const errPlot: PlotSpec = {
    xMin: -0.1, xMax: 1.1, yMin: -0.2, yMax: 0.2,
    fns: [
      { fn: err, color: PURPLE },
      { fn: () => E, color: ORANGE, width: 1.5, dash: '6 4' },
      { fn: () => -E, color: ORANGE, width: 1.5, dash: '6 4' },
    ],
    interval: [0, 1],
    points: [
      { x: 0, y: E, color: ORANGE, label: '+E' },
      { x: c, y: -E, color: ORANGE, label: '-E' },
      { x: 1, y: E, color: ORANGE, label: '+E' },
    ],
  }

  const steps: GStep[] = []

  steps.push({
    plot: { xMin: -0.1, xMax: 1.1, yMin: 0.5, yMax: 3, fns: [{ fn: f, color: BLUE }], interval: [0, 1] },
    instruction: {
      en: `The course fixes the problem: approximate $f(x) = e^x$ on $[0,1]$ by a LINE $L(x) = ax + b$ minimizing the WORST error $E = \\max_{[0,1]} |f(x) - L(x)|$. CONCEPT (Chebyshev): the best line is reached when the error EQUIOSCILLATES — it hits $+E$ and $-E$ alternately.`,
      fr: `Le cours fixe le probleme : approcher $f(x) = e^x$ sur $[0,1]$ par une DROITE $L(x) = ax + b$ minimisant la PIRE erreur $E = \\max_{[0,1]} |f(x) - L(x)|$. CONCEPT (Chebyshev) : la meilleure droite est atteinte quand l'erreur EQUIOSCILLE — elle touche $+E$ et $-E$ en alternance.`,
    },
  })

  steps.push({
    plot: mainPlot,
    instruction: {
      en: 'Equioscillation theorem: for the best approximation of degree $n$, the error must alternate between $+E$ and $-E$ at least $n + 2$ times.',
      fr: 'Theoreme d\'equioscillation : pour la meilleure approximation de degre $n$, l\'erreur doit alterner entre $+E$ et $-E$ au moins $n + 2$ fois.',
    },
    choice: {
      prompt: { en: 'For a LINE ($n = 1$), how many equioscillation points are needed?',
                fr: 'Pour une DROITE ($n = 1$), combien de points d\'equioscillation faut-il ?' },
      choices: [2, 3, 4].map(k => ({
        label: { en: `$${k}$`, fr: `$${k}$` },
        correct: k === 3,
        plot: k === 3 ? errPlot : undefined,
        feedback: k === 3
          ? { en: 'Yes: $n + 2 = 1 + 2 = 3$ points. The graph now shows the error curve $f - L$ touching $+E$, $-E$, $+E$ at $x = 0$, $x = c$, $x = 1$.',
              fr: 'Oui : $n + 2 = 1 + 2 = 3$ points. Le graphe montre maintenant la courbe d\'erreur $f - L$ touchant $+E$, $-E$, $+E$ en $x = 0$, $x = c$, $x = 1$.' }
          : { en: `No: the theorem requires $n + 2$ alternations, and here $n = 1$, so $1 + 2 = 3$, not $${k}$.`,
              fr: `Non : le theoreme exige $n + 2$ alternances, et ici $n = 1$, donc $1 + 2 = 3$, pas $${k}$.` },
      })),
    },
  })

  steps.push({
    plot: errPlot,
    instruction: {
      en: `Building the line. Extremes of the error at the ENDPOINTS being equal forces the slope: $a = \\frac{f(1) - f(0)}{1 - 0} = e - 1 \\approx ${fmt(a)}$ (the chord slope). The interior extremum is where $f'(x) = a$, i.e. $e^c = e - 1$, so $c = \\ln(e - 1) \\approx ${fmt(c)}$.`,
      fr: `Construction de la droite. L'egalite des erreurs aux EXTREMITES impose la pente : $a = \\frac{f(1) - f(0)}{1 - 0} = e - 1 \\approx ${fmt(a)}$ (pente de la corde). L'extremum interieur est la ou $f'(x) = a$, c'est-a-dire $e^c = e - 1$, donc $c = \\ln(e - 1) \\approx ${fmt(c)}$.`,
    },
  })

  steps.push({
    plot: errPlot,
    instruction: {
      en: `Balancing $+E$ at the ends and $-E$ at $c$ gives $b = \\frac{a(1 - c) + 1}{2} \\approx ${fmt(b)}$, hence the minimax line $L(x) = ${fmt(a)}x + ${fmt(b)}$. Now APPLY it: the worst error equals the error at $x = 0$. Compute $E = |f(0) - L(0)| = |1 - b|$ and type it.`,
      fr: `Equilibrer $+E$ aux extremites et $-E$ en $c$ donne $b = \\frac{a(1 - c) + 1}{2} \\approx ${fmt(b)}$, d'ou la droite minimax $L(x) = ${fmt(a)}x + ${fmt(b)}$. APPLIQUEZ : la pire erreur egale l'erreur en $x = 0$. Calculez $E = |f(0) - L(0)| = |1 - b|$ et tapez-la.`,
    },
    input: {
      label: '$E =$', expected: E, tol: 0.01,
      ok: { en: `Correct: $E = |1 - ${fmt(b)}| = ${fmt(E)}$. The orange dashed lines $\\pm E$ now frame the purple error curve — it touches them exactly 3 times.`,
            fr: `Exact : $E = |1 - ${fmt(b)}| = ${fmt(E)}$. Les pointilles oranges $\\pm E$ encadrent la courbe d'erreur violette — elle les touche exactement 3 fois.` },
      hint: { en: `Not quite. $f(0) = e^0 = 1$ and $L(0) = b \\approx ${fmt(b)}$. Subtract.`,
              fr: `Pas tout a fait. $f(0) = e^0 = 1$ et $L(0) = b \\approx ${fmt(b)}$. Soustrayez.` },
      reveal: { en: `Full computation: $E = |1 - ${fmt(b)}| = ${fmt(E)}$. Type this value.`,
                fr: `Calcul complet : $E = |1 - ${fmt(b)}| = ${fmt(E)}$. Tapez cette valeur.` },
      plotOnOk: errPlot,
    },
  })

  steps.push({
    plot: errPlot,
    instruction: {
      en: 'Check on the error plot: the purple curve never leaves the orange band $[-E, +E]$, and it touches the boundary at the 3 alternating points. That is the signature of optimality.',
      fr: 'Verifiez sur le graphe d\'erreur : la courbe violette ne sort jamais de la bande orange $[-E, +E]$, et elle touche la frontiere aux 3 points alternes. C\'est la signature de l\'optimalite.',
    },
    choice: {
      prompt: { en: 'If we tilted the line slightly to reduce the error at $x = 0$, what would happen?',
                fr: 'Si on inclinait legerement la droite pour reduire l\'erreur en $x = 0$, que se passerait-il ?' },
      choices: [
        {
          label: { en: 'The error would grow somewhere else above $E$', fr: 'L\'erreur grandirait ailleurs au-dela de $E$' },
          correct: true,
          feedback: { en: 'Exactly — that is WHY equioscillation characterizes the optimum: any change that lowers one peak raises another. The max error cannot go below $E$.',
                      fr: 'Exactement — c\'est POURQUOI l\'equioscillation caracterise l\'optimum : tout changement qui abaisse un pic en eleve un autre. L\'erreur max ne peut pas descendre sous $E$.' },
        },
        {
          label: { en: 'The max error would decrease everywhere', fr: 'L\'erreur max diminuerait partout' },
          correct: false,
          feedback: { en: 'Impossible: a line has only 2 parameters but the error already touches the bound at 3 alternating points — you cannot push all 3 down at once.',
                      fr: 'Impossible : une droite n\'a que 2 parametres mais l\'erreur touche deja la borne en 3 points alternes — on ne peut pas abaisser les 3 a la fois.' },
        },
      ],
    },
  })

  return {
    title: { en: 'Build the minimax line for exp yourself', fr: 'Construisez vous-meme la droite minimax de exp' },
    steps,
    done: {
      intro: { en: 'You APPLIED the equioscillation concept: you counted the alternation points and computed the optimal error level yourself:',
               fr: 'Vous avez APPLIQUE le concept d\'equioscillation : vous avez compte les points d\'alternance et calcule vous-meme le niveau d\'erreur optimal :' },
      eqTex: `L(x) = ${fmt(a)}\\,x + ${fmt(b)}, \\qquad E = ${fmt(E)}`,
      table: {
        cols: [
          { en: 'point', fr: 'point' },
          { en: '$x$', fr: '$x$' },
          { en: 'error $f(x) - L(x)$', fr: 'erreur $f(x) - L(x)$' },
        ],
        rows: [
          ['1', '$0$', `$+E = ${fmt(err(0))}$`],
          ['2', `$c = \\ln(e-1) \\approx ${fmt(c)}$`, `$-E = ${fmt(err(c))}$`],
          ['3', '$1$', `$+E = ${fmt(err(1))}$`],
        ],
      },
      plot: errPlot,
      outro: { en: `Concept &#8594; application: equioscillation at $n + 2 = 3$ alternating points proves YOUR line is the best possible — no other line gets a max error below $E \\approx ${fmt(E)}$. Compare: least squares minimizes the AVERAGE squared error, minimax minimizes the WORST error.`,
               fr: `Concept &#8594; application : l'equioscillation en $n + 2 = 3$ points alternes prouve que VOTRE droite est la meilleure possible — aucune autre droite n'obtient une erreur max sous $E \\approx ${fmt(E)}$. Comparez : les moindres carres minimisent l'erreur quadratique MOYENNE, le minimax minimise la PIRE erreur.` },
    },
  }
}

// ==================================================================
// 4. Gradient descent — f(x) = x^2 - 4x + 5
// ==================================================================
const QF = (x: number) => x * x - 4 * x + 5
const QDF = (x: number) => 2 * x - 4
const QTEX = 'x^{2} - 4x + 5'

function gdPlot(xs: number[], withTangents = true): PlotSpec {
  const points = xs.map((x, i) => ({ x, y: QF(x), color: i === xs.length - 1 ? ORANGE : MUTED, label: `x${'₀₁₂₃₄'[i] ?? String(i)}` }))
  const segs = withTangents
    ? xs.slice(0, -1).map(x => {
        const d = QDF(x)
        return { x1: x - 0.45, y1: QF(x) - 0.45 * d, x2: x + 0.45, y2: QF(x) + 0.45 * d, color: PURPLE, dash: '5 3', width: 2 }
      })
    : []
  return { xMin: -0.6, xMax: 4.2, yMin: 0, yMax: 6.5, fns: [{ fn: QF, color: BLUE }], points, segs, vlines: [{ x: 2, color: GREEN, dash: '4 4', label: 'min' }] }
}

function buildGradientDescent(): GScript {
  const alpha = 0.25
  const xs = [0]
  for (let k = 0; k < 3; k++) xs.push(xs[k] - alpha * QDF(xs[k]))  // 0, 1, 1.5, 1.75

  const steps: GStep[] = []

  steps.push({
    plot: gdPlot([0], false),
    instruction: {
      en: `The course fixes $f(x) = ${QTEX}$ (minimum at $x = 2$, green dashed line), the start $x_0 = 0$ and the step $\\alpha = ${fmt(alpha)}$. CONCEPT: the derivative $f'(x) = 2x - 4$ points UPHILL, so gradient descent moves AGAINST it: $x_{k+1} = x_k - \\alpha f'(x_k)$.`,
      fr: `Le cours fixe $f(x) = ${QTEX}$ (minimum en $x = 2$, pointilles verts), le depart $x_0 = 0$ et le pas $\\alpha = ${fmt(alpha)}$. CONCEPT : la derivee $f'(x) = 2x - 4$ pointe vers la MONTEE, donc la descente de gradient va CONTRE elle : $x_{k+1} = x_k - \\alpha f'(x_k)$.`,
    },
  })

  steps.push({
    plot: gdPlot([0], true),
    instruction: {
      en: `At $x_0 = 0$: $f'(0) = 2 \\cdot 0 - 4 = -4 < 0$ (the purple dashed tangent slopes DOWN to the right).`,
      fr: `En $x_0 = 0$ : $f'(0) = 2 \\cdot 0 - 4 = -4 < 0$ (la tangente violette en pointilles descend vers la droite).`,
    },
    choice: {
      prompt: { en: 'When $f\'(x_k) < 0$, in which direction must we move to DESCEND?',
                fr: 'Quand $f\'(x_k) < 0$, dans quel sens faut-il se deplacer pour DESCENDRE ?' },
      choices: [
        {
          label: { en: 'To the right ($x$ increases)', fr: 'Vers la droite ($x$ augmente)' },
          correct: true,
          feedback: { en: 'Yes: $x_{k+1} = x_k - \\alpha f\'(x_k)$ with $f\'(x_k) < 0$ gives $x_{k+1} > x_k$. Subtracting a negative number moves you right — downhill, following the tangent.',
                      fr: 'Oui : $x_{k+1} = x_k - \\alpha f\'(x_k)$ avec $f\'(x_k) < 0$ donne $x_{k+1} > x_k$. Soustraire un nombre negatif vous deplace a droite — vers le bas, en suivant la tangente.' },
        },
        {
          label: { en: 'To the left ($x$ decreases)', fr: 'Vers la gauche ($x$ diminue)' },
          correct: false,
          feedback: { en: 'No — look at the tangent: going left climbs the parabola. The formula subtracts $\\alpha f\'(x_k)$, and minus a NEGATIVE slope pushes you right.',
                      fr: 'Non — regardez la tangente : aller a gauche fait monter la parabole. La formule soustrait $\\alpha f\'(x_k)$, et moins une pente NEGATIVE vous pousse a droite.' },
        },
      ],
    },
  })

  const rows: string[][] = []
  for (let k = 0; k < 3; k++) {
    const xk = xs[k], d = QDF(xk), xn = xs[k + 1]
    rows.push([String(k), `$${fmt(xk)}$`, `$${fmt(d)}$`, `$${fmt(xn)}$`])
    steps.push({
      plot: gdPlot(xs.slice(0, k + 1), true),
      instruction: {
        en: `Iteration ${k + 1} of 3 — APPLY the update yourself: $x_{${k + 1}} = x_{${k}} - \\alpha f'(x_{${k}}) = ${fmt(xk)} - ${fmt(alpha)} \\cdot (${fmt(d)})$. Type $x_{${k + 1}}$.`,
        fr: `Iteration ${k + 1} sur 3 — APPLIQUEZ la mise a jour vous-meme : $x_{${k + 1}} = x_{${k}} - \\alpha f'(x_{${k}}) = ${fmt(xk)} - ${fmt(alpha)} \\cdot (${fmt(d)})$. Tapez $x_{${k + 1}}$.`,
      },
      input: {
        label: `$x_{${k + 1}} =$`, expected: xn, tol: Math.max(Math.abs(xn) * 0.01, 0.01),
        ok: { en: `Correct: $x_{${k + 1}} = ${fmt(xk)} + ${fmt(-alpha * d)} = ${fmt(xn)}$. Watch YOUR new point slide down the parabola toward $x = 2$.`,
              fr: `Exact : $x_{${k + 1}} = ${fmt(xk)} + ${fmt(-alpha * d)} = ${fmt(xn)}$. Regardez VOTRE nouveau point glisser le long de la parabole vers $x = 2$.` },
        hint: { en: `Not quite. $f'(${fmt(xk)}) = 2 \\cdot ${fmt(xk)} - 4 = ${fmt(d)}$, then subtract $\\alpha \\cdot f'$: ${fmt(xk)} - ${fmt(alpha)} \\cdot (${fmt(d)})$.`,
                fr: `Pas tout a fait. $f'(${fmt(xk)}) = 2 \\cdot ${fmt(xk)} - 4 = ${fmt(d)}$, puis soustrayez $\\alpha \\cdot f'$ : ${fmt(xk)} - ${fmt(alpha)} \\cdot (${fmt(d)})$.` },
        reveal: { en: `Full computation: $x_{${k + 1}} = ${fmt(xk)} - ${fmt(alpha)} \\cdot (${fmt(d)}) = ${fmt(xk)} + ${fmt(-alpha * d)} = ${fmt(xn)}$. Type this value.`,
                  fr: `Calcul complet : $x_{${k + 1}} = ${fmt(xk)} - ${fmt(alpha)} \\cdot (${fmt(d)}) = ${fmt(xk)} + ${fmt(-alpha * d)} = ${fmt(xn)}$. Tapez cette valeur.` },
        plotOnOk: gdPlot(xs.slice(0, k + 2), true),
      },
    })
  }

  steps.push({
    plot: gdPlot(xs, true),
    instruction: {
      en: `Look at YOUR trajectory: $0 \\to 1 \\to 1.5 \\to 1.75$. Each step covers half the remaining distance to $x = 2$, because the gradient shrinks as you approach the minimum.`,
      fr: `Regardez VOTRE trajectoire : $0 \\to 1 \\to 1.5 \\to 1.75$. Chaque pas couvre la moitie de la distance restante vers $x = 2$, car le gradient retrecit a l'approche du minimum.`,
    },
    choice: {
      prompt: { en: 'Why do the steps get smaller and smaller?',
                fr: 'Pourquoi les pas deviennent-ils de plus en plus petits ?' },
      choices: [
        {
          label: { en: '$|f\'(x_k)|$ shrinks near the minimum', fr: '$|f\'(x_k)|$ retrecit pres du minimum' },
          correct: true,
          feedback: { en: 'Exactly: the step is $\\alpha |f\'(x_k)|$ and $f\'(2) = 0$. The flatter the slope, the smaller the move — the method brakes automatically.',
                      fr: 'Exactement : le pas vaut $\\alpha |f\'(x_k)|$ et $f\'(2) = 0$. Plus la pente est plate, plus le deplacement est petit — la methode freine toute seule.' },
        },
        {
          label: { en: 'The step size $\\alpha$ decreases at each iteration', fr: 'Le pas $\\alpha$ diminue a chaque iteration' },
          correct: false,
          feedback: { en: 'No — here $\\alpha = 0.25$ is FIXED. What changes between iterations is the factor $f\'(x_k)$: $-4$, then $-2$, then $-1$.',
                      fr: 'Non — ici $\\alpha = 0.25$ est FIXE. Ce qui change entre les iterations est le facteur $f\'(x_k)$ : $-4$, puis $-2$, puis $-1$.' },
        },
      ],
    },
  })

  return {
    title: { en: 'Run gradient descent yourself', fr: 'Executez vous-meme la descente de gradient' },
    steps,
    done: {
      intro: { en: 'You APPLIED the gradient descent concept: you chose the descent direction and computed every iterate yourself:',
               fr: 'Vous avez APPLIQUE le concept de descente de gradient : vous avez choisi la direction de descente et calcule chaque itere vous-meme :' },
      eqTex: `f(x) = ${QTEX}, \\qquad x_{k+1} = x_k - ${fmt(alpha)}\\,f'(x_k)`,
      table: {
        cols: [
          { en: '$k$', fr: '$k$' },
          { en: '$x_k$', fr: '$x_k$' },
          { en: '$f\'(x_k)$', fr: '$f\'(x_k)$' },
          { en: '$x_{k+1}$ (yours)', fr: '$x_{k+1}$ (le votre)' },
        ],
        rows,
      },
      plot: gdPlot(xs, true),
      outro: { en: `Concept &#8594; application: moving against the gradient with $\\alpha = ${fmt(alpha)}$ halves the distance to the minimum at each step ($0, 1, 1.5, 1.75, \\dots \\to 2$). It converges, but only LINEARLY. Next script: Newton reaches $x = 2$ in ONE step.`,
               fr: `Concept &#8594; application : aller contre le gradient avec $\\alpha = ${fmt(alpha)}$ divise par deux la distance au minimum a chaque pas ($0, 1, 1.5, 1.75, \\dots \\to 2$). Cela converge, mais seulement LINEAIREMENT. Script suivant : Newton atteint $x = 2$ en UN pas.` },
    },
  }
}

// ==================================================================
// 5. Newton optimization — same f, a single step
// ==================================================================
function buildNewtonOptimization(): GScript {
  const x0 = 0
  const d1 = QDF(x0)        // -4
  const d2 = 2              // f'' = 2 everywhere
  const x1 = x0 - d1 / d2   // 2
  const gdXs = [0, 1, 1.5, 1.75]

  const newtonPlot: PlotSpec = {
    xMin: -0.6, xMax: 4.2, yMin: 0, yMax: 6.5,
    fns: [{ fn: QF, color: BLUE }],
    points: [
      { x: x0, y: QF(x0), color: MUTED, label: 'x₀' },
      { x: x1, y: QF(x1), color: GREEN, label: 'x₁ = min' },
    ],
    segs: [{ x1: x0, y1: QF(x0), x2: x1, y2: QF(x1), color: GREEN, dash: '6 4', width: 2 }],
    vlines: [{ x: 2, color: GREEN, dash: '4 4' }],
  }
  const comparePlot: PlotSpec = {
    xMin: -0.6, xMax: 4.2, yMin: 0, yMax: 6.5,
    fns: [{ fn: QF, color: BLUE }],
    points: [
      ...gdXs.map((x, i) => ({ x, y: QF(x), color: ORANGE, label: i === 0 ? 'x0' : `g${i}` })),
      { x: x1, y: QF(x1), color: GREEN, label: 'Newton x₁' },
    ],
    segs: [{ x1: x0, y1: QF(x0), x2: x1, y2: QF(x1), color: GREEN, dash: '6 4', width: 2 }],
    vlines: [{ x: 2, color: GREEN, dash: '4 4', label: 'min' }],
  }

  const steps: GStep[] = []

  steps.push({
    plot: gdPlot([x0], true),
    instruction: {
      en: `Same problem as before: minimize $f(x) = ${QTEX}$ from $x_0 = 0$. CONCEPT: Newton's method for optimization uses the CURVATURE too: $x_{k+1} = x_k - \\dfrac{f'(x_k)}{f''(x_k)}$. It models $f$ by its tangent PARABOLA and jumps straight to that parabola's minimum.`,
      fr: `Meme probleme qu'avant : minimiser $f(x) = ${QTEX}$ depuis $x_0 = 0$. CONCEPT : la methode de Newton pour l'optimisation utilise aussi la COURBURE : $x_{k+1} = x_k - \\dfrac{f'(x_k)}{f''(x_k)}$. Elle modelise $f$ par sa PARABOLE tangente et saute directement au minimum de cette parabole.`,
    },
  })

  steps.push({
    plot: gdPlot([x0], true),
    instruction: {
      en: `Gather the ingredients at $x_0 = 0$: $f'(x) = 2x - 4$ gives $f'(0) = ${fmt(d1)}$, and $f''(x) = 2$ everywhere, so $f''(0) = ${fmt(d2)}$.`,
      fr: `Reunissez les ingredients en $x_0 = 0$ : $f'(x) = 2x - 4$ donne $f'(0) = ${fmt(d1)}$, et $f''(x) = 2$ partout, donc $f''(0) = ${fmt(d2)}$.`,
    },
  })

  steps.push({
    plot: gdPlot([x0], true),
    instruction: {
      en: `APPLY Newton's update yourself: $x_1 = x_0 - \\dfrac{f'(x_0)}{f''(x_0)} = 0 - \\dfrac{${fmt(d1)}}{${fmt(d2)}}$. Type $x_1$.`,
      fr: `APPLIQUEZ vous-meme la mise a jour de Newton : $x_1 = x_0 - \\dfrac{f'(x_0)}{f''(x_0)} = 0 - \\dfrac{${fmt(d1)}}{${fmt(d2)}}$. Tapez $x_1$.`,
    },
    input: {
      label: '$x_1 =$', expected: x1, tol: 0.02,
      ok: { en: `Correct: $x_1 = 0 - \\frac{-4}{2} = 2$. ONE step and you landed EXACTLY on the minimum (green point). No iteration 2 needed!`,
            fr: `Exact : $x_1 = 0 - \\frac{-4}{2} = 2$. UN pas et vous atterrissez EXACTEMENT sur le minimum (point vert). Pas besoin d'iteration 2 !` },
      hint: { en: 'Not quite. Divide $f\'(x_0) = -4$ by $f\'\'(x_0) = 2$, then SUBTRACT the result from $x_0 = 0$.',
              fr: 'Pas tout a fait. Divisez $f\'(x_0) = -4$ par $f\'\'(x_0) = 2$, puis SOUSTRAYEZ le resultat de $x_0 = 0$.' },
      reveal: { en: `Full computation: $x_1 = 0 - \\frac{-4}{2} = 0 + 2 = ${fmt(x1)}$. Type this value.`,
                fr: `Calcul complet : $x_1 = 0 - \\frac{-4}{2} = 0 + 2 = ${fmt(x1)}$. Tapez cette valeur.` },
      plotOnOk: newtonPlot,
    },
  })

  steps.push({
    plot: newtonPlot,
    instruction: {
      en: `Check: $f'(2) = 2 \\cdot 2 - 4 = 0$, so $x_1 = 2$ is a stationary point, and $f''(2) = 2 > 0$ confirms a MINIMUM. Newton converged in one single step.`,
      fr: `Verification : $f'(2) = 2 \\cdot 2 - 4 = 0$, donc $x_1 = 2$ est un point stationnaire, et $f''(2) = 2 > 0$ confirme un MINIMUM. Newton a converge en un seul pas.`,
    },
    choice: {
      prompt: { en: 'Why does ONE Newton step suffice here?',
                fr: 'Pourquoi UN seul pas de Newton suffit-il ici ?' },
      choices: [
        {
          label: { en: '$f$ is quadratic: its tangent parabola IS $f$ itself', fr: '$f$ est quadratique : sa parabole tangente EST $f$ elle-meme' },
          correct: true,
          feedback: { en: 'Exactly. Newton minimizes the local quadratic model. When $f$ is already a parabola, the model is exact, so the jump lands on the true minimum. For non-quadratic $f$, Newton needs a few steps but converges QUADRATICALLY.',
                      fr: 'Exactement. Newton minimise le modele quadratique local. Quand $f$ est deja une parabole, le modele est exact, donc le saut atterrit sur le vrai minimum. Pour un $f$ non quadratique, Newton a besoin de quelques pas mais converge QUADRATIQUEMENT.' },
        },
        {
          label: { en: 'Because the starting point $x_0 = 0$ was lucky', fr: 'Parce que le point de depart $x_0 = 0$ etait chanceux' },
          correct: false,
          feedback: { en: 'No — try mentally from $x_0 = 5$: $x_1 = 5 - \\frac{2 \\cdot 5 - 4}{2} = 5 - 3 = 2$. ANY start reaches the minimum in one step, because $f$ is quadratic.',
                      fr: 'Non — essayez mentalement depuis $x_0 = 5$ : $x_1 = 5 - \\frac{2 \\cdot 5 - 4}{2} = 5 - 3 = 2$. N\'IMPORTE quel depart atteint le minimum en un pas, car $f$ est quadratique.' },
        },
        {
          label: { en: 'Because $f\'\'$ is small', fr: 'Parce que $f\'\'$ est petit' },
          correct: false,
          feedback: { en: 'No — the size of $f\'\'$ only scales the step. The key property is that $f\'\'$ is CONSTANT: the quadratic model matches $f$ exactly.',
                      fr: 'Non — la taille de $f\'\'$ ne fait que dimensionner le pas. La propriete cle est que $f\'\'$ est CONSTANTE : le modele quadratique coincide exactement avec $f$.' },
        },
      ],
    },
  })

  steps.push({
    plot: comparePlot,
    instruction: {
      en: `Side-by-side on the same parabola: the orange points are the gradient descent trajectory ($0, 1, 1.5, 1.75, \\dots$, still not at $2$ after 3 steps); the green jump is YOUR single Newton step. Gradient uses slope only ($\\alpha$ fixed); Newton divides the slope by the curvature — the perfect step size.`,
      fr: `Cote a cote sur la meme parabole : les points oranges sont la trajectoire de la descente de gradient ($0, 1, 1.5, 1.75, \\dots$, toujours pas en $2$ apres 3 pas) ; le saut vert est VOTRE unique pas de Newton. Le gradient n'utilise que la pente ($\\alpha$ fixe) ; Newton divise la pente par la courbure — le pas parfait.`,
    },
  })

  return {
    title: { en: 'Take one Newton step yourself', fr: 'Faites vous-meme un pas de Newton' },
    steps,
    done: {
      intro: { en: 'You APPLIED Newton\'s optimization concept: slope DIVIDED by curvature gives the exact step on a quadratic. Compare with your gradient descent run:',
               fr: 'Vous avez APPLIQUE le concept de Newton pour l\'optimisation : la pente DIVISEE par la courbure donne le pas exact sur une quadratique. Comparez avec votre descente de gradient :' },
      eqTex: `x_1 = x_0 - \\frac{f'(x_0)}{f''(x_0)} = 0 - \\frac{-4}{2} = 2`,
      table: {
        cols: [
          { en: 'method', fr: 'methode' },
          { en: 'uses', fr: 'utilise' },
          { en: 'steps to reach $x = 2$', fr: 'pas pour atteindre $x = 2$' },
          { en: 'after 3 steps', fr: 'apres 3 pas' },
        ],
        rows: [
          ['Gradient ($\\alpha = 0.25$)', '$f\'$', '$\\infty$ (limit / limite)', '$x_3 = 1.75$'],
          ['Newton', '$f\'$ et $f\'\'$', '$1$', '$x_1 = 2$ (exact)'],
        ],
      },
      plot: comparePlot,
      outro: { en: 'Concept &#8594; application: curvature information turns many small cautious steps into one exact jump. On general functions Newton is not always one-step, but near the minimum it converges quadratically — the number of correct digits roughly DOUBLES at every iteration — at the price of computing $f\'\'$ (the Hessian in higher dimension).',
               fr: 'Concept &#8594; application : l\'information de courbure transforme beaucoup de petits pas prudents en un saut exact. Sur des fonctions generales Newton n\'est pas toujours en un pas, mais pres du minimum il converge quadratiquement — le nombre de chiffres corrects DOUBLE environ a chaque iteration — au prix du calcul de $f\'\'$ (la hessienne en dimension superieure).' },
    },
  }
}

// ==================================================================
export const GUIDED_APPROXIMATION: Record<string, GScript> = {
  concept_least_squares: buildLeastSquares(),
  concept_orthogonal_polynomials: buildOrthogonal(),
  concept_minimax_approximation: buildMinimax(),
  concept_gradient_descent: buildGradientDescent(),
  concept_newton_optimization: buildNewtonOptimization(),
}
