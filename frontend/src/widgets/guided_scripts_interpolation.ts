/**
 * Guided scenarios — Interpolation module.
 *
 * Same pedagogical principle as guided_scripts_rootfinding.ts:
 * link a mathematical CONCEPT -> APPLICATION. The data are fixed
 * by the lesson, the student makes the decisions (choices or values
 * computed by hand) and sees the immediate graphical effect.
 */

import {
  GScript, GStep, PlotSpec,
  ORANGE, GREEN, TEAL, BLUE, PURPLE,
  fmt,
} from './guided_core'

// ==================================================================
// 1. Polynomial bases — p(x) = 0.3x^3 - 1.2x^2 + x + 2
// ==================================================================
function buildPolynomialBasics(): GScript {
  const c3 = 0.3, c2 = -1.2, c1 = 1, c0 = 2
  const p = (x: number) => c3 * x ** 3 + c2 * x ** 2 + c1 * x + c0
  const TEX = 'p(x) = 0.3x^{3} - 1.2x^{2} + x + 2'
  const X = 2
  const t3 = c3 * X ** 3        // 2.4
  const t2 = c2 * X ** 2        // -4.8
  const t1 = c1 * X             // 2
  const pX = p(X)               // 1.6

  const base: PlotSpec = { xMin: -1.2, xMax: 4.2, fns: [{ fn: p }] }
  const steps: GStep[] = []

  // step 1: read the degree
  steps.push({
    plot: base,
    instruction: {
      en: `Here is the curve of $${TEX}$, fixed by the course. A polynomial is entirely described by its COEFFICIENTS. First decision: read its structure.`,
      fr: `Voici la courbe de $${TEX}$, fixee par le cours. Un polynome est entierement decrit par ses COEFFICIENTS. Premiere decision : lire sa structure.`,
    },
    choice: {
      prompt: { en: 'What is the degree of $p$?', fr: 'Quel est le degre de $p$ ?' },
      choices: [2, 3, 4].map(d => ({
        label: { en: `degree $${d}$`, fr: `degre $${d}$` },
        correct: d === 3,
        feedback: d === 3
          ? { en: 'Yes: the highest power with a nonzero coefficient is $x^{3}$, so the degree is $3$.',
              fr: 'Oui : la plus haute puissance a coefficient non nul est $x^{3}$, donc le degre est $3$.' }
          : { en: `No: look at the highest power that actually appears. The term $0.3x^{3}$ rules — the degree is not $${d}$.`,
              fr: `Non : regardez la plus haute puissance qui apparait vraiment. Le terme $0.3x^{3}$ domine — le degre n'est pas $${d}$.` },
      })),
    },
  })

  // step 2: degree -> number of bends (local extrema)
  const dp = (x: number) => 3 * c3 * x ** 2 + 2 * c2 * x + c1
  // roots of p': local extrema, computed numerically
  const extrema: number[] = []
  let prev = dp(-1.2)
  for (let i = 1; i <= 540; i++) {
    const x = -1.2 + (5.4 * i) / 540
    const cur = dp(x)
    if (prev * cur < 0) {
      // raffinage par dichotomie
      let a = x - 5.4 / 540, b = x
      for (let k = 0; k < 50; k++) {
        const m = (a + b) / 2
        if (dp(a) * dp(m) <= 0) b = m; else a = m
      }
      extrema.push((a + b) / 2)
    }
    prev = cur
  }
  steps.push({
    plot: base,
    instruction: {
      en: 'CONCEPT: a polynomial of degree $n$ changes direction at most $n-1$ times (its derivative has degree $n-1$).',
      fr: 'CONCEPT : un polynome de degre $n$ change de direction au plus $n-1$ fois (sa derivee est de degre $n-1$).',
    },
    choice: {
      prompt: { en: 'How many bumps (local extrema) can this cubic have at most?',
                fr: 'Combien de bosses (extrema locaux) cette cubique peut-elle avoir au maximum ?' },
      choices: [1, 2, 3].map(n => ({
        label: { en: `$${n}$`, fr: `$${n}$` },
        correct: n === 2,
        plot: n === 2 ? {
          ...base,
          vlines: extrema.map((x, i) => ({ x, color: PURPLE, dash: '5 4', label: `extremum ${i + 1}` })),
        } : undefined,
        feedback: n === 2
          ? { en: `Exactly: $p'$ has degree $2$, so at most $2$ roots — see the two purple lines where the curve turns (near $x = ${fmt(extrema[0], 2)}$ and $x = ${fmt(extrema[1], 2)}$).`,
              fr: `Exactement : $p'$ est de degre $2$, donc au plus $2$ racines — voyez les deux lignes violettes ou la courbe tourne (vers $x = ${fmt(extrema[0], 2)}$ et $x = ${fmt(extrema[1], 2)}$).` }
          : { en: 'No: count with the derivative. $p\'$ has degree $3 - 1 = 2$, so at most $2$ turning points.',
              fr: 'Non : comptez avec la derivee. $p\'$ est de degre $3 - 1 = 2$, donc au plus $2$ points de retournement.' },
      })),
    },
  })

  // step 3: evaluate term by term — the cubic term
  steps.push({
    plot: { ...base, vlines: [{ x: X, color: ORANGE, dash: '6 4', label: `x = ${fmt(X)}` }] },
    instruction: {
      en: `APPLICATION: evaluate $p(${fmt(X)})$ term by term, like a computer would. Start with the cubic term.`,
      fr: `APPLICATION : evaluez $p(${fmt(X)})$ terme a terme, comme le ferait un ordinateur. Commencez par le terme cubique.`,
    },
    input: {
      label: '$0.3 \\times 2^{3} =$', expected: t3, tol: Math.max(Math.abs(t3) * 0.01, 0.01),
      ok: { en: `Correct: $0.3 \\cdot 2^{3} = 0.3 \\cdot 8 = ${fmt(t3)}$.`,
            fr: `Exact : $0.3 \\cdot 2^{3} = 0.3 \\cdot 8 = ${fmt(t3)}$.` },
      hint: { en: 'Compute $2^{3}$ first, then multiply by $0.3$.',
              fr: 'Calculez d\'abord $2^{3}$, puis multipliez par $0.3$.' },
      reveal: { en: `Full computation: $2^{3} = 8$, then $0.3 \\cdot 8 = ${fmt(t3)}$. Type this value.`,
                fr: `Calcul complet : $2^{3} = 8$, puis $0.3 \\cdot 8 = ${fmt(t3)}$. Tapez cette valeur.` },
    },
  })

  // step 4: total p(2)
  steps.push({
    plot: { ...base, vlines: [{ x: X, color: ORANGE, dash: '6 4', label: `x = ${fmt(X)}` }] },
    instruction: {
      en: `Now sum ALL the terms: $p(${fmt(X)}) = ${fmt(t3)} + (${fmt(t2)}) + ${fmt(t1)} + ${fmt(c0)}$. Type the total — your point will appear on the curve.`,
      fr: `Sommez maintenant TOUS les termes : $p(${fmt(X)}) = ${fmt(t3)} + (${fmt(t2)}) + ${fmt(t1)} + ${fmt(c0)}$. Tapez le total — votre point apparaitra sur la courbe.`,
    },
    input: {
      label: '$p(2) =$', expected: pX, tol: Math.max(Math.abs(pX) * 0.01, 0.01),
      ok: { en: `Yes: $p(${fmt(X)}) = ${fmt(pX)}$. The green dot is YOUR computed point, exactly on the curve.`,
            fr: `Oui : $p(${fmt(X)}) = ${fmt(pX)}$. Le point vert est VOTRE point calcule, exactement sur la courbe.` },
      hint: { en: `Add the four terms: $${fmt(t3)} - ${fmt(-t2)} + ${fmt(t1)} + ${fmt(c0)}$. Watch the signs.`,
              fr: `Additionnez les quatre termes : $${fmt(t3)} - ${fmt(-t2)} + ${fmt(t1)} + ${fmt(c0)}$. Attention aux signes.` },
      reveal: { en: `$${fmt(t3)} ${fmt(t2)} + ${fmt(t1)} + ${fmt(c0)} = ${fmt(pX)}$. Type this value.`,
                fr: `$${fmt(t3)} ${fmt(t2)} + ${fmt(t1)} + ${fmt(c0)} = ${fmt(pX)}$. Tapez cette valeur.` },
      plotOnOk: {
        ...base,
        vlines: [{ x: X, color: ORANGE, dash: '6 4' }],
        points: [{ x: X, y: pX, color: GREEN, label: `p(2) = ${fmt(pX)}` }],
      },
    },
  })

  // step 5: how many points fix a polynomial of degree n?
  steps.push({
    plot: {
      ...base,
      points: [{ x: X, y: pX, color: GREEN, label: `p(2) = ${fmt(pX)}` }],
    },
    instruction: {
      en: 'Key CONCEPT for interpolation: a polynomial of degree $n$ has $n+1$ coefficients, so it is uniquely pinned by data points.',
      fr: 'CONCEPT cle pour l\'interpolation : un polynome de degre $n$ a $n+1$ coefficients, il est donc fixe de maniere unique par des points de donnees.',
    },
    choice: {
      prompt: { en: 'How many points uniquely determine a cubic like this one?',
                fr: 'Combien de points determinent de maniere unique une cubique comme celle-ci ?' },
      choices: [3, 4, 5].map(n => ({
        label: { en: `$${n}$ points`, fr: `$${n}$ points` },
        correct: n === 4,
        plot: n === 4 ? {
          ...base,
          points: [-1, 0.5, 2, 3.5].map(x => ({ x, y: p(x), color: BLUE, label: `(${fmt(x)}, ${fmt(p(x), 2)})` })),
        } : undefined,
        feedback: n === 4
          ? { en: 'Yes: $4$ unknown coefficients $(c_{0}, c_{1}, c_{2}, c_{3})$ need $4$ equations, i.e. $4$ points. The blue dots now pin the curve completely.',
              fr: 'Oui : $4$ coefficients inconnus $(c_{0}, c_{1}, c_{2}, c_{3})$ exigent $4$ equations, donc $4$ points. Les points bleus fixent maintenant la courbe completement.' }
          : { en: `No: count the unknowns. Degree $3$ means coefficients $c_{0}, c_{1}, c_{2}, c_{3}$ — that is $3 + 1$ numbers, not $${n}$.`,
              fr: `Non : comptez les inconnues. Degre $3$ signifie coefficients $c_{0}, c_{1}, c_{2}, c_{3}$ — soit $3 + 1$ nombres, pas $${n}$.` },
      })),
    },
  })

  return {
    title: { en: 'Read and evaluate a polynomial yourself', fr: 'Lisez et evaluez un polynome vous-meme' },
    steps,
    done: {
      intro: { en: 'You did not memorize a formula — you APPLIED the structure of a polynomial. Your decisions:',
               fr: 'Vous n\'avez pas memorise une formule — vous avez APPLIQUE la structure d\'un polynome. Vos decisions :' },
      eqTex: TEX,
      table: {
        cols: [
          { en: 'decision', fr: 'decision' },
          { en: 'your answer', fr: 'votre reponse' },
          { en: 'why it matters', fr: 'pourquoi c\'est important' },
        ],
        rows: [
          ['degree', '$3$', '$n+1 = 4$ coefficients'],
          ['max bumps', '$2$', '$\\deg p\' = n - 1$'],
          [`$0.3 \\cdot 2^{3}$`, `$${fmt(t3)}$`, 'term-by-term evaluation'],
          [`$p(2)$`, `$${fmt(pX)}$`, 'point on the curve'],
          ['points to pin a cubic', '$4$', 'basis of interpolation'],
        ],
      },
      plot: {
        ...base,
        points: [
          { x: X, y: pX, color: GREEN, label: `p(2) = ${fmt(pX)}` },
          ...[-1, 0.5, 3.5].map(x => ({ x, y: p(x), color: BLUE })),
        ],
      },
      outro: { en: 'Concept &#8594; application: a degree-$n$ polynomial is a vector of $n+1$ coefficients, evaluated term by term, and pinned by $n+1$ points. That last fact IS interpolation — next scripts build the pinning polynomial.',
               fr: 'Concept &#8594; application : un polynome de degre $n$ est un vecteur de $n+1$ coefficients, evalue terme a terme, et fixe par $n+1$ points. Ce dernier fait EST l\'interpolation — les scripts suivants construisent le polynome qui epingle les points.' },
    },
  }
}

