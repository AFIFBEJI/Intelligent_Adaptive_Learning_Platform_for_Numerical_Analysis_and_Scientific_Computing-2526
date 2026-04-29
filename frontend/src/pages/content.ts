// ============================================================
// Content Page — Multi-Level Content Viewer + KaTeX
// ============================================================

import { api, Concept } from '../api'
import { createAppShell } from '../components/app-shell'
import { t } from '../i18n'

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
    pageSubtitle: 'Multi-level lessons with mathematical notation',
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
        background:linear-gradient(135deg,#f1f5f9 0%,#38bdf8 50%,#818cf8 100%);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:0.4rem;
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
      .concept-item.active { background:rgba(20,184,166,0.1);color:var(--brand-500);font-weight:800; }
      .concept-dot {
        width:8px;height:8px;border-radius:50%;flex-shrink:0;
        background:var(--bg-surface-3);transition:background 0.2s;
      }
      .concept-item.active .concept-dot { background:var(--brand-500);box-shadow:0 0 0 3px rgba(20,184,166,0.14); }

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
      .level-tab.active { border-color:var(--border-emphasis);color:var(--brand-500);background:rgba(20,184,166,0.1); }
      .level-tab.simplified.active { background:var(--success-bg);color:var(--success);border-color:var(--success-border); }
      .level-tab.standard.active { background:rgba(20,184,166,0.1);color:var(--brand-500);border-color:var(--border-emphasis); }
      .level-tab.rigorous.active { background:rgba(124,58,237,0.09);color:var(--accent-purple);border-color:rgba(124,58,237,0.22); }

      .content-title { font-size:1.3rem;font-weight:800;color:var(--text-primary);margin-bottom:1.5rem; }

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
        background:rgba(20,184,166,0.08);color:var(--brand-500);
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
        background:rgba(20,184,166,0.08);color:var(--brand-500);
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
        <h1 class="page-title">Course Content</h1>
        <p class="page-sub">Multi-level educational content with simplified, standard, and rigorous explanations.</p>
      </div>

      <div class="content-layout">
        <div class="sidebar" id="sidebar">
          <div class="sidebar-title">CONCEPTS</div>
          ${[1,2,3,4,5,6,7,8].map(_ => `<div class="sk-sidebar"></div>`).join('')}
        </div>

        <div class="content-area" id="content-area">
          <div class="empty-content">
            <p>Select a concept from the sidebar to view its content</p>
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

  const renderMarkdown = (md: string): string => {
    let html = md
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

    return html
  }

  const loadContent = async (conceptId: string, level: string) => {
    activeLevel = level

    sidebar.querySelectorAll('.concept-item').forEach(el => el.classList.remove('active'))
    sidebar.querySelector(`[data-id="${conceptId}"]`)?.classList.add('active')

    contentArea.innerHTML = `<div class="empty-content"><p>Loading content...</p></div>`

    try {
      const data: ContentItem[] = await api.getConceptContent(conceptId, level)

      const currentContent = data.find(c => c.level === level) || data[0]
      if (!currentContent) throw new Error('No content')

      contentArea.innerHTML = `
        <div class="level-tabs">
          ${(['simplified','standard','rigorous'] as const).map(l => `
            <button class="level-tab ${l} ${l === level ? 'active' : ''}" data-level="${l}">
              ${l === 'simplified' ? 'Simplified' : l === 'standard' ? 'Standard' : 'Rigorous'}
            </button>
          `).join('')}
        </div>
        <div class="content-title">${currentContent.title}</div>
        <div class="content-body" id="math-content">${renderMarkdown(currentContent.body)}</div>
      `

      setTimeout(() => {
        const mathEl = contentArea.querySelector('#math-content')
        if (mathEl) renderMathIn(mathEl as HTMLElement)
      }, 150)

      contentArea.querySelectorAll('.level-tab').forEach(tab => {
        tab.addEventListener('click', () => {
          loadContent(conceptId, (tab as HTMLElement).dataset.level || 'standard')
        })
      })

    } catch {
      contentArea.innerHTML = `
        <div class="level-tabs">
          ${(['simplified','standard','rigorous'] as const).map(l => `
            <button class="level-tab ${l} ${l === level ? 'active' : ''}" data-level="${l}">
              ${l === 'simplified' ? 'Simplified' : l === 'standard' ? 'Standard' : 'Rigorous'}
            </button>
          `).join('')}
        </div>
        <div class="empty-content">
          <p>No content available. Run <code>python scripts/seed_content.py</code></p>
        </div>
      `
      contentArea.querySelectorAll('.level-tab').forEach(tab => {
        tab.addEventListener('click', () => loadContent(conceptId, (tab as HTMLElement).dataset.level || 'standard'))
      })
    }
  }

  api.getConcepts().then((concepts: Concept[]) => {
    const grouped: Record<string, Concept[]> = {}
    concepts.forEach(c => {
      const cat = c.category || 'Other'
      if (!grouped[cat]) grouped[cat] = []
      grouped[cat].push(c)
    })

    sidebar.innerHTML = `<div class="sidebar-title">CONCEPTS</div>` +
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

    if (concepts.length > 0) loadContent(concepts[0].id, 'standard')
  }).catch(() => {
    sidebar.innerHTML = `<div class="sidebar-title">CONCEPTS</div><div style="padding:1rem;color:#475569;font-size:0.8rem;">Backend not connected</div>`
  })

  shell.setContent(container)
  return shell.element
}
