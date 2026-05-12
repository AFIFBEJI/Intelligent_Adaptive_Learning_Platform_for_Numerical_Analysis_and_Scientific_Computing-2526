// ============================================================
// Phase 4 — Page d'accueil de l'étude utilisateur
// ============================================================
// Cette page :
//   1. Affiche le consentement éclairé (résumé + lien doc complet).
//   2. Permet à l'étudiant de cocher 7 cases obligatoires + soumettre.
//   3. Appelle POST /study/enroll pour s'inscrire.
//   4. Redirige vers /study/pretest une fois le consentement signé.
//
// Le formulaire de consentement complet (10 KB FR+EN) est dans
// docs/phase4/02_CONSENTEMENT.md. Ici on présente la version condensée
// pour ne pas surcharger l'UI : si l'étudiant veut lire le détail, il
// clique sur "Lire le formulaire complet" qui ouvre la page docs/.

import { api } from '../api'
import { t } from '../i18n'
import { router } from '../router'

const CONSENT_KEYS = [
  'study.consent.read',
  'study.consent.questions',
  'study.consent.age',
  'study.consent.student',
  'study.consent.voluntary',
  'study.consent.collection',
  'study.consent.publication',
] as const

export function StudyWelcomePage(): HTMLElement {
  const container = document.createElement('div')
  container.className = 'study-welcome-page'

  container.innerHTML = `
    <style>
      .study-welcome-page {
        max-width: 720px;
        margin: 2rem auto;
        padding: 2rem;
        font-family: 'Segoe UI', sans-serif;
        color: #f8fafc;
      }
      .study-welcome-page h1 {
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
        color: #4fd1c5;
      }
      .study-welcome-page .subtitle {
        color: #94a3b8;
        margin-bottom: 1.5rem;
      }
      .study-welcome-page .card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        line-height: 1.6;
      }
      .study-welcome-page .card h2 {
        font-size: 1.2rem;
        margin-bottom: 0.75rem;
        color: #fbbf24;
      }
      .study-welcome-page .consent-list label {
        display: flex;
        align-items: flex-start;
        gap: 0.5rem;
        margin-bottom: 0.6rem;
        cursor: pointer;
      }
      .study-welcome-page .consent-list input[type="checkbox"] {
        margin-top: 0.25rem;
        flex-shrink: 0;
        cursor: pointer;
      }
      .study-welcome-page .actions {
        display: flex;
        gap: 1rem;
        margin-top: 1.5rem;
      }
      .study-welcome-page button {
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        border: none;
        font-size: 1rem;
      }
      .study-welcome-page button.primary {
        background: #4fd1c5;
        color: #07111f;
      }
      .study-welcome-page button.primary:disabled {
        background: #2d3748;
        color: #64748b;
        cursor: not-allowed;
      }
      .study-welcome-page button.secondary {
        background: transparent;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: #f8fafc;
      }
      .study-welcome-page .error {
        color: #fb7185;
        margin-top: 1rem;
      }
      .study-welcome-page .success {
        color: #4fd1c5;
        margin-top: 1rem;
        font-weight: 600;
      }
    </style>

    <h1>${t('study.welcome.title') || "Etude utilisateur — bienvenue"}</h1>
    <p class="subtitle">
      ${t('study.welcome.subtitle') ||
        "Tu participes a une recherche en EdTech (ESPRIT, PFE 2026). Merci pour ton temps."}
    </p>

    <div class="card">
      <h2>${t('study.about.title') || "En 30 secondes"}</h2>
      <ul>
        <li>${t('study.about.duration') ||
          "Engagement total : ~13h sur 6 semaines (3h/sem d'usage + 2 quiz de 20 min)."}</li>
        <li>${t('study.about.groups') ||
          "Tu es assigne(e) aleatoirement a un groupe : plateforme adaptive (IA) OU support classique."}</li>
        <li>${t('study.about.privacy') ||
          "Tes donnees sont pseudonymisees (P###). Pas de nom, pas d'email dans les analyses."}</li>
        <li>${t('study.about.withdraw') ||
          "Tu peux te retirer a tout moment sans justification."}</li>
        <li>${t('study.about.lottery') ||
          "Loterie a la fin : 1 carte Amazon 50 TND par groupe (chances 1/15)."}</li>
      </ul>
      <p style="margin-top:1rem;">
        <a href="/docs/phase4/02_CONSENTEMENT.md" target="_blank"
           style="color:#fbbf24; text-decoration:underline;">
          ${t('study.about.full_consent') || "Lire le formulaire de consentement complet (FR + EN)"}
        </a>
      </p>
    </div>

    <div class="card">
      <h2>${t('study.consent.title') || "Consentement eclaire"}</h2>
      <p>${t('study.consent.intro') ||
        "Coche chaque case ci-dessous pour confirmer ton consentement :"}</p>
      <div class="consent-list">
        ${CONSENT_KEYS.map((key, idx) => `
          <label>
            <input type="checkbox" data-consent-key="${key}" id="consent-${idx}">
            <span>${getConsentText(key)}</span>
          </label>
        `).join('')}
      </div>
    </div>

    <div class="actions">
      <button class="secondary" id="study-cancel">
        ${t('study.welcome.cancel') || "Plus tard"}
      </button>
      <button class="primary" id="study-enroll" disabled>
        ${t('study.welcome.enroll') || "Je participe -> Commencer le pre-test"}
      </button>
    </div>
    <div id="study-feedback"></div>
  `

  // ============================================================
  // Activation du bouton "Je participe" UNIQUEMENT si TOUTES les
  // cases sont cochees. C'est l'equivalent UI du "signature" RGPD.
  // ============================================================
  const checkboxes = Array.from(
    container.querySelectorAll<HTMLInputElement>('input[data-consent-key]'),
  )
  const enrollBtn = container.querySelector<HTMLButtonElement>('#study-enroll')!
  const cancelBtn = container.querySelector<HTMLButtonElement>('#study-cancel')!
  const feedback = container.querySelector<HTMLDivElement>('#study-feedback')!

  function updateEnrollState(): void {
    enrollBtn.disabled = checkboxes.some(cb => !cb.checked)
  }
  checkboxes.forEach(cb => cb.addEventListener('change', updateEnrollState))

  cancelBtn.addEventListener('click', () => {
    router.navigate('/dashboard')
  })

  enrollBtn.addEventListener('click', async () => {
    enrollBtn.disabled = true
    feedback.innerHTML = ''
    try {
      const resp = await api.studyEnroll()
      const message = resp.already_enrolled
        ? (t('study.welcome.already') || "Tu es deja inscrit(e)") +
          ` (code : ${resp.participant_code})`
        : (t('study.welcome.enrolled') || "Inscription reussie !") +
          ` ${t('study.welcome.code') || "Ton code :"} ${resp.participant_code}`
      feedback.innerHTML = `<p class="success">${message}</p>`
      // Petite pause pour que l'etudiant voie son code, puis redirige.
      setTimeout(() => router.navigate('/study/pretest'), 1500)
    } catch (err) {
      console.error('[study-welcome] enroll failed', err)
      const message = err instanceof Error ? err.message : String(err)
      feedback.innerHTML = `<p class="error">
        ${t('study.welcome.error') || "Une erreur est survenue :"} ${escape(message)}
      </p>`
      enrollBtn.disabled = false
    }
  })

  return container
}

// ============================================================
// Textes du consentement (fallback FR si i18n manquant)
// ============================================================
function getConsentText(key: string): string {
  const fallback = t(key)
  if (fallback && fallback !== key) return fallback
  // Fallback FR si la cle n'est pas dans i18n.ts.
  switch (key) {
    case 'study.consent.read':
      return "J'ai lu et compris la presentation de cette etude."
    case 'study.consent.questions':
      return "J'ai eu l'occasion de poser des questions."
    case 'study.consent.age':
      return "J'ai 18 ans revolus."
    case 'study.consent.student':
      return "Je suis etudiant(e) en formation d'ingenieur."
    case 'study.consent.voluntary':
      return "Je participe volontairement et je sais que je peux me retirer."
    case 'study.consent.collection':
      return "J'autorise la collecte de mes donnees dans les conditions decrites."
    case 'study.consent.publication':
      return "J'accepte que les donnees pseudonymisees soient publiees dans un article scientifique."
    default:
      return key
  }
}

function escape(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}
