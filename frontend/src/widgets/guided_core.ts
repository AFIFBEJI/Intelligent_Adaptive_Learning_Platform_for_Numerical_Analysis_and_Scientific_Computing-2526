/**
 * Generic engine for guided examples ("guided worked examples").
 *
 * Pedagogical principle: link a mathematical concept -> application.
 * The equation/data are FIXED by the lesson. The student makes the
 * DECISIONS of the method (clickable choices or values to compute and
 * type) and SEES the immediate graphical effect of each decision.
 *
 * One concept = one GScript (sequence of GStep precomputed along the
 * correct path) + a summary screen (table of THEIR decisions).
 *
 * MANDATORY conventions for the scripts:
 *  - bilingual texts {en, fr}, WITHOUT accented characters (bare e, a, u)
 *  - all mathematical notation in LaTeX between $...$ (KaTeX rendering)
 *  - exact numbers, formatted via fmt()
 */

import { loadAndRender } from '../utils/latex'

export type Lang = 'en' | 'fr'
export interface Txt { en: string; fr: string }

export const TEAL = '#0F766E'
export const ORANGE = '#EA580C'
export const GREEN = '#15803D'
export const BLUE = '#2563EB'
export const PURPLE = '#7C3AED'
export const MUTED = '#64748B'

// ==================================================================
// Formatting + round ticks
// ==================================================================
export const fmt = (v: number, d = 4): string => {
  if (!isFinite(v)) return '?'
  let s = v.toFixed(d)
  if (s.includes('.')) s = s.replace(/0+$/, '').replace(/\.$/, '')
  return s === '-0' ? '0' : s
}

function niceTicks(min: number, max: number, target = 5): number[] {
  const span = max - min
  if (!(span > 0)) return []
  const raw = span / target
  const mag = Math.pow(10, Math.floor(Math.log10(raw)))
  const norm = raw / mag
  const step = (norm < 1.5 ? 1 : norm < 3 ? 2 : norm < 7 ? 5 : 10) * mag
  const out: number[] = []
  for (let v = Math.ceil(min / step - 1e-9) * step; v <= max + 1e-9; v += step) {
    out.push(Math.round(v * 1e9) / 1e9)
  }
  return out
}

// ==================================================================
// Plot specification (pure SVG, round ticks)
// ==================================================================
export interface PlotSpec {
  xMin: number; xMax: number
  yMin?: number; yMax?: number          // optional: otherwise auto from the curves/points
  fns?: { fn: (x: number) => number; color?: string; width?: number; dash?: string }[]
  interval?: [number, number]           // teal vertical band
  mid?: number                          // orange dashed line "m = ..."
  root?: number                         // green point on the axis
  points?: { x: number; y: number; color?: string; label?: string }[]
  segs?: { x1: number; y1: number; x2: number; y2: number; color?: string; dash?: string; width?: number }[]
  polys?: { pts: [number, number][]; fill?: string; opacity?: number; stroke?: string }[]
  vlines?: { x: number; color?: string; label?: string; dash?: string }[]
  marks?: { x: number; label: string; color?: string }[]   // point + label on the 1st curve
}

