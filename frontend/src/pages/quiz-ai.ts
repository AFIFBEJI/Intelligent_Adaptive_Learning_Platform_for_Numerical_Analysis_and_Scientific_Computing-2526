// ============================================================
// Page Quiz Dynamique + Carte de Feedback
// ============================================================
// Trois états successifs dans la même page :
//   1. SETUP    → formulaire (concept/topic, nb questions, difficulté)
//   2. QUIZ     → affichage des questions + saisie des réponses
//   3. FEEDBACK → carte de feedback détaillée post-soumission
// + panneau historique (tentatives passées) accessible à tout moment.
// ============================================================

import { api } from '../api'
import { createAppShell } from '../components/app-shell'
import { getLang, languageName, t, type Lang } from '../i18n'
import { loadKatex, renderLatexIn } from '../utils/latex'
import type { Concept } from '../api'

// Cache des concepts pour eviter de les refetcher a chaque renderSetup
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
  // Si deja peuple (>1 option), on ne refait pas
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
  AiQuizQuestion,
  AiQuizSubmitResponse,
  AiAttemptSummary,
  AiFeedbackCard,
  AiStudentAnswer,
} from '../api'

// MathJax est chargé globalement par index.html (comme dans tutor.ts)
declare const MathJax: {
  typesetPromise?: (elements?: Element[]) => Promise<void>
} | undefined

// ------------------------------------------------------------
// État local de la page
// ------------------------------------------------------------
// 'chooser' = ecran d'accueil avec 2 grosses cartes (Parcours / Entrainement)
// 'setup'   = formulaire d'entrainement libre (filtres complets)
type Phase = 'chooser' | 'setup' | 'loading' | 'quiz' | 'submitting' | 'feedback' | 'history'

interface PageState {
  phase: Phase
  quiz: AiQuizResponse | null
  answers: Map<number, string>
  startedAt: number
  result: AiQuizSubmitResponse | null
  history: AiAttemptSummary[]
  historyOpen: boolean
  error: string | null
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
}

// ------------------------------------------------------------
// Utilities
// ------------------------------------------------------------
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
  if (score >= 90) return '#16a34a' // vert foncé
  if (score >= 75) return '#22c55e' // vert
  if (score >= 60) return '#eab308' // jaune
  if (score >= 40) return '#f97316' // orange
  return '#ef4444' // rouge
}

function displayDifficulty(value: string): string {
  if (value === 'facile') return t('quiz.difficulty.facile')
  if (value === 'moyen') return t('quiz.difficulty.moyen')
  if (value === 'difficile') return t('quiz.difficulty.difficile')
  if (value === 'auto') return t('quiz.difficulty.auto')
  return value
}

function displayQuestionType(value: string): string {
  if (value === 'mcq') return t('quiz.type.mcq')
  if (value === 'true_false') return t('quiz.type.true_false')
  if (value === 'open') return t('quiz.type.open')
  return value
}

function quizLanguage(): Lang {
  return state.quiz?.language || getLang()
}

