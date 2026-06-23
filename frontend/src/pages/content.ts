// ============================================================
// Content Page — Multi-Level Content Viewer + KaTeX
// ============================================================

import { api, Concept } from '../api'
import { createAppShell } from '../components/app-shell'
import { studyFlowHtml } from '../components/study-flow'
import { getLang, t } from '../i18n'
import { router } from '../router'
import { hasGuided, mountGuided } from '../widgets/guided'

interface ContentItem {
  id: string
  level: string
  title: string
  body: string
}

// Load KaTeX dynamically
function loadKaTeX(): Promise<void> {
  return new Promise((resolve) => {
    if (document.querySelector('link[href*="katex"]')) { resolve(); return }

    const css = document.createElement('link')
    css.rel = 'stylesheet'
    css.href = 'https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css'
    document.head.appendChild(css)

    const js = document.createElement('script')
    js.src = 'https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js'
    js.onload = () => {
      const autoRender = document.createElement('script')
      autoRender.src = 'https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js'
      autoRender.onload = () => resolve()
      document.head.appendChild(autoRender)
    }
    document.head.appendChild(js)
  })
}

function renderMathIn(element: HTMLElement) {
  if ((window as any).renderMathInElement) {
    (window as any).renderMathInElement(element, {
      delimiters: [
        { left: '$$', right: '$$', display: true },
        { left: '$', right: '$', display: false },
        { left: '\\[', right: '\\]', display: true },
        { left: '\\(', right: '\\)', display: false },
      ],
      throwOnError: false,
    })
  }
}