export function svgPlot(p: PlotSpec): string {
  const W = 640, H = 320, mL = 48, mR = 14, mT = 14, mB = 30
  const iw = W - mL - mR, ih = H - mT - mB

  // automatic y window: curves + points + polygons
  let yMin = p.yMin ?? Infinity
  let yMax = p.yMax ?? -Infinity
  if (p.yMin === undefined || p.yMax === undefined) {
    const ys: number[] = []
    for (const c of p.fns || []) {
      for (let i = 0; i <= 160; i++) {
        const y = c.fn(p.xMin + (p.xMax - p.xMin) * i / 160)
        if (isFinite(y) && Math.abs(y) < 1e4) ys.push(y)
      }
    }
    for (const pt of p.points || []) ys.push(pt.y)
    for (const pl of p.polys || []) for (const [, y] of pl.pts) ys.push(y)
    for (const sg of p.segs || []) { ys.push(sg.y1); ys.push(sg.y2) }
    if (ys.length) {
      ys.sort((a, b) => a - b)
      const lo = ys[Math.floor(ys.length * 0.02)]
      const hi = ys[Math.ceil(ys.length * 0.98) - 1]
      if (p.yMin === undefined) yMin = lo
      if (p.yMax === undefined) yMax = hi
    } else { yMin = -1; yMax = 1 }
  }
  if (yMin > -0.2) yMin = -0.2
  if (yMax < 0.2) yMax = 0.2
  const pad = (yMax - yMin) * 0.12
  yMin -= pad; yMax += pad

  const sx = (x: number) => mL + (x - p.xMin) / (p.xMax - p.xMin) * iw
  const sy = (y: number) => mT + (yMax - y) / (yMax - yMin) * ih
  const cl = (y: number) => Math.max(yMin, Math.min(yMax, y))
  let s = ''

  if (p.interval) {
    const [a, b] = p.interval
    s += `<rect x="${sx(a).toFixed(1)}" y="${mT}" width="${Math.max(sx(b) - sx(a), 0).toFixed(1)}" height="${ih}" fill="${TEAL}" opacity="0.10"/>`
    for (const v of [a, b]) {
      s += `<line x1="${sx(v).toFixed(1)}" y1="${mT}" x2="${sx(v).toFixed(1)}" y2="${mT + ih}" stroke="${TEAL}" stroke-width="2"/>`
      s += `<text x="${sx(v).toFixed(1)}" y="${H - 6}" text-anchor="middle" font-size="12" fill="${TEAL}" font-weight="700">${fmt(v)}</text>`
    }
  }

  for (const x of niceTicks(p.xMin, p.xMax)) {
    s += `<line x1="${sx(x).toFixed(1)}" y1="${mT}" x2="${sx(x).toFixed(1)}" y2="${mT + ih}" stroke="#E2E8F0" stroke-width="1"/>`
    const nearItv = p.interval && (Math.abs(x - p.interval[0]) < (p.xMax - p.xMin) * 0.04 || Math.abs(x - p.interval[1]) < (p.xMax - p.xMin) * 0.04)
    if (!nearItv) s += `<text x="${sx(x).toFixed(1)}" y="${H - 6}" text-anchor="middle" font-size="11" fill="${MUTED}">${fmt(x)}</text>`
  }
  for (const y of niceTicks(yMin, yMax, 4)) {
    s += `<line x1="${mL}" y1="${sy(y).toFixed(1)}" x2="${W - mR}" y2="${sy(y).toFixed(1)}" stroke="#EEF2F7" stroke-width="1"/>`
    s += `<text x="${mL - 6}" y="${(sy(y) + 4).toFixed(1)}" text-anchor="end" font-size="11" fill="${MUTED}">${fmt(y)}</text>`
  }

  if (yMin < 0 && yMax > 0) s += `<line x1="${mL}" y1="${sy(0).toFixed(1)}" x2="${W - mR}" y2="${sy(0).toFixed(1)}" stroke="${MUTED}" stroke-width="1.6"/>`
  s += `<line x1="${mL}" y1="${mT}" x2="${mL}" y2="${mT + ih}" stroke="${MUTED}" stroke-width="1.6"/>`

  // polygons (areas, Riemann rectangles, trapezoids) under the curves
  for (const pl of p.polys || []) {
    const pts = pl.pts.map(([x, y]) => `${sx(x).toFixed(1)},${sy(cl(y)).toFixed(1)}`).join(' ')
    s += `<polygon points="${pts}" fill="${pl.fill || TEAL}" opacity="${pl.opacity ?? 0.25}"${pl.stroke ? ` stroke="${pl.stroke}" stroke-width="1.5"` : ''}/>`
  }

  for (const c of p.fns || []) {
    let run: string[] = []
    const flush = () => {
      if (run.length > 1) s += `<polyline points="${run.join(' ')}" fill="none" stroke="${c.color || BLUE}" stroke-width="${c.width ?? 3}"${c.dash ? ` stroke-dasharray="${c.dash}"` : ''}/>`
      run = []
    }
    for (let i = 0; i <= 240; i++) {
      const x = p.xMin + (p.xMax - p.xMin) * i / 240
      const y = c.fn(x)
      if (!isFinite(y) || y < yMin - (yMax - yMin) || y > yMax + (yMax - yMin)) { flush(); continue }
      run.push(`${sx(x).toFixed(1)},${sy(cl(y)).toFixed(1)}`)
    }
    flush()
  }

  for (const sg of p.segs || []) {
    s += `<line x1="${sx(sg.x1).toFixed(1)}" y1="${sy(cl(sg.y1)).toFixed(1)}" x2="${sx(sg.x2).toFixed(1)}" y2="${sy(cl(sg.y2)).toFixed(1)}" stroke="${sg.color || ORANGE}" stroke-width="${sg.width ?? 2.5}"${sg.dash ? ` stroke-dasharray="${sg.dash}"` : ''}/>`
  }

  for (const vl of p.vlines || []) {
    s += `<line x1="${sx(vl.x).toFixed(1)}" y1="${mT}" x2="${sx(vl.x).toFixed(1)}" y2="${mT + ih}" stroke="${vl.color || MUTED}" stroke-width="2"${vl.dash ? ` stroke-dasharray="${vl.dash}"` : ''}/>`
    if (vl.label) s += `<text x="${sx(vl.x).toFixed(1)}" y="${mT + 14}" text-anchor="middle" font-size="12" fill="${vl.color || MUTED}" font-weight="700">${vl.label}</text>`
  }

  if (p.mid !== undefined) {
    s += `<line x1="${sx(p.mid).toFixed(1)}" y1="${mT}" x2="${sx(p.mid).toFixed(1)}" y2="${mT + ih}" stroke="${ORANGE}" stroke-width="2" stroke-dasharray="6 4"/>`
    s += `<text x="${sx(p.mid).toFixed(1)}" y="${mT + 14}" text-anchor="middle" font-size="12" fill="${ORANGE}" font-weight="700">m = ${fmt(p.mid)}</text>`
  }

  for (const pt of p.points || []) {
    const c = pt.color || BLUE
    s += `<circle cx="${sx(pt.x).toFixed(1)}" cy="${sy(cl(pt.y)).toFixed(1)}" r="5" fill="${c}"/>`
    if (pt.label) s += `<text x="${sx(pt.x).toFixed(1)}" y="${(sy(cl(pt.y)) - 10).toFixed(1)}" text-anchor="middle" font-size="12" fill="${c}" font-weight="600">${pt.label}</text>`
  }

  for (const mk of p.marks || []) {
    const c = mk.color || MUTED
    const f0 = p.fns && p.fns.length ? p.fns[0].fn : null
    const yv = f0 ? f0(mk.x) : 0
    if (!isFinite(yv)) continue
    const cy = sy(cl(yv))
    s += `<circle cx="${sx(mk.x).toFixed(1)}" cy="${cy.toFixed(1)}" r="5" fill="${c}"/>`
    s += `<text x="${sx(mk.x).toFixed(1)}" y="${(cy - 10).toFixed(1)}" text-anchor="middle" font-size="12" fill="${c}" font-weight="600">${mk.label}</text>`
  }

  if (p.root !== undefined) {
    s += `<circle cx="${sx(p.root).toFixed(1)}" cy="${sy(0).toFixed(1)}" r="6" fill="${GREEN}"/>`
  }
  return `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;display:block;">${s}</svg>`
}

