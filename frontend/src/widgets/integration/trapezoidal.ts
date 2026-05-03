/**
 * Trapezoidal rule : HTML slider N (2 -> 50) above the chart.
 * Trapezoids redraw live, approximation value compared to true integral.
 */
import { WIDGET_COLORS, createControlPanel, createHtmlSlider } from '../shared'

const f = (x: number): number => Math.sin(x) + 0.25 * x + 1.0

const i18n = {
  en: { instructions: 'Drag the slider for N. Approximation tightens as N grows.', approx: 'Trapezoidal approximation', truth: 'True integral' },
  fr: { instructions: 'Deplace le curseur N. L\'approximation se resserre quand N grandit.', approx: 'Approximation trapezes', truth: 'Integrale vraie' },
}

function trueIntegral(): number {
  const N = 5000, a = 0, b = 4, h = (b - a) / N
  let s = 0
  for (let i = 0; i < N; i++) s += f(a + (i + 0.5) * h) * h
  return s
}
function trapezoidalApprox(n: number): number {
  const a = 0, b = 4, h = (b - a) / n
  let s = 0.5 * (f(a) + f(b))
  for (let i = 1; i < n; i++) s += f(a + i * h)
  return s * h
}

export function mountTrapezoidalWidget(container: HTMLElement, lang: 'en' | 'fr'): void {
  if (!window.JXG) return
  const t = i18n[lang]
  container.innerHTML = `
    <div class="widget-header">
      <span class="widget-tag">INTERACTIVE</span>
      <h4 class="widget-title">${t.instructions}</h4>
    </div>
    <div class="widget-slot"></div>
    <div id="jxg-trapezoidal" class="jxg-board" style="width:100%;height:380px;"></div>
    <div class="widget-readouts">
      <span class="widget-readout"><strong>${t.approx} :</strong> <span id="trap-approx">…</span></span>
      <span class="widget-readout"><strong>${t.truth} :</strong> <span id="trap-true">…</span></span>
    </div>
  `
  const panel = createControlPanel(container.querySelector('.widget-slot') as HTMLElement)
  const nSlider = createHtmlSlider({
    parent: panel, label: 'N (trapezoids)', min: 2, max: 50, step: 1, value: 8,
    formatValue: v => v.toFixed(0),
  })

  const board = window.JXG.JSXGraph.initBoard('jxg-trapezoidal', {
    boundingbox: [-0.5, 3.5, 4.5, -0.5],
    axis: true, grid: true, showCopyright: false, showNavigation: false,
  })
  board.create('functiongraph', [f, 0, 4], { strokeColor: WIDGET_COLORS.brand, strokeWidth: 3 })

  let polygons: ReturnType<typeof board.create>[] = []
  const trueVal = trueIntegral()
  const approxEl = container.querySelector('#trap-approx') as HTMLElement
  const trueEl = container.querySelector('#trap-true') as HTMLElement
  if (trueEl) trueEl.textContent = trueVal.toFixed(4)

  const redraw = () => {
    polygons.forEach(p => board.removeObject(p as never))
    polygons = []
    const n = Math.round(nSlider.getValue())
    const h = 4 / n
    for (let i = 0; i < n; i++) {
      const x0 = i * h, x1 = (i + 1) * h
      polygons.push(board.create('polygon',
        [[x0, 0], [x1, 0], [x1, f(x1)], [x0, f(x0)]],
        {
          fillColor: WIDGET_COLORS.brandLight, fillOpacity: 0.45,
          borders: { strokeColor: WIDGET_COLORS.amber, strokeWidth: 1.2 },
          vertices: { visible: false }, fixed: true, highlight: false,
        }))
    }
    if (approxEl) approxEl.textContent = `${trapezoidalApprox(n).toFixed(4)} (N=${n})`
    board.update()
  }
  nSlider.setOnInput(redraw)
  redraw()
}
