// ============================================================
// Dynamic Quiz Page + Feedback Card
// ============================================================
// Three successive states in the same page:
//   1. SETUP    -> form (concept/topic, nb of questions, difficulty)
//   2. QUIZ     -> display of the questions + entering the answers
//   3. FEEDBACK -> detailed post-submission feedback card
// + history panel (past attempts) accessible at any time.
// ============================================================

import { api } from '../api'
import { createAppShell } from '../components/app-shell'
import { renderQuizChooser, renderQuizModeChooser } from '../components/quiz-mode-chooser'
import { studyFlowHtml } from '../components/study-flow'
import { renderQuizFeedbackCard } from '../components/quiz-feedback-card'
import { renderQuizHistoryPanel } from '../components/quiz-history-panel'
import {
  quizLoadingMessages,
  renderQuizLoading,
  startQuizLoadingRotation,
  stopQuizLoadingRotation,
} from '../components/quiz-loading'
import { buildQuestionCard } from '../components/quiz-question-card'
import { getLang, languageName, t, type Lang } from '../i18n'
import { loadKatex, renderLatexIn } from '../utils/latex'
import type { Concept } from '../api'

// Cache of the concepts to avoid refetching them on each renderSetup
let _cachedConcepts: Concept[] | null = null
let _conceptsFetching: Promise<Concept[]> | null = null
async function getCachedConcepts(): Promise<Concept[]> {
  if (_cachedConcepts) return _cachedConcepts
  if (_conceptsFetching) return _conceptsFetching
  _conceptsFetching = api.getConcepts().then(c => {
    _cachedConcepts = c
    return c
  }).catch(() => [])
  return _conceptsFetching
}
function populateConceptsSelect(root: HTMLElement): void {
  const sel = root.querySelector('#topic') as HTMLSelectElement | null
  if (!sel) return
  if (!_cachedConcepts || _cachedConcepts.length === 0) return
  // If already populated (>1 option), we do not redo it
  if (sel.options.length > 1) return
  const groups: Record<string, Concept[]> = {}
  for (const c of _cachedConcepts) {
    const cat = c.category || 'Autre'
    groups[cat] = groups[cat] || []
    groups[cat].push(c)
  }
  for (const [cat, list] of Object.entries(groups)) {
    const og = document.createElement('optgroup')
    og.label = cat
    for (const c of list) {
      const opt = document.createElement('option')
      opt.value = c.id
      opt.dataset.name = c.name
      opt.textContent = c.name
      og.appendChild(opt)
    }
    sel.appendChild(og)
  }
}
import type {
  AiQuizResponse,
  AiQuizSubmitResponse,
  AiAttemptSummary,
  AiStudentAnswer,
} from '../api'

// MathJax is loaded globally by index.html (as in tutor.ts)
declare const MathJax: {
  typesetPromise?: (elements?: Element[]) => Promise<void>
} | undefined

// ------------------------------------------------------------
// Local page state
// ------------------------------------------------------------
// 'chooser' = welcome screen with 2 large cards (Path / Practice)
// 'setup'   = free practice form (full filters)
type Phase = 'chooser' | 'mode_chooser' | 'setup' | 'loading' | 'quiz' | 'submitting' | 'feedback' | 'history'

interface PageState {
  phase: Phase
  quiz: AiQuizResponse | null
  answers: Map<number, string>
  startedAt: number
  result: AiQuizSubmitResponse | null
  history: AiAttemptSummary[]
  historyOpen: boolean
  error: string | null
  // (12/05/2026) Mode CHOSEN by the user via the toggle during the
  // quiz. Initialized to the generated quiz's mode, can be flipped at any
  // time. Sent at submit as mode_override. If null we do not send
  // an override (=> backend respects the Quiz's original mode).
  selectedMode: 'adaptive' | 'practice' | null
  // (12/05/2026) Concept_id arrives via ?concept= in the URL, stored while
  // waiting for the student to choose Adaptive or Practice. Once
  // the mode is chosen, we generate the quiz then reset this field to null.
  pendingConceptId: string | null
  // next_recommended[0] re-fetch after submit, feeds the "Next up" hero (commit #4).
  nextConcept: { id: string; name: string } | null
}

const state: PageState = {
  phase: 'chooser',
  quiz: null,
  answers: new Map(),
  startedAt: 0,
  result: null,
  history: [],
  historyOpen: false,
  error: null,
  selectedMode: null,
  pendingConceptId: null,
  nextConcept: null,
}

// ------------------------------------------------------------
// Utilities
// ------------------------------------------------------------
function escapeHtml(s: string): string {
  const div = document.createElement('div')
  div.textContent = s
  return div.innerHTML
}

function displayDifficulty(value: string): string {
  if (value === 'facile') return t('quiz.difficulty.facile')
  if (value === 'moyen') return t('quiz.difficulty.moyen')
  if (value === 'difficile') return t('quiz.difficulty.difficile')
  if (value === 'auto') return t('quiz.difficulty.auto')
  return value
}

// displayQuestionType + trueFalseOptions extracted into quiz-question-card.ts
// (commit #4-pre-c, 13/05/2026).

function quizLanguage(): Lang {
  return state.quiz?.language || getLang()
}

async function typesetMath(root: HTMLElement): Promise<void> {
  if (typeof MathJax !== 'undefined' && MathJax?.typesetPromise) {
    try {
      await MathJax.typesetPromise([root])
    } catch (err) {
      console.warn('MathJax typeset failed:', err)
    }
  }
}

// ------------------------------------------------------------
// Rendering — SETUP phase
// ------------------------------------------------------------
// The language selector of the quiz page has been removed: it is useless
// to have 3 toggles (sidebar + topbar + quiz setup). The language is managed
// only from the sidebar. The new questions/feedbacks follow
// `localStorage.app_lang` which is updated from the sidebar.

