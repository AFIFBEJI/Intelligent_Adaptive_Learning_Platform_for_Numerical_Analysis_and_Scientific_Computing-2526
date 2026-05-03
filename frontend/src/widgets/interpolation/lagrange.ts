/**
 * Lagrange interpolation : drag 4 points, the polynomial passing through
 * them updates in real time. The hands-on counterpart to the Manim video.
 */
import { WIDGET_COLORS } from '../shared'

const i18n = {
  en: {
    instructions: 'Drag any of the 4 points and watch the polynomial follow.',
    formula: 'Lagrange polynomial through the points',
  },
  fr: {
    instructions: 'Deplace n\'importe lequel des 4 points et observe le polynome suivre.',
    formula: 'Polynome de Lagrange passant par les points',
  },
}

/**
 * Solve a*x^3 + b*x^2 + c*x + d = y for 4 (x_i, y_i) using Cramer's rule.
 * Returns [a, b, c, d]. Falls back to lower degree if points are colinear,
 * but for our 4 user-draggable points we always assume general position.
 */
function fitCubic(pts: [number, number][]): [number, number, number, number] {
  // Build Vandermonde-like 4x4 system and solve.
  const x = pts.map(p => p[0])
  const y = pts.map(p => p[1])
  // 4x4 matrix
  const M: number[][] = x.map(xi => [xi ** 3, xi ** 2, xi, 1])

  // Solve via Gauss elimination (small, ok)
  const aug = M.map((row, i) => [...row, y[i]])
  const n = 4
  for (let i = 0; i < n; i++) {
    // pivot
    let max = i
    for (let k = i + 1; k < n; k++) {
      if (Math.abs(aug[k][i]) > Math.abs(aug[max][i])) max = k
    }
    ;[aug[i], aug[max]] = [aug[max], aug[i]]
    if (Math.abs(aug[i][i]) < 1e-12) return [0, 0, 0, 0]
    for (let k = i + 1; k < n; k++) {
      const f = aug[k][i] / aug[i][i]
      for (let j = i; j <= n; j++) aug[k][j] -= f * aug[i][j]
    }
  }
  // Back-substitute
  const c = [0, 0, 0, 0]
  for (let i = n - 1; i >= 0; i--) {
    let s = aug[i][n]
    for (let j = i + 1; j < n; j++) s -= aug[i][j] * c[j]
    c[i] = s / aug[i][i]
  }
  return [c[0], c[1], c[2], c[3]]
}

export function mountLagrangeWidget(container: HTMLElement, lang: 'en' | 'fr'): void {
  if (!window.JXG) return  // CDN not yet loaded

  const t = i18n[lang]

  // Container shell : title + JSXGraph board + dynamic formula readout
  container.innerHTML = `
    <div class="widget-header">
      <span class="widget-tag">INTERACTIVE</span>
      <h4 class="widget-title">${t.instructions}</h4>
    </div>
    <div id="jxg-lagrange" class="jxg-board" style="width:100%; height:380px;"></div>
    <p class="widget-formula" id="jxg-lagrange-formula">${t.formula}</p>
  `

  const board = window.JXG.JSXGraph.initBoard('jxg-lagrange', {
    boundingbox: [-1, 5, 6, -1],
    axis: true,
    grid: true,
    showCopyright: false,
    showNavigation: false,
  })

  // 4 draggable points with brand teal color
  const initial: [number, number][] = [[0, 1], [1.5, 3.2], [3, 1.5], [4.5, 3.5]]
  const points = initial.map(([x, y], i) =>
    board.create('point', [x, y], {
      name: `P${i}`,
      size: 5,
      strokeColor: '#fff',
      fillColor: WIDGET_COLORS.amber,
      fixed: false,
      label: { offset: [10, 10], color: WIDGET_COLORS.textPrimary, fontSize: 12 },
    })
  )

  const formulaEl = container.querySelector('#jxg-lagrange-formula') as HTMLElement

  // PURE function for the curve : just compute and return y = P(x).
  // No side effects allowed (JSXGraph re-evaluates 200+ times per frame).
  board.create(
    'functiongraph',
    [
      (x: number) => {
        const pts = points.map(p => [p.X(), p.Y()] as [number, number])
        const [a, b, c, d] = fitCubic(pts)
        return a * x ** 3 + b * x ** 2 + c * x + d
      },
      -1,
      6,
    ],
    { strokeColor: WIDGET_COLORS.brand, strokeWidth: 3 },
  )

  // Update the formula display only when a point is dragged.
  const updateFormula = () => {
    const pts = points.map(p => [p.X(), p.Y()] as [number, number])
    const [a, b, c, d] = fitCubic(pts)
    if (formulaEl) {
      formulaEl.textContent = `P(x) = ${fmt(a)}x³ + ${fmt(b)}x² + ${fmt(c)}x + ${fmt(d)}`
    }
  }
  points.forEach(p => {
    ;(p as unknown as { on: (e: string, fn: () => void) => void }).on('drag', updateFormula)
  })
  updateFormula()
}

function fmt(n: number): string {
  if (Math.abs(n) < 1e-3) return '0'
  return (n >= 0 ? '+' : '') + n.toFixed(2)
}
