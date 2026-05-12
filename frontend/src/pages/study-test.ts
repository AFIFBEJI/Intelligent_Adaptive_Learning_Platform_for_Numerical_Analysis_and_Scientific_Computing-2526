// ============================================================
// Phase 4 — Page unifiee pre-test et post-test
// ============================================================
// La page sait quelle phase afficher selon l'URL :
//   /study/pretest   -> appelle api.studyGetPretest()
//   /study/posttest  -> appelle api.studyGetPosttest()
//
// Le rendu est unifie car le format des items est identique pour les 2
// versions. La seule difference est la phase (libelle, endpoint submit,
// redirection en fin de test).
//
// UI :
//   - Bandeau du haut avec timer (mm:ss).
//   - 15 cards items, chacune avec radio buttons (QCM) ou input texte
//     (questions ouvertes "calcul").
//   - Bouton "Soumettre" en bas, desactive tant que TOUS les items
//     ne sont pas repondus (eviter les soumissions partielles).
//   - Apres submit : affichage du score + redirection.
//
// Important : aucun feedback "bonne/mauvaise reponse" pendant le test
// pour ne pas spoiler l'apprentissage (esp. pour les items B qui seront
// utilises au post-test si l'etudiant tombe sur A en pre).

import { api, StudyItem, StudyTestStartResponse, StudyTestSubmitResponse } from '../api'
import { t } from '../i18n'
import { router } from '../router'

type Phase = 'pretest' | 'posttest'

function getPhaseFromPath(): Phase {
  return window.location.pathname.endsWith('/posttest') ? 'posttest' : 'pretest'
}