// ============================================================
// renderChooser : delegation to the quiz-mode-chooser.ts component
// ============================================================
// The rendering lives in frontend/src/components/quiz-mode-chooser.ts since
// commit #4-pre-a (13/05/2026). This function stays here as glue
// to the page's state machine: it adapts the UI callbacks
// (onStartAdaptive, onStartPractice, onOpenHistory) into phase
// transitions and handler calls.
// ============================================================
function renderChooser(root: HTMLElement): void {
  renderQuizChooser(root, {
    error: state.error,
    onStartAdaptive: () => {
      state.error = null
      void handleGenerateAdaptive(root)
    },
    onStartPractice: () => {
      state.error = null
      state.phase = 'setup'
      renderAll(root)
    },
    onOpenHistory: () => {
      void (async () => {
        state.phase = 'history'
        await loadHistory()
        renderAll(root)
      })()
    },
  })
}

// ============================================================
// renderModeChooser : delegation to the quiz-mode-chooser.ts component
// ============================================================
// "targeted" variant of the chooser (the user arrives via ?concept=X).
// Glue to the state machine: onSelectMode triggers launchTargetedQuiz,
// onBackToPath resets the pendingConceptId before navigation.
// ============================================================
function renderModeChooser(root: HTMLElement): void {
  const conceptId = state.pendingConceptId
  if (!conceptId) {
    // Defense: if we arrive on the mode_chooser phase without a pending
    // concept (pathological case), we fall back on the generic chooser
    // instead of crashing the render.
    state.phase = 'chooser'
    renderAll(root)
    return
  }
  renderQuizModeChooser(root, {
    conceptId,
    error: state.error,
    onSelectMode: (mode) => {
      void launchTargetedQuiz(root, mode)
    },
    onBackToPath: () => {
      state.pendingConceptId = null
      window.location.href = '/path'
    },
  })
}

// ============================================================
// launchTargetedQuiz : API call + transition to the quiz phase
// ============================================================
// Helper common to the 2 buttons of the mode chooser above. Uses
// state.pendingConceptId, generates the quiz in the chosen mode with
// difficulty="auto" (the backend picks based on the current mastery).
// ============================================================
async function launchTargetedQuiz(
  root: HTMLElement,
  mode: 'adaptive' | 'practice',
): Promise<void> {
  const conceptId = state.pendingConceptId
  if (!conceptId) {
    state.error = t('quiz.error.generate')
    state.phase = 'chooser'
    renderAll(root)
    return
  }
  state.phase = 'loading'
  state.error = null
  renderAll(root)
  try {
    const quiz = await api.generateAiQuiz({
      concept_id: conceptId,
      topic: null,
      n_questions: 5,
      difficulty: 'auto',
      question_types: ['mcq', 'true_false'],
      language: getLang(),
      mode,
    })
    state.quiz = quiz
    state.answers = new Map()
    state.startedAt = Date.now()
    state.selectedMode = mode
    state.pendingConceptId = null
    state.phase = 'quiz'
    renderAll(root)
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err)
    state.error = message || t('quiz.error.generate')
    // We return to the mode chooser so it can retry or change
    // mode, instead of falling back on the main chooser which
    // would lose the selected concept.
    state.phase = 'mode_chooser'
    renderAll(root)
  }
}

