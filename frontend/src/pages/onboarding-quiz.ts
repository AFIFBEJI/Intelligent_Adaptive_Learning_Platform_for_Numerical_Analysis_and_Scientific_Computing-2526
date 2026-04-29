// ============================================================
// Onboarding diagnostic quiz
// ============================================================

import { api, type AiQuizResponse, type AiQuizSubmitResponse, type AiStudentAnswer } from '../api'
import { createAppShell } from '../components/app-shell'
import { createParticleBackground } from '../components/particles'
import { router } from '../router'
import { loadKatex, renderLatexIn } from '../utils/latex'

type Phase = 'intro' | 'generating' | 'quiz' | 'submitting' | 'done'

function escapeHtml(s: string): string {
  return (s || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function levelFromScore(score: number): string {
  if (score >= 70) return 'Advanced'
  if (score >= 40) return 'Intermediate'
  return 'Beginner'
}

export function OnboardingQuizPage(): HTMLElement {
  const wrapper = document.createElement('div')
  wrapper.className = 'onboarding-host'
  const stopParticles = createParticleBackground(wrapper)
  const shell = createAppShell({ activeRoute: '/onboarding-quiz', layout: 'focus' })

  void loadKatex()

  const main = document.createElement('div')
  main.innerHTML = `
    <style>
      .onboarding-screen {
        position: relative;
        z-index: 1;
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        width: min(900px, calc(100% - 2rem));
        margin: 0 auto;
        padding: var(--space-10) 0;
      }
      .onboarding-card {
        width: 100%;
        padding: var(--space-8);
        background: var(--bg-surface);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-lg);
      }
      .onboarding-center {
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: var(--space-4);
      }
      .onboarding-logo {
        width: 60px;
        height: 60px;
        display: grid;
        place-items: center;
        border-radius: var(--radius-md);
        color: #ffffff;
        background: var(--brand-gradient);
        font-weight: var(--font-weight-extrabold);
        box-shadow: var(--shadow-glow-brand);
      }
      .onboarding-title {
        margin: 0;
        color: var(--text-primary);
        font-size: var(--text-3xl);
        line-height: var(--line-height-tight);
      }
      .onboarding-sub {
        margin: 0;
        max-width: 620px;
        color: var(--text-muted);
        line-height: var(--line-height-relaxed);
      }
      .onboarding-facts {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: var(--space-3);
        width: 100%;
        margin: var(--space-4) 0;
      }
      .onboarding-fact {
        padding: var(--space-4);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        background: var(--bg-surface-2);
      }
      .onboarding-fact strong {
        display: block;
        color: var(--text-primary);
        font-size: var(--text-xl);
      }
      .onboarding-fact span {
        color: var(--text-muted);
        font-size: var(--text-xs);
        font-weight: var(--font-weight-bold);
        letter-spacing: 0.06em;
        text-transform: uppercase;
      }
      .spinner {
        width: 44px;
        height: 44px;
        border: 4px solid var(--border-default);
        border-top-color: var(--brand-300);
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
      }
      @keyframes spin { to { transform: rotate(360deg); } }
      .quiz-head {
        display: flex;
        justify-content: space-between;
        gap: var(--space-4);
        flex-wrap: wrap;
        margin-bottom: var(--space-5);
      }
      .question-text {
        margin: var(--space-5) 0;
        padding: var(--space-5);
        color: var(--text-secondary);
        line-height: var(--line-height-relaxed);
        background: var(--bg-surface-2);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
      }
      .option-list {
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
      }
      .option-button {
        width: 100%;
        min-height: 48px;
        padding: var(--space-3) var(--space-4);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-md);
        color: var(--text-secondary);
        background: var(--bg-surface);
        text-align: left;
        cursor: pointer;
        transition: border-color var(--transition-fast), background var(--transition-fast), color var(--transition-fast);
      }
      .option-button:hover {
        color: var(--text-primary);
        border-color: var(--border-emphasis);
      }
      .option-button.selected {
        color: var(--brand-100);
        border-color: var(--info-border);
        background: var(--info-bg);
      }
      .quiz-actions {
        display: flex;
        justify-content: space-between;
        gap: var(--space-3);
        flex-wrap: wrap;
        margin-top: var(--space-6);
      }
      .result-score {
        color: var(--text-primary);
        font-size: var(--text-5xl);
        font-weight: var(--font-weight-extrabold);
        line-height: 1;
      }
      .result-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: var(--space-4);
        width: 100%;
        margin-top: var(--space-5);
        text-align: left;
      }
      .result-list {
        margin: var(--space-3) 0 0;
        padding-left: var(--space-5);
        color: var(--text-muted);
        line-height: var(--line-height-relaxed);
      }
      .onboarding-host canvas { opacity: 0.12; }
      @media (max-width: 720px) {
        .onboarding-card { padding: var(--space-5); }
        .onboarding-facts,
        .result-grid { grid-template-columns: 1fr; }
      }
    </style>

    <section class="onboarding-screen">
      <div class="onboarding-card" id="onboarding-root"></div>
    </section>
  `

  shell.setContent(main)
  wrapper.appendChild(shell.element)

  let phase: Phase = 'intro'
  let quiz: AiQuizResponse | null = null
  let currentQuestionIdx = 0
  let answers: AiStudentAnswer[] = []
  let startedAt = 0
  let result: AiQuizSubmitResponse | null = null

  const root = main.querySelector('#onboarding-root') as HTMLElement

  const getAnswer = (questionId: number): string => {
    return answers.find(answer => answer.question_id === questionId)?.answer || ''
  }

  const setAnswer = (questionId: number, answer: string): void => {
    answers = answers.filter(item => item.question_id !== questionId)
    answers.push({ question_id: questionId, answer })
  }

  const submitQuiz = async (): Promise<void> => {
    if (!quiz) return
    phase = 'submitting'
    render()
    try {
      const tempsReponse = Math.floor((Date.now() - startedAt) / 1000)
      result = await api.submitAiQuiz(quiz.quiz_id, { answers, temps_reponse: tempsReponse })
      try {
        const user = await api.getMe()
        localStorage.setItem('user', JSON.stringify(user))
      } catch {
        // Result rendering should not fail if profile refresh is unavailable.
      }
      phase = 'done'
      render()
    } catch (err) {
      root.innerHTML = `
        <div class="onboarding-center">
          <div class="onboarding-logo">ER</div>
          <h1 class="onboarding-title">Submission failed</h1>
          <p class="onboarding-sub">${escapeHtml(err instanceof Error ? err.message : 'Unable to submit your diagnostic quiz.')}</p>
          <button class="ds-btn ds-btn-primary" id="retry-submit" type="button">Try again</button>
        </div>
      `
      root.querySelector('#retry-submit')?.addEventListener('click', () => { void submitQuiz() })
    }
  }

  const startQuiz = async (): Promise<void> => {
    phase = 'generating'
    render()
    try {
      quiz = await api.generateDiagnosticQuiz()
      currentQuestionIdx = 0
      answers = []
      startedAt = Date.now()
      phase = 'quiz'
      render()
    } catch (err) {
      root.innerHTML = `
        <div class="onboarding-center">
          <div class="onboarding-logo">API</div>
          <h1 class="onboarding-title">Diagnostic unavailable</h1>
          <p class="onboarding-sub">${escapeHtml(err instanceof Error ? err.message : 'Start the backend service and try again.')}</p>
          <button class="ds-btn ds-btn-primary" id="retry-generate" type="button">Try again</button>
        </div>
      `
      root.querySelector('#retry-generate')?.addEventListener('click', () => { void startQuiz() })
    }
  }

  function renderIntro(): void {
    root.innerHTML = `
      <div class="onboarding-center">
        <a href="/" data-link class="auth-brand" style="text-decoration:none;color:var(--text-primary);font-weight:var(--font-weight-extrabold);">
          <span class="onboarding-logo">AL</span>
        </a>
        <p class="ds-eyebrow">Initial calibration</p>
        <h1 class="onboarding-title">Take your diagnostic quiz</h1>
        <p class="onboarding-sub">This short quiz estimates your starting level and initializes your concept mastery profile. It helps the platform recommend the right next step.</p>
        <div class="onboarding-facts">
          <div class="onboarding-fact"><strong>5</strong><span>Questions</span></div>
          <div class="onboarding-fact"><strong>3</strong><span>Modules</span></div>
          <div class="onboarding-fact"><strong>1</strong><span>Adaptive path</span></div>
        </div>
        <button class="ds-btn ds-btn-primary" id="start-diagnostic" type="button">Start diagnostic</button>
      </div>
    `
    root.querySelector('#start-diagnostic')?.addEventListener('click', () => { void startQuiz() })
  }

  function renderGenerating(): void {
    root.innerHTML = `
      <div class="onboarding-center">
        <div class="spinner" aria-hidden="true"></div>
        <h1 class="onboarding-title">Generating your diagnostic</h1>
        <p class="onboarding-sub">The quiz is being prepared from the concept graph.</p>
      </div>
    `
  }

  function renderQuiz(): void {
    if (!quiz) return
    const question = quiz.questions[currentQuestionIdx]
    const selected = getAnswer(question.id)
    const progress = Math.round(((currentQuestionIdx + 1) / quiz.questions.length) * 100)
    const options = question.options && question.options.length > 0
      ? question.options
      : question.type === 'true_false'
        ? ['True', 'False']
        : []

    root.innerHTML = `
      <div>
        <div class="quiz-head">
          <div>
            <p class="ds-eyebrow">Question ${currentQuestionIdx + 1} of ${quiz.questions.length}</p>
            <h1 class="onboarding-title" style="text-align:left;">${escapeHtml(quiz.titre || 'Diagnostic quiz')}</h1>
          </div>
          <span class="ds-badge ds-badge-brand">${escapeHtml(question.difficulty)}</span>
        </div>
        <div class="ds-progress"><div class="ds-progress-bar" style="width:${progress}%;"></div></div>
        <div class="question-text">${escapeHtml(question.question)}</div>

        ${options.length > 0 ? `
          <div class="option-list">
            ${options.map(option => `
              <button class="option-button${selected === option ? ' selected' : ''}" data-answer="${escapeHtml(option)}" type="button">${escapeHtml(option)}</button>
            `).join('')}
          </div>
        ` : `
          <textarea id="open-answer" class="ds-textarea" placeholder="Write your answer here...">${escapeHtml(selected)}</textarea>
        `}

        <div class="quiz-actions">
          <button class="ds-btn ds-btn-secondary" id="prev-question" type="button" ${currentQuestionIdx === 0 ? 'disabled' : ''}>Previous</button>
          <div class="ds-row">
            ${currentQuestionIdx < quiz.questions.length - 1
              ? '<button class="ds-btn ds-btn-primary" id="next-question" type="button">Next</button>'
              : '<button class="ds-btn ds-btn-primary" id="finish-quiz" type="button">Finish diagnostic</button>'}
          </div>
        </div>
      </div>
    `

    root.querySelectorAll('.option-button').forEach(button => {
      button.addEventListener('click', () => {
        setAnswer(question.id, (button as HTMLElement).dataset.answer || '')
        render()
      })
    })

    const openAnswer = root.querySelector('#open-answer') as HTMLTextAreaElement | null
    openAnswer?.addEventListener('input', () => setAnswer(question.id, openAnswer.value))
    root.querySelector('#prev-question')?.addEventListener('click', () => {
      currentQuestionIdx = Math.max(0, currentQuestionIdx - 1)
      render()
    })
    root.querySelector('#next-question')?.addEventListener('click', () => {
      currentQuestionIdx = Math.min(quiz!.questions.length - 1, currentQuestionIdx + 1)
      render()
    })
    root.querySelector('#finish-quiz')?.addEventListener('click', () => { void submitQuiz() })
    renderLatexIn(root)
  }

  function renderSubmitting(): void {
    root.innerHTML = `
      <div class="onboarding-center">
        <div class="spinner" aria-hidden="true"></div>
        <h1 class="onboarding-title">Scoring your diagnostic</h1>
        <p class="onboarding-sub">Your profile and mastery map are being updated.</p>
      </div>
    `
  }

  function renderDone(): void {
    const score = result?.score || 0
    const card = result?.feedback_card
    root.innerHTML = `
      <div class="onboarding-center">
        <div class="onboarding-logo">OK</div>
        <p class="ds-eyebrow">Diagnostic complete</p>
        <h1 class="onboarding-title">Your starting level is ${levelFromScore(score)}</h1>
        <div class="result-score">${Math.round(score)}%</div>
        <p class="onboarding-sub">${escapeHtml(card?.summary || 'Your adaptive learning path is ready.')}</p>
        <div class="result-grid">
          <div class="ds-card">
            <h3 class="ds-section-title">Strengths</h3>
            <ul class="result-list">
              ${(card?.strengths && card.strengths.length > 0 ? card.strengths : ['Diagnostic completed']).map(item => `<li>${escapeHtml(item)}</li>`).join('')}
            </ul>
          </div>
          <div class="ds-card">
            <h3 class="ds-section-title">Next steps</h3>
            <ul class="result-list">
              ${(card?.next_steps && card.next_steps.length > 0 ? card.next_steps : ['Open your dashboard', 'Follow the recommended path']).map(item => `<li>${escapeHtml(item)}</li>`).join('')}
            </ul>
          </div>
        </div>
        <div class="ds-row" style="justify-content:center;margin-top:var(--space-4);">
          <button class="ds-btn ds-btn-primary" id="go-dashboard" type="button">Go to dashboard</button>
          <button class="ds-btn ds-btn-secondary" id="go-path" type="button">View learning path</button>
        </div>
      </div>
    `
    root.querySelector('#go-dashboard')?.addEventListener('click', () => router.navigate('/dashboard'))
    root.querySelector('#go-path')?.addEventListener('click', () => router.navigate('/path'))
  }

  function render(): void {
    if (phase === 'intro') renderIntro()
    if (phase === 'generating') renderGenerating()
    if (phase === 'quiz') renderQuiz()
    if (phase === 'submitting') renderSubmitting()
    if (phase === 'done') renderDone()
  }

  render()

  wrapper.addEventListener('remove', stopParticles)
  const origRemove = wrapper.remove.bind(wrapper)
  wrapper.remove = () => {
    stopParticles()
    origRemove()
  }

  return wrapper
}
