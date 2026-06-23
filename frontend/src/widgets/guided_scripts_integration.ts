/**
 * Guided scenarios — Module: Numerical integration.
 *
 * Same philosophy as guided_scripts_rootfinding.ts: each script links
 * the CONCEPT (Riemann sum, signed area, chord, parabola, Gauss
 * nodes) to its APPLICATION. The functions are FIXED by the lesson;
 * the student DECIDES (choices) and COMPUTES (inputs), with immediate
 * graphical effect of each decision.
 */

import {
  GScript, GStep, PlotSpec,
  ORANGE, GREEN, TEAL, PURPLE, MUTED,
  fmt,
} from './guided_core'

// ==================================================================
// Shared geometric helpers
// ==================================================================

/** Riemann rectangles (left = true -> height taken on the left). */
function riemannRects(
  f: (x: number) => number, a: number, b: number, n: number,
  left: boolean, fill: string,
): { pts: [number, number][]; fill: string; opacity: number; stroke: string }[] {
  const h = (b - a) / n
  const out: { pts: [number, number][]; fill: string; opacity: number; stroke: string }[] = []
  for (let i = 0; i < n; i++) {
    const x0 = a + i * h
    const x1 = x0 + h
    const y = f(left ? x0 : x1)
    out.push({ pts: [[x0, 0], [x1, 0], [x1, y], [x0, y]], fill, opacity: 0.3, stroke: fill })
  }
  return out
}

/** Trapezoids: we connect (x0, f(x0)) to (x1, f(x1)) by a chord. */
function trapPolys(
  f: (x: number) => number, a: number, b: number, n: number, fill: string,
): { pts: [number, number][]; fill: string; opacity: number; stroke: string }[] {
  const h = (b - a) / n
  const out: { pts: [number, number][]; fill: string; opacity: number; stroke: string }[] = []
  for (let i = 0; i < n; i++) {
    const x0 = a + i * h
    const x1 = x0 + h
    out.push({ pts: [[x0, 0], [x1, 0], [x1, f(x1)], [x0, f(x0)]], fill, opacity: 0.3, stroke: fill })
  }
  return out
}

/** Exact area under f between a and b (sampled polygon, axis side included). */
function areaPoly(
  f: (x: number) => number, a: number, b: number, fill: string, opacity = 0.22,
): { pts: [number, number][]; fill: string; opacity: number } {
  const pts: [number, number][] = [[a, 0]]
  for (let i = 0; i <= 60; i++) {
    const x = a + (b - a) * i / 60
    pts.push([x, f(x)])
  }
  pts.push([b, 0])
  return { pts, fill, opacity }
}

