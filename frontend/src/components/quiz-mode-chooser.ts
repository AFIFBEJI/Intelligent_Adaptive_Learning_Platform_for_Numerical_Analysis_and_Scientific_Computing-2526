// ============================================================
// QuizChooser + QuizModeChooser — quiz mode choice
// ============================================================
//
// Extracted from quiz-ai.ts (13/05/2026, commit #4-pre-a) to bring
// quiz-ai.ts under the 1200-line cap. The host page was at 1783
// lines after the WIP that added renderModeChooser; this split
// removes ~280 lines (UI + associated CSS, not the transition logic).
//
// Two UI variants, two separate APIs to avoid mixing the
// callbacks of each into a single interface:
//   - QuizChooser      : generic home screen (without a target concept).
//                        3 possible actions: start adaptive, start
//                        practice (-> setup), open history.
//   - QuizModeChooser  : targeted screen when /quiz-ai?concept=<id>. Shows
//                        the concept name and asks Adaptive vs Practice.
//
// Both share the same CSS classes .mode-chooser / .mode-card-big
// (auto-injected once, idempotent). The component is strictly
// presentational: no access to `state`, no direct navigation,
// no API mutation. Everything goes through the callbacks provided by
// the caller — the host page keeps control of the state machine.
// ============================================================

import { api } from '../api'
import { studyFlowHtml } from './study-flow'
import { getLang } from '../i18n'
import type { Concept } from '../api'

// Local concept cache to resolve the target concept name. The
// component can be rendered multiple times; we keep the fetch to a single
// network call for the whole session.
let _conceptsCache: Concept[] | null = null
let _conceptsFetching: Promise<Concept[]> | null = null
async function getCachedConcepts(): Promise<Concept[]> {
  if (_conceptsCache) return _conceptsCache
  if (_conceptsFetching) return _conceptsFetching
  _conceptsFetching = api.getConcepts()
    .then((list) => {
      _conceptsCache = list
      return list
    })
    .catch(() => [])
  return _conceptsFetching
}

function escapeHtml(s: string): string {
  const div = document.createElement('div')
  div.textContent = s
  return div.innerHTML
}

// ------------------------------------------------------------
// QuizChooser — generic home screen (no concept_id)
// ------------------------------------------------------------

export interface QuizChooserOptions {
  /** Error message to display in a banner above the cards. */
  error: string | null
  /** "Adaptive" card clicked: the page must start an adaptive quiz
   *  with the defaults (no setup form). */
  onStartAdaptive: () => void
  /** "Practice" card clicked: the page must transition to the
   *  'setup' phase (form). */
  onStartPractice: () => void
  /** History link in the toolbar: the page must transition to the
   *  'history' phase and load the attempts. */
  onOpenHistory: () => void
}

export function renderQuizChooser(root: HTMLElement, opts: QuizChooserOptions): void {
  injectQuizChooserStyles()
  const labels = chooserLabels(getLang())
  root.innerHTML = `
    <div class="quiz-ai-page">
      <div class="quiz-ai-toolbar">
        <button class="btn-link" id="btn-history">${escapeHtml(labels.history)}</button>
      </div>

      ${studyFlowHtml('practice', { compact: true })}

      ${opts.error ? `<div class="alert-error">${escapeHtml(opts.error)}</div>` : ''}

      <div class="mode-chooser mode-chooser-single">
        <button type="button" class="mode-card-big mode-adaptive" id="card-adaptive">
          <div class="mode-card-icon-wrap"><span class="mode-card-icon" aria-hidden="true">▲</span></div>
          <h3 class="mode-card-title">${escapeHtml(labels.adaptiveTitle)}</h3>
          <p class="mode-card-desc">${escapeHtml(labels.adaptiveTagline)}</p>
          <div class="mode-card-tags">
            <span class="mode-badge mode-badge-good">${escapeHtml(labels.adaptiveBadge)}</span>
          </div>
          <span class="mode-card-cta">${escapeHtml(labels.adaptiveCta)} <span aria-hidden="true">→</span></span>
        </button>
      </div>
    </div>
  `
  root.querySelector('#card-adaptive')?.addEventListener('click', () => opts.onStartAdaptive())
  root.querySelector('#btn-history')?.addEventListener('click', () => opts.onOpenHistory())
  // Single quiz type: the former "practice" card was removed. We keep the
  // onStartPractice option in the interface for backward compatibility but
  // no longer surface it. Reference it to satisfy strict unused checks.
  void opts.onStartPractice
}

// ------------------------------------------------------------
// QuizModeChooser — targeted variant (with concept_id)
// ------------------------------------------------------------

