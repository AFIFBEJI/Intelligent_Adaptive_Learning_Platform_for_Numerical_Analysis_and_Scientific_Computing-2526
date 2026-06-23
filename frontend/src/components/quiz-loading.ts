// ============================================================
// QuizLoading — loading screen + message rotation
// ============================================================
//
// Extracted from quiz-ai.ts (13/05/2026, commit #4-pre-c) along with quiz-history-panel
// to bring quiz-ai.ts under the 1200-line cap.
//
// Three exports:
//   - renderQuizLoading(root, message)     : DOM render with spinner + caption
//   - quizLoadingMessages()                : list of localized messages to rotate
//   - start/stopQuizLoadingRotation()      : drives the subtitle rotation
//
// The rotation targets the selector #loading-subtitle (created by
// renderQuizLoading). The timer is module-level state — the page calls
// start when entering phase 'loading' / 'submitting' and stop
// when leaving it. Idempotent (stop before start; start clears the old
// timer if it exists).
// ============================================================

import { getLang } from '../i18n'

function escapeHtml(s: string): string {
  const div = document.createElement('div')
  div.textContent = s
  return div.innerHTML
}

/**
 * List of rotating messages during generation. The 1st serves as the
 * "static caption" in the initial render, the following ones scroll.
 */
export function quizLoadingMessages(): string[] {
  return getLang() === 'fr'
    ? [
        'Analyse du concept choisi...',
        'Verification des prerequis dans le graphe...',
        'Generation de questions adaptees...',
        'Controle de coherence des reponses...',
        'Calibration de la difficulte...',
        'Presque pret...',
      ]
    : [
        'Analyzing the selected concept...',
        'Checking prerequisites in the learning graph...',
        'Generating questions for your level...',
        'Checking answer consistency...',
        'Calibrating difficulty...',
        'Almost ready...',
      ]
}

/**
 * Minimalist render: spinner + main message + rotating subtitle.
 * The subtitle #loading-subtitle is the DOM targeted by startQuizLoadingRotation.
 *
 * First subtitle = `quiz.loading.generate` in plain text (Generation en cours...);
 * the rotation replaces it every 4s with the messages from quizLoadingMessages().
 */
export function renderQuizLoading(root: HTMLElement, message: string): void {
  injectQuizLoadingStyles()
  // The initial subtitle is intentionally more static than the rotation
  // messages: it serves as a "fallback" if JS does not start the timer.
  const initialSubtitle = getLang() === 'fr' ? 'Generation en cours...' : 'Generating...'
  root.innerHTML = `
    <div class="quiz-ai-page">
      <div class="loading-card">
        <div class="spinner"></div>
        <p>${escapeHtml(message)}</p>
        <small id="loading-subtitle">${escapeHtml(initialSubtitle)}</small>
      </div>
    </div>
  `
}

let _loadingTimer: number | null = null

/**
 * Starts the rotation of the subtitle #loading-subtitle (idempotent: if
 * a timer already exists, we stop it first). 4s cycle.
 */
export function startQuizLoadingRotation(): void {
  stopQuizLoadingRotation()
  let idx = 0
  _loadingTimer = window.setInterval(() => {
    const sub = document.querySelector('#loading-subtitle')
    if (sub) {
      const messages = quizLoadingMessages()
      idx = (idx + 1) % messages.length
      sub.textContent = messages[idx]
    }
  }, 4000)
}

export function stopQuizLoadingRotation(): void {
  if (_loadingTimer !== null) {
    window.clearInterval(_loadingTimer)
    _loadingTimer = null
  }
}

function injectQuizLoadingStyles(): void {
  if (document.querySelector('style[data-ds-quiz-loading]')) return
  const style = document.createElement('style')
  style.dataset.dsQuizLoading = 'true'
  style.textContent = `
    .loading-card { text-align: center; padding: 60px 20px; color: var(--text-secondary); }
    .spinner { width: 40px; height: 40px; border: 3px solid var(--border-default); border-top-color: var(--brand-400); border-radius: 50%; animation: quiz-loading-spin 0.8s linear infinite; margin: 0 auto 20px; }
    @keyframes quiz-loading-spin { to { transform: rotate(360deg); } }
  `
  document.head.appendChild(style)
}
