import { api } from '../api'
import { createAppShell } from '../components/app-shell'
import { initLangFromUser, t } from '../i18n'
import { router } from '../router'

export function LoginPage(): HTMLElement {
  const shell = createAppShell({ activeRoute: '/login', layout: 'focus' })
  const page = document.createElement('main')
  page.className = 'auth-page'
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
        width: min(100%, 430px);
        padding: var(--space-8);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-md);
        background: var(--bg-surface);
        box-shadow: var(--shadow-lg);
      }
      .auth-head { margin-bottom: var(--space-6); }
      .auth-brand { display: inline-flex; align-items: center; gap: var(--space-3); margin-bottom: var(--space-6); text-decoration: none; }
      .auth-logo {
        width: 38px; height: 38px; display: grid; place-items: center;
        border-radius: var(--radius-md); color: #ffffff;
        background: var(--brand-gradient);
        font-weight: var(--font-weight-extrabold);
      }
      .auth-title { margin: 0 0 var(--space-2); font-size: var(--text-3xl); line-height: var(--line-height-tight); }
      .auth-sub { margin: 0; color: var(--text-muted); line-height: var(--line-height-relaxed); }
      .auth-form { display: flex; flex-direction: column; gap: var(--space-4); }
      .auth-foot { margin-top: var(--space-5); color: var(--text-muted); font-size: var(--text-sm); text-align: center; }
    </style>

    <section class="auth-card">
      <a href="/" data-link class="auth-brand">
        <span class="auth-logo">AL</span>
        <span>${t('sidebar.brand.name')}</span>
      </a>
      <div class="auth-head">
        <h1 class="auth-title">${t('auth.login.title')}</h1>
        <p class="auth-sub">${t('auth.login.subtitle')}</p>
      </div>
      <div class="ds-alert ds-alert-error" id="error-box" style="display:none;"></div>
      <form class="auth-form" id="login-form">
        <label>
          <span class="ds-label">${t('auth.email')}</span>
          <input class="ds-input" id="email" type="email" autocomplete="email" required />
        </label>
        <label>
          <span class="ds-label">${t('auth.password')}</span>
          <input class="ds-input" id="password" type="password" autocomplete="current-password" required />
        </label>
        <button class="ds-btn ds-btn-primary" id="submit-btn" type="submit">${t('auth.login.submit')}</button>
      </form>
      <div class="auth-foot">
        ${t('auth.needAccount')} <a href="/register" data-link class="ds-link">${t('auth.goRegister')}</a>
      </div>
    </section>
  `
  shell.setContent(page)

  const form = page.querySelector('#login-form') as HTMLFormElement
  const errorBox = page.querySelector('#error-box') as HTMLElement
  const submitBtn = page.querySelector('#submit-btn') as HTMLButtonElement

  form.addEventListener('submit', async (event) => {
    event.preventDefault()
    submitBtn.disabled = true
    submitBtn.textContent = t('auth.login.loading')
    errorBox.style.display = 'none'

    try {
      const token = await api.login({
        email: (page.querySelector('#email') as HTMLInputElement).value,
        mot_de_passe: (page.querySelector('#password') as HTMLInputElement).value,
      })
      api.setToken(token.access_token)
      localStorage.setItem('token', token.access_token)
      const user = await api.getMe()
      localStorage.setItem('user', JSON.stringify(user))
      initLangFromUser()
      router.navigate('/dashboard')
    } catch (err) {
      errorBox.textContent = err instanceof Error ? err.message : t('auth.error.login')
      errorBox.style.display = 'block'
      submitBtn.disabled = false
      submitBtn.textContent = t('auth.login.submit')
    }
  })

  return shell.element
}