export interface QuizModeChooserOptions {
  /** Target concept (comes from ?concept=<id> in the URL). */
  conceptId: string
  /** Error message to display in a banner. */
  error: string | null
  /** Chosen mode: the page must call api.generateAiQuiz with this mode
   *  and the conceptId, then transition to the 'quiz' phase. */
  onSelectMode: (mode: 'adaptive' | 'practice') => void
  /** "Back to path" link in the toolbar: the page must navigate to /path
   *  AND reset the pendingConceptId. */
  onBackToPath: () => void
}

export function renderQuizModeChooser(root: HTMLElement, opts: QuizModeChooserOptions): void {
  injectQuizChooserStyles()
  const isFr = getLang() === 'fr'
  // Fallback title derived from conceptId: "concept_polynomial_basics"
  // -> "Polynomial Basics". Replaced by the real name once the cache
  // is resolved (cf. the .then() block below).
  const fallbackTitle = opts.conceptId
    .replace(/^concept_/, '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())

  root.innerHTML = `
    <div class="quiz-ai-page">
      <div class="quiz-ai-toolbar">
        <button class="btn-link" id="btn-back-path">← ${escapeHtml(isFr ? 'Retour au parcours' : 'Back to path')}</button>
      </div>

      ${studyFlowHtml('practice', { compact: true })}

      <div class="mode-chooser-header">
        <p class="mode-chooser-eyebrow">${escapeHtml(isFr ? 'Quiz cible' : 'Targeted quiz')}</p>
        <h2 class="mode-chooser-title" id="concept-title">${escapeHtml(fallbackTitle)}</h2>
        <p class="mode-chooser-sub">${escapeHtml(isFr
          ? 'Ton score met a jour ton niveau de maitrise.'
          : 'Your score updates your mastery level.')}</p>
      </div>

      ${opts.error ? `<div class="alert-error">${escapeHtml(opts.error)}</div>` : ''}

      <div class="mode-chooser mode-chooser-single">
        <button type="button" class="mode-card-big mode-adaptive" id="card-adaptive">
          <div class="mode-card-icon-wrap"><span class="mode-card-icon" aria-hidden="true">▲</span></div>
          <h3 class="mode-card-title">${escapeHtml(isFr ? 'Quiz' : 'Quiz')}</h3>
          <p class="mode-card-desc">${escapeHtml(isFr
            ? 'Ton score met a jour ton niveau de maitrise. Recommande pour progresser.'
            : 'Your score updates your mastery level. Recommended to advance.')}</p>
          <div class="mode-card-tags">
            <span class="mode-badge mode-badge-good">${escapeHtml(isFr ? 'Compte pour ma progression' : 'Counts towards progress')}</span>
          </div>
          <span class="mode-card-cta">${escapeHtml(isFr ? 'Demarrer le quiz' : 'Start the quiz')} <span aria-hidden="true">→</span></span>
        </button>
      </div>
    </div>
  `

  // Asynchronous resolution of the real concept name (the fallback derived
  // from the id stays displayed as long as the promise does not resolve).
  void getCachedConcepts()
    .then((concepts) => {
      const found = concepts.find((c) => c.id === opts.conceptId)
      if (found?.name) {
        const el = root.querySelector('#concept-title') as HTMLElement | null
        if (el) el.textContent = found.name
      }
    })
    .catch(() => { /* fallback already shown */ })

  root.querySelector('#btn-back-path')?.addEventListener('click', () => opts.onBackToPath())
  // Single quiz type: always adaptive (counts towards progression).
  root.querySelector('#card-adaptive')?.addEventListener('click', () => opts.onSelectMode('adaptive'))
}

// ------------------------------------------------------------
// i18n labels for the generic chooser
// ------------------------------------------------------------
// We do not go through i18n.ts to stay decoupled: these labels never
// existed as t() keys before this refactor (the original
// code called t('quiz.mode.adaptive.title') etc., which ARE in
// i18n.ts). We re-route them here via an explicit lookup to avoid
// importing t() and its global state into the component.

function chooserLabels(lang: 'fr' | 'en') {
  if (lang === 'fr') {
    return {
      history: 'Voir l\'historique',
      adaptiveTitle: 'Quiz',
      adaptiveTagline: 'Le systeme ajuste les questions a ton niveau, et chaque score met a jour ta progression.',
      adaptiveBadge: 'Compte pour ma progression',
      adaptiveCta: 'Demarrer le quiz',
      practiceTitle: 'Practice',
      practiceTagline: 'Choisis le concept, le nombre de questions et la difficulte. Les scores ne modifient pas ton niveau.',
      practiceBadge: "N'impacte pas mon niveau",
      practiceCta: 'Configurer un quiz',
    }
  }
  return {
    history: 'View history',
    adaptiveTitle: 'Quiz',
    adaptiveTagline: 'The system tailors questions to your level, and every score updates your progress.',
    adaptiveBadge: 'Counts towards progress',
    adaptiveCta: 'Start the quiz',
    practiceTitle: 'Practice',
    practiceTagline: 'Pick a concept, question count and difficulty. Scores do not affect your level.',
    practiceBadge: 'No impact on level',
    practiceCta: 'Configure a quiz',
  }
}

// ------------------------------------------------------------
// CSS injection (idempotent) — shared by the 2 variants
// ------------------------------------------------------------

function injectQuizChooserStyles(): void {
  if (document.querySelector('style[data-ds-quiz-chooser]')) return
  const style = document.createElement('style')
  style.dataset.dsQuizChooser = 'true'
  style.textContent = `
    .mode-chooser {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: var(--space-5);
      margin-top: var(--space-4);
    }
    /* Single quiz type: one centered card, not stretched full-width. */
    .mode-chooser.mode-chooser-single {
      grid-template-columns: minmax(320px, 480px);
      justify-content: center;
    }
    @media (max-width: 768px) {
      .mode-chooser { grid-template-columns: 1fr; }
      .mode-chooser.mode-chooser-single { grid-template-columns: 1fr; }
    }
    .mode-card-big {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      gap: var(--space-3);
      padding: var(--space-6) var(--space-5);
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: var(--radius-lg);
      cursor: pointer;
      text-align: left;
      font-family: inherit;
      transition: transform var(--transition-fast), border-color var(--transition-fast),
                  box-shadow var(--transition-fast), background var(--transition-fast);
      min-height: 280px;
      position: relative;
    }
    .mode-card-big.mode-adaptive { border-top: 4px solid var(--brand-500); }
    .mode-card-big.mode-practice { border-top: 4px solid var(--text-muted); }
    .mode-card-big:hover {
      transform: translateY(-3px);
      border-color: var(--border-emphasis);
      box-shadow: var(--shadow-md);
      background: var(--bg-surface-hover);
    }
    .mode-card-big:active { transform: translateY(-1px); }
    .mode-card-icon-wrap {
      width: 56px; height: 56px;
      border-radius: var(--radius-md);
      display: flex; align-items: center; justify-content: center;
      flex-shrink: 0;
    }
    .mode-adaptive .mode-card-icon-wrap { background: rgba(15,118,110,0.12); color: var(--brand-600); }
    .mode-practice .mode-card-icon-wrap { background: var(--bg-surface-2); color: var(--text-secondary); }
    .mode-card-icon { font-size: 1.6rem; font-weight: 800; }
    .mode-card-title {
      margin: 0;
      font-size: 1.4rem; font-weight: 800;
      color: var(--text-primary);
      letter-spacing: -0.01em;
    }
    .mode-card-desc {
      margin: 0;
      color: var(--text-muted);
      font-size: 0.95rem; line-height: 1.55;
      flex: 1;
    }
    .mode-card-tags { display: flex; flex-wrap: wrap; gap: var(--space-2); }
    .mode-card-cta {
      display: inline-flex; align-items: center; gap: var(--space-2);
      margin-top: var(--space-2);
      padding: 0.6rem 1rem;
      border-radius: var(--radius-md);
      background: var(--brand-gradient);
      color: var(--text-on-inverse);
      font-weight: 700; font-size: 0.92rem;
      transition: gap var(--transition-fast), background var(--transition-fast);
    }
    .mode-card-big:hover .mode-card-cta { gap: var(--space-3); }
    .mode-badge {
      display: inline-flex; align-items: center;
      min-height: 26px; padding: 4px 10px;
      border-radius: var(--radius-md);
      font-size: 0.72rem; font-weight: 800;
      letter-spacing: 0.03em; flex-shrink: 0;
    }
    .mode-badge-good { background: var(--success-bg); color: var(--success); border: 1px solid var(--success-border); }
    .mode-badge-warn { background: var(--warning-bg); color: var(--warning); border: 1px solid var(--warning-border); }
    .mode-chooser-header {
      margin: var(--space-4) auto var(--space-5);
      text-align: center;
      max-width: 640px;
      padding: 0 var(--space-3);
    }
    .mode-chooser-eyebrow {
      font-size: 0.85rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: var(--brand-primary);
      margin-bottom: 8px;
    }
    .mode-chooser-title {
      font-size: 2.2rem;
      font-weight: 800;
      color: var(--text-primary);
      margin: 0 0 12px;
      line-height: 1.2;
      letter-spacing: -0.01em;
    }
    .mode-chooser-sub {
      color: var(--text-muted);
      font-size: 1.05rem;
      max-width: 520px;
      margin: 0 auto;
      line-height: 1.5;
    }
    @media (max-width: 640px) {
      .mode-chooser-title { font-size: 1.7rem; }
      .mode-chooser-sub { font-size: 0.95rem; }
    }
  `
  document.head.appendChild(style)
}
