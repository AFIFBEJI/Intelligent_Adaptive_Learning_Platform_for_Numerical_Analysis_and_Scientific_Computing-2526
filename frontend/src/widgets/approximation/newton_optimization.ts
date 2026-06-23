/**
 * Newton's method for optimization : HTML slider for starting x.
 * 4 Newton steps converge on the nearest local minimum.
 */
import { WIDGET_COLORS, createControlPanel, createHtmlSlider } from '../shared'

const fobj = (x: number): number => 0.25 * x ** 4 - 1.5 * x ** 2 + x + 3
const fp = (x: number): number => x ** 3 - 3 * x + 1
const fpp = (x: number): number => 3 * x ** 2 - 3

const i18n = {
  en: { instructions: 'Drag the starting x. Newton steps jump to the nearest minimum.' },
  fr: { instructions: 'Deplace le x de depart. Les pas sautent vers le minimum local.' },
}

export function mountNewtonOptimizationWidget(container: HTMLElement, lang: 'en' | 'fr'): void {
  if (!window.JXG) return
  const t = i18n[lang]
  container.innerHTML = `
    <div class="widget-header">
      <span class="widget-tag">INTERACTIVE</span>
      <h4 class="widget-title">${t.instructions}</h4>
    </div>
    <div class="widget-slot"></div>
    <div id="jxg-newopt" class="jxg-board" style="width:100%;height:380px;"></div>
  `
  const panel = createControlPanel(container.querySelector('.widget-slot') as HTMLElement)
  const slider = createHtmlSlider({
    parent: panel, label: 'starting x', min: -2.5, max: 2.5, step: 0.1, value: 2.4,
    formatValue: v => v.toFixed(2),
  })

  const board = window.JXG.JSXGraph.initBoard('jxg-newopt', {
    boundingbox: [-3, 7, 3, -1],
    axis: true, grid: true, showCopyright: false, showNavigation: false,
  })
  board.create('functiongraph', [fobj, -2.7, 2.7], { strokeColor: WIDGET_COLORS.brand, strokeWidth: 3 })

  let steps: ReturnType<typeof board.create>[] = []
  const redraw = () => {
    steps.forEach(s => board.removeObject(s as never))
    steps = []
    let x = slider.getValue()
    for (let i = 0; i < 4; i++) {
      const fxx = fpp(x)
      if (Math.abs(fxx) < 1e-9) break
      const xNext = x - fp(x) / fxx
      steps.push(board.create('point', [x, fobj(x)], {
        size: 4, fillColor: WIDGET_COLORS.amber, strokeColor: '#fff',
        withLabel: false, fixed: true, highlight: false,
      }))
      steps.push(board.create('segment', [[x, fobj(x)], [xNext, fobj(xNext)]], {
        strokeColor: WIDGET_COLORS.amber, strokeWidth: 1.5, dash: 2,
        fixed: true, highlight: false,
      }))
      x = xNext
    }
    steps.push(board.create('point', [x, fobj(x)], {
      size: 4.5, fillColor: WIDGET_COLORS.green, strokeColor: '#fff',
      withLabel: false, fixed: true, highlight: false,
    }))
    board.update()
  }
  slider.setOnInput(redraw)
  redraw()
}
