/**
 * Gradient descent : HTML sliders for starting point and learning rate
 * above the chart. Path of 8 iterations updates live.
 */
import { WIDGET_COLORS, createControlPanel, createHtmlSlider } from '../shared'

const loss = (x: number): number => (x - 2) ** 2 + 0.4
const grad = (x: number): number => 2 * (x - 2)

const i18n = {
  en: { instructions: 'Drag the starting point and the learning rate. Watch the path adapt.' },
  fr: { instructions: 'Deplace le point de depart et le taux d\'apprentissage.' },
}

export function mountGradientDescentWidget(container: HTMLElement, lang: 'en' | 'fr'): void {
  if (!window.JXG) return
  const t = i18n[lang]
  container.innerHTML = `
    <div class="widget-header">
      <span class="widget-tag">INTERACTIVE</span>
      <h4 class="widget-title">${t.instructions}</h4>
    </div>
    <div class="widget-slot"></div>
    <div id="jxg-grad" class="jxg-board" style="width:100%;height:380px;"></div>
  `
  const panel = createControlPanel(container.querySelector('.widget-slot') as HTMLElement)
  const startX = createHtmlSlider({
    parent: panel, label: 'starting x', min: -2, max: 4.5, step: 0.1, value: -1.5,
    formatValue: v => v.toFixed(2),
  })
  const lrSlider = createHtmlSlider({
    parent: panel, label: 'learning rate', min: 0.05, max: 0.6, step: 0.05, value: 0.30,
    formatValue: v => v.toFixed(2),
  })

  const board = window.JXG.JSXGraph.initBoard('jxg-grad', {
    boundingbox: [-3, 8, 6, -1],
    axis: true, grid: true, showCopyright: false, showNavigation: false,
  })
  board.create('functiongraph', [loss, -2.5, 5.5], { strokeColor: WIDGET_COLORS.brand, strokeWidth: 3 })

  let pathDots: ReturnType<typeof board.create>[] = []
  let pathSegs: ReturnType<typeof board.create>[] = []

  const redraw = () => {
    pathDots.forEach(d => board.removeObject(d as never))
    pathSegs.forEach(s => board.removeObject(s as never))
    pathDots = []; pathSegs = []

    let x = startX.getValue()
    const eta = lrSlider.getValue()
    const N_STEPS = 8

    let prev: [number, number] = [x, loss(x)]
    pathDots.push(board.create('point', prev, {
      size: 4, fillColor: WIDGET_COLORS.amber, strokeColor: '#fff',
      fixed: true, withLabel: false, highlight: false,
    }))

    for (let i = 0; i < N_STEPS; i++) {
      const xNext = x - eta * grad(x)
      const cur: [number, number] = [xNext, loss(xNext)]
      const isLast = i === N_STEPS - 1
      pathSegs.push(board.create('segment', [prev, cur], {
        strokeColor: WIDGET_COLORS.amber, strokeWidth: 2, dash: 2,
        fixed: true, highlight: false,
      }))
      pathDots.push(board.create('point', cur, {
        size: 4,
        fillColor: isLast ? WIDGET_COLORS.green : WIDGET_COLORS.amber,
        strokeColor: '#fff', fixed: true, withLabel: false, highlight: false,
      }))
      prev = cur
      x = xNext
    }
    board.update()
  }
  startX.setOnInput(redraw); lrSlider.setOnInput(redraw)
  redraw()
}
