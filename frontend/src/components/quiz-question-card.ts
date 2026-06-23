// ============================================================
// QuizQuestionCard — DOM of an individual question
// ============================================================
//
// Extracted from quiz-ai.ts (13/05/2026, commit #4-pre-c) — 3rd module
// extracted in the same commit along with quiz-history-panel and quiz-loading,
// to bring quiz-ai.ts under 1200 lines.
//
// Signature intentionally positional to match the original call:
//   buildQuestionCard(q, idx, onAnswer)
// onAnswer is the ONLY communication back to the page: the page
// manages state.answers and refreshProgress. The component never touches
// the global state.
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
  if (value === 'numeric') return t('quiz.type.numeric')
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
 * Builds the DOM of a question. Returns an `<article>` ready to append.
 *
 * Communication with the page: `onAnswer(qid, value)` is called every
 * time the answer changes. `value = null` when the user clears
 * their answer (empties the textarea). No direct state mutation on the
 * component side — it is the page that decides what it implies (typically
 * state.answers.set/delete + refresh of the progress bar).
 *
 * Language note: we no longer have access to state.quiz?.language here. We use
 * `q.language || getLang()`; in practice both always coincide
 * (the backend generates the questions in the quiz language), so no
 * visible regression.
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
  } else if (q.type === 'numeric') {
    // Numeric answer: a single value typed by the student, graded
    // deterministically server-side (no AI). Easy to type for maths.
    body = `
      <input type="text" inputmode="decimal" class="numeric-answer" name="q-${q.id}"
        autocomplete="off" spellcheck="false"
        placeholder="${escapeHtml(t('quiz.answer.numeric'))}" />
    `
  } else {
    body = `
      <textarea class="open-answer" name="q-${q.id}" rows="2"
        placeholder="${escapeHtml(t('quiz.answer.placeholder'))}"></textarea>
    `
  }

  card.innerHTML = header + body

  // Handler binding: we emit onAnswer on every change. The page
  // decides what to do (typically update state.answers + refreshProgress).
  // Radio buttons (mcq / true_false): emit the chosen value on change.
  card.querySelectorAll<HTMLInputElement>(`input[type="radio"][name="q-${q.id}"]`).forEach((el) => {
    el.addEventListener('change', () => onAnswer(q.id, el.value))
  })
  // Free-text answer (open question).
  const textarea = card.querySelector<HTMLTextAreaElement>(`textarea[name="q-${q.id}"]`)
  if (textarea) {
    textarea.addEventListener('input', () => {
      const val = textarea.value.trim()
      onAnswer(q.id, val ? val : null)
    })
  }
  // Numeric answer (single value).
  const numInput = card.querySelector<HTMLInputElement>(`input.numeric-answer[name="q-${q.id}"]`)
  if (numInput) {
    numInput.addEventListener('input', () => {
      const val = numInput.value.trim()
      onAnswer(q.id, val ? val : null)
    })
  }

  return card
}