// ============================================================
// renderSetup : free practice form (filters)
// ============================================================
// Displays ONLY the filters form + a back button to
// the choice screen. No adaptive card here anymore.
// ============================================================
function renderSetup(root: HTMLElement): void {
  const isFr = getLang() === 'fr'
  const qtypeHelp = isFr
    ? 'Coche les formats de questions que tu veux dans ton quiz.'
    : 'Check the question formats you want in your quiz.'
  // qtypeHelp is inline with the label, no longer on a separate line
  void qtypeHelp
  root.innerHTML = `
    <div class="quiz-ai-page">
      <div class="quiz-ai-toolbar">
        <button class="btn-link" id="btn-back-chooser">← ${escapeHtml(isFr ? 'Retour' : 'Back')}</button>
        <button class="btn-link" id="btn-history">${escapeHtml(t('quiz.history'))}</button>
      </div>

      ${studyFlowHtml('practice', { compact: true })}

      ${state.error ? `<div class="alert-error">${escapeHtml(state.error)}</div>` : ''}

      <!-- ============================================================
           Header simple : titre + sous-titre + petit badge subtil
           Pas de carte coloree autour, pas de border-left agressive.
           ============================================================ -->
      <header class="practice-setup-head">
        <div>
          <h2 class="practice-setup-title">${escapeHtml(t('quiz.mode.practice.title'))}</h2>
          <p class="practice-setup-sub">${escapeHtml(t('quiz.mode.practice.tagline'))}</p>
        </div>
        <span class="practice-setup-badge">${escapeHtml(t('quiz.mode.practice.badge'))}</span>
      </header>

      <form id="setup-form" class="practice-form">
        <!-- Section 1 : sujet -->
        <div class="form-section">
          <label class="form-label" for="topic">${escapeHtml(t('quiz.setup.concept'))}</label>
          <select id="topic" class="form-control">
            <option value="">${escapeHtml(t('quiz.setup.autoConcept'))}</option>
          </select>
        </div>

        <!-- Section 2 : nombre + difficulte (2 colonnes) -->
        <div class="form-row form-row-2">
          <div class="form-section">
            <label class="form-label" for="n_questions">${escapeHtml(t('quiz.setup.questions'))}</label>
            <select id="n_questions" class="form-control">
              <option value="3">3</option>
              <option value="5" selected>5</option>
              <option value="7">7</option>
              <option value="10">10</option>
            </select>
          </div>

          <div class="form-section">
            <label class="form-label" for="difficulty">${escapeHtml(t('quiz.setup.difficulty'))}</label>
            <select id="difficulty" class="form-control">
              <option value="auto">${escapeHtml(t('quiz.difficulty.auto'))}</option>
              <option value="facile">${escapeHtml(t('quiz.difficulty.facile'))}</option>
              <option value="moyen" selected>${escapeHtml(t('quiz.difficulty.moyen'))}</option>
              <option value="difficile">${escapeHtml(t('quiz.difficulty.difficile'))}</option>
            </select>
          </div>
        </div>

        <!-- Section 3 : types de questions (chips compacts, multi-select) -->
        <div class="form-section">
          <label class="form-label">${escapeHtml(t('quiz.setup.types'))}</label>
          <div class="qtype-chips">
            <label class="qtype-chip">
              <input type="checkbox" name="qtype" value="mcq" checked />
              <span class="qtype-chip-text">${escapeHtml(t('quiz.type.mcq'))}</span>
            </label>
            <label class="qtype-chip">
              <input type="checkbox" name="qtype" value="true_false" checked />
              <span class="qtype-chip-text">${escapeHtml(t('quiz.type.true_false'))}</span>
            </label>
            <label class="qtype-chip">
              <input type="checkbox" name="qtype" value="numeric" />
              <span class="qtype-chip-text">${escapeHtml(t('quiz.type.numeric'))}</span>
            </label>
          </div>
        </div>

        <!-- Footer : warning subtil + CTA -->
        <div class="practice-form-footer">
          <p class="practice-warn-inline">
            <span aria-hidden="true">⚠</span> ${escapeHtml(t('quiz.mode.practice.warn'))}
          </p>
          <button type="submit" class="btn-primary practice-cta">
            ${escapeHtml(t('quiz.mode.practice.cta'))}
          </button>
        </div>
      </form>
    </div>
  `

  root.querySelector('#btn-back-chooser')?.addEventListener('click', () => {
    state.phase = 'chooser'
    renderAll(root)
  })

  root.querySelector('#setup-form')?.addEventListener('submit', async (e) => {
    e.preventDefault()
    state.error = null
    await handleGeneratePractice(root)
  })

  root.querySelector('#btn-history')?.addEventListener('click', async () => {
    state.phase = 'history'
    await loadHistory()
    renderAll(root)
  })

  // Pre-selection via URL: /quiz-ai?concept=concept_lagrange
  const urlConceptId = new URLSearchParams(window.location.search).get('concept')
  if (urlConceptId) {
    void getCachedConcepts().then(concepts => {
      const c = concepts.find(x => x.id === urlConceptId || x.name === urlConceptId)
      if (!c) return
      const sel = root.querySelector('#topic') as HTMLSelectElement | null
      if (!sel) return
      const tryFill = () => {
        const opt = Array.from(sel.options).find(o => o.value === c.id)
        if (opt) { sel.value = c.id; return true }
        return false
      }
      if (!tryFill()) {
        setTimeout(tryFill, 50)
      }
    })
  }
}

// ============================================================
// Path mode (adaptive): no filters, the backend chooses everything.
// We force concept_id=null and difficulty='auto' so the service
// picks the weak concept and the difficulty adapted to the mastery.
// ============================================================
async function handleGenerateAdaptive(root: HTMLElement): Promise<void> {
  state.phase = 'loading'
  renderAll(root)

  try {
    const quiz = await api.generateAiQuiz({
      concept_id: null,
      topic: null,
      n_questions: 5,
      difficulty: 'auto',
      // Reasonable MCQ + T/F mix for a quick path quiz.
      question_types: ['mcq', 'true_false'],
      language: getLang(),
      mode: 'adaptive',
    })
    state.quiz = quiz
    state.answers = new Map()
    state.startedAt = Date.now()
    state.phase = 'quiz'
    renderAll(root)
  } catch (err: any) {
    state.error = err?.message || t('quiz.error.generate')
    // On a path-mode error, we return to the chooser
    // (not to setup) since the adaptive mode does not go through this form.
    state.phase = 'chooser'
    renderAll(root)
  }
}

// ============================================================
// Free practice mode (practice): the student chooses everything.
// The backend will store mode='practice' on the Quiz, so the submit
// will NOT touch the mastery.
// ============================================================
async function handleGeneratePractice(root: HTMLElement): Promise<void> {
  await handleGenerate(root, 'practice')
}

async function handleGenerate(root: HTMLElement, mode: 'adaptive' | 'practice'): Promise<void> {
  const conceptId = (root.querySelector('#topic') as HTMLSelectElement)?.value.trim()
  const n = parseInt(
    (root.querySelector('#n_questions') as HTMLSelectElement)?.value || '5',
    10,
  )
  const difficulty = (
    root.querySelector('#difficulty') as HTMLSelectElement
  )?.value as 'auto' | 'facile' | 'moyen' | 'difficile'

  const types: Array<'mcq' | 'open' | 'true_false' | 'numeric'> = []
  document
    .querySelectorAll<HTMLInputElement>('input[name="qtype"]:checked')
    .forEach((cb) => {
      types.push(cb.value as 'mcq' | 'open' | 'true_false' | 'numeric')
    })

  if (types.length === 0) {
    state.error = t('quiz.error.types')
    renderAll(root)
    return
  }

  state.phase = 'loading'
  renderAll(root)

  try {
    const quiz = await api.generateAiQuiz({
      concept_id: conceptId || null,
      topic: null,
      n_questions: n,
      difficulty,
      question_types: types,
      language: getLang(),
      mode,
    })
    state.quiz = quiz
    state.answers = new Map()
    state.startedAt = Date.now()
    state.phase = 'quiz'
    renderAll(root)
  } catch (err) {
    state.error =
      err instanceof Error ? err.message : t('quiz.error.generate')
    state.phase = 'setup'
    renderAll(root)
  }
}

