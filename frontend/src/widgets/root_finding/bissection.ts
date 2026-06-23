/**
 * Bisection : HTML sliders for a, b above the chart. Show 5 successive
 * brackets narrowing on the root of f(x) = x^3 - 2x - 5.
 */
import { WIDGET_COLORS, createControlPanel, createHtmlSlider } from '../shared'

const f = (x: number): number => x ** 3 - 2 * x - 5

const i18n = {
  en: { instructions: 'Drag a, b. Each iteration halves the bracket.', root: 'Bracket midpoint after 5 iterations' },
  fr: { instructions: 'Deplace a, b. Chaque iteration divise l\'intervalle par 2.', root: 'Milieu du bracket apres 5 iterations' },
}

export function mountBisectionWidget(container: HTMLElement, lang: 'en' | 'fr'): void {
  if (!window.JXG) return
  const t = i18n[lang]
  container.innerHTML = `
    <div class="widget-header">
      <span class="widget-tag">INTERACTIVE</span>
      <h4 class="widget-title">${t.instructions}</h4>
    </div>
    <div class="widget-slot"></div>
    <div id="jxg-bissection" class="jxg-board" style="width:100%;height:380px;"></div>
    <div class="widget-readouts">
      <span class="widget-readout"><strong>${t.root} :</strong> <span id="bis-root">…</span></span>
    </div>
  `
  const panel = createControlPanel(container.querySelector('.widget-slot') as HTMLElement)
  const aSlider = createHtmlSlider({ parent: panel, label: 'a', min: 0.5, max: 2.0, step: 0.1, value: 1.0, formatValue: v => v.toFixed(2) })
  const bSlider = createHtmlSlider({ parent: panel, label: 'b', min: 2.0, max: 3.5, step: 0.1, value: 3.0, formatValue: v => v.toFixed(2) })

  const board = window.JXG.JSXGraph.initBoard('jxg-bissection', {
    boundingbox: [-0.5, 14, 4, -10],
    axis: true, grid: true, showCopyright: false, showNavigation: false,
  })
  board.create('functiongraph', [f, 0.1, 3.6], { strokeColor: WIDGET_COLORS.brand, strokeWidth: 3 })

  let segs: ReturnType<typeof board.create>[] = []
  const rootEl = container.querySelector('#bis-root') as HTMLElement

  const redraw = () => {
    segs.forEach(s => board.removeObject(s as never))
    segs = []
    let a = aSlider.getValue(), b = bSlider.getValue()
    if (a > b) [a, b] = [b, a]
    if (f(a) * f(b) >= 0) {
      if (rootEl) rootEl.textContent = '(no sign change in [a, b])'
      return
    }
    for (let i = 0; i < 5; i++) {
      const m = (a + b) / 2
      const yOff = -1 - i * 0.7
      segs.push(board.create('segment', [[a, yOff], [b, yOff]], {
        strokeColor: WIDGET_COLORS.amber, strokeWidth: 4 - i * 0.4,
        fixed: true, highlight: false,
      }))
      segs.push(board.create('point', [m, yOff], {
        size: 3, fillColor: WIDGET_COLORS.red, strokeColor: '#fff',
        withLabel: false, fixed: true, highlight: false,
      }))
      if (f(a) * f(m) < 0) b = m
      else a = m
    }
    if (rootEl) rootEl.textContent = ((a + b) / 2).toFixed(4)
    board.update()
  }
  aSlider.setOnInput(redraw)
  bSlider.setOnInput(redraw)
  redraw()
}
