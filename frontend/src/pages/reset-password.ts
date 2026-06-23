// ============================================================
// Page : /reset-password (token capture depuis ?token=...)
// ============================================================
// Sequence :
//   1. Au load : extrait le token depuis l'URL (?token=... ou path).
//      Si absent, on bascule sur l'etat "no-token" (carte rouge).
//   2. L'utilisateur saisit nouveau mot de passe (x2 pour confirmer).
//      Indicateur de force + toggle voir/masquer pour chaque champ.
//   3. Submit -> POST /auth/reset-password { token, new_password }.
//   4. Si OK : etat "success" avec icone cle verte et CTA login.
//      Si erreur : message rouge dans le formulaire.
// ============================================================
import { api } from '../api'
import { createAppShell } from '../components/app-shell'
import { t } from '../i18n'

export function ResetPasswordPage(): HTMLElement {
  const shell = createAppShell({ activeRoute: '/reset-password', layout: 'focus' })
  const page = document.createElement('main')
  page.className = 'auth-page'

  // Recupere le token depuis ?token=... ou depuis le path /reset-password/<token>.
  const params = new URLSearchParams(window.location.search)
  let token = params.get('token') || ''
  if (!token) {
    const pathMatch = window.location.pathname.match(/\/reset-password\/(.+)$/)
    if (pathMatch) token = decodeURIComponent(pathMatch[1])
  }

  page.innerHTML = `
    <style>
      /* Centrage parfait + gradient discret en arriere-plan */
      .auth-page {
        min-height: 100vh;
        display: grid;
        place-items: center;
        padding: var(--space-6);
        background: linear-gradient(180deg, #f0f9f8 0%, #f8fafc 100%);
      }

      /* Grosse card centree, padding genereux, ombre douce */
      .reset-card {
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

      /* Logo en haut, sans soulignement */
      .reset-brand {
        display: inline-flex; align-items: center; gap: 10px;
        margin: 0 auto var(--space-5);
        text-decoration: none !important;
        color: var(--text-primary);
        justify-content: center;
        width: 100%;
      }
      .reset-brand:hover { text-decoration: none !important; }
      .reset-brand-logo {
        width: 36px; height: 36px;
        border-radius: 10px;
        background: var(--brand-gradient);
        color: #ffffff;
        display: grid; place-items: center;
        font-weight: 800; font-size: 14px;
        letter-spacing: 0.5px;
      }
      .reset-brand-name {
        font-size: 1rem; font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.01em;
      }

      /* Icone centrale (cle / check / warning) */
      .reset-icon-wrap {
        width: 72px; height: 72px;
        margin: 0 auto var(--space-4);
        border-radius: 50%;
        display: grid; place-items: center;
        background: rgba(15, 118, 110, 0.12);
        color: var(--brand-600);
      }
      .reset-icon-wrap.success {
        background: rgba(16, 185, 129, 0.14);
        color: #059669;
      }
      .reset-icon-wrap.error {
        background: rgba(220, 38, 38, 0.12);
        color: #dc2626;
      }
      .reset-icon-wrap svg { width: 36px; height: 36px; }

      /* Titre + sous-titre centres */
      .reset-title {
        text-align: center;
        font-size: 1.6rem; font-weight: 800;
        margin: 0 0 12px;
        color: var(--text-primary);
        letter-spacing: -0.02em;
      }
      .reset-sub {
        text-align: center;
        margin: 0 0 28px;
        color: var(--text-muted);
        font-size: 0.95rem; line-height: 1.55;
      }

      /* Form inputs alignes avec forgot-password */
      .reset-state .ds-label {
        display: block;
        font-size: 0.78rem;
        font-weight: 700;
        color: var(--text-secondary);
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 8px;
      }
      .reset-input-wrap {
        position: relative;
        margin-bottom: 16px;
      }
      .reset-state .ds-input {
        width: 100%;
        height: 48px;
        padding: 0 44px 0 16px; /* place pour le toggle voir/masquer */
        font-size: 0.95rem;
        border-radius: 10px;
        border: 1.5px solid var(--border-default);
        background: var(--bg-surface);
        transition: all 0.2s;
      }
      .reset-state .ds-input:focus {
        border-color: var(--brand-500);
        box-shadow: 0 0 0 4px rgba(15, 118, 110, 0.12);
        outline: none;
      }

      /* Toggle voir / masquer le mot de passe */
      .reset-eye-btn {
        position: absolute;
        right: 12px;
        top: 50%;
        transform: translateY(-50%);
        margin-top: 14px; /* compense le label au-dessus */
        background: transparent;
        border: none;
        padding: 4px;
        cursor: pointer;
        color: var(--text-muted);
        transition: color 0.2s;
        line-height: 0;
      }
      .reset-eye-btn:hover { color: var(--brand-600); }
      .reset-eye-btn svg { width: 18px; height: 18px; }

      /* Indicateur de force du mot de passe */
      .reset-strength {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 6px;
        margin: -8px 0 14px;
      }
      .reset-strength-bar {
        height: 4px;
        border-radius: 2px;
        background: #e5e7eb;
        transition: background 0.25s;
      }
      .reset-strength-bar.on-weak   { background: #dc2626; }
      .reset-strength-bar.on-medium { background: #f59e0b; }
      .reset-strength-bar.on-good   { background: #10b981; }
      .reset-strength-bar.on-strong { background: #059669; }
      .reset-strength-label {
        font-size: 0.78rem;
        font-weight: 600;
        color: var(--text-muted);
        margin: 0 0 16px;
        text-align: right;
        letter-spacing: 0.02em;
      }

      .reset-state .ds-btn-primary {
        width: 100%;
        height: 48px;
        margin-top: 8px;
        font-size: 0.95rem;
        font-weight: 700;
        border-radius: 10px;
      }

      /* Etats : transitions douces */
      .reset-state { display: none; animation: resetFadeIn 0.35s ease; }
      .reset-state.active { display: block; }
      @keyframes resetFadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0); }
      }

      /* Message d'erreur dans le formulaire */
      .reset-error {
        display: none;
        margin: 0 0 16px;
        padding: 12px 14px;
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-left: 4px solid #dc2626;
        border-radius: 8px;
        font-size: 0.88rem;
        color: #7f1d1d;
        line-height: 1.45;
      }
      .reset-error.visible { display: block; }

      /* CTA secondaires */
      .reset-actions {
        display: flex; flex-direction: column; gap: 12px;
        margin-top: 24px;
      }
      .reset-secondary-btn {
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
      .reset-secondary-btn:hover {
        background: var(--bg-surface-hover);
        border-color: var(--brand-500);
        color: var(--brand-600);
      }

      /* Petit lien "back to sign in" en bas */
      .reset-foot-link {
        display: block;
        text-align: center;
        margin-top: 20px;
        color: var(--text-muted);
        font-size: 0.88rem;
        text-decoration: none !important;
      }
      .reset-foot-link:hover { color: var(--brand-600); }
    </style>

    <section class="reset-card">
      <a href="/" data-link class="reset-brand">
        <span class="reset-brand-logo">N</span>
        <span class="reset-brand-name">${t('sidebar.brand.name')}</span>
      </a>

      <!-- ETAT 1 : Formulaire (token present) -->
      <div class="reset-state ${token ? 'active' : ''}" id="state-form">
        <div class="reset-icon-wrap" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4" />
          </svg>
        </div>
        <h1 class="reset-title">${t('auth.reset.title')}</h1>
        <p class="reset-sub">${t('auth.reset.intro') || ''}</p>

        <div class="reset-error" id="error-box"></div>

        <form class="auth-form" id="reset-form" novalidate>
          <div>
            <label class="ds-label" for="new-password">${t('auth.reset.newPassword')}</label>
            <div class="reset-input-wrap">
              <input class="ds-input" id="new-password" type="password" autocomplete="new-password" minlength="8" required />
              <button type="button" class="reset-eye-btn" data-toggle="new-password" aria-label="Show password">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                  <circle cx="12" cy="12" r="3" />
                </svg>
              </button>
            </div>

            <!-- Indicateur de force -->
            <div class="reset-strength" id="strength-bars" aria-hidden="true">
              <span class="reset-strength-bar"></span>
              <span class="reset-strength-bar"></span>
              <span class="reset-strength-bar"></span>
              <span class="reset-strength-bar"></span>
            </div>
            <p class="reset-strength-label" id="strength-label"></p>
          </div>

          <div>
            <label class="ds-label" for="confirm-password">${t('auth.reset.confirmPassword')}</label>
            <div class="reset-input-wrap">
              <input class="ds-input" id="confirm-password" type="password" autocomplete="new-password" minlength="8" required />
              <button type="button" class="reset-eye-btn" data-toggle="confirm-password" aria-label="Show password">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                  <circle cx="12" cy="12" r="3" />
                </svg>
              </button>
            </div>
          </div>

          <button class="ds-btn ds-btn-primary" id="submit-btn" type="submit">
            ${t('auth.reset.submit')}
          </button>
        </form>
      </div>

      <!-- ETAT 2 : Succes (mot de passe change) -->
      <div class="reset-state" id="state-success">
        <div class="reset-icon-wrap success" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 6L9 17l-5-5" />
          </svg>
        </div>
        <h1 class="reset-title">${t('auth.reset.successTitle') || t('auth.reset.success')}</h1>
        <p class="reset-sub">${t('auth.reset.successBody') || ''}</p>
        <div class="reset-actions">
          <a href="/login" data-link class="ds-btn ds-btn-primary" style="display:grid; place-items:center; text-decoration:none;">
            ${t('auth.forgot.backToLogin')}
          </a>
        </div>
      </div>

      <!-- ETAT 3 : Token absent ou invalide -->
      <div class="reset-state ${token ? '' : 'active'}" id="state-no-token">
        <div class="reset-icon-wrap error" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="13" />
            <line x1="12" y1="17" x2="12.01" y2="17" />
          </svg>
        </div>
        <h1 class="reset-title">${t('auth.reset.errorTitle') || t('auth.reset.errorGeneric')}</h1>
        <p class="reset-sub">${t('auth.reset.errorBody') || t('auth.reset.errorGeneric')}</p>
        <div class="reset-actions">
          <a href="/forgot-password" data-link class="ds-btn ds-btn-primary" style="display:grid; place-items:center; text-decoration:none;">
            ${t('auth.reset.requestNewLink') || t('auth.forgotLink')}
          </a>
        </div>
      </div>

      <!-- Lien discret "back to sign in" tout en bas -->
      <a href="/login" data-link class="reset-foot-link">
        ← ${t('auth.forgot.backToLogin')}
      </a>
    </section>
  `

  shell.setContent(page)

  // Helper : bascule entre les 3 etats
  const states = {
    form: page.querySelector('#state-form') as HTMLElement,
    success: page.querySelector('#state-success') as HTMLElement,
    'no-token': page.querySelector('#state-no-token') as HTMLElement,
  }
  function showState(name: 'form' | 'success' | 'no-token') {
    Object.entries(states).forEach(([key, el]) => {
      el.classList.toggle('active', key === name)
    })
  }

  // Si pas de token : etat erreur deja actif via le markup, on s'arrete la.
  if (!token) {
    return shell.element
  }

  // Toggle voir / masquer pour les deux champs password
  page.querySelectorAll<HTMLButtonElement>('.reset-eye-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const targetId = btn.dataset.toggle || ''
      const input = page.querySelector(`#${targetId}`) as HTMLInputElement | null
      if (!input) return
      input.type = input.type === 'password' ? 'text' : 'password'
    })
  })

  // Indicateur de force du mot de passe (4 niveaux)
  const newPwd = page.querySelector('#new-password') as HTMLInputElement
  const bars = page.querySelectorAll<HTMLElement>('#strength-bars .reset-strength-bar')
  const strengthLabel = page.querySelector('#strength-label') as HTMLElement

  function pwdScore(pwd: string): { score: 0 | 1 | 2 | 3 | 4; label: string; cls: string } {
    let s = 0
    if (pwd.length >= 8) s += 1
    if (pwd.length >= 12) s += 1
    if (/[A-Z]/.test(pwd) && /[a-z]/.test(pwd)) s += 1
    if (/[0-9]/.test(pwd) && /[^A-Za-z0-9]/.test(pwd)) s += 1
    const map = [
      { label: '', cls: '' },
      { label: t('auth.reset.strengthWeak') || 'Weak', cls: 'on-weak' },
      { label: t('auth.reset.strengthMedium') || 'Medium', cls: 'on-medium' },
      { label: t('auth.reset.strengthGood') || 'Good', cls: 'on-good' },
      { label: t('auth.reset.strengthStrong') || 'Strong', cls: 'on-strong' },
    ] as const
    return { score: s as 0 | 1 | 2 | 3 | 4, ...map[s] }
  }

  newPwd.addEventListener('input', () => {
    const { score, label, cls } = pwdScore(newPwd.value)
    bars.forEach((bar, i) => {
      bar.classList.remove('on-weak', 'on-medium', 'on-good', 'on-strong')
      if (cls && i < score) bar.classList.add(cls)
    })
    strengthLabel.textContent = newPwd.value ? label : ''
  })

  const form = page.querySelector('#reset-form') as HTMLFormElement
  const errorBox = page.querySelector('#error-box') as HTMLElement
  const submitBtn = page.querySelector('#submit-btn') as HTMLButtonElement

  function showError(msg: string) {
    errorBox.textContent = msg
    errorBox.classList.add('visible')
  }
  function hideError() {
    errorBox.classList.remove('visible')
  }

  form.addEventListener('submit', async (event) => {
    event.preventDefault()
    hideError()

    const newPassword = (page.querySelector('#new-password') as HTMLInputElement).value
    const confirmPassword = (page.querySelector('#confirm-password') as HTMLInputElement).value

    // Validation client : longueur min + match
    if (newPassword.length < 8) {
      showError(t('auth.reset.errorMinLength'))
      return
    }
    if (newPassword !== confirmPassword) {
      showError(t('auth.reset.errorMismatch'))
      return
    }

    submitBtn.disabled = true
    submitBtn.textContent = t('auth.reset.sending') || '...'

    try {
      await api.resetPassword(token, newPassword)
      showState('success')
    } catch (err: any) {
      showError(err?.message || t('auth.reset.errorGeneric'))
      submitBtn.disabled = false
      submitBtn.textContent = t('auth.reset.submit')
    }
  })

  return shell.element
}
