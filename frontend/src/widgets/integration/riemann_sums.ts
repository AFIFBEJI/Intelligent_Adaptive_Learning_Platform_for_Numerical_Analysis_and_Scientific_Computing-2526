/**
 * Riemann Sums : HTML slider N (2 -> 60) above the chart.
 * Rectangles thin and approximation converges to the true integral.
 */
import { WIDGET_COLORS, createControlPanel, createHtmlSlider } from '../shared'

const f = (x: number): number => Math.sin(x) + 0.3 * x + 1.0

const i18n = {
  en: { instructions: 'Drag the slider for N. Rectangles thin, approximation tightens.', approx: 'Riemann sum', truth: 'True integral' },
  fr: { instructions: 'Deplace le curseur N. Les rectangles s\'affinent.', approx: 'Somme de Riemann', truth: 'Integrale vraie' },
}

function trueInt(): number {
  const N = 5000, h = 4 / N
  let s = 0
  for (let i = 0; i < N; i++) s += f((i + 0.5) * h) * h
  return s
}
function riemannLeft(n: number): number {
  const h = 4 / n
  let s = 0
  for (let i = 0; i < n; i++) s += f(i * h) * h
  return s
}

export function mountRiemannSumsWidget(container: HTMLElement, lang: 'en' | 'fr'): void {
  if (!window.JXG) return
  const t = i18n[lang]
  container.innerHTML = `
    <div class="widget-header">
      <span class="widget-tag">INTERACTIVE</span>
      <h4 class="widget-title">${t.instructions}</h4>
    </div>
    <div class="widget-slot"></div>
    <div id="jxg-riemann" class="jxg-board" style="width:100%;height:380px;"></div>
    <div class="widget-readouts">
      <span class="widget-readout"><strong>${t.approx} :</strong> <span id="riemann-approx">…</span></span>
      <span class="widget-readout"><strong>${t.truth} :</strong> <span id="riemann-true">…</span></span>
    </div>
  `
  const panel = createControlPanel(container.querySelector('.widget-slot') as HTMLElement)
  const nSlider = createHtmlSlider({
    parent: panel, label: 'N (rectangles)', min: 2, max: 60, step: 1, value: 6,
    formatValue: v => v.toFixed(0),
  })

  const board = window.JXG.JSXGraph.initBoard('jxg-riemann', {
    boundingbox: [-0.3, 3.5, 4.5, -0.5],
    axis: true, grid: true, showCopyright: false, showNavigation: false,
  })
  board.create('functiongraph', [f, 0, 4], { strokeColor: WIDGET_COLORS.brand, strokeWidth: 3 })

  let polys: ReturnType<typeof board.create>[] = []
  const approxEl = container.querySelector('#riemann-approx') as HTMLElement
  const trueEl = container.querySelector('#riemann-true') as HTMLElement
  if (trueEl) trueEl.textContent = trueInt().toFixed(4)

  const redraw = () => {
    polys.forEach(p => board.removeObject(p as never))
    polys = []
    const n = Math.round(nSlider.getValue())
    const h = 4 / n
    for (let i = 0; i < n; i++) {
      const x0 = i * h
      polys.push(board.create('polygon',
        [[x0, 0], [x0 + h, 0], [x0 + h, f(x0)], [x0, f(x0)]],
        {
          fillColor: WIDGET_COLORS.brandLight, fillOpacity: 0.4,
          borders: { strokeColor: WIDGET_COLORS.amber, strokeWidth: 1 },
          vertices: { visible: false }, fixed: true, highlight: false,
        }))
    }
    if (approxEl) approxEl.textContent = `${riemannLeft(n).toFixed(4)} (N=${n})`
    board.update()
  }
  nSlider.setOnInput(redraw)
  redraw()
}