export function ContentPage(): HTMLElement {
  const shell = createAppShell({
    activeRoute: '/content',
    pageTitle: t('sidebar.content'),
    pageSubtitle: t('content.subtitle'),
  })
  const container = document.createElement('div')
  const token = localStorage.getItem('token')
  if (token) api.setToken(token)

  const main = document.createElement('div')
  main.innerHTML = `
    <style>
      @keyframes slideUp { from{opacity:0;transform:translateY(25px)} to{opacity:1;transform:translateY(0)} }
      @keyframes fadeIn { from{opacity:0} to{opacity:1} }
      @keyframes shimmer { 0%{background-position:-200% 0} 100%{background-position:200% 0} }

      .content-page { max-width:1200px;margin:0 auto;padding:2rem;position:relative;z-index:1; }
      .content-flow-slot { margin-bottom: var(--space-5); }
      .page-header { margin-bottom:2rem;animation:slideUp 0.5s ease; }
      .page-title {
        font-size:2rem;font-weight:900;
        color:var(--text-primary);margin-bottom:0.4rem;
      }
      .page-sub { color:#64748b;font-size:0.9rem; }

      .content-layout { display:grid;grid-template-columns:300px 1fr;gap:var(--space-5);animation:slideUp 0.5s 0.1s ease both; }
      @media(max-width:768px){ .content-layout{grid-template-columns:1fr;} }

      .sidebar {
        background:var(--bg-surface);border:1px solid var(--border-default);
        border-radius:var(--radius-md);padding:var(--space-3);box-shadow:var(--shadow-sm);
        max-height:calc(100vh - 160px);overflow-y:auto;
      }
      .sidebar::-webkit-scrollbar { width:4px; }
      .sidebar::-webkit-scrollbar-track { background:transparent; }
      .sidebar::-webkit-scrollbar-thumb { background:rgba(255,255,255,0.1);border-radius:2px; }
      .sidebar-title { font-size:0.75rem;font-weight:800;color:var(--text-muted);letter-spacing:0.08em;padding:0.5rem 0.75rem;margin-bottom:0.25rem; }

      .concept-item {
        display:flex;align-items:center;gap:0.6rem;
        padding:0.65rem 0.75rem;border-radius:var(--radius-md);cursor:pointer;
        transition:all 0.2s;margin-bottom:2px;
        color:var(--text-secondary);font-size:0.82rem;font-weight:600;
      }
      .concept-item:hover { background:var(--bg-surface-hover);color:var(--text-primary); }
      .concept-item.active { background:rgba(15,118,110,0.1);color:var(--brand-600);font-weight:800; }
      .concept-dot {
        width:8px;height:8px;border-radius:50%;flex-shrink:0;
        background:var(--bg-surface-3);transition:background 0.2s;
      }
      .concept-item.active .concept-dot { background:var(--brand-500);box-shadow:0 0 0 3px rgba(15,118,110,0.14); }

      .module-label {
        font-size:0.68rem;font-weight:800;color:var(--text-muted);letter-spacing:0.06em;
        padding:0.75rem 0.75rem 0.3rem;margin-top:0.5rem;
      }

      .content-area {
        background:var(--bg-surface);border:1px solid var(--border-default);
        border-radius:var(--radius-md);padding:var(--space-6);box-shadow:var(--shadow-sm);min-height:520px;
        overflow-x:auto;
      }

      .level-tabs {
        display:flex;gap:0.5rem;margin-bottom:1.5rem;padding-bottom:1rem;
        border-bottom:1px solid var(--border-subtle);
      }
      .level-tab {
        padding:0.5rem 1.2rem;border-radius:var(--radius-md);
        border:1px solid var(--border-default);
        background:var(--bg-surface);color:var(--text-muted);font-size:0.8rem;font-weight:800;
        cursor:pointer;transition:all 0.25s;
      }
      .level-tab:hover { border-color:var(--border-emphasis);color:var(--text-primary);background:var(--bg-surface-hover); }
      .level-tab.active { border-color:var(--border-emphasis);color:var(--brand-600);background:rgba(15,118,110,0.1); }
      .level-tab.simplified.active { background:var(--success-bg);color:var(--success);border-color:var(--success-border); }
      .level-tab.standard.active { background:rgba(15,118,110,0.1);color:var(--brand-600);border-color:var(--border-emphasis); }
      .level-tab.rigorous.active { background:rgba(183,121,31,0.1);color:var(--accent-amber);border-color:rgba(183,121,31,0.24); }

      .content-title { font-size:1.3rem;font-weight:800;color:var(--text-primary);margin-bottom:1.5rem; }

      /* ============================================================
         "Demander au tuteur" : action bar at the top of the content
         ============================================================
         The button opens the Tutor page with:
           - the current concept pre-selected (parameter ?concept=...)
           - a pre-filled question (parameter ?prefill=...)
         See tutor.ts for the receiving-side logic. */
      .content-action-row {
        display:flex;align-items:flex-start;justify-content:space-between;
        gap:1rem;margin-bottom:1rem;
      }
      .content-title-block { flex:1;min-width:0; }
      .content-title-block .content-title { margin-bottom:0.4rem; }
      .content-title-block .content-title-hint {
        margin:0;color:var(--text-muted);font-size:0.78rem;line-height:1.5;
      }
      .ask-tutor-btn {
        display:inline-flex;align-items:center;gap:0.5rem;
        padding:0.6rem 1rem;border-radius:var(--radius-md);
        background:var(--brand-gradient);
        color:var(--text-on-inverse);
        border:1px solid rgba(15,118,110,0.35);
        font-weight:700;font-size:0.82rem;cursor:pointer;
        white-space:nowrap;flex-shrink:0;
        transition:all 0.25s;
        box-shadow:var(--shadow-sm);
      }
      .ask-tutor-btn:hover {
        transform:translateY(-2px);
        box-shadow:var(--shadow-glow-brand);
      }
      .ask-tutor-btn:active { transform:translateY(0); }
      .ask-tutor-btn svg { width:16px;height:16px; }
      @media(max-width:560px) {
        .content-action-row { flex-direction:column;align-items:stretch; }
        .ask-tutor-btn { width:100%;justify-content:center; }
      }

      /* (13/05/2026 #5) Toolbar of cross-links under the title:
         "Take quiz on this concept" + prereqs disclosure + Desmos preset.
         Makes the cross-cutting links VISIBLE (without them, the student
         must go back through /path or /quiz-ai to practice the concept). */
      .concept-cross-links {
        display: flex; flex-wrap: wrap; align-items: center;
        gap: 12px; margin: 0 0 1.4rem;
        padding: 12px 14px;
        background: rgba(15,118,110,0.04);
        border: 1px solid rgba(15,118,110,0.14);
        border-radius: 10px;
      }
      .ccl-quiz-btn {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 8px 14px; border-radius: var(--radius-md);
        background: var(--brand-gradient); color: var(--text-on-inverse);
        font-weight: 700; font-size: 0.85rem; text-decoration: none;
        transition: transform 0.15s, box-shadow 0.15s;
      }
      .ccl-quiz-btn:hover { transform: translateY(-1px); box-shadow: var(--shadow-glow-brand); }
      .ccl-prereqs { flex: 1; min-width: 0; font-size: 0.82rem; color: var(--text-muted); }
      .ccl-prereqs summary {
        cursor: pointer; color: var(--text-secondary); font-weight: 600;
        list-style: none; user-select: none;
      }
      .ccl-prereqs summary::before { content: '▸ '; color: var(--brand-500); }
      .ccl-prereqs[open] summary::before { content: '▾ '; }
      .ccl-prereqs-list {
        margin: 8px 0 0; padding: 0; list-style: none;
        display: flex; flex-direction: column; gap: 4px;
      }
      .ccl-prereq-item {
        display: grid; grid-template-columns: 1fr auto;
        gap: 10px; padding: 4px 8px;
        background: rgba(255,255,255,0.02); border-radius: 6px;
        font-size: 0.78rem;
      }
      .ccl-prereq-item.ok { color: var(--success); }
      .ccl-prereq-item.todo { color: var(--warning); }
      .ccl-prereq-mastery { font-weight: 700; font-variant-numeric: tabular-nums; }

      /* ============================================================
         "Etape 1 - Visualiser" : compact button that opens the video in
         full screen (modal). Clean course page; the click is a deliberate
         choice; at the end of the video, a CTA to the course.
         ============================================================ */
      .video-cta-bar {
        display: flex; align-items: center; gap: 14px;
        margin: 0 0 1.4rem; padding: 12px 16px;
        border: 1px solid rgba(15,118,110,0.22); border-radius: 14px;
        background: linear-gradient(135deg, rgba(15,118,110,0.06), rgba(15,118,110,0.015));
      }
      .video-hero-badge {
        font-size: 0.68rem; font-weight: 800; letter-spacing: 0.08em;
        color: #0F766E; background: rgba(15,118,110,0.10);
        padding: 4px 10px; border-radius: 999px; text-transform: uppercase;
        white-space: nowrap;
      }
      .video-cta-text { flex: 1; min-width: 0; font-size: 0.86rem; color: var(--text-muted); }
      .video-cta-btn {
        display: inline-flex; align-items: center; gap: 10px;
        background: #0F766E; color: #fff; border: none; cursor: pointer;
        padding: 10px 20px; border-radius: 999px; font-weight: 700; font-size: 0.92rem;
        box-shadow: 0 6px 16px rgba(15,118,110,0.35);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        white-space: nowrap;
      }
      .video-cta-btn:hover { transform: translateY(-1px); box-shadow: 0 8px 20px rgba(15,118,110,0.45); }
      .video-cta-btn .play-ico {
        width: 26px; height: 26px; border-radius: 50%; background: rgba(255,255,255,0.18);
        display: inline-flex; align-items: center; justify-content: center; font-size: 0.8rem;
      }
      /* --- full screen modal ("cinema mode") --- */
      .video-modal {
        position: fixed; inset: 0; z-index: 1000; display: none;
        align-items: center; justify-content: center;
        background: rgba(5,8,14,0.82); backdrop-filter: blur(4px);
      }
      .video-modal.open { display: flex; }
      .video-modal-box {
        width: min(960px, 92vw);
        background: #0E1117; border-radius: 16px; padding: 16px;
        box-shadow: 0 24px 64px rgba(0,0,0,0.5);
      }
      .video-modal-head {
        display: flex; align-items: center; justify-content: space-between;
        margin: 0 2px 10px;
      }
      .video-modal-title { color: #ECEDEE; font-weight: 700; font-size: 0.98rem; margin: 0; }
      .video-modal-close {
        background: none; border: none; color: #9AA4B2; font-size: 1.4rem;
        cursor: pointer; line-height: 1; padding: 4px 8px;
      }
      .video-modal-close:hover { color: #fff; }
      .manim-player {
        width: 100%; max-height: 70vh; border-radius: 12px;
        background: #000; display: block;
      }
      .video-modal-after { display: none; margin-top: 12px; text-align: center; }
      .video-modal-after .btn-read {
        display: inline-flex; align-items: center; gap: 8px;
        background: #0F766E; color: #fff; border: none; cursor: pointer;
        padding: 10px 22px; border-radius: 10px; font-weight: 700; font-size: 0.92rem;
      }

      /* ============================================================
         Interactive JSXGraph widget: box similar to the Manim player
         but with an "INTERACTIVE" tag oriented toward action rather than
         video. The student can drag/drop points and see the curves
         recompute in real time.
         ============================================================ */
      .content-widget {
        margin: 0 0 1.4rem;
        padding: 16px 18px 14px;
        background: linear-gradient(135deg, rgba(15,118,110,0.05) 0%, rgba(245,158,11,0.03) 100%);
        border: 1px solid rgba(15,118,110,0.2);
        border-radius: 14px;
      }
      .widget-header {
        display: flex; align-items: center; gap: 10px;
        margin-bottom: 12px;
      }
      .widget-tag {
        display: inline-block;
        padding: 2px 9px;
        background: var(--brand-gradient, linear-gradient(135deg,#0f766e,#14b8a6));
        color: #fff;
        font-size: 0.62rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        border-radius: 6px;
      }
      .widget-title {
        margin: 0;
        font-size: 0.88rem;
        font-weight: 600;
        color: var(--text-primary);
      }
      .jxg-board {
        background: #fff;
        border-radius: 8px;
        border: 1px solid rgba(15,23,42,0.06);
        overflow: hidden;
      }
      .widget-formula {
        margin: 10px 4px 0;
        font-size: 0.84rem;
        font-family: 'Cambria Math', 'Latin Modern Math', Georgia, serif;
        color: var(--text-primary);
        font-weight: 600;
      }
      .widget-readouts {
        display: flex; flex-wrap: wrap; gap: 14px;
        margin-top: 10px;
        padding-top: 10px;
        border-top: 1px dashed rgba(15,118,110,0.18);
      }
      .widget-readout {
        font-size: 0.82rem;
        color: var(--text-secondary);
      }
      .widget-readout strong { color: var(--text-primary); }

      /* HTML slider panel above the JSXGraph board.
         Replaces the in-chart sliders that overlapped curves. */
      .widget-controls {
        display: flex; flex-wrap: wrap; gap: 14px 22px;
        margin-bottom: 12px;
        padding: 10px 14px;
        background: rgba(15,118,110,0.04);
        border: 1px solid rgba(15,118,110,0.14);
        border-radius: 8px;
      }
      .widget-slider { flex: 1; min-width: 200px; }
      .widget-slider label {
        display: flex; align-items: center; gap: 10px;
        cursor: pointer;
      }
      .widget-slider-name {
        font-size: 0.82rem;
        font-weight: 700;
        color: var(--text-primary);
        min-width: 24px;
      }
      .widget-slider input[type="range"] {
        flex: 1;
        accent-color: #0f766e;
        height: 6px;
        cursor: pointer;
      }
      .widget-slider-value {
        font-size: 0.82rem;
        font-weight: 700;
        color: #115e59;
        min-width: 44px;
        text-align: right;
        font-family: 'JetBrains Mono', 'Cascadia Mono', Consolas, monospace;
      }

      .content-body {
        color:var(--text-secondary);font-size:0.95rem;line-height:1.9;
        animation:fadeIn 0.3s ease;
      }
      .content-body h1 {
        font-size:1.4rem;font-weight:800;color:var(--text-primary);
        margin:2rem 0 1rem;line-height:1.3;
        padding-bottom:0.5rem;
        border-bottom:1px solid var(--border-subtle);
      }
      .content-body h1:first-child { margin-top:0; }
      .content-body h2 {
        font-size:1.15rem;font-weight:800;color:var(--text-primary);
        margin:1.5rem 0 0.75rem;
        display:flex;align-items:center;gap:0.5rem;
      }
      .content-body h2::before {
        content:'';width:3px;height:1.1em;border-radius:2px;
        background:var(--brand-500);flex-shrink:0;
      }
      .content-body h3 { font-size:1rem;font-weight:800;color:var(--text-secondary);margin:1.25rem 0 0.5rem; }
      .content-body p { margin-bottom:0.85rem; }
      .content-body strong { color:var(--brand-500);font-weight:800; }
      .content-body em { color:var(--accent-purple);font-style:italic; }
      .content-body code {
        background:rgba(15,118,110,0.08);color:var(--brand-600);
        padding:0.2rem 0.5rem;border-radius:6px;font-size:0.85rem;
        font-family:'Fira Code','Cascadia Code',monospace;
        border:1px solid rgba(15,118,110,0.12);
      }
      .content-body ul, .content-body ol { margin:0.75rem 0 1rem 1.5rem; }
      .content-body li { margin-bottom:0.4rem;color:var(--text-secondary); }
      .content-body li strong { color:var(--text-primary); }

      .content-body table { width:100%;border-collapse:collapse;margin:1.25rem 0;border-radius:12px;overflow:hidden; }
      .content-body th {
        padding:0.65rem 1rem;
        background:rgba(15,118,110,0.08);color:var(--brand-600);
        font-weight:700;font-size:0.78rem;letter-spacing:0.04em;
        text-align:left;border-bottom:2px solid rgba(15,118,110,0.15);
      }
      .content-body td {
        padding:0.6rem 1rem;border-bottom:1px solid var(--border-subtle);
        font-size:0.85rem;color:var(--text-secondary);
      }
      .content-body tr:hover td { background:var(--bg-surface-2); }

      .content-body .katex-display {
        margin:1.25rem 0;padding:1rem 1.5rem;
        background:var(--bg-surface-2);
        border:1px solid var(--border-default);
        border-radius:12px;overflow-x:auto;
        border-left:3px solid var(--brand-500);
      }
      .content-body .katex-display > .katex { text-align:center; }
      .content-body .katex { color:var(--text-primary);font-size:1.05em; }

      .empty-content {
        display:flex;flex-direction:column;align-items:center;justify-content:center;
        height:300px;color:var(--text-muted);text-align:center;
      }
      .empty-content .icon { display:none; }

      .sk-sidebar { height:30px;margin-bottom:4px;border-radius:10px;
        background:linear-gradient(90deg,rgba(148,163,184,0.12) 25%,rgba(148,163,184,0.22) 50%,rgba(148,163,184,0.12) 75%);
        background-size:200% 100%;animation:shimmer 1.5s infinite;
      }
    </style>

    <div class="content-page">
      <div class="content-flow-slot">
        ${studyFlowHtml('learn', { compact: true })}
      </div>

      <div class="page-header">
        <h1 class="page-title">${t('content.title')}</h1>
        <p class="page-sub">${t('content.intro')}</p>
      </div>

      <div class="content-layout">
        <div class="sidebar" id="sidebar">
          <div class="sidebar-title">${t('content.sidebar.title')}</div>
          ${[1,2,3,4,5,6,7,8].map(_ => `<div class="sk-sidebar"></div>`).join('')}
        </div>

        <div class="content-area" id="content-area">
          <div class="empty-content">
            <p>${t('content.empty.select')}</p>
          </div>
        </div>
      </div>
    </div>
  `

  container.appendChild(main)
  loadKaTeX()

  const sidebar = main.querySelector('#sidebar')!
  const contentArea = main.querySelector('#content-area')!

  let activeLevel = 'standard'
  // We keep the list of loaded concepts handy so we can resolve the
  // (readable) NAME from an id when building the prompt sent to the
  // Tutor. Without this we would send "concept_bissection" instead of
  // "Methode de bissection" in the pre-filled question.
  let conceptsCache: Concept[] = []

  const renderMarkdown = (md: string): string => {
    // WARNING: LaTeX contains special characters (`*`, `_`, `|`, `` ` ``)
    // that are ALSO Markdown markers. Without protection, the italic rule
    // /\*(.+?)\*/g eats the `*` in expressions like `p^*` or `\sigma^*`,
    // which breaks the formula. So we first extract the LaTeX blocks into
    // placeholders, apply the Markdown, then restore them.
    const latexBlocks: string[] = []
    const placeholder = (idx: number) => `LATEX${idx}`

    // 1. Capture $$...$$ (display math, non-greedy, multi-line).
    let protectedMd = md.replace(/\$\$([\s\S]+?)\$\$/g, (_match, body) => {
      const idx = latexBlocks.length
      latexBlocks.push(`$$${body}$$`)
      return placeholder(idx)
    })
    // 2. Capture $...$ (inline math, non-greedy, on a single line).
    protectedMd = protectedMd.replace(/\$([^\$\n]+?)\$/g, (_match, body) => {
      const idx = latexBlocks.length
      latexBlocks.push(`$${body}$`)
      return placeholder(idx)
    })

    let html = protectedMd
      .replace(/^### (.+)$/gm, '<h3>$1</h3>')
      .replace(/^## (.+)$/gm, '<h2>$1</h2>')
      .replace(/^# (.+)$/gm, '<h1>$1</h1>')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      .replace(/`(.+?)`/g, '<code>$1</code>')
      .replace(/^\- (.+)$/gm, '<li>$1</li>')

    html = html.replace(/(<li>.*?<\/li>\s*)+/gs, (match) => `<ul>${match}</ul>`)

    html = html.replace(/(\|.+\|[\r\n]+\|[-:|]+\|[\r\n]+((\|.+\|[\r\n]*)+))/g, (tableBlock) => {
      const rows = tableBlock.trim().split('\n').filter(r => r.trim())
      if (rows.length < 2) return tableBlock
      const headerCells = rows[0].split('|').filter(c => c.trim()).map(c => c.trim())
      const dataRows = rows.slice(2)
      let table = '<table><thead><tr>'
      headerCells.forEach(c => { table += `<th>${c}</th>` })
      table += '</tr></thead><tbody>'
      dataRows.forEach(row => {
        const cells = row.split('|').filter(c => c.trim()).map(c => c.trim())
        if (cells.length > 0) { table += '<tr>'; cells.forEach(c => { table += `<td>${c}</td>` }); table += '</tr>' }
      })
      table += '</tbody></table>'
      return table
    })

    html = html.replace(/\n\n+/g, '</p><p>')
    html = '<p>' + html + '</p>'
    html = html.replace(/<p>\s*<(h[123]|ul|ol|table|div)/g, '<$1')
    html = html.replace(/<\/(h[123]|ul|ol|table|div)>\s*<\/p>/g, '</$1>')
    html = html.replace(/<p>\s*<\/p>/g, '')

    // 3. Restore the LaTeX blocks intact so KaTeX/MathJax can render them.
    html = html.replace(/LATEX(\d+)/g, (_match, idx) => latexBlocks[Number(idx)] || '')

    return html
  }

  // We store the concept and the level in the query string. This lets the
  // page recover the same position after a language change (which re-renders
  // the page via router.navigate) or after an F5 reload.
  const updateUrl = (conceptId: string, level: string) => {
    const url = new URL(window.location.href)
    url.searchParams.set('concept', conceptId)
    url.searchParams.set('level', level)
    window.history.replaceState(null, '', url.toString())
  }

  const loadContent = async (conceptId: string, level: string) => {
    activeLevel = level
    updateUrl(conceptId, level)

    sidebar.querySelectorAll('.concept-item').forEach(el => el.classList.remove('active'))
    sidebar.querySelector(`[data-id="${conceptId}"]`)?.classList.add('active')

    contentArea.innerHTML = `<div class="empty-content"><p>Loading content...</p></div>`

    try {
      const data: ContentItem[] = await api.getConceptContent(conceptId, level)

      const currentContent = data.find(c => c.level === level) || data[0]
      if (!currentContent) throw new Error('No content')

      // We look up the readable name of the current concept for the Tutor prompt.
      // The content title (currentContent.title) is more precise than the
      // concept name (often identical but not always), so we prefer it.
      // Fallback: the concept name in the list, then the id.
      const conceptName = currentContent.title
        || conceptsCache.find(c => c.id === conceptId)?.name
        || conceptId
      // "Demander au tuteur" button: opens /tutor passing
      // ?concept=<id>&prefill=<pre-filled question>. On the tutor side, we
      // will automatically create a session and fill the textarea.
      const askPrompt = t('content.askTutor.prefill').replace('{concept}', conceptName)
      const askHref = `/tutor?from=content&concept=${encodeURIComponent(conceptId)}&prefill=${encodeURIComponent(askPrompt)}`

      contentArea.innerHTML = `
        <div class="level-tabs">
          ${(['simplified','standard','rigorous'] as const).map(l => `
            <button class="level-tab ${l} ${l === level ? 'active' : ''}" data-level="${l}">
              ${l === 'simplified' ? t('content.level.simplified') : l === 'standard' ? t('content.level.standard') : t('content.level.rigorous')}
            </button>
          `).join('')}
        </div>
        <div class="content-action-row">
          <div class="content-title-block">
            <div class="content-title">${currentContent.title}</div>
            <p class="content-title-hint">${t('content.askTutor.hint')}</p>
          </div>
          <button class="ask-tutor-btn" id="ask-tutor-btn" type="button"
                  data-href="${askHref}"
                  title="${t('content.askTutor.hint')}">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
            ${t('content.askTutor')}
          </button>
        </div>
        <!-- (13/05/2026 #5) Toolbar cross-links : quiz CTA + prereqs +
             Desmos. Sans ces liens, lire une fiche concept ne menait
             nulle part — ici on rend EXPLICITE qu'on peut le pratiquer,
             voir ce qu'il faut maitriser avant, et l'explorer en live. -->
        <div class="concept-cross-links">
          <a href="/quiz-ai?concept=${encodeURIComponent(conceptId)}" data-link class="ccl-quiz-btn">
            ${getLang() === 'fr' ? 'Faire un quiz sur ce concept' : 'Take a quiz on this concept'}
            <span aria-hidden="true">→</span>
          </a>
          <details class="ccl-prereqs" id="ccl-prereqs">
            <summary>${getLang() === 'fr' ? 'Voir les prerequis' : 'View prerequisites'}</summary>
            <ul class="ccl-prereqs-list" id="ccl-prereqs-list">
              <li class="ccl-prereq-item"><span>${getLang() === 'fr' ? 'Chargement...' : 'Loading...'}</span></li>
            </ul>
          </details>
        </div>
        <!-- "Etape 1" : bouton compact qui ouvre la video en plein ecran
             (modal). La page de cours reste epuree ; le play est un choix
             volontaire ; a la fin, CTA vers le cours. Si aucune video pour
             ce concept, la barre reste display:none. -->
        <div class="video-cta-bar" id="content-animation" style="display:none;">
          <span class="video-hero-badge">${getLang() === 'fr' ? 'Étape 1 · Visualiser' : 'Step 1 · Visualize'}</span>
          <span class="video-cta-text">${getLang() === 'fr' ? "Comprenez l'idée en 2 minutes avant de lire le cours." : 'Get the idea in 2 minutes before reading the lesson.'}</span>
          <button class="video-cta-btn" id="video-open-btn"><span class="play-ico">▶</span>${getLang() === 'fr' ? 'Regarder la vidéo' : 'Watch the video'}</button>
        </div>
        <div class="video-modal" id="video-modal">
          <div class="video-modal-box">
            <div class="video-modal-head">
              <p class="video-modal-title">${getLang() === 'fr' ? 'Vidéo du concept' : 'Concept video'}</p>
              <button class="video-modal-close" id="video-close-btn" aria-label="Close">✕</button>
            </div>
            <video playsinline controls preload="metadata" class="manim-player">
              <source id="content-animation-src" src="" type="video/mp4" />
            </video>
            <div class="video-modal-after" id="video-after">
              <button class="btn-read" id="video-read-btn">${getLang() === 'fr' ? 'Maintenant, lisez le cours ↓' : 'Now read the lesson ↓'}</button>
            </div>
          </div>
        </div>
        <!-- Widget interactif JSXGraph : drag points / sliders et voir les
             courbes se recalculer en live. Existe pour 4 concepts heros pour
             l'instant ; le slot reste vide pour les autres. -->
        ${hasGuided(conceptId) ? '<div class="content-widget" id="content-widget"></div>' : ''}
        <div class="content-body" id="math-content">${renderMarkdown(currentContent.body)}</div>
      `

      // Try to load the associated Manim animation. If it exists, we
      // display it at the top of the content. Otherwise, silent 404 and the
      // block stays hidden.
      api.getAnimationUrl(conceptId).then(url => {
        if (!url) return
        const wrap = contentArea.querySelector('#content-animation') as HTMLElement | null
        const src = contentArea.querySelector('#content-animation-src') as HTMLSourceElement | null
        const video = contentArea.querySelector('.video-modal video') as HTMLVideoElement | null
        if (!wrap || !src || !video) return
        src.src = url
        video.load()
        wrap.style.display = 'flex'

        // "Regarder la video" button -> full screen modal; CTA at the end.
        const modal = contentArea.querySelector('#video-modal') as HTMLElement | null
        const after = contentArea.querySelector('#video-after') as HTMLElement | null
        const openBtn = wrap.querySelector('#video-open-btn') as HTMLElement | null
        const closeBtn = contentArea.querySelector('#video-close-btn') as HTMLElement | null
        const readBtn = contentArea.querySelector('#video-read-btn') as HTMLElement | null
        if (!modal) return
        // position:fixed is trapped by an animated ancestor (transform via
        // the layout's slideUp animation): the modal showed up stuck inside
        // the panel. We move it to the body level (portal) for a true
        // full screen, cleaning up modals from a previous visit.
        document.body.querySelectorAll('.video-modal').forEach(m => { if (m !== modal) m.remove() })
        document.body.appendChild(modal)
        const openModal = () => {
          modal.classList.add('open')
          video.play().catch(() => { /* playback refused : controls remain */ })
        }
        const closeModal = () => {
          modal.classList.remove('open')
          video.pause()
        }
        const goToLesson = () => {
          closeModal()
          const body = contentArea.querySelector('#math-content') as HTMLElement | null
          body?.scrollIntoView({ behavior: 'smooth', block: 'start' })
        }
        openBtn?.addEventListener('click', openModal)
        closeBtn?.addEventListener('click', closeModal)
        modal.addEventListener('click', (e) => { if (e.target === modal) closeModal() })
        video.addEventListener('ended', () => {
          if (after) after.style.display = 'block'
        })
        readBtn?.addEventListener('click', goToLesson)
      }).catch(() => { /* silently ignore : not critical */ })

      // Interactive guided example: the student runs the method themselves
      // (question -> choice -> feedback -> visible effect on the graph).
      // Pure SVG engine, no external dependency (replaces JSXGraph).
      if (hasGuided(conceptId)) {
        const widgetContainer = contentArea.querySelector('#content-widget') as HTMLElement | null
        if (widgetContainer) {
          mountGuided(widgetContainer, conceptId, getLang())
        }
      }

      setTimeout(() => {
        const mathEl = contentArea.querySelector('#math-content')
        if (mathEl) renderMathIn(mathEl as HTMLElement)
      }, 150)

      contentArea.querySelectorAll('.level-tab').forEach(tab => {
        tab.addEventListener('click', () => {
          loadContent(conceptId, (tab as HTMLElement).dataset.level || 'standard')
        })
      })

      // Click on "Demander au tuteur" -> navigation to /tutor with
      // the query params. We use window.location.href to go through the
      // router which knows how to handle the parameters and history.
      const askBtn = contentArea.querySelector('#ask-tutor-btn') as HTMLButtonElement | null
      askBtn?.addEventListener('click', () => {
        const href = askBtn.dataset.href
        // SPA navigation : we go through the router to avoid a full
        // reload. The router only looks at pathname to match the route,
        // but it preserves the query string in the URL thanks to pushState.
        if (href) router.navigate(href)
      })

      // (13/05/2026 #5) Lazy load of the prereqs on the 1st open of <details>.
      // Cross-referenced with the user's mastery (best-effort via getLearningPath)
      // to show acquired/to work on. If fetch fails, we degrade
      // gracefully to a list of names only.
      const detailsEl = contentArea.querySelector('#ccl-prereqs') as HTMLDetailsElement | null
      const prereqsList = contentArea.querySelector('#ccl-prereqs-list') as HTMLElement | null
      if (detailsEl && prereqsList) {
        let loaded = false
        detailsEl.addEventListener('toggle', async () => {
          if (!detailsEl.open || loaded) return
          loaded = true
          const isFr = getLang() === 'fr'
          try {
            const prereqs = await api.getConceptPrerequisites(conceptId)
            if (prereqs.length === 0) {
              prereqsList.innerHTML = `<li class="ccl-prereq-item"><span>${isFr ? 'Aucun prerequis declare.' : 'No declared prerequisite.'}</span></li>`
              return
            }
            const masteryMap = new Map<string, number>()
            try {
              const userRaw = localStorage.getItem('user')
              const user = userRaw ? JSON.parse(userRaw) : null
              if (user?.id) {
                const path = await api.getLearningPath(user.id)
                path.concepts_to_improve.forEach((c) => masteryMap.set(c.id, c.mastery))
              }
            } catch {
              // Best-effort : we continue with an empty map.
            }
            prereqsList.innerHTML = prereqs.map((p) => {
              const m = masteryMap.get(p.id) ?? 0
              const ok = m >= 70
              const status = ok ? (isFr ? 'acquis' : 'mastered') : (isFr ? 'a travailler' : 'to work')
              return `<li class="ccl-prereq-item ${ok ? 'ok' : 'todo'}">
                <span>${p.name}</span>
                <span class="ccl-prereq-mastery">${m.toFixed(0)}% - ${status}</span>
              </li>`
            }).join('')
          } catch {
            prereqsList.innerHTML = `<li class="ccl-prereq-item"><span>${isFr ? 'Erreur de chargement.' : 'Loading error.'}</span></li>`
          }
        })
      }

    } catch {
      contentArea.innerHTML = `
        <div class="level-tabs">
          ${(['simplified','standard','rigorous'] as const).map(l => `
            <button class="level-tab ${l} ${l === level ? 'active' : ''}" data-level="${l}">
              ${l === 'simplified' ? t('content.level.simplified') : l === 'standard' ? t('content.level.standard') : t('content.level.rigorous')}
            </button>
          `).join('')}
        </div>
        <div class="empty-content">
          <p>${t('content.empty.run')}</p>
        </div>
      `
      contentArea.querySelectorAll('.level-tab').forEach(tab => {
        tab.addEventListener('click', () => loadContent(conceptId, (tab as HTMLElement).dataset.level || 'standard'))
      })
    }
  }

  api.getConcepts().then((concepts: Concept[]) => {
    conceptsCache = concepts
    const grouped: Record<string, Concept[]> = {}
    concepts.forEach(c => {
      const cat = c.category || 'Other'
      if (!grouped[cat]) grouped[cat] = []
      grouped[cat].push(c)
    })

    sidebar.innerHTML = `<div class="sidebar-title">${t('content.sidebar.title')}</div>` +
      Object.entries(grouped).map(([module, items]) => `
        <div class="module-label">${module.toUpperCase()}</div>
        ${items.map(c => `
          <div class="concept-item" data-id="${c.id}">
            <div class="concept-dot"></div>
            ${c.name}
          </div>
        `).join('')}
      `).join('')

    sidebar.querySelectorAll('.concept-item').forEach(item => {
      item.addEventListener('click', () => {
        const id = (item as HTMLElement).dataset.id
        if (id) loadContent(id, activeLevel)
      })
    })

    // Initial choice: we read the query string (?concept=...&level=...) if present.
    // Otherwise, first concept in the list with the standard level.
    const params = new URLSearchParams(window.location.search)
    const requestedConcept = params.get('concept')
    const requestedLevel = params.get('level')
    const validLevels = new Set(['simplified', 'standard', 'rigorous'])
    const initialLevel = requestedLevel && validLevels.has(requestedLevel) ? requestedLevel : 'standard'
    const initialConcept = requestedConcept && concepts.some(c => c.id === requestedConcept)
      ? requestedConcept
      : (concepts[0]?.id || null)

    if (initialConcept) loadContent(initialConcept, initialLevel)
  }).catch(() => {
    sidebar.innerHTML = `<div class="sidebar-title">${t('content.sidebar.title')}</div><div style="padding:1rem;color:#475569;font-size:0.8rem;">${t('content.error.backend')}</div>`
  })

  shell.setContent(container)
  return shell.element
}