// ------------------------------------------------------------
// Rendering — LOADING phase
// ------------------------------------------------------------
// renderLoading delegates to quiz-loading.ts (commit #4-pre-c, 13/05/2026).
function renderLoading(root: HTMLElement, message: string): void {
  renderQuizLoading(root, message)
}

// ------------------------------------------------------------
// Rendering — QUIZ phase
// ------------------------------------------------------------
function renderQuiz(root: HTMLElement): void {
  const quiz = state.quiz!
  const answered = state.answers.size
  const total = quiz.questions.length
  // (12/05/2026) `selectedMode` is what the student CHOOSES during the
  // quiz (via the toggle below). That is the mode that will be sent to the
  // backend as `mode_override`. If null, we fall back on the generated
  // quiz's mode.
  const effectiveMode = state.selectedMode || quiz.mode || 'adaptive'
  const isPractice = effectiveMode === 'practice'

  root.innerHTML = `
    <div class="quiz-ai-page">
      ${isPractice ? `
        <div class="practice-banner">
          <span aria-hidden="true">⚠</span>
          <span>${escapeHtml(t('quiz.mode.practice.warn'))}</span>
        </div>
      ` : ''}

      <header class="quiz-ai-header">
        <h1>${escapeHtml(quiz.titre)}</h1>
        <p class="sub">
          ${escapeHtml(t('quiz.meta.module'))}: <strong>${escapeHtml(quiz.module)}</strong>
          <span class="score-meta-sep">/</span>
          ${escapeHtml(t('quiz.meta.difficulty'))}: <strong>${escapeHtml(displayDifficulty(quiz.difficulte))}</strong>
          <span class="score-meta-sep">/</span>
          ${escapeHtml(t('quiz.meta.language'))}: <strong>${escapeHtml(languageName(quizLanguage()))}</strong>
          <span class="score-meta-sep">/</span>
          ${total} ${escapeHtml(t('quiz.meta.questions'))}
        </p>
        <div class="progress-bar">
          <div class="progress-fill" style="width: ${(answered / total) * 100}%"></div>
        </div>
        <small>${answered} / ${total} ${escapeHtml(t('quiz.meta.answered'))}</small>
      </header>

      <div id="questions-list"></div>

      <div class="quiz-actions">
        <button class="btn-secondary" id="btn-cancel">${escapeHtml(t('quiz.action.cancel'))}</button>
        <button class="btn-primary" id="btn-submit" ${
          answered < total ? 'disabled' : ''
        }>
          ${escapeHtml(t('quiz.action.submit'))}
        </button>
      </div>
    </div>
  `

  const list = root.querySelector('#questions-list') as HTMLElement
  // Shared callback: the question-card component emits a (qid, value)
  // on each change. The page updates state.answers and the progress
  // bar. This avoids the component having to import state.
  const onAnswer = (qid: number, value: string | null): void => {
    if (value === null) state.answers.delete(qid)
    else state.answers.set(qid, value)
    refreshProgress()
  }
  quiz.questions.forEach((q, idx) => list.appendChild(buildQuestionCard(q, idx, onAnswer)))

  root.querySelector('#btn-cancel')?.addEventListener('click', () => {
    if (confirm(t('quiz.confirm.leave'))) {
      state.quiz = null
      state.answers.clear()
      // After cancelling a quiz, we return to the choice screen
      // (the user can re-choose a different mode).
      state.phase = 'chooser'
      renderAll(root)
    }
  })

  root.querySelector('#btn-submit')?.addEventListener('click', async () => {
    await handleSubmit(root)
  })

  typesetMath(list)
}

// buildQuestionCard extracted into quiz-question-card.ts
// (commit #4-pre-c, 13/05/2026). The page provides an onAnswer callback
// to stay in control of the state.

function refreshProgress(): void {
  const total = state.quiz?.questions.length ?? 0
  const answered = state.answers.size
  const bar = document.querySelector<HTMLElement>('.progress-fill')
  if (bar) bar.style.width = `${(answered / total) * 100}%`
  const counter = document.querySelector<HTMLElement>('.quiz-ai-header small')
  if (counter) counter.textContent = `${answered} / ${total} ${t('quiz.meta.answered')}`
  const submit = document.querySelector('#btn-submit') as HTMLButtonElement | null
  if (submit) submit.disabled = answered < total
}

// Best-effort fetch of the next concept (adaptive only, silent on error).
async function fetchNextConceptBestEffort(mode?: string): Promise<{ id: string; name: string } | null> {
  if (mode !== 'adaptive') return null
  try {
    const user = JSON.parse(localStorage.getItem('user') || 'null')
    if (!user?.id) return null
    const path = await api.getLearningPath(user.id)
    const n = path.next_recommended[0]
    return n ? { id: n.id, name: n.name } : null
  } catch {
    return null
  }
}

async function handleSubmit(root: HTMLElement): Promise<void> {
  if (!state.quiz) return

  const payload: AiStudentAnswer[] = Array.from(state.answers.entries()).map(
    ([question_id, answer]) => ({ question_id, answer }),
  )

  state.phase = 'submitting'
  renderAll(root)

  try {
    const result = await api.submitAiQuiz(state.quiz.quiz_id, {
      answers: payload,
      temps_reponse: Math.round((Date.now() - state.startedAt) / 1000),
      language: state.quiz.language || getLang(),
      // If the student flipped the toggle during the quiz, we send
      // mode_override. Otherwise (null) the backend respects the generated mode.
      mode_override: state.selectedMode || undefined,
    })
    state.result = result
    state.nextConcept = await fetchNextConceptBestEffort(result.mode)
    state.phase = 'feedback'
    renderAll(root)
  } catch (err) {
    state.error =
      err instanceof Error ? err.message : t('quiz.error.submit')
    state.phase = 'quiz'
    renderAll(root)
  }
}

