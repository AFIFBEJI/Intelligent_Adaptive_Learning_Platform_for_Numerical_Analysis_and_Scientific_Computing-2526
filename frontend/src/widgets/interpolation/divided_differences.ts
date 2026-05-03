/**
 * Divided Differences : drag 4 points and see the divided differences table
 * recompute live alongside the interpolating polynomial.
 */
import { WIDGET_COLORS } from '../shared'

const i18n = {
  en: { instructions: 'Drag the 4 points. The divided differences table updates live.' },
  fr: { instructions: 'Deplace les 4 points. La table des differences divisees est recalculee en direct.' },
}

function fmt(n: number): string { return n.toFixed(3) }

export function mountDividedDifferencesWidget(container: HTMLElement, lang: 'en' | 'fr'): void {
  if (!window.JXG) return
  const t = i18n[lang]
  container.innerHTML = `
    <div class="widget-header">
      <span class="widget-tag">INTERACTIVE</span>
      <h4 class="widget-title">${t.instructions}</h4>
    </div>
    <div id="jxg-dd" class="jxg-board" style="width:100%;height:340px;"></div>
    <pre class="widget-formula" id="dd-table" style="font-size:0.78rem;line-height:1.6;"></pre>
  `

  const board = window.JXG.JSXGraph.initBoard('jxg-dd', {
    boundingbox: [-0.5, 5, 4.5, -1.5],
    axis: true, grid: true, showCopyright: false, showNavigation: false,
  })
  const initial: [number, number][] = [[0, 1], [1, 3], [2, 1.5], [3.5, 3]]
  const points = initial.map(([x, y], i) =>
    board.create('point', [x, y], {
      name: `(x_${i}, y_${i})`, size: 5, fillColor: WIDGET_COLORS.amber, strokeColor: '#fff',
      label: { offset: [10, 10], color: WIDGET_COLORS.textPrimary, fontSize: 11 },
    }),
  )

  const tableEl = container.querySelector('#dd-table') as HTMLElement

  // Pure helper : compute divided differences (no side effects).
  const computeDiagCoeffs = (): { coeffs: number[]; xs: number[] } => {
    const xs = points.map(p => p.X())
    const ys = points.map(p => p.Y())
    const n = xs.length
    const dd: number[][] = ys.map(v => [v])
    for (let j = 1; j < n; j++) {
      for (let i = 0; i < n - j; i++) {
        dd[i][j] = (dd[i + 1][j - 1] - dd[i][j - 1]) / (xs[i + j] - xs[i])
      }
    }
    return { coeffs: dd[0], xs }
  }
  const evalNewton = (x: number, coeffs: number[], xs: number[]): number => {
    let res = coeffs[coeffs.length - 1]
    for (let i = coeffs.length - 2; i >= 0; i--) res = res * (x - xs[i]) + coeffs[i]
    return res
  }

  // PURE function for the curve.
  board.create('functiongraph', [
    (x: number) => {
      const { coeffs, xs } = computeDiagCoeffs()
      return evalNewton(x, coeffs, xs)
    },
    -0.5, 4.5,
  ], { strokeColor: WIDGET_COLORS.brand, strokeWidth: 3 })

  // Update the displayed table only on drag (DOM side effect).
  // We render the subscripts using HTML <sub> via innerHTML so that
  // 'x₀, x₁, x₂' display nicely without literal underscores.
  const refreshTable = () => {
    const { coeffs } = computeDiagCoeffs()
    if (!tableEl) return
    tableEl.innerHTML = [
      `f[x₀]              =  <strong>${fmt(coeffs[0])}</strong>`,
      `f[x₀, x₁]          =  <strong>${fmt(coeffs[1])}</strong>`,
      `f[x₀, x₁, x₂]      =  <strong>${fmt(coeffs[2])}</strong>`,
      `f[x₀, x₁, x₂, x₃]  =  <strong>${fmt(coeffs[3])}</strong>`,
    ].join('\n')
  }
  points.forEach(p => {
    ;(p as unknown as { on: (e: string, fn: () => void) => void }).on('drag', refreshTable)
  })
  refreshTable()
}
