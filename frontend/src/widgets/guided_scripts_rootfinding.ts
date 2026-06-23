/**
 * Guided scenarios — Module 4: Solving nonlinear equations.
 *
 * STYLE REFERENCE: buildBisection() below. Each script links
 * the CONCEPT (theorem, formula) to its APPLICATION: the student decides,
 * computes, and sees the graphical effect of each decision.
 */

import {
  GScript, GStep, PlotSpec,
  ORANGE, GREEN, BLUE, PURPLE, MUTED,
  fmt,
} from './guided_core'

// ==================================================================
// Bisection — reference script
// ==================================================================
function buildBisection(): GScript {
  const f = (x: number) => x * x - 2
  const TEX = 'x^{2}-2'
  const steps: GStep[] = []

  const markFor = (x: number): { x: number; label: string; color: string } => ({
    x, label: `f(${fmt(x)}) = ${fmt(f(x))}`, color: f(x) < 0 ? ORANGE : GREEN,
  })
  const basePlot = (a: number, b: number, mid?: number): PlotSpec => {
    const span = Math.max(b - a, 1e-9)
    return { xMin: a - span * 0.35, xMax: b + span * 0.35, fns: [{ fn: f }],
             interval: [a, b], mid, marks: [markFor(a), markFor(b)] }
  }

  // ---- step 1: the concept of the sign change, tested graphically
  const wide: PlotSpec = { xMin: -0.5, xMax: 3.2, fns: [{ fn: f }] }
  const itvChoices: [number, number][] = [[0, 1], [1, 2], [2, 3]]
  steps.push({
    plot: wide,
    instruction: {
      en: `We want to solve $f(x) = ${TEX} = 0$. The CONCEPT behind bisection: if $f$ changes sign between $a$ and $b$, a root is trapped in $[a,\\;b]$ (intermediate value theorem). Let us APPLY it.`,
      fr: `On veut resoudre $f(x) = ${TEX} = 0$. Le CONCEPT derriere la dichotomie : si $f$ change de signe entre $a$ et $b$, une racine est piegee dans $[a,\\;b]$ (theoreme des valeurs intermediaires). APPLIQUONS-le.`,
    },
    choice: {
      prompt: { en: 'Test each interval on the graph: which one traps a root?',
                fr: 'Testez chaque intervalle sur le graphe : lequel piege une racine ?' },
      choices: itvChoices.map(([a, b]) => {
        const fa = f(a), fb = f(b)
        const correct = fa * fb < 0
        return {
          label: { en: `$[${fmt(a)},\\;${fmt(b)}]$`, fr: `$[${fmt(a)},\\;${fmt(b)}]$` },
          correct,
          plot: { ...wide, interval: [a, b] as [number, number], marks: [markFor(a), markFor(b)] },
          feedback: correct
            ? { en: `Yes! $f(${fmt(a)}) = ${fmt(fa)} < 0$ and $f(${fmt(b)}) = ${fmt(fb)} > 0$: the curve crosses the axis, a root is trapped. That is the concept in action.`,
                fr: `Oui ! $f(${fmt(a)}) = ${fmt(fa)} < 0$ et $f(${fmt(b)}) = ${fmt(fb)} > 0$ : la courbe traverse l'axe, une racine est piegee. C'est le concept en action.` }
            : { en: `Look at YOUR choice on the graph: $f(${fmt(a)}) = ${fmt(fa)}$ and $f(${fmt(b)}) = ${fmt(fb)}$ have the SAME sign — no guaranteed root there. Try another interval.`,
                fr: `Regardez VOTRE choix sur le graphe : $f(${fmt(a)}) = ${fmt(fa)}$ et $f(${fmt(b)}) = ${fmt(fb)}$ ont le MEME signe — aucune racine garantie ici. Essayez un autre intervalle.` },
        }
      }),
    },
  })

  // ---- 3 iterations: midpoint (input) -> sign (choice) -> half (choice)
  let a = 1, b = 2
  const N = 3
  const rows: string[][] = []
  for (let k = 1; k <= N; k++) {
    const m = (a + b) / 2
    const fm = f(m)
    const fa = f(a)
    const keptLeft = fa * fm < 0
    const na = keptLeft ? a : m
    const nb = keptLeft ? m : b

    steps.push({
      plot: basePlot(a, b),
      instruction: {
        en: `Iteration ${k} of ${N} — APPLY the method: compute the midpoint of $[${fmt(a)},\\;${fmt(b)}]$ yourself and type it.`,
        fr: `Iteration ${k} sur ${N} — APPLIQUEZ la methode : calculez vous-meme le milieu de $[${fmt(a)},\\;${fmt(b)}]$ et tapez-le.`,
      },
      input: {
        label: '$m =$', expected: m, tol: Math.max(Math.abs(m) * 1e-3, (b - a) * 0.02),
        ok: { en: `Correct: $m = \\frac{${fmt(a)}+${fmt(b)}}{2} = ${fmt(m)}$. The orange line shows YOUR cut.`,
              fr: `Exact : $m = \\frac{${fmt(a)}+${fmt(b)}}{2} = ${fmt(m)}$. La ligne orange montre VOTRE coupe.` },
        hint: { en: 'Not quite. The formula is $m = \\frac{a+b}{2}$. Compute it again.',
                fr: 'Pas tout a fait. La formule est $m = \\frac{a+b}{2}$. Recalculez.' },
        reveal: { en: `Here is the computation: $m = \\frac{${fmt(a)}+${fmt(b)}}{2} = ${fmt(m)}$. Type this value.`,
                  fr: `Voici le calcul : $m = \\frac{${fmt(a)}+${fmt(b)}}{2} = ${fmt(m)}$. Tapez cette valeur.` },
        plotOnOk: basePlot(a, b, m),
      },
    })

    steps.push({
      plot: basePlot(a, b, m),
      instruction: {
        en: `We evaluate at your cut: $f(${fmt(m)}) = ${fmt(fm)}$.`,
        fr: `On evalue a votre coupe : $f(${fmt(m)}) = ${fmt(fm)}$.`,
      },
      choice: {
        prompt: { en: 'What is its sign?', fr: 'Quel est son signe ?' },
        choices: [true, false].map(pos => ({
          label: pos ? { en: 'Positive', fr: 'Positif' } : { en: 'Negative', fr: 'Negatif' },
          correct: pos === (fm >= 0),
          feedback: pos === (fm >= 0)
            ? { en: `Right: $f(${fmt(m)}) = ${fmt(fm)}$.`, fr: `Exact : $f(${fmt(m)}) = ${fmt(fm)}$.` }
            : { en: `Look again at the value: $f(${fmt(m)}) = ${fmt(fm)}$.`,
                fr: `Regardez de nouveau la valeur : $f(${fmt(m)}) = ${fmt(fm)}$.` },
        })),
      },
    })

    steps.push({
      plot: basePlot(a, b, m),
      instruction: {
        en: 'Same concept again: the root is trapped where the sign CHANGES.',
        fr: 'Meme concept a nouveau : la racine est piegee la ou le signe CHANGE.',
      },
      choice: {
        prompt: { en: 'Which half still traps the root?', fr: 'Quelle moitie piege encore la racine ?' },
        choices: [true, false].map(left => {
          const ca = left ? a : m, cb = left ? m : b
          const correct = left === keptLeft
          return {
            label: { en: `$[${fmt(ca)},\\;${fmt(cb)}]$`, fr: `$[${fmt(ca)},\\;${fmt(cb)}]$` },
            correct,
            plot: correct ? basePlot(na, nb) : undefined,
            feedback: correct
              ? { en: `Yes: the sign changes between $f(${fmt(ca)}) = ${fmt(f(ca))}$ and $f(${fmt(cb)}) = ${fmt(f(cb))}$. Watch the graph zoom onto YOUR half.`,
                  fr: `Oui : le signe change entre $f(${fmt(ca)}) = ${fmt(f(ca))}$ et $f(${fmt(cb)}) = ${fmt(f(cb))}$. Regardez le graphe zoomer sur VOTRE moitie.` }
              : { en: `No: $f(${fmt(ca)}) = ${fmt(f(ca))}$ and $f(${fmt(cb)}) = ${fmt(f(cb))}$ have the SAME sign — no guaranteed root there.`,
                  fr: `Non : $f(${fmt(ca)}) = ${fmt(f(ca))}$ et $f(${fmt(cb)}) = ${fmt(f(cb))}$ ont le MEME signe — aucune racine garantie ici.` },
          }
        }),
      },
    })

    rows.push([String(k), `$[${fmt(a)},\\;${fmt(b)}]$`, `$${fmt(m)}$`, `$${fmt(fm)}$`,
               `$[${fmt(na)},\\;${fmt(nb)}]$`])
    a = na; b = nb
  }

  const root = Math.SQRT2
  const span = Math.max(b - a, 1e-9)
  return {
    title: { en: 'Apply the bisection yourself', fr: 'Appliquez la dichotomie vous-meme' },
    steps,
    done: {
      intro: { en: 'You did not memorize an example — you APPLIED the concept. Every interval below was YOUR decision:',
               fr: 'Vous n\'avez pas memorise un exemple — vous avez APPLIQUE le concept. Chaque intervalle ci-dessous est VOTRE decision :' },
      eqTex: `f(x) = ${TEX}`,
      table: {
        cols: [
          { en: 'iter.', fr: 'iter.' },
          { en: 'interval', fr: 'intervalle' },
          { en: 'midpoint $m$', fr: 'milieu $m$' },
          { en: '$f(m)$', fr: '$f(m)$' },
          { en: 'kept half', fr: 'moitie gardee' },
        ],
        rows,
      },
      plot: { xMin: a - span * 0.6, xMax: b + span * 0.6, fns: [{ fn: f }], interval: [a, b], root },
      outro: { en: `Concept &#8594; application: sign change traps the root, halving shrinks the trap. After ${N} cuts the interval is $2^{${N}} = ${2 ** N}$ times smaller and $\\sqrt{2} \\approx ${fmt(root)}$ (green dot) is still inside. The computer just repeats YOUR decisions, faster.`,
              fr: `Concept &#8594; application : le changement de signe piege la racine, couper en deux resserre le piege. Apres ${N} coupes, l'intervalle est $2^{${N}} = ${2 ** N}$ fois plus petit et $\\sqrt{2} \\approx ${fmt(root)}$ (point vert) est toujours dedans. L'ordinateur ne fait que repeter VOS decisions, plus vite.` },
    },
  }
}

