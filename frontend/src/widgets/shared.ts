/**
 * Shared constants & types used by every widget.
 *
 * IMPORTANT : this file MUST NOT import any widget module.
 * Widgets import from here, and `index.ts` imports widgets — putting
 * shared values here breaks the circular import that would otherwise
 * cause "Cannot access 'WIDGET_COLORS' before initialization".
 */

// Brand palette mirroring backend/manim_scenes/_base.py
export const WIDGET_COLORS = {
  brand: '#0F766E',
  brandLight: '#5EEAD4',
  amber: '#F59E0B',
  red: '#DC2626',
  green: '#10B981',
  textPrimary: '#0F172A',
  textMuted: '#64748B',
  gridLight: '#E2E8F0',
} as const

// JSXGraph global typing — minimal subset we use.
declare global {
  interface Window {
    JXG: {
      JSXGraph: {
        initBoard(id: string | HTMLElement, options: Record<string, unknown>): JsxBoard
        freeBoard(b: JsxBoard): void
      }
    }
  }
}

export interface JsxBoard {
  create(type: string, parents: unknown[], attributes?: Record<string, unknown>): JsxElement
  update(): void
  on(event: string, handler: (...args: unknown[]) => void): void
  off(event: string, handler: (...args: unknown[]) => void): void
  removeObject(el: JsxElement): void
}

export interface JsxElement {
  X(): number
  Y(): number
  setPosition?(method: number, coords: [number, number]): void
  Value?(): number
  on(event: string, handler: (...args: unknown[]) => void): void
}

// =============================================================
// HTML slider helper. We use real <input type="range"> above the
// JSXGraph board instead of JSXGraph's own slider, because the
// latter sits INSIDE the chart's coordinate system and overlaps
// the curves / axis labels. HTML sliders sit cleanly above the
// board, are accessible (keyboard/screen reader), and easier to
// style.
// =============================================================
export interface SliderHandle {
  input: HTMLInputElement
  getValue(): number
  setOnInput(fn: (v: number) => void): void
}

/**
 * Append a labeled range slider to `parent`. The current value is
 * shown to the right of the slider and updated live.
 */
export function createHtmlSlider(opts: {
  parent: HTMLElement
  label: string
  min: number
  max: number
  step: number
  value: number
  formatValue?: (v: number) => string
}): SliderHandle {
  const wrap = document.createElement('div')
  wrap.className = 'widget-slider'
  const labelEl = document.createElement('label')
  const labelText = document.createElement('span')
  labelText.className = 'widget-slider-name'
  labelText.textContent = opts.label
  const input = document.createElement('input')
  input.type = 'range'
  input.min = String(opts.min)
  input.max = String(opts.max)
  input.step = String(opts.step)
  input.value = String(opts.value)
  const valueEl = document.createElement('span')
  valueEl.className = 'widget-slider-value'
  const fmt = opts.formatValue || ((v: number) => v.toString())
  valueEl.textContent = fmt(opts.value)
  labelEl.appendChild(labelText)
  labelEl.appendChild(input)
  labelEl.appendChild(valueEl)
  wrap.appendChild(labelEl)
  opts.parent.appendChild(wrap)

  let userOnInput: (v: number) => void = () => {}
  input.addEventListener('input', () => {
    const v = parseFloat(input.value)
    valueEl.textContent = fmt(v)
    userOnInput(v)
  })

  return {
    input,
    getValue: () => parseFloat(input.value),
    setOnInput: (fn) => { userOnInput = fn },
  }
}

/**
 * Create the control panel container that holds HTML sliders.
 * Conventionally placed above the JSXGraph board.
 */
export function createControlPanel(parent: HTMLElement): HTMLElement {
  const panel = document.createElement('div')
  panel.className = 'widget-controls'
  parent.appendChild(panel)
  return panel
}