// ==================================================================
// Data common to scripts 2-4: (0,1), (1,3), (2,2)
// ==================================================================
const XS = [0, 1, 2]
const YS = [1, 3, 2]

function lagBasis(j: number, x: number): number {
  let v = 1
  for (let k = 0; k < XS.length; k++) {
    if (k !== j) v *= (x - XS[k]) / (XS[j] - XS[k])
  }
  return v
}
function lagP(x: number): number {
  let v = 0
  for (let j = 0; j < XS.length; j++) v += YS[j] * lagBasis(j, x)
  return v
}
const DATA_PTS = XS.map((x, i) => ({ x, y: YS[i], color: BLUE, label: `(${fmt(x)}, ${fmt(YS[i])})` }))

// ==================================================================
// 2. Lagrange — bases l_j then P = sum y_j l_j
// ==================================================================
function buildLagrange(): GScript {
  const steps: GStep[] = []
  const base: PlotSpec = { xMin: -0.6, xMax: 2.6, points: DATA_PTS, yMin: -1.5, yMax: 3.6 }
  const xq = 0.5
  const l1q = lagBasis(1, xq)   // 0.75
  const Pq = lagP(xq)           // 2.375

  // step 1: objective
  steps.push({
    plot: base,
    instruction: {
      en: 'The course fixes three data points: $(0, 1)$, $(1, 3)$, $(2, 2)$. GOAL: build the unique polynomial of degree $\\le 2$ through all three. Lagrange\'s CONCEPT: build it from basis functions $\\ell_{j}$, one per point.',
      fr: 'Le cours fixe trois points de donnees : $(0, 1)$, $(1, 3)$, $(2, 2)$. OBJECTIF : construire l\'unique polynome de degre $\\le 2$ passant par les trois. Le CONCEPT de Lagrange : le construire avec des fonctions de base $\\ell_{j}$, une par point.',
    },
    choice: {
      prompt: { en: 'Three points: what degree does the interpolating polynomial need at most?',
                fr: 'Trois points : quel degre faut-il au plus pour le polynome d\'interpolation ?' },
      choices: [1, 2, 3].map(d => ({
        label: { en: `degree $${d}$`, fr: `degre $${d}$` },
        correct: d === 2,
        feedback: d === 2
          ? { en: 'Yes: $3$ points need $3$ coefficients, hence degree $\\le 2$ — a parabola.',
              fr: 'Oui : $3$ points exigent $3$ coefficients, donc degre $\\le 2$ — une parabole.' }
          : { en: `No: $n+1$ points pin a degree-$n$ polynomial. Here $n+1 = 3$, so $n = 2$, not $${d}$.`,
              fr: `Non : $n+1$ points fixent un polynome de degre $n$. Ici $n+1 = 3$, donc $n = 2$, pas $${d}$.` },
      })),
    },
  })

  // step 2: property l1(x1) = 1
  const l1Plot: PlotSpec = {
    ...base,
    fns: [{ fn: (x: number) => lagBasis(1, x), color: PURPLE }],
    points: [...DATA_PTS, { x: 1, y: 1, color: PURPLE, label: 'ℓ₁(1) = 1' }],
  }
  steps.push({
    plot: { ...base, fns: [{ fn: (x: number) => lagBasis(1, x), color: PURPLE }] },
    instruction: {
      en: 'The purple curve is the basis $\\ell_{1}(x) = \\frac{(x - x_{0})(x - x_{2})}{(x_{1} - x_{0})(x_{1} - x_{2})}$ attached to the point $x_{1} = 1$. Its defining property is what makes the whole method work.',
      fr: 'La courbe violette est la base $\\ell_{1}(x) = \\frac{(x - x_{0})(x - x_{2})}{(x_{1} - x_{0})(x_{1} - x_{2})}$ attachee au point $x_{1} = 1$. Sa propriete fondatrice est ce qui fait marcher toute la methode.',
    },
    choice: {
      prompt: { en: 'What is $\\ell_{1}(x_{1}) = \\ell_{1}(1)$?', fr: 'Que vaut $\\ell_{1}(x_{1}) = \\ell_{1}(1)$ ?' },
      choices: [0, 1, 3].map(v => ({
        label: { en: `$${v}$`, fr: `$${v}$` },
        correct: v === 1,
        plot: v === 1 ? l1Plot : undefined,
        feedback: v === 1
          ? { en: 'Yes: at its OWN node, numerator and denominator are identical, so $\\ell_{1}(1) = 1$. See the purple dot at height $1$.',
              fr: 'Oui : a SON propre noeud, numerateur et denominateur sont identiques, donc $\\ell_{1}(1) = 1$. Voyez le point violet a hauteur $1$.' }
          : { en: 'No: plug $x = 1$ into the formula — the numerator $(1-0)(1-2)$ equals the denominator $(1-0)(1-2)$.',
              fr: 'Non : remplacez $x = 1$ dans la formule — le numerateur $(1-0)(1-2)$ egale le denominateur $(1-0)(1-2)$.' },
      })),
    },
  })

  // step 3: property l1(x0) = 0
  const l1ZerosPlot: PlotSpec = {
    ...base,
    fns: [{ fn: (x: number) => lagBasis(1, x), color: PURPLE }],
    points: [...DATA_PTS,
      { x: 0, y: 0, color: GREEN, label: 'ℓ₁(0) = 0' },
      { x: 2, y: 0, color: GREEN, label: 'ℓ₁(2) = 0' }],
  }
  steps.push({
    plot: l1Plot,
    instruction: {
      en: 'Second half of the concept: what does $\\ell_{1}$ do at the OTHER nodes $x_{0} = 0$ and $x_{2} = 2$?',
      fr: 'Seconde moitie du concept : que fait $\\ell_{1}$ aux AUTRES noeuds $x_{0} = 0$ et $x_{2} = 2$ ?',
    },
    choice: {
      prompt: { en: 'What is $\\ell_{1}(x_{0}) = \\ell_{1}(0)$?', fr: 'Que vaut $\\ell_{1}(x_{0}) = \\ell_{1}(0)$ ?' },
      choices: [0, 1, -1].map(v => ({
        label: { en: `$${v}$`, fr: `$${v}$` },
        correct: v === 0,
        plot: v === 0 ? l1ZerosPlot : undefined,
        feedback: v === 0
          ? { en: 'Yes: the factor $(x - x_{0})$ in the numerator kills $\\ell_{1}$ at $x_{0}$. So $\\ell_{j}(x_{k}) = 0$ for $k \\ne j$ — each basis is invisible at the other nodes (green dots).',
              fr: 'Oui : le facteur $(x - x_{0})$ au numerateur annule $\\ell_{1}$ en $x_{0}$. Donc $\\ell_{j}(x_{k}) = 0$ pour $k \\ne j$ — chaque base est invisible aux autres noeuds (points verts).' }
          : { en: 'No: look at the numerator $(x - 0)(x - 2)$. At $x = 0$ the first factor vanishes.',
              fr: 'Non : regardez le numerateur $(x - 0)(x - 2)$. En $x = 0$ le premier facteur s\'annule.' },
      })),
    },
  })

  // step 4: compute l1(0.5)
  steps.push({
    plot: {
      ...l1ZerosPlot,
      vlines: [{ x: xq, color: ORANGE, dash: '6 4', label: `x = ${fmt(xq)}` }],
    },
    instruction: {
      en: `APPLICATION: evaluate the basis BETWEEN the nodes. Compute $\\ell_{1}(${fmt(xq)}) = \\frac{(${fmt(xq)} - 0)(${fmt(xq)} - 2)}{(1 - 0)(1 - 2)}$ yourself.`,
      fr: `APPLICATION : evaluez la base ENTRE les noeuds. Calculez vous-meme $\\ell_{1}(${fmt(xq)}) = \\frac{(${fmt(xq)} - 0)(${fmt(xq)} - 2)}{(1 - 0)(1 - 2)}$.`,
    },
    input: {
      label: '$\\ell_1(0.5) =$', expected: l1q, tol: Math.max(Math.abs(l1q) * 0.01, 0.01),
      ok: { en: `Correct: $\\ell_{1}(${fmt(xq)}) = ${fmt(l1q)}$. The orange dot sits exactly on the purple basis curve — your value matches the graph.`,
            fr: `Exact : $\\ell_{1}(${fmt(xq)}) = ${fmt(l1q)}$. Le point orange est exactement sur la courbe violette — votre valeur colle au graphe.` },
      hint: { en: 'Numerator: $(0.5)(0.5 - 2)$. Denominator: $(1)(-1)$. Divide.',
              fr: 'Numerateur : $(0.5)(0.5 - 2)$. Denominateur : $(1)(-1)$. Divisez.' },
      reveal: { en: `$\\frac{(0.5)(-1.5)}{(1)(-1)} = \\frac{-0.75}{-1} = ${fmt(l1q)}$. Type this value.`,
                fr: `$\\frac{(0.5)(-1.5)}{(1)(-1)} = \\frac{-0.75}{-1} = ${fmt(l1q)}$. Tapez cette valeur.` },
      plotOnOk: {
        ...l1ZerosPlot,
        vlines: [{ x: xq, color: ORANGE, dash: '6 4' }],
        points: [...DATA_PTS, { x: xq, y: l1q, color: ORANGE, label: `ℓ₁(0.5) = ${fmt(l1q)}` }],
      },
    },
  })

  // step 5: the three bases together
  const allBasesPlot: PlotSpec = {
    ...base,
    fns: [
      { fn: (x: number) => lagBasis(0, x), color: TEAL },
      { fn: (x: number) => lagBasis(1, x), color: PURPLE },
      { fn: (x: number) => lagBasis(2, x), color: ORANGE },
    ],
  }
  steps.push({
    plot: allBasesPlot,
    instruction: {
      en: 'Here are ALL three bases: $\\ell_{0}$ (teal), $\\ell_{1}$ (purple), $\\ell_{2}$ (orange). Each equals $1$ at its own node and $0$ at the others. Now assemble the interpolant: $P(x) = y_{0}\\ell_{0}(x) + y_{1}\\ell_{1}(x) + y_{2}\\ell_{2}(x)$.',
      fr: 'Voici LES trois bases : $\\ell_{0}$ (sarcelle), $\\ell_{1}$ (violet), $\\ell_{2}$ (orange). Chacune vaut $1$ a son noeud et $0$ aux autres. Assemblons l\'interpolant : $P(x) = y_{0}\\ell_{0}(x) + y_{1}\\ell_{1}(x) + y_{2}\\ell_{2}(x)$.',
    },
    choice: {
      prompt: { en: 'Why does $P(x_{1}) = y_{1} = 3$ automatically?',
                fr: 'Pourquoi a-t-on automatiquement $P(x_{1}) = y_{1} = 3$ ?' },
      choices: [
        {
          label: { en: 'At $x_{1}$, only $\\ell_{1}$ survives (equals $1$), the others vanish',
                   fr: 'En $x_{1}$, seule $\\ell_{1}$ survit (vaut $1$), les autres s\'annulent' },
          correct: true,
          plot: {
            ...base,
            fns: [{ fn: lagP, color: GREEN, width: 3.5 }],
          },
          feedback: { en: 'Exactly: $P(x_{1}) = y_{0} \\cdot 0 + y_{1} \\cdot 1 + y_{2} \\cdot 0 = y_{1}$. Watch the green curve thread through ALL three points at once.',
                      fr: 'Exactement : $P(x_{1}) = y_{0} \\cdot 0 + y_{1} \\cdot 1 + y_{2} \\cdot 0 = y_{1}$. Regardez la courbe verte enfiler les TROIS points d\'un coup.' },
        },
        {
          label: { en: 'Because the three bases sum to $3$ at $x_{1}$',
                   fr: 'Parce que les trois bases somment a $3$ en $x_{1}$' },
          correct: false,
          feedback: { en: 'No: the bases sum to $1$ everywhere, not $3$. The trick is that $\\ell_{0}$ and $\\ell_{2}$ both vanish at $x_{1}$, leaving $y_{1} \\cdot 1$.',
                      fr: 'Non : les bases somment a $1$ partout, pas $3$. L\'astuce : $\\ell_{0}$ et $\\ell_{2}$ s\'annulent en $x_{1}$, ne laissant que $y_{1} \\cdot 1$.' },
        },
      ],
    },
  })

  // step 6: evaluate P(0.5)
  const finalPlot: PlotSpec = {
    ...base,
    fns: [{ fn: lagP, color: GREEN, width: 3.5 }],
  }
  steps.push({
    plot: { ...finalPlot, vlines: [{ x: xq, color: ORANGE, dash: '6 4', label: `x = ${fmt(xq)}` }] },
    instruction: {
      en: `Final APPLICATION: predict the value between the data. $P(${fmt(xq)}) = 1 \\cdot \\ell_{0}(${fmt(xq)}) + 3 \\cdot \\ell_{1}(${fmt(xq)}) + 2 \\cdot \\ell_{2}(${fmt(xq)}) = 1 \\cdot ${fmt(lagBasis(0, xq))} + 3 \\cdot ${fmt(l1q)} + 2 \\cdot (${fmt(lagBasis(2, xq))})$. Compute it.`,
      fr: `APPLICATION finale : predisez la valeur entre les donnees. $P(${fmt(xq)}) = 1 \\cdot \\ell_{0}(${fmt(xq)}) + 3 \\cdot \\ell_{1}(${fmt(xq)}) + 2 \\cdot \\ell_{2}(${fmt(xq)}) = 1 \\cdot ${fmt(lagBasis(0, xq))} + 3 \\cdot ${fmt(l1q)} + 2 \\cdot (${fmt(lagBasis(2, xq))})$. Calculez.`,
    },
    input: {
      label: '$P(0.5) =$', expected: Pq, tol: Math.max(Math.abs(Pq) * 0.01, 0.01),
      ok: { en: `Correct: $P(${fmt(xq)}) = ${fmt(Pq)}$ — YOUR prediction, sitting on the green interpolant.`,
            fr: `Exact : $P(${fmt(xq)}) = ${fmt(Pq)}$ — VOTRE prediction, posee sur l'interpolant vert.` },
      hint: { en: `Weighted sum: $1 \\cdot ${fmt(lagBasis(0, xq))} + 3 \\cdot ${fmt(l1q)} + 2 \\cdot (${fmt(lagBasis(2, xq))})$.`,
              fr: `Somme ponderee : $1 \\cdot ${fmt(lagBasis(0, xq))} + 3 \\cdot ${fmt(l1q)} + 2 \\cdot (${fmt(lagBasis(2, xq))})$.` },
      reveal: { en: `$${fmt(1 * lagBasis(0, xq))} + ${fmt(3 * l1q)} ${fmt(2 * lagBasis(2, xq))} = ${fmt(Pq)}$. Type this value.`,
                fr: `$${fmt(1 * lagBasis(0, xq))} + ${fmt(3 * l1q)} ${fmt(2 * lagBasis(2, xq))} = ${fmt(Pq)}$. Tapez cette valeur.` },
      plotOnOk: {
        ...finalPlot,
        vlines: [{ x: xq, color: ORANGE, dash: '6 4' }],
        points: [...DATA_PTS, { x: xq, y: Pq, color: ORANGE, label: `P(0.5) = ${fmt(Pq)}` }],
      },
    },
  })

  return {
    title: { en: 'Build a Lagrange interpolant yourself', fr: 'Construisez un interpolant de Lagrange vous-meme' },
    steps,
    done: {
      intro: { en: 'You APPLIED the Lagrange concept: bases that are $1$ at their node and $0$ elsewhere, then a weighted sum. Your decisions:',
               fr: 'Vous avez APPLIQUE le concept de Lagrange : des bases valant $1$ a leur noeud et $0$ ailleurs, puis une somme ponderee. Vos decisions :' },
      eqTex: 'P(x) = \\sum_{j=0}^{2} y_{j}\\,\\ell_{j}(x)',
      table: {
        cols: [
          { en: 'decision', fr: 'decision' },
          { en: 'your answer', fr: 'votre reponse' },
          { en: 'concept used', fr: 'concept utilise' },
        ],
        rows: [
          ['degree for 3 points', '$2$', '$n+1$ points $\\Rightarrow$ degree $n$'],
          ['$\\ell_{1}(1)$', '$1$', '$\\ell_{j}(x_{j}) = 1$'],
          ['$\\ell_{1}(0)$', '$0$', '$\\ell_{j}(x_{k}) = 0,\\; k \\ne j$'],
          [`$\\ell_{1}(${fmt(xq)})$`, `$${fmt(l1q)}$`, 'basis between nodes'],
          [`$P(${fmt(xq)})$`, `$${fmt(Pq)}$`, 'weighted sum of bases'],
        ],
      },
      plot: {
        ...base,
        fns: [
          { fn: lagP, color: GREEN, width: 3.5 },
          { fn: (x: number) => lagBasis(0, x), color: TEAL, width: 1.5, dash: '4 4' },
          { fn: (x: number) => lagBasis(1, x), color: PURPLE, width: 1.5, dash: '4 4' },
          { fn: (x: number) => lagBasis(2, x), color: ORANGE, width: 1.5, dash: '4 4' },
        ],
        points: [...DATA_PTS, { x: xq, y: Pq, color: ORANGE, label: `P(0.5) = ${fmt(Pq)}` }],
      },
      outro: { en: 'Concept &#8594; application: the dashed curves are the three bases; the green curve is THEIR weighted sum, forced through every data point by the $1$-or-$0$ property. No linear system was solved — the structure did the work.',
               fr: 'Concept &#8594; application : les courbes pointillees sont les trois bases ; la courbe verte est LEUR somme ponderee, forcee de passer par chaque point grace a la propriete $1$-ou-$0$. Aucun systeme lineaire resolu — la structure a fait le travail.' },
    },
  }
}

