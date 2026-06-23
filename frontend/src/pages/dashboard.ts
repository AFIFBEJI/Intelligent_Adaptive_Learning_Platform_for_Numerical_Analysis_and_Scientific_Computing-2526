// ============================================================
// Dashboard
// ============================================================

import { api, Etudiant, LearningPath } from '../api'
import { createAppShell } from '../components/app-shell'
import { nextStepHeroHtml } from '../components/next-step-hero'
import { statTileHtml } from '../components/stat-tile'
import { studyFlowHtml } from '../components/study-flow'
import { t, tLevel } from '../i18n'

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

  const main = document.createElement('div')
  main.innerHTML = `
    <style>
      @keyframes dashIn { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: translateY(0); } }

      .dashboard {
        display: flex;
        flex-direction: column;
        gap: var(--space-5);
        animation: dashIn 0.36s ease both;
      }

      /* (13/05/2026) 3-column grid for the stat tiles, aligned with
         the "Today's plan" hero above. The tiles render via the
         statTileHtml() component (frontend/src/components/stat-tile.ts). */
      .stats-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: var(--space-4);
      }

      .dash-panel,
      .quick-action {
        position: relative;
        overflow: hidden;
        background: var(--bg-surface);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-sm);
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
        color: var(--brand-600);
        background: rgba(15, 118, 110, 0.1);
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
        .dashboard-workbench { grid-template-columns: 1fr; }
      }

      @media (max-width: 760px) {
        .quick-actions,
        .stats-grid { grid-template-columns: 1fr; }
        .priority-item,
        .recommend-item { grid-template-columns: 1fr; }
        .priority-score { text-align: left; }
      }
    </style>

    <div class="dashboard">
      <div id="dashboard-hero-slot">
        <div class="skeleton" style="height:188px"></div>
      </div>

      <section class="stats-grid" id="dashboard-stats-slot" aria-label="Key metrics">
        ${[1, 2, 3].map(() => `<div class="skeleton" style="height:110px"></div>`).join('')}
      </section>

      <section class="dashboard-workbench">
        <div class="dash-panel">
          <div class="panel-head">
            <div>
              <h3 class="panel-title">${t('dashboard.priorities.title')}</h3>
              <p class="panel-subtitle">${t('dashboard.priorities.subtitle')}</p>
            </div>
            <a href="/content" data-link class="ds-btn ds-btn-secondary">${t('dashboard.priorities.courses')}</a>
          </div>
          <div class="priority-list" id="priority-list">
            ${[1, 2, 3].map(() => `<div class="skeleton sk-card"></div>`).join('')}
          </div>
        </div>

        <div class="focus-stack">
          <div class="dash-panel">
            <div class="panel-head">
              <div>
                <h3 class="panel-title">${t('dashboard.next.title')}</h3>
                <p class="panel-subtitle">${t('dashboard.next.subtitle')}</p>
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
            <h3 class="quick-title">${t('dashboard.quick.concepts.title')}</h3>
            <p class="quick-desc">${t('dashboard.quick.concepts.desc')}</p>
          </div>
        </a>
        <a href="/quiz-ai" data-link class="quick-action">
          <div class="quick-token">QZ</div>
          <div>
            <h3 class="quick-title">${t('dashboard.quick.train.title')}</h3>
            <p class="quick-desc">${t('dashboard.quick.train.desc')}</p>
          </div>
        </a>
        <a href="/tutor" data-link class="quick-action">
          <div class="quick-token">AI</div>
          <div>
            <h3 class="quick-title">${t('dashboard.quick.tutor.title')}</h3>
            <p class="quick-desc">${t('dashboard.quick.tutor.desc')}</p>
          </div>
        </a>
      </section>

      ${studyFlowHtml(null, { compact: true })}
    </div>
  `

  container.appendChild(main)

  const renderLoaded = (path: LearningPath): void => {
    const { total_concepts, mastered, in_progress } = path.overall_progress
    const masteryPct = total_concepts > 0 ? clampPct((mastered / total_concepts) * 100) : 0
    const isFr = (localStorage.getItem('app_lang') || 'en').startsWith('fr')

    // Hero "Today's plan": same component as /path, eyebrow "TODAY'S PLAN".
    // Cascading fallback: next_recommended[0] -> concepts_to_improve[0] ->
    // variant 'done' (nothing to do = everything is mastered). Lets us
    // always have a visible action even after the diagnostic.
    const nextStep =
      path.next_recommended[0] ||
      (path.concepts_to_improve[0]
        ? {
            id: path.concepts_to_improve[0].id,
            name: path.concepts_to_improve[0].name,
            level: 'in_progress',
            category: '',
          }
        : null)

    const heroSlot = main.querySelector('#dashboard-hero-slot')!
    heroSlot.innerHTML = nextStep
      ? nextStepHeroHtml({
          eyebrow: isFr ? 'PLAN DU JOUR' : "TODAY'S PLAN",
          title: nextStep.name,
          description: isFr
            ? 'Concentre-toi sur ce concept pour avancer dans ton parcours adaptatif.'
            : 'Focus on this concept to advance through your adaptive path.',
          primaryCta: {
            href: `/quiz-ai?concept=${encodeURIComponent(nextStep.id)}`,
            label: isFr ? 'Commencer ce concept' : 'Start this concept',
          },
        })
      : nextStepHeroHtml({
          eyebrow: isFr ? 'BRAVO !' : 'WELL DONE!',
          title: isFr ? 'Tous les concepts disponibles maitrises' : 'All available concepts mastered',
          description: isFr
            ? 'Repasse en mode practice pour consolider tes acquis.'
            : 'Revisit in practice mode to consolidate what you have learned.',
          variant: 'done',
        })

    // 3 stat tiles: mastery %, in-progress count, next milestone.
    // Cards #2 and #3 have no "trend" to stay clean (cf. plan #3).
    // Card #3 uses variant: 'text' for a 2-line ellipsis on long
    // concept names (ex: "Newton interpolation with divided differences").
    const milestone =
      path.next_recommended[0]?.name ||
      path.concepts_to_improve[0]?.name ||
      (isFr ? 'Tous maitrises ✓' : 'All mastered ✓')

    const statsSlot = main.querySelector('#dashboard-stats-slot')!
    statsSlot.innerHTML = [
      statTileHtml({
        label: isFr ? 'Maitrise actuelle' : 'Current mastery',
        value: `${masteryPct}%`,
        trend: `${mastered} / ${total_concepts} ${isFr ? 'maitrises' : 'mastered'}`,
      }),
      statTileHtml({
        label: isFr ? 'Concepts en cours' : 'Concepts in progress',
        value: in_progress,
      }),
      statTileHtml({
        label: isFr ? 'Prochaine etape' : 'Next milestone',
        value: milestone,
        variant: 'text',
      }),
    ].join('')

    const priorityList = main.querySelector('#priority-list')!
    if (path.concepts_to_improve.length === 0) {
      priorityList.innerHTML = `<div class="empty-state"><p>${t('dashboard.priorities.empty')}</p></div>`
    } else {
      priorityList.innerHTML = path.concepts_to_improve.slice(0, 5).map((concept) => `
        <article class="priority-item">
          <div>
            <div class="priority-name">${escapeHtml(concept.name)}</div>
            <div class="priority-meta">
              <span>${escapeHtml(concept.status || t('dashboard.priorities.needsPractice'))}</span>
              <span>${concept.mastery.toFixed(0)}% ${t('dashboard.priorities.mastery')}</span>
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
      recommendList.innerHTML = `<div class="empty-state"><p>${t('dashboard.next.empty')}</p></div>`
    } else {
      recommendList.innerHTML = path.next_recommended.slice(0, 4).map((concept) => `
        <article class="recommend-item">
          <div>
            <div class="recommend-name">${escapeHtml(concept.name)}</div>
            <div class="recommend-meta">
              <span>${escapeHtml(concept.category || t('dashboard.next.module'))}</span>
              <span>${t('dashboard.next.level')} ${escapeHtml(tLevel(concept.level || '-'))}</span>
            </div>
          </div>
          <span class="recommend-badge">${t('dashboard.next.ready')}</span>
        </article>
      `).join('')
    }
  }

  if (user) {
    api.getLearningPath(user.id)
      .then(renderLoaded)
      .catch(() => {
        // Empty the 4 dynamic slots: without this, the skeletons would stay
        // animated indefinitely and the user would not know that nothing is coming.
        main.querySelector('#dashboard-hero-slot')!.innerHTML = `<div class="empty-state"><p>${t('dashboard.error.firstQuiz')}</p></div>`
        main.querySelector('#dashboard-stats-slot')!.innerHTML = ''
        main.querySelector('#priority-list')!.innerHTML = `<div class="empty-state"><p>${t('dashboard.error.firstQuiz')}</p></div>`
        main.querySelector('#recommend-list')!.innerHTML = `<div class="empty-state"><p>${t('dashboard.error.afterDiagnostic')}</p></div>`
      })
  }

  shell.setContent(container)
  return shell.element
}
