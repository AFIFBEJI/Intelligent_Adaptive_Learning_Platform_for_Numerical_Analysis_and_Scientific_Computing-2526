// ============================================================
// Concepts Page
// ============================================================

import { api, Concept } from '../api'
import { createAppShell } from '../components/app-shell'
import { t } from '../i18n'

function escapeHtml(s: string): string {
  return (s || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

export function ConceptsPage(): HTMLElement {
  const shell = createAppShell({
    activeRoute: '/concepts',
    pageTitle: t('sidebar.concepts'),
    pageSubtitle: 'Knowledge graph and module structure',
  })
  const container = document.createElement('div')
  const token = localStorage.getItem('token')
  if (token) api.setToken(token)

  const main = document.createElement('div')
  main.innerHTML = `
    <style>
      @keyframes conceptIn { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }

      .concepts-page {
        display: flex;
        flex-direction: column;
        gap: var(--space-5);
        animation: conceptIn 0.35s ease both;
      }
      .concepts-toolbar {
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto;
        align-items: end;
        gap: var(--space-4);
        padding: var(--space-6);
        background:
          linear-gradient(180deg, rgba(15, 27, 45, 0.96), rgba(8, 18, 31, 0.94)),
          linear-gradient(135deg, rgba(56, 189, 248, 0.1), rgba(99, 102, 241, 0.06));
        border: 1px solid var(--border-default);
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-sm);
      }
      .concepts-toolbar-title {
        margin: 0;
        color: var(--text-primary);
        font-size: var(--text-3xl);
        font-weight: var(--font-weight-extrabold);
        line-height: var(--line-height-tight);
      }
      .concepts-toolbar-sub {
        margin: var(--space-2) 0 0;
        max-width: 620px;
        color: var(--text-muted);
        font-size: var(--text-sm);
        line-height: var(--line-height-relaxed);
      }
      .filter-bar {
        display: flex;
        gap: var(--space-2);
        flex-wrap: wrap;
        justify-content: flex-end;
      }
      .filter-chip {
        min-height: 36px;
        padding: 0.48rem 0.85rem;
        border: 1px solid var(--border-default);
        border-radius: var(--radius-md);
        color: var(--text-muted);
        background: rgba(148, 163, 184, 0.07);
        font-size: var(--text-sm);
        font-weight: var(--font-weight-bold);
        cursor: pointer;
        transition: color var(--transition-fast), background var(--transition-fast), border-color var(--transition-fast);
      }
      .filter-chip:hover {
        color: var(--text-primary);
        border-color: var(--border-emphasis);
        background: var(--bg-surface-hover);
      }
      .filter-chip.active {
        color: var(--brand-100);
        background: rgba(56, 189, 248, 0.14);
        border-color: var(--border-emphasis);
      }
      .concepts-overview {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: var(--space-4);
      }
      .overview-card {
        min-height: 96px;
        padding: var(--space-4);
        background: linear-gradient(180deg, rgba(15, 27, 45, 0.94), rgba(11, 23, 39, 0.92));
        border: 1px solid var(--border-default);
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-sm);
      }
      .overview-value {
        color: var(--text-primary);
        font-size: var(--text-3xl);
        font-weight: var(--font-weight-extrabold);
        line-height: 1;
      }
      .overview-label {
        margin-top: var(--space-2);
        color: var(--text-muted);
        font-size: var(--text-xs);
        font-weight: var(--font-weight-extrabold);
        letter-spacing: 0.06em;
        text-transform: uppercase;
      }
      .cards-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(270px, 1fr));
        gap: var(--space-4);
      }
      .concept-card {
        min-height: 228px;
        display: flex;
        flex-direction: column;
        gap: var(--space-4);
        padding: var(--space-5);
        background: linear-gradient(180deg, rgba(15, 27, 45, 0.94), rgba(11, 23, 39, 0.92));
        border: 1px solid var(--border-default);
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-sm);
        transition: transform var(--transition-fast), box-shadow var(--transition-fast), border-color var(--transition-fast);
      }
      .concept-card:hover {
        transform: translateY(-2px);
        border-color: var(--border-emphasis);
        box-shadow: var(--shadow-md);
        background: var(--bg-surface-hover);
      }
      .concept-card-top {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: var(--space-3);
      }
      .card-category-badge {
        display: inline-flex;
        align-items: center;
        min-height: 26px;
        padding: 0.2rem 0.55rem;
        border-radius: var(--radius-md);
        font-size: var(--text-xs);
        font-weight: var(--font-weight-extrabold);
      }
      .cat-interpolation { color: var(--info); background: var(--info-bg); border: 1px solid var(--info-border); }
      .cat-integration { color: var(--success); background: var(--success-bg); border: 1px solid var(--success-border); }
      .cat-ode { color: var(--accent-purple); background: rgba(124, 58, 237, 0.09); border: 1px solid rgba(124, 58, 237, 0.2); }
      .cat-default { color: var(--text-muted); background: var(--bg-surface-2); border: 1px solid var(--border-default); }
      .card-level {
        color: var(--brand-300);
        font-size: var(--text-xs);
        font-weight: var(--font-weight-extrabold);
      }
      .card-name {
        margin: 0;
        color: var(--text-primary);
        font-size: var(--text-lg);
        font-weight: var(--font-weight-extrabold);
        line-height: 1.25;
      }
      .card-desc {
        margin: 0;
        color: var(--text-muted);
        font-size: var(--text-sm);
        line-height: var(--line-height-relaxed);
        flex: 1;
      }
      .card-level-bar {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 4px;
      }
      .level-dot {
        height: 6px;
        border-radius: var(--radius-full);
        background: var(--bg-surface-3);
      }
      .level-dot.active { background: var(--brand-gradient); }
      .sk-card {
        min-height: 210px;
        border-radius: var(--radius-md);
        background: linear-gradient(90deg, rgba(148, 163, 184, 0.12) 25%, rgba(148, 163, 184, 0.22) 50%, rgba(148, 163, 184, 0.12) 75%);
        background-size: 200% 100%;
        animation: ds-skeleton-shimmer 1.3s infinite;
      }
      .no-results {
        grid-column: 1 / -1;
        min-height: 220px;
        display: grid;
        place-items: center;
        padding: var(--space-8);
        color: var(--text-muted);
        text-align: center;
        background: var(--bg-surface);
        border: 1px dashed var(--border-default);
        border-radius: var(--radius-md);
      }
      @media (max-width: 760px) {
        .concepts-toolbar { grid-template-columns: 1fr; align-items: start; }
        .filter-bar { justify-content: flex-start; }
        .concepts-overview { grid-template-columns: 1fr; }
      }
    </style>

    <div class="concepts-page">
      <section class="concepts-toolbar">
        <div>
          <h2 class="concepts-toolbar-title">Concept map</h2>
          <p class="concepts-toolbar-sub">Une vue structuree des modules, niveaux et notions importantes de l'analyse numerique.</p>
        </div>
        <div class="filter-bar" id="filter-bar">
          <button class="filter-chip active" data-cat="all">All concepts</button>
        </div>
      </section>
      <section class="concepts-overview" id="concepts-overview" aria-label="Concept overview">
        <div class="overview-card"><div class="overview-value skeleton" style="width:64px;height:34px"></div><div class="overview-label">Concepts</div></div>
        <div class="overview-card"><div class="overview-value skeleton" style="width:64px;height:34px"></div><div class="overview-label">Modules</div></div>
        <div class="overview-card"><div class="overview-value skeleton" style="width:64px;height:34px"></div><div class="overview-label">Max level</div></div>
      </section>
      <section class="cards-grid" id="cards-grid" aria-label="Concept cards">
        ${[1, 2, 3, 4, 5, 6].map(() => `<div class="sk-card"></div>`).join('')}
      </section>
    </div>
  `

  container.appendChild(main)

  const getCatClass = (category: string) => {
    const value = category?.toLowerCase() || ''
    if (value.includes('interpolat')) return 'cat-interpolation'
    if (value.includes('integrat')) return 'cat-integration'
    if (value.includes('ode') || value.includes('differential')) return 'cat-ode'
    return 'cat-default'
  }

  const getLevelDots = (level: string | number) => {
    const parsed = typeof level === 'number' ? level : parseInt(level) || 2
    return [1, 2, 3, 4, 5].map((index) => `<span class="level-dot${index <= parsed ? ' active' : ''}"></span>`).join('')
  }

  api.getConcepts().then((concepts: Concept[]) => {
    const categories = ['all', ...new Set(concepts.map((concept) => concept.category).filter(Boolean))]
    const filterBar = main.querySelector('#filter-bar')!
    const maxLevel = concepts.reduce((max, concept) => Math.max(max, parseInt(String(concept.level)) || 0), 0)
    main.querySelector('#concepts-overview')!.innerHTML = `
      <div class="overview-card"><div class="overview-value">${concepts.length}</div><div class="overview-label">Concepts</div></div>
      <div class="overview-card"><div class="overview-value">${categories.length - 1}</div><div class="overview-label">Modules</div></div>
      <div class="overview-card"><div class="overview-value">${maxLevel || '-'}</div><div class="overview-label">Max level</div></div>
    `

    filterBar.innerHTML = categories.map((category) => `
      <button class="filter-chip${category === 'all' ? ' active' : ''}" data-cat="${escapeHtml(category)}">
        ${category === 'all' ? 'All concepts' : escapeHtml(category)}
      </button>
    `).join('')

    const renderCards = (filter: string) => {
      const filtered = filter === 'all' ? concepts : concepts.filter((concept) => concept.category === filter)
      const grid = main.querySelector('#cards-grid')!

      if (filtered.length === 0) {
        grid.innerHTML = '<div class="no-results">No concepts found.</div>'
        return
      }

      grid.innerHTML = filtered.map((concept) => `
        <article class="concept-card">
          <div class="concept-card-top">
            <span class="card-category-badge ${getCatClass(concept.category)}">${escapeHtml(concept.category || 'Concept')}</span>
            <span class="card-level">Level ${escapeHtml(String(concept.level || '-'))}</span>
          </div>
          <h3 class="card-name">${escapeHtml(concept.name)}</h3>
          <p class="card-desc">${escapeHtml(concept.description || 'Core concept in numerical analysis and scientific computing.')}</p>
          <div class="card-level-bar" aria-label="Difficulty level">${getLevelDots(concept.level)}</div>
        </article>
      `).join('')
    }

    renderCards('all')

    filterBar.addEventListener('click', (event) => {
      const chip = (event.target as HTMLElement).closest('.filter-chip') as HTMLElement | null
      if (!chip) return
      filterBar.querySelectorAll('.filter-chip').forEach((button) => button.classList.remove('active'))
      chip.classList.add('active')
      renderCards(chip.dataset.cat || 'all')
    })
  }).catch(() => {
    main.querySelector('#cards-grid')!.innerHTML = `
      <div class="no-results">
        Backend not connected. Start the API service and reload this page.
      </div>
    `
  })

  shell.setContent(container)
  return shell.element
}
