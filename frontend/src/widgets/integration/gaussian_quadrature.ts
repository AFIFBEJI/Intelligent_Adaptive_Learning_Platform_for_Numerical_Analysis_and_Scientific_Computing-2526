/**
 * Gaussian Quadrature : HTML slider for n (2..5) above the chart.
 * Optimal Gauss-Legendre node positions and approximation value.
 */
import { WIDGET_COLORS, createControlPanel, createHtmlSlider } from '../shared'

const f = (x: number): number => 0.6 + Math.cos(x) + 0.15 * x

const GL: Record<number, { t: number[]; w: number[] }> = {
  2: { t: [-0.5773502692, 0.5773502692], w: [1.0, 1.0] },
  3: { t: [-0.7745966692, 0.0, 0.7745966692], w: [0.5555555556, 0.8888888889, 0.5555555556] },
  4: { t: [-0.8611363116, -0.3399810436, 0.3399810436, 0.8611363116],
       w: [0.3478548451, 0.6521451549, 0.6521451549, 0.3478548451] },
  5: { t: [-0.9061798459, -0.5384693101, 0.0, 0.5384693101, 0.9061798459],
       w: [0.2369268851, 0.4786286705, 0.5688888889, 0.4786286705, 0.2369268851] },
}

function gaussInt(n: number, a: number, b: number): number {
  const { t, w } = GL[n]
  const c1 = (b - a) / 2, c2 = (a + b) / 2
  let s = 0
  for (let i = 0; i < t.length; i++) s += w[i] * f(c1 * t[i] + c2)
  return c1 * s
}

const i18n = {
  en: { instructions: 'Drag n. See Gauss-Legendre nodes shift to optimal positions.' },
  fr: { instructions: 'Deplace n. Les nœuds de Gauss-Legendre se placent automatiquement.' },
}

export function mountGaussianQuadratureWidget(container: HTMLElement, lang: 'en' | 'fr'): void {
  if (!window.JXG) return
  const t = i18n[lang]
  container.innerHTML = `
    <div class="widget-header">
      <span class="widget-tag">INTERACTIVE</span>
      <h4 class="widget-title">${t.instructions}</h4>
    </div>
    <div class="widget-slot"></div>
    <div id="jxg-gauss" class="jxg-board" style="width:100%;height:380px;"></div>
    <div class="widget-readouts">
      <span class="widget-readout"><strong>Gauss approx :</strong> <span id="gauss-approx">…</span></span>
    </div>
  `
  const panel = createControlPanel(container.querySelector('.widget-slot') as HTMLElement)
  const nSlider = createHtmlSlider({
    parent: panel, label: 'n (nodes)', min: 2, max: 5, step: 1, value: 3,
    formatValue: v => v.toFixed(0),
  })

  const board = window.JXG.JSXGraph.initBoard('jxg-gauss', {
    boundingbox: [-0.3, 3, 4.5, -0.5],
    axis: true, grid: true, showCopyright: false, showNavigation: false,
  })
  board.create('functiongraph', [f, 0, 4], { strokeColor: WIDGET_COLORS.brand, strokeWidth: 3 })

  let nodes: ReturnType<typeof board.create>[] = []
  const approxEl = container.querySelector('#gauss-approx') as HTMLElement

  const redraw = () => {
    nodes.forEach(p => board.removeObject(p as never))
    nodes = []
    const n = Math.round(nSlider.getValue())
    if (!GL[n]) return
    const a = 0, b = 4
    const c1 = (b - a) / 2, c2 = (a + b) / 2
    GL[n].t.forEach(ti => {
      const xi = c1 * ti + c2
      nodes.push(board.create('point', [xi, f(xi)], {
        size: 5, fillColor: WIDGET_COLORS.green, strokeColor: '#fff',
        withLabel: false, fixed: true, highlight: false,
      }))
      nodes.push(board.create('segment', [[xi, 0], [xi, f(xi)]], {
        strokeColor: WIDGET_COLORS.green, strokeWidth: 1.5, dash: 2,
        fixed: true, highlight: false,
      }))
    })
    if (approxEl) approxEl.textContent = `${gaussInt(n, a, b).toFixed(4)} (n=${n})`
    board.update()
  }
  nSlider.setOnInput(redraw)
  redraw()
}
