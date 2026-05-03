/**
 * Polynomial Basics : 4 HTML sliders (a, b, c, d) above the chart.
 * Build any polynomial of degree <= 3 by adjusting coefficients.
 */
import { WIDGET_COLORS, createControlPanel, createHtmlSlider } from '../shared'

const i18n = {
  en: { instructions: 'Adjust each coefficient and watch the polynomial change.' },
  fr: { instructions: 'Ajuste chaque coefficient et observe le polynome changer.' },
}

export function mountPolynomialBasicsWidget(container: HTMLElement, lang: 'en' | 'fr'): void {
  if (!window.JXG) return
  const t = i18n[lang]
  container.innerHTML = `
    <div class="widget-header">
      <span class="widget-tag">INTERACTIVE</span>
      <h4 class="widget-title">${t.instructions}</h4>
    </div>
    <div class="widget-slot"></div>
    <div id="jxg-polybasics" class="jxg-board" style="width:100%;height:380px;"></div>
  `
  const panel = createControlPanel(container.querySelector('.widget-slot') as HTMLElement)
  const sa = createHtmlSlider({ parent: panel, label: 'a (x³)', min: -1, max: 1, step: 0.05, value: 0.30, formatValue: v => v.toFixed(2) })
  const sb = createHtmlSlider({ parent: panel, label: 'b (x²)', min: -2, max: 2, step: 0.1, value: -0.50, formatValue: v => v.toFixed(2) })
  const sc = createHtmlSlider({ parent: panel, label: 'c (x)',  min: -3, max: 3, step: 0.1, value: 0.50, formatValue: v => v.toFixed(2) })
  const sd = createHtmlSlider({ parent: panel, label: 'd',      min: -3, max: 3, step: 0.1, value: 0.0, formatValue: v => v.toFixed(2) })

  const board = window.JXG.JSXGraph.initBoard('jxg-polybasics', {
    boundingbox: [-3, 6, 3, -4],
    axis: true, grid: true, showCopyright: false, showNavigation: false,
  })
  board.create('functiongraph', [
    (x: number) => sa.getValue() * x ** 3 + sb.getValue() * x ** 2 + sc.getValue() * x + sd.getValue(),
    -3, 3,
  ], { strokeColor: WIDGET_COLORS.brand, strokeWidth: 3 })

  const refresh = () => board.update()
  sa.setOnInput(refresh); sb.setOnInput(refresh); sc.setOnInput(refresh); sd.setOnInput(refresh)
}
