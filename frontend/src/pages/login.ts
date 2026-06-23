import { api } from '../api'
import { createAppShell } from '../components/app-shell'
import { hasChosenLang, initLangFromUser, setLang, t, type Lang } from '../i18n'
import { router } from '../router'

export function LoginPage(): HTMLElement {
  const shell = createAppShell({ activeRoute: '/login', layout: 'focus' })
  const page = document.createElement('main')
  page.className = 'auth-page'

  // Sélection initiale = celle déjà choisie (si elle existe), sinon AUCUNE.
  // Le bouton "Se connecter" reste désactivé tant que rien n'est choisi.
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
        width: min(100%, 460px);
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

      /* ============================================================
         Carte d'erreur de login - design pro avec icone, titre,
         sous-message rassurant et 2 CTA d'aide.
         ============================================================ */
      .login-error-card {
        display: none;
        margin: 0 0 var(--space-4);
        padding: var(--space-4) var(--space-5);
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-left: 4px solid #dc2626;
        border-radius: var(--radius-md);
        animation: errorSlideIn 0.25s ease-out;
      }
      .login-error-card.visible { display: block; }
      @keyframes errorSlideIn {
        from { opacity: 0; transform: translateY(-6px); }
        to   { opacity: 1; transform: translateY(0); }
      }
      .login-error-head {
        display: flex; align-items: flex-start; gap: 12px;
        margin-bottom: var(--space-3);
      }
      .login-error-icon {
        flex-shrink: 0;
        width: 32px; height: 32px;
        border-radius: 50%;
        background: #dc2626;
        color: #ffffff;
        display: grid; place-items: center;
        font-weight: 800; font-size: 16px;
      }
      .login-error-text {
        flex: 1;
      }
      .login-error-title {
        margin: 0 0 4px;
        font-size: 0.95rem; font-weight: 800;
        color: #991b1b;
      }
      .login-error-body {
        margin: 0;
        font-size: 0.85rem; line-height: 1.5;
        color: #7f1d1d;
      }
      .login-error-tips {
        display: flex; flex-direction: column; gap: 6px;
        margin-top: var(--space-3);
        padding-top: var(--space-3);
        border-top: 1px dashed #fecaca;
      }
      .login-error-tip {
        font-size: 0.85rem; color: #7f1d1d;
        display: flex; align-items: center; gap: 6px;
        flex-wrap: wrap;
      }
      .login-error-tip a {
        color: var(--brand-600); font-weight: 700; text-decoration: none;
      }
      .login-error-tip a:hover { text-decoration: underline; }
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
      <!-- Erreur unique : un simple message + icone, pas de gros CTA -->
      <div class="ds-alert ds-alert-error" id="error-box" style="display:none;"></div>

      <form class="auth-form" id="login-form" novalidate>
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
          <span class="ds-label">${t('auth.email')}</span>
          <input class="ds-input" id="email" type="email" autocomplete="email" required />
        </label>
        <label>
          <span class="ds-label">${t('auth.password')}</span>
          <input class="ds-input" id="password" type="password" autocomplete="current-password" required />
        </label>
        <button class="ds-btn ds-btn-primary" id="submit-btn" type="submit" ${initialLang ? '' : 'disabled'}>${t('auth.login.submit')}</button>
      </form>
      <div class="auth-foot">
        <a href="/forgot-password" data-link class="ds-link">${t('auth.forgotLink')}</a>
        <span style="margin: 0 var(--space-2); color: var(--text-muted);">·</span>
        ${t('auth.needAccount')} <a href="/register" data-link class="ds-link">${t('auth.goRegister')}</a>
      </div>
    </section>
  `
  shell.setContent(page)

  const langInput = page.querySelector('#langue') as HTMLInputElement
  const submitBtn = page.querySelector('#submit-btn') as HTMLButtonElement
  const errorBox = page.querySelector('#error-box') as HTMLElement
  const form = page.querySelector('#login-form') as HTMLFormElement

  // Choix de langue : applique immédiatement la langue (l'UI se met à jour
  // au prochain rendu). Active le bouton de soumission.
  page.querySelectorAll<HTMLButtonElement>('.language-option').forEach((btn) => {
    btn.addEventListener('click', () => {
      const lang = (btn.dataset.lang as Lang) || 'en'
      page.querySelectorAll('.language-option').forEach((item) => item.classList.remove('active'))
      btn.classList.add('active')
      langInput.value = lang
      submitBtn.disabled = false
      setLang(lang)
      // Re-rendu pour appliquer la langue à toute la page de login.
      router.navigate('/login')
    })
  })

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
    submitBtn.textContent = t('auth.login.loading')

    try {
      const token = await api.login({
        email: (page.querySelector('#email') as HTMLInputElement).value,
        mot_de_passe: (page.querySelector('#password') as HTMLInputElement).value,
      })
      api.setToken(token.access_token)
      localStorage.setItem('token', token.access_token)
      // On force la langue choisie au login (override la langue stockée côté DB).
      try {
        await api.updateMyLanguage(chosenLang)
      } catch {
        // Si la persistance échoue, on garde la langue locale.
        setLang(chosenLang)
      }
      const user = await api.getMe()
      localStorage.setItem('user', JSON.stringify(user))
      setLang(chosenLang)
      initLangFromUser()
      router.navigate('/dashboard')
    } catch (err) {
      // Message d'erreur simple : email ou mot de passe incorrect.
      // Anti user-enumeration : on ne distingue pas "email inconnu" vs
      // "mot de passe faux" pour eviter qu'un attaquant puisse savoir
      // quels emails ont un compte sur la plateforme.
      void err
      errorBox.textContent = t('auth.error.login')
      errorBox.style.display = 'block'
      submitBtn.disabled = false
      submitBtn.textContent = t('auth.login.submit')
    }
  })

  return shell.element
}
