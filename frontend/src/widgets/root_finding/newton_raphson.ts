/**
 * Newton-Raphson : HTML slider for the starting point x_0 above the chart.
 * 4 successive tangents converge on the root.
 */
import { WIDGET_COLORS, createControlPanel, createHtmlSlider } from '../shared'

const f = (x: number): number => x ** 3 - 2 * x - 5
const fp = (x: number): number => 3 * x ** 2 - 2

const i18n = {
  en: { instructions: 'Drag the starting point. The 4 tangents converge on the root.' },
  fr: { instructions: 'Deplace le point de depart. Les 4 tangentes convergent vers la racine.' },
}

export function mountNewtonRaphsonWidget(container: HTMLElement, lang: 'en' | 'fr'): void {
  if (!window.JXG) return
  const t = i18n[lang]
  container.innerHTML = `
    <div class="widget-header">
      <span class="widget-tag">INTERACTIVE</span>
      <h4 class="widget-title">${t.instructions}</h4>
    </div>
    <div class="widget-slot"></div>
    <div id="jxg-newton" class="jxg-board" style="width:100%;height:380px;"></div>
  `
  const panel = createControlPanel(container.querySelector('.widget-slot') as HTMLElement)
  const x0Slider = createHtmlSlider({
    parent: panel, label: 'starting x', min: 0.5, max: 3.8, step: 0.1, value: 3.0,
    formatValue: v => v.toFixed(2),
  })

  const board = window.JXG.JSXGraph.initBoard('jxg-newton', {
    boundingbox: [-0.5, 14, 4, -10],
    axis: true, grid: true, showCopyright: false, showNavigation: false,
  })
  board.create('functiongraph', [f, 0.1, 3.6], { strokeColor: WIDGET_COLORS.brand, strokeWidth: 3 })

  let dots: ReturnType<typeof board.create>[] = []
  let tangents: ReturnType<typeof board.create>[] = []
  let vlines: ReturnType<typeof board.create>[] = []

  const redraw = () => {
    dots.forEach(d => board.removeObject(d as never))
    tangents.forEach(s => board.removeObject(s as never))
    vlines.forEach(s => board.removeObject(s as never))
    dots = []; tangents = []; vlines = []

    let x = x0Slider.getValue()
    const N_ITER = 4
    for (let i = 0; i < N_ITER; i++) {
      const fx = f(x)
      const slope = fp(x)
      if (Math.abs(slope) < 1e-9) break
      const xNext = x - fx / slope

      dots.push(board.create('point', [x, fx], {
        size: 4, fillColor: WIDGET_COLORS.amber, strokeColor: '#fff',
        fixed: true, withLabel: false, highlight: false,
      }))
      vlines.push(board.create('segment', [[x, 0], [x, fx]], {
        strokeColor: WIDGET_COLORS.amber, strokeWidth: 1.5, dash: 2,
        fixed: true, highlight: false,
      }))
      const xLeft = Math.max(-0.4, xNext - 0.5)
      const xRight = x + 0.3
      tangents.push(board.create('segment',
        [[xLeft, slope * (xLeft - x) + fx], [xRight, slope * (xRight - x) + fx]],
        {
          strokeColor: i === N_ITER - 1 ? WIDGET_COLORS.green : WIDGET_COLORS.red,
          strokeWidth: 2, fixed: true, highlight: false,
        },
      ))
      dots.push(board.create('point', [xNext, 0], {
        size: 3.5,
        fillColor: i === N_ITER - 1 ? WIDGET_COLORS.green : WIDGET_COLORS.amber,
        strokeColor: '#fff', fixed: true, withLabel: false, highlight: false,
      }))
      x = xNext
    }
    board.update()
  }
  x0Slider.setOnInput(redraw)
  redraw()
}
