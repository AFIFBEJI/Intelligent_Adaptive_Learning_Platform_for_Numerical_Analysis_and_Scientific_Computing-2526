// ============================================================
// Phase 4 — Adapted SUS questionnaire (post-study)
// ============================================================
// Final page of the user study flow. Submits 6 Likert 1-5 items +
// 3 free-text answers to /study/sus.
//
// The 6 SUS-adapted items are a condensed version of the standard System
// Usability Scale (10 items, Brooke 1996) calibrated for our bilingual
// EdTech context. The even items are positive, the odd items
// negative (attention check).

import { api } from '../api'
import { t } from '../i18n'
import { router } from '../router'

// 6 SUS-adapted statements (bilingual). Index 0-5.
// positive / negative alternation for the attention check.
const SUS_ITEMS_FR: string[] = [
  // Positive items
  "Je pense que j'utiliserais cette plateforme regulierement si elle etait disponible.",
  "La plateforme m'a aide a mieux comprendre l'analyse numerique.",
  "Les explications du tuteur IA etaient claires et pertinentes.",
  // Negative items (to invert at scoring if following strict Brooke 1996)
  "J'ai trouve la plateforme inutilement complexe.",
  "J'ai eu besoin d'aide pour utiliser la plateforme.",
  "J'ai trouve les bugs / lenteurs frustrants.",
]
const SUS_ITEMS_EN: string[] = [
  "I would use this platform regularly if available.",
  "The platform helped me understand numerical analysis better.",
  "The AI tutor's explanations were clear and relevant.",
  "I found the platform unnecessarily complex.",
  "I needed help to use the platform.",
  "I found bugs / slowness frustrating.",
]

const OPEN_QUESTIONS_FR = {
  helped: "Qu'est-ce qui t'a le PLUS aide dans cette plateforme ?",
  frustrated: "Qu'est-ce qui t'a le plus FRUSTRE ?",
  recommend: "Recommanderais-tu cette plateforme a un autre etudiant ? Pourquoi ?",
}
const OPEN_QUESTIONS_EN = {
  helped: "What helped you MOST in this platform?",
  frustrated: "What was most FRUSTRATING?",
  recommend: "Would you recommend this platform to another student? Why?",
}