function trueFalseOptions(lang: Lang): [string, string] {
  return lang === 'fr' ? ['Vrai', 'Faux'] : ['True', 'False']
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
// Le selecteur de langue de la page quiz a ete supprime : il est inutile
// d'avoir 3 toggles (sidebar + topbar + setup quiz). La langue est gere
// uniquement depuis la sidebar. Les nouvelles questions/feedbacks suivent
// `localStorage.app_lang` qui est mis a jour depuis la sidebar.

// ============================================================
// renderChooser : ecran d'accueil avec 2 GROSSES cartes cote a cote
// ============================================================
// On clique sur une carte -> on lance directement le mode correspondant.
// - Carte adaptive : pas de setup, lance tout de suite avec les defauts.
// - Carte practice : ouvre le formulaire (phase 'setup').
// ============================================================
function renderChooser(root: HTMLElement): void {
  root.innerHTML = `
    <div class="quiz-ai-page">
      <div class="quiz-ai-toolbar">
        <button class="btn-link" id="btn-history">${escapeHtml(t('quiz.history'))}</button>
      </div>

      ${state.error ? `<div class="alert-error">${escapeHtml(state.error)}</div>` : ''}

      <div class="mode-chooser">
        <button type="button" class="mode-card-big mode-adaptive" id="card-adaptive">
          <div class="mode-card-icon-wrap">
            <span class="mode-card-icon" aria-hidden="true">▲</span>
          </div>
          <h3 class="mode-card-title">${escapeHtml(t('quiz.mode.adaptive.title'))}</h3>
          <p class="mode-card-desc">${escapeHtml(t('quiz.mode.adaptive.tagline'))}</p>
          <div class="mode-card-tags">
            <span class="mode-badge mode-badge-good">${escapeHtml(t('quiz.mode.adaptive.badge'))}</span>
          </div>
          <span class="mode-card-cta">
            ${escapeHtml(t('quiz.mode.adaptive.cta'))}
            <span aria-hidden="true">→</span>
          </span>
        </button>

        <button type="button" class="mode-card-big mode-practice" id="card-practice">
          <div class="mode-card-icon-wrap">
            <span class="mode-card-icon" aria-hidden="true">⚙</span>
          </div>
          <h3 class="mode-card-title">${escapeHtml(t('quiz.mode.practice.title'))}</h3>
          <p class="mode-card-desc">${escapeHtml(t('quiz.mode.practice.tagline'))}</p>
          <div class="mode-card-tags">
            <span class="mode-badge mode-badge-warn">${escapeHtml(t('quiz.mode.practice.badge'))}</span>
          </div>
          <span class="mode-card-cta">
            ${escapeHtml(t('quiz.mode.practice.cta'))}
            <span aria-hidden="true">→</span>
          </span>
        </button>
      </div>
    </div>
  `

  root.querySelector('#card-adaptive')?.addEventListener('click', async () => {
    state.error = null
    await handleGenerateAdaptive(root)
  })

  root.querySelector('#card-practice')?.addEventListener('click', () => {
    state.error = null
    state.phase = 'setup'
    renderAll(root)
  })

  root.querySelector('#btn-history')?.addEventListener('click', async () => {
    state.phase = 'history'
    await loadHistory()
    renderAll(root)
  })
}

// ============================================================
// renderSetup : formulaire d'entrainement libre (filtres)
// ============================================================
// Affiche UNIQUEMENT le formulaire des filtres + un bouton retour vers
// l'ecran de choix. Plus de carte adaptive ici.
// ============================================================
function renderSetup(root: HTMLElement): void {
  const isFr = getLang() === 'fr'
  const qtypeHelp = isFr
    ? 'Coche les formats de questions que tu veux dans ton quiz.'
    : 'Check the question formats you want in your quiz.'
  // qtypeHelp est inline avec le label, plus dans une ligne separee
  void qtypeHelp
  root.innerHTML = `
    <div class="quiz-ai-page">
      <div class="quiz-ai-toolbar">
        <button class="btn-link" id="btn-back-chooser">← ${escapeHtml(isFr ? 'Retour' : 'Back')}</button>
        <button class="btn-link" id="btn-history">${escapeHtml(t('quiz.history'))}</button>
      </div>

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
              <input type="checkbox" name="qtype" value="open" />
              <span class="qtype-chip-text">${escapeHtml(t('quiz.type.open'))}</span>
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

  // Pre-selection via URL : /quiz-ai?concept=concept_lagrange
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
// Mode parcours (adaptive) : pas de filtres, le backend choisit tout.
// On force concept_id=null et difficulty='auto' pour que le service
// pioche le concept fragile et la difficulte adaptee au mastery.
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
      // Mix raisonnable QCM + V/F pour un quiz parcours rapide.
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
    // Sur erreur du mode parcours, on retourne au chooser
    // (pas au setup) puisque le mode adaptive ne passe pas par ce formulaire.
    state.phase = 'chooser'
    renderAll(root)
  }
}

// ============================================================
// Mode entrainement libre (practice) : l'etudiant choisit tout.
// Le backend stockera mode='practice' sur le Quiz, donc le submit
// ne touchera PAS au mastery.
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

  const types: Array<'mcq' | 'open' | 'true_false'> = []
  document
    .querySelectorAll<HTMLInputElement>('input[name="qtype"]:checked')
    .forEach((cb) => {
      types.push(cb.value as 'mcq' | 'open' | 'true_false')
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
function renderLoading(root: HTMLElement, message: string): void {
  root.innerHTML = `
    <div class="quiz-ai-page">
      <div class="loading-card">
        <div class="spinner"></div>
        <p>${escapeHtml(message)}</p>
        <small id="loading-subtitle">${escapeHtml(t('quiz.loading.generate'))}</small>
      </div>
    </div>
  `
}

// ------------------------------------------------------------
// Rendering — QUIZ phase
// ------------------------------------------------------------
function renderQuiz(root: HTMLElement): void {
  const quiz = state.quiz!
  const answered = state.answers.size
  const total = quiz.questions.length
  // Affiche un bandeau d'avertissement si on est en mode practice :
  // c'est important pour que l'etudiant n'oublie pas que ce quiz ne
  // comptera pas dans sa progression.
  const isPractice = quiz.mode === 'practice'

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
  quiz.questions.forEach((q, idx) => list.appendChild(buildQuestionCard(q, idx)))

  root.querySelector('#btn-cancel')?.addEventListener('click', () => {
    if (confirm(t('quiz.confirm.leave'))) {
      state.quiz = null
      state.answers.clear()
      // Apres avoir annule un quiz, on retourne a l'ecran de choix
      // (l'utilisateur peut re-choisir un mode different).
      state.phase = 'chooser'
      renderAll(root)
    }
  })

  root.querySelector('#btn-submit')?.addEventListener('click', async () => {
    await handleSubmit(root)
  })

  typesetMath(list)
}

function buildQuestionCard(q: AiQuizQuestion, idx: number): HTMLElement {
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
        ${q.options
          .map(
            (opt, i) => `
          <label class="option">
            <input type="radio" name="q-${q.id}" value="${escapeHtml(opt)}" />
            <span class="option-key">${String.fromCharCode(65 + i)}</span>
            <span class="option-text">${escapeHtml(opt)}</span>
          </label>
        `,
          )
          .join('')}
      </div>
    `
  } else if (q.type === 'true_false') {
    const [trueLabel, falseLabel] = q.options && q.options.length >= 2
      ? [q.options[0], q.options[1]]
      : trueFalseOptions(q.language || quizLanguage())
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

  // Lier l'événement de capture
  card.querySelectorAll<HTMLInputElement>(`input[name="q-${q.id}"]`).forEach((el) => {
    el.addEventListener('change', () => {
      state.answers.set(q.id, el.value)
      refreshProgress()
    })
  })
  const textarea = card.querySelector<HTMLTextAreaElement>(`textarea[name="q-${q.id}"]`)
  if (textarea) {
    textarea.addEventListener('input', () => {
      const val = textarea.value.trim()
      if (val) state.answers.set(q.id, val)
      else state.answers.delete(q.id)
      refreshProgress()
    })
  }

  return card
}

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
    })
    state.result = result
    state.phase = 'feedback'
    renderAll(root)
  } catch (err) {
    state.error =
      err instanceof Error ? err.message : t('quiz.error.submit')
    state.phase = 'quiz'
    renderAll(root)
  }
}

