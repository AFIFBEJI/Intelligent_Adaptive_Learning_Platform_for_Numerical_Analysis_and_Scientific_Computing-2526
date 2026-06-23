// ============================================================
// Page : /verify-email/<token>
// ============================================================
// Cible des liens envoyes par email. Au montage :
//   1. Recupere le token depuis l'URL (path ou ?token=)
//   2. Appelle GET /auth/verify-email/{token}
//   3. Affiche succes ou erreur
//
// Pas de formulaire : c'est une simple landing qui valide le clic.
// ============================================================
import { api } from '../api'
import { createAppShell } from '../components/app-shell'
import { t } from '../i18n'

export function VerifyEmailPage(): HTMLElement {
  const shell = createAppShell({ activeRoute: '/verify-email', layout: 'focus' })
  const page = document.createElement('main')
  page.className = 'auth-page'

  // Token : soit dans le path /verify-email/<token>, soit dans ?token=
  const params = new URLSearchParams(window.location.search)
  let token = params.get('token') || ''
  if (!token) {
    const pathMatch = window.location.pathname.match(/\/verify-email\/(.+)$/)
    if (pathMatch) token = decodeURIComponent(pathMatch[1])
  }

  page.innerHTML = `
    <section class="auth-card">
      <a href="/" data-link class="auth-brand">
        <span class="auth-logo">AL</span>
        <span>${t('sidebar.brand.name')}</span>
      </a>
      <div class="auth-head">
        <h1 class="auth-title">${t('auth.verify.title')}</h1>
      </div>

      <div class="ds-alert ds-alert-info" id="status-box">
        ${t('auth.verify.checking')}
      </div>

      <div class="auth-foot" id="actions" style="display:none;">
        <a href="/login" data-link class="ds-btn ds-btn-primary">
          ${t('auth.verify.goLogin')}
        </a>
      </div>
    </section>
  `

  shell.setContent(page)

  const statusBox = page.querySelector('#status-box') as HTMLElement
  const actions = page.querySelector('#actions') as HTMLElement

  if (!token) {
    statusBox.className = 'ds-alert ds-alert-error'
    statusBox.textContent = t('auth.verify.error')
    actions.style.display = 'block'
    return shell.element
  }

  // Lance la verification au montage de la page.
  void (async () => {
    try {
      await api.verifyEmail(token)
      statusBox.className = 'ds-alert ds-alert-success'
      statusBox.textContent = t('auth.verify.success')
    } catch (err: any) {
      statusBox.className = 'ds-alert ds-alert-error'
      statusBox.textContent = err?.message || t('auth.verify.error')
    } finally {
      actions.style.display = 'block'
    }
  })()

  return shell.element
}