export function StudySusPage(): HTMLElement {
  const container = document.createElement('div')
  container.className = 'study-sus-page'

  const lang = (localStorage.getItem('app_lang') as 'fr' | 'en') || 'fr'
  const items = lang === 'en' ? SUS_ITEMS_EN : SUS_ITEMS_FR
  const openQuestions = lang === 'en' ? OPEN_QUESTIONS_EN : OPEN_QUESTIONS_FR

  container.innerHTML = `
    <style>
      .study-sus-page {
        max-width: 760px;
        margin: 2rem auto;
        padding: 2rem;
        font-family: 'Segoe UI', sans-serif;
        color: #f8fafc;
      }
      .study-sus-page h1 {
        font-size: 1.6rem;
        color: #4fd1c5;
        margin-bottom: 0.5rem;
      }
      .study-sus-page .subtitle {
        color: #94a3b8;
        margin-bottom: 1.5rem;
      }
      .study-sus-page .likert-item {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 1.1rem 1.2rem;
        margin-bottom: 0.8rem;
      }
      .study-sus-page .likert-statement {
        margin-bottom: 0.8rem;
        line-height: 1.5;
      }
      .study-sus-page .likert-scale {
        display: flex;
        justify-content: space-between;
        gap: 0.4rem;
      }
      .study-sus-page .likert-scale label {
        flex: 1;
        text-align: center;
        padding: 0.5rem 0.4rem;
        border-radius: 6px;
        cursor: pointer;
        border: 1px solid rgba(255,255,255,0.1);
        background: rgba(255,255,255,0.02);
        transition: background 0.15s;
      }
      .study-sus-page .likert-scale label:hover {
        background: rgba(79, 209, 197, 0.1);
      }
      .study-sus-page .likert-scale input[type="radio"] {
        display: none;
      }
      .study-sus-page .likert-scale input[type="radio"]:checked + .pill {
        background: #4fd1c5;
        color: #07111f;
        font-weight: 700;
      }
      .study-sus-page .pill {
        display: inline-block;
        width: 100%;
        padding: 0.25rem;
        border-radius: 4px;
      }
      .study-sus-page .legend {
        display: flex;
        justify-content: space-between;
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 0.4rem;
      }
      .study-sus-page .open-question {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 1.1rem 1.2rem;
        margin-bottom: 0.8rem;
      }
      .study-sus-page .open-question label {
        display: block;
        margin-bottom: 0.6rem;
        font-weight: 600;
      }
      .study-sus-page .open-question textarea {
        width: 100%;
        min-height: 80px;
        padding: 0.6rem;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 6px;
        color: #f8fafc;
        font-family: inherit;
        resize: vertical;
      }
      .study-sus-page .actions {
        display: flex;
        justify-content: flex-end;
        margin-top: 1.5rem;
      }
      .study-sus-page button.submit {
        padding: 0.8rem 2rem;
        background: #4fd1c5;
        color: #07111f;
        border: none;
        border-radius: 8px;
        font-weight: 700;
        cursor: pointer;
        font-size: 1rem;
      }
      .study-sus-page button.submit:disabled {
        background: #2d3748;
        color: #64748b;
        cursor: not-allowed;
      }
      .study-sus-page .error { color: #fb7185; margin-top: 1rem; }
      .study-sus-page .success {
        text-align: center;
        background: rgba(79,209,197,0.08);
        border: 1px solid #4fd1c5;
        border-radius: 12px;
        padding: 2rem;
        margin-top: 1.5rem;
      }
    </style>

    <h1>${t('study.sus.title') || "Questionnaire de satisfaction"}</h1>
    <p class="subtitle">
      ${t('study.sus.subtitle') ||
        "Derniere etape. ~5 minutes. Merci pour ta participation !"}
    </p>

    <h2 style="color:#fbbf24;font-size:1.1rem;margin:1.5rem 0 0.8rem;">
      ${t('study.sus.likertHeader') ||
        "Pour chaque enonce, indique a quel point tu es d'accord (1 = pas du tout, 5 = tout a fait)"}
    </h2>

    <div id="likert-items">
      ${items.map((statement, idx) => `
        <div class="likert-item" data-likert-idx="${idx}">
          <div class="likert-statement">${idx + 1}. ${escapeHtml(statement)}</div>
          <div class="likert-scale">
            ${[1, 2, 3, 4, 5].map(val => `
              <label>
                <input type="radio" name="likert-${idx}" value="${val}">
                <span class="pill">${val}</span>
              </label>
            `).join('')}
          </div>
          <div class="legend">
            <span>${t('study.sus.disagree') || "Pas du tout d'accord"}</span>
            <span>${t('study.sus.agree') || "Tout a fait d'accord"}</span>
          </div>
        </div>
      `).join('')}
    </div>

    <h2 style="color:#fbbf24;font-size:1.1rem;margin:1.5rem 0 0.8rem;">
      ${t('study.sus.openHeader') || "3 questions ouvertes (facultatif mais precieux)"}
    </h2>

    <div class="open-question">
      <label for="open-helped">${escapeHtml(openQuestions.helped)}</label>
      <textarea id="open-helped" data-open-key="helped"
                placeholder="${t('study.sus.placeholder') || 'Quelques phrases suffisent.'}"></textarea>
    </div>
    <div class="open-question">
      <label for="open-frustrated">${escapeHtml(openQuestions.frustrated)}</label>
      <textarea id="open-frustrated" data-open-key="frustrated"
                placeholder="${t('study.sus.placeholder') || 'Quelques phrases suffisent.'}"></textarea>
    </div>
    <div class="open-question">
      <label for="open-recommend">${escapeHtml(openQuestions.recommend)}</label>
      <textarea id="open-recommend" data-open-key="recommend"
                placeholder="${t('study.sus.placeholder') || 'Quelques phrases suffisent.'}"></textarea>
    </div>

    <div class="actions">
      <button class="submit" id="sus-submit" disabled>
        ${t('study.sus.submit') || "Soumettre et terminer l'etude"}
      </button>
    </div>
    <div id="feedback"></div>
  `

  // ============================================================
  // State + validation
  // ============================================================
  const likertValues: (number | null)[] = new Array(items.length).fill(null)
  const openResponses: Record<string, string> = {}
  const submitBtn = container.querySelector<HTMLButtonElement>('#sus-submit')!
  const feedback = container.querySelector<HTMLDivElement>('#feedback')!

  function updateSubmitState(): void {
    const allLikertAnswered = likertValues.every(v => v !== null)
    submitBtn.disabled = !allLikertAnswered
  }

  // Radio listeners
  container.querySelectorAll<HTMLInputElement>('input[type="radio"]').forEach(input => {
    input.addEventListener('change', () => {
      const idx = parseInt(input.name.replace('likert-', ''), 10)
      likertValues[idx] = parseInt(input.value, 10)
      updateSubmitState()
    })
  })

  // Textarea listeners (the open questions remain optional,
  // so we do not gate the submit on them).
  container.querySelectorAll<HTMLTextAreaElement>('textarea[data-open-key]').forEach(ta => {
    ta.addEventListener('input', () => {
      const key = ta.dataset.openKey!
      openResponses[key] = ta.value.trim()
    })
  })

  // Submit
  submitBtn.addEventListener('click', async () => {
    submitBtn.disabled = true
    feedback.innerHTML = ''
    try {
      const resp = await api.studySubmitSus({
        likert: likertValues as number[],
        open_responses: openResponses,
      })
      feedback.innerHTML = `
        <div class="success">
          <h2 style="color:#4fd1c5;font-size:1.4rem;">
            ${t('study.sus.thanks') || "Merci enormement !"}
          </h2>
          <p style="margin:1rem 0;">
            ${t('study.sus.thanksDetail') ||
              "Ta participation contribue a faire avancer la recherche en pedagogie."}
          </p>
          <p style="color:#94a3b8;">
            ${t('study.sus.code') || "Code participant :"}
            <strong style="color:#fbbf24;">${escapeHtml(resp.participant_code)}</strong>
          </p>
          <p style="color:#94a3b8;font-size:0.9rem;margin-top:0.5rem;">
            ${t('study.sus.lottery') || "Si tu es tire au sort pour la carte cadeau, on te contactera par email."}
          </p>
          <button class="submit" id="back-dashboard" style="margin-top:1.5rem;">
            ${t('study.sus.backDashboard') || "Retour au tableau de bord"}
          </button>
        </div>
      `
      const backBtn = container.querySelector<HTMLButtonElement>('#back-dashboard')!
      backBtn.addEventListener('click', () => router.navigate('/dashboard'))
    } catch (err) {
      console.error('[study-sus] submit failed', err)
      const message = err instanceof Error ? err.message : String(err)
      feedback.innerHTML = `<p class="error">
        ${t('study.sus.error') || "Erreur lors de la soumission :"}
        ${escapeHtml(message)}
      </p>`
      submitBtn.disabled = false
    }
  })

  return container
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}
