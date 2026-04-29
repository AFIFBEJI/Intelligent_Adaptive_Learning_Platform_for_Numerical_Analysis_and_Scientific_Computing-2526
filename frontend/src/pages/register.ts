import { api } from '../api'
import { createAppShell } from '../components/app-shell'
import { getLang, setLang, t, type Lang } from '../i18n'
import { router } from '../router'

export function RegisterPage(): HTMLElement {
  const shell = createAppShell({ activeRoute: '/register', layout: 'focus' })
  const page = document.createElement('main')
  page.className = 'auth-page'
  const selectedLang = getLang()
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
        color: var(--brand-100);
        background: var(--info-bg);
        box-shadow: var(--shadow-focus);
      }
      .auth-foot { margin-top: var(--space-5); color: var(--text-muted); font-size: var(--text-sm); text-align: center; }
    </style>

    <section class="auth-card">
      <a href="/" data-link class="auth-brand">
        <span class="auth-logo">AL</span>
        <span>${t('sidebar.brand.name')}</span>
      </a>
      <h1 class="auth-title">${t('auth.register.title')}</h1>
      <p class="auth-sub">${t('auth.register.subtitle')}</p>
      <div class="ds-alert ds-alert-error" id="error-box" style="display:none;"></div>
      <form class="auth-form" id="register-form">
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
        <div>
          <span class="ds-label">${t('auth.language')}</span>
          <div class="language-grid" role="radiogroup" aria-label="${t('auth.language')}">
            <button type="button" class="language-option ${selectedLang === 'en' ? 'active' : ''}" data-lang="en">${t('auth.english')}</button>
            <button type="button" class="language-option ${selectedLang === 'fr' ? 'active' : ''}" data-lang="fr">${t('auth.french')}</button>
          </div>
          <input type="hidden" id="langue" value="${selectedLang}" />
        </div>
        <button class="ds-btn ds-btn-primary" id="submit-btn" type="submit">${t('auth.register.submit')}</button>
      </form>
      <div class="auth-foot">
        ${t('auth.haveAccount')} <a href="/login" data-link class="ds-link">${t('auth.goLogin')}</a>
      </div>
    </section>
  `
  shell.setContent(page)

  page.querySelectorAll<HTMLButtonElement>('.language-option').forEach(btn => {
    btn.addEventListener('click', () => {
      const lang = (btn.dataset.lang as Lang) || 'en'
      page.querySelectorAll('.language-option').forEach(item => item.classList.remove('active'))
      btn.classList.add('active')
      ;(page.querySelector('#langue') as HTMLInputElement).value = lang
      setLang(lang)
      router.navigate('/register')
    })
  })

  const form = page.querySelector('#register-form') as HTMLFormElement
  const errorBox = page.querySelector('#error-box') as HTMLElement
  const submitBtn = page.querySelector('#submit-btn') as HTMLButtonElement

  form.addEventListener('submit', async (event) => {
    event.preventDefault()
    submitBtn.disabled = true
    submitBtn.textContent = t('auth.register.loading')
    errorBox.style.display = 'none'

    try {
      const lang = ((page.querySelector('#langue') as HTMLInputElement).value || 'en') as Lang
      const token = await api.register({
        nom_complet: (page.querySelector('#nom') as HTMLInputElement).value,
        email: (page.querySelector('#email') as HTMLInputElement).value,
        mot_de_passe: (page.querySelector('#password') as HTMLInputElement).value,
        niveau_actuel: 'beginner',
        langue_preferee: lang,
      })
      api.setToken(token.access_token)
      localStorage.setItem('token', token.access_token)
      const user = await api.getMe()
      localStorage.setItem('user', JSON.stringify(user))
      setLang(user.langue_preferee)
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