export function StudyTestPage(): HTMLElement {
  const container = document.createElement('div')
  container.className = 'study-test-page'

  const phase = getPhaseFromPath()
  const lang = (localStorage.getItem('app_lang') as 'fr' | 'en') || 'fr'

  container.innerHTML = `
    <style>
      .study-test-page {
        max-width: 800px;
        margin: 1rem auto;
        padding: 1.5rem;
        font-family: 'Segoe UI', sans-serif;
        color: #f8fafc;
      }
      .study-test-page header {
        position: sticky;
        top: 0;
        background: #07111f;
        padding: 1rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
        z-index: 10;
        margin-bottom: 1.5rem;
      }
      .study-test-page h1 {
        font-size: 1.4rem;
        color: #4fd1c5;
        margin: 0;
      }
      .study-test-page .timer {
        font-family: 'Courier New', monospace;
        font-size: 1.2rem;
        background: rgba(251, 191, 36, 0.1);
        color: #fbbf24;
        padding: 0.4rem 0.8rem;
        border-radius: 6px;
      }
      .study-test-page .item {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 1rem;
      }
      .study-test-page .item-header {
        font-size: 0.85rem;
        color: #94a3b8;
        margin-bottom: 0.5rem;
      }
      .study-test-page .item-question {
        font-size: 1.05rem;
        margin-bottom: 1rem;
        line-height: 1.5;
      }
      .study-test-page .options label {
        display: flex;
        align-items: flex-start;
        gap: 0.6rem;
        padding: 0.5rem 0.75rem;
        border-radius: 6px;
        cursor: pointer;
        margin-bottom: 0.3rem;
        border: 1px solid transparent;
        transition: background 0.15s;
      }
      .study-test-page .options label:hover {
        background: rgba(79, 209, 197, 0.08);
      }
      .study-test-page .options input[type="radio"] {
        margin-top: 0.3rem;
        flex-shrink: 0;
      }
      .study-test-page .options input[type="radio"]:checked + span {
        color: #4fd1c5;
        font-weight: 600;
      }
      .study-test-page .open-answer input {
        width: 100%;
        padding: 0.6rem;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 6px;
        color: #f8fafc;
        font-family: 'Courier New', monospace;
        font-size: 1rem;
      }
      .study-test-page .open-answer .hint {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 0.3rem;
      }
      .study-test-page .submit-bar {
        position: sticky;
        bottom: 0;
        background: #07111f;
        border-top: 1px solid rgba(255,255,255,0.1);
        padding: 1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      .study-test-page .progress {
        color: #94a3b8;
      }
      .study-test-page button.submit-btn {
        padding: 0.7rem 1.8rem;
        background: #4fd1c5;
        color: #07111f;
        border: none;
        border-radius: 8px;
        font-weight: 700;
        cursor: pointer;
        font-size: 1rem;
      }
      .study-test-page button.submit-btn:disabled {
        background: #2d3748;
        color: #64748b;
        cursor: not-allowed;
      }
      .study-test-page .result-card {
        background: rgba(79, 209, 197, 0.08);
        border: 1px solid #4fd1c5;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
      }
      .study-test-page .result-card .score {
        font-size: 3rem;
        color: #4fd1c5;
        font-weight: 700;
      }
      .study-test-page .error {
        color: #fb7185;
        margin: 1rem 0;
      }
    </style>

    <header>
      <h1 id="phase-title">${phase === 'pretest'
        ? (t('study.pretest.title') || "Pre-test (15 questions, ~20 min)")
        : (t('study.posttest.title') || "Post-test (15 questions, ~20 min)")}</h1>
      <div class="timer" id="timer">00:00</div>
    </header>
    <div id="instructions" style="margin-bottom:1.5rem; color:#cbd5e1;">
      ${phase === 'pretest'
        ? (t('study.pretest.instructions') ||
           "Reponds au mieux. Aucun feedback ne sera affiche pendant le test. Resultat a la fin.")
        : (t('study.posttest.instructions') ||
           "Dernier quiz ! Apres celui-ci tu auras le questionnaire de satisfaction.")}
    </div>
    <div id="items-container">
      <p style="color:#94a3b8;">${t('study.test.loading') || "Chargement des questions..."}</p>
    </div>
    <div class="submit-bar" id="submit-bar" style="display:none;">
      <span class="progress" id="progress">0 / 15</span>
      <button class="submit-btn" id="submit-btn" disabled>
        ${t('study.test.submit') || "Soumettre mes reponses"}
      </button>
    </div>
    <div id="feedback"></div>
  `

  // ============================================================
  // Etat de la page
  // ============================================================
  const startTime = Date.now()
  const itemsContainer = container.querySelector<HTMLDivElement>('#items-container')!
  const submitBar = container.querySelector<HTMLDivElement>('#submit-bar')!
  const submitBtn = container.querySelector<HTMLButtonElement>('#submit-btn')!
  const progressLabel = container.querySelector<HTMLSpanElement>('#progress')!
  const timerEl = container.querySelector<HTMLDivElement>('#timer')!
  const feedback = container.querySelector<HTMLDivElement>('#feedback')!
  let items: StudyItem[] = []
  const answers: Record<string, number | string> = {}

  // Timer mm:ss qui s'incremente toutes les secondes.
  const timerInterval = setInterval(() => {
    const elapsed = Math.floor((Date.now() - startTime) / 1000)
    const mm = Math.floor(elapsed / 60).toString().padStart(2, '0')
    const ss = (elapsed % 60).toString().padStart(2, '0')
    timerEl.textContent = `${mm}:${ss}`
    // Au-dela de 25 min on colore en rouge pour suggerer de soumettre.
    if (elapsed > 25 * 60) {
      timerEl.style.color = '#fb7185'
      timerEl.style.background = 'rgba(251, 113, 133, 0.1)'
    }
  }, 1000)

  function updateProgress(): void {
    const answered = items.filter(it => answers[it.id] !== undefined).length
    progressLabel.textContent = `${answered} / ${items.length}`
    submitBtn.disabled = answered < items.length
  }

  function renderItems(): void {
    itemsContainer.innerHTML = items.map((item, idx) => {
      const question = lang === 'en' ? item.question_en : item.question_fr
      const itemHeader = `${idx + 1}/${items.length}` +
        ` — ${item.concept_id} — ${item.difficulty} — ${item.points} pt`

      if (item.options && item.options.length > 0) {
        // QCM
        return `
          <div class="item" data-item-id="${item.id}">
            <div class="item-header">${itemHeader}</div>
            <div class="item-question">${escapeHtml(question)}</div>
            <div class="options">
              ${item.options.map((opt, optIdx) => `
                <label>
                  <input type="radio" name="q-${item.id}" value="${optIdx}">
                  <span>${escapeHtml(opt)}</span>
                </label>
              `).join('')}
            </div>
          </div>
        `
      }
      // Question ouverte (calcul libre)
      const hint = t('study.test.openHint') ||
        "Reponse libre (forme developpee, ex: 1 - x**2). Pas de difference de casse."
      return `
        <div class="item" data-item-id="${item.id}">
          <div class="item-header">${itemHeader}</div>
          <div class="item-question">${escapeHtml(question)}</div>
          <div class="open-answer">
            <input type="text" data-open-id="${item.id}"
                   placeholder="${t('study.test.placeholder') || 'Ta reponse...'}">
            <div class="hint">${hint}</div>
          </div>
        </div>
      `
    }).join('')

    // Hook listeners apres render
    itemsContainer.querySelectorAll<HTMLInputElement>('input[type="radio"]').forEach(input => {
      input.addEventListener('change', () => {
        const itemId = input.name.replace('q-', '')
        answers[itemId] = parseInt(input.value, 10)
        updateProgress()
      })
    })
    itemsContainer.querySelectorAll<HTMLInputElement>('input[data-open-id]').forEach(input => {
      input.addEventListener('input', () => {
        const itemId = input.dataset.openId!
        const trimmed = input.value.trim()
        if (trimmed) {
          answers[itemId] = trimmed
        } else {
          delete answers[itemId]
        }
        updateProgress()
      })
    })
  }

  // ============================================================
  // Chargement des items via API
  // ============================================================
  async function loadItems(): Promise<void> {
    try {
      const resp: StudyTestStartResponse = phase === 'pretest'
        ? await api.studyGetPretest()
        : await api.studyGetPosttest()
      items = resp.items
      renderItems()
      submitBar.style.display = 'flex'
      updateProgress()
    } catch (err) {
      console.error('[study-test] load failed', err)
      const message = err instanceof Error ? err.message : String(err)
      itemsContainer.innerHTML =
        `<p class="error">${t('study.test.loadError') ||
                          "Impossible de charger le test :"} ${escapeHtml(message)}</p>`
    }
  }
  void loadItems()

  // ============================================================
  // Soumission
  // ============================================================
  submitBtn.addEventListener('click', async () => {
    submitBtn.disabled = true
    clearInterval(timerInterval)
    const durationSeconds = Math.floor((Date.now() - startTime) / 1000)

    try {
      const resp: StudyTestSubmitResponse = phase === 'pretest'
        ? await api.studySubmitPretest({ answers, duration_seconds: durationSeconds })
        : await api.studySubmitPosttest({ answers, duration_seconds: durationSeconds })

      // Affichage du resultat dans une grosse card centree.
      itemsContainer.style.display = 'none'
      submitBar.style.display = 'none'

      const nextAction = phase === 'pretest'
        ? (t('study.test.nextPre') ||
           "Tu vas maintenant utiliser la plateforme pendant 4 semaines. " +
           "Reviens dans 4 semaines pour le post-test.")
        : (t('study.test.nextPost') ||
           "Derniere etape : 5 min de questionnaire de satisfaction.")

      const groupText = resp.group_assigned
        ? `<p style="margin-top:1rem; color:#fbbf24;">
             ${t('study.test.group') || "Groupe assigne :"}
             <strong>${escapeHtml(resp.group_assigned)}</strong>
           </p>`
        : ''

      feedback.innerHTML = `
        <div class="result-card">
          <div class="score">${resp.score.toFixed(0)}%</div>
          <p style="color:#cbd5e1;">
            ${t('study.test.scoreLabel') || "Score :"}
            ${resp.raw} / ${resp.max} ${t('study.test.points') || "points"}
          </p>
          ${groupText}
          <p style="margin-top:1.5rem;">${nextAction}</p>
          <button class="submit-btn" id="continue-btn" style="margin-top:1.5rem;">
            ${phase === 'pretest'
              ? (t('study.test.toDashboard') || "Aller au tableau de bord")
              : (t('study.test.toSus') || "Continuer vers le questionnaire")}
          </button>
        </div>
      `
      const continueBtn = container.querySelector<HTMLButtonElement>('#continue-btn')!
      continueBtn.addEventListener('click', () => {
        if (phase === 'pretest') {
          router.navigate('/dashboard')
        } else {
          router.navigate('/study/sus')
        }
      })
    } catch (err) {
      console.error('[study-test] submit failed', err)
      const message = err instanceof Error ? err.message : String(err)
      feedback.innerHTML = `<p class="error">
        ${t('study.test.submitError') || "Erreur lors de la soumission :"}
        ${escapeHtml(message)}
      </p>`
      submitBtn.disabled = false
    }
  })

  // Nettoyage timer si on quitte la page (navigation)
  container.addEventListener('disconnect', () => clearInterval(timerInterval))

  return container
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}
