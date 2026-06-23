import { api } from '../api'
import { createAppShell } from '../components/app-shell'
import { hasChosenLang, setLang, t, type Lang } from '../i18n'
import { router } from '../router'

export function RegisterPage(): HTMLElement {
  const shell = createAppShell({ activeRoute: '/register', layout: 'focus' })
  const page = document.createElement('main')
  page.className = 'auth-page'

  // Aucune langue pré-sélectionnée tant que l'utilisateur n'a pas choisi.
  const initialLang: Lang | '' = hasChosenLang() ? (localStorage.getItem('app_lang') as Lang) : ''

  page.innerHTML = `
    <style>
      .auth-page {
        min-height: 100vh;
        display: grid;
        place-items: center;
        padding: var(--space-6);
        background: transparent;
      }
      .auth-card {
        width: min(100%, 500px);
        padding: var(--space-8);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-md);
        background: var(--bg-surface);
        box-shadow: var(--shadow-lg);
      }
      .auth-brand { display: inline-flex; align-items: center; gap: var(--space-3); margin-bottom: var(--space-6); text-decoration: none; }
      .auth-logo {
        width: 38px; height: 38px; display: grid; place-items: center;
        border-radius: var(--radius-md); color: #ffffff;
        background: var(--brand-gradient);
        font-weight: var(--font-weight-extrabold);
      }
      .auth-title { margin: 0 0 var(--space-2); font-size: var(--text-3xl); line-height: var(--line-height-tight); }
      .auth-sub { margin: 0 0 var(--space-6); color: var(--text-muted); line-height: var(--line-height-relaxed); }
      .auth-form { display: flex; flex-direction: column; gap: var(--space-4); }
      .language-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-3); }
      .language-option {
        min-height: 58px;
        border: 1px solid var(--border-default);
        border-radius: var(--radius-md);
        background: var(--bg-surface);
        color: var(--text-secondary);
        font-weight: var(--font-weight-bold);
        cursor: pointer;
      }
      .language-option.active {
        border-color: var(--info-border);
        color: var(--brand-600);
        background: rgba(15, 118, 110, 0.1);
        box-shadow: var(--shadow-focus);
      }
      .language-required {
        font-size: var(--text-sm);
        color: var(--text-muted);
        margin-top: var(--space-2);
      }
      .auth-form button[disabled] { opacity: 0.6; cursor: not-allowed; }
      .auth-foot { margin-top: var(--space-5); color: var(--text-muted); font-size: var(--text-sm); text-align: center; }

      /* Petite note inline, ultra discrete */
      .lang-quiz-note {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-top: 8px;
        font-size: 0.78rem;
        color: var(--text-muted);
        line-height: 1.4;
      }
      .lang-quiz-note svg {
        flex-shrink: 0;
        width: 13px; height: 13px;
        color: var(--brand-600);
        opacity: 0.85;
      }
    </style>

    <section class="auth-card">
      <a href="/" data-link class="auth-brand">
        <span class="auth-logo">AL</span>
        <span>${t('sidebar.brand.name')}</span>
      </a>
      <h1 class="auth-title">${t('auth.register.title')}</h1>
      <p class="auth-sub">${t('auth.register.subtitle')}</p>
      <div class="ds-alert ds-alert-error" id="error-box" style="display:none;"></div>
      <form class="auth-form" id="register-form" novalidate>
        <div>
          <span class="ds-label">${t('auth.language')} *</span>
          <div class="language-grid" role="radiogroup" aria-label="${t('auth.language')}" aria-required="true">
            <button type="button" class="language-option ${initialLang === 'en' ? 'active' : ''}" data-lang="en">${t('auth.english')}</button>
            <button type="button" class="language-option ${initialLang === 'fr' ? 'active' : ''}" data-lang="fr">${t('auth.french')}</button>
          </div>
          <input type="hidden" id="langue" value="${initialLang}" required />

          <!-- Petite ligne inline ultra discrete : juste pour le quiz. -->
          <p class="lang-quiz-note" role="note">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="16" x2="12" y2="12" />
              <line x1="12" y1="8" x2="12.01" y2="8" />
            </svg>
            <span>${t('auth.langInfo.quizMain')}</span>
          </p>
        </div>
        <label>
          <span class="ds-label">${t('auth.fullName')}</span>
          <input class="ds-input" id="nom" type="text" autocomplete="name" required />
        </label>
        <label>
          <span class="ds-label">${t('auth.email')}</span>
          <input class="ds-input" id="email" type="email" autocomplete="email" required />
        </label>
        <label>
          <span class="ds-label">${t('auth.password')}</span>
          <input class="ds-input" id="password" type="password" autocomplete="new-password" minlength="8" required />
        </label>
        <button class="ds-btn ds-btn-primary" id="submit-btn" type="submit" ${initialLang ? '' : 'disabled'}>${t('auth.register.submit')}</button>
      </form>
      <div class="auth-foot">
        ${t('auth.haveAccount')} <a href="/login" data-link class="ds-link">${t('auth.goLogin')}</a>
      </div>
    </section>
  `
  shell.setContent(page)

  const langInput = page.querySelector('#langue') as HTMLInputElement
  const submitBtn = page.querySelector('#submit-btn') as HTMLButtonElement

  page.querySelectorAll<HTMLButtonElement>('.language-option').forEach((btn) => {
    btn.addEventListener('click', () => {
      const lang = (btn.dataset.lang as Lang) || 'en'
      page.querySelectorAll('.language-option').forEach((item) => item.classList.remove('active'))
      btn.classList.add('active')
      langInput.value = lang
      submitBtn.disabled = false
      setLang(lang)
      router.navigate('/register')
    })
  })

  const form = page.querySelector('#register-form') as HTMLFormElement
  const errorBox = page.querySelector('#error-box') as HTMLElement

  form.addEventListener('submit', async (event) => {
    event.preventDefault()
    errorBox.style.display = 'none'

    const chosenLang = (langInput.value || '') as Lang | ''
    if (chosenLang !== 'en' && chosenLang !== 'fr') {
      errorBox.textContent = t('auth.error.langRequired')
      errorBox.style.display = 'block'
      return
    }

    submitBtn.disabled = true
    submitBtn.textContent = t('auth.register.loading')

    try {
      const token = await api.register({
        nom_complet: (page.querySelector('#nom') as HTMLInputElement).value,
        email: (page.querySelector('#email') as HTMLInputElement).value,
        mot_de_passe: (page.querySelector('#password') as HTMLInputElement).value,
        niveau_actuel: 'beginner',
        langue_preferee: chosenLang,
      })
      api.setToken(token.access_token)
      localStorage.setItem('token', token.access_token)
      const user = await api.getMe()
      localStorage.setItem('user', JSON.stringify(user))
      setLang(user.langue_preferee || chosenLang)
      router.navigate('/onboarding-quiz')
    } catch (err) {
      errorBox.textContent = err instanceof Error ? err.message : t('auth.error.register')
      errorBox.style.display = 'block'
      submitBtn.disabled = false
      submitBtn.textContent = t('auth.register.submit')
    }
  })

  return shell.element
}
