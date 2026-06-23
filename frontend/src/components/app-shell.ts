// ============================================================
// AppShell - global layout with persistent navigation
// ============================================================

import { router } from '../router'
import { api } from '../api'
import { clearLang, getLang, languageName, setLang, t, tLevel, type Lang } from '../i18n'

export interface AppShellOptions {
  activeRoute: string
  pageTitle?: string
  pageSubtitle?: string
  /** app = sidebar/topbar, public = public topbar, focus = no chrome */
  layout?: 'app' | 'public' | 'focus'
  /** True = full-width content without topbar padding, used by /tutor. */
  fullBleed?: boolean
}

export interface AppShellHandle {
  element: HTMLElement
  setContent(content: HTMLElement): void
}

type IconName =
  | 'dashboard'
  | 'path'
  | 'concepts'
  | 'content'
  | 'quiz'
  | 'tutor'
  | 'logout'
  | 'menu'
  | 'spark'
  | 'login'

interface NavItem {
  label: string
  icon: IconName
  path: string
  group: string
}

interface UserInfo {
  nom_complet: string
  email: string
  niveau_actuel: string
  langue_preferee?: 'fr' | 'en'
}

const ICONS: Record<IconName, string> = {
  dashboard: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="8" rx="2"/><rect x="14" y="3" width="7" height="5" rx="2"/><rect x="14" y="12" width="7" height="9" rx="2"/><rect x="3" y="15" width="7" height="6" rx="2"/></svg>',
  path: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="6" cy="6" r="2"/><circle cx="18" cy="18" r="2"/><path d="M8 6h5a4 4 0 0 1 0 8h-2a4 4 0 0 0 0 8h5"/></svg>',
  concepts: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3v3"/><path d="M12 18v3"/><path d="M4.2 7.5l2.6 1.5"/><path d="M17.2 15l2.6 1.5"/><path d="M19.8 7.5 17.2 9"/><path d="M6.8 15l-2.6 1.5"/><circle cx="12" cy="12" r="4"/></svg>',
  content: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 4h10a4 4 0 0 1 4 4v12H8a3 3 0 0 1-3-3z"/><path d="M8 4v13a3 3 0 0 0 3 3"/><path d="M9 8h6"/><path d="M9 12h5"/></svg>',
  quiz: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l2 2 4-5"/><path d="M20 6v14H4V4h10"/><path d="M14 4v4h4"/></svg>',
  tutor: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z"/><path d="M8 9h8"/><path d="M8 13h5"/></svg>',
  logout: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 17l-5-5 5-5"/><path d="M5 12h12"/><path d="M14 4h5v16h-5"/></svg>',
  menu: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 6h16"/><path d="M4 12h16"/><path d="M4 18h16"/></svg>',
  spark: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l1.6 5.2L19 10l-5.4 1.8L12 17l-1.6-5.2L5 10l5.4-1.8z"/><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z"/></svg>',
  login: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><path d="M10 17l5-5-5-5"/><path d="M15 12H3"/></svg>',
}

