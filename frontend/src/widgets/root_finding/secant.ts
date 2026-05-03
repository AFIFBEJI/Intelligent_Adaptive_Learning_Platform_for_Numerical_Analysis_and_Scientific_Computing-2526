/**
 * Secant Method : HTML sliders for x_prev and x_curr above the chart.
 * 4 secants drawn between consecutive iterates.
 */
import { WIDGET_COLORS, createControlPanel, createHtmlSlider } from '../shared'

const f = (x: number): number => x ** 3 - 2 * x - 5

const i18n = {
  en: { instructions: 'Drag the two starting points. The secants converge to the root.' },
  fr: { instructions: 'Deplace les deux points de depart. Les secantes convergent vers la racine.' },
}

export function mountSecantWidget(container: HTMLElement, lang: 'en' | 'fr'): void {
  if (!window.JXG) return
  const t = i18n[lang]
  container.innerHTML = `
    <div class="widget-header">
      <span class="widget-tag">INTERACTIVE</span>
      <h4 class="widget-title">${t.instructions}</h4>
    </div>
    <div class="widget-slot"></div>
    <div id="jxg-secant" class="jxg-board" style="width:100%;height:380px;"></div>
  `
  const panel = createControlPanel(container.querySelector('.widget-slot') as HTMLElement)
  // Plain ASCII names ; underscores would render literally
  const xPrev = createHtmlSlider({ parent: panel, label: 'x prev', min: 0.5, max: 2.0, step: 0.1, value: 1.0, formatValue: v => v.toFixed(2) })
  const x0 = createHtmlSlider({ parent: panel, label: 'x curr', min: 2.0, max: 3.5, step: 0.1, value: 3.0, formatValue: v => v.toFixed(2) })

  const board = window.JXG.JSXGraph.initBoard('jxg-secant', {
    boundingbox: [-0.5, 14, 4, -10],
    axis: true, grid: true, showCopyright: false, showNavigation: false,
  })
  board.create('functiongraph', [f, 0.1, 3.6], { strokeColor: WIDGET_COLORS.brand, strokeWidth: 3 })

  let elems: ReturnType<typeof board.create>[] = []
  const redraw = () => {
    elems.forEach(e => board.removeObject(e as never))
    elems = []
    let xp = xPrev.getValue()
    let x = x0.getValue()
    for (let i = 0; i < 4; i++) {
      const slope = (f(x) - f(xp)) / (x - xp)
      if (Math.abs(slope) < 1e-9) break
      const xNext = x - f(x) / slope
      const xL = Math.max(-0.4, Math.min(xp, x, xNext) - 0.3)
      const xR = Math.max(xp, x, xNext) + 0.2
      const yAt = (t: number) => slope * (t - x) + f(x)
      elems.push(board.create('segment', [[xL, yAt(xL)], [xR, yAt(xR)]], {
        strokeColor: i === 3 ? WIDGET_COLORS.green : WIDGET_COLORS.red,
        strokeWidth: 2, fixed: true, highlight: false,
      }))
      elems.push(board.create('point', [xNext, 0], {
        size: 4, fillColor: i === 3 ? WIDGET_COLORS.green : WIDGET_COLORS.amber,
        strokeColor: '#fff', withLabel: false, fixed: true, highlight: false,
      }))
      xp = x
      x = xNext
    }
    board.update()
  }
  xPrev.setOnInput(redraw)
  x0.setOnInput(redraw)
  redraw()
}
