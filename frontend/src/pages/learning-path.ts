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
    pageSubtitle: t('learningPath.subtitle'),
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
      @keyframes pulseGlow { 0%, 100% { box-shadow: 0 0 0 0 rgba(15, 118, 110, 0.35); } 50% { box-shadow: 0 0 0 12px rgba(15, 118, 110, 0); } }

      .path-page {
        display: flex;
        flex-direction: column;
        gap: var(--space-5);
        animation: pathIn 0.35s ease both;
      }

      /* (12/05/2026) Hero "Next step" — vraie guidance adaptative.
         Met en avant LE prochain concept recommande par l'algo.
         Sans ce hero, l'etudiant voit juste une liste et clique au
         hasard ; avec, il a une direction claire. */
      .next-step-hero {
        background: linear-gradient(135deg, rgba(15, 118, 110, 0.18), rgba(20, 184, 166, 0.08));
        border: 1px solid rgba(15, 118, 110, 0.45);
        border-radius: var(--radius-md);
        padding: var(--space-6);
        text-align: center;
        position: relative;
      }
      .next-step-hero::before {
        content: '';
        position: absolute;
        inset: -1px;
        border-radius: var(--radius-md);
        pointer-events: none;
        animation: pulseGlow 2.4s ease-out infinite;
      }
      .next-step-eyebrow {
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.14em;
        color: var(--brand-primary);
        margin-bottom: 10px;
      }
      .next-step-title {
        font-size: 2rem;
        font-weight: 800;
        color: var(--text-primary);
        margin: 0 0 10px;
        letter-spacing: -0.01em;
        line-height: 1.15;
      }
      .next-step-sub {
        color: var(--text-muted);
        max-width: 620px;
        margin: 0 auto var(--space-4);
        line-height: 1.55;
      }
      .next-step-actions {
        display: flex;
        gap: 12px;
        justify-content: center;
        flex-wrap: wrap;
      }
      .next-step-cta {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 14px 28px;
        background: var(--brand-gradient, linear-gradient(135deg, #0f766e, #14b8a6));
        color: var(--text-on-inverse, #fff);
        border-radius: 10px;
        font-weight: 800;
        text-decoration: none;
        font-size: 1.05rem;
        box-shadow: var(--shadow-md, 0 4px 14px rgba(15, 118, 110, 0.35));
        transition: transform 0.15s, box-shadow 0.15s;
      }
      .next-step-cta:hover { transform: translateY(-2px); box-shadow: 0 8px 22px rgba(15, 118, 110, 0.45); }
      .next-step-secondary {
        display: inline-flex;
        align-items: center;
        padding: 13px 22px;
        background: transparent;
        border: 1.5px solid rgba(255, 255, 255, 0.18);
        color: var(--text-primary);
        border-radius: 10px;
        font-weight: 600;
        text-decoration: none;
        transition: all 0.15s;
      }
      .next-step-secondary:hover { border-color: var(--brand-primary); color: var(--brand-primary); }
      .next-step-hero-done { background: linear-gradient(135deg, rgba(34, 197, 94, 0.18), rgba(16, 185, 129, 0.06)); border-color: rgba(34, 197, 94, 0.45); }
      @media (max-width: 640px) {
        .next-step-title { font-size: 1.4rem; }
        .next-step-cta { width: 100%; justify-content: center; }
        .next-step-secondary { width: 100%; justify-content: center; }
      }

      /* (12/05/2026) "Why locked?" inline disclosure pour expliquer
         visuellement les prerequis manquants — rend l'algorithme
         adaptatif TRANSPARENT au lieu d'un generique "locked". */
      .why-locked-btn {
        margin-left: 8px;
        padding: 2px 10px;
        font-size: 0.75rem;
        font-weight: 600;
        background: transparent;
        border: 1px solid var(--border-default);
        border-radius: 6px;
        color: var(--text-muted);
        cursor: pointer;
        transition: all 0.15s;
      }
      .why-locked-btn:hover { color: var(--brand-primary); border-color: var(--brand-primary); }
      .prereq-detail {
        margin-top: 8px;
        padding: 12px 14px;
        background: var(--bg-surface-2, rgba(255, 255, 255, 0.04));
        border: 1px solid var(--border-default);
        border-radius: 8px;
        font-size: 0.85rem;
      }
      .prereq-list {
        list-style: none;
        padding: 0;
        margin: 8px 0 0;
        display: flex;
        flex-direction: column;
        gap: 6px;
      }
      .prereq-item {
        display: grid;
        grid-template-columns: 1fr auto auto;
        gap: 12px;
        padding: 6px 10px;
        border-radius: 6px;
        background: rgba(255, 255, 255, 0.02);
        align-items: center;
      }
      .prereq-item.ok { color: var(--success, #22c55e); }
      .prereq-item.todo { color: var(--warning, #f59e0b); }
      .prereq-mastery { font-weight: 700; font-variant-numeric: tabular-nums; }
      .prereq-status { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.8; }
      .overall-bar,
      .module-section {
        background: var(--bg-surface);
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
        color: var(--brand-600);
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
        color: var(--brand-600);
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
      .status-ready { color: var(--brand-600); background: rgba(15, 118, 110, 0.1); border: 1px solid var(--border-emphasis); }
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
      .concept-prereq.ready { color: var(--brand-600); }
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
        background: var(--bg-surface);
        font-size: var(--text-xs);
        font-weight: var(--font-weight-extrabold);
        text-decoration: none;
        white-space: nowrap;
      }
      .btn-start { color: var(--text-on-inverse); background: var(--brand-gradient); border-color: rgba(15, 118, 110, 0.42); }
      .btn-review { color: var(--warning); background: var(--warning-bg); border-color: var(--warning-border); }
      .empty-state {
        min-height: 260px;
        display: grid;
        place-items: center;
        gap: var(--space-4);
        padding: var(--space-8);
        color: var(--text-muted);
        text-align: center;
        background: var(--bg-surface);
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

    // ============================================================
    // (12/05/2026) HERO "Next recommended step" — guidance adaptative
    // ============================================================
    // Avant ce hero, le user voyait juste une liste de concepts et pouvait
    // cliquer aleatoirement n'importe lequel : la plateforme n'avait pas
    // l'air "guidee". Maintenant, on met en avant LE prochain concept
    // recommande par l'algo (`path.next_recommended[0]` ou, a defaut, le
    // 1er `concepts_to_improve`). C'est ce qui rend la guidance VISIBLE.
    const isFr = (localStorage.getItem('app_lang') || 'en').startsWith('fr')
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

    const heroHtml = nextStep
      ? `
        <section class="next-step-hero">
          <div class="next-step-eyebrow">${isFr ? 'PROCHAINE ETAPE RECOMMANDEE' : 'YOUR RECOMMENDED NEXT STEP'}</div>
          <h2 class="next-step-title">${escapeHtml(nextStep.name)}</h2>
          <p class="next-step-sub">${isFr
              ? "L'algorithme adaptatif pointe ce concept comme la suite logique de ta progression. Commence ici pour un parcours guide."
              : 'The adaptive engine picks this concept as the logical next step in your journey. Start here for a guided path.'}</p>
          <div class="next-step-actions">
            <a href="/quiz-ai?concept=${encodeURIComponent(nextStep.id)}" data-link class="next-step-cta">
              ${isFr ? 'Commencer ce concept' : 'Start this concept'} <span aria-hidden="true">→</span>
            </a>
            <a href="/content?concept=${encodeURIComponent(nextStep.id)}" data-link class="next-step-secondary">
              ${isFr ? "Lire la theorie d'abord" : 'Read the theory first'}
            </a>
          </div>
        </section>
      `
      : `
        <section class="next-step-hero next-step-hero-done">
          <div class="next-step-eyebrow">${isFr ? "BRAVO !" : 'WELL DONE!'}</div>
          <h2 class="next-step-title">${isFr ? "Tous les concepts disponibles sont maitrises" : 'All available concepts are mastered'}</h2>
          <p class="next-step-sub">${isFr
              ? 'Tu peux maintenant repasser des concepts en mode practice pour les consolider.'
              : 'You can now revisit concepts in practice mode to consolidate.'}</p>
        </section>
      `

    pathContent.innerHTML = `
      ${heroHtml}

      <section class="overall-bar">
        <div class="overall-header">
          <div>
            <div class="overall-label">${t('learningPath.overall')}</div>
            <div class="overall-caption">${t('learningPath.overall.caption')}</div>
          </div>
          <div class="overall-pct">${pct}%</div>
        </div>
        <div class="progress-track">
          <div class="progress-fill" style="width:${pct}%"></div>
        </div>
        <div class="overall-stats">
          <div class="overall-stat"><strong>${mastered}</strong>${t('learningPath.mastered')}</div>
          <div class="overall-stat"><strong>${in_progress}</strong>${t('learningPath.inprogress')}</div>
          <div class="overall-stat"><strong>${Math.max(total_concepts - mastered - in_progress, 0)}</strong>${t('learningPath.todiscover')}</div>
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
                  <div class="module-count">${modMastered}/${moduleConcepts.length} ${t('learningPath.conceptsMastered')}</div>
                </div>
              </div>
              <div class="module-progress">${modPct}${t('learningPath.percentComplete')}</div>
            </div>
            ${moduleConcepts.map((concept) => {
              const status = getStatus(concept.id)
              const mastery = getMastery(concept.id)
              const statusToken = status === 'mastered' ? 'OK' : status === 'progress' ? 'IP' : status === 'ready' ? 'GO' : 'LK'
              const statusCls = status === 'mastered' ? 'status-mastered' : status === 'progress' ? 'status-progress' : status === 'ready' ? 'status-ready' : 'status-locked'
              const barCls = mastery >= 70 ? 'bar-green' : mastery > 0 ? 'bar-orange' : 'bar-gray'

              // (12/05/2026) Pour les concepts LOCKED, on ajoute un bouton
              // "Why locked?" qui appelle GET /graph/concepts/<id>/prerequisites
              // au clic et affiche EXACTEMENT quels concepts il faut maitriser
              // d'abord (avec leur mastery actuel). Ca rend l'algo
              // transparent au lieu du generique "Prerequisites not met".
              return `
                <div class="concept-row" data-concept-id="${escapeHtml(concept.id)}">
                  <div class="concept-status ${statusCls}">${statusToken}</div>
                  <div class="concept-info">
                    <div class="concept-name">${escapeHtml(concept.name)}</div>
                    ${status === 'locked' ? `
                      <div class="concept-prereq">
                        ${t('learningPath.prereqLocked')}
                        <button type="button"
                                class="why-locked-btn"
                                data-prereq-of="${escapeHtml(concept.id)}">
                          ${isFr ? 'Pourquoi ?' : 'Why?'}
                        </button>
                      </div>
                      <div class="prereq-detail" id="prereq-${escapeHtml(concept.id)}" hidden></div>
                    ` : ''}
                    ${status === 'ready' ? `<div class="concept-prereq ready">${t('learningPath.ready')}</div>` : ''}
                  </div>
                  <div class="mastery-bar-wrap">
                    <div class="mastery-bar ${barCls}" style="width:${mastery}%"></div>
                  </div>
                  <div class="mastery-pct">${mastery > 0 ? mastery.toFixed(0) + '%' : '-'}</div>
                  ${status === 'ready' ? `<a href="/quiz-ai?concept=${encodeURIComponent(concept.id)}" data-link class="action-btn btn-start">${t('learningPath.cta.quiz')}</a>` : ''}
                  ${status === 'progress' ? `<a href="/quiz-ai?concept=${encodeURIComponent(concept.id)}" data-link class="action-btn btn-review">${t('learningPath.cta.quiz')}</a>` : ''}
                </div>
              `
            }).join('')}
          </section>
        `
      }).join('')}
    `

    // ============================================================
    // (12/05/2026) Wire-up "Why locked?" - revele les prerequis
    // ============================================================
    // Quand l'etudiant clique sur "Pourquoi ?" a cote d'un concept
    // verrouille, on appelle /graph/concepts/<id>/prerequisites pour
    // recuperer la liste des prerequis Neo4j, on les croise avec son
    // mastery courant, et on affiche pour chacun :
    //   - mastery actuel (%)
    //   - statut (acquis si >=70, sinon a travailler)
    // Le panneau toggle a chaque clic (lazy load la 1ere fois).
    pathContent.querySelectorAll<HTMLButtonElement>('.why-locked-btn').forEach((btn) => {
      btn.addEventListener('click', async (e) => {
        e.preventDefault()
        e.stopPropagation()
        const conceptId = btn.dataset.prereqOf
        if (!conceptId) return
        const detailEl = pathContent.querySelector(`#prereq-${conceptId}`) as HTMLElement | null
        if (!detailEl) return
        // Toggle si deja charge.
        if (detailEl.dataset.loaded === 'true') {
          detailEl.hidden = !detailEl.hidden
          return
        }
        detailEl.hidden = false
        detailEl.innerHTML = `<em>${isFr ? 'Chargement...' : 'Loading...'}</em>`
        try {
          const prereqs = await api.getConceptPrerequisites(conceptId)
          if (!prereqs.length) {
            detailEl.innerHTML = `<em>${isFr
              ? 'Aucun prerequis declare ; verifie que ton niveau global est suffisant.'
              : 'No declared prerequisite; check that your overall level is high enough.'}</em>`
          } else {
            detailEl.innerHTML = `
              <strong>${isFr ? 'Tu dois d\'abord maitriser (>=70%) :' : 'You must first master (>=70%):'}</strong>
              <ul class="prereq-list">
                ${prereqs.map((p) => {
                  const pm = masteryMap[p.id] || 0
                  const ok = pm >= 70
                  const status = ok
                    ? (isFr ? 'acquis' : 'mastered')
                    : (isFr ? 'a travailler' : 'to work')
                  return `<li class="prereq-item ${ok ? 'ok' : 'todo'}">
                    <span class="prereq-name">${escapeHtml(p.name)}</span>
                    <span class="prereq-mastery">${pm.toFixed(0)}%</span>
                    <span class="prereq-status">${status}</span>
                  </li>`
                }).join('')}
              </ul>
            `
          }
          detailEl.dataset.loaded = 'true'
        } catch (err) {
          detailEl.innerHTML = `<em>${isFr ? 'Erreur de chargement.' : 'Loading error.'}</em>`
          console.error('[learning-path] prereq fetch failed', err)
        }
      })
    })
  }).catch(() => {
    main.querySelector('#path-content')!.innerHTML = `
      <div class="empty-state">
        <p>${t('learningPath.empty')}</p>
        <a href="/quiz-ai" data-link class="ds-btn ds-btn-primary">${t('learningPath.cta.quiz')}</a>
      </div>
    `
  })

  shell.setContent(container)
  return shell.element
}
