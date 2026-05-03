// ============================================================
// Content Page — Multi-Level Content Viewer + KaTeX
// ============================================================

import { api, Concept } from '../api'
import { createAppShell } from '../components/app-shell'
import { getLang, t } from '../i18n'
import { router } from '../router'
import { hasWidget, mountWidget } from '../widgets'

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
         "Demander au tuteur" : barre d'action en haut du contenu
         ============================================================
         Le bouton ouvre la page Tuteur avec :
           - le concept courant pre-selectionne (parametre ?concept=...)
           - une question pre-remplie  (parametre ?prefill=...)
         Voir tutor.ts pour la logique cote reception. */
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

      /* ============================================================
         Lecteur Manim integre en haut du contenu d'un concept.
         Visible si une animation existe, joue automatiquement en boucle.
         ============================================================ */
      .content-animation {
        margin: 0 0 1.4rem;
        padding: 14px;
        background: linear-gradient(135deg, rgba(15,118,110,0.04) 0%, rgba(15,118,110,0.01) 100%);
        border: 1px solid rgba(15,118,110,0.18);
        border-radius: 14px;
      }
      .manim-player {
        width: 100%;
        max-height: 460px;
        border-radius: 10px;
        background: #000;
        box-shadow: 0 4px 14px rgba(15,23,42,0.10);
        display: block;
      }
      .manim-caption {
        margin: 8px 4px 0;
        font-size: 0.78rem;
        color: var(--text-muted);
        letter-spacing: 0.01em;
        font-style: italic;
      }

      /* ============================================================
         Widget JSXGraph interactif : encadre similaire au lecteur Manim
         mais avec un tag "INTERACTIVE" oriente action plutot que video.
         L'etudiant peut drag/drop des points et voir les courbes se
         recalculer en temps reel.
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
  // On garde la liste des concepts charges sous la main pour pouvoir
  // resoudre le NOM (lisible) a partir d'un id quand on construit le
  // prompt envoye au Tuteur. Sans ca on enverrait "concept_bissection"
  // au lieu de "Methode de bissection" dans la question pre-remplie.
  let conceptsCache: Concept[] = []

  const renderMarkdown = (md: string): string => {
    // ATTENTION : le LaTeX contient des caracteres speciaux (`*`, `_`, `|`, `` ` ``)
    // qui sont AUSSI des marqueurs Markdown. Sans protection, la regle italique
    // /\*(.+?)\*/g mange les `*` dans des expressions comme `p^*` ou `\sigma^*`,
    // ce qui casse la formule. On extrait donc d'abord les blocs LaTeX vers des
    // placeholders, on applique le Markdown, puis on les restitue.
    const latexBlocks: string[] = []
    const placeholder = (idx: number) => `LATEX${idx}`

    // 1. Capture $$...$$ (display math, non-glouton, multi-ligne).
    let protectedMd = md.replace(/\$\$([\s\S]+?)\$\$/g, (_match, body) => {
      const idx = latexBlocks.length
      latexBlocks.push(`$$${body}$$`)
      return placeholder(idx)
    })
    // 2. Capture $...$ (inline math, non-glouton, sur une ligne).
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

    // 3. Restitue les blocs LaTeX intacts pour que KaTeX/MathJax les rende.
    html = html.replace(/LATEX(\d+)/g, (_match, idx) => latexBlocks[Number(idx)] || '')

    return html
  }

  // On stocke le concept et le niveau dans la query string. Cela permet a la
  // page de retrouver la meme position apres un changement de langue (qui
  // re-rend la page via router.navigate) ou apres un rechargement F5.
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

      // On cherche le nom lisible du concept courant pour le prompt Tuteur.
      // Le titre du contenu (currentContent.title) est plus precis que le
      // nom du concept (souvent identique mais pas toujours), donc on le
      // privilegie. Fallback : le nom du concept dans la liste, puis l'id.
      const conceptName = currentContent.title
        || conceptsCache.find(c => c.id === conceptId)?.name
        || conceptId
      // Bouton "Demander au tuteur" : ouvre /tutor en passant
      // ?concept=<id>&prefill=<question pre-remplie>. Cote tuteur, on
      // creera automatiquement une session et on remplira le textarea.
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
        <!-- Animation Manim : toujours visible quand elle existe, lecture
             en boucle automatique pour que l'etudiant puisse la regarder
             plusieurs fois sans cliquer rejouer. L'attribut muted est
             obligatoire pour que les navigateurs autorisent l'autoplay
             sans clic. Si aucune video pour ce concept, le bloc reste
             display:none. -->
        <div class="content-animation" id="content-animation" style="display:none;">
          <video autoplay loop muted playsinline controls preload="metadata" class="manim-player">
            <source id="content-animation-src" src="" type="video/mp4" />
          </video>
          <p class="manim-caption">${t('content.animation.caption') || 'Visual explanation generated with Manim'}</p>
        </div>
        <!-- Widget interactif JSXGraph : drag points / sliders et voir les
             courbes se recalculer en live. Existe pour 4 concepts heros pour
             l'instant ; le slot reste vide pour les autres. -->
        ${hasWidget(conceptId) ? '<div class="content-widget" id="content-widget"></div>' : ''}
        <div class="content-body" id="math-content">${renderMarkdown(currentContent.body)}</div>
      `

      // Tente de charger l'animation Manim associee. Si elle existe, on
      // l'affiche en haut du contenu. Sinon, 404 silencieux et le bloc
      // reste cache.
      api.getAnimationUrl(conceptId).then(url => {
        if (!url) return
        const wrap = contentArea.querySelector('#content-animation') as HTMLElement | null
        const src = contentArea.querySelector('#content-animation-src') as HTMLSourceElement | null
        const video = wrap?.querySelector('video') as HTMLVideoElement | null
        if (!wrap || !src || !video) return
        src.src = url
        video.load()
        wrap.style.display = 'block'
      }).catch(() => { /* silently ignore : pas critique */ })

      // Widget JSXGraph interactif. mount() est synchrone : la lib JSXGraph
      // est chargee via CDN dans index.html, donc disponible des le premier
      // render. Si elle n'est pas encore prete (rare), on retry une fois.
      if (hasWidget(conceptId)) {
        const widgetContainer = contentArea.querySelector('#content-widget') as HTMLElement | null
        if (widgetContainer) {
          const tryMount = () => {
            if (window.JXG) {
              mountWidget(widgetContainer, conceptId, getLang())
            } else {
              setTimeout(tryMount, 200)
            }
          }
          tryMount()
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

      // Click sur "Demander au tuteur" -> navigation vers /tutor avec
      // les query params. On utilise window.location.href pour passer par
      // le routeur qui sait gerer les parametres et l'historique.
      const askBtn = contentArea.querySelector('#ask-tutor-btn') as HTMLButtonElement | null
      askBtn?.addEventListener('click', () => {
        const href = askBtn.dataset.href
        // SPA navigation : on passe par le routeur pour eviter un full
        // reload. Le routeur ne regarde que pathname pour matcher la route,
        // mais il preserve la query string dans l'URL grace a pushState.
        if (href) router.navigate(href)
      })

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

    // Choix initial : on lit la query string (?concept=...&level=...) si presente.
    // Sinon, premier concept de la liste avec le niveau standard.
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