// ==================================================================
// Differences divisees partagees (scripts 3 et 4)
// ==================================================================
const D01 = (YS[1] - YS[0]) / (XS[1] - XS[0])        // 2
const D12 = (YS[2] - YS[1]) / (XS[2] - XS[1])        // -1
const D012 = (D12 - D01) / (XS[2] - XS[0])           // -1.5
const newton2 = (x: number) => YS[0] + D01 * x + D012 * x * (x - 1)

// ==================================================================
// 3. Divided differences — build the table yourself
// ==================================================================
function buildDividedDifferences(): GScript {
  const steps: GStep[] = []
  const base: PlotSpec = { xMin: -0.6, xMax: 2.6, points: DATA_PTS, yMin: -1, yMax: 3.6 }

  // step 1: what the 1st column is for
  steps.push({
    plot: base,
    instruction: {
      en: 'Same fixed data: $(0, 1)$, $(1, 3)$, $(2, 2)$. Newton\'s CONCEPT: instead of bases, organize the data in a TABLE of divided differences. Each column has a geometric meaning.',
      fr: 'Memes donnees fixees : $(0, 1)$, $(1, 3)$, $(2, 2)$. Le CONCEPT de Newton : au lieu de bases, organiser les donnees dans un TABLEAU de differences divisees. Chaque colonne a un sens geometrique.',
    },
    choice: {
      prompt: { en: 'The first-order difference $f[x_{0}, x_{1}] = \\frac{f(x_{1}) - f(x_{0})}{x_{1} - x_{0}}$ measures what?',
                fr: 'La difference d\'ordre 1 $f[x_{0}, x_{1}] = \\frac{f(x_{1}) - f(x_{0})}{x_{1} - x_{0}}$ mesure quoi ?' },
      choices: [
        {
          label: { en: 'The SLOPE of the chord between the two points', fr: 'La PENTE de la corde entre les deux points' },
          correct: true,
          plot: {
            ...base,
            segs: [{ x1: 0, y1: 1, x2: 1, y2: 3, color: TEAL, width: 3 }],
          },
          feedback: { en: 'Yes: rise over run — a discrete derivative. The teal chord shows it.',
                      fr: 'Oui : variation verticale sur variation horizontale — une derivee discrete. La corde sarcelle la montre.' },
        },
        {
          label: { en: 'The area under the curve', fr: 'L\'aire sous la courbe' },
          correct: false,
          feedback: { en: 'No: that is integration. A difference quotient $\\frac{\\Delta y}{\\Delta x}$ approximates a DERIVATIVE.',
                      fr: 'Non : ca c\'est l\'integration. Un quotient de differences $\\frac{\\Delta y}{\\Delta x}$ approche une DERIVEE.' },
        },
        {
          label: { en: 'The midpoint of the two values', fr: 'Le milieu des deux valeurs' },
          correct: false,
          feedback: { en: 'No: a midpoint would be $\\frac{y_{0} + y_{1}}{2}$. Here we DIVIDE a difference of $y$ by a difference of $x$: a slope.',
                      fr: 'Non : un milieu serait $\\frac{y_{0} + y_{1}}{2}$. Ici on DIVISE une difference de $y$ par une difference de $x$ : une pente.' },
        },
      ],
    },
  })

  // step 2: input f[x0,x1]
  steps.push({
    plot: { ...base, segs: [{ x1: 0, y1: 1, x2: 1, y2: 3, color: TEAL, width: 3 }] },
    instruction: {
      en: 'APPLICATION: fill the first cell of YOUR table. Compute $f[x_{0}, x_{1}] = \\frac{3 - 1}{1 - 0}$.',
      fr: 'APPLICATION : remplissez la premiere case de VOTRE tableau. Calculez $f[x_{0}, x_{1}] = \\frac{3 - 1}{1 - 0}$.',
    },
    input: {
      label: '$f[x_0,x_1] =$', expected: D01, tol: 0.01,
      ok: { en: `Correct: $f[x_{0}, x_{1}] = ${fmt(D01)}$ — the teal chord rises with slope $${fmt(D01)}$.`,
            fr: `Exact : $f[x_{0}, x_{1}] = ${fmt(D01)}$ — la corde sarcelle monte avec une pente de $${fmt(D01)}$.` },
      hint: { en: 'Formula: $\\frac{f(x_{1}) - f(x_{0})}{x_{1} - x_{0}}$ with $f(x_{0}) = 1$, $f(x_{1}) = 3$.',
              fr: 'Formule : $\\frac{f(x_{1}) - f(x_{0})}{x_{1} - x_{0}}$ avec $f(x_{0}) = 1$, $f(x_{1}) = 3$.' },
      reveal: { en: `$\\frac{3 - 1}{1 - 0} = \\frac{2}{1} = ${fmt(D01)}$. Type this value.`,
                fr: `$\\frac{3 - 1}{1 - 0} = \\frac{2}{1} = ${fmt(D01)}$. Tapez cette valeur.` },
      plotOnOk: {
        ...base,
        segs: [{ x1: 0, y1: 1, x2: 1, y2: 3, color: TEAL, width: 3 }],
        fns: [{ fn: (x: number) => YS[0] + D01 * x, color: TEAL, width: 1.5, dash: '5 4' }],
      },
    },
  })

  // step 3: input f[x1,x2]
  steps.push({
    plot: {
      ...base,
      segs: [{ x1: 0, y1: 1, x2: 1, y2: 3, color: TEAL, width: 3 }],
      fns: [{ fn: (x: number) => YS[0] + D01 * x, color: TEAL, width: 1.5, dash: '5 4' }],
    },
    instruction: {
      en: 'The dashed teal line is the degree-1 interpolant of the first two points — but it MISSES $(2, 2)$. Next cell: the slope of the second chord, $f[x_{1}, x_{2}] = \\frac{2 - 3}{2 - 1}$.',
      fr: 'La droite sarcelle pointillee est l\'interpolant de degre 1 des deux premiers points — mais elle RATE $(2, 2)$. Case suivante : la pente de la seconde corde, $f[x_{1}, x_{2}] = \\frac{2 - 3}{2 - 1}$.',
    },
    input: {
      label: '$f[x_1,x_2] =$', expected: D12, tol: 0.01,
      ok: { en: `Correct: $f[x_{1}, x_{2}] = ${fmt(D12)}$ — the orange chord goes DOWN. Two different slopes: the data is curved.`,
            fr: `Exact : $f[x_{1}, x_{2}] = ${fmt(D12)}$ — la corde orange DESCEND. Deux pentes differentes : les donnees sont courbees.` },
      hint: { en: 'Same formula, next pair: $\\frac{f(x_{2}) - f(x_{1})}{x_{2} - x_{1}}$ with $f(x_{1}) = 3$, $f(x_{2}) = 2$. Mind the sign.',
              fr: 'Meme formule, paire suivante : $\\frac{f(x_{2}) - f(x_{1})}{x_{2} - x_{1}}$ avec $f(x_{1}) = 3$, $f(x_{2}) = 2$. Attention au signe.' },
      reveal: { en: `$\\frac{2 - 3}{2 - 1} = \\frac{-1}{1} = ${fmt(D12)}$. Type this value.`,
                fr: `$\\frac{2 - 3}{2 - 1} = \\frac{-1}{1} = ${fmt(D12)}$. Tapez cette valeur.` },
      plotOnOk: {
        ...base,
        segs: [
          { x1: 0, y1: 1, x2: 1, y2: 3, color: TEAL, width: 3 },
          { x1: 1, y1: 3, x2: 2, y2: 2, color: ORANGE, width: 3 },
        ],
      },
    },
  })

  // step 4: meaning of the 2nd column
  steps.push({
    plot: {
      ...base,
      segs: [
        { x1: 0, y1: 1, x2: 1, y2: 3, color: TEAL, width: 3 },
        { x1: 1, y1: 3, x2: 2, y2: 2, color: ORANGE, width: 3 },
      ],
    },
    instruction: {
      en: `Two chords, two slopes: $${fmt(D01)}$ then $${fmt(D12)}$. The second-order difference compares them: $f[x_{0}, x_{1}, x_{2}] = \\frac{f[x_{1}, x_{2}] - f[x_{0}, x_{1}]}{x_{2} - x_{0}}$.`,
      fr: `Deux cordes, deux pentes : $${fmt(D01)}$ puis $${fmt(D12)}$. La difference d'ordre 2 les compare : $f[x_{0}, x_{1}, x_{2}] = \\frac{f[x_{1}, x_{2}] - f[x_{0}, x_{1}]}{x_{2} - x_{0}}$.`,
    },
    choice: {
      prompt: { en: 'Geometrically, what does this second column capture?',
                fr: 'Geometriquement, que capture cette deuxieme colonne ?' },
      choices: [
        {
          label: { en: 'The CURVATURE: how fast the slope changes', fr: 'La COURBURE : la vitesse de variation de la pente' },
          correct: true,
          feedback: { en: 'Yes: change of slope per unit of $x$ — a discrete second derivative. It will be the coefficient of the quadratic term.',
                      fr: 'Oui : variation de pente par unite de $x$ — une derivee seconde discrete. Ce sera le coefficient du terme quadratique.' },
        },
        {
          label: { en: 'The average of the $y$ values', fr: 'La moyenne des valeurs $y$' },
          correct: false,
          feedback: { en: 'No: it involves slopes, not raw values. Slope of slopes $\\approx$ curvature.',
                      fr: 'Non : elle implique des pentes, pas des valeurs brutes. Pente des pentes $\\approx$ courbure.' },
        },
      ],
    },
  })

  // step 5: input f[x0,x1,x2]
  steps.push({
    plot: {
      ...base,
      segs: [
        { x1: 0, y1: 1, x2: 1, y2: 3, color: TEAL, width: 3 },
        { x1: 1, y1: 3, x2: 2, y2: 2, color: ORANGE, width: 3 },
      ],
    },
    instruction: {
      en: `Last cell of YOUR table: $f[x_{0}, x_{1}, x_{2}] = \\frac{${fmt(D12)} - ${fmt(D01)}}{2 - 0}$.`,
      fr: `Derniere case de VOTRE tableau : $f[x_{0}, x_{1}, x_{2}] = \\frac{${fmt(D12)} - ${fmt(D01)}}{2 - 0}$.`,
    },
    input: {
      label: '$f[x_0,x_1,x_2] =$', expected: D012, tol: 0.01,
      ok: { en: `Correct: $f[x_{0}, x_{1}, x_{2}] = ${fmt(D012)}$. Negative curvature — and indeed the green parabola through the three points bends DOWN.`,
            fr: `Exact : $f[x_{0}, x_{1}, x_{2}] = ${fmt(D012)}$. Courbure negative — et en effet la parabole verte passant par les trois points se courbe vers le BAS.` },
      hint: { en: `Numerator: $${fmt(D12)} - ${fmt(D01)}$. Denominator: the OUTERMOST nodes, $x_{2} - x_{0} = 2$.`,
              fr: `Numerateur : $${fmt(D12)} - ${fmt(D01)}$. Denominateur : les noeuds EXTREMES, $x_{2} - x_{0} = 2$.` },
      reveal: { en: `$\\frac{${fmt(D12)} - ${fmt(D01)}}{2} = \\frac{${fmt(D12 - D01)}}{2} = ${fmt(D012)}$. Type this value.`,
                fr: `$\\frac{${fmt(D12)} - ${fmt(D01)}}{2} = \\frac{${fmt(D12 - D01)}}{2} = ${fmt(D012)}$. Tapez cette valeur.` },
      plotOnOk: {
        ...base,
        fns: [{ fn: newton2, color: GREEN, width: 3.5 }],
        segs: [
          { x1: 0, y1: 1, x2: 1, y2: 3, color: TEAL, width: 2, dash: '5 4' },
          { x1: 1, y1: 3, x2: 2, y2: 2, color: ORANGE, width: 2, dash: '5 4' },
        ],
      },
    },
  })

  // step 6: the diagonal = coefficients
  steps.push({
    plot: { ...base, fns: [{ fn: newton2, color: GREEN, width: 3.5 }] },
    instruction: {
      en: `Your table is complete. Newton\'s form reads the TOP DIAGONAL as coefficients: $P(x) = ${fmt(YS[0])} + ${fmt(D01)}\\,x + (${fmt(D012)})\\,x(x - 1)$ — the green curve.`,
      fr: `Votre tableau est complet. La forme de Newton lit la DIAGONALE superieure comme coefficients : $P(x) = ${fmt(YS[0])} + ${fmt(D01)}\\,x + (${fmt(D012)})\\,x(x - 1)$ — la courbe verte.`,
    },
    choice: {
      prompt: { en: 'Why does the term $x(x-1)$ not break the fit at $x_{0} = 0$ and $x_{1} = 1$?',
                fr: 'Pourquoi le terme $x(x-1)$ ne casse-t-il pas l\'ajustement en $x_{0} = 0$ et $x_{1} = 1$ ?' },
      choices: [
        {
          label: { en: 'It VANISHES at both nodes, so it only adjusts $x_{2}$', fr: 'Il S\'ANNULE aux deux noeuds, donc il n\'ajuste que $x_{2}$' },
          correct: true,
          feedback: { en: 'Exactly: $x(x-1) = 0$ at $x = 0$ and $x = 1$. Each new Newton term corrects the NEXT node without disturbing the previous ones. This is the key for the next script.',
                      fr: 'Exactement : $x(x-1) = 0$ en $x = 0$ et $x = 1$. Chaque nouveau terme de Newton corrige le noeud SUIVANT sans deranger les precedents. C\'est la cle du script suivant.' },
        },
        {
          label: { en: 'Because its coefficient is small', fr: 'Parce que son coefficient est petit' },
          correct: false,
          feedback: { en: 'No: the size of the coefficient is irrelevant. The factor $x(x-1)$ is built to be ZERO at the earlier nodes.',
                      fr: 'Non : la taille du coefficient n\'a aucune importance. Le facteur $x(x-1)$ est construit pour etre NUL aux noeuds precedents.' },
        },
      ],
    },
  })

  return {
    title: { en: 'Fill the divided-difference table yourself', fr: 'Remplissez le tableau des differences divisees vous-meme' },
    steps,
    done: {
      intro: { en: 'You APPLIED the concept: each column of the table is a discrete derivative of the previous one. Here is YOUR table:',
               fr: 'Vous avez APPLIQUE le concept : chaque colonne du tableau est une derivee discrete de la precedente. Voici VOTRE tableau :' },
      eqTex: `P(x) = ${fmt(YS[0])} + ${fmt(D01)}x ${fmt(D012)}\\,x(x-1)`,
      table: {
        cols: [
          { en: '$x_{i}$', fr: '$x_{i}$' },
          { en: '$f(x_{i})$', fr: '$f(x_{i})$' },
          { en: 'order 1 (slope)', fr: 'ordre 1 (pente)' },
          { en: 'order 2 (curvature)', fr: 'ordre 2 (courbure)' },
        ],
        rows: [
          [`$${fmt(XS[0])}$`, `$${fmt(YS[0])}$`, '', ''],
          ['', '', `$${fmt(D01)}$`, ''],
          [`$${fmt(XS[1])}$`, `$${fmt(YS[1])}$`, '', `$${fmt(D012)}$`],
          ['', '', `$${fmt(D12)}$`, ''],
          [`$${fmt(XS[2])}$`, `$${fmt(YS[2])}$`, '', ''],
        ],
      },
      plot: {
        xMin: -0.6, xMax: 2.6, yMin: -1, yMax: 3.6,
        fns: [{ fn: newton2, color: GREEN, width: 3.5 }],
        points: DATA_PTS,
        segs: [
          { x1: 0, y1: 1, x2: 1, y2: 3, color: TEAL, width: 2, dash: '5 4' },
          { x1: 1, y1: 3, x2: 2, y2: 2, color: ORANGE, width: 2, dash: '5 4' },
        ],
      },
      outro: { en: 'Concept &#8594; application: slopes ($2$ and $-1$), then curvature ($-1.5$) — the diagonal of YOUR table IS the polynomial. Same green parabola as Lagrange would give: the interpolant is unique, only the construction differs.',
               fr: 'Concept &#8594; application : des pentes ($2$ et $-1$), puis une courbure ($-1.5$) — la diagonale de VOTRE tableau EST le polynome. Meme parabole verte que donnerait Lagrange : l\'interpolant est unique, seule la construction change.' },
    },
  }
}

