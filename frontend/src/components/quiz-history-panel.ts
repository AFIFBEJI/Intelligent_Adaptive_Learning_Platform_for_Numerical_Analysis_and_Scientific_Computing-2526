// ============================================================
// QuizHistoryPanel — table of previous attempts
// ============================================================
//
// Extracted from quiz-ai.ts (13/05/2026, commit #4-pre-c) so quiz-ai.ts
// goes under the 1200-line cap. The host page loads the history
// via api.listAiAttempts() (or an equivalent endpoint) and passes the
// table to the component; clicks on the "details" buttons emit
// onSelectAttempt(id) — the page then handles the detail fetch and
// the transition to the feedback phase.
//
// Private helpers (escapeHtml, formatDate, gradeColor) duplicated from
// quiz-ai.ts: they were no longer used elsewhere after the extraction
// of feedback in #4-pre-b. gradeColor in particular is used here to color
// the score, formatDate to localize the date according to getLang().
// ============================================================

import { getLang, t } from '../i18n'
import type { AiAttemptSummary } from '../api'

function escapeHtml(s: string): string {
  const div = document.createElement('div')
  div.textContent = s
  return div.innerHTML
}

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleString(getLang() === 'fr' ? 'fr-FR' : 'en-US', {
      day: '2-digit',
      month: '2-digit',
      year: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return iso
  }
}

function gradeColor(score: number): string {
  if (score >= 90) return '#16a34a'
  if (score >= 75) return '#22c55e'
  if (score >= 60) return '#eab308'
  if (score >= 40) return '#f97316'
  return '#ef4444'
}

export interface QuizHistoryPanelOptions {
  /** List of attempts, already loaded by the caller. */
  history: AiAttemptSummary[]
  /** Click on "back": the page switches to phase 'chooser'. */
  onBackToChooser: () => void
  /** Click on a "details" button: the page retrieves the detail of the
   *  attempt (api.getAiAttempt) and switches to phase 'feedback'.
   *  Returns a Promise so the caller can handle an error. */
  onSelectAttempt: (id: number) => Promise<void>
}

export function renderQuizHistoryPanel(
  root: HTMLElement,
  opts: QuizHistoryPanelOptions,
): void {
  injectQuizHistoryPanelStyles()

  root.innerHTML = `
    <div class="quiz-ai-page">
      <header class="quiz-ai-header">
        <h1>${escapeHtml(t('quiz.history.title'))}</h1>
        <button class="btn-link" id="btn-back-setup">${escapeHtml(t('quiz.history.back'))}</button>
      </header>

      ${
        opts.history.length === 0
          ? `<p class="empty">${escapeHtml(t('quiz.history.empty'))}</p>`
          : `
        <table class="history-table">
          <thead>
            <tr>
              <th>${escapeHtml(t('quiz.history.date'))}</th>
              <th>${escapeHtml(t('quiz.history.quiz'))}</th>
              <th>${escapeHtml(t('quiz.history.score'))}</th>
              <th>${escapeHtml(t('quiz.history.time'))}</th>
              <th>${escapeHtml(t('quiz.history.result'))}</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            ${opts.history.map((h) => `
              <tr>
                <td>${formatDate(h.date_tentative)}</td>
                <td>${escapeHtml(h.quiz_titre)}</td>
                <td style="color:${gradeColor(h.score)}"><strong>${h.score.toFixed(0)}</strong></td>
                <td>${h.temps_reponse}s</td>
                <td>${escapeHtml(h.grade_label ?? '-')}</td>
                <td><button class="btn-link" data-id="${h.id}">${escapeHtml(t('quiz.history.details'))}</button></td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      `
      }
    </div>
  `

  root.querySelector('#btn-back-setup')?.addEventListener('click', () => opts.onBackToChooser())

  root.querySelectorAll<HTMLButtonElement>('button.btn-link[data-id]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const id = parseInt(btn.dataset.id!, 10)
      void opts.onSelectAttempt(id)
    })
  })
}

function injectQuizHistoryPanelStyles(): void {
  if (document.querySelector('style[data-ds-quiz-history-panel]')) return
  const style = document.createElement('style')
  style.dataset.dsQuizHistoryPanel = 'true'
  style.textContent = `
    .history-table { width: 100%; background: var(--bg-surface); border-radius: 8px; overflow: hidden; border-collapse: collapse; }
    .history-table th, .history-table td { padding: 12px 16px; text-align: left; border-bottom: 1px solid var(--border-subtle); }
    .history-table th { background: var(--bg-surface-hover); font-weight: 600; font-size: 0.9rem; color: var(--text-secondary); }
    .empty { text-align: center; color: var(--text-muted); padding: 40px; }
  `
  document.head.appendChild(style)
}
