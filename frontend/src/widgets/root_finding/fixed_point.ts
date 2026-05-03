/**
 * Fixed-point iteration : HTML slider for the starting x. The cobweb
 * diagram traces the iteration path on g(x) = cos(x).
 */
import { WIDGET_COLORS, createControlPanel, createHtmlSlider } from '../shared'

const g = (x: number): number => Math.cos(x)

const i18n = {
  en: { instructions: 'Drag the starting x. Cobweb traces the iteration path.' },
  fr: { instructions: 'Deplace le x de depart. Le cobweb trace les iterations.' },
}

export function mountFixedPointWidget(container: HTMLElement, lang: 'en' | 'fr'): void {
  if (!window.JXG) return
  const t = i18n[lang]
  container.innerHTML = `
    <div class="widget-header">
      <span class="widget-tag">INTERACTIVE</span>
      <h4 class="widget-title">${t.instructions}</h4>
    </div>
    <div class="widget-slot"></div>
    <div id="jxg-fixedpoint" class="jxg-board" style="width:100%;height:380px;"></div>
  `
  const panel = createControlPanel(container.querySelector('.widget-slot') as HTMLElement)
  const slider = createHtmlSlider({
    parent: panel, label: 'starting x', min: 0.0, max: 1.4, step: 0.05, value: 0.2,
    formatValue: v => v.toFixed(2),
  })

  const board = window.JXG.JSXGraph.initBoard('jxg-fixedpoint', {
    boundingbox: [-0.2, 1.5, 1.5, -0.2],
    axis: true, grid: true, showCopyright: false, showNavigation: false,
  })
  board.create('functiongraph', [g, -0.1, 1.4], { strokeColor: WIDGET_COLORS.brand, strokeWidth: 3 })
  board.create('functiongraph', [(x: number) => x, -0.1, 1.4],
    { strokeColor: WIDGET_COLORS.amber, strokeWidth: 2 })

  let segs: ReturnType<typeof board.create>[] = []
  const redraw = () => {
    segs.forEach(s => board.removeObject(s as never))
    segs = []
    let x = slider.getValue()
    for (let i = 0; i < 9; i++) {
      const y = g(x)
      const fromY = i === 0 ? 0 : x
      segs.push(board.create('segment', [[x, fromY], [x, y]], {
        strokeColor: '#000', strokeWidth: 1.5, fixed: true, highlight: false,
      }))
      segs.push(board.create('segment', [[x, y], [y, y]], {
        strokeColor: '#000', strokeWidth: 1.5, fixed: true, highlight: false,
      }))
      x = y
    }
    segs.push(board.create('point', [x, x], {
      size: 5, fillColor: WIDGET_COLORS.green, strokeColor: '#fff',
      withLabel: false, fixed: true, highlight: false,
    }))
    board.update()
  }
  slider.setOnInput(redraw)
  redraw()
}