// ==================================================================
// 4. Newton form — add a point without recomputing everything
// ==================================================================
function buildNewtonInterpolation(): GScript {
  const x3 = 3, y3 = 4
  const D23 = (y3 - YS[2]) / (x3 - XS[2])            // 2
  const D123 = (D23 - D12) / (x3 - XS[1])            // 1.5
  const D0123 = (D123 - D012) / (x3 - XS[0])         // 1
  const newton3 = (x: number) => newton2(x) + D0123 * x * (x - 1) * (x - 2)
  const PTS4 = [...DATA_PTS, { x: x3, y: y3, color: PURPLE, label: `(${fmt(x3)}, ${fmt(y3)}) new` }]
  const base: PlotSpec = {
    xMin: -0.6, xMax: 3.6, yMin: -3, yMax: 5,
    fns: [{ fn: newton2, color: GREEN, width: 3 }],
    points: PTS4,
  }
  const steps: GStep[] = []

  // step 1: the problem
  steps.push({
    plot: base,
    instruction: {
      en: `From the previous table we have $P_{2}(x) = 1 + 2x - 1.5\\,x(x - 1)$ through $(0,1)$, $(1,3)$, $(2,2)$ (green). The lab now measures a NEW point $(3, 4)$ (purple) — and $P_{2}(3) = ${fmt(newton2(3))}$, far off.`,
      fr: `Du tableau precedent on a $P_{2}(x) = 1 + 2x - 1.5\\,x(x - 1)$ passant par $(0,1)$, $(1,3)$, $(2,2)$ (vert). Le labo mesure un NOUVEAU point $(3, 4)$ (violet) — or $P_{2}(3) = ${fmt(newton2(3))}$, tres loin.`,
    },
    choice: {
      prompt: { en: 'With Newton\'s form, what must we do to include the new point?',
                fr: 'Avec la forme de Newton, que faut-il faire pour inclure le nouveau point ?' },
      choices: [
        {
          label: { en: 'ADD one term $c\\,x(x-1)(x-2)$ — keep $P_{2}$ as is', fr: 'AJOUTER un terme $c\\,x(x-1)(x-2)$ — garder $P_{2}$ tel quel' },
          correct: true,
          feedback: { en: 'Yes! The new factor vanishes at $0$, $1$, $2$, so the old fit is untouched. One coefficient to compute, not four.',
                      fr: 'Oui ! Le nouveau facteur s\'annule en $0$, $1$, $2$, donc l\'ancien ajustement est intact. Un seul coefficient a calculer, pas quatre.' },
        },
        {
          label: { en: 'Recompute everything from scratch with 4 points', fr: 'Tout recalculer de zero avec 4 points' },
          correct: false,
          feedback: { en: 'That works but wastes the previous effort. Newton\'s WHOLE POINT: $x(x-1)(x-2) = 0$ at the old nodes, so we just append one term.',
                      fr: 'Ca marche mais gaspille l\'effort precedent. TOUT L\'INTERET de Newton : $x(x-1)(x-2) = 0$ aux anciens noeuds, on ajoute donc juste un terme.' },
        },
      ],
    },
  })

  // step 2: input f[x2,x3]
  steps.push({
    plot: base,
    instruction: {
      en: `Extend YOUR table by one diagonal. First the new chord slope: $f[x_{2}, x_{3}] = \\frac{${fmt(y3)} - ${fmt(YS[2])}}{${fmt(x3)} - ${fmt(XS[2])}}$.`,
      fr: `Prolongez VOTRE tableau d'une diagonale. D'abord la pente de la nouvelle corde : $f[x_{2}, x_{3}] = \\frac{${fmt(y3)} - ${fmt(YS[2])}}{${fmt(x3)} - ${fmt(XS[2])}}$.`,
    },
    input: {
      label: '$f[x_2,x_3] =$', expected: D23, tol: 0.01,
      ok: { en: `Correct: $f[x_{2}, x_{3}] = ${fmt(D23)}$ — the new orange chord climbs toward the purple point.`,
            fr: `Exact : $f[x_{2}, x_{3}] = ${fmt(D23)}$ — la nouvelle corde orange grimpe vers le point violet.` },
      hint: { en: 'Slope of the chord between $(2, 2)$ and $(3, 4)$: $\\frac{\\Delta y}{\\Delta x}$.',
              fr: 'Pente de la corde entre $(2, 2)$ et $(3, 4)$ : $\\frac{\\Delta y}{\\Delta x}$.' },
      reveal: { en: `$\\frac{4 - 2}{3 - 2} = ${fmt(D23)}$. Type this value.`,
                fr: `$\\frac{4 - 2}{3 - 2} = ${fmt(D23)}$. Tapez cette valeur.` },
      plotOnOk: {
        ...base,
        segs: [{ x1: 2, y1: 2, x2: 3, y2: 4, color: ORANGE, width: 3 }],
      },
    },
  })

  // step 3: input f[x1,x2,x3]
  steps.push({
    plot: { ...base, segs: [{ x1: 2, y1: 2, x2: 3, y2: 4, color: ORANGE, width: 3 }] },
    instruction: {
      en: `Next cell of the diagonal: $f[x_{1}, x_{2}, x_{3}] = \\frac{f[x_{2}, x_{3}] - f[x_{1}, x_{2}]}{x_{3} - x_{1}} = \\frac{${fmt(D23)} - (${fmt(D12)})}{${fmt(x3)} - ${fmt(XS[1])}}$.`,
      fr: `Case suivante de la diagonale : $f[x_{1}, x_{2}, x_{3}] = \\frac{f[x_{2}, x_{3}] - f[x_{1}, x_{2}]}{x_{3} - x_{1}} = \\frac{${fmt(D23)} - (${fmt(D12)})}{${fmt(x3)} - ${fmt(XS[1])}}$.`,
    },
    input: {
      label: '$f[x_1,x_2,x_3] =$', expected: D123, tol: 0.01,
      ok: { en: `Correct: $f[x_{1}, x_{2}, x_{3}] = ${fmt(D123)}$. The curvature on the right side is positive — the data bends UP there.`,
            fr: `Exact : $f[x_{1}, x_{2}, x_{3}] = ${fmt(D123)}$. La courbure du cote droit est positive — les donnees remontent la-bas.` },
      hint: { en: `Difference of the two latest slopes, divided by the span $x_{3} - x_{1} = 2$. Careful: subtracting $${fmt(D12)}$ means ADDING $${fmt(-D12)}$.`,
              fr: `Difference des deux dernieres pentes, divisee par l'ecart $x_{3} - x_{1} = 2$. Attention : soustraire $${fmt(D12)}$ revient a AJOUTER $${fmt(-D12)}$.` },
      reveal: { en: `$\\frac{${fmt(D23)} - (${fmt(D12)})}{2} = \\frac{${fmt(D23 - D12)}}{2} = ${fmt(D123)}$. Type this value.`,
                fr: `$\\frac{${fmt(D23)} - (${fmt(D12)})}{2} = \\frac{${fmt(D23 - D12)}}{2} = ${fmt(D123)}$. Tapez cette valeur.` },
    },
  })

  // step 4: input f[x0,x1,x2,x3] — THE new coefficient
  steps.push({
    plot: { ...base, segs: [{ x1: 2, y1: 2, x2: 3, y2: 4, color: ORANGE, width: 3 }] },
    instruction: {
      en: `Final cell — the ONLY new coefficient: $f[x_{0}, x_{1}, x_{2}, x_{3}] = \\frac{f[x_{1}, x_{2}, x_{3}] - f[x_{0}, x_{1}, x_{2}]}{x_{3} - x_{0}} = \\frac{${fmt(D123)} - (${fmt(D012)})}{${fmt(x3)} - ${fmt(XS[0])}}$.`,
      fr: `Derniere case — le SEUL nouveau coefficient : $f[x_{0}, x_{1}, x_{2}, x_{3}] = \\frac{f[x_{1}, x_{2}, x_{3}] - f[x_{0}, x_{1}, x_{2}]}{x_{3} - x_{0}} = \\frac{${fmt(D123)} - (${fmt(D012)})}{${fmt(x3)} - ${fmt(XS[0])}}$.`,
    },
    input: {
      label: '$f[x_0,\\dots,x_3] =$', expected: D0123, tol: 0.01,
      ok: { en: `Correct: the new coefficient is $${fmt(D0123)}$. Watch the curve DEFORM: $P_{3}$ (purple) bends away from $P_{2}$ (green, dashed) and catches the new point — without losing the first three.`,
            fr: `Exact : le nouveau coefficient vaut $${fmt(D0123)}$. Regardez la courbe se DEFORMER : $P_{3}$ (violet) s'ecarte de $P_{2}$ (vert, pointille) et attrape le nouveau point — sans perdre les trois premiers.` },
      hint: { en: `Same recipe one level up: $\\frac{${fmt(D123)} - (${fmt(D012)})}{3}$.`,
              fr: `Meme recette un cran au-dessus : $\\frac{${fmt(D123)} - (${fmt(D012)})}{3}$.` },
      reveal: { en: `$\\frac{${fmt(D123)} + ${fmt(-D012)}}{3} = \\frac{${fmt(D123 - D012)}}{3} = ${fmt(D0123)}$. Type this value.`,
                fr: `$\\frac{${fmt(D123)} + ${fmt(-D012)}}{3} = \\frac{${fmt(D123 - D012)}}{3} = ${fmt(D0123)}$. Tapez cette valeur.` },
      plotOnOk: {
        xMin: -0.6, xMax: 3.6, yMin: -3, yMax: 5,
        fns: [
          { fn: newton3, color: PURPLE, width: 3.5 },
          { fn: newton2, color: GREEN, width: 2, dash: '6 4' },
        ],
        points: PTS4,
      },
    },
  })

  // step 5: verify that the old nodes are intact
  steps.push({
    plot: {
      xMin: -0.6, xMax: 3.6, yMin: -3, yMax: 5,
      fns: [
        { fn: newton3, color: PURPLE, width: 3.5 },
        { fn: newton2, color: GREEN, width: 2, dash: '6 4' },
      ],
      points: PTS4,
    },
    instruction: {
      en: `$P_{3}(x) = P_{2}(x) + ${fmt(D0123)}\\,x(x - 1)(x - 2)$. The two curves split between the nodes, yet both pass through $(0,1)$, $(1,3)$, $(2,2)$.`,
      fr: `$P_{3}(x) = P_{2}(x) + ${fmt(D0123)}\\,x(x - 1)(x - 2)$. Les deux courbes se separent entre les noeuds, mais toutes deux passent par $(0,1)$, $(1,3)$, $(2,2)$.`,
    },
    choice: {
      prompt: { en: 'What is the value of the correction term $x(x-1)(x-2)$ at the OLD nodes $x = 0, 1, 2$?',
                fr: 'Que vaut le terme correctif $x(x-1)(x-2)$ aux ANCIENS noeuds $x = 0, 1, 2$ ?' },
      choices: [
        {
          label: { en: '$0$ at all three', fr: '$0$ aux trois' },
          correct: true,
          feedback: { en: `Exactly: one factor vanishes at each old node, so $P_{3} = P_{2}$ there. And at the new node, $P_{3}(3) = ${fmt(newton3(3))} = y_{3}$. That is the whole concept.`,
                      fr: `Exactement : un facteur s'annule a chaque ancien noeud, donc $P_{3} = P_{2}$ la. Et au nouveau noeud, $P_{3}(3) = ${fmt(newton3(3))} = y_{3}$. C'est tout le concept.` },
        },
        {
          label: { en: 'Small but nonzero', fr: 'Petit mais non nul' },
          correct: false,
          feedback: { en: 'No: compute it. At $x = 1$: $1 \\cdot 0 \\cdot (-1) = 0$. Exactly zero, by construction.',
                      fr: 'Non : calculez-le. En $x = 1$ : $1 \\cdot 0 \\cdot (-1) = 0$. Exactement zero, par construction.' },
        },
      ],
    },
  })

  // step 6: cost of recomputation
  steps.push({
    plot: {
      xMin: -0.6, xMax: 3.6, yMin: -3, yMax: 5,
      fns: [{ fn: newton3, color: PURPLE, width: 3.5 }],
      points: PTS4,
    },
    instruction: {
      en: 'Last conceptual decision: compare the two strategies when a point arrives.',
      fr: 'Derniere decision conceptuelle : comparez les deux strategies quand un point arrive.',
    },
    choice: {
      prompt: { en: 'With Lagrange, adding the point $(3, 4)$ would require...',
                fr: 'Avec Lagrange, ajouter le point $(3, 4)$ exigerait...' },
      choices: [
        {
          label: { en: 'Rebuilding ALL the bases $\\ell_{j}$ (each denominator changes)', fr: 'Reconstruire TOUTES les bases $\\ell_{j}$ (chaque denominateur change)' },
          correct: true,
          feedback: { en: 'Yes: every $\\ell_{j}$ gains a factor, so everything is recomputed. Newton: one diagonal, one term. That is why Newton\'s form is preferred for growing data.',
                      fr: 'Oui : chaque $\\ell_{j}$ gagne un facteur, donc tout est recalcule. Newton : une diagonale, un terme. Voila pourquoi la forme de Newton est preferee quand les donnees grandissent.' },
        },
        {
          label: { en: 'Just adding $y_{3}\\ell_{3}$ and keeping the old bases', fr: 'Juste ajouter $y_{3}\\ell_{3}$ en gardant les anciennes bases' },
          correct: false,
          feedback: { en: 'Tempting but wrong: the OLD bases $\\ell_{0}, \\ell_{1}, \\ell_{2}$ must also gain a factor $\\frac{x - x_{3}}{x_{j} - x_{3}}$ to vanish at the new node. Everything changes.',
                      fr: 'Tentant mais faux : les ANCIENNES bases $\\ell_{0}, \\ell_{1}, \\ell_{2}$ doivent aussi gagner un facteur $\\frac{x - x_{3}}{x_{j} - x_{3}}$ pour s\'annuler au nouveau noeud. Tout change.' },
        },
      ],
    },
  })

  return {
    title: { en: 'Extend a Newton interpolant yourself', fr: 'Prolongez un interpolant de Newton vous-meme' },
    steps,
    done: {
      intro: { en: 'You APPLIED Newton\'s key idea: a new point costs ONE new diagonal of the table and ONE new term. Your additions:',
               fr: 'Vous avez APPLIQUE l\'idee cle de Newton : un nouveau point coute UNE nouvelle diagonale du tableau et UN nouveau terme. Vos ajouts :' },
      eqTex: `P_{3}(x) = P_{2}(x) + ${fmt(D0123)}\\,x(x-1)(x-2)`,
      table: {
        cols: [
          { en: 'new cell', fr: 'nouvelle case' },
          { en: 'your value', fr: 'votre valeur' },
          { en: 'meaning', fr: 'sens' },
        ],
        rows: [
          ['$f[x_{2}, x_{3}]$', `$${fmt(D23)}$`, 'slope of the new chord'],
          ['$f[x_{1}, x_{2}, x_{3}]$', `$${fmt(D123)}$`, 'curvature on the right'],
          ['$f[x_{0}, x_{1}, x_{2}, x_{3}]$', `$${fmt(D0123)}$`, 'coefficient of $x(x-1)(x-2)$'],
        ],
      },
      plot: {
        xMin: -0.6, xMax: 3.6, yMin: -3, yMax: 5,
        fns: [
          { fn: newton3, color: PURPLE, width: 3.5 },
          { fn: newton2, color: GREEN, width: 2, dash: '6 4' },
        ],
        points: PTS4,
      },
      outro: { en: `Concept &#8594; application: the factor $x(x-1)(x-2)$ vanishes at the old nodes, so $P_{2}$ (dashed) and $P_{3}$ (purple) agree there and split elsewhere; the new term steers the curve onto $(3, 4)$. Check: $P_{3}(3) = ${fmt(newton3(3))}$.`,
               fr: `Concept &#8594; application : le facteur $x(x-1)(x-2)$ s'annule aux anciens noeuds, donc $P_{2}$ (pointille) et $P_{3}$ (violet) coincident la et se separent ailleurs ; le nouveau terme guide la courbe sur $(3, 4)$. Verification : $P_{3}(3) = ${fmt(newton3(3))}$.` },
    },
  }
}

