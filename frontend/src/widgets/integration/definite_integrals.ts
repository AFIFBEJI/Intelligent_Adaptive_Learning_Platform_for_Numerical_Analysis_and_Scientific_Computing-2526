/**
 * Definite Integrals : HTML sliders for a, b above the chart.
 * Shaded area updates live, integral value displayed.
 */
import { WIDGET_COLORS, createControlPanel, createHtmlSlider } from '../shared'

const f = (x: number): number => 0.4 * (x - 1) ** 2 + 0.5 * Math.sin(2 * x) + 1

const i18n = {
  en: { instructions: 'Drag a and b. Shaded area = integral from a to b of f(x) dx.', value: 'Integral value' },
  fr: { instructions: 'Deplace a et b. Aire ombree = integrale de a a b de f(x) dx.', value: 'Valeur de l\'integrale' },
}

function integrate(a: number, b: number): number {
  if (a > b) [a, b] = [b, a]
  const N = 2000, h = (b - a) / N
  let s = 0
  for (let i = 0; i < N; i++) s += f(a + (i + 0.5) * h) * h
  return s
}

export function mountDefiniteIntegralsWidget(container: HTMLElement, lang: 'en' | 'fr'): void {
  if (!window.JXG) return
  const t = i18n[lang]
  container.innerHTML = `
    <div class="widget-header">
      <span class="widget-tag">INTERACTIVE</span>
      <h4 class="widget-title">${t.instructions}</h4>
    </div>
    <div class="widget-slot"></div>
    <div id="jxg-defint" class="jxg-board" style="width:100%;height:380px;"></div>
    <div class="widget-readouts">
      <span class="widget-readout"><strong>${t.value} :</strong> <span id="defint-val">…</span></span>
    </div>
  `
  const panel = createControlPanel(container.querySelector('.widget-slot') as HTMLElement)
  const aSlider = createHtmlSlider({ parent: panel, label: 'a (left)', min: 0, max: 4, step: 0.1, value: 0.5, formatValue: v => v.toFixed(2) })
  const bSlider = createHtmlSlider({ parent: panel, label: 'b (right)', min: 0, max: 4, step: 0.1, value: 3.5, formatValue: v => v.toFixed(2) })

  const board = window.JXG.JSXGraph.initBoard('jxg-defint', {
    boundingbox: [-0.5, 4, 5, -0.7],
    axis: true, grid: true, showCopyright: false, showNavigation: false,
  })
  board.create('functiongraph', [f, 0, 4.5], { strokeColor: WIDGET_COLORS.brand, strokeWidth: 3 })

  let polys: ReturnType<typeof board.create>[] = []
  const valEl = container.querySelector('#defint-val') as HTMLElement
  const redraw = () => {
    polys.forEach(p => board.removeObject(p as never))
    polys = []
    let a = aSlider.getValue(), b = bSlider.getValue()
    if (a > b) [a, b] = [b, a]
    const N = 60, h = (b - a) / N
    for (let i = 0; i < N; i++) {
      const x0 = a + i * h, x1 = a + (i + 1) * h
      polys.push(board.create('polygon',
        [[x0, 0], [x1, 0], [x1, f(x1)], [x0, f(x0)]],
        {
          fillColor: WIDGET_COLORS.brand, fillOpacity: 0.25,
          borders: { strokeColor: 'transparent' },
          vertices: { visible: false }, fixed: true, highlight: false,
        }))
    }
    if (valEl) valEl.textContent = integrate(a, b).toFixed(4)
    board.update()
  }
  aSlider.setOnInput(redraw); bSlider.setOnInput(redraw)
  redraw()
}