function escapeHtml(s: string): string {
  return (s || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function iconSvg(name: IconName, className: string): string {
  return `<span class="${className}" aria-hidden="true">${ICONS[name]}</span>`
}

function getUser(): UserInfo | null {
  try {
    const raw = localStorage.getItem('user')
    return raw ? (JSON.parse(raw) as UserInfo) : null
  } catch {
    return null
  }
}

function getNavItems(): NavItem[] {
  return [
    { label: t('sidebar.dashboard'), icon: 'dashboard', path: '/dashboard', group: t('sidebar.group.parcours') },
    { label: t('sidebar.path'), icon: 'path', path: '/path', group: t('sidebar.group.parcours') },
    { label: t('sidebar.concepts'), icon: 'concepts', path: '/concepts', group: t('sidebar.group.apprendre') },
    { label: t('sidebar.content'), icon: 'content', path: '/content', group: t('sidebar.group.apprendre') },
    { label: t('sidebar.quiz'), icon: 'quiz', path: '/quiz-ai', group: t('sidebar.group.pratiquer') },
    { label: t('sidebar.tutor'), icon: 'tutor', path: '/tutor', group: t('sidebar.group.aide') },
  ]
}

function getLevelToken(level: string): string {
  const normalized = level.toLowerCase()
  if (normalized.startsWith('av') || normalized.includes('advanced')) return 'ADV'
  if (normalized.startsWith('inter') || normalized.includes('intermediate')) return 'INT'
  return 'NEW'
}

function currentRouteWithQuery(): string {
  return `${window.location.pathname || '/'}${window.location.search || ''}${window.location.hash || ''}`
}

function languageButton(lang: Lang, activeLang: Lang): string {
  const label = languageName(lang)
  const isActive = activeLang === lang
  return `
    <button
      class="ds-lang-btn ${isActive ? 'active' : ''}"
      data-lang="${lang}"
      type="button"
      aria-pressed="${isActive}"
      aria-label="${escapeHtml(`${t('language.label')}: ${label}`)}"
      title="${escapeHtml(t('language.switchHelp'))}"
    >
      <span class="ds-lang-code">${lang.toUpperCase()}</span>
      <small>${escapeHtml(label)}</small>
    </button>
  `
}

function bindLanguageSwitcher(root: HTMLElement, selector = '[data-lang]'): void {
  root.querySelectorAll<HTMLButtonElement>(selector).forEach((button) => {
    button.addEventListener('click', async () => {
      const newLang = (button.dataset.lang as Lang) || 'en'
      if (newLang === getLang()) return

      root.querySelectorAll<HTMLButtonElement>(selector).forEach((btn) => {
        btn.disabled = true
      })

      setLang(newLang)
      try {
        if (localStorage.getItem('token')) {
          await api.updateMyLanguage(newLang)
        }
      } catch {
        // The local language still changes immediately; persistence can retry later.
      } finally {
        router.navigate(currentRouteWithQuery())
      }
    })
  })
}

function buildSidebar(activeRoute: string): HTMLElement {
  const user = getUser()
  const sidebar = document.createElement('aside')
  sidebar.className = 'ds-sidebar'

  const groups: Record<string, NavItem[]> = {}
  for (const item of getNavItems()) {
    groups[item.group] = groups[item.group] || []
    groups[item.group].push(item)
  }

  let navHtml = ''
  for (const [groupName, items] of Object.entries(groups)) {
    navHtml += `<div class="ds-nav-group-label">${escapeHtml(groupName)}</div>`
    for (const item of items) {
      const isActive = item.path === activeRoute || (activeRoute === '/quiz' && item.path === '/quiz-ai')
      navHtml += `
        <a href="${item.path}" data-link class="ds-nav-item${isActive ? ' active' : ''}">
          ${iconSvg(item.icon, 'ds-nav-icon')}
          <span class="ds-nav-label">${escapeHtml(item.label)}</span>
        </a>`
    }
  }

  const level = user?.niveau_actuel || 'Beginner'
  const lang = getLang()

  sidebar.innerHTML = `
    <div class="ds-sidebar-brand">
      <a href="/dashboard" data-link class="ds-brand-logo" aria-label="${escapeHtml(t('sidebar.brand.name'))}">AL</a>
      <div class="ds-brand-text">
        <div class="ds-brand-name">${escapeHtml(t('sidebar.brand.name'))}</div>
        <div class="ds-brand-sub">${escapeHtml(t('sidebar.brand.sub'))}</div>
      </div>
    </div>

    <nav class="ds-sidebar-nav" aria-label="Main navigation">
      ${navHtml}
    </nav>

    <div class="ds-sidebar-footer">
      ${user ? `
        <div class="ds-user-card">
          <div class="ds-user-avatar">${escapeHtml((user.nom_complet || '?').charAt(0).toUpperCase())}</div>
          <div class="ds-user-meta">
            <div class="ds-user-name">${escapeHtml(user.nom_complet || t('sidebar.student'))}</div>
            <div class="ds-user-level">
              <span class="ds-user-level-token">${escapeHtml(getLevelToken(level))}</span>
              <span>${escapeHtml(tLevel(level))}</span>
            </div>
          </div>
        </div>
        <div class="ds-lang-block">
          <div class="ds-lang-label">${escapeHtml(t('language.label'))}</div>
          <div class="ds-lang-toggle" role="radiogroup" aria-label="${escapeHtml(t('language.label'))}">
            ${languageButton('en', lang)}
            ${languageButton('fr', lang)}
          </div>
        </div>
        <button class="ds-logout-btn" id="ds-logout" type="button">
          ${iconSvg('logout', 'ds-footer-icon')}
          <span>${escapeHtml(t('sidebar.logout'))}</span>
        </button>
      ` : `
        <a href="/login" data-link class="ds-btn ds-btn-secondary ds-login-link">
          ${iconSvg('login', 'ds-footer-icon')}
          <span>${escapeHtml(t('sidebar.login'))}</span>
        </a>
      `}
    </div>
  `

  sidebar.querySelector('#ds-logout')?.addEventListener('click', () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    // On nettoie aussi la langue : à la prochaine connexion l'utilisateur
    // devra de nouveau choisir explicitement (FR ou EN).
    clearLang()
    api.clearToken()
    // Hard navigation to '/' so any in-memory page state (router, caches,
    // in-flight requests) is fully discarded and the user lands cleanly on
    // the public home page.
    window.location.href = '/'
  })

  bindLanguageSwitcher(sidebar)

  return sidebar
}

function buildTopbar(opts: AppShellOptions, shell: HTMLElement): HTMLElement {
  const layout = opts.layout || 'app'
  const topbar = document.createElement('header')
  topbar.className = 'ds-topbar'

  if (layout === 'public') {
    const lang = getLang()
    topbar.innerHTML = `
      <div class="ds-topbar-content">
        <a href="/" data-link class="ds-public-brand">
          <span class="ds-public-logo">AL</span>
          <span>${escapeHtml(t('sidebar.brand.name'))}</span>
        </a>
        <div class="ds-public-actions">
          <div class="ds-lang-toggle ds-lang-toggle--public" role="radiogroup" aria-label="Language">
            ${languageButton('en', lang)}
            ${languageButton('fr', lang)}
          </div>
          <nav class="ds-public-nav" aria-label="Public navigation">
            <a href="/login" data-link class="ds-btn ds-btn-ghost">${escapeHtml(t('home.cta.login'))}</a>
            <a href="/register" data-link class="ds-btn ds-btn-primary">${escapeHtml(t('home.cta.register'))}</a>
          </nav>
        </div>
      </div>
    `
    bindLanguageSwitcher(topbar)
    return topbar
  }

  topbar.innerHTML = `
    <div class="ds-topbar-content">
      <div class="ds-topbar-left">
        ${layout === 'app' ? `<button class="ds-topbar-menu" type="button" aria-label="Open navigation" aria-expanded="false">${iconSvg('menu', 'ds-menu-icon')}</button>` : ''}
        <div class="ds-topbar-titles">
          ${opts.pageTitle ? `<p class="ds-topbar-kicker">${escapeHtml(t('sidebar.brand.sub'))}</p>` : ''}
          ${opts.pageTitle ? `<h1 class="ds-topbar-title">${escapeHtml(opts.pageTitle)}</h1>` : ''}
          ${opts.pageSubtitle ? `<p class="ds-topbar-subtitle">${escapeHtml(opts.pageSubtitle)}</p>` : ''}
        </div>
      </div>
      <div class="ds-topbar-right">
        <span class="ds-topbar-pill">${iconSvg('spark', 'ds-pill-icon')} ${escapeHtml(t('topbar.adaptive'))}</span>
      </div>
    </div>
  `

  // Le selecteur de langue de la sidebar (footer) est l'unique source de
  // verite quand l'utilisateur est connecte ; on n'en duplique pas dans le topbar.

  topbar.querySelector('.ds-topbar-menu')?.addEventListener('click', () => {
    const open = !shell.classList.contains('sidebar-open')
    shell.classList.toggle('sidebar-open', open)
    ;(topbar.querySelector('.ds-topbar-menu') as HTMLButtonElement | null)?.setAttribute('aria-expanded', String(open))
  })

  return topbar
}

function injectShellStyles(): void {
  if (document.querySelector('style[data-ds-shell]')) return
  const style = document.createElement('style')
  style.dataset.dsShell = 'true'
  style.textContent = `
    .ds-shell { min-height: 100vh; background: transparent; }
    .ds-shell--app { display: grid; grid-template-columns: var(--sidebar-width) minmax(0, 1fr); }
    .ds-shell--public, .ds-shell--focus { display: flex; flex-direction: column; }

    .ds-sidebar {
      position: sticky;
      top: 0;
      height: 100vh;
      display: flex;
      flex-direction: column;
      gap: var(--space-5);
      padding: var(--space-5) var(--space-3);
      color: var(--text-on-inverse);
      background:
        linear-gradient(rgba(248, 251, 255, 0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(248, 251, 255, 0.035) 1px, transparent 1px),
        linear-gradient(180deg, var(--bg-inverse-soft) 0%, var(--bg-inverse) 100%);
      background-size: 26px 26px, 26px 26px, auto;
      border-right: 1px solid rgba(248, 251, 255, 0.12);
      box-shadow: 18px 0 48px rgba(15, 35, 51, 0.16);
      z-index: 210;
    }

    .ds-sidebar-brand {
      display: flex;
      align-items: center;
      gap: var(--space-3);
      padding: var(--space-2) var(--space-3) var(--space-4);
      border-bottom: 1px solid rgba(248, 251, 255, 0.12);
    }
    .ds-brand-logo,
    .ds-public-logo {
      width: 40px;
      height: 40px;
      display: grid;
      place-items: center;
      flex: 0 0 auto;
      border-radius: var(--radius-md);
      color: var(--text-on-inverse);
      background: var(--brand-gradient);
      font-size: var(--text-xs);
      font-weight: var(--font-weight-extrabold);
      letter-spacing: 0.04em;
      text-decoration: none;
      box-shadow: 0 14px 34px rgba(15, 35, 51, 0.22);
    }
    .ds-brand-text { min-width: 0; }
    .ds-brand-name {
      color: var(--text-on-inverse);
      font-size: var(--text-md);
      font-weight: var(--font-weight-extrabold);
      line-height: 1.2;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .ds-brand-sub { color: var(--text-muted-inverse); font-size: var(--text-xs); margin-top: 2px; }

    .ds-sidebar-nav {
      display: flex;
      flex-direction: column;
      gap: var(--space-1);
      flex: 1;
      overflow-y: auto;
      padding-right: var(--space-1);
    }
    .ds-nav-group-label {
      padding: var(--space-4) var(--space-3) var(--space-1);
      color: rgba(248, 251, 255, 0.5);
      font-size: 0.68rem;
      font-weight: var(--font-weight-bold);
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }
    .ds-nav-item {
      position: relative;
      display: flex;
      align-items: center;
      gap: var(--space-3);
      min-height: 42px;
      padding: 0.62rem var(--space-3);
      color: rgba(248, 251, 255, 0.78);
      text-decoration: none;
      border-radius: var(--radius-md);
      font-size: var(--text-sm);
      font-weight: var(--font-weight-semibold);
      transition: color var(--transition-fast), background var(--transition-fast), transform var(--transition-fast);
    }
    .ds-nav-item:hover {
      color: var(--text-on-inverse);
      background: rgba(248, 251, 255, 0.08);
      transform: translateX(2px);
    }
    .ds-nav-item.active {
      color: var(--text-on-inverse);
      background: rgba(248, 251, 255, 0.13);
      box-shadow: inset 0 0 0 1px rgba(204, 251, 239, 0.22);
    }
    .ds-nav-item.active::before {
      content: "";
      position: absolute;
      left: -0.45rem;
      top: 10px;
      bottom: 10px;
      width: 3px;
      border-radius: var(--radius-full);
      background: var(--accent-amber);
    }
    .ds-nav-icon,
    .ds-footer-icon,
    .ds-menu-icon,
    .ds-pill-icon {
      display: inline-grid;
      place-items: center;
      flex: 0 0 auto;
    }
    .ds-nav-icon { width: 20px; height: 20px; color: currentColor; opacity: 0.92; }
    .ds-footer-icon { width: 18px; height: 18px; }
    .ds-menu-icon { width: 20px; height: 20px; }
    .ds-pill-icon { width: 14px; height: 14px; }
    .ds-nav-icon svg,
    .ds-footer-icon svg,
    .ds-menu-icon svg,
    .ds-pill-icon svg { width: 100%; height: 100%; }
    .ds-nav-label { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

    .ds-sidebar-footer {
      display: flex;
      flex-direction: column;
      gap: var(--space-3);
      padding-top: var(--space-4);
      border-top: 1px solid rgba(248, 251, 255, 0.12);
    }
    .ds-user-card {
      display: flex;
      align-items: center;
      gap: var(--space-3);
      padding: var(--space-3);
      border-radius: var(--radius-md);
      background: rgba(248, 251, 255, 0.08);
      border: 1px solid rgba(248, 251, 255, 0.12);
    }
    .ds-user-avatar {
      width: 38px;
      height: 38px;
      display: grid;
      place-items: center;
      flex: 0 0 auto;
      color: var(--text-on-inverse);
      background: var(--brand-gradient);
      border-radius: var(--radius-md);
      font-weight: var(--font-weight-extrabold);
    }
    .ds-user-meta { min-width: 0; flex: 1; }
    .ds-user-name {
      color: var(--text-on-inverse);
      font-size: var(--text-sm);
      font-weight: var(--font-weight-bold);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .ds-user-level {
      display: flex;
      align-items: center;
      gap: var(--space-2);
      margin-top: 2px;
      color: var(--text-muted-inverse);
      font-size: var(--text-xs);
    }
    .ds-user-level-token {
      color: var(--bg-inverse);
      background: rgba(248, 251, 255, 0.86);
      border-radius: var(--radius-sm);
      padding: 0.08rem 0.32rem;
      font-weight: var(--font-weight-extrabold);
      line-height: 1.25;
    }

    .ds-lang-block {
      display: flex;
      flex-direction: column;
      gap: var(--space-2);
    }
    .ds-lang-label {
      color: rgba(248, 251, 255, 0.52);
      font-size: 0.68rem;
      font-weight: var(--font-weight-bold);
      letter-spacing: 0.08em;
      text-transform: uppercase;
      padding: 0 var(--space-1);
    }
    .ds-lang-toggle {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 2px;
      padding: 3px;
      border: 1px solid rgba(248, 251, 255, 0.12);
      border-radius: var(--radius-md);
      background: rgba(248, 251, 255, 0.08);
    }
    .ds-lang-btn {
      min-height: 42px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 1px;
      border: 0;
      border-radius: var(--radius-sm);
      color: rgba(248, 251, 255, 0.7);
      background: transparent;
      font-size: var(--text-xs);
      font-weight: var(--font-weight-extrabold);
      letter-spacing: 0.05em;
      cursor: pointer;
      transition: color var(--transition-fast), background var(--transition-fast);
    }
    .ds-lang-btn small {
      max-width: 100%;
      color: currentColor;
      font-size: 0.62rem;
      font-weight: var(--font-weight-semibold);
      letter-spacing: 0;
      opacity: 0.75;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .ds-lang-btn:hover { color: var(--text-on-inverse); }
    .ds-lang-btn:disabled { cursor: wait; opacity: 0.72; }
    .ds-lang-btn.active {
      color: var(--text-on-inverse);
      background: var(--brand-gradient);
      box-shadow: var(--shadow-xs);
    }
    .ds-logout-btn,
    .ds-login-link {
      width: 100%;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: var(--space-2);
      min-height: 40px;
      padding: 0.65rem var(--space-3);
      color: rgba(248, 251, 255, 0.76);
      background: transparent;
      border: 1px solid rgba(248, 251, 255, 0.14);
      border-radius: var(--radius-md);
      font-size: var(--text-sm);
      font-weight: var(--font-weight-bold);
      text-decoration: none;
      cursor: pointer;
      transition: color var(--transition-fast), border-color var(--transition-fast), background var(--transition-fast);
    }
    .ds-logout-btn:hover,
    .ds-login-link:hover {
      color: var(--text-on-inverse);
      border-color: rgba(244, 63, 94, 0.34);
      background: rgba(180, 35, 58, 0.18);
    }

    .ds-main {
      min-width: 0;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }
    .ds-topbar {
      position: sticky;
      top: 0;
      z-index: 120;
      min-height: var(--topbar-height);
      display: flex;
      align-items: center;
      padding: var(--space-4) var(--content-padding-x);
      background: var(--bg-overlay);
      border-bottom: 1px solid var(--border-subtle);
      backdrop-filter: blur(18px);
    }
    .ds-topbar-content {
      width: 100%;
      max-width: var(--content-max-width);
      margin: 0 auto;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: var(--space-4);
    }
    .ds-topbar-left,
    .ds-topbar-right {
      display: flex;
      align-items: center;
      gap: var(--space-3);
      min-width: 0;
    }
    .ds-topbar-menu {
      display: none;
      width: 40px;
      height: 40px;
      align-items: center;
      justify-content: center;
      border: 1px solid var(--border-default);
      border-radius: var(--radius-md);
      color: var(--text-secondary);
      background: var(--bg-surface-2);
      cursor: pointer;
      box-shadow: var(--shadow-xs);
    }
    .ds-topbar-titles { min-width: 0; }
    .ds-topbar-kicker {
      margin: 0 0 2px;
      color: var(--brand-300);
      font-size: 0.68rem;
      font-weight: var(--font-weight-extrabold);
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }
    .ds-topbar-title {
      margin: 0;
      color: var(--text-primary);
      font-size: var(--text-2xl);
      font-weight: var(--font-weight-extrabold);
      line-height: 1.16;
      letter-spacing: 0;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .ds-topbar-subtitle {
      margin: var(--space-1) 0 0;
      max-width: 760px;
      color: var(--text-muted);
      font-size: var(--text-sm);
      line-height: 1.45;
    }
    .ds-topbar-pill {
      display: inline-flex;
      align-items: center;
      gap: var(--space-2);
      min-height: 34px;
      padding: 0.42rem 0.72rem;
      color: var(--brand-600);
      background: rgba(15, 118, 110, 0.1);
      border: 1px solid rgba(15, 118, 110, 0.22);
      border-radius: var(--radius-md);
      font-size: var(--text-xs);
      font-weight: var(--font-weight-extrabold);
    }

    .ds-public-brand {
      display: inline-flex;
      align-items: center;
      gap: var(--space-3);
      color: var(--text-primary);
      text-decoration: none;
      font-weight: var(--font-weight-extrabold);
    }
    .ds-public-logo { color: var(--text-on-inverse); }
    .ds-public-actions { display: flex; align-items: center; gap: var(--space-3); }
    .ds-public-nav { display: flex; gap: var(--space-2); }
    .ds-topbar-lang {
      display: flex;
      align-items: center;
      min-width: 178px;
    }
    .ds-lang-toggle--topbar {
      width: 100%;
      background: var(--bg-surface-2);
      border-color: var(--border-default);
      box-shadow: var(--shadow-xs);
    }
    .ds-lang-toggle--topbar .ds-lang-btn {
      color: var(--text-muted);
      min-height: 34px;
    }
    .ds-lang-toggle--topbar .ds-lang-btn:hover { color: var(--text-primary); }
    .ds-lang-toggle--topbar .ds-lang-btn.active {
      color: var(--text-on-inverse);
      background: var(--brand-gradient);
    }
    .ds-lang-toggle--public {
      min-width: 86px;
      background: var(--bg-surface-2);
      border-color: var(--border-default);
    }
    .ds-lang-toggle--public .ds-lang-btn { color: var(--text-muted); }
    .ds-lang-toggle--public .ds-lang-btn:hover { color: var(--text-primary); }
    .ds-lang-toggle--public .ds-lang-btn.active {
      color: var(--text-on-inverse);
      background: var(--brand-gradient);
    }

    .ds-content {
      flex: 1;
      min-width: 0;
      padding: var(--space-8) var(--content-padding-x);
    }
    .ds-content-inner {
      width: 100%;
      max-width: var(--content-max-width);
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: var(--space-8);
    }
    .ds-content--full {
      padding: 0;
      display: flex;
      flex-direction: column;
      min-height: 100vh;
    }
    .ds-content-inner--full {
      max-width: none;
      gap: 0;
      flex: 1;
      min-height: 0;
      width: 100%;
      display: block;
    }
    .ds-content-inner--full > * {
      width: 100%;
      height: 100%;
      min-height: 100vh;
    }

    .ds-mobile-overlay { display: none; }

    /* ============================================================
       Bouton "Back to home" pour le layout focus (pages d'auth).
       Position fixe en haut a gauche, toujours visible.
       Discret au repos, plus marque au hover.
       ============================================================ */
    .ds-back-home {
      position: fixed;
      top: 24px;
      left: 24px;
      z-index: 250;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 10px 16px 10px 12px;
      background: #ffffff;
      border: 1px solid var(--border-default);
      border-radius: 999px;
      color: var(--text-secondary);
      font-size: 0.88rem;
      font-weight: 600;
      text-decoration: none !important;
      box-shadow: 0 2px 8px rgba(15, 23, 42, 0.06);
      transition: all 0.2s ease;
    }
    .ds-back-home:hover {
      color: var(--brand-600);
      border-color: var(--brand-500);
      background: #ffffff;
      box-shadow:
        0 4px 14px rgba(15, 118, 110, 0.16),
        0 2px 6px rgba(15, 23, 42, 0.06);
      transform: translateX(-2px);
    }
    .ds-back-home:hover svg { transform: translateX(-2px); }
    .ds-back-home svg {
      width: 16px;
      height: 16px;
      flex-shrink: 0;
      transition: transform 0.2s ease;
    }
    @media (max-width: 640px) {
      .ds-back-home {
        top: 16px;
        left: 16px;
        padding: 8px 14px 8px 10px;
        font-size: 0.82rem;
      }
      .ds-back-home svg { width: 14px; height: 14px; }
    }

    @media (max-width: 980px) {
      .ds-shell--app { grid-template-columns: 1fr; }
      .ds-sidebar {
        position: fixed;
        left: 0;
        transform: translateX(-105%);
        width: min(88vw, var(--sidebar-width));
        transition: transform var(--transition-base);
      }
      .ds-shell--app.sidebar-open .ds-sidebar { transform: translateX(0); }
      .ds-shell--app.sidebar-open .ds-mobile-overlay {
        display: block;
        position: fixed;
        inset: 0;
        z-index: 190;
        background: rgba(15, 35, 51, 0.34);
        backdrop-filter: blur(4px);
      }
      .ds-topbar-menu { display: inline-flex; }
      .ds-content { padding: var(--space-6) var(--content-padding-x); }
    }

    @media (max-width: 640px) {
      .ds-topbar {
        align-items: flex-start;
        padding-top: var(--space-3);
        padding-bottom: var(--space-3);
      }
      .ds-topbar-content { align-items: flex-start; }
      .ds-topbar-title { font-size: var(--text-xl); white-space: normal; }
      .ds-topbar-subtitle { display: none; }
      .ds-topbar-right { display: none; }
      .ds-public-actions { gap: var(--space-2); }
      .ds-public-nav .ds-btn-ghost { display: none; }
      .ds-content { padding: var(--space-5) var(--content-padding-x); }
    }
  `
  document.head.appendChild(style)
}

export function createAppShell(opts: AppShellOptions): AppShellHandle {
  injectShellStyles()
  const layout = opts.layout || 'app'

  const shell = document.createElement('div')
  shell.className = `ds-shell ds-shell--${layout}${opts.fullBleed ? ' ds-shell--full' : ''}`

  const main = document.createElement('div')
  main.className = 'ds-main'

  const contentWrapper = document.createElement('div')
  contentWrapper.className = 'ds-content' + (opts.fullBleed ? ' ds-content--full' : '')
  const contentInner = document.createElement('div')
  contentInner.className = 'ds-content-inner' + (opts.fullBleed ? ' ds-content-inner--full' : '')
  contentWrapper.appendChild(contentInner)

  if (layout === 'app') {
    const sidebar = buildSidebar(opts.activeRoute)
    const overlay = document.createElement('div')
    overlay.className = 'ds-mobile-overlay'
    overlay.addEventListener('click', () => shell.classList.remove('sidebar-open'))

    if (!opts.fullBleed) {
      main.appendChild(buildTopbar(opts, shell))
    }
    main.appendChild(contentWrapper)
    shell.appendChild(sidebar)
    shell.appendChild(main)
    shell.appendChild(overlay)
  } else if (layout === 'public') {
    main.appendChild(buildTopbar(opts, shell))
    main.appendChild(contentWrapper)
    shell.appendChild(main)
  } else {
    // Layout 'focus' : pages d'auth (login, register, forgot, reset, verify).
    // Pas de sidebar ni topbar, mais on injecte un bouton "Back to home"
    // tres visible en haut a gauche pour que l'utilisateur sache toujours
    // comment revenir a la page d'accueil sans devoir deviner que le logo
    // est cliquable.
    const backHome = document.createElement('a')
    backHome.href = '/'
    backHome.setAttribute('data-link', '')
    backHome.className = 'ds-back-home'
    backHome.setAttribute('aria-label', t('auth.backToHome'))
    backHome.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <line x1="19" y1="12" x2="5" y2="12" />
        <polyline points="12 19 5 12 12 5" />
      </svg>
      <span>${escapeHtml(t('auth.backToHome'))}</span>
    `
    shell.appendChild(backHome)
    main.appendChild(contentWrapper)
    shell.appendChild(main)
  }

  return {
    element: shell,
    setContent(content: HTMLElement) {
      contentInner.innerHTML = ''
      contentInner.appendChild(content)
    },
  }
}