// ------------------------------------------------------------
// Rendering — FEEDBACK phase
// ------------------------------------------------------------
function renderFeedback(root: HTMLElement): void {
  const res = state.result!
  const card = res.feedback_card

  // Construire les recommandations contextuelles a partir des concepts
  // ou l'etudiant a echoue (extraits des evaluations) et des concepts
  // recommandes par le moteur de feedback.
  const failedConceptIds = Array.from(new Set(
    res.evaluations
      .filter(e => !e.is_correct && e.concept_id)
      .map(e => e.concept_id!)
  )).slice(0, 3)

  const recoSection = (failedConceptIds.length > 0 || (card.recommended_concepts || []).length > 0) ? `
    <div class="fb-recommendations">
      <div class="fb-recommendations-title">${escapeHtml(t('quiz.feedback.recommended'))}</div>
      <div class="fb-reco-actions">
        ${failedConceptIds.map(cid => `
          <a href="/content?concept=${encodeURIComponent(cid)}" data-link class="fb-reco-chip">
            ${escapeHtml(t('quiz.feedback.review'))}
          </a>
          <a href="/quiz-ai?concept=${encodeURIComponent(cid)}" data-link class="fb-reco-chip">
            ${escapeHtml(t('quiz.feedback.practice'))}
          </a>
        `).join('')}
        <a href="/tutor" data-link class="fb-reco-chip">${escapeHtml(t('quiz.feedback.tutor'))}</a>
        <a href="/path" data-link class="fb-reco-chip">${escapeHtml(t('quiz.feedback.path'))}</a>
      </div>
    </div>
  ` : ''

  // ============================================================
  // Bandeau de mode + delta mastery
  // ============================================================
  // En mode adaptive, on affiche les concepts dont le mastery a ete
  // mis a jour (la liste vient du backend, ordonnee par premiere
  // apparition dans le quiz). En mode practice, on affiche un message
  // explicite : pas d'impact sur la progression.
  const isPractice = res.mode === 'practice'
  const masteryUpdated = res.mastery_updated || []
  // Resoudre les noms lisibles depuis le cache des concepts (best-effort).
  // On garde l'id en fallback si le concept n'est pas dans le cache.
  const conceptNames = new Map<string, string>()
  for (const c of (_cachedConcepts || [])) conceptNames.set(c.id, c.name)
  const updatedNames = masteryUpdated.map(cid => conceptNames.get(cid) || cid)

  const modeBanner = isPractice
    ? `<div class="results-mode-badge practice">⚠ ${escapeHtml(t('quiz.results.modePractice'))}</div>`
    : `<div class="results-mode-badge adaptive">✓ ${escapeHtml(t('quiz.results.modeAdaptive'))}</div>`

  const deltaSection = isPractice
    ? `<div class="delta-mastery">${escapeHtml(t('quiz.results.noDelta'))}</div>`
    : (updatedNames.length > 0
        ? `<div class="delta-mastery"><strong>${escapeHtml(t('quiz.results.deltaMastery'))} :</strong> ${updatedNames.map(n => escapeHtml(n)).join(', ')}</div>`
        : '')

  root.innerHTML = `
    <div class="quiz-ai-page">
      <div class="feedback-card">
        ${modeBanner}
        ${renderScoreRing(card)}
        ${deltaSection}
        ${renderFeedbackBody(card)}
        ${renderEvaluations(res.evaluations)}
        ${recoSection}
        <div class="fb-actions">
          <button class="btn-secondary" id="btn-back">${escapeHtml(t('quiz.action.backSetup'))}</button>
          <button class="btn-primary" id="btn-again">${escapeHtml(t('quiz.action.again'))}</button>
        </div>
      </div>
    </div>
  `

  root.querySelector('#btn-back')?.addEventListener('click', () => {
    resetPage()
    renderAll(root)
  })
  root.querySelector('#btn-again')?.addEventListener('click', () => {
    resetPage()
    // Apres un quiz, retour a l'ecran de choix pour re-selectionner
    // le mode (parcours ou entrainement) avant un nouveau quiz.
    state.phase = 'chooser'
    renderAll(root)
  })

  typesetMath(root)
}