// ==================================================================
// 1. Riemann sums — f(x) = x^2 on [0, 2]
// ==================================================================
function buildRiemann(): GScript {
  const f = (x: number) => x * x
  const TEX = 'x^{2}'
  const a = 0, b = 2, n = 4, h = (b - a) / n          // h = 0.5
  const exact = 8 / 3                                  // 2.6667
  const L4 = h * (f(0) + f(0.5) + f(1) + f(1.5))       // 1.75
  const R4 = h * (f(0.5) + f(1) + f(1.5) + f(2))       // 3.75
  const L8 = 2.1875, R8 = 3.1875                       // verified in python

  const base: PlotSpec = { xMin: -0.3, xMax: 2.4, fns: [{ fn: f }], interval: [a, b] }
  const withLeft: PlotSpec = { ...base, polys: riemannRects(f, a, b, n, true, ORANGE) }
  const withRight: PlotSpec = { ...base, polys: riemannRects(f, a, b, n, false, GREEN) }

  const steps: GStep[] = []

  // step 1: the concept — approximate an area with rectangles
  steps.push({
    plot: { ...base, polys: [areaPoly(f, a, b, TEAL)] },
    instruction: {
      en: `We want the area under $f(x) = ${TEX}$ on $[0,\\;2]$ (shaded). The CONCEPT of Riemann sums: replace the curved region by $n$ rectangles whose total area we CAN compute. Here $n = ${n}$, so each rectangle has width $h = \\frac{2-0}{${n}} = ${fmt(h)}$.`,
      fr: `On veut l'aire sous $f(x) = ${TEX}$ sur $[0,\\;2]$ (zone coloree). Le CONCEPT des sommes de Riemann : remplacer la region courbe par $n$ rectangles dont on SAIT calculer l'aire totale. Ici $n = ${n}$, donc chaque rectangle a pour largeur $h = \\frac{2-0}{${n}} = ${fmt(h)}$.`,
    },
  })

  // step 2: choice — does left underestimate or overestimate? (f increasing)
  steps.push({
    plot: base,
    instruction: {
      en: `First decision: where do we read the HEIGHT of each rectangle? With the LEFT rule, the height on $[x_{i},\\;x_{i+1}]$ is $f(x_{i})$. Note that $f$ is INCREASING on $[0,\\;2]$.`,
      fr: `Premiere decision : ou lit-on la HAUTEUR de chaque rectangle ? Avec la regle a GAUCHE, la hauteur sur $[x_{i},\\;x_{i+1}]$ vaut $f(x_{i})$. Remarquez que $f$ est CROISSANTE sur $[0,\\;2]$.`,
    },
    choice: {
      prompt: { en: 'Since $f$ is increasing, the left rectangles will...',
                fr: 'Puisque $f$ est croissante, les rectangles a gauche vont...' },
      choices: [
        {
          label: { en: 'UNDER-estimate the area', fr: 'SOUS-estimer l\'aire' },
          correct: true,
          plot: withLeft,
          feedback: {
            en: `Yes! Look at the graph: each orange rectangle stays BELOW the curve because $f(x_{i}) \\le f(x)$ on the whole sub-interval when $f$ increases. So $L_{4} \\le \\int_{0}^{2} f$.`,
            fr: `Oui ! Regardez le graphe : chaque rectangle orange reste SOUS la courbe car $f(x_{i}) \\le f(x)$ sur tout le sous-intervalle quand $f$ croit. Donc $L_{4} \\le \\int_{0}^{2} f$.`,
          },
        },
        {
          label: { en: 'OVER-estimate the area', fr: 'SUR-estimer l\'aire' },
          correct: false,
          plot: withRight,
          feedback: {
            en: `That would be the RIGHT rule (green rectangles shown): heights $f(x_{i+1})$ poke ABOVE an increasing curve. The LEFT heights $f(x_{i})$ stay below it.`,
            fr: `Ce serait la regle a DROITE (rectangles verts affiches) : les hauteurs $f(x_{i+1})$ depassent AU-DESSUS d'une courbe croissante. Les hauteurs a GAUCHE $f(x_{i})$ restent en dessous.`,
          },
        },
      ],
    },
  })

  // step 3: input — height f(0.5)
  steps.push({
    plot: withLeft,
    instruction: {
      en: `Now APPLY it. The left nodes are $x_{0} = 0$, $x_{1} = 0.5$, $x_{2} = 1$, $x_{3} = 1.5$. Compute the height of the SECOND rectangle yourself: $f(0.5)$.`,
      fr: `APPLIQUEZ maintenant. Les noeuds a gauche sont $x_{0} = 0$, $x_{1} = 0.5$, $x_{2} = 1$, $x_{3} = 1.5$. Calculez vous-meme la hauteur du DEUXIEME rectangle : $f(0.5)$.`,
    },
    input: {
      label: '$f(0.5) =$', expected: 0.25, tol: 0.0025,
      ok: { en: `Correct: $f(0.5) = 0.5^{2} = 0.25$. The dot marks YOUR height on the graph.`,
            fr: `Exact : $f(0.5) = 0.5^{2} = 0.25$. Le point marque VOTRE hauteur sur le graphe.` },
      hint: { en: 'Remember: $f(x) = x^{2}$, so square the node.',
              fr: 'Rappel : $f(x) = x^{2}$, donc elevez le noeud au carre.' },
      reveal: { en: `Full computation: $f(0.5) = 0.5 \\times 0.5 = 0.25$. Type $0.25$.`,
                fr: `Calcul complet : $f(0.5) = 0.5 \\times 0.5 = 0.25$. Tapez $0.25$.` },
      plotOnOk: { ...withLeft, points: [{ x: 0.5, y: 0.25, color: ORANGE, label: 'f(0.5) = 0.25' }] },
    },
  })

  // step 4: input — the left sum L4
  steps.push({
    plot: withLeft,
    instruction: {
      en: `The four left heights are $f(0) = 0$, $f(0.5) = 0.25$, $f(1) = 1$, $f(1.5) = 2.25$. Assemble YOUR left sum: $L_{4} = h \\cdot (f(0) + f(0.5) + f(1) + f(1.5))$ with $h = ${fmt(h)}$.`,
      fr: `Les quatre hauteurs a gauche sont $f(0) = 0$, $f(0.5) = 0.25$, $f(1) = 1$, $f(1.5) = 2.25$. Assemblez VOTRE somme a gauche : $L_{4} = h \\cdot (f(0) + f(0.5) + f(1) + f(1.5))$ avec $h = ${fmt(h)}$.`,
    },
    input: {
      label: '$L_4 =$', expected: L4, tol: L4 * 0.01,
      ok: { en: `Yes: $L_{4} = ${fmt(h)} \\times (0 + 0.25 + 1 + 2.25) = ${fmt(h)} \\times 3.5 = ${fmt(L4)}$. That is YOUR rectangle area, drawn in orange.`,
            fr: `Oui : $L_{4} = ${fmt(h)} \\times (0 + 0.25 + 1 + 2.25) = ${fmt(h)} \\times 3.5 = ${fmt(L4)}$. C'est VOTRE aire de rectangles, dessinee en orange.` },
      hint: { en: 'Formula: $L_{n} = h \\sum_{i=0}^{n-1} f(x_{i})$. Add the four heights, THEN multiply by $h = 0.5$.',
              fr: 'Formule : $L_{n} = h \\sum_{i=0}^{n-1} f(x_{i})$. Additionnez les quatre hauteurs, PUIS multipliez par $h = 0.5$.' },
      reveal: { en: `Computation: $0 + 0.25 + 1 + 2.25 = 3.5$, then $0.5 \\times 3.5 = ${fmt(L4)}$. Type $${fmt(L4)}$.`,
                fr: `Calcul : $0 + 0.25 + 1 + 2.25 = 3.5$, puis $0.5 \\times 3.5 = ${fmt(L4)}$. Tapez $${fmt(L4)}$.` },
      plotOnOk: withLeft,
    },
  })

  // step 5: choice — compare L4 to the exact value, bounding
  steps.push({
    plot: { ...base, polys: [...riemannRects(f, a, b, n, false, GREEN), ...riemannRects(f, a, b, n, true, ORANGE)] },
    instruction: {
      en: `The exact area is $\\int_{0}^{2} x^{2}\\,dx = \\frac{8}{3} \\approx ${fmt(exact)}$. The same computation with RIGHT heights gives $R_{4} = ${fmt(R4)}$. Both families of rectangles are shown.`,
      fr: `L'aire exacte vaut $\\int_{0}^{2} x^{2}\\,dx = \\frac{8}{3} \\approx ${fmt(exact)}$. Le meme calcul avec les hauteurs a DROITE donne $R_{4} = ${fmt(R4)}$. Les deux familles de rectangles sont affichees.`,
    },
    choice: {
      prompt: { en: 'What do $L_{4}$ and $R_{4}$ tell us about the exact value?',
                fr: 'Que nous disent $L_{4}$ et $R_{4}$ sur la valeur exacte ?' },
      choices: [
        {
          label: { en: 'They TRAP it: $L_{4} \\le \\frac{8}{3} \\le R_{4}$', fr: 'Ils l\'ENCADRENT : $L_{4} \\le \\frac{8}{3} \\le R_{4}$' },
          correct: true,
          feedback: {
            en: `Exactly: $${fmt(L4)} \\le ${fmt(exact)} \\le ${fmt(R4)}$. For an increasing $f$, left under-estimates and right over-estimates — the truth is squeezed between YOUR two sums.`,
            fr: `Exactement : $${fmt(L4)} \\le ${fmt(exact)} \\le ${fmt(R4)}$. Pour $f$ croissante, gauche sous-estime et droite surestime — la verite est coincee entre VOS deux sommes.`,
          },
        },
        {
          label: { en: 'Both are above it', fr: 'Les deux sont au-dessus' },
          correct: false,
          feedback: {
            en: `Check the numbers: $L_{4} = ${fmt(L4)} < ${fmt(exact)}$. Your own left sum is BELOW the exact value, the right sum is above: together they trap it.`,
            fr: `Verifiez les nombres : $L_{4} = ${fmt(L4)} < ${fmt(exact)}$. Votre propre somme a gauche est SOUS la valeur exacte, la somme a droite au-dessus : ensemble elles l'encadrent.`,
          },
        },
      ],
    },
  })

  // step 6: choice — what happens when n grows
  steps.push({
    plot: { ...base, polys: riemannRects(f, a, b, 8, true, ORANGE) },
    instruction: {
      en: `Last decision. We double the number of rectangles: $n = 8$, so $h = 0.25$ (shown). The sums become $L_{8} = ${fmt(L8)}$ and $R_{8} = ${fmt(R8)}$.`,
      fr: `Derniere decision. On double le nombre de rectangles : $n = 8$, donc $h = 0.25$ (affiche). Les sommes deviennent $L_{8} = ${fmt(L8)}$ et $R_{8} = ${fmt(R8)}$.`,
    },
    choice: {
      prompt: { en: 'What happens as $n \\to \\infty$?', fr: 'Que se passe-t-il quand $n \\to \\infty$ ?' },
      choices: [
        {
          label: { en: 'Both sums converge to $\\frac{8}{3}$ — that IS the integral', fr: 'Les deux sommes convergent vers $\\frac{8}{3}$ — c\'est CELA l\'integrale' },
          correct: true,
          plot: { ...base, polys: riemannRects(f, a, b, 16, true, ORANGE) },
          feedback: {
            en: `Yes. The gap $R_{n} - L_{n} = h\\,(f(2) - f(0)) = 4h \\to 0$. The common limit is the DEFINITION of $\\int_{0}^{2} f$. The concept of the integral IS a limit of your rectangle sums.`,
            fr: `Oui. L'ecart $R_{n} - L_{n} = h\\,(f(2) - f(0)) = 4h \\to 0$. La limite commune est la DEFINITION de $\\int_{0}^{2} f$. Le concept d'integrale EST une limite de vos sommes de rectangles.`,
          },
        },
        {
          label: { en: 'The sums stop changing after some $n$', fr: 'Les sommes cessent de changer a partir d\'un certain $n$' },
          correct: false,
          feedback: {
            en: `Compare yourself: $L_{4} = ${fmt(L4)}$ then $L_{8} = ${fmt(L8)}$ — still moving toward $${fmt(exact)}$. They keep improving forever; only the LIMIT is fixed.`,
            fr: `Comparez vous-meme : $L_{4} = ${fmt(L4)}$ puis $L_{8} = ${fmt(L8)}$ — toujours en marche vers $${fmt(exact)}$. Elles s'ameliorent sans fin ; seule la LIMITE est fixe.`,
          },
        },
      ],
    },
  })

  return {
    title: { en: 'Build a Riemann sum yourself', fr: 'Construisez une somme de Riemann vous-meme' },
    steps,
    done: {
      intro: { en: 'You did not memorize a formula — you BUILT the integral concept: rectangles, your heights, your sum, and the squeeze toward the limit.',
               fr: 'Vous n\'avez pas memorise une formule — vous avez CONSTRUIT le concept d\'integrale : rectangles, vos hauteurs, votre somme, et l\'encadrement vers la limite.' },
      eqTex: `\\int_{0}^{2} ${TEX}\\,dx = \\frac{8}{3} \\approx ${fmt(exact)}`,
      table: {
        cols: [
          { en: '$n$', fr: '$n$' },
          { en: 'left $L_{n}$', fr: 'gauche $L_{n}$' },
          { en: 'right $R_{n}$', fr: 'droite $R_{n}$' },
          { en: 'exact', fr: 'exact' },
        ],
        rows: [
          ['$4$', `$${fmt(L4)}$`, `$${fmt(R4)}$`, `$${fmt(exact)}$`],
          ['$8$', `$${fmt(L8)}$`, `$${fmt(R8)}$`, `$${fmt(exact)}$`],
        ],
      },
      plot: { ...base, polys: [areaPoly(f, a, b, TEAL), ...riemannRects(f, a, b, 16, true, ORANGE)] },
      outro: { en: `Concept &#8594; application: every numerical integration method you will meet (trapezoid, Simpson, Gauss) is just a SMARTER way to choose the heights of these rectangles. You computed $L_{4} = ${fmt(L4)}$ by hand — the computer repeats YOUR steps with $n$ in the millions.`,
               fr: `Concept &#8594; application : toute methode d'integration numerique que vous rencontrerez (trapezes, Simpson, Gauss) n'est qu'une facon plus INTELLIGENTE de choisir les hauteurs de ces rectangles. Vous avez calcule $L_{4} = ${fmt(L4)}$ a la main — l'ordinateur repete VOS etapes avec $n$ en millions.` },
    },
  }
}