// ==================================================================
// Fixed point — x = g(x), Heron iteration for sqrt(2)
// ==================================================================
function buildFixedPoint(): GScript {
  const g = (x: number) => (x + 2 / x) / 2          // Heron : converge (g'(sqrt2) = 0)
  const g1 = (x: number) => 2 / x                   // oscille (|g1'(sqrt2)| = 1)
  const idf = (x: number) => x
  const GTEX = 'g(x) = \\frac{1}{2}\\left(x + \\frac{2}{x}\\right)'
  const root = Math.SQRT2

  type Seg = { x1: number; y1: number; x2: number; y2: number; color?: string; dash?: string; width?: number }

  // cobweb: x -> (x, g(x)) vertical, then (g(x), g(x)) horizontal towards y = x
  const cobweb = (gg: (x: number) => number, x0: number, n: number, color: string): Seg[] => {
    const segs: Seg[] = []
    let x = x0
    for (let i = 0; i < n; i++) {
      const y = gg(x)
      segs.push({ x1: x, y1: x, x2: x, y2: y, color, width: 2 })
      segs.push({ x1: x, y1: y, x2: y, y2: y, color, width: 2 })
      x = y
    }
    return segs
  }

  const basePlot = (extra?: Partial<PlotSpec>): PlotSpec => ({
    xMin: 0.6, xMax: 2.4, yMin: 0.6, yMax: 2.4,
    fns: [{ fn: g, color: BLUE }, { fn: idf, color: MUTED, width: 2, dash: '6 4' }],
    ...extra,
  })

  // values of the Heron iterations
  const xs: number[] = [2]
  for (let i = 0; i < 3; i++) xs.push(g(xs[i]))
  const x1 = xs[1]   // 1.5
  const x2 = xs[2]   // 1.41666...

  const steps: GStep[] = []

  // ---- step 1: the concept of the fixed point
  steps.push({
    plot: basePlot({ points: [{ x: root, y: root, color: GREEN, label: 'x* = g(x*)' }] }),
    instruction: {
      en: `To solve $x^{2}-2 = 0$ we REWRITE it as $x = g(x)$ with $${GTEX}$ (Heron's recipe). The CONCEPT: a fixed point $x^{*} = g(x^{*})$ is the INTERSECTION of the blue curve $y = g(x)$ and the dashed line $y = x$. Iterating $x_{n+1} = g(x_{n})$ should walk toward it.`,
      fr: `Pour resoudre $x^{2}-2 = 0$ on la REECRIT en $x = g(x)$ avec $${GTEX}$ (recette de Heron). Le CONCEPT : un point fixe $x^{*} = g(x^{*})$ est l'INTERSECTION de la courbe bleue $y = g(x)$ et de la droite pointillee $y = x$. Iterer $x_{n+1} = g(x_{n})$ doit marcher vers lui.`,
    },
  })

  // ---- step 2: choice of the rewriting (graphical effect: cobwebs)
  const cobBad = cobweb(g1, 2, 3, ORANGE)
  const cobGood = cobweb(g, 2, 3, GREEN)
  steps.push({
    plot: basePlot(),
    instruction: {
      en: `The same equation $x^{2}-2 = 0$ has MANY rewritings: $g_{1}(x) = \\frac{2}{x}$ or $g_{2}(x) = \\frac{1}{2}\\left(x + \\frac{2}{x}\\right)$. Both have $\\sqrt{2}$ as fixed point — but iteration does NOT behave the same. Test them from $x_{0} = 2$.`,
      fr: `La meme equation $x^{2}-2 = 0$ a PLUSIEURS reecritures : $g_{1}(x) = \\frac{2}{x}$ ou $g_{2}(x) = \\frac{1}{2}\\left(x + \\frac{2}{x}\\right)$. Toutes deux ont $\\sqrt{2}$ comme point fixe — mais l'iteration ne se comporte PAS pareil. Testez-les depuis $x_{0} = 2$.`,
    },
    choice: {
      prompt: { en: 'Which rewriting makes the iteration converge?',
                fr: 'Quelle reecriture fait converger l\'iteration ?' },
      choices: [
        {
          label: { en: '$g_{1}(x) = \\frac{2}{x}$', fr: '$g_{1}(x) = \\frac{2}{x}$' },
          correct: false,
          plot: { xMin: 0.6, xMax: 2.4, yMin: 0.6, yMax: 2.4,
                  fns: [{ fn: g1, color: ORANGE }, { fn: idf, color: MUTED, width: 2, dash: '6 4' }],
                  segs: cobBad,
                  points: [{ x: 2, y: 2, color: ORANGE, label: 'x₀ = 2' }] },
          feedback: {
            en: `Look at the orange path (the "cobweb"): $2 \\to 1 \\to 2 \\to 1 \\dots$ it goes round and round forever, never approaching $\\sqrt{2}$. This rewriting OSCILLATES. Pick the other one.`,
            fr: `Regardez le chemin orange (le "cobweb") : $2 \\to 1 \\to 2 \\to 1 \\dots$ il tourne en rond pour toujours, sans jamais approcher $\\sqrt{2}$. Cette reecriture OSCILLE. Choisissez l'autre.`,
          },
        },
        {
          label: { en: '$g_{2}(x) = \\frac{1}{2}\\left(x + \\frac{2}{x}\\right)$', fr: '$g_{2}(x) = \\frac{1}{2}\\left(x + \\frac{2}{x}\\right)$' },
          correct: true,
          plot: basePlot({ segs: cobGood,
                           points: [{ x: 2, y: 2, color: BLUE, label: 'x₀ = 2' },
                                    { x: root, y: root, color: GREEN, label: 'x*' }] }),
          feedback: {
            en: `Yes! The green staircase rushes straight into the intersection: each step lands much closer to $\\sqrt{2}$. Same equation, different rewriting, totally different behavior — THAT is why the choice of $g$ matters.`,
            fr: `Oui ! L'escalier vert fonce droit vers l'intersection : chaque pas atterrit bien plus pres de $\\sqrt{2}$. Meme equation, autre reecriture, comportement totalement different — VOILA pourquoi le choix de $g$ compte.`,
          },
        },
      ],
    },
  })

  // ---- step 3: computation of x1 = g(2)
  steps.push({
    plot: basePlot({ points: [{ x: 2, y: 2, color: BLUE, label: 'x₀ = 2' }] }),
    instruction: {
      en: `APPLY the iteration with $g(x) = \\frac{1}{2}\\left(x + \\frac{2}{x}\\right)$ from $x_{0} = 2$: compute $x_{1} = g(x_{0})$ yourself and type it.`,
      fr: `APPLIQUEZ l'iteration avec $g(x) = \\frac{1}{2}\\left(x + \\frac{2}{x}\\right)$ depuis $x_{0} = 2$ : calculez vous-meme $x_{1} = g(x_{0})$ et tapez-le.`,
    },
    input: {
      label: '$x_1 =$', expected: x1, tol: Math.abs(x1) * 0.01,
      ok: { en: `Correct: $x_{1} = \\frac{1}{2}\\left(2 + \\frac{2}{2}\\right) = ${fmt(x1)}$. Watch YOUR first cobweb step: down to the curve, across to $y = x$.`,
            fr: `Exact : $x_{1} = \\frac{1}{2}\\left(2 + \\frac{2}{2}\\right) = ${fmt(x1)}$. Regardez VOTRE premier pas de cobweb : descendre sur la courbe, traverser vers $y = x$.` },
      hint: { en: 'Not quite. The formula is $x_{1} = g(x_{0}) = \\frac{1}{2}\\left(x_{0} + \\frac{2}{x_{0}}\\right)$ with $x_{0} = 2$.',
              fr: 'Pas tout a fait. La formule est $x_{1} = g(x_{0}) = \\frac{1}{2}\\left(x_{0} + \\frac{2}{x_{0}}\\right)$ avec $x_{0} = 2$.' },
      reveal: { en: `Here is the computation: $x_{1} = \\frac{1}{2}\\left(2 + \\frac{2}{2}\\right) = \\frac{1}{2}(2+1) = ${fmt(x1)}$. Type this value.`,
                fr: `Voici le calcul : $x_{1} = \\frac{1}{2}\\left(2 + \\frac{2}{2}\\right) = \\frac{1}{2}(2+1) = ${fmt(x1)}$. Tapez cette valeur.` },
      plotOnOk: basePlot({ segs: cobweb(g, 2, 1, GREEN),
                           points: [{ x: 2, y: 2, color: BLUE, label: 'x₀ = 2' },
                                    { x: x1, y: x1, color: GREEN, label: `x₁ = ${fmt(x1)}` }] }),
    },
  })

  // ---- step 4: computation of x2 = g(1.5)
  steps.push({
    plot: basePlot({ segs: cobweb(g, 2, 1, GREEN),
                     points: [{ x: x1, y: x1, color: GREEN, label: `x₁ = ${fmt(x1)}` }] }),
    instruction: {
      en: `One more step of the SAME recipe: compute $x_{2} = g(x_{1}) = g(${fmt(x1)})$ and type it (4 decimals).`,
      fr: `Encore un pas de la MEME recette : calculez $x_{2} = g(x_{1}) = g(${fmt(x1)})$ et tapez-le (4 decimales).`,
    },
    input: {
      label: '$x_2 =$', expected: x2, tol: Math.abs(x2) * 0.01,
      ok: { en: `Correct: $x_{2} = \\frac{1}{2}\\left(${fmt(x1)} + \\frac{2}{${fmt(x1)}}\\right) = ${fmt(x2)}$. The staircase shrinks fast — you are already at 3 correct digits of $\\sqrt{2}$.`,
            fr: `Exact : $x_{2} = \\frac{1}{2}\\left(${fmt(x1)} + \\frac{2}{${fmt(x1)}}\\right) = ${fmt(x2)}$. L'escalier retrecit vite — vous avez deja 3 chiffres corrects de $\\sqrt{2}$.` },
      hint: { en: `Not quite. Same formula, new input: $x_{2} = \\frac{1}{2}\\left(x_{1} + \\frac{2}{x_{1}}\\right)$ with $x_{1} = ${fmt(x1)}$.`,
              fr: `Pas tout a fait. Meme formule, nouvelle entree : $x_{2} = \\frac{1}{2}\\left(x_{1} + \\frac{2}{x_{1}}\\right)$ avec $x_{1} = ${fmt(x1)}$.` },
      reveal: { en: `Here is the computation: $x_{2} = \\frac{1}{2}\\left(${fmt(x1)} + \\frac{2}{${fmt(x1)}}\\right) = \\frac{1}{2}(${fmt(x1)} + ${fmt(2 / x1)}) = ${fmt(x2)}$. Type this value.`,
                fr: `Voici le calcul : $x_{2} = \\frac{1}{2}\\left(${fmt(x1)} + \\frac{2}{${fmt(x1)}}\\right) = \\frac{1}{2}(${fmt(x1)} + ${fmt(2 / x1)}) = ${fmt(x2)}$. Tapez cette valeur.` },
      plotOnOk: basePlot({ segs: cobweb(g, 2, 2, GREEN),
                           points: [{ x: x1, y: x1, color: GREEN, label: `x₁ = ${fmt(x1)}` },
                                    { x: x2, y: x2, color: PURPLE, label: `x₂ = ${fmt(x2)}` }] }),
    },
  })

  // ---- step 5: the convergence criterion |g'(x*)| < 1
  steps.push({
    plot: basePlot({ segs: cobweb(g, 2, 3, GREEN),
                     points: [{ x: root, y: root, color: GREEN, label: 'x*' }] }),
    instruction: {
      en: `Why did $g_{2}$ converge while $g_{1}$ went in circles? The CONCEPT behind it is the slope of $g$ AT the fixed point. Here $g_{2}'(x) = \\frac{1}{2}\\left(1 - \\frac{2}{x^{2}}\\right)$, so $g_{2}'(\\sqrt{2}) = 0$, while $g_{1}'(\\sqrt{2}) = -1$.`,
      fr: `Pourquoi $g_{2}$ a-t-elle converge alors que $g_{1}$ tournait en rond ? Le CONCEPT derriere est la pente de $g$ AU point fixe. Ici $g_{2}'(x) = \\frac{1}{2}\\left(1 - \\frac{2}{x^{2}}\\right)$, donc $g_{2}'(\\sqrt{2}) = 0$, alors que $g_{1}'(\\sqrt{2}) = -1$.`,
    },
    choice: {
      prompt: { en: 'What is the convergence criterion for fixed-point iteration?',
                fr: 'Quel est le critere de convergence de l\'iteration de point fixe ?' },
      choices: [
        {
          label: { en: '$|g\'(x^{*})| < 1$', fr: '$|g\'(x^{*})| < 1$' },
          correct: true,
          feedback: {
            en: `Exactly. Each iteration multiplies the error by roughly $|g'(x^{*})|$: below 1 the error shrinks (contraction). For Heron $g'(\\sqrt{2}) = 0$ — the error shrinks dramatically, which is the fast staircase you drew.`,
            fr: `Exactement. Chaque iteration multiplie l'erreur par environ $|g'(x^{*})|$ : en dessous de 1 l'erreur retrecit (contraction). Pour Heron $g'(\\sqrt{2}) = 0$ — l'erreur fond, c'est l'escalier rapide que vous avez dessine.`,
          },
        },
        {
          label: { en: '$g(x^{*}) > 0$', fr: '$g(x^{*}) > 0$' },
          correct: false,
          feedback: {
            en: `No: the VALUE of $g$ at the fixed point only says where the point is, not whether iterates approach it. Think about what stretches or shrinks the error at each step.`,
            fr: `Non : la VALEUR de $g$ au point fixe dit seulement ou est le point, pas si les iteres s'en approchent. Pensez a ce qui etire ou retrecit l'erreur a chaque pas.`,
          },
        },
        {
          label: { en: '$|g\'(x^{*})| > 1$', fr: '$|g\'(x^{*})| > 1$' },
          correct: false,
          feedback: {
            en: `The opposite: a slope steeper than 1 AMPLIFIES the error — the cobweb spirals away. Convergence needs the error to shrink at each step.`,
            fr: `Le contraire : une pente plus raide que 1 AMPLIFIE l'erreur — le cobweb s'eloigne en spirale. La convergence exige que l'erreur retrecisse a chaque pas.`,
          },
        },
      ],
    },
  })

  const rows: string[][] = []
  for (let n = 0; n < xs.length; n++) {
    rows.push([`$x_{${n}}$`, `$${fmt(xs[n], 6)}$`, `$${fmt(Math.abs(xs[n] - root), 6)}$`])
  }

  return {
    title: { en: 'Apply fixed-point iteration yourself', fr: 'Appliquez le point fixe vous-meme' },
    steps,
    done: {
      intro: { en: 'You chose the right rewriting and walked the cobweb yourself. Here are YOUR iterates:',
               fr: 'Vous avez choisi la bonne reecriture et parcouru le cobweb vous-meme. Voici VOS iteres :' },
      eqTex: `x_{n+1} = g(x_{n}), \\quad ${GTEX}`,
      table: {
        cols: [
          { en: 'iterate', fr: 'itere' },
          { en: 'value', fr: 'valeur' },
          { en: 'error $|x_{n} - \\sqrt{2}|$', fr: 'erreur $|x_{n} - \\sqrt{2}|$' },
        ],
        rows,
      },
      plot: basePlot({ segs: cobweb(g, 2, 3, GREEN),
                       points: [{ x: 2, y: 2, color: BLUE, label: 'x₀' },
                                { x: root, y: root, color: GREEN, label: 'x* = √2' }] }),
      outro: { en: `Concept &#8594; application: a root of $x^{2}-2$ became a FIXED POINT $x^{*} = g(x^{*})$, the intersection of $y = g(x)$ and $y = x$. Because $|g'(x^{*})| < 1$ (here even $0$), YOUR staircase contracted onto $\\sqrt{2} \\approx ${fmt(root)}$ in just ${xs.length - 1} steps.`,
              fr: `Concept &#8594; application : une racine de $x^{2}-2$ est devenue un POINT FIXE $x^{*} = g(x^{*})$, l'intersection de $y = g(x)$ et $y = x$. Comme $|g'(x^{*})| < 1$ (ici meme $0$), VOTRE escalier s'est contracte sur $\\sqrt{2} \\approx ${fmt(root)}$ en seulement ${xs.length - 1} pas.` },
    },
  }
}

