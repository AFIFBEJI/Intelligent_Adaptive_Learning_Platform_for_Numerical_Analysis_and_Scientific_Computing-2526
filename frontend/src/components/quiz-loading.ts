// ============================================================
// QuizLoading — ecran de chargement + rotation messages
// ============================================================
//
// Extrait de quiz-ai.ts (13/05/2026, commit #4-pre-c) avec quiz-history-panel
// pour faire passer quiz-ai.ts sous le plafond de 1200 lignes.
//
// Trois exports :
//   - renderQuizLoading(root, message)     : DOM render avec spinner + caption
//   - quizLoadingMessages()                : liste de messages localises a faire tourner
//   - start/stopQuizLoadingRotation()      : pilote la rotation du sous-titre
//
// La rotation cible le selecteur #loading-subtitle (cree par
// renderQuizLoading). Le timer est un module-level state — la page appelle
// start au moment d'entrer en phase 'loading' / 'submitting' et stop
// quand elle en sort. Idempotent (stop avant start ; start clear l'ancien
// timer s'il existe).
// ============================================================

import { getLang } from '../i18n'

function escapeHtml(s: string): string {
  const div = document.createElement('div')
  div.textContent = s
  return div.innerHTML
}

/**
 * Liste de messages rotatifs pendant la generation. Le 1er sert de
 * "static caption" au render initial, les suivants defilent.
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
 * Render minimaliste : spinner + message principal + sous-titre rotatif.
 * Le sous-titre #loading-subtitle est le DOM cible par startQuizLoadingRotation.
 *
 * Premier sous-titre = `quiz.loading.generate` en clair (Generation en cours...) ;
 * la rotation le remplace toutes les 4s par les messages de quizLoadingMessages().
 */
export function renderQuizLoading(root: HTMLElement, message: string): void {
  injectQuizLoadingStyles()
  // Le sous-titre initial est volontairement plus statique que les messages
  // de rotation : il sert de "fallback" si JS ne demarre pas le timer.
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
 * Demarre la rotation du sous-titre #loading-subtitle (idempotent : si
 * un timer existe deja, on le stoppe d'abord). Cycle de 4s.
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
