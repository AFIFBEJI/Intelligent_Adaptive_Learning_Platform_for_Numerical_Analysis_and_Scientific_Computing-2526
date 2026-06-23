/**
 * Simpson's Rule : HTML slider for N (must be even). Composite rule
 * with parabolas drawn live.
 */
import { WIDGET_COLORS, createControlPanel, createHtmlSlider } from '../shared'

const f = (x: number): number => 0.5 + 0.7 * Math.sin(0.9 * x) + 0.2 * x

const i18n = {
  en: { instructions: 'Drag the slider for N (must be even). Watch parabolas hug the curve.' },
  fr: { instructions: 'Deplace le curseur N (pair). Les paraboles epousent la courbe.' },
}

function trueInt(): number {
  const N = 5000, h = 4 / N
  let s = 0
  for (let i = 0; i < N; i++) s += f((i + 0.5) * h) * h
  return s
}
function simpsonComposite(n: number): number {
  if (n % 2 === 1) n += 1
  const a = 0, b = 4, h = (b - a) / n
  let s = f(a) + f(b)
  for (let i = 1; i < n; i++) s += f(a + i * h) * (i % 2 === 0 ? 2 : 4)
  return (h / 3) * s
}

export function mountSimpsonWidget(container: HTMLElement, lang: 'en' | 'fr'): void {
  if (!window.JXG) return
  const t = i18n[lang]
  container.innerHTML = `
    <div class="widget-header">
      <span class="widget-tag">INTERACTIVE</span>
      <h4 class="widget-title">${t.instructions}</h4>
    </div>
    <div class="widget-slot"></div>
    <div id="jxg-simpson" class="jxg-board" style="width:100%;height:380px;"></div>
    <div class="widget-readouts">
      <span class="widget-readout"><strong>Simpson :</strong> <span id="simp-approx">…</span></span>
      <span class="widget-readout"><strong>True :</strong> <span id="simp-true">…</span></span>
    </div>
  `
  const panel = createControlPanel(container.querySelector('.widget-slot') as HTMLElement)
  const nSlider = createHtmlSlider({
    parent: panel, label: 'N (subintervals, even)', min: 2, max: 20, step: 2, value: 4,
    formatValue: v => v.toFixed(0),
  })

  const board = window.JXG.JSXGraph.initBoard('jxg-simpson', {
    boundingbox: [-0.3, 3, 4.5, -0.5],
    axis: true, grid: true, showCopyright: false, showNavigation: false,
  })
  board.create('functiongraph', [f, 0, 4], { strokeColor: WIDGET_COLORS.brand, strokeWidth: 3 })

  let curves: ReturnType<typeof board.create>[] = []
  const approxEl = container.querySelector('#simp-approx') as HTMLElement
  const trueEl = container.querySelector('#simp-true') as HTMLElement
  if (trueEl) trueEl.textContent = trueInt().toFixed(4)

  const redraw = () => {
    curves.forEach(c => board.removeObject(c as never))
    curves = []
    let n = Math.round(nSlider.getValue())
    if (n % 2 === 1) n += 1
    const a = 0, b = 4, h = (b - a) / n
    for (let i = 0; i < n; i += 2) {
      const x0 = a + i * h, xm = a + (i + 1) * h, x1 = a + (i + 2) * h
      const y0 = f(x0), ym = f(xm), y1 = f(x1)
      const denom = (x0 - xm) * (x0 - x1) * (xm - x1)
      const A = (x1 * (ym - y0) + xm * (y0 - y1) + x0 * (y1 - ym)) / denom
      const B = (x1 ** 2 * (y0 - ym) + xm ** 2 * (y1 - y0) + x0 ** 2 * (ym - y1)) / denom
      const C = (xm * x1 * (xm - x1) * y0 + x1 * x0 * (x1 - x0) * ym + x0 * xm * (x0 - xm) * y1) / denom
      curves.push(board.create('functiongraph',
        [(x: number) => A * x * x + B * x + C, x0, x1],
        { strokeColor: WIDGET_COLORS.amber, strokeWidth: 2.5 }))
    }
    if (approxEl) approxEl.textContent = `${simpsonComposite(n).toFixed(4)} (N=${n})`
    board.update()
  }
  nSlider.setOnInput(redraw)
  redraw()
}