// ==================================================================
// Newton-Raphson — follow the tangent down to the axis
// ==================================================================
function buildNewtonRaphson(): GScript {
  const f = (x: number) => x * x - 2
  const df = (x: number) => 2 * x
  const TEX = 'x^{2}-2'
  const root = Math.SQRT2

  type Seg = { x1: number; y1: number; x2: number; y2: number; color?: string; dash?: string; width?: number }

  // tangent at x0 drawn between xa and xb: y = f(x0) + f'(x0)(x - x0)
  const tangentSeg = (x0: number, xa: number, xb: number, color: string): Seg => ({
    x1: xa, y1: f(x0) + df(x0) * (xa - x0),
    x2: xb, y2: f(x0) + df(x0) * (xb - x0),
    color, width: 2, dash: '7 4',
  })
  // vertical dashed line from the axis up to the curve
  const dropSeg = (x0: number, color: string): Seg => ({
    x1: x0, y1: 0, x2: x0, y2: f(x0), color, dash: '3 4', width: 1.5,
  })

  // Newton iterations
  const xs: number[] = [2]
  for (let i = 0; i < 3; i++) xs.push(xs[i] - f(xs[i]) / df(xs[i]))
  const x1 = xs[1]   // 1.5
  const x2 = xs[2]   // 1.41666...

  const basePlot = (extra?: Partial<PlotSpec>): PlotSpec => ({
    xMin: 0.8, xMax: 2.4, fns: [{ fn: f, color: BLUE }], ...extra,
  })

  const steps: GStep[] = []

  // ---- step 1: the concept of the tangent
  steps.push({
    plot: basePlot({ points: [{ x: 2, y: f(2), color: ORANGE, label: '(2, f(2))' }] }),
    instruction: {
      en: `Same equation $f(x) = ${TEX} = 0$, new CONCEPT: at the current point, replace the curve by its TANGENT line — easy to solve — and follow it down to the axis. The crossing becomes the next guess: $x_{n+1} = x_{n} - \\frac{f(x_{n})}{f'(x_{n})}$, with $f'(x) = 2x$. Start at $x_{0} = 2$.`,
      fr: `Meme equation $f(x) = ${TEX} = 0$, nouveau CONCEPT : au point courant, on remplace la courbe par sa TANGENTE — facile a resoudre — et on la suit jusqu'a l'axe. L'intersection devient le prochain candidat : $x_{n+1} = x_{n} - \\frac{f(x_{n})}{f'(x_{n})}$, avec $f'(x) = 2x$. On part de $x_{0} = 2$.`,
    },
  })

  // ---- step 2: choice — where does the tangent cross the axis?
  steps.push({
    plot: basePlot({ points: [{ x: 2, y: f(2), color: ORANGE, label: '(2, f(2)) = (2, 2)' }] }),
    instruction: {
      en: `At $x_{0} = 2$: $f(2) = 2$ and the slope is $f'(2) = 4$. The tangent is the line $y = 2 + 4(x - 2)$.`,
      fr: `En $x_{0} = 2$ : $f(2) = 2$ et la pente vaut $f'(2) = 4$. La tangente est la droite $y = 2 + 4(x - 2)$.`,
    },
    choice: {
      prompt: { en: 'Where does this tangent cross the x-axis?',
                fr: 'Ou cette tangente coupe-t-elle l\'axe des x ?' },
      choices: [
        {
          label: { en: '$x = 1$', fr: '$x = 1$' },
          correct: false,
          plot: basePlot({ segs: [tangentSeg(2, 1.0, 2.3, ORANGE)],
                           points: [{ x: 2, y: f(2), color: ORANGE, label: 'x₀ = 2' },
                                    { x: 1, y: 0, color: MUTED, label: 'x = 1 ?' }] }),
          feedback: {
            en: `Check on the graph: the dashed tangent is still well below the axis... no wait, at $x = 1$ the tangent gives $2 + 4(1-2) = -2 \\ne 0$. Solve $2 + 4(x-2) = 0$ properly.`,
            fr: `Verifiez sur le graphe : en $x = 1$ la tangente donne $2 + 4(1-2) = -2 \\ne 0$. Resolvez $2 + 4(x-2) = 0$ correctement.`,
          },
        },
        {
          label: { en: '$x = 1.5$', fr: '$x = 1{,}5$' },
          correct: true,
          plot: basePlot({ segs: [tangentSeg(2, 1.2, 2.3, ORANGE), dropSeg(2, MUTED)],
                           points: [{ x: 2, y: f(2), color: ORANGE, label: 'x₀ = 2' },
                                    { x: 1.5, y: 0, color: GREEN, label: 'x₁ = 1.5' }] }),
          feedback: {
            en: `Yes! $2 + 4(x-2) = 0 \\Rightarrow x = 2 - \\frac{2}{4} = 1.5$. Look at the graph: the orange tangent slides from $(2,\\;2)$ straight down to the axis at $1.5$ — that IS one Newton step.`,
            fr: `Oui ! $2 + 4(x-2) = 0 \\Rightarrow x = 2 - \\frac{2}{4} = 1{,}5$. Regardez le graphe : la tangente orange glisse de $(2,\\;2)$ jusqu'a l'axe en $1{,}5$ — c'est EXACTEMENT un pas de Newton.`,
          },
        },
        {
          label: { en: '$x = 1.75$', fr: '$x = 1{,}75$' },
          correct: false,
          plot: basePlot({ segs: [tangentSeg(2, 1.2, 2.3, ORANGE)],
                           points: [{ x: 2, y: f(2), color: ORANGE, label: 'x₀ = 2' },
                                    { x: 1.75, y: 0, color: MUTED, label: 'x = 1.75 ?' }] }),
          feedback: {
            en: `At $x = 1.75$ the tangent gives $2 + 4(1.75 - 2) = 1 \\ne 0$: still above the axis. Solve $2 + 4(x-2) = 0$ for $x$.`,
            fr: `En $x = 1{,}75$ la tangente donne $2 + 4(1{,}75 - 2) = 1 \\ne 0$ : encore au-dessus de l'axe. Resolvez $2 + 4(x-2) = 0$ en $x$.`,
          },
        },
      ],
    },
  })

  // ---- step 3: input x1 via the formula
  steps.push({
    plot: basePlot({ segs: [tangentSeg(2, 1.2, 2.3, ORANGE)],
                     points: [{ x: 2, y: f(2), color: ORANGE, label: 'x₀ = 2' }] }),
    instruction: {
      en: `Now write the SAME geometry as a formula and APPLY it: $x_{1} = x_{0} - \\frac{f(x_{0})}{f'(x_{0})}$ with $f(2) = 2$ and $f'(2) = 4$. Type $x_{1}$.`,
      fr: `Ecrivez maintenant la MEME geometrie en formule et APPLIQUEZ-la : $x_{1} = x_{0} - \\frac{f(x_{0})}{f'(x_{0})}$ avec $f(2) = 2$ et $f'(2) = 4$. Tapez $x_{1}$.`,
    },
    input: {
      label: '$x_1 =$', expected: x1, tol: Math.abs(x1) * 0.01,
      ok: { en: `Correct: $x_{1} = 2 - \\frac{2}{4} = ${fmt(x1)}$ — exactly where YOUR tangent crossed the axis. The formula and the picture are the same thing.`,
            fr: `Exact : $x_{1} = 2 - \\frac{2}{4} = ${fmt(x1)}$ — exactement la ou VOTRE tangente coupait l'axe. La formule et le dessin sont la meme chose.` },
      hint: { en: 'Not quite. The formula is $x_{1} = x_{0} - \\frac{f(x_{0})}{f\'(x_{0})}$: subtract the ratio from $x_{0} = 2$.',
              fr: 'Pas tout a fait. La formule est $x_{1} = x_{0} - \\frac{f(x_{0})}{f\'(x_{0})}$ : soustrayez le rapport de $x_{0} = 2$.' },
      reveal: { en: `Here is the computation: $x_{1} = 2 - \\frac{f(2)}{f'(2)} = 2 - \\frac{2}{4} = ${fmt(x1)}$. Type this value.`,
                fr: `Voici le calcul : $x_{1} = 2 - \\frac{f(2)}{f'(2)} = 2 - \\frac{2}{4} = ${fmt(x1)}$. Tapez cette valeur.` },
      plotOnOk: basePlot({ segs: [tangentSeg(2, 1.2, 2.3, ORANGE), dropSeg(x1, MUTED)],
                           points: [{ x: 2, y: f(2), color: ORANGE, label: 'x₀ = 2' },
                                    { x: x1, y: 0, color: GREEN, label: `x₁ = ${fmt(x1)}` }] }),
    },
  })

  // ---- step 4: input x2 (second tangent)
  steps.push({
    plot: basePlot({ segs: [tangentSeg(2, 1.2, 2.3, MUTED), dropSeg(x1, MUTED)],
                     points: [{ x: x1, y: f(x1), color: ORANGE, label: '(x₁, f(x₁))' }] }),
    instruction: {
      en: `Repeat from YOUR new point: $f(${fmt(x1)}) = ${fmt(f(x1))}$ and $f'(${fmt(x1)}) = ${fmt(df(x1))}$. Compute $x_{2} = x_{1} - \\frac{f(x_{1})}{f'(x_{1})}$ (4 decimals).`,
      fr: `Recommencez depuis VOTRE nouveau point : $f(${fmt(x1)}) = ${fmt(f(x1))}$ et $f'(${fmt(x1)}) = ${fmt(df(x1))}$. Calculez $x_{2} = x_{1} - \\frac{f(x_{1})}{f'(x_{1})}$ (4 decimales).`,
    },
    input: {
      label: '$x_2 =$', expected: x2, tol: Math.abs(x2) * 0.01,
      ok: { en: `Correct: $x_{2} = ${fmt(x1)} - \\frac{${fmt(f(x1))}}{${fmt(df(x1))}} = ${fmt(x2)}$. A second, flatter tangent appears — and you are already at $\\sqrt{2}$ to 3 digits.`,
            fr: `Exact : $x_{2} = ${fmt(x1)} - \\frac{${fmt(f(x1))}}{${fmt(df(x1))}} = ${fmt(x2)}$. Une seconde tangente, plus plate, apparait — et vous etes deja a $\\sqrt{2}$ a 3 chiffres pres.` },
      hint: { en: `Not quite. Same recipe, new point: $x_{2} = x_{1} - \\frac{f(x_{1})}{f'(x_{1})}$ with $x_{1} = ${fmt(x1)}$, $f(x_{1}) = ${fmt(f(x1))}$, $f'(x_{1}) = ${fmt(df(x1))}$.`,
              fr: `Pas tout a fait. Meme recette, nouveau point : $x_{2} = x_{1} - \\frac{f(x_{1})}{f'(x_{1})}$ avec $x_{1} = ${fmt(x1)}$, $f(x_{1}) = ${fmt(f(x1))}$, $f'(x_{1}) = ${fmt(df(x1))}$.` },
      reveal: { en: `Here is the computation: $x_{2} = ${fmt(x1)} - \\frac{${fmt(f(x1))}}{${fmt(df(x1))}} = ${fmt(x1)} - ${fmt(f(x1) / df(x1), 6)} = ${fmt(x2)}$. Type this value.`,
                fr: `Voici le calcul : $x_{2} = ${fmt(x1)} - \\frac{${fmt(f(x1))}}{${fmt(df(x1))}} = ${fmt(x1)} - ${fmt(f(x1) / df(x1), 6)} = ${fmt(x2)}$. Tapez cette valeur.` },
      plotOnOk: { xMin: 1.3, xMax: 1.65, fns: [{ fn: f, color: BLUE }],
                  segs: [tangentSeg(x1, 1.32, 1.62, ORANGE), dropSeg(x1, MUTED)],
                  points: [{ x: x1, y: f(x1), color: ORANGE, label: `x₁ = ${fmt(x1)}` },
                           { x: x2, y: 0, color: GREEN, label: `x₂ = ${fmt(x2)}` }],
                  root },
    },
  })

  // ---- step 5: why so fast? (conceptual choice)
  steps.push({
    plot: { xMin: 1.3, xMax: 1.65, fns: [{ fn: f, color: BLUE }],
            segs: [tangentSeg(x1, 1.32, 1.62, ORANGE)],
            points: [{ x: x2, y: 0, color: GREEN, label: `x₂ = ${fmt(x2)}` }], root },
    instruction: {
      en: `Look at your residuals: $f(x_{0}) = ${fmt(f(xs[0]))}$, $f(x_{1}) = ${fmt(f(x1))}$, $f(x_{2}) = ${fmt(f(x2), 6)}$. Each step roughly SQUARES the error.`,
      fr: `Regardez vos residus : $f(x_{0}) = ${fmt(f(xs[0]))}$, $f(x_{1}) = ${fmt(f(x1))}$, $f(x_{2}) = ${fmt(f(x2), 6)}$. Chaque pas met l'erreur environ AU CARRE.`,
    },
    choice: {
      prompt: { en: 'What is this type of convergence called?',
                fr: 'Comment appelle-t-on ce type de convergence ?' },
      choices: [
        {
          label: { en: 'Linear', fr: 'Lineaire' },
          correct: false,
          feedback: { en: 'Linear convergence (like bisection) gains a FIXED factor per step. Here the number of correct digits roughly DOUBLES each step — that is faster.',
                      fr: 'La convergence lineaire (comme la dichotomie) gagne un facteur FIXE par pas. Ici le nombre de chiffres corrects DOUBLE environ a chaque pas — c\'est plus rapide.' },
        },
        {
          label: { en: 'Quadratic', fr: 'Quadratique' },
          correct: true,
          feedback: { en: `Yes: $|e_{n+1}| \\approx C\\,|e_{n}|^{2}$ — quadratic convergence. The price: you must know $f'(x)$ and evaluate it at every step.`,
                      fr: `Oui : $|e_{n+1}| \\approx C\\,|e_{n}|^{2}$ — convergence quadratique. Le prix a payer : il faut connaitre $f'(x)$ et l'evaluer a chaque pas.` },
        },
        {
          label: { en: 'Logarithmic', fr: 'Logarithmique' },
          correct: false,
          feedback: { en: 'Logarithmic would be far SLOWER than what you observe. Compare the errors: each one is about the square of the previous one.',
                      fr: 'Logarithmique serait bien plus LENT que ce que vous observez. Comparez les erreurs : chacune est environ le carre de la precedente.' },
        },
      ],
    },
  })

  const rows: string[][] = []
  for (let n = 0; n < xs.length; n++) {
    rows.push([`$x_{${n}}$`, `$${fmt(xs[n], 6)}$`, `$${fmt(f(xs[n]), 8)}$`])
  }

  return {
    title: { en: 'Apply Newton-Raphson yourself', fr: 'Appliquez Newton-Raphson vous-meme' },
    steps,
    done: {
      intro: { en: 'You followed each tangent down to the axis yourself. Here are YOUR iterates:',
               fr: 'Vous avez suivi chaque tangente jusqu\'a l\'axe vous-meme. Voici VOS iteres :' },
      eqTex: `x_{n+1} = x_{n} - \\frac{f(x_{n})}{f'(x_{n})}, \\quad f(x) = ${TEX}`,
      table: {
        cols: [
          { en: 'iterate', fr: 'itere' },
          { en: 'value $x_{n}$', fr: 'valeur $x_{n}$' },
          { en: 'residual $f(x_{n})$', fr: 'residu $f(x_{n})$' },
        ],
        rows,
      },
      plot: basePlot({ segs: [tangentSeg(2, 1.2, 2.3, ORANGE), tangentSeg(x1, 1.25, 1.7, PURPLE)],
                       points: [{ x: 2, y: f(2), color: ORANGE, label: 'x₀' },
                                { x: x1, y: f(x1), color: PURPLE, label: 'x₁' },
                                { x: x2, y: 0, color: GREEN, label: 'x₂' }],
                       root }),
      outro: { en: `Concept &#8594; application: each TANGENT is a local straight-line model of $f$, and solving the model gives the next guess. Quadratic convergence took you from $2$ to $${fmt(xs[3], 8)}$ in 3 steps — $\\sqrt{2} \\approx ${fmt(root, 8)}$ (green dot). Bisection would need about 20 steps for the same accuracy.`,
              fr: `Concept &#8594; application : chaque TANGENTE est un modele droit local de $f$, et resoudre le modele donne le candidat suivant. La convergence quadratique vous a menes de $2$ a $${fmt(xs[3], 8)}$ en 3 pas — $\\sqrt{2} \\approx ${fmt(root, 8)}$ (point vert). La dichotomie aurait besoin d'environ 20 pas pour la meme precision.` },
    },
  }
}