// Rendering — FEEDBACK phase. Component: quiz-feedback-card.ts (#4-pre-b).
// Latent bug: onResetToSetup does not change state.phase => render after
// resetPage crashes on state.result!. Backlog note.
function renderFeedback(root: HTMLElement): void {
  const conceptNames = new Map<string, string>()
  for (const c of (_cachedConcepts || [])) conceptNames.set(c.id, c.name)
  renderQuizFeedbackCard(root, {
    result: state.result!,
    conceptNames,
    nextConcept: state.nextConcept,
    targetConceptId: state.quiz?.concept_id ?? null,
    onResetToSetup: () => {
      resetPage()
      renderAll(root)
    },
    onTryAgain: () => {
      resetPage()
      // After a quiz, return to the choice screen to re-select
      // the mode (path or practice) before a new quiz.
      state.phase = 'chooser'
      renderAll(root)
    },
  })
}

// ------------------------------------------------------------
// Rendering — HISTORY phase
// ------------------------------------------------------------
async function loadHistory(): Promise<void> {
  try {
    state.history = await api.listAiAttempts()
  } catch (err) {
    state.error = err instanceof Error ? err.message : 'Unable to load history.'
    state.history = []
  }
}

// renderHistory delegates to quiz-history-panel.ts (commit #4-pre-c, 13/05/2026).
function renderHistory(root: HTMLElement): void {
  renderQuizHistoryPanel(root, {
    history: state.history,
    onBackToChooser: () => {
      state.phase = 'chooser'
      renderAll(root)
    },
    onSelectAttempt: async (id) => {
      try {
        state.result = await api.getAiAttempt(id)
        state.nextConcept = null // no hero CTA on a past attempt
        state.phase = 'feedback'
        renderAll(root)
      } catch (err) {
        state.error = err instanceof Error ? err.message : 'Unable to load attempt details.'
        renderAll(root)
      }
    },
  })
}

function resetPage(): void {
  state.quiz = null
  state.result = null
  state.answers.clear()
  state.startedAt = 0
  state.error = null
}

// ------------------------------------------------------------
// Main router
// ------------------------------------------------------------
// Rotating messages + spinner extracted into quiz-loading.ts
// (commit #4-pre-c, 13/05/2026).

function renderAll(root: HTMLElement): void {
  // Re-render KaTeX after each renderAll (questions, options, feedback...)
  // KaTeX auto-render is idempotent, we can call it safely every time.
  setTimeout(() => renderLatexIn(root), 0)

  // Start/stop the message rotation depending on the phase.
  // Implementation in quiz-loading.ts.
  if (state.phase === 'loading' || state.phase === 'submitting') {
    startQuizLoadingRotation()
  } else {
    stopQuizLoadingRotation()
  }

  switch (state.phase) {
    case 'chooser':
      renderChooser(root)
      // We preload the concepts in the background: if the user clicks
      // on "Practice", the dropdown will already be populated.
      void getCachedConcepts()
      break
    case 'mode_chooser':
      renderModeChooser(root)
      break
    case 'setup':
      renderSetup(root)
      void getCachedConcepts().then(() => populateConceptsSelect(root))
      break
    case 'loading':
      renderLoading(root, quizLoadingMessages()[0])
      break
    case 'quiz':
      renderQuiz(root)
      break
    case 'submitting':
      renderLoading(root, t('quiz.loading.submit'))
      break
    case 'feedback':
      renderFeedback(root)
      break
    case 'history':
      renderHistory(root)
      break
  }
}

