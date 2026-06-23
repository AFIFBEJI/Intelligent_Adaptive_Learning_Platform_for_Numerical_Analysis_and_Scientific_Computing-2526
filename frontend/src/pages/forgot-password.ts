// ============================================================
// Page : /forgot-password
// ============================================================
// Trois etats UI distincts :
//   - "form"     : formulaire email (etat initial)
//   - "success"  : carte verte avec icone enveloppe + instructions
//   - "notfound" : carte rouge "le compte n'existe pas" + CTA register
//
// Le backend retourne :
//   - 200 si le compte existe -> on bascule sur "success"
//   - 404 si le compte n'existe pas -> on bascule sur "notfound"
// ============================================================
import { api } from '../api'
import { createAppShell } from '../components/app-shell'
import { t } from '../i18n'

export function ForgotPasswordPage(): HTMLElement {
  const shell = createAppShell({ activeRoute: '/forgot-password', layout: 'focus' })
  const page = document.createElement('main')
  page.className = 'auth-page'

  page.innerHTML = `
    <style>
      /* La page entiere : centrage parfait vertical + horizontal */
      .auth-page {
        min-height: 100vh;
        display: grid;
        place-items: center;
        padding: var(--space-6);
        background: linear-gradient(180deg, #f0f9f8 0%, #f8fafc 100%);
      }

      /* Grosse card centree, bien aeree, avec ombre douce */
      .forgot-card {
        width: 100%;
        max-width: 520px;
        padding: 48px 40px;
        background: #ffffff;
        border-radius: 20px;
        box-shadow:
          0 20px 60px rgba(15, 23, 42, 0.08),
          0 4px 12px rgba(15, 23, 42, 0.04);
        border: 1px solid rgba(15, 118, 110, 0.08);
      }

      /* Logo en haut, sans soulignement, pas de lien-style */
      .forgot-brand {
        display: inline-flex; align-items: center; gap: 10px;
        margin: 0 auto var(--space-5);
        text-decoration: none !important;
        color: var(--text-primary);
        justify-content: center;
        width: 100%;
      }
      .forgot-brand:hover { text-decoration: none !important; }
      .forgot-brand-logo {
        width: 36px; height: 36px;
        border-radius: 10px;
        background: var(--brand-gradient);
        color: #ffffff;
        display: grid; place-items: center;
        font-weight: 800; font-size: 14px;
        letter-spacing: 0.5px;
      }
      .forgot-brand-name {
        font-size: 1rem; font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.01em;
      }

      /* Icone centrale (cadenas / mail / warning) */
      .forgot-icon-wrap {
        width: 72px; height: 72px;
        margin: 0 auto var(--space-4);
        border-radius: 50%;
        display: grid; place-items: center;
        background: rgba(15, 118, 110, 0.12);
        color: var(--brand-600);
      }
      .forgot-icon-wrap.success {
        background: rgba(16, 185, 129, 0.14);
        color: #059669;
      }
      .forgot-icon-wrap.error {
        background: rgba(220, 38, 38, 0.12);
        color: #dc2626;
      }
      .forgot-icon-wrap svg { width: 36px; height: 36px; }

      /* Titre + sous-titre centres */
      .forgot-title-center {
        text-align: center;
        font-size: 1.6rem; font-weight: 800;
        margin: 0 0 12px;
        color: var(--text-primary);
        letter-spacing: -0.02em;
      }
      .forgot-sub-center {
        text-align: center;
        margin: 0 0 28px;
        color: var(--text-muted);
        font-size: 0.95rem; line-height: 1.55;
      }

      /* Form input plus grand, plus accueillant */
      .forgot-state .ds-label {
        display: block;
        font-size: 0.78rem;
        font-weight: 700;
        color: var(--text-secondary);
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 8px;
      }
      .forgot-state .ds-input {
        width: 100%;
        height: 48px;
        padding: 0 16px;
        font-size: 0.95rem;
        border-radius: 10px;
        border: 1.5px solid var(--border-default);
        background: var(--bg-surface);
        transition: all 0.2s;
      }
      .forgot-state .ds-input:focus {
        border-color: var(--brand-500);
        box-shadow: 0 0 0 4px rgba(15, 118, 110, 0.12);
        outline: none;
      }

      .forgot-state .ds-btn-primary {
        width: 100%;
        height: 48px;
        margin-top: 16px;
        font-size: 0.95rem;
        font-weight: 700;
        border-radius: 10px;
      }

      /* Etats : transitions douces */
      .forgot-state { display: none; animation: forgotFadeIn 0.35s ease; }
      .forgot-state.active { display: block; }
      @keyframes forgotFadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0); }
      }

      /* CTA secondaires (Back, Try another) */
      .forgot-actions {
        display: flex; flex-direction: column; gap: 12px;
        margin-top: 24px;
      }
      .forgot-secondary-btn {
        background: transparent;
        border: 1.5px solid var(--border-default);
        height: 44px;
        border-radius: 10px;
        color: var(--text-primary);
        font-weight: 600; font-size: 0.92rem;
        cursor: pointer;
        text-align: center;
        text-decoration: none !important;
        display: grid; place-items: center;
        transition: all 0.2s;
      }
      .forgot-secondary-btn:hover {
        background: var(--bg-surface-hover);
        border-color: var(--brand-500);
        color: var(--brand-600);
      }

      /* Petit lien "back to sign in" en bas, discret */
      .forgot-foot-link {
        display: block;
        text-align: center;
        margin-top: 20px;
        color: var(--text-muted);
        font-size: 0.88rem;
        text-decoration: none !important;
      }
      .forgot-foot-link:hover { color: var(--brand-600); }
    </style>

    <section class="forgot-card">
      <a href="/" data-link class="forgot-brand">
        <span class="forgot-brand-logo">N</span>
        <span class="forgot-brand-name">${t('sidebar.brand.name')}</span>
      </a>

      <!-- ETAT 1 : Formulaire -->
      <div class="forgot-state active" id="state-form">
        <div class="forgot-icon-wrap" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="11" width="18" height="11" rx="2" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </svg>
        </div>
        <h1 class="forgot-title-center">${t('auth.forgot.title')}</h1>
        <p class="forgot-sub-center">${t('auth.forgot.intro')}</p>

        <form class="auth-form" id="forgot-form" novalidate>
          <label>
            <span class="ds-label">${t('auth.email')}</span>
            <input class="ds-input" id="email" type="email" autocomplete="email" placeholder="you@example.com" required />
          </label>
          <button class="ds-btn ds-btn-primary" id="submit-btn" type="submit">
            ${t('auth.forgot.submit')}
          </button>
        </form>
      </div>

      <!-- ETAT 2 : Succes (mail envoye) -->
      <div class="forgot-state" id="state-success">
        <div class="forgot-icon-wrap success" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="5" width="18" height="14" rx="2" />
            <path d="M3 7l9 6 9-6" />
          </svg>
        </div>
        <h1 class="forgot-title-center">${t('auth.forgot.successTitle')}</h1>
        <p class="forgot-sub-center" id="success-body-text">${t('auth.forgot.successBody')}</p>
        <div class="forgot-actions">
          <a href="/login" data-link class="forgot-secondary-btn">
            ${t('auth.forgot.backToLogin')}
          </a>
        </div>
      </div>

      <!-- ETAT 3 : Compte inexistant -->
      <div class="forgot-state" id="state-notfound">
        <div class="forgot-icon-wrap error" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="13" />
            <line x1="12" y1="17" x2="12.01" y2="17" />
          </svg>
        </div>
        <h1 class="forgot-title-center">${t('auth.forgot.notFoundTitle')}</h1>
        <p class="forgot-sub-center">${t('auth.forgot.notFoundBody')}</p>
        <div class="forgot-actions">
          <a href="/register" data-link class="ds-btn ds-btn-primary" style="display:grid; place-items:center; text-decoration:none;">
            ${t('auth.forgot.notFoundCta')}
          </a>
          <button type="button" class="forgot-secondary-btn" id="btn-try-another">
            ${t('auth.forgot.tryAnother')}
          </button>
        </div>
      </div>

      <!-- Lien discret "back to sign in" tout en bas, valable sur tous les etats -->
      <a href="/login" data-link class="forgot-foot-link">
        ← ${t('auth.forgot.backToLogin')}
      </a>
    </section>
  `

  shell.setContent(page)

  // Helper : bascule entre les 3 etats
  const states = {
    form: page.querySelector('#state-form') as HTMLElement,
    success: page.querySelector('#state-success') as HTMLElement,
    notfound: page.querySelector('#state-notfound') as HTMLElement,
  }
  function showState(name: 'form' | 'success' | 'notfound') {
    Object.entries(states).forEach(([key, el]) => {
      el.classList.toggle('active', key === name)
    })
  }

  const form = page.querySelector('#forgot-form') as HTMLFormElement
  const submitBtn = page.querySelector('#submit-btn') as HTMLButtonElement

  form.addEventListener('submit', async (event) => {
    event.preventDefault()

    const email = (page.querySelector('#email') as HTMLInputElement).value.trim()
    if (!email) return

    submitBtn.disabled = true
    submitBtn.textContent = t('auth.forgot.sending')

    try {
      await api.forgotPassword(email)
      // Backend a renvoye 200 -> compte existe et mail envoye
      showState('success')
    } catch (err: any) {
      // Backend a renvoye 404 -> compte introuvable
      // (L'API client lit le err.detail du backend ; on affiche notre etat
      // local au lieu de le re-afficher mot pour mot.)
      const msg = (err?.message || '').toLowerCase()
      if (msg.includes('no account') || msg.includes('not found') || msg.includes('introuvable')) {
        showState('notfound')
      } else {
        // Erreur reseau / serveur : on remet l'etat form avec un message
        // generique discret. Pas de carte rouge.
        alert(err?.message || 'Network error')
        submitBtn.disabled = false
        submitBtn.textContent = t('auth.forgot.submit')
      }
    }
  })

  // Bouton "essayer un autre email" sur l'etat notfound : revient au form
  page.querySelector('#btn-try-another')?.addEventListener('click', () => {
    showState('form')
    submitBtn.disabled = false
    submitBtn.textContent = t('auth.forgot.submit')
    ;(page.querySelector('#email') as HTMLInputElement).focus()
  })

  return shell.element
}