function renderScoreRing(card: AiFeedbackCard): string {
  const color = gradeColor(card.score)
  const pct = Math.max(0, Math.min(100, card.score))
  const circumference = 2 * Math.PI * 54
  const dash = (pct / 100) * circumference

  // Couleurs adaptees au theme sombre : track gris semi-transparent, texte clair.
  return `
    <div class="score-ring">
      <svg width="140" height="140" viewBox="0 0 140 140">
        <circle cx="70" cy="70" r="54" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="14"/>
        <circle cx="70" cy="70" r="54" fill="none" stroke="${color}" stroke-width="14"
          stroke-dasharray="${dash} ${circumference}" stroke-linecap="round"
          transform="rotate(-90 70 70)"/>
        <text x="70" y="74" text-anchor="middle" font-size="28" font-weight="700" fill="var(--text-primary)">
          ${pct.toFixed(0)}
        </text>
        <text x="70" y="94" text-anchor="middle" font-size="11" fill="var(--text-muted)">/ 100</text>
      </svg>
      <div class="grade-label" style="color:${color}">${escapeHtml(card.grade_label)}</div>
      <div class="score-meta">
        <strong>${card.n_correct}</strong> / ${card.n_total} ${escapeHtml(t('quiz.meta.correct'))}
        <span class="score-meta-sep">/</span>
        ${card.temps_reponse}s
      </div>
    </div>
  `
}

