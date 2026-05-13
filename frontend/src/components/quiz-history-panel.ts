// ============================================================
// QuizHistoryPanel — table des tentatives precedentes
// ============================================================
//
// Extrait de quiz-ai.ts (13/05/2026, commit #4-pre-c) pour que quiz-ai.ts
// passe sous le plafond de 1200 lignes. La page hote charge l'historique
// via api.listAiAttempts() (ou un endpoint equivalent) et passe le
// tableau au composant ; les clics sur les boutons "details" emettent
// onSelectAttempt(id) — la page se charge alors du fetch detail et de
// la transition vers la phase feedback.
//
// Helpers prives (escapeHtml, formatDate, gradeColor) duplique depuis
// quiz-ai.ts : ils n'etaient plus utilises ailleurs apres l'extraction
// de feedback en #4-pre-b. gradeColor en particulier sert ici a colorer
// le score, formatDate a localiser la date selon getLang().
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
  /** Liste des tentatives, deja chargee par l'appelant. */
  history: AiAttemptSummary[]
  /** Clic sur "back" : la page bascule vers la phase 'chooser'. */
  onBackToChooser: () => void
  /** Clic sur un bouton "details" : la page recupere le detail de la
   *  tentative (api.getAiAttempt) et bascule vers la phase 'feedback'.
   *  Renvoie une Promise pour que l'appelant puisse gerer une erreur. */
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