// ==================================================================
// Scenario types
// ==================================================================
export interface GChoice {
  label: Txt
  correct: boolean
  feedback: Txt
  plot?: PlotSpec          // graphical effect of THIS choice (rendered on click)
}

export interface GInput {
  label: string            // e.g.: 'm =' (plain text to the left of the field)
  expected: number
  tol: number
  ok: Txt                  // success feedback
  hint: Txt                // 1st failure: formula reminder, NOT the value
  reveal: Txt              // 2nd failure: full computation with the value
  plotOnOk?: PlotSpec      // graph updated when the value is correct
}

export interface GStep {
  plot: PlotSpec
  instruction: Txt
  choice?: { prompt: Txt; choices: GChoice[] }
  input?: GInput
  // neither choice nor input -> simple "Continue"
}

export interface GDone {
  intro: Txt
  eqTex?: string                              // e.g.: 'f(x) = x^{2}-2'
  table?: { cols: Txt[]; rows: string[][] }   // cells: LaTeX $...$ allowed
  plot?: PlotSpec
  outro: Txt
}

export interface GScript {
  title: Txt
  steps: GStep[]
  done: GDone
}

// ==================================================================
// Shared styles
// ==================================================================
let stylesInjected = false
function injectStyles(): void {
  if (stylesInjected) return
  stylesInjected = true
  const st = document.createElement('style')
  st.textContent = `
    .gw-card { border:1px solid rgba(15,118,110,0.22); border-radius:16px; padding:16px 18px;
               background:linear-gradient(135deg, rgba(15,118,110,0.05), rgba(15,118,110,0.01));
               margin:0 0 1.4rem; }
    .gw-head { display:flex; align-items:center; gap:12px; margin-bottom:8px; flex-wrap:wrap; }
    .gw-badge { font-size:0.68rem; font-weight:800; letter-spacing:0.08em; color:#0F766E;
                background:rgba(15,118,110,0.10); padding:4px 10px; border-radius:999px; text-transform:uppercase; }
    .gw-title { flex:1; font-weight:700; color:#0F172A; font-size:0.98rem; }
    .gw-progress { font-size:0.78rem; color:#64748B; font-weight:600; white-space:nowrap; }
    .gw-bar { height:5px; border-radius:99px; background:rgba(15,118,110,0.12); margin-bottom:12px; overflow:hidden; }
    .gw-bar-fill { height:100%; background:#0F766E; border-radius:99px; transition:width 0.4s ease; }
    .gw-plot { border-radius:12px; overflow:hidden; background:#fff; border:1px solid #E2E8F0; }
    .gw-instruction { margin:12px 2px 4px; font-size:0.92rem; color:#0F172A; line-height:1.55; }
    .gw-inputs { display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin:10px 2px; }
    .gw-ilabel { font-weight:700; color:#0F172A; font-size:0.95rem; }
    .gw-input { border:1.5px solid rgba(15,118,110,0.35); border-radius:10px; padding:9px 12px;
                font-size:0.95rem; font-family:'JetBrains Mono','Consolas',monospace; width:130px; }
    .gw-input:focus { outline:none; border-color:#0F766E; box-shadow:0 0 0 3px rgba(15,118,110,0.12); }
    .gw-check-btn { background:#0F766E; color:#fff; border:none; cursor:pointer; padding:9px 18px;
                    border-radius:10px; font-weight:700; font-size:0.88rem; }
    .gw-question { margin:10px 2px 8px; font-size:0.92rem; font-weight:700; color:#0F766E; }
    .gw-choices { display:flex; flex-wrap:wrap; gap:10px; }
    .gw-choice { border:1.5px solid rgba(15,118,110,0.35); background:#fff; color:#0F172A;
                 padding:9px 16px; border-radius:10px; cursor:pointer; font-size:0.88rem; font-weight:600;
                 transition:all 0.15s ease; }
    .gw-choice:hover { border-color:#0F766E; transform:translateY(-1px); }
    .gw-choice.ok { background:#ECFDF5; border-color:#15803D; color:#15803D; }
    .gw-choice.ko { background:#FEF2F2; border-color:#DC2626; color:#DC2626; }
    .gw-feedback { min-height:1.2em; margin:10px 2px 0; font-size:0.86rem; line-height:1.5; }
    .gw-feedback.ok { color:#15803D; }
    .gw-feedback.ko { color:#B45309; }
    .gw-actions { margin-top:12px; text-align:right; }
    .gw-next { background:#0F766E; color:#fff; border:none; cursor:pointer; padding:9px 22px;
               border-radius:10px; font-weight:700; font-size:0.9rem; box-shadow:0 5px 14px rgba(15,118,110,0.3); }
    .gw-next:disabled { opacity:0.35; cursor:not-allowed; box-shadow:none; }
    .gw-eq-display { margin:8px 2px; font-size:1rem; color:#0F172A; }
    .gw-done-badge { display:inline-flex; align-items:center; gap:8px; background:#ECFDF5; color:#15803D;
                     font-weight:800; padding:8px 16px; border-radius:999px; margin-bottom:10px; }
    .gw-conclusion { font-size:0.94rem; color:#0F172A; line-height:1.6; margin:6px 2px 12px; }
    .gw-table { border-collapse:collapse; margin:10px 0 14px; font-size:0.88rem; }
    .gw-table th, .gw-table td { border:1px solid #CBD5E1; padding:6px 12px; text-align:center; color:#0F172A; }
    .gw-table th { background:rgba(15,118,110,0.08); color:#0F766E; }
    .gw-restart { background:none; border:1.5px solid rgba(15,118,110,0.4); color:#0F766E; cursor:pointer;
                  padding:8px 18px; border-radius:10px; font-weight:700; font-size:0.88rem; }
  `
  document.head.appendChild(st)
}

