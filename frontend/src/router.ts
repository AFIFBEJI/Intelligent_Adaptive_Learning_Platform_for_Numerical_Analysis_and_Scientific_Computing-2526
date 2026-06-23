// ============================================================
// Router - Custom SPA Router (Vanilla TypeScript)
// ============================================================

import { hasChosenLang } from './i18n'

type RouteHandler = () => HTMLElement

interface Route {
  path: string
  handler: RouteHandler
  requiresAuth: boolean
}

class Router {
  private routes: Route[] = []
  private appContainer: HTMLElement

  constructor(containerId: string) {
    const container = document.getElementById(containerId)
    if (!container) throw new Error(`Container #${containerId} not found`)
    this.appContainer = container

    window.addEventListener('popstate', () => this.resolve())
    document.addEventListener('click', (e) => {
      const target = e.target as HTMLElement
      const link = target.closest('[data-link]') as HTMLAnchorElement | null
      if (link) {
        e.preventDefault()
        this.navigate(link.getAttribute('href') || '/')
      }
    })
  }

  addRoute(path: string, handler: RouteHandler, requiresAuth = false): Router {
    this.routes.push({ path, handler, requiresAuth })
    return this
  }

  navigate(path: string): void {
    window.history.pushState(null, '', path)
    this.resolve()
  }

  resolve(): void {
    const path = window.location.pathname

    // Match : exact d'abord, puis prefix-match pour supporter les
    // chemins avec parametre type /verify-email/<token>. Une route
    // dont le path se termine par '/*' matche tous les sous-paths.
    // Sinon, on fait aussi un match "prefix" pour les routes sans '/*'
    // mais qui veulent quand meme accepter /<route>/n-importe-quoi
    // (Phase 3 : verify-email, reset-password). Pour eviter d'autres
    // routes de matcher trop largement, on ne fait ce match qu'apres
    // avoir essaye le match exact.
    let route = this.routes.find(r => r.path === path)
    if (!route) {
      route = this.routes.find(r => {
        // Routes wildcard explicites : '/foo/*' -> matche /foo/anything
        if (r.path.endsWith('/*')) {
          const base = r.path.slice(0, -2)
          return path === base || path.startsWith(base + '/')
        }
        // Match prefix pour les routes auth-token (verify-email, reset-password)
        return (
          (r.path === '/verify-email' || r.path === '/reset-password') &&
          path.startsWith(r.path + '/')
        )
      })
    }
    if (!route) {
      route = this.routes.find(r => r.path === '/404')
    }

    if (!route) return

    const token = localStorage.getItem('token')
    if (route.requiresAuth && !token) {
      this.navigate('/login')
      return
    }

    // Garde-fou : aucune route protégée n'est accessible sans avoir
    // explicitement choisi une langue. Si la session a perdu la langue,
    // on renvoie vers /login pour forcer un nouveau choix.
    if (route.requiresAuth && !hasChosenLang()) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.navigate('/login')
      return
    }

    if ((path === '/login' || path === '/register') && token && hasChosenLang()) {
      this.navigate('/dashboard')
      return
    }

    this.appContainer.innerHTML = ''
    this.appContainer.appendChild(route.handler())
  }

  start(): void {
    this.resolve()
  }
}

export const router = new Router('app')