function renderFeedbackBody(card: AiFeedbackCard): string {
  const section = (title: string, items: string[], cls: string): string => {
    if (!items || items.length === 0) return ''
    return `
      <section class="fb-section ${cls}">
        <h3>${escapeHtml(title)}</h3>
        <ul>${items.map((x) => `<li>${escapeHtml(x)}</li>`).join('')}</ul>
      </section>
    `
  }

  return `
    <div class="fb-body">
      <blockquote class="fb-summary">${escapeHtml(card.summary)}</blockquote>
      ${section(t('quiz.feedback.summary.strengths'), card.strengths, 'fb-strengths')}
      ${section(t('quiz.feedback.summary.review'), card.weaknesses, 'fb-weaknesses')}
      ${section(
        t('quiz.feedback.summary.mistakes'),
        card.mistakes_detail,
        'fb-mistakes',
      )}
      ${section(t('quiz.feedback.summary.next'), card.next_steps, 'fb-nexts')}
    </div>
  `
}

function renderEvaluations(
  evals: {
    question_id: number
    question: string
    student_answer: string
    correct_answer: string
    is_correct: boolean
    partial_credit: number
    explanation: string
  }[],
): string {
  if (!evals || evals.length === 0) return ''
  return `
    <details class="eval-details">
      <summary>${escapeHtml(t('quiz.feedback.details'))} (${evals.length})</summary>
      <div class="eval-list">
        ${evals
          .map(
            (e) => `
          <div class="eval-row ${e.is_correct ? 'eval-ok' : 'eval-ko'}">
            <div class="eval-head">
              <span class="eval-icon">${e.is_correct ? 'OK' : 'NO'}</span>
              <strong>Q${e.question_id}</strong>
              <span class="eval-pc">${(e.partial_credit * 100).toFixed(0)}%</span>
            </div>
            <div class="eval-q">${escapeHtml(e.question)}</div>
            <div class="eval-ans">
              <div><em>${escapeHtml(t('quiz.feedback.yourAnswer'))}:</em> ${escapeHtml(e.student_answer || t('quiz.feedback.empty'))}</div>
              <div><em>${escapeHtml(t('quiz.feedback.expected'))}:</em> ${escapeHtml(e.correct_answer)}</div>
            </div>
            ${e.explanation ? `<div class="eval-exp">${escapeHtml(e.explanation)}</div>` : ''}
          </div>
        `,
          )
          .join('')}
      </div>
    </details>
  `
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

function renderHistory(root: HTMLElement): void {
  root.innerHTML = `
    <div class="quiz-ai-page">
      <header class="quiz-ai-header">
        <h1>${escapeHtml(t('quiz.history.title'))}</h1>
        <button class="btn-link" id="btn-back-setup">${escapeHtml(t('quiz.history.back'))}</button>
      </header>

      ${
        state.history.length === 0
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
            ${state.history
              .map(
                (h) => `
              <tr>
                <td>${formatDate(h.date_tentative)}</td>
                <td>${escapeHtml(h.quiz_titre)}</td>
                <td style="color:${gradeColor(h.score)}"><strong>${h.score.toFixed(0)}</strong></td>
                <td>${h.temps_reponse}s</td>
                <td>${escapeHtml(h.grade_label ?? '-')}</td>
                <td><button class="btn-link" data-id="${h.id}">${escapeHtml(t('quiz.history.details'))}</button></td>
              </tr>
            `,
              )
              .join('')}
          </tbody>
        </table>
      `
      }
    </div>
  `

  root.querySelector('#btn-back-setup')?.addEventListener('click', () => {
    // Depuis l'historique, on retourne a l'ecran de choix.
    state.phase = 'chooser'
    renderAll(root)
  })

  root.querySelectorAll<HTMLButtonElement>('button.btn-link[data-id]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const id = parseInt(btn.dataset.id!, 10)
      try {
        state.result = await api.getAiAttempt(id)
        state.phase = 'feedback'
        renderAll(root)
      } catch (err) {
        state.error = err instanceof Error ? err.message : 'Unable to load attempt details.'
        renderAll(root)
      }
    })
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
// Messages rotatifs pour le loading — reduit la frustration pendant la generation
function loadingMessages(): string[] {
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
let _loadingTimer: number | null = null

function startLoadingRotation(): void {
  stopLoadingRotation()
  let idx = 0
  _loadingTimer = window.setInterval(() => {
    const sub = document.querySelector('#loading-subtitle')
    if (sub) {
      const messages = loadingMessages()
      idx = (idx + 1) % messages.length
      sub.textContent = messages[idx]
    }
  }, 4000)
}
function stopLoadingRotation(): void {
  if (_loadingTimer !== null) {
    window.clearInterval(_loadingTimer)
    _loadingTimer = null
  }
}

function renderAll(root: HTMLElement): void {
  // Re-render KaTeX apres chaque renderAll (questions, options, feedback...)
  // KaTeX auto-render est idempotent, on peut l'appeler safely a chaque fois.
  setTimeout(() => renderLatexIn(root), 0)

  // Demarrer/arreter la rotation des messages selon la phase
  if (state.phase === 'loading' || state.phase === 'submitting') {
    startLoadingRotation()
  } else {
    stopLoadingRotation()
  }

  switch (state.phase) {
    case 'chooser':
      renderChooser(root)
      // On precharge les concepts en arriere-plan : si l'utilisateur clique
      // sur "Practice", le dropdown sera deja peuple.
      void getCachedConcepts()
      break
    case 'setup':
      renderSetup(root)
      void getCachedConcepts().then(() => populateConceptsSelect(root))
      break
    case 'loading':
      renderLoading(root, loadingMessages()[0])
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
// Styles (inline — on garde la page auto-contenue)
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

/* ============================================================
   Chooser : 2 GROSSES cartes cote a cote sur l'ecran d'accueil
   ============================================================
   C'est la PREMIERE chose que l'utilisateur voit en arrivant sur /quiz-ai.
   Style "card picker" inspire du selecteur de LLM dans tutor.ts. */
.mode-chooser {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-5);
  margin-top: var(--space-4);
}
@media (max-width: 768px) {
  .mode-chooser { grid-template-columns: 1fr; }
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
/* Practice : palette slate neutre cohérente avec le reste, pas d'orange agressif. */
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
.mode-card-tags {
  display: flex; flex-wrap: wrap; gap: var(--space-2);
}
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
/* Les deux CTA partagent le meme gradient teal/bleu de la marque pour
   garantir la coherence visuelle. La distinction entre les modes se fait
   par les BADGES (vert "Counts" vs amber "No impact") et la bordure haut
   de la carte (teal vs slate), pas par la couleur du bouton. */
.mode-card-big:hover .mode-card-cta { gap: var(--space-3); }

/* ============================================================
   Setup d'entrainement libre : layout aere, structure claire
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

/* Question types : chips horizontaux compacts au lieu de grosses cartes */
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

/* Footer : warning inline subtil + CTA aligne */
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
   Cartes "mode pedagogique" : Parcours (adaptive) vs Entrainement (practice)
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
/* Pendant le quiz, on rappelle le mode practice en haut de l'ecran */
.practice-banner { padding: 10px 14px; margin-bottom: var(--space-4); border-radius: var(--radius-md); background: var(--warning-bg); color: var(--warning); border: 1px solid var(--warning-border); font-size: 0.9rem; font-weight: 600; display:flex; align-items:center; gap: 8px; }
/* Sur la page resultat, badge qui resume le mode + zone delta mastery */
.results-mode-badge { display:inline-flex; align-items:center; padding: 5px 12px; border-radius: var(--radius-md); font-size: 0.8rem; font-weight: 700; margin-bottom: var(--space-3); }
.results-mode-badge.adaptive { background: var(--success-bg); color: var(--success); border: 1px solid var(--success-border); }
.results-mode-badge.practice { background: var(--warning-bg); color: var(--warning); border: 1px solid var(--warning-border); }
.delta-mastery { padding: 12px 16px; margin: var(--space-3) 0; border-radius: var(--radius-md); background: rgba(15,118,110,0.08); border: 1px solid rgba(15,118,110,0.22); font-size: 0.92rem; }
.delta-mastery strong { color: var(--brand-600); }
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
.loading-card { background: var(--bg-surface); padding: 48px; border-radius: 12px; text-align: center; box-shadow: var(--shadow-sm); }
.spinner { width: 48px; height: 48px; border: 4px solid #e5e7eb; border-top-color: var(--brand-400); border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 16px; }
@keyframes spin { to { transform: rotate(360deg); } }
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
.quiz-actions { display: flex; justify-content: space-between; margin-top: 24px; gap: 12px; }
.feedback-card { background: var(--bg-surface); border-radius: 12px; padding: 32px; box-shadow: var(--shadow-md); }
.score-ring { text-align: center; margin-bottom: 24px; }
.grade-label { font-size: 1.3rem; font-weight: 700; margin: 8px 0 4px; }
.score-meta { color: var(--text-muted); font-size: 0.95rem; }
.fb-summary { background: rgba(15,118,110,0.08); border-left: 4px solid var(--brand-500); padding: 16px 20px; margin: 16px 0; border-radius: 4px; font-size: 1.05rem; }
.fb-section { margin: 20px 0; }
.fb-section h3 { font-size: 1.05rem; margin: 0 0 10px; }
.fb-section ul { margin: 0; padding-left: 22px; }
.fb-section li { margin: 6px 0; line-height: 1.5; }
.fb-strengths h3 { color: var(--success); }
.fb-weaknesses h3 { color: #fb923c; }
.fb-mistakes h3 { color: var(--danger); }
.fb-nexts h3 { color: var(--brand-600); }
.eval-details { margin-top: 20px; }
.eval-details summary { cursor: pointer; font-weight: 600; padding: 8px 0; }
.eval-list { display: flex; flex-direction: column; gap: 12px; margin-top: 12px; }
.eval-row { padding: 14px; border-radius: 8px; border: 1px solid var(--border-default); }
.eval-ok { background: var(--success-bg); border-color: var(--success-border); }
.eval-ko { background: var(--danger-bg); border-color: var(--danger-border); }
.eval-head { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; font-size: 0.9rem; }
.eval-icon { font-size: 1.2rem; font-weight: 700; }
.eval-ok .eval-icon { color: var(--success); }
.eval-ko .eval-icon { color: var(--danger); }
.eval-pc { margin-left: auto; color: var(--text-muted); font-size: 0.85rem; }
.eval-q { font-size: 0.95rem; margin-bottom: 8px; }
.eval-ans { display: flex; gap: 24px; font-size: 0.9rem; color: var(--text-secondary); }
.eval-ans em { color: var(--text-muted); font-style: normal; font-weight: 500; margin-right: 4px; }
.eval-exp { margin-top: 10px; padding-top: 10px; border-top: 1px dashed var(--border-default); color: var(--text-secondary); font-size: 0.92rem; font-style: italic; line-height: 1.6; }
.fb-actions { display: flex; justify-content: center; gap: 12px; margin-top: 28px; flex-wrap: wrap; }
.fb-recommendations { margin: 24px 0 0; padding: 20px; background: rgba(15,118,110,0.06); border: 1px solid rgba(15,118,110,0.2); border-radius: 12px; }
.fb-recommendations-title { font-size: 0.78rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--brand-600); margin: 0 0 12px; }
.fb-reco-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.fb-reco-chip { display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; border-radius: 999px; background: var(--bg-surface); border: 1px solid var(--border-default); color: var(--text-secondary); font-size: 0.85rem; font-weight: 600; text-decoration: none; transition: all 0.15s; }
.fb-reco-chip:hover { border-color: var(--border-emphasis); color: var(--brand-600); background: rgba(15,118,110,0.1); }
.score-meta-sep { color: var(--text-subtle); margin: 0 6px; }
.history-table { width: 100%; background: var(--bg-surface); border-radius: 8px; overflow: hidden; border-collapse: collapse; }
.history-table th, .history-table td { padding: 12px 16px; text-align: left; border-bottom: 1px solid var(--border-subtle); }
.history-table th { background: var(--bg-surface-hover); font-weight: 600; font-size: 0.9rem; color: var(--text-secondary); }
.empty { text-align: center; color: var(--text-muted); padding: 40px; }
.loading-card { text-align: center; padding: 60px 20px; color: var(--text-secondary); }
.spinner { width: 40px; height: 40px; border: 3px solid var(--border-default); border-top-color: var(--brand-400); border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 20px; }
@keyframes spin { to { transform: rotate(360deg); } }
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
.feedback-card,
.loading-card,
.history-table {
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}
.quiz-ai-header { padding: var(--space-5); margin-bottom: var(--space-5); }
.setup-card,
.question-card,
.feedback-card { padding: var(--space-6); }
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
  // Cas particulier : si on arrive avec ?concept=... dans l'URL (depuis
  // la page Cours ou Concepts), on saute l'ecran de choix et on va
  // directement au formulaire d'entrainement avec le concept pre-selectionne.
  // Sinon, on demarre sur le chooser (les 2 grosses cartes).
  const incomingConcept = new URLSearchParams(window.location.search).get('concept')
  state.phase = incomingConcept ? 'setup' : 'chooser'
  renderAll(container)

  return shell.element
}