// ==================================================================
// 2. Definite integral = SIGNED area — f(x) = x^2 - 1 on [0, 2]
// ==================================================================
function buildDefiniteIntegrals(): GScript {
  const f = (x: number) => x * x - 1
  const TEX = 'x^{2}-1'
  const exact = 8 / 3 - 2                 // 0.6667
  const negPart = 1 / 3 - 1               // -0.6667 on [0,1]
  const posPart = exact - negPart          // 1.3333 on [1,2]

  const base: PlotSpec = { xMin: -0.3, xMax: 2.4, fns: [{ fn: f }], interval: [0, 2] }
  const signedPlot: PlotSpec = {
    ...base,
    polys: [areaPoly(f, 0, 1, ORANGE, 0.3), areaPoly(f, 1, 2, GREEN, 0.3)],
    vlines: [{ x: 1, color: MUTED, dash: '5 4', label: 'x = 1' }],
  }

  const steps: GStep[] = []

  // step 1: concept of signed area
  steps.push({
    plot: base,
    instruction: {
      en: `New function: $f(x) = ${TEX}$ on $[0,\\;2]$. Notice the curve goes BELOW the axis, then above. The CONCEPT: the definite integral $\\int_{0}^{2} f$ is a SIGNED area — regions under the axis count negatively.`,
      fr: `Nouvelle fonction : $f(x) = ${TEX}$ sur $[0,\\;2]$. Remarquez que la courbe passe SOUS l'axe, puis au-dessus. Le CONCEPT : l'integrale definie $\\int_{0}^{2} f$ est une aire SIGNEE — les regions sous l'axe comptent negativement.`,
    },
  })

  // step 2: where the curve crosses the axis
  steps.push({
    plot: base,
    instruction: {
      en: `To split the signed regions we need the point where $f$ crosses the axis, i.e. where $${TEX} = 0$.`,
      fr: `Pour separer les regions signees, il faut le point ou $f$ coupe l'axe, c'est-a-dire ou $${TEX} = 0$.`,
    },
    input: {
      label: '$x =$', expected: 1, tol: 0.01,
      ok: { en: `Right: $x^{2} = 1$ gives $x = 1$ on our interval. The dashed line marks YOUR crossing point.`,
            fr: `Exact : $x^{2} = 1$ donne $x = 1$ sur notre intervalle. La ligne pointillee marque VOTRE point de coupure.` },
      hint: { en: 'Solve $x^{2} - 1 = 0$ for $x \\ge 0$.',
              fr: 'Resolvez $x^{2} - 1 = 0$ pour $x \\ge 0$.' },
      reveal: { en: `Computation: $x^{2} - 1 = 0 \\Rightarrow x^{2} = 1 \\Rightarrow x = 1$ (we keep the positive root). Type $1$.`,
                fr: `Calcul : $x^{2} - 1 = 0 \\Rightarrow x^{2} = 1 \\Rightarrow x = 1$ (on garde la racine positive). Tapez $1$.` },
      plotOnOk: { ...base, vlines: [{ x: 1, color: MUTED, dash: '5 4', label: 'x = 1' }], points: [{ x: 1, y: 0, color: GREEN, label: 'f(1) = 0' }] },
    },
  })

  // step 3: choice — which piece counts negatively
  steps.push({
    plot: { ...base, vlines: [{ x: 1, color: MUTED, dash: '5 4', label: 'x = 1' }] },
    instruction: {
      en: `The interval splits into $[0,\\;1]$ and $[1,\\;2]$. Apply the signed-area concept.`,
      fr: `L'intervalle se decoupe en $[0,\\;1]$ et $[1,\\;2]$. Appliquez le concept d'aire signee.`,
    },
    choice: {
      prompt: { en: 'Which piece contributes NEGATIVELY to the integral?',
                fr: 'Quel morceau contribue NEGATIVEMENT a l\'integrale ?' },
      choices: [
        {
          label: { en: '$[0,\\;1]$', fr: '$[0,\\;1]$' },
          correct: true,
          plot: signedPlot,
          feedback: {
            en: `Yes: on $[0,\\;1]$, $f(x) \\le 0$ (e.g. $f(0) = -1$), so the orange region lies UNDER the axis and counts negatively. The green region on $[1,\\;2]$ counts positively.`,
            fr: `Oui : sur $[0,\\;1]$, $f(x) \\le 0$ (par ex. $f(0) = -1$), donc la region orange est SOUS l'axe et compte negativement. La region verte sur $[1,\\;2]$ compte positivement.`,
          },
        },
        {
          label: { en: '$[1,\\;2]$', fr: '$[1,\\;2]$' },
          correct: false,
          plot: { ...base, polys: [areaPoly(f, 1, 2, GREEN, 0.3)], vlines: [{ x: 1, color: MUTED, dash: '5 4', label: 'x = 1' }] },
          feedback: {
            en: `Look at the highlighted region: on $[1,\\;2]$ the curve is ABOVE the axis ($f(2) = 3 > 0$), so that piece counts POSITIVELY. The negative piece is the other one.`,
            fr: `Regardez la region en surbrillance : sur $[1,\\;2]$ la courbe est AU-DESSUS de l'axe ($f(2) = 3 > 0$), donc ce morceau compte POSITIVEMENT. Le morceau negatif est l'autre.`,
          },
        },
      ],
    },
  })

  // step 4: input — value of the negative piece
  steps.push({
    plot: signedPlot,
    instruction: {
      en: `Compute the negative contribution yourself. An antiderivative of $${TEX}$ is $F(x) = \\frac{x^{3}}{3} - x$. So $\\int_{0}^{1} (${TEX})\\,dx = F(1) - F(0)$.`,
      fr: `Calculez vous-meme la contribution negative. Une primitive de $${TEX}$ est $F(x) = \\frac{x^{3}}{3} - x$. Donc $\\int_{0}^{1} (${TEX})\\,dx = F(1) - F(0)$.`,
    },
    input: {
      label: '$I_{[0,1]} =$', expected: negPart, tol: Math.abs(negPart) * 0.01,
      ok: { en: `Correct: $F(1) - F(0) = (\\frac{1}{3} - 1) - 0 = -\\frac{2}{3} \\approx ${fmt(negPart)}$. Negative, exactly as the orange region predicted.`,
            fr: `Exact : $F(1) - F(0) = (\\frac{1}{3} - 1) - 0 = -\\frac{2}{3} \\approx ${fmt(negPart)}$. Negatif, exactement comme la region orange le predisait.` },
      hint: { en: 'Evaluate $F(x) = \\frac{x^{3}}{3} - x$ at $1$ and at $0$, then subtract. Mind the SIGN.',
              fr: 'Evaluez $F(x) = \\frac{x^{3}}{3} - x$ en $1$ et en $0$, puis soustrayez. Attention au SIGNE.' },
      reveal: { en: `Computation: $F(1) = \\frac{1}{3} - 1 = -\\frac{2}{3}$ and $F(0) = 0$, so the integral is $-\\frac{2}{3} \\approx ${fmt(negPart)}$. Type $${fmt(negPart)}$.`,
                fr: `Calcul : $F(1) = \\frac{1}{3} - 1 = -\\frac{2}{3}$ et $F(0) = 0$, donc l'integrale vaut $-\\frac{2}{3} \\approx ${fmt(negPart)}$. Tapez $${fmt(negPart)}$.` },
      plotOnOk: signedPlot,
    },
  })

  // step 5: input — the total integral
  steps.push({
    plot: signedPlot,
    instruction: {
      en: `The positive piece is $\\int_{1}^{2} (${TEX})\\,dx = F(2) - F(1) = \\frac{4}{3} \\approx ${fmt(posPart)}$. Now combine YOUR two signed pieces to get the full integral $\\int_{0}^{2} (${TEX})\\,dx$.`,
      fr: `Le morceau positif vaut $\\int_{1}^{2} (${TEX})\\,dx = F(2) - F(1) = \\frac{4}{3} \\approx ${fmt(posPart)}$. Combinez maintenant VOS deux morceaux signes pour obtenir l'integrale complete $\\int_{0}^{2} (${TEX})\\,dx$.`,
    },
    input: {
      label: '$I_{[0,2]} =$', expected: exact, tol: exact * 0.01,
      ok: { en: `Yes: $-\\frac{2}{3} + \\frac{4}{3} = \\frac{2}{3} \\approx ${fmt(exact)}$. The green region wins, but only by the DIFFERENCE of areas — that is the signed-area concept.`,
            fr: `Oui : $-\\frac{2}{3} + \\frac{4}{3} = \\frac{2}{3} \\approx ${fmt(exact)}$. La region verte l'emporte, mais seulement par la DIFFERENCE des aires — c'est le concept d'aire signee.` },
      hint: { en: 'Chasles relation: $\\int_{0}^{2} = \\int_{0}^{1} + \\int_{1}^{2}$. Add your negative piece to the positive one.',
              fr: 'Relation de Chasles : $\\int_{0}^{2} = \\int_{0}^{1} + \\int_{1}^{2}$. Ajoutez votre morceau negatif au positif.' },
      reveal: { en: `Computation: $-\\frac{2}{3} + \\frac{4}{3} = \\frac{2}{3} \\approx ${fmt(exact)}$. Type $${fmt(exact)}$.`,
                fr: `Calcul : $-\\frac{2}{3} + \\frac{4}{3} = \\frac{2}{3} \\approx ${fmt(exact)}$. Tapez $${fmt(exact)}$.` },
      plotOnOk: signedPlot,
    },
  })

  // step 6: choice — why the part below the axis is subtracted
  steps.push({
    plot: signedPlot,
    instruction: {
      en: `One last conceptual decision. The geometric (unsigned) area of the two regions is $\\frac{2}{3} + \\frac{4}{3} = 2$, yet the integral is only $\\frac{2}{3}$.`,
      fr: `Une derniere decision conceptuelle. L'aire geometrique (non signee) des deux regions vaut $\\frac{2}{3} + \\frac{4}{3} = 2$, pourtant l'integrale ne vaut que $\\frac{2}{3}$.`,
    },
    choice: {
      prompt: { en: 'Why does the region under the axis SUBTRACT?',
                fr: 'Pourquoi la region sous l\'axe se SOUSTRAIT-elle ?' },
      choices: [
        {
          label: { en: 'Because the rectangle heights $f(x_{i})$ are negative there', fr: 'Parce que les hauteurs de rectangles $f(x_{i})$ y sont negatives' },
          correct: true,
          plot: { ...base, polys: riemannRects(f, 0, 2, 8, true, PURPLE), vlines: [{ x: 1, color: MUTED, dash: '5 4', label: 'x = 1' }] },
          feedback: {
            en: `Exactly — back to the Riemann concept: the integral is a limit of sums $h \\sum f(x_{i})$, and on $[0,\\;1]$ every term $f(x_{i}) < 0$. The rectangles below the axis (shown) literally ADD negative numbers.`,
            fr: `Exactement — retour au concept de Riemann : l'integrale est une limite de sommes $h \\sum f(x_{i})$, et sur $[0,\\;1]$ chaque terme $f(x_{i}) < 0$. Les rectangles sous l'axe (affiches) AJOUTENT litteralement des nombres negatifs.`,
          },
        },
        {
          label: { en: 'It is just a sign convention with no computational meaning', fr: 'C\'est juste une convention de signe sans sens calculatoire' },
          correct: false,
          feedback: {
            en: `It is more than a convention: the Riemann sum $h \\sum f(x_{i})$ AUTOMATICALLY produces negative terms where $f < 0$. The sign comes from the heights themselves.`,
            fr: `C'est plus qu'une convention : la somme de Riemann $h \\sum f(x_{i})$ produit AUTOMATIQUEMENT des termes negatifs la ou $f < 0$. Le signe vient des hauteurs elles-memes.`,
          },
        },
      ],
    },
  })

  return {
    title: { en: 'Discover the signed area yourself', fr: 'Decouvrez l\'aire signee vous-meme' },
    steps,
    done: {
      intro: { en: 'You located the crossing, decided which piece is negative, and computed each signed contribution yourself:',
               fr: 'Vous avez localise la coupure, decide quel morceau est negatif, et calcule vous-meme chaque contribution signee :' },
      eqTex: `\\int_{0}^{2} (${TEX})\\,dx = -\\tfrac{2}{3} + \\tfrac{4}{3} = \\tfrac{2}{3} \\approx ${fmt(exact)}`,
      table: {
        cols: [
          { en: 'piece', fr: 'morceau' },
          { en: 'sign of $f$', fr: 'signe de $f$' },
          { en: 'contribution', fr: 'contribution' },
        ],
        rows: [
          ['$[0,\\;1]$', '$f \\le 0$', `$-\\tfrac{2}{3} \\approx ${fmt(negPart)}$`],
          ['$[1,\\;2]$', '$f \\ge 0$', `$+\\tfrac{4}{3} \\approx ${fmt(posPart)}$`],
          ['$[0,\\;2]$', '&#8212;', `$\\tfrac{2}{3} \\approx ${fmt(exact)}$`],
        ],
      },
      plot: signedPlot,
      outro: { en: `Concept &#8594; application: numerical methods never "see" the sign — they just sum $f(x_{i})$ values, which are negative under the axis. That is why every method of this module computes the SIGNED integral, not the geometric area.`,
               fr: `Concept &#8594; application : les methodes numeriques ne "voient" jamais le signe — elles sommes des valeurs $f(x_{i})$, negatives sous l'axe. C'est pourquoi toute methode de ce module calcule l'integrale SIGNEE, pas l'aire geometrique.` },
    },
  }
}