// ------------------------------------------------------------
// Styles (inline — we keep the page self-contained)
// ------------------------------------------------------------
const STYLES = `
<style>
.quiz-ai-page { max-width: 1040px; margin: 0 auto; padding: 0; font-family: var(--font-sans); color: var(--text-primary); }
.quiz-ai-header h1 { margin: 0 0 4px; font-size: 1.5rem; font-weight: 800; letter-spacing: -0.02em; }
.quiz-ai-header .sub { color: var(--text-muted); margin: 0 0 12px; font-size: 0.9rem; }
.quiz-ai-toolbar { display: flex; justify-content: flex-end; margin: 0 0 var(--space-4); }
.adaptive-note { display:flex; align-items:flex-start; gap: 10px; margin: 0 0 var(--space-4); padding: 14px 16px; border-radius: var(--radius-md); background: rgba(15,118,110,0.08); border: 1px solid rgba(15,118,110,0.22); color: var(--text-secondary); font-size: 0.9rem; line-height: 1.45; }
.adaptive-note strong { color: var(--brand-600); white-space: nowrap; }
.quiz-language-panel { display:flex; align-items:center; justify-content:space-between; gap: 16px; margin: 0 0 var(--space-4); padding: 16px; border-radius: var(--radius-md); background: var(--bg-surface); border: 1px solid var(--border-default); }
.quiz-language-panel strong { display:block; color: var(--text-primary); font-size: 0.95rem; margin-bottom: 2px; }
.quiz-language-panel small { color: var(--text-muted); line-height: 1.4; }
.quiz-lang-segment { display:grid; grid-template-columns: 1fr 1fr; min-width: 240px; gap: 3px; padding: 3px; border-radius: var(--radius-md); border: 1px solid var(--border-default); background: var(--bg-surface-2); }
.quiz-lang-btn { min-height: 44px; border: 0; border-radius: var(--radius-sm); color: var(--text-muted); background: transparent; cursor: pointer; display:flex; flex-direction:column; align-items:center; justify-content:center; gap: 1px; transition: background var(--transition-fast), color var(--transition-fast); }
.quiz-lang-btn strong { margin: 0; color: currentColor; font-size: 0.82rem; letter-spacing: 0.04em; }
.quiz-lang-btn span { font-size: 0.72rem; font-weight: 700; }
.quiz-lang-btn:hover { color: var(--text-primary); }
.quiz-lang-btn:disabled { cursor: wait; opacity: 0.72; }
.quiz-lang-btn.active { color: #06111f; background: linear-gradient(135deg, #e0f2fe, #7dd3fc 60%, #86efac); box-shadow: var(--shadow-xs); }
.btn-link { background: none; border: 1px solid var(--border-default); color: var(--text-secondary); cursor: pointer; font-size: 0.85rem; text-decoration: none; padding: 6px 14px; border-radius: var(--radius-md); transition: all var(--transition-fast); font-weight: 500; }
.btn-link:hover { border-color: var(--border-emphasis); color: var(--brand-600); background: rgba(15,118,110,0.06); }
.btn-primary { background: var(--brand-gradient); color: var(--text-on-inverse); border: none; padding: 10px 18px; border-radius: 8px; font-size: 1rem; font-weight: 700; cursor: pointer; }
.btn-primary:disabled { background: var(--bg-surface-2); cursor: not-allowed; }
.btn-secondary { background: var(--bg-surface-2); color: var(--text-primary); border: 1px solid var(--border-default); padding: 10px 18px; border-radius: 8px; cursor: pointer; }
.alert-error { background: var(--danger-bg); color: var(--danger); padding: 12px 16px; border-radius: 8px; margin-bottom: 16px; }
.setup-card { background: var(--bg-surface); padding: var(--space-6); border: 1px solid var(--border-default); border-radius: var(--radius-lg); display: flex; flex-direction: column; gap: var(--space-5); }

/* Chooser styles -> components/quiz-mode-chooser.ts (auto-injected). */

/* ============================================================
   Free practice setup: airy layout, clear structure
   ============================================================ */
.practice-setup-head {
  display: flex; align-items: flex-start; justify-content: space-between;
  gap: var(--space-4);
  margin: var(--space-2) 0 var(--space-5);
  flex-wrap: wrap;
}
.practice-setup-title {
  margin: 0 0 4px;
  font-size: 1.4rem; font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}
.practice-setup-sub {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.9rem; line-height: 1.5;
  max-width: 580px;
}
.practice-setup-badge {
  display: inline-flex; align-items: center;
  padding: 4px 10px; border-radius: var(--radius-md);
  font-size: 0.7rem; font-weight: 700;
  background: var(--warning-bg);
  color: var(--warning);
  border: 1px solid var(--warning-border);
  flex-shrink: 0;
  letter-spacing: 0.02em;
}

.practice-form {
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  display: flex; flex-direction: column; gap: var(--space-4);
}
.form-section { display: flex; flex-direction: column; gap: 6px; }
.form-row { display: flex; gap: var(--space-4); }
.form-row-2 > * { flex: 1; min-width: 0; }
@media (max-width: 560px) { .form-row { flex-direction: column; } }
.form-label {
  font-size: 0.85rem; font-weight: 700;
  color: var(--text-secondary);
  letter-spacing: 0.01em;
}
.form-control {
  width: 100%;
  padding: 0.65rem 0.85rem;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  background: var(--bg-surface);
  color: var(--text-primary);
  font-size: 0.92rem;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}
.form-control:focus {
  outline: none;
  border-color: var(--brand-500);
  box-shadow: var(--shadow-focus);
}

/* Question types: compact horizontal chips instead of large cards */
.qtype-chips {
  display: flex; flex-wrap: wrap; gap: 8px;
}
.qtype-chip {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 8px 14px;
  border: 1px solid var(--border-default);
  border-radius: 999px;
  background: var(--bg-surface);
  cursor: pointer;
  transition: all var(--transition-fast);
  user-select: none;
}
.qtype-chip:hover {
  border-color: var(--border-emphasis);
  background: var(--bg-surface-hover);
}
.qtype-chip input[type="checkbox"] {
  width: 14px; height: 14px;
  margin: 0;
  accent-color: var(--brand-500);
  cursor: pointer;
}
.qtype-chip-text {
  font-size: 0.88rem; font-weight: 600;
  color: var(--text-secondary);
}
.qtype-chip:has(input:checked) {
  background: rgba(15,118,110,0.08);
  border-color: var(--brand-500);
}
.qtype-chip:has(input:checked) .qtype-chip-text {
  color: var(--brand-600);
}

/* Footer: subtle inline warning + aligned CTA */
.practice-form-footer {
  display: flex; align-items: center; justify-content: space-between;
  gap: var(--space-4);
  padding-top: var(--space-3);
  border-top: 1px solid var(--border-subtle);
  flex-wrap: wrap;
}
.practice-warn-inline {
  margin: 0; flex: 1; min-width: 220px;
  font-size: 0.82rem; line-height: 1.45;
  color: var(--text-muted);
}
.practice-warn-inline span[aria-hidden] {
  color: var(--warning);
  margin-right: 4px;
}
.practice-cta {
  min-width: 200px;
  flex-shrink: 0;
}

/* ============================================================
   "Pedagogical mode" cards: Path (adaptive) vs Practice (practice)
   ============================================================ */
.mode-card { background: var(--bg-surface); border: 1px solid var(--border-default); border-radius: var(--radius-lg); padding: var(--space-5); margin-bottom: var(--space-5); display: flex; flex-direction: column; gap: var(--space-4); transition: border-color var(--transition-fast), box-shadow var(--transition-fast); }
.mode-card.mode-adaptive { border-left: 4px solid var(--brand-500); }
.mode-card.mode-practice { border-left: 4px solid var(--accent-amber); }
.mode-card:hover { box-shadow: var(--shadow-sm); }
.mode-card-head { display:flex; align-items:flex-start; gap: 14px; flex-wrap: wrap; }
.mode-card-head > div { flex: 1; min-width: 220px; }
.mode-icon { display:inline-flex; align-items:center; justify-content:center; width: 38px; height: 38px; border-radius: var(--radius-md); font-size: 1.1rem; font-weight: 800; flex-shrink: 0; }
.mode-adaptive .mode-icon { background: rgba(15,118,110,0.12); color: var(--brand-600); }
.mode-practice .mode-icon { background: rgba(183,121,31,0.12); color: var(--accent-amber); }
.mode-title { margin: 0 0 4px; font-size: 1.1rem; font-weight: 800; color: var(--text-primary); }
.mode-tag { margin: 0; color: var(--text-muted); font-size: 0.88rem; line-height: 1.5; }
.mode-badge { display:inline-flex; align-items:center; min-height: 26px; padding: 4px 10px; border-radius: var(--radius-md); font-size: 0.72rem; font-weight: 800; letter-spacing: 0.03em; flex-shrink: 0; }
.mode-badge-good { background: var(--success-bg); color: var(--success); border: 1px solid var(--success-border); }
.mode-badge-warn { background: var(--warning-bg); color: var(--warning); border: 1px solid var(--warning-border); }
.btn-mode { align-self: flex-start; min-width: 220px; }
.practice-warn-row { padding: 10px 14px; border-radius: var(--radius-md); background: var(--warning-bg); color: var(--warning); border: 1px solid var(--warning-border); font-size: 0.85rem; line-height: 1.5; }
/* During the quiz, we remind the practice mode at the top of the screen */
.practice-banner { padding: 10px 14px; margin-bottom: var(--space-4); border-radius: var(--radius-md); background: var(--warning-bg); color: var(--warning); border: 1px solid var(--warning-border); font-size: 0.9rem; font-weight: 600; display:flex; align-items:center; gap: 8px; }

/* Feedback styles -> components/quiz-feedback-card.ts. */

.field { display: flex; flex-direction: column; gap: 6px; }
.field > span, .field > legend { font-weight: 600; color: var(--text-secondary); font-size: 0.95rem; }
.field input, .field select, .field textarea {
  padding: 10px 12px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  font-size: 0.95rem;
  background: var(--bg-surface-2);
  color: var(--text-primary);
  font-family: inherit;
  transition: border-color var(--transition-fast), background var(--transition-fast);
}
.field input:focus, .field select:focus, .field textarea:focus {
  outline: none;
  border-color: var(--border-focus);
  background: var(--bg-surface-hover);
  box-shadow: var(--shadow-focus);
}
.field input::placeholder, .field textarea::placeholder { color: var(--text-subtle); }
.field select option { background: var(--bg-surface-2); color: var(--text-primary); }
.field input[type="checkbox"], .field input[type="radio"] {
  accent-color: var(--brand-500);
  width: 16px; height: 16px;
  cursor: pointer;
}
.option input[type="radio"] { accent-color: var(--brand-500); }
.field small { color: var(--text-muted); font-size: 0.85rem; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.field label { display: flex; align-items: center; gap: 6px; font-weight: 400; cursor: pointer; }
.qtype-field {
  margin: 0;
  padding: 0;
  border: 0;
}
.qtype-field legend {
  margin-bottom: var(--space-1);
  color: var(--text-primary);
  font-weight: 800;
}
.qtype-help {
  margin: 0 0 var(--space-3);
  color: var(--text-muted);
  font-size: var(--text-sm);
}
.qtype-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-3);
}
.qtype-option {
  position: relative;
  min-height: 78px;
  display: grid;
  grid-template-columns: 22px 38px minmax(0, 1fr);
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  background: var(--bg-surface-2);
  cursor: pointer;
  transition: border-color var(--transition-fast), background var(--transition-fast), transform var(--transition-fast);
}
.qtype-option:hover {
  border-color: var(--border-emphasis);
  background: var(--bg-surface-hover);
  transform: translateY(-1px);
}
.qtype-option:focus-within {
  border-color: var(--border-focus);
  box-shadow: var(--shadow-focus);
}
.qtype-option input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}
.qtype-check {
  width: 22px;
  height: 22px;
  display: grid;
  place-items: center;
  border: 2px solid var(--border-default);
  border-radius: var(--radius-sm);
  background: var(--bg-surface);
  transition: background var(--transition-fast), border-color var(--transition-fast);
}
.qtype-check::after {
  content: "";
  width: 10px;
  height: 6px;
  border-left: 2px solid var(--text-on-inverse);
  border-bottom: 2px solid var(--text-on-inverse);
  transform: rotate(-45deg) scale(0);
  transition: transform var(--transition-fast);
}
.qtype-option:has(input:checked) {
  border-color: var(--border-emphasis);
  background: rgba(15,118,110,0.1);
}
.qtype-option:has(input:checked) .qtype-check {
  border-color: var(--brand-600);
  background: var(--brand-600);
}
.qtype-option:has(input:checked) .qtype-check::after {
  transform: rotate(-45deg) scale(1);
}
.qtype-mark {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  border-radius: var(--radius-md);
  color: var(--brand-600);
  background: rgba(15,118,110,0.12);
  border: 1px solid rgba(15,118,110,0.2);
  font-size: var(--text-xs);
  font-weight: 800;
}
.qtype-copy {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.qtype-copy strong {
  min-width: 0;
  color: var(--text-primary);
  font-size: var(--text-sm);
  line-height: 1.25;
}
.qtype-copy small {
  color: var(--text-muted);
  font-size: 0.76rem;
  line-height: 1.35;
}
.progress-bar { background: var(--bg-surface-2); height: 8px; border-radius: 4px; margin-top: 12px; overflow: hidden; }
.progress-fill { background: var(--brand-500); height: 100%; transition: width 0.3s; }
.question-card { background: var(--bg-surface); border: 1px solid var(--border-default); border-radius: 10px; padding: 20px; margin: 16px 0; }
.q-head { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
.q-num { background: var(--brand-500); color: white; padding: 4px 10px; border-radius: 4px; font-weight: 700; font-size: 0.85rem; }
.q-type, .q-diff { padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }
.tag-mcq { background: rgba(15,118,110,0.12); color: var(--brand-600); }
.tag-true_false { background: var(--warning-bg); color: var(--warning); }
.tag-open { background: var(--success-bg); color: var(--success); }
.tag-facile { background: var(--success-bg); color: var(--success); }
.tag-moyen { background: var(--warning-bg); color: var(--warning); }
.tag-difficile { background: var(--danger-bg); color: var(--danger); }
.q-text { font-size: 1.05rem; margin-bottom: 14px; line-height: 1.5; }
.options { display: flex; flex-direction: column; gap: 8px; }
.options-tf { flex-direction: row; }
.option { display: flex; align-items: center; gap: 10px; padding: 10px 14px; border: 1px solid var(--border-default); border-radius: 8px; cursor: pointer; transition: all 0.15s; }
.option:hover { background: var(--bg-surface-hover); border-color: var(--brand-400); }
.option input[type="radio"] { margin: 0; }
.option-key { background: var(--bg-surface-2); padding: 2px 8px; border-radius: 4px; font-weight: 700; font-size: 0.85rem; }
.open-answer { width: 100%; padding: 10px; border: 1px solid var(--border-default); border-radius: 6px; font-family: inherit; font-size: 0.95rem; resize: vertical; }
.numeric-answer { width: 220px; max-width: 100%; padding: 11px 14px; border: 1.5px solid var(--border-default); border-radius: 8px; font-family: 'JetBrains Mono','Consolas',monospace; font-size: 1.05rem; }
.numeric-answer:focus { outline: none; border-color: #0f766e; box-shadow: 0 0 0 3px rgba(15,118,110,0.12); }
.quiz-actions { display: flex; justify-content: space-between; margin-top: 24px; gap: 12px; }
/* .feedback-card/.score-ring/.fb-*/.eval-* -> quiz-feedback-card.ts.
   .history-table/.empty -> quiz-history-panel.ts.
   .loading-card/.spinner -> quiz-loading.ts. */
.progress-bar { height: 4px; background: var(--bg-surface-2); border-radius: 999px; overflow: hidden; margin-top: 8px; }
.progress-fill { height: 100%; background: var(--brand-gradient); transition: width 0.3s ease; border-radius: 999px; }
.q-card { background: var(--bg-surface); border: 1px solid var(--border-default); border-radius: 12px; padding: 20px; margin-bottom: 16px; }
.q-head { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; font-size: 0.85rem; color: var(--text-muted); }
.q-num { font-weight: 700; color: var(--text-primary); }
.q-tag { padding: 2px 10px; border-radius: 999px; font-size: 0.75rem; font-weight: 600; }
.tag-mcq { background: rgba(15,118,110,0.12); color: var(--brand-600); }
.quiz-ai-page { max-width: 1040px; }
.quiz-ai-header,
.setup-card,
.question-card,
.loading-card,
.history-table {
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}
.quiz-ai-header { padding: var(--space-5); margin-bottom: var(--space-5); }
.setup-card,
.question-card { padding: var(--space-6); }
.btn-primary,
.btn-secondary,
.btn-link {
  min-height: 40px;
  border-radius: var(--radius-md);
  font-weight: var(--font-weight-bold);
}
.btn-primary { color: var(--text-on-inverse); background: var(--brand-gradient); box-shadow: var(--shadow-glow-brand); }
.btn-primary:disabled {
  color: var(--text-subtle);
  background: var(--bg-surface-2);
  box-shadow: none;
}
.btn-secondary,
.btn-link {
  color: var(--text-primary);
  background: var(--bg-surface-2);
  border: 1px solid var(--border-default);
}
@media (max-width: 720px) {
  .quiz-language-panel { align-items: stretch; flex-direction: column; }
  .quiz-lang-segment { min-width: 0; width: 100%; }
  .grid-2,
  .qtype-grid { grid-template-columns: 1fr; }
  .options-tf { flex-direction: column; }
}
</style>
`

