/**
 * Spline Interpolation : drag 5 points, natural cubic spline updates.
 * We compute the spline using the standard tridiagonal system for
 * second derivatives at internal knots.
 */
import { WIDGET_COLORS } from '../shared'

const i18n = {
  en: { instructions: 'Drag the 5 points. The natural cubic spline follows.' },
  fr: { instructions: 'Deplace les 5 points. La spline cubique naturelle suit.' },
}

/**
 * Solve a tridiagonal system Ax = d (Thomas algorithm).
 * a[i] = sub-diagonal (a[0] unused), b[i] = diagonal, c[i] = super-diagonal (c[n-1] unused).
 */
function thomas(a: number[], b: number[], c: number[], d: number[]): number[] {
  const n = b.length
  const cp = [...c], dp = [...d]
  cp[0] = c[0] / b[0]
  dp[0] = d[0] / b[0]
  for (let i = 1; i < n; i++) {
    const m = b[i] - a[i] * cp[i - 1]
    cp[i] = c[i] / m
    dp[i] = (d[i] - a[i] * dp[i - 1]) / m
  }
  const x = new Array(n).fill(0)
  x[n - 1] = dp[n - 1]
  for (let i = n - 2; i >= 0; i--) x[i] = dp[i] - cp[i] * x[i + 1]
  return x
}

function naturalSpline(xs: number[], ys: number[]): {
  evalAt: (x: number) => number
} {
  const n = xs.length
  const h = new Array(n - 1).fill(0)
  for (let i = 0; i < n - 1; i++) h[i] = xs[i + 1] - xs[i]

  // Solve for second derivatives M[i] using natural BC : M[0] = M[n-1] = 0
  const A = new Array(n - 2).fill(0)
  const B = new Array(n - 2).fill(0)
  const C = new Array(n - 2).fill(0)
  const D = new Array(n - 2).fill(0)
  for (let i = 0; i < n - 2; i++) {
    A[i] = i === 0 ? 0 : h[i]
    B[i] = 2 * (h[i] + h[i + 1])
    C[i] = i === n - 3 ? 0 : h[i + 1]
    D[i] = 6 * ((ys[i + 2] - ys[i + 1]) / h[i + 1] - (ys[i + 1] - ys[i]) / h[i])
  }
  const M_inner = thomas(A, B, C, D)
  const M = [0, ...M_inner, 0]

  return {
    evalAt: (x: number) => {
      // Find segment
      let i = 0
      for (i = 0; i < n - 1; i++) if (x <= xs[i + 1]) break
      i = Math.min(i, n - 2)
      const dx1 = x - xs[i]
      const dx2 = xs[i + 1] - x
      const hi = h[i]
      return (M[i] * dx2 ** 3 + M[i + 1] * dx1 ** 3) / (6 * hi)
        + (ys[i] / hi - M[i] * hi / 6) * dx2
        + (ys[i + 1] / hi - M[i + 1] * hi / 6) * dx1
    },
  }
}

export function mountSplineInterpolationWidget(container: HTMLElement, lang: 'en' | 'fr'): void {
  if (!window.JXG) return
  const t = i18n[lang]
  container.innerHTML = `
    <div class="widget-header">
      <span class="widget-tag">INTERACTIVE</span>
      <h4 class="widget-title">${t.instructions}</h4>
    </div>
    <div id="jxg-spline" class="jxg-board" style="width:100%;height:380px;"></div>
  `
  const board = window.JXG.JSXGraph.initBoard('jxg-spline', {
    boundingbox: [-0.5, 5, 5.5, -1.5],
    axis: true, grid: true, showCopyright: false, showNavigation: false,
  })
  const initial: [number, number][] = [[0, 1], [1, 2.5], [2, 0.5], [3, 3], [4, 1.5]]
  const points = initial.map(([x, y]) =>
    board.create('point', [x, y], {
      size: 5, fillColor: WIDGET_COLORS.amber, strokeColor: '#fff',
      withLabel: false,
    }),
  )

  board.create('functiongraph', [
    (x: number) => {
      const xs = points.map(p => p.X()).sort((a, b) => a - b)
      // Re-index ys to match sorted xs
      const sortedPts = points.map(p => [p.X(), p.Y()] as [number, number])
        .sort((a, b) => a[0] - b[0])
      const ys = sortedPts.map(p => p[1])
      try {
        const sp = naturalSpline(xs, ys)
        return sp.evalAt(Math.max(xs[0], Math.min(xs[xs.length - 1], x)))
      } catch {
        return 0
      }
    },
    0, 4,
  ], { strokeColor: WIDGET_COLORS.brand, strokeWidth: 3 })
}