// ==================================================================
// 3. Trapezoidal method — f(x) = x^2 on [0, 2]
// ==================================================================
function buildTrapezoidal(): GScript {
  const f = (x: number) => x * x
  const TEX = 'x^{2}'
  const exact = 8 / 3
  const T1 = (f(0) + f(1)) / 2 * 1        // 0.5: ONE trapezoid on [0,1]
  const T2 = (f(0) + 2 * f(1) + f(2)) / 2 // 3 (h = 1)
  const T4 = 2.75                          // verified in python
  const errT2 = T2 - exact
  const errT4 = T4 - exact

  const base: PlotSpec = { xMin: -0.3, xMax: 2.4, fns: [{ fn: f }], interval: [0, 2] }
  const trap2: PlotSpec = { ...base, polys: trapPolys(f, 0, 2, 2, ORANGE) }
  const trap4: PlotSpec = { ...base, polys: trapPolys(f, 0, 2, 4, GREEN) }

  const steps: GStep[] = []

  // step 1: the concept of the chord
  steps.push({
    plot: { ...base, segs: [{ x1: 0, y1: f(0), x2: 1, y2: f(1), color: ORANGE }, { x1: 1, y1: f(1), x2: 2, y2: f(2), color: ORANGE }] },
    instruction: {
      en: `Back to $f(x) = ${TEX}$ on $[0,\\;2]$, exact integral $\\frac{8}{3} \\approx ${fmt(exact)}$. The trapezoid CONCEPT: instead of a flat rectangle top, replace $f$ on each sub-interval by its CHORD (orange segments, $n = 2$). The region under a chord is a trapezoid — easy area.`,
      fr: `Retour a $f(x) = ${TEX}$ sur $[0,\\;2]$, integrale exacte $\\frac{8}{3} \\approx ${fmt(exact)}$. Le CONCEPT des trapezes : au lieu d'un toit plat de rectangle, on remplace $f$ sur chaque sous-intervalle par sa CORDE (segments oranges, $n = 2$). La region sous une corde est un trapeze — aire facile.`,
    },
  })

  // step 2: choice — formula for the area of a trapezoid
  steps.push({
    plot: { ...base, polys: trapPolys(f, 0, 1, 1, ORANGE) },
    instruction: {
      en: `Zoom on the FIRST trapezoid, on $[0,\\;1]$: parallel sides $f(0)$ and $f(1)$, width $h = 1$.`,
      fr: `Zoom sur le PREMIER trapeze, sur $[0,\\;1]$ : cotes paralleles $f(0)$ et $f(1)$, largeur $h = 1$.`,
    },
    choice: {
      prompt: { en: 'Which formula gives its area?', fr: 'Quelle formule donne son aire ?' },
      choices: [
        {
          label: { en: '$\\frac{f(0)+f(1)}{2} \\cdot h$ (average height times width)', fr: '$\\frac{f(0)+f(1)}{2} \\cdot h$ (hauteur moyenne fois largeur)' },
          correct: true,
          feedback: {
            en: `Yes — a trapezoid is a rectangle whose height is the AVERAGE of the two sides. This is the whole method: average the endpoints instead of picking one.`,
            fr: `Oui — un trapeze est un rectangle dont la hauteur est la MOYENNE des deux cotes. C'est toute la methode : moyenner les extremites au lieu d'en choisir une.`,
          },
        },
        {
          label: { en: '$f(0) \\cdot f(1) \\cdot h$', fr: '$f(0) \\cdot f(1) \\cdot h$' },
          correct: false,
          feedback: {
            en: `A product of heights has the wrong units (height squared times width). The area of a trapezoid uses the AVERAGE of the parallel sides: $\\frac{f(0)+f(1)}{2} \\cdot h$.`,
            fr: `Un produit de hauteurs a les mauvaises unites (hauteur au carre fois largeur). L'aire d'un trapeze utilise la MOYENNE des cotes paralleles : $\\frac{f(0)+f(1)}{2} \\cdot h$.`,
          },
        },
      ],
    },
  })

  // step 3: input — area of ONE trapezoid
  steps.push({
    plot: { ...base, polys: trapPolys(f, 0, 1, 1, ORANGE) },
    instruction: {
      en: `APPLY it: with $f(0) = 0$, $f(1) = 1$ and $h = 1$, compute the area of this first trapezoid.`,
      fr: `APPLIQUEZ : avec $f(0) = 0$, $f(1) = 1$ et $h = 1$, calculez l'aire de ce premier trapeze.`,
    },
    input: {
      label: '$A_1 =$', expected: T1, tol: T1 * 0.01,
      ok: { en: `Correct: $\\frac{0+1}{2} \\times 1 = ${fmt(T1)}$. That orange trapezoid is YOURS.`,
            fr: `Exact : $\\frac{0+1}{2} \\times 1 = ${fmt(T1)}$. Ce trapeze orange est le VOTRE.` },
      hint: { en: 'Formula: $\\frac{f(0)+f(1)}{2} \\cdot h$ with $h = 1$.',
              fr: 'Formule : $\\frac{f(0)+f(1)}{2} \\cdot h$ avec $h = 1$.' },
      reveal: { en: `Computation: $\\frac{0+1}{2} \\times 1 = 0.5$. Type $0.5$.`,
                fr: `Calcul : $\\frac{0+1}{2} \\times 1 = 0.5$. Tapez $0.5$.` },
      plotOnOk: { ...base, polys: trapPolys(f, 0, 1, 1, ORANGE) },
    },
  })

  // step 4: input — full T2
  steps.push({
    plot: trap2,
    instruction: {
      en: `Now the SECOND trapezoid on $[1,\\;2]$ has area $\\frac{f(1)+f(2)}{2} \\times 1 = \\frac{1+4}{2} = 2.5$. Adding both gives the composite rule $T_{2} = \\frac{h}{2}(f(0) + 2f(1) + f(2))$ — the middle node is shared, hence the factor $2$. Compute $T_{2}$.`,
      fr: `Le SECOND trapeze sur $[1,\\;2]$ a pour aire $\\frac{f(1)+f(2)}{2} \\times 1 = \\frac{1+4}{2} = 2.5$. La somme des deux donne la regle composite $T_{2} = \\frac{h}{2}(f(0) + 2f(1) + f(2))$ — le noeud du milieu est partage, d'ou le facteur $2$. Calculez $T_{2}$.`,
    },
    input: {
      label: '$T_2 =$', expected: T2, tol: T2 * 0.01,
      ok: { en: `Yes: $T_{2} = 0.5 + 2.5 = \\frac{1}{2}(0 + 2 \\times 1 + 4) = ${fmt(T2)}$. Both YOUR trapezoids are drawn.`,
            fr: `Oui : $T_{2} = 0.5 + 2.5 = \\frac{1}{2}(0 + 2 \\times 1 + 4) = ${fmt(T2)}$. Vos DEUX trapezes sont dessines.` },
      hint: { en: 'Just add your two trapezoid areas: $0.5 + 2.5$. Or use $\\frac{h}{2}(f(0) + 2f(1) + f(2))$ with $h = 1$.',
              fr: 'Additionnez simplement vos deux aires de trapezes : $0.5 + 2.5$. Ou utilisez $\\frac{h}{2}(f(0) + 2f(1) + f(2))$ avec $h = 1$.' },
      reveal: { en: `Computation: $\\frac{1}{2}(0 + 2 + 4) = \\frac{6}{2} = 3$. Type $3$.`,
                fr: `Calcul : $\\frac{1}{2}(0 + 2 + 4) = \\frac{6}{2} = 3$. Tapez $3$.` },
      plotOnOk: trap2,
    },
  })

  // step 5: choice — why T overestimates here (convexity)
  steps.push({
    plot: trap2,
    instruction: {
      en: `Your result $T_{2} = ${fmt(T2)}$ versus the exact $\\frac{8}{3} \\approx ${fmt(exact)}$: the trapezoid rule OVER-estimates here. Look closely at the chords on the graph.`,
      fr: `Votre resultat $T_{2} = ${fmt(T2)}$ contre l'exact $\\frac{8}{3} \\approx ${fmt(exact)}$ : la methode des trapezes SURESTIME ici. Observez bien les cordes sur le graphe.`,
    },
    choice: {
      prompt: { en: 'Why does it over-estimate for THIS function?',
                fr: 'Pourquoi surestime-t-elle pour CETTE fonction ?' },
      choices: [
        {
          label: { en: '$f$ is CONVEX: every chord lies ABOVE the curve', fr: '$f$ est CONVEXE : toute corde est AU-DESSUS de la courbe' },
          correct: true,
          feedback: {
            en: `Exactly: $f''(x) = 2 > 0$, so chords sit above the graph and each trapezoid contains a sliver of extra area. Concave function &#8594; the rule would UNDER-estimate. The concept (convexity) predicts the SIGN of the error.`,
            fr: `Exactement : $f''(x) = 2 > 0$, donc les cordes sont au-dessus du graphe et chaque trapeze contient un croissant d'aire en trop. Fonction concave &#8594; la regle SOUS-estimerait. Le concept (convexite) predit le SIGNE de l'erreur.`,
          },
        },
        {
          label: { en: 'Because $f$ is increasing on $[0,\\;2]$', fr: 'Parce que $f$ est croissante sur $[0,\\;2]$' },
          correct: false,
          feedback: {
            en: `Monotonicity decided the sign for left/right RECTANGLES, but a chord follows the slope. What matters now is CURVATURE: a convex curve bends below its chords. Check $f''(x) = 2 > 0$.`,
            fr: `La monotonie decidait le signe pour les RECTANGLES gauche/droite, mais une corde suit la pente. Ce qui compte maintenant est la COURBURE : une courbe convexe plonge sous ses cordes. Verifiez $f''(x) = 2 > 0$.`,
          },
        },
      ],
    },
  })

  // step 6: input — T4
  steps.push({
    plot: trap4,
    instruction: {
      en: `Refine: $n = 4$, so $h = 0.5$ (green trapezoids). The rule reads $T_{4} = \\frac{h}{2}(f(0) + 2f(0.5) + 2f(1) + 2f(1.5) + f(2))$ with $f(0.5) = 0.25$ and $f(1.5) = 2.25$. Compute $T_{4}$.`,
      fr: `Raffinez : $n = 4$, donc $h = 0.5$ (trapezes verts). La regle s'ecrit $T_{4} = \\frac{h}{2}(f(0) + 2f(0.5) + 2f(1) + 2f(1.5) + f(2))$ avec $f(0.5) = 0.25$ et $f(1.5) = 2.25$. Calculez $T_{4}$.`,
    },
    input: {
      label: '$T_4 =$', expected: T4, tol: T4 * 0.01,
      ok: { en: `Correct: $T_{4} = \\frac{0.5}{2}(0 + 0.5 + 2 + 4.5 + 4) = 0.25 \\times 11 = ${fmt(T4)}$. The thinner trapezoids hug the curve much better.`,
            fr: `Exact : $T_{4} = \\frac{0.5}{2}(0 + 0.5 + 2 + 4.5 + 4) = 0.25 \\times 11 = ${fmt(T4)}$. Les trapezes plus fins epousent bien mieux la courbe.` },
      hint: { en: 'Inside the parentheses: $0 + 2 \\times 0.25 + 2 \\times 1 + 2 \\times 2.25 + 4$. Then multiply by $\\frac{h}{2} = 0.25$.',
              fr: 'Dans la parenthese : $0 + 2 \\times 0.25 + 2 \\times 1 + 2 \\times 2.25 + 4$. Puis multipliez par $\\frac{h}{2} = 0.25$.' },
      reveal: { en: `Computation: parentheses $= 0 + 0.5 + 2 + 4.5 + 4 = 11$, then $0.25 \\times 11 = ${fmt(T4)}$. Type $${fmt(T4)}$.`,
                fr: `Calcul : parenthese $= 0 + 0.5 + 2 + 4.5 + 4 = 11$, puis $0.25 \\times 11 = ${fmt(T4)}$. Tapez $${fmt(T4)}$.` },
      plotOnOk: trap4,
    },
  })

  // step 7: choice — order of convergence
  steps.push({
    plot: trap4,
    instruction: {
      en: `Compare YOUR errors: $T_{2} - \\frac{8}{3} = ${fmt(errT2)}$ and $T_{4} - \\frac{8}{3} = ${fmt(errT4)}$. The step went from $h = 1$ to $h = 0.5$.`,
      fr: `Comparez VOS erreurs : $T_{2} - \\frac{8}{3} = ${fmt(errT2)}$ et $T_{4} - \\frac{8}{3} = ${fmt(errT4)}$. Le pas est passe de $h = 1$ a $h = 0.5$.`,
    },
    choice: {
      prompt: { en: 'When $h$ is halved, the error is divided by about...',
                fr: 'Quand $h$ est divise par 2, l\'erreur est divisee par environ...' },
      choices: [
        {
          label: { en: '$4$ — error $\\propto h^{2}$ (order 2)', fr: '$4$ — erreur $\\propto h^{2}$ (ordre 2)' },
          correct: true,
          feedback: {
            en: `Yes: $\\frac{${fmt(errT2)}}{${fmt(errT4)}} \\approx ${fmt(errT2 / errT4, 2)}$. The theory says error $= -\\frac{(b-a)h^{2}}{12} f''(\\xi)$, and YOUR two computations just verified the $h^{2}$ experimentally.`,
            fr: `Oui : $\\frac{${fmt(errT2)}}{${fmt(errT4)}} \\approx ${fmt(errT2 / errT4, 2)}$. La theorie dit erreur $= -\\frac{(b-a)h^{2}}{12} f''(\\xi)$, et VOS deux calculs viennent de verifier le $h^{2}$ experimentalement.`,
          },
        },
        {
          label: { en: '$2$ — error $\\propto h$ (order 1)', fr: '$2$ — erreur $\\propto h$ (ordre 1)' },
          correct: false,
          feedback: {
            en: `Divide your own numbers: $\\frac{${fmt(errT2)}}{${fmt(errT4)}} \\approx 4$, not $2$. The trapezoid rule gains a FACTOR 4 per halving: that is the signature of order $h^{2}$.`,
            fr: `Divisez vos propres nombres : $\\frac{${fmt(errT2)}}{${fmt(errT4)}} \\approx 4$, pas $2$. La regle des trapezes gagne un FACTEUR 4 par division du pas : c'est la signature de l'ordre $h^{2}$.`,
          },
        },
      ],
    },
  })

  return {
    title: { en: 'Apply the trapezoidal rule yourself', fr: 'Appliquez la methode des trapezes vous-meme' },
    steps,
    done: {
      intro: { en: 'You replaced the curve by chords, computed each trapezoid, and measured the order of convergence with your own numbers:',
               fr: 'Vous avez remplace la courbe par des cordes, calcule chaque trapeze, et mesure l\'ordre de convergence avec vos propres nombres :' },
      eqTex: `\\int_{0}^{2} ${TEX}\\,dx = \\tfrac{8}{3} \\approx ${fmt(exact)}`,
      table: {
        cols: [
          { en: '$n$', fr: '$n$' },
          { en: '$h$', fr: '$h$' },
          { en: '$T_{n}$', fr: '$T_{n}$' },
          { en: 'error', fr: 'erreur' },
        ],
        rows: [
          ['$2$', '$1$', `$${fmt(T2)}$`, `$${fmt(errT2)}$`],
          ['$4$', '$0.5$', `$${fmt(T4)}$`, `$${fmt(errT4)}$`],
        ],
      },
      plot: trap4,
      outro: { en: `Concept &#8594; application: chord above a convex curve &#8594; positive error; error $\\propto h^{2}$ &#8594; each halving buys a factor 4. You PREDICTED both effects before computing them. Next step: replace the chord by a parabola — that is Simpson.`,
               fr: `Concept &#8594; application : corde au-dessus d'une courbe convexe &#8594; erreur positive ; erreur $\\propto h^{2}$ &#8594; chaque division du pas gagne un facteur 4. Vous avez PREDIT les deux effets avant de les calculer. Etape suivante : remplacer la corde par une parabole — c'est Simpson.` },
    },
  }
}

