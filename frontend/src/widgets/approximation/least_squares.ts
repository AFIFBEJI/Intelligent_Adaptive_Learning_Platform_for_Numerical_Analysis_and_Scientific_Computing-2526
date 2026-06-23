/**
 * Least Squares : drag 8 noisy data points, the best-fit line follows.
 * Residuals shown as red dashed segments.
 *
 * IMPORTANT : the function passed to `functiongraph` MUST be pure (no
 * side effects). JSXGraph calls it 200+ times per render to draw the
 * curve ; if the callback creates board elements, each creation triggers
 * a re-render which calls the callback again -> infinite loop, browser
 * hangs. Hence we keep the line fn pure and update residuals via
 * an `update` event listener on the board.
 */
import { WIDGET_COLORS } from '../shared'

const i18n = {
  en: { instructions: 'Drag any data point. Best-fit line and residuals update live.' },
  fr: { instructions: 'Deplace n\'importe quel point. La droite et les residus suivent.' },
}

function computeFit(points: { X(): number; Y(): number }[]): { m: number; b: number } {
  const n = points.length
  let sx = 0, sy = 0, sxx = 0, sxy = 0
  for (const p of points) {
    const x = p.X(), y = p.Y()
    sx += x; sy += y; sxx += x * x; sxy += x * y
  }
  const m = (n * sxy - sx * sy) / (n * sxx - sx * sx)
  const b = (sy - m * sx) / n
  return { m, b }
}

export function mountLeastSquaresWidget(container: HTMLElement, lang: 'en' | 'fr'): void {
  if (!window.JXG) return
  const t = i18n[lang]
  container.innerHTML = `
    <div class="widget-header">
      <span class="widget-tag">INTERACTIVE</span>
      <h4 class="widget-title">${t.instructions}</h4>
    </div>
    <div id="jxg-leastsq" class="jxg-board" style="width:100%;height:380px;"></div>
    <p class="widget-formula" id="leastsq-formula">y = mx + b</p>
  `
  const board = window.JXG.JSXGraph.initBoard('jxg-leastsq', {
    boundingbox: [-0.5, 6, 7, -1],
    axis: true, grid: true, showCopyright: false, showNavigation: false,
  })
  const initial: [number, number][] = [
    [0.5, 1.2], [1.0, 1.6], [1.7, 2.6], [2.4, 2.0],
    [3.2, 3.4], [4.0, 3.6], [4.8, 4.4], [5.6, 4.0],
  ]
  const points = initial.map(([x, y]) =>
    board.create('point', [x, y], {
      size: 4, fillColor: WIDGET_COLORS.amber, strokeColor: '#fff', withLabel: false,
    }),
  )

  const formulaEl = container.querySelector('#leastsq-formula') as HTMLElement
  let resids: ReturnType<typeof board.create>[] = []

  // PURE function for the regression line — NO side effects allowed here.
  // JSXGraph re-evaluates this many times per frame.
  board.create('functiongraph', [
    (x: number) => {
      const { m, b } = computeFit(points)
      return m * x + b
    },
    -0.3, 6.3,
  ], { strokeColor: WIDGET_COLORS.brand, strokeWidth: 3 })

  // Update residuals + formula DOM ONLY when a point is dragged or initially.
  // We use the global `update` event of the board, fired exactly once per
  // user interaction frame.
  const refreshResidualsAndFormula = () => {
    const { m, b } = computeFit(points)
    if (formulaEl) {
      formulaEl.textContent = `y = ${m.toFixed(3)} x + ${b.toFixed(3)}`
    }
    // Wipe old residuals, build new ones
    resids.forEach(r => board.removeObject(r as never))
    resids = []
    for (const p of points) {
      const xv = p.X(), yv = p.Y(), pred = m * xv + b
      resids.push(board.create('segment', [[xv, yv], [xv, pred]], {
        strokeColor: WIDGET_COLORS.red, strokeWidth: 1.5, dash: 2,
        fixed: true, highlight: false,
      }))
    }
  }

  // Hook the update on each point so residuals follow the drag
  points.forEach(p => {
    ;(p as unknown as { on: (e: string, fn: () => void) => void }).on('drag', refreshResidualsAndFormula)
  })
  refreshResidualsAndFormula()  // initial render
}
