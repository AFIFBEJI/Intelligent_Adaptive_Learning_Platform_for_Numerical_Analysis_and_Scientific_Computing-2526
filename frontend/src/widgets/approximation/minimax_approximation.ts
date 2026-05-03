/**
 * Minimax Approximation : HTML sliders for a, b, c above the chart.
 * The user adjusts the polynomial p(x) = ax² + bx + c and watches
 * the maximum |f - p| update live.
 */
import { WIDGET_COLORS, createControlPanel, createHtmlSlider } from '../shared'

const f = (x: number): number => Math.sin(x) + 0.3 * x ** 2 / 4

const i18n = {
  en: { instructions: 'Adjust a, b, c. Try to minimize the worst-case error |f - p|.', err: 'Max |error|' },
  fr: { instructions: 'Ajuste a, b, c. Tente de minimiser l\'erreur max |f - p|.', err: 'Erreur max' },
}

export function mountMinimaxApproximationWidget(container: HTMLElement, lang: 'en' | 'fr'): void {
  if (!window.JXG) return
  const t = i18n[lang]
  container.innerHTML = `
    <div class="widget-header">
      <span class="widget-tag">INTERACTIVE</span>
      <h4 class="widget-title">${t.instructions}</h4>
    </div>
    <div class="widget-slot"></div>
    <div id="jxg-mmx" class="jxg-board" style="width:100%;height:380px;"></div>
    <div class="widget-readouts">
      <span class="widget-readout"><strong>${t.err} :</strong> <span id="mmx-err">…</span></span>
    </div>
  `
  const panel = createControlPanel(container.querySelector('.widget-slot') as HTMLElement)
  const sa = createHtmlSlider({ parent: panel, label: 'a', min: -1, max: 1, step: 0.02, value: 0.32, formatValue: v => v.toFixed(2) })
  const sb = createHtmlSlider({ parent: panel, label: 'b', min: -1, max: 1, step: 0.02, value: 0.22, formatValue: v => v.toFixed(2) })
  const sc = createHtmlSlider({ parent: panel, label: 'c', min: -1, max: 1, step: 0.02, value: 0.05, formatValue: v => v.toFixed(2) })

  const board = window.JXG.JSXGraph.initBoard('jxg-mmx', {
    boundingbox: [-2.5, 2.5, 2.5, -2],
    axis: true, grid: true, showCopyright: false, showNavigation: false,
  })
  board.create('functiongraph', [f, -2.3, 2.3], { strokeColor: WIDGET_COLORS.brand, strokeWidth: 3 })

  const errEl = container.querySelector('#mmx-err') as HTMLElement
  const p = (x: number) => sa.getValue() * x ** 2 + sb.getValue() * x + sc.getValue()
  board.create('functiongraph', [p, -2.3, 2.3], {
    strokeColor: WIDGET_COLORS.amber, strokeWidth: 3,
  })

  const updateMax = () => {
    let mx = 0
    for (let i = 0; i <= 200; i++) {
      const x = -2.3 + (4.6 * i) / 200
      mx = Math.max(mx, Math.abs(f(x) - p(x)))
    }
    if (errEl) errEl.textContent = mx.toFixed(4)
    board.update()
  }
  sa.setOnInput(updateMax)
  sb.setOnInput(updateMax)
  sc.setOnInput(updateMax)
  updateMax()
}