// ==================================================================
// 5. Cubic splines — joined pieces vs global polynomial
// ==================================================================
function buildSpline(): GScript {
  const SX = [0, 1, 2, 3]
  const SY = [0, 1, 0, 1]
  const SPTS = SX.map((x, i) => ({ x, y: SY[i], color: BLUE, label: `(${fmt(x)}, ${fmt(SY[i])})` }))

  // global polynomial of degree 3 by divided differences (4 points)
  const g01 = (SY[1] - SY[0]) / (SX[1] - SX[0])
  const g12 = (SY[2] - SY[1]) / (SX[2] - SX[1])
  const g23 = (SY[3] - SY[2]) / (SX[3] - SX[2])
  const g012 = (g12 - g01) / (SX[2] - SX[0])
  const g123 = (g23 - g12) / (SX[3] - SX[1])
  const g0123 = (g123 - g012) / (SX[3] - SX[0])
  const globalP = (x: number) =>
    SY[0] + g01 * x + g012 * x * (x - 1) + g0123 * x * (x - 1) * (x - 2)

  // natural cubic spline, step h = 1:
  // M0 = M3 = 0 ; systeme 2x2 : 4 M1 + M2 = b1 ; M1 + 4 M2 = b2
  const b1 = 6 * (SY[0] - 2 * SY[1] + SY[2])
  const b2 = 6 * (SY[1] - 2 * SY[2] + SY[3])
  const det = 4 * 4 - 1 * 1
  const M1 = (4 * b1 - b2) / det
  const M2 = (4 * b2 - b1) / det
  const M = [0, M1, M2, 0]
  const splinePiece = (i: number, x: number): number => {
    const xi = SX[i], xi1 = SX[i + 1], h = 1
    return (M[i] * (xi1 - x) ** 3 + M[i + 1] * (x - xi) ** 3) / (6 * h)
      + (SY[i] - M[i] * h * h / 6) * (xi1 - x) / h
      + (SY[i + 1] - M[i + 1] * h * h / 6) * (x - xi) / h
  }
  const spline = (x: number): number => {
    const i = Math.max(0, Math.min(2, Math.floor(x)))
    return splinePiece(i, x)
  }
  // piece i extended (to show that a single piece diverges outside its interval)
  const pieceFn = (i: number) => (x: number) => splinePiece(i, x)

  // overshoot of the global polynomial
  let gMax = -Infinity, gMaxX = 0
  for (let i = 0; i <= 300; i++) {
    const x = 3 * i / 300
    const v = globalP(x)
    if (v > gMax) { gMax = v; gMaxX = x }
  }

  const base: PlotSpec = { xMin: -0.3, xMax: 3.3, points: SPTS, yMin: -0.6, yMax: 1.6 }
  const steps: GStep[] = []

  // step 1: the global polynomial and its overshoot
  steps.push({
    plot: { ...base, fns: [{ fn: globalP, color: ORANGE, width: 3 }] },
    instruction: {
      en: 'New fixed data, a zigzag: $(0,0)$, $(1,1)$, $(2,0)$, $(3,1)$. The orange curve is the SINGLE global polynomial of degree $3$ through all four points.',
      fr: 'Nouvelles donnees fixees, en zigzag : $(0,0)$, $(1,1)$, $(2,0)$, $(3,1)$. La courbe orange est l\'UNIQUE polynome global de degre $3$ passant par les quatre points.',
    },
    choice: {
      prompt: { en: 'The data lives in $[0, 1]$. Does the orange curve stay inside that band?',
                fr: 'Les donnees vivent dans $[0, 1]$. La courbe orange reste-t-elle dans cette bande ?' },
      choices: [
        {
          label: { en: 'No — it OVERSHOOTS above 1 and below 0', fr: 'Non — elle DEPASSE au-dessus de 1 et en dessous de 0' },
          correct: true,
          plot: {
            ...base,
            fns: [{ fn: globalP, color: ORANGE, width: 3 }],
            points: [...SPTS, { x: gMaxX, y: gMax, color: ORANGE, label: `max = ${fmt(gMax, 2)}` }],
            segs: [
              { x1: -0.3, y1: 1, x2: 3.3, y2: 1, color: '#94A3B8', dash: '4 4', width: 1.5 },
              { x1: -0.3, y1: 0, x2: 3.3, y2: 0, color: '#94A3B8', dash: '4 4', width: 1.5 },
            ],
          },
          feedback: { en: `Right: it peaks at $${fmt(gMax, 3)} > 1$ and dips below $0$. With more zigzag points the overshoot EXPLODES (Runge phenomenon). One rigid polynomial cannot follow wiggly data calmly.`,
                      fr: `Exact : elle culmine a $${fmt(gMax, 3)} > 1$ et plonge sous $0$. Avec plus de points en zigzag, le depassement EXPLOSE (phenomene de Runge). Un polynome rigide ne peut pas suivre calmement des donnees ondulantes.` },
        },
        {
          label: { en: 'Yes — interpolation never leaves the data range', fr: 'Oui — l\'interpolation ne sort jamais de la plage des donnees' },
          correct: false,
          feedback: { en: 'Look closely between the nodes: the curve climbs above the dashed line $y = 1$. Interpolation pins the NODES only, between them anything can happen.',
                      fr: 'Regardez bien entre les noeuds : la courbe monte au-dessus de la ligne $y = 1$. L\'interpolation fixe les NOEUDS seulement, entre eux tout peut arriver.' },
        },
      ],
    },
  })

  // step 2: the idea of the spline
  steps.push({
    plot: {
      ...base,
      fns: [{ fn: globalP, color: ORANGE, width: 2, dash: '5 4' }],
      vlines: SX.slice(1, 3).map(x => ({ x, color: TEAL, dash: '4 4', label: `x = ${fmt(x)}` })),
    },
    instruction: {
      en: 'The spline CONCEPT: instead of one rigid polynomial, use a LOW-degree (cubic) piece on each subinterval $[0,1]$, $[1,2]$, $[2,3]$, and glue them at the knots (teal lines).',
      fr: 'Le CONCEPT de la spline : au lieu d\'un polynome rigide, utiliser un morceau de BAS degre (cubique) sur chaque sous-intervalle $[0,1]$, $[1,2]$, $[2,3]$, et les coller aux noeuds (lignes sarcelle).',
    },
    choice: {
      prompt: { en: 'Three cubic pieces have $3 \\times 4 = 12$ unknown coefficients. Interpolating the 4 points gives only 6 conditions (each piece hits its 2 ends). Where do the missing conditions come from?',
                fr: 'Trois morceaux cubiques ont $3 \\times 4 = 12$ coefficients inconnus. Interpoler les 4 points ne donne que 6 conditions (chaque morceau touche ses 2 bouts). D\'ou viennent les conditions manquantes ?' },
      choices: [
        {
          label: { en: 'SMOOTHNESS at the knots: $S\'$ and $S\'\'$ must also match', fr: 'La REGULARITE aux noeuds : $S\'$ et $S\'\'$ doivent aussi coincider' },
          correct: true,
          feedback: { en: 'Yes: at each interior knot we demand continuity of the value, the slope $S\'$ AND the curvature $S\'\'$ — that is what makes the junction invisible to the eye.',
                      fr: 'Oui : a chaque noeud interieur on exige la continuite de la valeur, de la pente $S\'$ ET de la courbure $S\'\'$ — c\'est ce qui rend le raccord invisible a l\'oeil.' },
        },
        {
          label: { en: 'We pick the coefficients randomly', fr: 'On choisit les coefficients au hasard' },
          correct: false,
          feedback: { en: 'No: the conditions are mathematical constraints — smoothness of $S\'$ and $S\'\'$ at the interior knots, plus two boundary conditions.',
                      fr: 'Non : les conditions sont des contraintes mathematiques — regularite de $S\'$ et $S\'\'$ aux noeuds interieurs, plus deux conditions aux bords.' },
        },
        {
          label: { en: 'We add more data points', fr: 'On ajoute plus de points de donnees' },
          correct: false,
          feedback: { en: 'No: the data is fixed by the course. The extra equations come from gluing the PIECES smoothly, not from new measurements.',
                      fr: 'Non : les donnees sont fixees par le cours. Les equations supplementaires viennent du collage LISSE des morceaux, pas de nouvelles mesures.' },
        },
      ],
    },
  })

  // step 3: count the joining conditions
  const nCond = 6 + 2 * 2 + 2  // 12
  steps.push({
    plot: {
      ...base,
      vlines: SX.slice(1, 3).map(x => ({ x, color: TEAL, dash: '4 4' })),
    },
    instruction: {
      en: 'Count with me: 6 interpolation conditions, plus at EACH of the 2 interior knots, continuity of $S\'$ and of $S\'\'$ (that is $2 \\times 2 = 4$), plus 2 boundary conditions ($S\'\'(0) = S\'\'(3) = 0$ for the natural spline).',
      fr: 'Comptons ensemble : 6 conditions d\'interpolation, plus a CHACUN des 2 noeuds interieurs, continuite de $S\'$ et de $S\'\'$ (soit $2 \\times 2 = 4$), plus 2 conditions aux bords ($S\'\'(0) = S\'\'(3) = 0$ pour la spline naturelle).',
    },
    input: {
      label: 'total =', expected: nCond, tol: 0.01,
      ok: { en: `Correct: $6 + 4 + 2 = ${fmt(nCond)}$ conditions for $12$ coefficients — the system is square, the natural cubic spline exists and is unique.`,
            fr: `Exact : $6 + 4 + 2 = ${fmt(nCond)}$ conditions pour $12$ coefficients — le systeme est carre, la spline cubique naturelle existe et est unique.` },
      hint: { en: 'Add the three groups: $6$ (interpolation) $+ 4$ (smoothness) $+ 2$ (boundary).',
              fr: 'Additionnez les trois groupes : $6$ (interpolation) $+ 4$ (regularite) $+ 2$ (bords).' },
      reveal: { en: `$6 + 4 + 2 = ${fmt(nCond)}$. Type this value.`,
                fr: `$6 + 4 + 2 = ${fmt(nCond)}$. Tapez cette valeur.` },
    },
  })

  // step 4: first piece, extended — it diverges outside [0,1]
  steps.push({
    plot: {
      ...base,
      fns: [{ fn: pieceFn(0), color: TEAL, width: 3 }],
      interval: [0, 1],
    },
    instruction: {
      en: 'Solving the system gives the curvatures at the knots: $S\'\'(1) = M_{1} = ' + fmt(M1) + '$, $S\'\'(2) = M_{2} = ' + fmt(M2) + '$. The teal curve is the FIRST cubic piece, drawn beyond its home interval $[0, 1]$ (shaded).',
      fr: 'Resoudre le systeme donne les courbures aux noeuds : $S\'\'(1) = M_{1} = ' + fmt(M1) + '$, $S\'\'(2) = M_{2} = ' + fmt(M2) + '$. La courbe sarcelle est le PREMIER morceau cubique, trace au-dela de son intervalle $[0, 1]$ (zone grisee).',
    },
    choice: {
      prompt: { en: 'Outside $[0, 1]$, should we keep following this piece?',
                fr: 'Hors de $[0, 1]$, doit-on continuer a suivre ce morceau ?' },
      choices: [
        {
          label: { en: 'No — switch to the NEXT piece at the knot $x = 1$', fr: 'Non — basculer sur le morceau SUIVANT au noeud $x = 1$' },
          correct: true,
          plot: {
            ...base,
            interval: [1, 2],
            fns: [
              { fn: pieceFn(0), color: TEAL, width: 2, dash: '5 4' },
              { fn: pieceFn(1), color: PURPLE, width: 3 },
            ],
          },
          feedback: { en: 'Yes: each piece is only valid on its own subinterval. The purple piece takes over on $[1, 2]$ — and at $x = 1$ they share the same value, slope and curvature, so the hand-off is seamless.',
                      fr: 'Oui : chaque morceau n\'est valable que sur son sous-intervalle. Le morceau violet prend le relais sur $[1, 2]$ — et en $x = 1$ ils partagent valeur, pente et courbure : le passage de temoin est invisible.' },
        },
        {
          label: { en: 'Yes — one cubic is enough everywhere', fr: 'Oui — une seule cubique suffit partout' },
          correct: false,
          plot: {
            xMin: -0.3, xMax: 3.3, yMin: -3, yMax: 2,
            points: SPTS,
            fns: [{ fn: pieceFn(0), color: TEAL, width: 3 }],
            interval: [0, 1],
          },
          feedback: { en: 'Watch what happens: extended to the right, this single piece dives far from the data — it misses $(2, 0)$ and $(3, 1)$ completely. Pieces must stay home.',
                      fr: 'Regardez : prolonge a droite, ce morceau unique plonge loin des donnees — il rate completement $(2, 0)$ et $(3, 1)$. Chaque morceau doit rester chez lui.' },
        },
      ],
    },
  })

  // step 5: verify the C1 join numerically
  const eps = 1e-6
  const slopeLeft = (splinePiece(0, 1) - splinePiece(0, 1 - eps)) / eps
  steps.push({
    plot: {
      ...base,
      fns: [
        { fn: pieceFn(0), color: TEAL, width: 3 },
        { fn: pieceFn(1), color: PURPLE, width: 3 },
      ],
      vlines: [{ x: 1, color: ORANGE, dash: '4 4', label: 'x = 1' }],
    },
    instruction: {
      en: `Zoom on the knot $x = 1$: the slope of the teal piece arriving from the left is $S\'(1^{-}) = ${fmt(slopeLeft, 3)}$ (computed from $M_{1}$).`,
      fr: `Zoom sur le noeud $x = 1$ : la pente du morceau sarcelle arrivant de gauche vaut $S\'(1^{-}) = ${fmt(slopeLeft, 3)}$ (calculee depuis $M_{1}$).`,
    },
    choice: {
      prompt: { en: 'By the smoothness conditions, what slope must the purple piece START with at $x = 1$?',
                fr: 'D\'apres les conditions de regularite, avec quelle pente le morceau violet doit-il DEMARRER en $x = 1$ ?' },
      choices: [
        {
          label: { en: `the same: $${fmt(slopeLeft, 3)}$`, fr: `la meme : $${fmt(slopeLeft, 3)}$` },
          correct: true,
          feedback: { en: 'Exactly: continuity of $S\'$ forces the two tangents to agree at the knot. No kink — that IS the spline.',
                      fr: 'Exactement : la continuite de $S\'$ force les deux tangentes a coincider au noeud. Aucun angle — c\'est CA la spline.' },
        },
        {
          label: { en: 'any slope, the value match is enough', fr: 'n\'importe quelle pente, l\'egalite des valeurs suffit' },
          correct: false,
          feedback: { en: 'No: matching values alone would leave a KINK (a corner) at the knot — that is a broken line, not a spline. We also impose $S\'$ and $S\'\'$ continuity.',
                      fr: 'Non : egaliser seulement les valeurs laisserait un ANGLE au noeud — c\'est une ligne brisee, pas une spline. On impose aussi la continuite de $S\'$ et $S\'\'$.' },
        },
      ],
    },
  })

  // step 6: final comparison spline vs global
  steps.push({
    plot: {
      ...base,
      fns: [
        { fn: spline, color: GREEN, width: 3.5 },
        { fn: globalP, color: ORANGE, width: 2, dash: '6 4' },
      ],
    },
    instruction: {
      en: 'Final comparison on ONE plot: the full natural spline (green, three glued pieces) versus the global polynomial (orange, dashed). Both pass through all four points.',
      fr: 'Comparaison finale sur UN graphe : la spline naturelle complete (verte, trois morceaux colles) contre le polynome global (orange, pointille). Les deux passent par les quatre points.',
    },
    choice: {
      prompt: { en: 'Which curve would you trust to predict between the data, and why?',
                fr: 'A quelle courbe feriez-vous confiance pour predire entre les donnees, et pourquoi ?' },
      choices: [
        {
          label: { en: 'The spline: it stays close to the data band, no wild swings', fr: 'La spline : elle reste proche de la bande des donnees, sans embardees' },
          correct: true,
          feedback: { en: 'Good engineering judgment: low-degree pieces cannot oscillate much, and the smooth gluing keeps the curve calm. With many points this advantage becomes overwhelming.',
                      fr: 'Bon jugement d\'ingenieur : des morceaux de bas degre ne peuvent pas beaucoup osciller, et le collage lisse garde la courbe calme. Avec beaucoup de points cet avantage devient ecrasant.' },
        },
        {
          label: { en: 'The global polynomial: a single formula is always better', fr: 'Le polynome global : une seule formule est toujours meilleure' },
          correct: false,
          feedback: { en: 'A single formula is convenient but the degree grows with the data, and high degree means oscillation (Runge). Convenience is not accuracy.',
                      fr: 'Une seule formule est pratique mais le degre croit avec les donnees, et haut degre signifie oscillation (Runge). La commodite n\'est pas la precision.' },
        },
      ],
    },
  })

  return {
    title: { en: 'Glue a cubic spline yourself', fr: 'Collez une spline cubique vous-meme' },
    steps,
    done: {
      intro: { en: 'You APPLIED the spline concept: low-degree pieces, glued with matching value, slope and curvature. Your decisions:',
               fr: 'Vous avez APPLIQUE le concept de spline : des morceaux de bas degre, colles avec valeur, pente et courbure identiques. Vos decisions :' },
      eqTex: 'S \\in C^{2}: \\quad S_{i}(x_{i+1}) = S_{i+1}(x_{i+1}),\\; S\'_{i} = S\'_{i+1},\\; S\'\'_{i} = S\'\'_{i+1}',
      table: {
        cols: [
          { en: 'decision', fr: 'decision' },
          { en: 'your answer', fr: 'votre reponse' },
          { en: 'concept', fr: 'concept' },
        ],
        rows: [
          ['global cubic overshoots?', 'yes', `max $= ${fmt(gMax, 3)} > 1$`],
          ['missing conditions', '$S\'$, $S\'\'$ at knots', 'smooth gluing'],
          ['condition count', `$${fmt(nCond)}$`, '$= 12$ coefficients: unique spline'],
          ['piece beyond its interval?', 'no', 'switch at the knot'],
          [`slope at knot $x = 1$`, `$${fmt(slopeLeft, 3)}$ on both sides`, '$C^{1}$ continuity'],
          ['trusted curve', 'spline', 'no oscillation'],
        ],
      },
      plot: {
        xMin: -0.3, xMax: 3.3, yMin: -0.6, yMax: 1.6,
        fns: [
          { fn: spline, color: GREEN, width: 3.5 },
          { fn: globalP, color: ORANGE, width: 2, dash: '6 4' },
        ],
        points: SPTS,
        vlines: [{ x: 1, color: TEAL, dash: '4 4' }, { x: 2, color: TEAL, dash: '4 4' }],
      },
      outro: { en: `Concept &#8594; application: the knot curvatures you solved for ($M_{1} = ${fmt(M1)}$, $M_{2} = ${fmt(M2)}$, $M_{0} = M_{3} = 0$) are exactly what makes the three pieces meet with no visible seam, while the global polynomial (dashed) overshoots to $${fmt(gMax, 3)}$. This is why CAD, fonts and trajectories all use splines.`,
               fr: `Concept &#8594; application : les courbures aux noeuds que vous avez determinees ($M_{1} = ${fmt(M1)}$, $M_{2} = ${fmt(M2)}$, $M_{0} = M_{3} = 0$) sont exactement ce qui fait que les trois morceaux se rejoignent sans couture visible, tandis que le polynome global (pointille) depasse jusqu'a $${fmt(gMax, 3)}$. Voila pourquoi la CAO, les polices et les trajectoires utilisent des splines.` },
    },
  }
}

// ==================================================================
// Export
// ==================================================================
export const GUIDED_INTERPOLATION: Record<string, GScript> = {
  concept_polynomial_basics: buildPolynomialBasics(),
  concept_lagrange: buildLagrange(),
  concept_divided_differences: buildDividedDifferences(),
  concept_newton_interpolation: buildNewtonInterpolation(),
  concept_spline_interpolation: buildSpline(),
}
