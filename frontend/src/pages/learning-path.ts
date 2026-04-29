// ============================================================
// Learning Path Page
// ============================================================

import { api } from '../api'
import { createAppShell } from '../components/app-shell'
import { t } from '../i18n'

function escapeHtml(s: string): string {
  return (s || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

export function LearningPathPage(): HTMLElement {
  const shell = createAppShell({
    activeRoute: '/path',
    pageTitle: t('sidebar.path'),
    pageSubtitle: 'Recommended sequence based on mastery and prerequisites',
  })
  const container = document.createElement('div')
  const userStr = localStorage.getItem('user')
  const user = userStr ? JSON.parse(userStr) : null
  const token = localStorage.getItem('token')
  if (token) api.setToken(token)

  const main = document.createElement('div')
  main.innerHTML = `
    <style>
      @keyframes pathIn { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }

      .path-page {
        display: flex;
        flex-direction: column;
        gap: var(--space-5);
        animation: pathIn 0.35s ease both;
      }
      .overall-bar,
      .module-section {
        background:
          linear-gradient(180deg, rgba(15, 27, 45, 0.96), rgba(8, 18, 31, 0.94)),
          linear-gradient(135deg, rgba(56, 189, 248, 0.08), rgba(99, 102, 241, 0.05));
        border: 1px solid var(--border-default);
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-sm);
      }
      .overall-bar { padding: var(--space-6); }
      .overall-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: var(--space-4);
        margin-bottom: var(--space-4);
      }
      .overall-label {
        color: var(--text-primary);
        font-size: var(--text-lg);
        font-weight: var(--font-weight-extrabold);
      }
      .overall-caption {
        margin-top: var(--space-1);
        color: var(--text-muted);
        font-size: var(--text-sm);
      }
      .overall-pct {
        color: var(--brand-300);
        font-size: var(--text-4xl);
        font-weight: var(--font-weight-extrabold);
        line-height: 1;
      }
      .progress-track {
        width: 100%;
        height: 10px;
        overflow: hidden;
        background: var(--bg-surface-3);
        border-radius: var(--radius-full);
      }
      .progress-fill {
        height: 100%;
        border-radius: inherit;
        background: var(--brand-gradient);
        transition: width 1.2s ease;
      }
      .overall-stats {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: var(--space-3);
        margin-top: var(--space-5);
      }
      .overall-stat {
        padding: var(--space-4);
        color: var(--text-muted);
        background: rgba(148, 163, 184, 0.06);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        font-size: var(--text-sm);
      }
      .overall-stat strong {
        display: block;
        margin-bottom: var(--space-1);
        color: var(--text-primary);
        font-size: var(--text-2xl);
        line-height: 1;
      }
      .module-section {
        padding: var(--space-5);
      }
      .module-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: var(--space-4);
        margin-bottom: var(--space-4);
      }
      .module-title-wrap {
        display: flex;
        align-items: center;
        gap: var(--space-3);
        min-width: 0;
      }
      .module-icon {
        width: 42px;
        height: 42px;
        display: grid;
        place-items: center;
        flex: 0 0 auto;
        border-radius: var(--radius-md);
        font-size: var(--text-xs);
        font-weight: var(--font-weight-extrabold);
        letter-spacing: 0.04em;
      }
      .mi-blue { color: var(--info); background: var(--info-bg); border: 1px solid var(--info-border); }
      .mi-green { color: var(--success); background: var(--success-bg); border: 1px solid var(--success-border); }
      .mi-purple { color: var(--accent-purple); background: rgba(124, 58, 237, 0.09); border: 1px solid rgba(124, 58, 237, 0.2); }
      .module-name {
        color: var(--text-primary);
        font-size: var(--text-lg);
        font-weight: var(--font-weight-extrabold);
        line-height: 1.25;
      }
      .module-count {
        margin-top: var(--space-1);
        color: var(--text-muted);
        font-size: var(--text-sm);
      }
      .module-progress {
        min-width: 96px;
        color: var(--brand-300);
        text-align: right;
        font-size: var(--text-sm);
        font-weight: var(--font-weight-extrabold);
      }
      .concept-row {
        display: grid;
        grid-template-columns: 34px minmax(0, 1fr) minmax(110px, 160px) 52px auto;
        align-items: center;
        gap: var(--space-3);
        padding: var(--space-3) 0;
        border-top: 1px solid var(--border-subtle);
      }
      .concept-status {
        width: 28px;
        height: 28px;
        display: grid;
        place-items: center;
        border-radius: var(--radius-md);
        font-size: 0.66rem;
        font-weight: var(--font-weight-extrabold);
      }
      .status-mastered { color: var(--success); background: var(--success-bg); border: 1px solid var(--success-border); }
      .status-progress { color: var(--warning); background: var(--warning-bg); border: 1px solid var(--warning-border); }
      .status-ready { color: var(--brand-100); background: rgba(56, 189, 248, 0.12); border: 1px solid var(--border-emphasis); }
      .status-locked { color: var(--text-muted); background: var(--bg-surface-2); border: 1px solid var(--border-default); }
      .concept-info { min-width: 0; }
      .concept-name {
        color: var(--text-secondary);
        font-size: var(--text-sm);
        font-weight: var(--font-weight-bold);
      }
      .concept-prereq {
        margin-top: 2px;
        color: var(--text-muted);
        font-size: var(--text-xs);
      }
      .concept-prereq.ready { color: var(--brand-300); }
      .mastery-bar-wrap {
        height: 8px;
        overflow: hidden;
        background: var(--bg-surface-3);
        border-radius: var(--radius-full);
      }
      .mastery-bar { height: 100%; border-radius: inherit; transition: width 1.2s ease; }
      .bar-green { background: var(--success); }
      .bar-orange { background: var(--warning); }
      .bar-gray { background: var(--text-disabled); }
      .mastery-pct {
        color: var(--text-muted);
        font-size: var(--text-xs);
        font-weight: var(--font-weight-extrabold);
        text-align: right;
      }
      .action-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 34px;
        padding: 0.42rem 0.72rem;
        border: 1px solid var(--border-default);
        border-radius: var(--radius-md);
        color: var(--text-primary);
        background: rgba(21, 36, 58, 0.88);
        font-size: var(--text-xs);
        font-weight: var(--font-weight-extrabold);
        text-decoration: none;
        white-space: nowrap;
      }
      .btn-start { color: #06111f; background: linear-gradient(135deg, #e0f2fe, #7dd3fc); border-color: rgba(125, 211, 252, 0.6); }
      .btn-review { color: var(--warning); background: var(--warning-bg); border-color: var(--warning-border); }
      .empty-state {
        min-height: 260px;
        display: grid;
        place-items: center;
        gap: var(--space-4);
        padding: var(--space-8);
        color: var(--text-muted);
        text-align: center;
        background: rgba(15, 27, 45, 0.92);
        border: 1px dashed var(--border-default);
        border-radius: var(--radius-md);
      }
      .empty-state p { margin: 0; }
      .skeleton {
        background: linear-gradient(90deg, rgba(148, 163, 184, 0.12) 25%, rgba(148, 163, 184, 0.22) 50%, rgba(148, 163, 184, 0.12) 75%);
        background-size: 200% 100%;
        animation: ds-skeleton-shimmer 1.3s infinite;
        border-radius: var(--radius-md);
      }
      .sk-module { height: 210px; margin-top: var(--space-4); }
      @media (max-width: 880px) {
        .overall-stats { grid-template-columns: 1fr; }
        .concept-row { grid-template-columns: 34px minmax(0, 1fr) 52px; }
        .mastery-bar-wrap,
        .action-btn { grid-column: 2 / -1; }
        .mastery-pct { text-align: left; }
      }
      @media (max-width: 620px) {
        .overall-header,
        .module-header { align-items: flex-start; flex-direction: column; }
        .module-progress { text-align: left; }
      }
    </style>

    <div class="path-page">
      <div id="path-content">
        <div class="overall-bar"><div class="skeleton" style="height:92px"></div></div>
        ${[1, 2, 3].map(() => `<div class="skeleton sk-module"></div>`).join('')}
      </div>
    </div>
  `

  container.appendChild(main)

  if (!user) {
    shell.setContent(container)
    return shell.element
  }

  Promise.all([
    api.getLearningPath(user.id),
    api.getConcepts(),
  ]).then(([path, concepts]) => {
    const { total_concepts, mastered, in_progress } = path.overall_progress
    const pct = total_concepts > 0 ? Math.round((mastered / total_concepts) * 100) : 0

    const masteryMap: Record<string, number> = {}
    path.concepts_to_improve.forEach((concept) => { masteryMap[concept.id] = concept.mastery })

    const modules: Record<string, typeof concepts> = {}
    concepts.forEach((concept) => {
      const category = concept.category || 'Other'
      if (!modules[category]) modules[category] = []
      modules[category].push(concept)
    })

    const moduleColors: Record<string, { icon: string; cls: string }> = {
      'Interpolation': { icon: 'INT', cls: 'mi-blue' },
      'Numerical Integration': { icon: 'NUM', cls: 'mi-green' },
      'Ordinary Differential Equations (ODEs)': { icon: 'ODE', cls: 'mi-purple' },
    }

    const getStatus = (conceptId: string) => {
      const mastery = masteryMap[conceptId]
      if (mastery !== undefined && mastery >= 70) return 'mastered'
      if (mastery !== undefined && mastery > 0) return 'progress'
      if (path.next_recommended.some((item) => item.id === conceptId)) return 'ready'
      return 'locked'
    }

    const getMastery = (conceptId: string) => masteryMap[conceptId] || 0
    const pathContent = main.querySelector('#path-content')!

    pathContent.innerHTML = `
      <section class="overall-bar">
        <div class="overall-header">
          <div>
            <div class="overall-label">Overall mastery</div>
            <div class="overall-caption">Progress calculated from mastered concepts and current work.</div>
          </div>
          <div class="overall-pct">${pct}%</div>
        </div>
        <div class="progress-track">
          <div class="progress-fill" style="width:${pct}%"></div>
        </div>
        <div class="overall-stats">
          <div class="overall-stat"><strong>${mastered}</strong>Mastered</div>
          <div class="overall-stat"><strong>${in_progress}</strong>In progress</div>
          <div class="overall-stat"><strong>${Math.max(total_concepts - mastered - in_progress, 0)}</strong>To discover</div>
        </div>
      </section>

      ${Object.entries(modules).map(([moduleName, moduleConcepts]) => {
        const moduleStyle = moduleColors[moduleName] || { icon: 'MOD', cls: 'mi-blue' }
        const modMastered = moduleConcepts.filter((concept) => getMastery(concept.id) >= 70).length
        const modPct = moduleConcepts.length > 0 ? Math.round((modMastered / moduleConcepts.length) * 100) : 0

        return `
          <section class="module-section">
            <div class="module-header">
              <div class="module-title-wrap">
                <div class="module-icon ${moduleStyle.cls}">${moduleStyle.icon}</div>
                <div>
                  <div class="module-name">${escapeHtml(moduleName)}</div>
                  <div class="module-count">${modMastered}/${moduleConcepts.length} concepts mastered</div>
                </div>
              </div>
              <div class="module-progress">${modPct}% complete</div>
            </div>
            ${moduleConcepts.map((concept) => {
              const status = getStatus(concept.id)
              const mastery = getMastery(concept.id)
              const statusToken = status === 'mastered' ? 'OK' : status === 'progress' ? 'IP' : status === 'ready' ? 'GO' : 'LK'
              const statusCls = status === 'mastered' ? 'status-mastered' : status === 'progress' ? 'status-progress' : status === 'ready' ? 'status-ready' : 'status-locked'
              const barCls = mastery >= 70 ? 'bar-green' : mastery > 0 ? 'bar-orange' : 'bar-gray'

              return `
                <div class="concept-row">
                  <div class="concept-status ${statusCls}">${statusToken}</div>
                  <div class="concept-info">
                    <div class="concept-name">${escapeHtml(concept.name)}</div>
                    ${status === 'locked' ? '<div class="concept-prereq">Prerequisites not met</div>' : ''}
                    ${status === 'ready' ? '<div class="concept-prereq ready">Ready to start</div>' : ''}
                  </div>
                  <div class="mastery-bar-wrap">
                    <div class="mastery-bar ${barCls}" style="width:${mastery}%"></div>
                  </div>
                  <div class="mastery-pct">${mastery > 0 ? mastery.toFixed(0) + '%' : '-'}</div>
                  ${status === 'ready' ? '<a href="/quiz-ai" data-link class="action-btn btn-start">Start</a>' : ''}
                  ${status === 'progress' ? '<a href="/quiz-ai" data-link class="action-btn btn-review">Review</a>' : ''}
                </div>
              `
            }).join('')}
          </section>
        `
      }).join('')}
    `
  }).catch(() => {
    main.querySelector('#path-content')!.innerHTML = `
      <div class="empty-state">
        <p>Take your first quiz to generate your personalized learning path.</p>
        <a href="/quiz-ai" data-link class="ds-btn ds-btn-primary">Go to quizzes</a>
      </div>
    `
  })

  shell.setContent(container)
  return shell.element
}
