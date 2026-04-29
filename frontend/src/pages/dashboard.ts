// ============================================================
// Dashboard
// ============================================================

import { api, Etudiant, LearningPath } from '../api'
import { createAppShell } from '../components/app-shell'
import { t } from '../i18n'

function escapeHtml(s: string): string {
  return (s || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function clampPct(value: number): number {
  return Math.max(0, Math.min(100, Math.round(value)))
}

export function DashboardPage(): HTMLElement {
  const shell = createAppShell({
    activeRoute: '/dashboard',
    pageTitle: t('dashboard.title'),
    pageSubtitle: t('dashboard.subtitle'),
  })
  const container = document.createElement('div')
  const userStr = localStorage.getItem('user')
  const user: Etudiant | null = userStr ? JSON.parse(userStr) : null
  const token = localStorage.getItem('token')
  if (token) api.setToken(token)

  const firstName = user?.nom_complet?.split(' ')[0] || 'Student'
  const currentLevel = user?.niveau_actuel || 'Intermediate'

  const main = document.createElement('div')
  main.innerHTML = `
    <style>
      @keyframes dashIn { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: translateY(0); } }
      @keyframes ringFill { from { stroke-dashoffset: 364; } }

      .dashboard {
        display: flex;
        flex-direction: column;
        gap: var(--space-5);
        animation: dashIn 0.36s ease both;
      }

      .dashboard-hero {
        display: grid;
        grid-template-columns: minmax(0, 1.2fr) 330px;
        gap: var(--space-5);
        align-items: stretch;
      }

      .hero-panel,
      .mastery-panel,
      .metric-card,
      .dash-panel,
      .quick-action {
        position: relative;
        overflow: hidden;
        background:
          linear-gradient(180deg, rgba(15, 27, 45, 0.96), rgba(8, 18, 31, 0.94)),
          linear-gradient(135deg, rgba(56, 189, 248, 0.08), rgba(99, 102, 241, 0.06));
        border: 1px solid var(--border-default);
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-sm);
      }

      .hero-panel {
        min-height: 286px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        gap: var(--space-8);
        padding: var(--space-8);
      }

      .hero-kicker {
        display: inline-flex;
        align-items: center;
        width: fit-content;
        min-height: 28px;
        padding: 0.25rem 0.62rem;
        color: var(--brand-100);
        background: rgba(56, 189, 248, 0.12);
        border: 1px solid rgba(125, 211, 252, 0.24);
        border-radius: var(--radius-md);
        font-size: var(--text-xs);
        font-weight: var(--font-weight-extrabold);
        letter-spacing: 0.07em;
        text-transform: uppercase;
      }

      .hero-title {
        margin: var(--space-4) 0 var(--space-3);
        max-width: 760px;
        color: var(--text-primary);
        font-size: var(--text-5xl);
        line-height: 1.02;
        font-weight: var(--font-weight-extrabold);
      }

      .hero-title span { color: var(--brand-300); }

      .hero-sub {
        margin: 0;
        max-width: 690px;
        color: var(--text-muted);
        font-size: var(--text-md);
        line-height: var(--line-height-relaxed);
      }

      .hero-bottom {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: var(--space-4);
        flex-wrap: wrap;
      }

      .level-stack {
        display: flex;
        gap: var(--space-3);
        flex-wrap: wrap;
      }

      .level-chip,
      .mini-chip {
        display: inline-flex;
        align-items: center;
        min-height: 34px;
        padding: 0.42rem 0.75rem;
        border-radius: var(--radius-md);
        color: var(--text-secondary);
        background: rgba(148, 163, 184, 0.08);
        border: 1px solid var(--border-subtle);
        font-size: var(--text-xs);
        font-weight: var(--font-weight-extrabold);
      }

      .level-chip strong,
      .mini-chip strong { color: var(--brand-100); margin-left: var(--space-2); }

      .hero-actions {
        display: flex;
        gap: var(--space-2);
        flex-wrap: wrap;
      }

      .mastery-panel {
        min-height: 286px;
        padding: var(--space-6);
        display: grid;
        align-content: space-between;
        gap: var(--space-5);
      }

      .mastery-head {
        display: flex;
        justify-content: space-between;
        gap: var(--space-3);
      }

      .mastery-label {
        margin: 0;
        color: var(--text-primary);
        font-size: var(--text-lg);
        font-weight: var(--font-weight-extrabold);
      }

      .mastery-caption {
        margin: var(--space-1) 0 0;
        color: var(--text-muted);
        font-size: var(--text-sm);
      }

      .mastery-ring-wrap {
        width: 168px;
        height: 168px;
        margin: 0 auto;
        position: relative;
        display: grid;
        place-items: center;
      }

      .mastery-ring { transform: rotate(-90deg); }
      .mastery-ring-bg {
        fill: none;
        stroke: rgba(148, 163, 184, 0.16);
        stroke-width: 12;
      }
      .mastery-ring-fill {
        fill: none;
        stroke: url(#masteryGradient);
        stroke-width: 12;
        stroke-linecap: round;
        stroke-dasharray: 364;
        transition: stroke-dashoffset 1.2s ease;
        animation: ringFill 0.8s ease both;
      }
      .mastery-ring-value {
        position: absolute;
        inset: 0;
        display: grid;
        place-items: center;
        color: var(--text-primary);
        font-size: var(--text-4xl);
        font-weight: var(--font-weight-extrabold);
      }

      .mastery-foot {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: var(--space-2);
      }

      .mastery-mini {
        min-height: 62px;
        padding: var(--space-3);
        border-radius: var(--radius-md);
        background: rgba(148, 163, 184, 0.06);
        border: 1px solid var(--border-subtle);
      }

      .mastery-mini strong {
        display: block;
        color: var(--text-primary);
        font-size: var(--text-lg);
        line-height: 1;
      }

      .mastery-mini span {
        display: block;
        margin-top: var(--space-1);
        color: var(--text-muted);
        font-size: var(--text-xs);
        font-weight: var(--font-weight-bold);
      }

      .metrics-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: var(--space-4);
      }

      .metric-card {
        min-height: 132px;
        padding: var(--space-5);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        gap: var(--space-4);
      }

      .metric-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: var(--space-3);
      }

      .metric-token {
        width: 38px;
        height: 38px;
        display: grid;
        place-items: center;
        color: var(--brand-100);
        background: rgba(56, 189, 248, 0.1);
        border: 1px solid rgba(125, 211, 252, 0.22);
        border-radius: var(--radius-md);
        font-size: var(--text-xs);
        font-weight: var(--font-weight-extrabold);
      }

      .metric-trend {
        color: var(--text-muted);
        font-size: var(--text-xs);
        font-weight: var(--font-weight-bold);
      }

      .metric-value {
        color: var(--text-primary);
        font-size: var(--text-4xl);
        font-weight: var(--font-weight-extrabold);
        line-height: 1;
      }

      .metric-label {
        margin-top: var(--space-2);
        color: var(--text-muted);
        font-size: var(--text-xs);
        font-weight: var(--font-weight-extrabold);
        letter-spacing: 0.06em;
        text-transform: uppercase;
      }

      .dashboard-workbench {
        display: grid;
        grid-template-columns: minmax(0, 1.12fr) minmax(320px, 0.88fr);
        gap: var(--space-5);
      }

      .dash-panel {
        padding: var(--space-5);
      }

      .panel-head {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: var(--space-4);
        margin-bottom: var(--space-4);
      }

      .panel-title {
        margin: 0;
        color: var(--text-primary);
        font-size: var(--text-lg);
        font-weight: var(--font-weight-extrabold);
      }

      .panel-subtitle {
        margin: var(--space-1) 0 0;
        color: var(--text-muted);
        font-size: var(--text-sm);
      }

      .priority-list,
      .recommend-list {
        display: flex;
        flex-direction: column;
        gap: var(--space-3);
      }

      .priority-item,
      .recommend-item {
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto;
        gap: var(--space-4);
        align-items: center;
        min-height: 76px;
        padding: var(--space-4);
        border-radius: var(--radius-md);
        background: rgba(148, 163, 184, 0.055);
        border: 1px solid var(--border-subtle);
      }

      .priority-name,
      .recommend-name {
        color: var(--text-secondary);
        font-size: var(--text-sm);
        font-weight: var(--font-weight-bold);
        line-height: 1.35;
      }

      .priority-meta,
      .recommend-meta {
        margin-top: var(--space-2);
        display: flex;
        align-items: center;
        gap: var(--space-2);
        color: var(--text-muted);
        font-size: var(--text-xs);
        font-weight: var(--font-weight-bold);
      }

      .priority-bar {
        width: min(180px, 100%);
        height: 8px;
        overflow: hidden;
        border-radius: var(--radius-full);
        background: rgba(148, 163, 184, 0.16);
      }

      .priority-fill {
        height: 100%;
        border-radius: inherit;
        background: linear-gradient(90deg, var(--warning), var(--danger));
      }

      .priority-score {
        color: var(--warning);
        font-size: var(--text-sm);
        font-weight: var(--font-weight-extrabold);
        text-align: right;
      }

      .recommend-badge {
        display: inline-flex;
        align-items: center;
        min-height: 26px;
        padding: 0.22rem 0.58rem;
        color: var(--success);
        background: var(--success-bg);
        border: 1px solid var(--success-border);
        border-radius: var(--radius-md);
        font-size: var(--text-xs);
        font-weight: var(--font-weight-extrabold);
      }

      .focus-stack {
        display: grid;
        grid-template-columns: 1fr;
        gap: var(--space-4);
      }

      .quick-actions {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: var(--space-4);
      }

      .quick-action {
        min-height: 132px;
        padding: var(--space-5);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        text-decoration: none;
        transition: transform var(--transition-fast), border-color var(--transition-fast), background var(--transition-fast);
      }

      .quick-action:hover {
        transform: translateY(-2px);
        border-color: var(--border-emphasis);
        background: var(--bg-surface-hover);
      }

      .quick-token {
        width: 34px;
        height: 34px;
        display: grid;
        place-items: center;
        color: var(--brand-100);
        background: rgba(56, 189, 248, 0.11);
        border: 1px solid rgba(125, 211, 252, 0.22);
        border-radius: var(--radius-md);
        font-size: var(--text-xs);
        font-weight: var(--font-weight-extrabold);
      }

      .quick-title {
        margin: var(--space-4) 0 var(--space-1);
        color: var(--text-primary);
        font-size: var(--text-md);
        font-weight: var(--font-weight-extrabold);
      }

      .quick-desc {
        margin: 0;
        color: var(--text-muted);
        font-size: var(--text-sm);
        line-height: 1.5;
      }

      .empty-state {
        min-height: 160px;
        display: grid;
        place-items: center;
        padding: var(--space-6);
        color: var(--text-muted);
        text-align: center;
        border: 1px dashed var(--border-default);
        border-radius: var(--radius-md);
        background: rgba(148, 163, 184, 0.045);
      }

      .empty-state p { margin: 0; }

      .skeleton {
        background: linear-gradient(90deg, rgba(148, 163, 184, 0.08) 25%, rgba(148, 163, 184, 0.16) 50%, rgba(148, 163, 184, 0.08) 75%);
        background-size: 200% 100%;
        animation: ds-skeleton-shimmer 1.3s infinite;
        border-radius: var(--radius-md);
      }

      .sk-line { height: 14px; }
      .sk-card { height: 76px; }

      @media (max-width: 1120px) {
        .dashboard-hero,
        .dashboard-workbench { grid-template-columns: 1fr; }
        .mastery-panel { min-height: auto; }
        .metrics-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      }

      @media (max-width: 760px) {
        .hero-panel { padding: var(--space-5); }
        .hero-title { font-size: var(--text-4xl); }
        .hero-bottom { align-items: flex-start; flex-direction: column; }
        .hero-actions .ds-btn { width: 100%; }
        .metrics-grid,
        .quick-actions,
        .mastery-foot { grid-template-columns: 1fr; }
        .priority-item,
        .recommend-item { grid-template-columns: 1fr; }
        .priority-score { text-align: left; }
      }
    </style>

    <div class="dashboard">
      <section class="dashboard-hero">
        <div class="hero-panel">
          <div>
            <div class="hero-kicker">Adaptive learning cockpit</div>
            <h2 class="hero-title">Bonjour, <span>${escapeHtml(firstName)}</span></h2>
            <p class="hero-sub">Une vue claire pour reprendre le bon concept, lancer un quiz adapte et obtenir de l'aide au bon moment.</p>
          </div>
          <div class="hero-bottom">
            <div class="level-stack">
              <span class="level-chip">Niveau <strong>${escapeHtml(currentLevel)}</strong></span>
              <span class="mini-chip">Mode <strong>Personalise</strong></span>
            </div>
            <div class="hero-actions">
              <a href="/quiz-ai" data-link class="ds-btn ds-btn-primary">Generer un quiz</a>
              <a href="/path" data-link class="ds-btn ds-btn-secondary">Voir le parcours</a>
            </div>
          </div>
        </div>

        <aside class="mastery-panel" aria-label="Mastery summary">
          <div class="mastery-head">
            <div>
              <p class="mastery-label">Maitrise globale</p>
              <p class="mastery-caption">Basee sur les concepts valides.</p>
            </div>
          </div>
          <div class="mastery-ring-wrap" id="mastery-ring">
            <svg class="mastery-ring" width="168" height="168" viewBox="0 0 168 168">
              <defs>
                <linearGradient id="masteryGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#7dd3fc"/>
                  <stop offset="58%" stop-color="#818cf8"/>
                  <stop offset="100%" stop-color="#34d399"/>
                </linearGradient>
              </defs>
              <circle class="mastery-ring-bg" cx="84" cy="84" r="58"/>
              <circle class="mastery-ring-fill" cx="84" cy="84" r="58" stroke-dashoffset="364"/>
            </svg>
            <div class="mastery-ring-value">0%</div>
          </div>
          <div class="mastery-foot" id="mastery-foot">
            <div class="mastery-mini"><strong>-</strong><span>Mastered</span></div>
            <div class="mastery-mini"><strong>-</strong><span>Progress</span></div>
            <div class="mastery-mini"><strong>-</strong><span>Next</span></div>
          </div>
        </aside>
      </section>

      <section class="metrics-grid" id="metrics-grid" aria-label="Progress metrics">
        ${['TC', 'OK', 'IP', 'ND'].map(() => `
          <div class="metric-card">
            <div class="metric-top">
              <div class="metric-token skeleton" style="width:38px;height:38px"></div>
              <div class="metric-trend skeleton" style="width:54px;height:12px"></div>
            </div>
            <div>
              <div class="metric-value skeleton" style="width:78px;height:42px"></div>
              <div class="metric-label skeleton" style="width:118px;height:12px;margin-top:12px"></div>
            </div>
          </div>
        `).join('')}
      </section>

      <section class="dashboard-workbench">
        <div class="dash-panel">
          <div class="panel-head">
            <div>
              <h3 class="panel-title">Priorites de revision</h3>
              <p class="panel-subtitle">Les points faibles a travailler en premier.</p>
            </div>
            <a href="/content" data-link class="ds-btn ds-btn-secondary">Cours</a>
          </div>
          <div class="priority-list" id="priority-list">
            ${[1, 2, 3].map(() => `<div class="skeleton sk-card"></div>`).join('')}
          </div>
        </div>

        <div class="focus-stack">
          <div class="dash-panel">
            <div class="panel-head">
              <div>
                <h3 class="panel-title">Prochaine etape</h3>
                <p class="panel-subtitle">Concepts prets pour avancer.</p>
              </div>
            </div>
            <div class="recommend-list" id="recommend-list">
              ${[1, 2].map(() => `<div class="skeleton sk-card"></div>`).join('')}
            </div>
          </div>
        </div>
      </section>

      <section class="quick-actions" aria-label="Quick actions">
        <a href="/concepts" data-link class="quick-action">
          <div class="quick-token">KG</div>
          <div>
            <h3 class="quick-title">Explorer les concepts</h3>
            <p class="quick-desc">Voir les modules, niveaux et dependances.</p>
          </div>
        </a>
        <a href="/quiz-ai" data-link class="quick-action">
          <div class="quick-token">QZ</div>
          <div>
            <h3 class="quick-title">S'entrainer</h3>
            <p class="quick-desc">Generer un quiz cible sur un concept.</p>
          </div>
        </a>
        <a href="/tutor" data-link class="quick-action">
          <div class="quick-token">AI</div>
          <div>
            <h3 class="quick-title">Demander au tuteur</h3>
            <p class="quick-desc">Obtenir une explication adaptee.</p>
          </div>
        </a>
      </section>
    </div>
  `

  container.appendChild(main)

  const renderLoaded = (path: LearningPath): void => {
    const { total_concepts, mastered, in_progress } = path.overall_progress
    const toDiscover = Math.max(total_concepts - mastered - in_progress, 0)
    const masteryPct = total_concepts > 0 ? clampPct((mastered / total_concepts) * 100) : 0
    const circumference = 364

    const ringFill = main.querySelector('.mastery-ring-fill') as SVGCircleElement | null
    const ringValue = main.querySelector('.mastery-ring-value') as HTMLElement | null
    if (ringFill) ringFill.setAttribute('stroke-dashoffset', String(circumference - (circumference * masteryPct / 100)))
    if (ringValue) ringValue.textContent = `${masteryPct}%`

    const masteryFoot = main.querySelector('#mastery-foot')!
    masteryFoot.innerHTML = `
      <div class="mastery-mini"><strong>${mastered}</strong><span>Mastered</span></div>
      <div class="mastery-mini"><strong>${in_progress}</strong><span>Progress</span></div>
      <div class="mastery-mini"><strong>${toDiscover}</strong><span>Next</span></div>
    `

    const metrics = [
      { token: 'TC', value: total_concepts, label: 'Total concepts', trend: 'Scope' },
      { token: 'OK', value: mastered, label: 'Mastered', trend: `${masteryPct}%` },
      { token: 'IP', value: in_progress, label: 'In progress', trend: 'Active' },
      { token: 'ND', value: toDiscover, label: 'To discover', trend: 'Queued' },
    ]

    const metricsGrid = main.querySelector('#metrics-grid')!
    metricsGrid.innerHTML = metrics.map((metric) => `
      <article class="metric-card">
        <div class="metric-top">
          <div class="metric-token">${metric.token}</div>
          <div class="metric-trend">${metric.trend}</div>
        </div>
        <div>
          <div class="metric-value">${metric.value}</div>
          <div class="metric-label">${metric.label}</div>
        </div>
      </article>
    `).join('')

    const priorityList = main.querySelector('#priority-list')!
    if (path.concepts_to_improve.length === 0) {
      priorityList.innerHTML = `<div class="empty-state"><p>Aucune faiblesse critique pour le moment.</p></div>`
    } else {
      priorityList.innerHTML = path.concepts_to_improve.slice(0, 5).map((concept) => `
        <article class="priority-item">
          <div>
            <div class="priority-name">${escapeHtml(concept.name)}</div>
            <div class="priority-meta">
              <span>${escapeHtml(concept.status || 'Needs practice')}</span>
              <span>${concept.mastery.toFixed(0)}% mastery</span>
            </div>
          </div>
          <div>
            <div class="priority-score">${concept.mastery.toFixed(0)}%</div>
            <div class="priority-bar" aria-label="Mastery">
              <div class="priority-fill" style="width:${clampPct(concept.mastery)}%"></div>
            </div>
          </div>
        </article>
      `).join('')
    }

    const recommendList = main.querySelector('#recommend-list')!
    if (path.next_recommended.length === 0) {
      recommendList.innerHTML = `<div class="empty-state"><p>Termine les revisions en cours pour debloquer la suite.</p></div>`
    } else {
      recommendList.innerHTML = path.next_recommended.slice(0, 4).map((concept) => `
        <article class="recommend-item">
          <div>
            <div class="recommend-name">${escapeHtml(concept.name)}</div>
            <div class="recommend-meta">
              <span>${escapeHtml(concept.category || 'Module')}</span>
              <span>Level ${escapeHtml(concept.level || '-')}</span>
            </div>
          </div>
          <span class="recommend-badge">Ready</span>
        </article>
      `).join('')
    }
  }

  if (user) {
    api.getLearningPath(user.id)
      .then(renderLoaded)
      .catch(() => {
        main.querySelector('#priority-list')!.innerHTML = `<div class="empty-state"><p>Lance un premier quiz pour creer ton profil de progression.</p></div>`
        main.querySelector('#recommend-list')!.innerHTML = `<div class="empty-state"><p>Les recommandations apparaitront apres ton diagnostic.</p></div>`
      })
  }

  shell.setContent(container)
  return shell.element
}
