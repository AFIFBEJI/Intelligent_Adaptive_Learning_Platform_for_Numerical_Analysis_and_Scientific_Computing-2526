/**
 * Orthogonal Polynomials : HTML slider for degree n above the chart.
 * Each Legendre polynomial appears in its own color.
 */
import { WIDGET_COLORS, createControlPanel, createHtmlSlider } from '../shared'

const PALETTE = [WIDGET_COLORS.brand, WIDGET_COLORS.amber, WIDGET_COLORS.green,
  WIDGET_COLORS.brandLight, WIDGET_COLORS.red]

const P: ((x: number) => number)[] = [
  () => 1,
  (x) => x,
  (x) => 0.5 * (3 * x ** 2 - 1),
  (x) => 0.5 * (5 * x ** 3 - 3 * x),
  (x) => (35 * x ** 4 - 30 * x ** 2 + 3) / 8,
]

const i18n = {
  en: { instructions: 'Drag n. Each Legendre polynomial appears in its own color.' },
  fr: { instructions: 'Deplace n. Chaque polynome de Legendre apparait dans sa couleur.' },
}

export function mountOrthogonalPolynomialsWidget(container: HTMLElement, lang: 'en' | 'fr'): void {
  if (!window.JXG) return
  const t = i18n[lang]
  container.innerHTML = `
    <div class="widget-header">
      <span class="widget-tag">INTERACTIVE</span>
      <h4 class="widget-title">${t.instructions}</h4>
    </div>
    <div class="widget-slot"></div>
    <div id="jxg-ortho" class="jxg-board" style="width:100%;height:380px;"></div>
  `
  const panel = createControlPanel(container.querySelector('.widget-slot') as HTMLElement)
  const nSlider = createHtmlSlider({
    parent: panel, label: 'max degree n', min: 0, max: 4, step: 1, value: 2,
    formatValue: v => v.toFixed(0),
  })

  const board = window.JXG.JSXGraph.initBoard('jxg-ortho', {
    boundingbox: [-1.2, 1.5, 1.2, -1.5],
    axis: true, grid: true, showCopyright: false, showNavigation: false,
  })

  let curves: ReturnType<typeof board.create>[] = []
  const redraw = () => {
    curves.forEach(c => board.removeObject(c as never))
    curves = []
    const n = Math.round(nSlider.getValue())
    for (let i = 0; i <= n; i++) {
      curves.push(board.create('functiongraph', [P[i], -1, 1],
        { strokeColor: PALETTE[i % PALETTE.length], strokeWidth: 2.5 }))
    }
    board.update()
  }
  nSlider.setOnInput(redraw)
  redraw()
}
