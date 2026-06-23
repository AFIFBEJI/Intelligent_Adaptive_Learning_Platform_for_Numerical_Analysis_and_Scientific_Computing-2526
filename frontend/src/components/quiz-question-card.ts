// ============================================================
// QuizQuestionCard — DOM d'une question individuelle
// ============================================================
//
// Extrait de quiz-ai.ts (13/05/2026, commit #4-pre-c) — 3e module
// extrait dans le meme commit avec quiz-history-panel et quiz-loading,
// pour ramener quiz-ai.ts sous 1200 lignes.
//
// Signature volontairement positionnelle pour matcher l'appel d'origine :
//   buildQuestionCard(q, idx, onAnswer)
// onAnswer est la SEULE communication retour vers la page : la page
// gere state.answers et refreshProgress. Le composant ne touche jamais
// au state global.
// ============================================================

import { getLang, t, type Lang } from '../i18n'
import type { AiQuizQuestion } from '../api'

function escapeHtml(s: string): string {
  const div = document.createElement('div')
  div.textContent = s
  return div.innerHTML
}

function displayQuestionType(value: string): string {
  if (value === 'mcq') return t('quiz.type.mcq')
  if (value === 'true_false') return t('quiz.type.true_false')
  if (value === 'open') return t('quiz.type.open')
  return value
}

function displayDifficulty(value: string): string {
  if (value === 'facile') return t('quiz.difficulty.facile')
  if (value === 'moyen') return t('quiz.difficulty.moyen')
  if (value === 'difficile') return t('quiz.difficulty.difficile')
  if (value === 'auto') return t('quiz.difficulty.auto')
  return value
}

function trueFalseOptions(lang: Lang): [string, string] {
  return lang === 'fr' ? ['Vrai', 'Faux'] : ['True', 'False']
}

/**
 * Construit le DOM d'une question. Retourne un `<article>` pret a appendre.
 *
 * Communication avec la page : `onAnswer(qid, value)` est appele a chaque
 * fois que la reponse change. `value = null` quand l'utilisateur efface
 * sa reponse (vide le textarea). Pas de mutation directe de state cote
 * composant — c'est la page qui decide ce que ca implique (typiquement
 * state.answers.set/delete + refresh de la barre de progression).
 *
 * Note langue : on n'a plus acces a state.quiz?.language ici. On utilise
 * `q.language || getLang()` ; en pratique les deux coincident toujours
 * (le backend genere les questions dans la langue du quiz), donc pas de
 * regression visible.
 */
export function buildQuestionCard(
  q: AiQuizQuestion,
  idx: number,
  onAnswer: (questionId: number, value: string | null) => void,
): HTMLElement {
  const card = document.createElement('article')
  card.className = 'question-card'
  card.dataset.qid = String(q.id)

  const header = `
    <div class="q-head">
      <span class="q-num">Q${idx + 1}</span>
      <span class="q-type tag-${q.type}">${escapeHtml(displayQuestionType(q.type))}</span>
      <span class="q-diff tag-${q.difficulty}">${displayDifficulty(q.difficulty)}</span>
    </div>
    <div class="q-text">${escapeHtml(q.question)}</div>
  `

  let body = ''
  if (q.type === 'mcq' && q.options) {
    body = `
      <div class="options">
        ${q.options.map((opt, i) => `
          <label class="option">
            <input type="radio" name="q-${q.id}" value="${escapeHtml(opt)}" />
            <span class="option-key">${String.fromCharCode(65 + i)}</span>
            <span class="option-text">${escapeHtml(opt)}</span>
          </label>
        `).join('')}
      </div>
    `
  } else if (q.type === 'true_false') {
    const lang: Lang = (q.language as Lang) || getLang()
    const [trueLabel, falseLabel] = q.options && q.options.length >= 2
      ? [q.options[0], q.options[1]]
      : trueFalseOptions(lang)
    body = `
      <div class="options options-tf">
        <label class="option"><input type="radio" name="q-${q.id}" value="${escapeHtml(trueLabel)}" /> <span>${escapeHtml(trueLabel)}</span></label>
        <label class="option"><input type="radio" name="q-${q.id}" value="${escapeHtml(falseLabel)}" /> <span>${escapeHtml(falseLabel)}</span></label>
      </div>
    `
  } else {
    body = `
      <textarea class="open-answer" name="q-${q.id}" rows="2"
        placeholder="${escapeHtml(t('quiz.answer.placeholder'))}"></textarea>
    `
  }

  card.innerHTML = header + body

  // Liaison des handlers : on emet onAnswer a chaque changement. La page
  // decide quoi faire (typiquement maj state.answers + refreshProgress).
  card.querySelectorAll<HTMLInputElement>(`input[name="q-${q.id}"]`).forEach((el) => {
    el.addEventListener('change', () => onAnswer(q.id, el.value))
  })
  const textarea = card.querySelector<HTMLTextAreaElement>(`textarea[name="q-${q.id}"]`)
  if (textarea) {
    textarea.addEventListener('input', () => {
      const val = textarea.value.trim()
      onAnswer(q.id, val ? val : null)
    })
  }

  return card
}
