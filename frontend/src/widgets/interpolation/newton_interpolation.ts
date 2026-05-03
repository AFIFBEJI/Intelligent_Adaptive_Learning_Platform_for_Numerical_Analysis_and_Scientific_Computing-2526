/**
 * Newton Interpolation : drag points + HTML slider for "use N points"
 * to grow the polynomial degree incrementally.
 */
import { WIDGET_COLORS, createControlPanel, createHtmlSlider } from '../shared'

const i18n = {
  en: { instructions: 'Drag points OR change "use" to grow the polynomial degree.' },
  fr: { instructions: 'Deplace les points OU change "use" pour augmenter le degre du polynome.' },
}

function newtonEval(x: number, xs: number[], coeffs: number[]): number {
  let res = coeffs[coeffs.length - 1]
  for (let i = coeffs.length - 2; i >= 0; i--) res = res * (x - xs[i]) + coeffs[i]
  return res
}
function divDiffCoeffs(xs: number[], ys: number[]): number[] {
  const n = xs.length
  const dd: number[][] = ys.map(v => [v])
  for (let j = 1; j < n; j++) {
    for (let i = 0; i < n - j; i++) dd[i][j] = (dd[i + 1][j - 1] - dd[i][j - 1]) / (xs[i + j] - xs[i])
  }
  return dd[0]
}

export function mountNewtonInterpolationWidget(container: HTMLElement, lang: 'en' | 'fr'): void {
  if (!window.JXG) return
  const t = i18n[lang]
  container.innerHTML = `
    <div class="widget-header">
      <span class="widget-tag">INTERACTIVE</span>
      <h4 class="widget-title">${t.instructions}</h4>
    </div>
    <div class="widget-slot"></div>
    <div id="jxg-newton-interp" class="jxg-board" style="width:100%;height:380px;"></div>
  `
  const panel = createControlPanel(container.querySelector('.widget-slot') as HTMLElement)
  const useSlider = createHtmlSlider({
    parent: panel, label: 'use first N points', min: 2, max: 4, step: 1, value: 4,
    formatValue: v => v.toFixed(0),
  })

  const board = window.JXG.JSXGraph.initBoard('jxg-newton-interp', {
    boundingbox: [-0.5, 5, 5, -1],
    axis: true, grid: true, showCopyright: false, showNavigation: false,
  })

  const initial: [number, number][] = [[0, 1], [1, 3], [2.5, 0.5], [4, 3]]
  const points = initial.map(([x, y]) =>
    board.create('point', [x, y], {
      size: 5, fillColor: WIDGET_COLORS.amber, strokeColor: '#fff',
      withLabel: false,
    }),
  )

  board.create('functiongraph', [
    (x: number) => {
      const k = Math.round(useSlider.getValue())
      const xs = points.slice(0, k).map(p => p.X())
      const ys = points.slice(0, k).map(p => p.Y())
      const coeffs = divDiffCoeffs(xs, ys)
      return newtonEval(x, xs, coeffs)
    },
    -0.5, 5,
  ], { strokeColor: WIDGET_COLORS.brand, strokeWidth: 3 })

  useSlider.setOnInput(() => board.update())
}