// ==================================================================
// Secant — replace the tangent by the chord through two points
// ==================================================================
function buildSecant(): GScript {
  const f = (x: number) => x * x - 2
  const TEX = 'x^{2}-2'
  const root = Math.SQRT2

  type Seg = { x1: number; y1: number; x2: number; y2: number; color?: string; dash?: string; width?: number }

  // line through (xa, f(xa)) and (xb, f(xb)) drawn between u and v
  const secantSeg = (xa: number, xb: number, u: number, v: number, color: string): Seg => {
    const slope = (f(xb) - f(xa)) / (xb - xa)
    return { x1: u, y1: f(xa) + slope * (u - xa), x2: v, y2: f(xa) + slope * (v - xa),
             color, width: 2, dash: '7 4' }
  }

  // secant iterations from x0 = 2, x1 = 1.5
  const xs: number[] = [2, 1.5]
  for (let i = 0; i < 3; i++) {
    const a = xs[xs.length - 2], b = xs[xs.length - 1]
    xs.push(b - f(b) * (b - a) / (f(b) - f(a)))
  }
  const x0 = xs[0], x1 = xs[1], x2 = xs[2], x3 = xs[3]

  const basePlot = (extra?: Partial<PlotSpec>): PlotSpec => ({
    xMin: 1.1, xMax: 2.3, fns: [{ fn: f, color: BLUE }], ...extra,
  })

  const steps: GStep[] = []

  // ---- step 1: the concept — no derivative
  steps.push({
    plot: basePlot({ points: [{ x: x0, y: f(x0), color: ORANGE, label: '(x₀, f(x₀))' },
                              { x: x1, y: f(x1), color: PURPLE, label: '(x₁, f(x₁))' }] }),
    instruction: {
      en: `Same equation $f(x) = ${TEX} = 0$. Newton needs the derivative $f'$ — but suppose we do NOT have it. New CONCEPT: through the last TWO points $(x_{0}, f(x_{0}))$ and $(x_{1}, f(x_{1}))$ draw the SECANT line and follow it down to the axis. Start: $x_{0} = 2$, $x_{1} = 1.5$.`,
      fr: `Meme equation $f(x) = ${TEX} = 0$. Newton exige la derivee $f'$ — mais supposons qu'on ne l'ait PAS. Nouveau CONCEPT : par les DEUX derniers points $(x_{0}, f(x_{0}))$ et $(x_{1}, f(x_{1}))$ on trace la SECANTE et on la suit jusqu'a l'axe. Depart : $x_{0} = 2$, $x_{1} = 1{,}5$.`,
    },
  })

  // ---- step 2: conceptual choice — why a secant?
  steps.push({
    plot: basePlot({ points: [{ x: x0, y: f(x0), color: ORANGE, label: 'x₀ = 2' },
                              { x: x1, y: f(x1), color: PURPLE, label: 'x₁ = 1.5' }] }),
    instruction: {
      en: `Before computing, make sure the idea is clear. The slope of the secant, $\\frac{f(x_{1}) - f(x_{0})}{x_{1} - x_{0}}$, plays the role of $f'$ in Newton's formula.`,
      fr: `Avant de calculer, assurons-nous de l'idee. La pente de la secante, $\\frac{f(x_{1}) - f(x_{0})}{x_{1} - x_{0}}$, joue le role de $f'$ dans la formule de Newton.`,
    },
    choice: {
      prompt: { en: 'Why replace the tangent by a secant?',
                fr: 'Pourquoi remplacer la tangente par une secante ?' },
      choices: [
        {
          label: { en: '$f\'$ may be unknown or expensive', fr: '$f\'$ peut etre inconnue ou couteuse' },
          correct: true,
          plot: basePlot({ segs: [secantSeg(x0, x1, 1.2, 2.2, ORANGE)],
                           points: [{ x: x0, y: f(x0), color: ORANGE, label: 'x₀ = 2' },
                                    { x: x1, y: f(x1), color: PURPLE, label: 'x₁ = 1.5' }] }),
          feedback: {
            en: `Exactly. Many real functions come from simulations or measurements: no formula for $f'$. The secant uses only VALUES of $f$ — see the dashed line through your two points: it imitates the tangent without any derivative.`,
            fr: `Exactement. Beaucoup de fonctions reelles viennent de simulations ou de mesures : pas de formule pour $f'$. La secante n'utilise que des VALEURS de $f$ — voyez la droite pointillee par vos deux points : elle imite la tangente sans aucune derivee.`,
          },
        },
        {
          label: { en: 'The secant always converges faster', fr: 'La secante converge toujours plus vite' },
          correct: false,
          feedback: {
            en: `No — the secant is slightly SLOWER than Newton (order $\\approx 1.618$ vs $2$). Its advantage is elsewhere: what does Newton require at every step that the secant does not?`,
            fr: `Non — la secante est legerement plus LENTE que Newton (ordre $\\approx 1{,}618$ contre $2$). Son avantage est ailleurs : que demande Newton a chaque pas que la secante ne demande pas ?`,
          },
        },
        {
          label: { en: 'It guarantees a bracketed root', fr: 'Elle garantit une racine encadree' },
          correct: false,
          feedback: {
            en: `No — unlike bisection, the secant does NOT keep the root trapped between its two points (they may end up on the same side). Think about what ingredient of Newton it removes.`,
            fr: `Non — contrairement a la dichotomie, la secante ne garde PAS la racine piegee entre ses deux points (ils peuvent finir du meme cote). Pensez a l'ingredient de Newton qu'elle supprime.`,
          },
        },
      ],
    },
  })

  // ---- step 3: input x2
  steps.push({
    plot: basePlot({ segs: [secantSeg(x0, x1, 1.2, 2.2, ORANGE)],
                     points: [{ x: x0, y: f(x0), color: ORANGE, label: 'x₀ = 2' },
                              { x: x1, y: f(x1), color: PURPLE, label: 'x₁ = 1.5' }] }),
    instruction: {
      en: `APPLY it: $x_{2} = x_{1} - f(x_{1})\\,\\frac{x_{1} - x_{0}}{f(x_{1}) - f(x_{0})}$ with $f(2) = ${fmt(f(x0))}$ and $f(1.5) = ${fmt(f(x1))}$. Compute $x_{2}$ (4 decimals).`,
      fr: `APPLIQUEZ : $x_{2} = x_{1} - f(x_{1})\\,\\frac{x_{1} - x_{0}}{f(x_{1}) - f(x_{0})}$ avec $f(2) = ${fmt(f(x0))}$ et $f(1{,}5) = ${fmt(f(x1))}$. Calculez $x_{2}$ (4 decimales).`,
    },
    input: {
      label: '$x_2 =$', expected: x2, tol: Math.abs(x2) * 0.01,
      ok: { en: `Correct: $x_{2} = ${fmt(x1)} - ${fmt(f(x1))} \\cdot \\frac{${fmt(x1)} - ${fmt(x0)}}{${fmt(f(x1))} - ${fmt(f(x0))}} = ${fmt(x2)}$ — exactly where YOUR secant crosses the axis.`,
            fr: `Exact : $x_{2} = ${fmt(x1)} - ${fmt(f(x1))} \\cdot \\frac{${fmt(x1)} - ${fmt(x0)}}{${fmt(f(x1))} - ${fmt(f(x0))}} = ${fmt(x2)}$ — exactement la ou VOTRE secante coupe l'axe.` },
      hint: { en: `Not quite. The formula is $x_{2} = x_{1} - f(x_{1})\\,\\frac{x_{1} - x_{0}}{f(x_{1}) - f(x_{0})}$: mind the signs, $x_{1} - x_{0} = ${fmt(x1 - x0)}$ is negative.`,
              fr: `Pas tout a fait. La formule est $x_{2} = x_{1} - f(x_{1})\\,\\frac{x_{1} - x_{0}}{f(x_{1}) - f(x_{0})}$ : attention aux signes, $x_{1} - x_{0} = ${fmt(x1 - x0)}$ est negatif.` },
      reveal: { en: `Here is the computation: $x_{2} = ${fmt(x1)} - ${fmt(f(x1))} \\cdot \\frac{${fmt(x1 - x0)}}{${fmt(f(x1) - f(x0))}} = ${fmt(x1)} + ${fmt(-f(x1) * (x1 - x0) / (f(x1) - f(x0)), 6)} \\approx ${fmt(x2)}$. Type this value.`,
                fr: `Voici le calcul : $x_{2} = ${fmt(x1)} - ${fmt(f(x1))} \\cdot \\frac{${fmt(x1 - x0)}}{${fmt(f(x1) - f(x0))}} = ${fmt(x1)} + ${fmt(-f(x1) * (x1 - x0) / (f(x1) - f(x0)), 6)} \\approx ${fmt(x2)}$. Tapez cette valeur.` },
      plotOnOk: basePlot({ segs: [secantSeg(x0, x1, 1.2, 2.2, ORANGE)],
                           points: [{ x: x0, y: f(x0), color: ORANGE, label: 'x₀ = 2' },
                                    { x: x1, y: f(x1), color: PURPLE, label: 'x₁ = 1.5' },
                                    { x: x2, y: 0, color: GREEN, label: `x₂ = ${fmt(x2)}` }] }),
    },
  })

  // ---- step 4: input x3 (the window slides: we keep the last 2 points)
  steps.push({
    plot: { xMin: 1.3, xMax: 1.6, fns: [{ fn: f, color: BLUE }],
            segs: [secantSeg(x1, x2, 1.32, 1.58, PURPLE)],
            points: [{ x: x1, y: f(x1), color: PURPLE, label: `x₁ = ${fmt(x1)}` },
                     { x: x2, y: f(x2), color: GREEN, label: `x₂ = ${fmt(x2)}` }] },
    instruction: {
      en: `The window SLIDES: forget $x_{0}$, keep the two latest points $x_{1} = ${fmt(x1)}$ and $x_{2} = ${fmt(x2)}$, with $f(x_{1}) = ${fmt(f(x1))}$ and $f(x_{2}) = ${fmt(f(x2), 6)}$. Compute $x_{3} = x_{2} - f(x_{2})\\,\\frac{x_{2} - x_{1}}{f(x_{2}) - f(x_{1})}$ (4 decimals).`,
      fr: `La fenetre GLISSE : on oublie $x_{0}$, on garde les deux derniers points $x_{1} = ${fmt(x1)}$ et $x_{2} = ${fmt(x2)}$, avec $f(x_{1}) = ${fmt(f(x1))}$ et $f(x_{2}) = ${fmt(f(x2), 6)}$. Calculez $x_{3} = x_{2} - f(x_{2})\\,\\frac{x_{2} - x_{1}}{f(x_{2}) - f(x_{1})}$ (4 decimales).`,
    },
    input: {
      label: '$x_3 =$', expected: x3, tol: Math.abs(x3) * 0.01,
      ok: { en: `Correct: $x_{3} = ${fmt(x3, 6)}$. The new secant is almost indistinguishable from the curve — you are within $${fmt(Math.abs(x3 - root), 6)}$ of $\\sqrt{2}$.`,
            fr: `Exact : $x_{3} = ${fmt(x3, 6)}$. La nouvelle secante est presque confondue avec la courbe — vous etes a $${fmt(Math.abs(x3 - root), 6)}$ de $\\sqrt{2}$.` },
      hint: { en: 'Not quite. Same formula, indices shifted by one: $x_{3} = x_{2} - f(x_{2})\\,\\frac{x_{2} - x_{1}}{f(x_{2}) - f(x_{1})}$.',
              fr: 'Pas tout a fait. Meme formule, indices decales de un : $x_{3} = x_{2} - f(x_{2})\\,\\frac{x_{2} - x_{1}}{f(x_{2}) - f(x_{1})}$.' },
      reveal: { en: `Here is the computation: $x_{3} = ${fmt(x2)} - ${fmt(f(x2), 6)} \\cdot \\frac{${fmt(x2 - x1, 6)}}{${fmt(f(x2) - f(x1), 6)}} \\approx ${fmt(x3, 6)}$. Type this value (4 decimals are enough).`,
                fr: `Voici le calcul : $x_{3} = ${fmt(x2)} - ${fmt(f(x2), 6)} \\cdot \\frac{${fmt(x2 - x1, 6)}}{${fmt(f(x2) - f(x1), 6)}} \\approx ${fmt(x3, 6)}$. Tapez cette valeur (4 decimales suffisent).` },
      plotOnOk: { xMin: 1.3, xMax: 1.6, fns: [{ fn: f, color: BLUE }],
                  segs: [secantSeg(x1, x2, 1.32, 1.58, PURPLE)],
                  points: [{ x: x1, y: f(x1), color: PURPLE, label: 'x₁' },
                           { x: x2, y: f(x2), color: GREEN, label: 'x₂' },
                           { x: x3, y: 0, color: GREEN, label: `x₃ = ${fmt(x3)}` }],
                  root },
    },
  })

  // ---- step 5: comparison with Newton (choice)
  steps.push({
    plot: { xMin: 1.3, xMax: 1.6, fns: [{ fn: f, color: BLUE }],
            points: [{ x: x3, y: 0, color: GREEN, label: `x₃ = ${fmt(x3, 6)}` }], root },
    instruction: {
      en: `Compare with Newton from the same start: after the same number of $f$-evaluations Newton gives $1.41421569$ while your secant gives $${fmt(x3, 8)}$. Both rush to $\\sqrt{2}$.`,
      fr: `Comparez avec Newton depuis le meme depart : apres le meme nombre d'evaluations de $f$, Newton donne $1{,}41421569$ et votre secante $${fmt(x3, 8)}$. Les deux foncent vers $\\sqrt{2}$.`,
    },
    choice: {
      prompt: { en: 'What does each secant step need that a Newton step does not?',
                fr: 'De quoi chaque pas de secante a-t-il besoin, contrairement a un pas de Newton ?' },
      choices: [
        {
          label: { en: 'Only one NEW evaluation of $f$, no derivative', fr: 'Une seule NOUVELLE evaluation de $f$, pas de derivee' },
          correct: true,
          feedback: { en: `Right: the secant reuses $f(x_{n-1})$ and adds just one new value $f(x_{n})$ — no $f'$ at all. Per evaluation it is often CHEAPER than Newton, even if its order ($\\approx 1.618$) is lower.`,
                      fr: `Exact : la secante reutilise $f(x_{n-1})$ et n'ajoute qu'une nouvelle valeur $f(x_{n})$ — aucun $f'$. Par evaluation, elle est souvent MOINS CHERE que Newton, meme si son ordre ($\\approx 1{,}618$) est plus bas.` },
        },
        {
          label: { en: 'The exact derivative $f\'(x_{n})$', fr: 'La derivee exacte $f\'(x_{n})$' },
          correct: false,
          feedback: { en: `That is exactly what the secant AVOIDS — it was the whole point of replacing the tangent. Read the secant formula again: which quantities appear in it?`,
                      fr: `C'est exactement ce que la secante EVITE — c'etait tout l'interet de remplacer la tangente. Relisez la formule de la secante : quelles quantites y apparaissent ?` },
        },
        {
          label: { en: 'A sign change between the two points', fr: 'Un changement de signe entre les deux points' },
          correct: false,
          feedback: { en: `No: that is the requirement of BISECTION (and regula falsi). The secant happily uses two points on the same side of the axis.`,
                      fr: `Non : c'est l'exigence de la DICHOTOMIE (et de la fausse position). La secante utilise sans probleme deux points du meme cote de l'axe.` },
        },
      ],
    },
  })

  const rows: string[][] = []
  for (let n = 0; n < xs.length; n++) {
    rows.push([`$x_{${n}}$`, `$${fmt(xs[n], 6)}$`, `$${fmt(f(xs[n]), 8)}$`])
  }

  return {
    title: { en: 'Apply the secant method yourself', fr: 'Appliquez la methode de la secante vous-meme' },
    steps,
    done: {
      intro: { en: 'You replaced every tangent by a secant through YOUR two latest points. Here are YOUR iterates:',
               fr: 'Vous avez remplace chaque tangente par une secante passant par VOS deux derniers points. Voici VOS iteres :' },
      eqTex: `x_{n+1} = x_{n} - f(x_{n})\\,\\frac{x_{n} - x_{n-1}}{f(x_{n}) - f(x_{n-1})}, \\quad f(x) = ${TEX}`,
      table: {
        cols: [
          { en: 'iterate', fr: 'itere' },
          { en: 'value $x_{n}$', fr: 'valeur $x_{n}$' },
          { en: 'residual $f(x_{n})$', fr: 'residu $f(x_{n})$' },
        ],
        rows,
      },
      plot: basePlot({ segs: [secantSeg(x0, x1, 1.2, 2.2, ORANGE), secantSeg(x1, x2, 1.2, 1.7, PURPLE)],
                       points: [{ x: x0, y: f(x0), color: ORANGE, label: 'x₀' },
                                { x: x1, y: f(x1), color: PURPLE, label: 'x₁' },
                                { x: x2, y: f(x2), color: GREEN, label: 'x₂' }],
                       root }),
      outro: { en: `Concept &#8594; application: the slope $\\frac{f(x_{n}) - f(x_{n-1})}{x_{n} - x_{n-1}}$ is a FINITE-DIFFERENCE stand-in for $f'$. No derivative, one new evaluation per step, order $\\approx 1.618$: after ${xs.length - 2} secant steps you reached $${fmt(xs[4], 8)}$, while $\\sqrt{2} \\approx ${fmt(root, 8)}$ (green dot). Slightly slower than Newton per step — often faster per evaluation.`,
              fr: `Concept &#8594; application : la pente $\\frac{f(x_{n}) - f(x_{n-1})}{x_{n} - x_{n-1}}$ est un substitut par DIFFERENCE FINIE de $f'$. Pas de derivee, une seule nouvelle evaluation par pas, ordre $\\approx 1{,}618$ : apres ${xs.length - 2} pas de secante vous atteignez $${fmt(xs[4], 8)}$, alors que $\\sqrt{2} \\approx ${fmt(root, 8)}$ (point vert). Un peu plus lente que Newton par pas — souvent plus rapide par evaluation.` },
    },
  }
}

export const GUIDED_ROOTFINDING: Record<string, GScript> = {
  concept_bissection: buildBisection(),
  concept_fixed_point: buildFixedPoint(),
  concept_newton_raphson: buildNewtonRaphson(),
  concept_secant: buildSecant(),
}