// ==================================================================
// 4. Simpson's method — f(x) = x^3 - 2x^2 + 2 on [0, 2]
// ==================================================================
function buildSimpson(): GScript {
  const f = (x: number) => x * x * x - 2 * x * x + 2
  const TEX = 'x^{3}-2x^{2}+2'
  const exact = 8 / 3                       // 4 - 16/3 + 4
  const h = 1
  const S2 = (h / 3) * (f(0) + 4 * f(1) + f(2))   // 8/3
  const T2 = (f(0) + 2 * f(1) + f(2)) / 2          // 3: trapezoids for comparison
  // parabole de Simpson : interpole (0,2), (1,1), (2,2) -> p(x) = x^2 - 2x + 2
  const par = (x: number) => x * x - 2 * x + 2

  const base: PlotSpec = { xMin: -0.3, xMax: 2.4, fns: [{ fn: f }], interval: [0, 2] }
  const withParabola: PlotSpec = {
    ...base,
    fns: [{ fn: f }, { fn: par, color: PURPLE, dash: '7 5', width: 2.5 }],
    points: [
      { x: 0, y: f(0), color: PURPLE, label: 'f(0) = 2' },
      { x: 1, y: f(1), color: PURPLE, label: 'f(1) = 1' },
      { x: 2, y: f(2), color: PURPLE, label: 'f(2) = 2' },
    ],
  }

  const steps: GStep[] = []

  // step 1: the concept of the parabola
  steps.push({
    plot: base,
    instruction: {
      en: `New function: $f(x) = ${TEX}$ on $[0,\\;2]$. A chord cannot follow this S-shape. Simpson CONCEPT: through each PAIR of sub-intervals, fit a PARABOLA using three points $f(a)$, $f(m)$, $f(b)$ — a parabola can bend, a chord cannot.`,
      fr: `Nouvelle fonction : $f(x) = ${TEX}$ sur $[0,\\;2]$. Une corde ne peut pas suivre cette forme en S. CONCEPT de Simpson : sur chaque PAIRE de sous-intervalles, on ajuste une PARABOLE par trois points $f(a)$, $f(m)$, $f(b)$ — une parabole peut se courber, pas une corde.`,
    },
  })

  // step 2: input — f(1), the midpoint
  steps.push({
    plot: { ...base, points: [{ x: 0, y: f(0), color: PURPLE, label: 'f(0) = 2' }, { x: 2, y: f(2), color: PURPLE, label: 'f(2) = 2' }] },
    instruction: {
      en: `The three Simpson nodes on $[0,\\;2]$ are $0$, $1$, $2$ ($h = 1$). We already have $f(0) = 2$ and $f(2) = 2$. Compute the midpoint value $f(1)$ yourself.`,
      fr: `Les trois noeuds de Simpson sur $[0,\\;2]$ sont $0$, $1$, $2$ ($h = 1$). On a deja $f(0) = 2$ et $f(2) = 2$. Calculez vous-meme la valeur au milieu $f(1)$.`,
    },
    input: {
      label: '$f(1) =$', expected: 1, tol: 0.01,
      ok: { en: `Correct: $f(1) = 1 - 2 + 2 = 1$. The three purple points now pin down ONE parabola.`,
            fr: `Exact : $f(1) = 1 - 2 + 2 = 1$. Les trois points violets determinent maintenant UNE parabole.` },
      hint: { en: `Plug $x = 1$ into $${TEX}$ — careful with the minus sign.`,
              fr: `Injectez $x = 1$ dans $${TEX}$ — attention au signe moins.` },
      reveal: { en: `Computation: $f(1) = 1^{3} - 2 \\times 1^{2} + 2 = 1 - 2 + 2 = 1$. Type $1$.`,
                fr: `Calcul : $f(1) = 1^{3} - 2 \\times 1^{2} + 2 = 1 - 2 + 2 = 1$. Tapez $1$.` },
      plotOnOk: withParabola,
    },
  })

  // step 3: choice — the weights 1-4-1
  steps.push({
    plot: withParabola,
    instruction: {
      en: `The dashed purple curve is the unique parabola through YOUR three points. Integrating that parabola exactly gives Simpson's rule. Its weights are famous.`,
      fr: `La courbe violette pointillee est l'unique parabole passant par VOS trois points. Integrer exactement cette parabole donne la regle de Simpson. Ses poids sont celebres.`,
    },
    choice: {
      prompt: { en: 'Which weight pattern does Simpson give to $f(0)$, $f(1)$, $f(2)$?',
                fr: 'Quel motif de poids Simpson donne-t-il a $f(0)$, $f(1)$, $f(2)$ ?' },
      choices: [
        {
          label: { en: '$\\frac{h}{3}(1,\\;4,\\;1)$ — the midpoint counts four times', fr: '$\\frac{h}{3}(1,\\;4,\\;1)$ — le milieu compte quatre fois' },
          correct: true,
          feedback: {
            en: `Yes: $S = \\frac{h}{3}(f(0) + 4f(1) + f(2))$. The midpoint carries most of the curvature information, hence its big weight.`,
            fr: `Oui : $S = \\frac{h}{3}(f(0) + 4f(1) + f(2))$. Le milieu porte l'essentiel de l'information de courbure, d'ou son grand poids.`,
          },
        },
        {
          label: { en: '$\\frac{h}{2}(1,\\;2,\\;1)$ — equal sharing like trapezoids', fr: '$\\frac{h}{2}(1,\\;2,\\;1)$ — partage egal comme les trapezes' },
          correct: false,
          feedback: {
            en: `That is the composite TRAPEZOID rule (two chords). Simpson integrates a parabola, and the exact integration of a parabola through three equidistant points yields weights $\\frac{h}{3}(1,\\;4,\\;1)$.`,
            fr: `C'est la regle composite des TRAPEZES (deux cordes). Simpson integre une parabole, et l'integration exacte d'une parabole par trois points equidistants donne les poids $\\frac{h}{3}(1,\\;4,\\;1)$.`,
          },
        },
      ],
    },
  })

  // step 4: input — S2
  steps.push({
    plot: withParabola,
    instruction: {
      en: `APPLY Simpson with YOUR values: $S_{2} = \\frac{h}{3}(f(0) + 4f(1) + f(2)) = \\frac{1}{3}(2 + 4 \\times 1 + 2)$. Compute it.`,
      fr: `APPLIQUEZ Simpson avec VOS valeurs : $S_{2} = \\frac{h}{3}(f(0) + 4f(1) + f(2)) = \\frac{1}{3}(2 + 4 \\times 1 + 2)$. Calculez.`,
    },
    input: {
      label: '$S_2 =$', expected: S2, tol: S2 * 0.01,
      ok: { en: `Yes: $S_{2} = \\frac{1}{3}(2 + 4 + 2) = \\frac{8}{3} \\approx ${fmt(S2)}$. Keep this number in mind...`,
            fr: `Oui : $S_{2} = \\frac{1}{3}(2 + 4 + 2) = \\frac{8}{3} \\approx ${fmt(S2)}$. Gardez ce nombre en tete...` },
      hint: { en: 'Add inside: $2 + 4 + 2 = 8$, then divide by $3$.',
              fr: 'Additionnez dans la parenthese : $2 + 4 + 2 = 8$, puis divisez par $3$.' },
      reveal: { en: `Computation: $\\frac{1}{3} \\times 8 = \\frac{8}{3} \\approx ${fmt(S2)}$. Type $${fmt(S2)}$.`,
                fr: `Calcul : $\\frac{1}{3} \\times 8 = \\frac{8}{3} \\approx ${fmt(S2)}$. Tapez $${fmt(S2)}$.` },
      plotOnOk: withParabola,
    },
  })

  // step 5: input — verify the exact integral
  steps.push({
    plot: withParabola,
    instruction: {
      en: `Now the surprise check. Compute the EXACT integral with the antiderivative $F(x) = \\frac{x^{4}}{4} - \\frac{2x^{3}}{3} + 2x$: $\\int_{0}^{2} (${TEX})\\,dx = F(2) - F(0) = 4 - \\frac{16}{3} + 4$.`,
      fr: `Place a la verification surprise. Calculez l'integrale EXACTE avec la primitive $F(x) = \\frac{x^{4}}{4} - \\frac{2x^{3}}{3} + 2x$ : $\\int_{0}^{2} (${TEX})\\,dx = F(2) - F(0) = 4 - \\frac{16}{3} + 4$.`,
    },
    input: {
      label: '$I =$', expected: exact, tol: exact * 0.01,
      ok: { en: `Exact value: $8 - \\frac{16}{3} = \\frac{8}{3} \\approx ${fmt(exact)}$ — IDENTICAL to your $S_{2}$! Simpson made ZERO error on a cubic.`,
            fr: `Valeur exacte : $8 - \\frac{16}{3} = \\frac{8}{3} \\approx ${fmt(exact)}$ — IDENTIQUE a votre $S_{2}$ ! Simpson a fait ZERO erreur sur une cubique.` },
      hint: { en: 'Compute $4 + 4 = 8$, then subtract $\\frac{16}{3} \\approx 5.3333$.',
              fr: 'Calculez $4 + 4 = 8$, puis soustrayez $\\frac{16}{3} \\approx 5.3333$.' },
      reveal: { en: `Computation: $4 - \\frac{16}{3} + 4 = 8 - \\frac{16}{3} = \\frac{24-16}{3} = \\frac{8}{3} \\approx ${fmt(exact)}$. Type $${fmt(exact)}$.`,
                fr: `Calcul : $4 - \\frac{16}{3} + 4 = 8 - \\frac{16}{3} = \\frac{24-16}{3} = \\frac{8}{3} \\approx ${fmt(exact)}$. Tapez $${fmt(exact)}$.` },
      plotOnOk: withParabola,
    },
  })

  // step 6: choice — why exact (degree <= 3)
  steps.push({
    plot: withParabola,
    instruction: {
      en: `Your $S_{2} = \\frac{8}{3}$ equals the exact integral, even though the purple parabola is clearly NOT the cubic $f$. This is no accident.`,
      fr: `Votre $S_{2} = \\frac{8}{3}$ egale l'integrale exacte, alors que la parabole violette n'est manifestement PAS la cubique $f$. Ce n'est pas un hasard.`,
    },
    choice: {
      prompt: { en: 'Why is Simpson EXACT here?', fr: 'Pourquoi Simpson est-il EXACT ici ?' },
      choices: [
        {
          label: { en: 'Simpson has degree of exactness 3: cubic error terms cancel by symmetry', fr: 'Simpson a un degre d\'exactitude 3 : les termes d\'erreur cubiques s\'annulent par symetrie' },
          correct: true,
          feedback: {
            en: `Right. Built for degree 2, Simpson gets degree 3 FOR FREE: the cubic part of $f - p$ is odd around the midpoint, so its integral cancels. Error $\\propto f^{(4)}$, and here $f^{(4)} = 0$.`,
            fr: `Exact. Construite pour le degre 2, la regle de Simpson obtient le degre 3 GRATUITEMENT : la partie cubique de $f - p$ est impaire autour du milieu, donc son integrale s'annule. Erreur $\\propto f^{(4)}$, et ici $f^{(4)} = 0$.`,
          },
        },
        {
          label: { en: 'Lucky coincidence: the parabola happens to equal $f$', fr: 'Pure coincidence : la parabole se trouve egaler $f$' },
          correct: false,
          feedback: {
            en: `Look at the graph: the dashed parabola and $f$ only MEET at the three nodes, they differ everywhere else. Yet their integrals match: the areas the parabola misses on one side, it gains on the other. That symmetry holds for EVERY cubic.`,
            fr: `Regardez le graphe : la parabole pointillee et $f$ ne se RENCONTRENT qu'aux trois noeuds, elles different partout ailleurs. Pourtant leurs integrales coincident : l'aire que la parabole rate d'un cote, elle la regagne de l'autre. Cette symetrie vaut pour TOUTE cubique.`,
          },
        },
      ],
    },
  })

  return {
    title: { en: 'Apply Simpson\'s rule yourself', fr: 'Appliquez la regle de Simpson vous-meme' },
    steps,
    done: {
      intro: { en: 'You fitted a parabola through your three values, applied the 1-4-1 weights, and PROVED experimentally that Simpson is exact on a cubic:',
               fr: 'Vous avez ajuste une parabole par vos trois valeurs, applique les poids 1-4-1, et PROUVE experimentalement que Simpson est exact sur une cubique :' },
      eqTex: `\\int_{0}^{2} (${TEX})\\,dx = \\tfrac{8}{3} = S_{2}`,
      table: {
        cols: [
          { en: 'method', fr: 'methode' },
          { en: 'value', fr: 'valeur' },
          { en: 'error', fr: 'erreur' },
        ],
        rows: [
          [`$T_{2}$ (chords)`, `$${fmt(T2)}$`, `$${fmt(T2 - exact)}$`],
          [`$S_{2}$ (parabola)`, `$${fmt(S2)}$`, `$0$`],
          [`exact`, `$\\tfrac{8}{3} \\approx ${fmt(exact)}$`, '&#8212;'],
        ],
      },
      plot: withParabola,
      outro: { en: `Concept &#8594; application: a bending model (parabola) beats a straight one (chord), and the hidden symmetry pushes exactness up to degree 3 — error $\\propto h^{4} f^{(4)}$. Same 3 evaluations as the trapezoid pair, infinitely better here. Choosing the MODEL is choosing the accuracy.`,
               fr: `Concept &#8594; application : un modele qui se courbe (parabole) bat un modele droit (corde), et la symetrie cachee pousse l'exactitude jusqu'au degre 3 — erreur $\\propto h^{4} f^{(4)}$. Memes 3 evaluations que la paire de trapezes, infiniment mieux ici. Choisir le MODELE, c'est choisir la precision.` },
    },
  }
}