// ------------------------------------------------------------
// Page entry point
// ------------------------------------------------------------
export function QuizAiPage(): HTMLElement {
  const shell = createAppShell({
    activeRoute: '/quiz-ai',
    pageTitle: t('quiz.title'),
    pageSubtitle: t('quiz.subtitle'),
  })
  const container = document.createElement('div')
  shell.setContent(container)

  if (!document.querySelector('style[data-quiz-ai-styles]')) {
    const style = document.createElement('style')
    style.dataset.quizAiStyles = 'true'
    style.innerHTML = STYLES.replace(/^<style>|<\/style>$/g, '')
    document.head.appendChild(style)
  }

  void loadKatex()
  resetPage()
  // ============================================================
  // ?concept=... -> mode chooser PAGE (12/05/2026)
  // ============================================================
  // When the student clicks "Go to quizzes" on a concept from /path,
  // we send them here with ?concept=<id>. Rather than directly launching
  // a quiz, we first display a page that proposes the 2 modes:
  //   - Adaptive: the score updates their level
  //   - Practice: free practice, no impact
  // Once they have chosen, we generate the quiz targeted on this concept in
  // the requested mode. See renderModeChooser().
  const incomingConcept = new URLSearchParams(window.location.search).get('concept')
  if (incomingConcept) {
    state.pendingConceptId = incomingConcept
    state.phase = 'mode_chooser'
  } else {
    state.phase = 'chooser'
  }
  renderAll(container)

  return shell.element
}