// ==================================================================
// Generic rendering engine
// ==================================================================
const UI = {
  badge:    { en: 'Guided example', fr: 'Exemple guide' },
  step:     { en: 'Step', fr: 'Etape' },
  check:    { en: 'Check', fr: 'Verifier' },
  continue: { en: 'Continue &#8594;', fr: 'Continuer &#8594;' },
  finish:   { en: 'See my application', fr: 'Voir mon application' },
  done:     { en: 'Concept applied!', fr: 'Concept applique !' },
  restart:  { en: 'Redo the example', fr: 'Refaire l\'exemple' },
}

export function mountScript(container: HTMLElement, script: GScript, lang: Lang): void {
  injectStyles()
  const tr = (l: Txt) => (lang === 'fr' ? l.fr : l.en)
  const num = (raw: string): number => Number(raw.replace(',', '.').trim())
  const TOTAL = script.steps.length
  let idx = 0

  const shell = (stepNo: number, inner: string): string => `
    <div class="gw-card">
      <div class="gw-head">
        <span class="gw-badge">${tr(UI.badge)}</span>
        <span class="gw-title">${tr(script.title)}</span>
        <span class="gw-progress">${tr(UI.step)} ${Math.min(stepNo, TOTAL)}/${TOTAL}</span>
      </div>
      <div class="gw-bar"><div class="gw-bar-fill" style="width:${Math.min((stepNo - 1) / TOTAL, 1) * 100}%"></div></div>
      ${inner}
    </div>`

  const setFb = (cls: 'ok' | 'ko', html: string) => {
    const fb = container.querySelector('#gw-fb') as HTMLElement | null
    if (!fb) return
    fb.innerHTML = html
    fb.className = 'gw-feedback ' + cls
    void loadAndRender(fb)
  }
  const setPlot = (spec: PlotSpec) => {
    const el = container.querySelector('#gw-plot') as HTMLElement | null
    if (el) el.innerHTML = svgPlot(spec)
  }

  const renderDone = () => {
    const d = script.done
    const tableHtml = d.table ? `
      <table class="gw-table">
        <tr>${d.table.cols.map(c => `<th>${tr(c)}</th>`).join('')}</tr>
        ${d.table.rows.map(r => `<tr>${r.map(c => `<td>${c}</td>`).join('')}</tr>`).join('')}
      </table>` : ''
    container.innerHTML = shell(TOTAL + 1, `
      <div class="gw-done-badge">&#10003; ${tr(UI.done)}</div>
      <p class="gw-conclusion">${tr(d.intro)}</p>
      ${d.eqTex ? `<p class="gw-eq-display">$${d.eqTex}$</p>` : ''}
      ${tableHtml}
      ${d.plot ? `<div class="gw-plot">${svgPlot(d.plot)}</div>` : ''}
      <p class="gw-conclusion" style="margin-top:12px">${tr(d.outro)}</p>
      <button class="gw-restart" id="gw-restart">${tr(UI.restart)}</button>`)
    container.querySelector('#gw-restart')?.addEventListener('click', () => { idx = 0; render() })
    void loadAndRender(container)
  }

  const render = () => {
    const step = script.steps[idx]
    const isLast = idx === TOTAL - 1
    const nextLabel = isLast ? tr(UI.finish) : tr(UI.continue)
    const hasInteraction = !!(step.choice || step.input)

    let interaction = ''
    if (step.choice) {
      interaction = `
        <p class="gw-question">${tr(step.choice.prompt)}</p>
        <div class="gw-choices">
          ${step.choice.choices.map((c, i) => `<button class="gw-choice" data-i="${i}">${tr(c.label)}</button>`).join('')}
        </div>`
    } else if (step.input) {
      interaction = `
        <div class="gw-inputs">
          <span class="gw-ilabel">${step.input.label}</span>
          <input class="gw-input" id="gw-in" autocomplete="off" spellcheck="false">
          <button class="gw-check-btn" id="gw-in-btn">${tr(UI.check)}</button>
        </div>`
    }

    container.innerHTML = shell(idx + 1, `
      <div class="gw-plot" id="gw-plot">${svgPlot(step.plot)}</div>
      <p class="gw-instruction">${tr(step.instruction)}</p>
      ${interaction}
      <p class="gw-feedback" id="gw-fb"></p>
      <div class="gw-actions"><button class="gw-next" id="gw-next" ${hasInteraction ? 'disabled' : ''}>${nextLabel}</button></div>`)

    const next = container.querySelector('#gw-next') as HTMLButtonElement

    if (step.choice) {
      const ch = step.choice
      container.querySelectorAll('.gw-choice').forEach(btn => {
        btn.addEventListener('click', () => {
          const i = Number((btn as HTMLElement).dataset.i)
          const choice = ch.choices[i]
          container.querySelectorAll('.gw-choice').forEach(x => x.classList.remove('ok', 'ko'))
          btn.classList.add(choice.correct ? 'ok' : 'ko')
          if (choice.plot) setPlot(choice.plot)
          setFb(choice.correct ? 'ok' : 'ko', tr(choice.feedback))
          next.disabled = !choice.correct
        })
      })
    } else if (step.input) {
      const inp = step.input
      const el = container.querySelector('#gw-in') as HTMLInputElement
      let tries = 0
      const check = () => {
        const v = num(el.value)
        if (isFinite(v) && Math.abs(v - inp.expected) <= inp.tol) {
          if (inp.plotOnOk) setPlot(inp.plotOnOk)
          setFb('ok', tr(inp.ok))
          next.disabled = false
        } else {
          tries++
          setFb('ko', tries >= 2 ? tr(inp.reveal) : tr(inp.hint))
          next.disabled = true
        }
      }
      container.querySelector('#gw-in-btn')?.addEventListener('click', check)
      el.addEventListener('keydown', e => { if ((e as KeyboardEvent).key === 'Enter') check() })
    }

    next.addEventListener('click', () => {
      if (isLast) renderDone()
      else { idx++; render() }
    })
    void loadAndRender(container)
  }

  render()
}