// ==================================================================
// 5. Gauss quadrature — f(x) = x^3 + x^2 + 1 on [-1, 1]
// ==================================================================
function buildGauss(): GScript {
  const f = (x: number) => x * x * x + x * x + 1
  const TEX = 'x^{3}+x^{2}+1'
  const exact = 2 / 3 + 2                       // 8/3
  const xg = 1 / Math.sqrt(3)                    // 0.5774
  const fPlus = f(xg)                            // 1.5258
  const fMinus = f(-xg)                          // 1.1409
  const G2 = fPlus + fMinus                      // 8/3 exactement
  const trapEnd = f(-1) + f(1)                   // 4: trapezoid on the endpoints

  const base: PlotSpec = { xMin: -1.3, xMax: 1.3, fns: [{ fn: f }], interval: [-1, 1] }
  const gaussNodes: PlotSpec = {
    ...base,
    vlines: [
      { x: -xg, color: GREEN, label: '-0.5774' },
      { x: xg, color: GREEN, label: '+0.5774' },
    ],
    points: [
      { x: -xg, y: fMinus, color: GREEN },
      { x: xg, y: fPlus, color: GREEN },
    ],
  }
  const equiNodes: PlotSpec = {
    ...base,
    vlines: [
      { x: -1, color: ORANGE, label: '-1' },
      { x: 1, color: ORANGE, label: '+1' },
    ],
    points: [
      { x: -1, y: f(-1), color: ORANGE },
      { x: 1, y: f(1), color: ORANGE },
    ],
  }

  const steps: GStep[] = []

  // step 1: the concept — choose the nodes
  steps.push({
    plot: base,
    instruction: {
      en: `Final concept. So far the nodes were IMPOSED (endpoints, midpoints). Gauss CONCEPT: let the method CHOOSE both the nodes $x_{i}$ and the weights $w_{i}$ to maximize accuracy. Target: $\\int_{-1}^{1} (${TEX})\\,dx$, whose exact value is $\\frac{2}{3} + 2 = \\frac{8}{3} \\approx ${fmt(exact)}$ (the odd part $x^{3}$ integrates to zero).`,
      fr: `Dernier concept. Jusqu'ici les noeuds etaient IMPOSES (bornes, milieux). CONCEPT de Gauss : laisser la methode CHOISIR a la fois les noeuds $x_{i}$ et les poids $w_{i}$ pour maximiser la precision. Cible : $\\int_{-1}^{1} (${TEX})\\,dx$, de valeur exacte $\\frac{2}{3} + 2 = \\frac{8}{3} \\approx ${fmt(exact)}$ (la partie impaire $x^{3}$ s'integre a zero).`,
    },
  })

  // step 2: choice — how many points for degree 3
  steps.push({
    plot: base,
    instruction: {
      en: `Counting argument: $n$ points give $2n$ free parameters ($n$ nodes + $n$ weights), enough to be exact for all polynomials of degree $\\le 2n - 1$.`,
      fr: `Argument de comptage : $n$ points donnent $2n$ parametres libres ($n$ noeuds + $n$ poids), assez pour etre exact pour tous les polynomes de degre $\\le 2n - 1$.`,
    },
    choice: {
      prompt: { en: 'How many Gauss points are needed to integrate our degree-3 polynomial EXACTLY?',
                fr: 'Combien de points de Gauss faut-il pour integrer EXACTEMENT notre polynome de degre 3 ?' },
      choices: [
        {
          label: { en: '$2$ points: $2n - 1 = 3$', fr: '$2$ points : $2n - 1 = 3$' },
          correct: true,
          plot: gaussNodes,
          feedback: {
            en: `Yes: with $n = 2$, degree of exactness $2 \\times 2 - 1 = 3$. The two green nodes appear: $x = \\pm\\frac{1}{\\sqrt{3}}$, with equal weights $w_{1} = w_{2} = 1$.`,
            fr: `Oui : avec $n = 2$, degre d'exactitude $2 \\times 2 - 1 = 3$. Les deux noeuds verts apparaissent : $x = \\pm\\frac{1}{\\sqrt{3}}$, avec poids egaux $w_{1} = w_{2} = 1$.`,
          },
        },
        {
          label: { en: '$4$ points: one per degree', fr: '$4$ points : un par degre' },
          correct: false,
          feedback: {
            en: `That would be the Newton-Cotes logic (fixed nodes). Gauss also optimizes WHERE to evaluate: $n$ points buy degree $2n - 1$, so $n = 2$ already covers degree 3. Half the work.`,
            fr: `Ce serait la logique de Newton-Cotes (noeuds fixes). Gauss optimise aussi OU evaluer : $n$ points achetent le degre $2n - 1$, donc $n = 2$ couvre deja le degre 3. Moitie moins de travail.`,
          },
        },
      ],
    },
  })

  // step 3: input — the positive node
  steps.push({
    plot: gaussNodes,
    instruction: {
      en: `The 2-point Gauss-Legendre nodes are the roots of the Legendre polynomial $P_{2}(x) = \\frac{3x^{2}-1}{2}$. Solve $P_{2}(x) = 0$ and type the POSITIVE node (4 decimals).`,
      fr: `Les noeuds de Gauss-Legendre a 2 points sont les racines du polynome de Legendre $P_{2}(x) = \\frac{3x^{2}-1}{2}$. Resolvez $P_{2}(x) = 0$ et tapez le noeud POSITIF (4 decimales).`,
    },
    input: {
      label: '$x =$', expected: xg, tol: xg * 0.01,
      ok: { en: `Correct: $3x^{2} = 1 \\Rightarrow x = \\frac{1}{\\sqrt{3}} \\approx ${fmt(xg)}$. Note the nodes are NOT the endpoints — they sit strategically inside.`,
            fr: `Exact : $3x^{2} = 1 \\Rightarrow x = \\frac{1}{\\sqrt{3}} \\approx ${fmt(xg)}$. Notez que les noeuds ne sont PAS les bornes — ils se placent strategiquement a l'interieur.` },
      hint: { en: 'Solve $3x^{2} - 1 = 0$, keep the positive root, i.e. $\\frac{1}{\\sqrt{3}}$.',
              fr: 'Resolvez $3x^{2} - 1 = 0$, gardez la racine positive, c\'est-a-dire $\\frac{1}{\\sqrt{3}}$.' },
      reveal: { en: `Computation: $x^{2} = \\frac{1}{3}$, so $x = \\frac{1}{\\sqrt{3}} \\approx ${fmt(xg)}$. Type $${fmt(xg)}$.`,
                fr: `Calcul : $x^{2} = \\frac{1}{3}$, donc $x = \\frac{1}{\\sqrt{3}} \\approx ${fmt(xg)}$. Tapez $${fmt(xg)}$.` },
      plotOnOk: gaussNodes,
    },
  })

  // step 4: input — the Gauss sum
  steps.push({
    plot: gaussNodes,
    instruction: {
      en: `APPLY the rule. With weights $1$ and $1$: $G_{2} = f(${fmt(xg)}) + f(-${fmt(xg)})$. We computed the two values for you: $f(${fmt(xg)}) = ${fmt(fPlus)}$ and $f(-${fmt(xg)}) = ${fmt(fMinus)}$ (green dots). Add them.`,
      fr: `APPLIQUEZ la regle. Avec les poids $1$ et $1$ : $G_{2} = f(${fmt(xg)}) + f(-${fmt(xg)})$. On a calcule les deux valeurs pour vous : $f(${fmt(xg)}) = ${fmt(fPlus)}$ et $f(-${fmt(xg)}) = ${fmt(fMinus)}$ (points verts). Additionnez-les.`,
    },
    input: {
      label: '$G_2 =$', expected: G2, tol: G2 * 0.01,
      ok: { en: `Yes: $G_{2} = ${fmt(fPlus)} + ${fmt(fMinus)} = ${fmt(G2)} = \\frac{8}{3}$ — EXACTLY the integral, with only TWO evaluations. The cubic parts cancel between the symmetric nodes.`,
            fr: `Oui : $G_{2} = ${fmt(fPlus)} + ${fmt(fMinus)} = ${fmt(G2)} = \\frac{8}{3}$ — EXACTEMENT l'integrale, avec seulement DEUX evaluations. Les parties cubiques s'annulent entre les noeuds symetriques.` },
      hint: { en: `Just add the two displayed values: $${fmt(fPlus)} + ${fmt(fMinus)}$ with 4 decimals.`,
              fr: `Additionnez simplement les deux valeurs affichees : $${fmt(fPlus)} + ${fmt(fMinus)}$ avec 4 decimales.` },
      reveal: { en: `Computation: $${fmt(fPlus)} + ${fmt(fMinus)} = ${fmt(G2)}$. Type $${fmt(G2)}$.`,
                fr: `Calcul : $${fmt(fPlus)} + ${fmt(fMinus)} = ${fmt(G2)}$. Tapez $${fmt(G2)}$.` },
      plotOnOk: gaussNodes,
    },
  })

  // step 5: choice — compare with equidistant nodes
  steps.push({
    plot: equiNodes,
    instruction: {
      en: `Counter-experiment: same budget of TWO evaluations, but at the IMPOSED endpoints $\\pm 1$ (trapezoid rule, orange): $T = \\frac{2}{2}(f(-1) + f(1)) = f(-1) + f(1) = 1 + 3 = ${fmt(trapEnd)}$.`,
      fr: `Contre-experience : meme budget de DEUX evaluations, mais aux bornes IMPOSEES $\\pm 1$ (regle des trapezes, orange) : $T = \\frac{2}{2}(f(-1) + f(1)) = f(-1) + f(1) = 1 + 3 = ${fmt(trapEnd)}$.`,
    },
    choice: {
      prompt: { en: 'Two evaluations each — who wins, and by how much?',
                fr: 'Deux evaluations chacun — qui gagne, et de combien ?' },
      choices: [
        {
          label: { en: `Gauss: error $0$ versus trapezoid error $${fmt(trapEnd - exact)}$`,
                   fr: `Gauss : erreur $0$ contre erreur trapezes $${fmt(trapEnd - exact)}$` },
          correct: true,
          plot: gaussNodes,
          feedback: {
            en: `Exactly: your $G_{2} = \\frac{8}{3}$ is exact, while the trapezoid gets $4$, an error of $4 - \\frac{8}{3} = \\frac{4}{3} \\approx ${fmt(trapEnd - exact)}$ — that is $50\\%$ of the true value. Same cost, radically different accuracy: only the POSITION of the nodes changed.`,
            fr: `Exactement : votre $G_{2} = \\frac{8}{3}$ est exact, tandis que les trapezes donnent $4$, une erreur de $4 - \\frac{8}{3} = \\frac{4}{3} \\approx ${fmt(trapEnd - exact)}$ — soit $50\\%$ de la vraie valeur. Meme cout, precision radicalement differente : seule la POSITION des noeuds a change.`,
          },
        },
        {
          label: { en: 'A tie: same number of points means same accuracy', fr: 'Egalite : meme nombre de points, meme precision' },
          correct: false,
          feedback: {
            en: `Compare the numbers you produced: $G_{2} = ${fmt(G2)}$ (exact) versus $T = ${fmt(trapEnd)}$. The point COUNT is equal, but the point PLACEMENT is not — and that placement is the whole Gauss concept.`,
            fr: `Comparez les nombres que vous avez produits : $G_{2} = ${fmt(G2)}$ (exact) contre $T = ${fmt(trapEnd)}$. Le NOMBRE de points est egal, mais leur PLACEMENT ne l'est pas — et ce placement est tout le concept de Gauss.`,
          },
        },
      ],
    },
  })

  // step 6: choice — generalization
  steps.push({
    plot: gaussNodes,
    instruction: {
      en: `Last conceptual question to lock in the idea.`,
      fr: `Derniere question conceptuelle pour ancrer l'idee.`,
    },
    choice: {
      prompt: { en: 'With $n = 3$ Gauss points, exactness would reach degree...',
                fr: 'Avec $n = 3$ points de Gauss, l\'exactitude atteindrait le degre...' },
      choices: [
        {
          label: { en: '$5$, because $2n - 1 = 5$', fr: '$5$, car $2n - 1 = 5$' },
          correct: true,
          feedback: {
            en: `Right: $2 \\times 3 - 1 = 5$. Each extra Gauss point buys TWO extra degrees (a node AND a weight). This is why Gauss quadrature dominates when each evaluation of $f$ is expensive.`,
            fr: `Exact : $2 \\times 3 - 1 = 5$. Chaque point de Gauss supplementaire achete DEUX degres de plus (un noeud ET un poids). C'est pourquoi la quadrature de Gauss domine quand chaque evaluation de $f$ coute cher.`,
          },
        },
        {
          label: { en: '$3$, one degree per point', fr: '$3$, un degre par point' },
          correct: false,
          feedback: {
            en: `You just verified the opposite with $n = 2$: it was exact up to degree $3$, not $2$. Free nodes double the return: $2n - 1 = 5$ for $n = 3$.`,
            fr: `Vous venez de verifier le contraire avec $n = 2$ : exactitude jusqu'au degre $3$, pas $2$. Les noeuds libres doublent le rendement : $2n - 1 = 5$ pour $n = 3$.`,
          },
        },
      ],
    },
  })

  return {
    title: { en: 'Place the Gauss nodes yourself', fr: 'Placez les noeuds de Gauss vous-meme' },
    steps,
    done: {
      intro: { en: 'You chose the number of points, located the optimal nodes, and verified the exactness with your own sum:',
               fr: 'Vous avez choisi le nombre de points, localise les noeuds optimaux, et verifie l\'exactitude avec votre propre somme :' },
      eqTex: `\\int_{-1}^{1} (${TEX})\\,dx = f\\left(\\tfrac{1}{\\sqrt{3}}\\right) + f\\left(-\\tfrac{1}{\\sqrt{3}}\\right) = \\tfrac{8}{3}`,
      table: {
        cols: [
          { en: 'rule (2 evaluations)', fr: 'regle (2 evaluations)' },
          { en: 'nodes', fr: 'noeuds' },
          { en: 'value', fr: 'valeur' },
          { en: 'error', fr: 'erreur' },
        ],
        rows: [
          [`Gauss $G_{2}$`, `$\\pm ${fmt(xg)}$`, `$${fmt(G2)}$`, `$0$`],
          [`Trapezoid $T$`, `$\\pm 1$`, `$${fmt(trapEnd)}$`, `$${fmt(trapEnd - exact)}$`],
          [`exact`, '&#8212;', `$\\tfrac{8}{3} \\approx ${fmt(exact)}$`, '&#8212;'],
        ],
      },
      plot: gaussNodes,
      outro: { en: `Concept &#8594; application: the integration journey ends where it began — choosing WHERE to sample $f$. Riemann sampled naively, trapezoid and Simpson improved the MODEL, Gauss optimizes the SAMPLING itself: $n$ smart points beat $2n$ naive ones. Two evaluations gave you the exact $\\frac{8}{3}$.`,
               fr: `Concept &#8594; application : le voyage de l'integration finit la ou il a commence — choisir OU echantillonner $f$. Riemann echantillonnait naivement, trapezes et Simpson ont ameliore le MODELE, Gauss optimise l'ECHANTILLONNAGE lui-meme : $n$ points malins battent $2n$ points naifs. Deux evaluations vous ont donne le $\\frac{8}{3}$ exact.` },
    },
  }
}

// ==================================================================
// Export
// ==================================================================
export const GUIDED_INTEGRATION: Record<string, GScript> = {
  concept_riemann_sums: buildRiemann(),
  concept_definite_integrals: buildDefiniteIntegrals(),
  concept_trapezoidal: buildTrapezoidal(),
  concept_simpson: buildSimpson(),
  concept_gaussian_quadrature: buildGauss(),
}
