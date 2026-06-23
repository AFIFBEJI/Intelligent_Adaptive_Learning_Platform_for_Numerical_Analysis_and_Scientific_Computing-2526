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

    // Match: exact first, then prefix-match to support
    // paths with a parameter like /verify-email/<token>. A route
    // whose path ends with '/*' matches all sub-paths.
    // Otherwise, we also do a "prefix" match for routes without '/*'
    // but that still want to accept /<route>/anything
    // (Phase 3: verify-email, reset-password). To avoid other
    // routes matching too broadly, we only do this match after
    // having tried the exact match.
    let route = this.routes.find(r => r.path === path)
    if (!route) {
      route = this.routes.find(r => {
        // Explicit wildcard routes: '/foo/*' -> matches /foo/anything
        if (r.path.endsWith('/*')) {
          const base = r.path.slice(0, -2)
          return path === base || path.startsWith(base + '/')
        }
        // Prefix match for auth-token routes (verify-email, reset-password)
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

    // Safeguard: no protected route is accessible without having
    // explicitly chosen a language. If the session lost the language,
    // we send back to /login to force a new choice.
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

    // Remove any leftover full-screen modal that was portaled to <body>
    // on a previous page (e.g. the concept-video modal). Without this, it
    // lingers across navigations as an unstyled black box, because the
    // page <style> that hid it was removed when we cleared #app.
    document.querySelectorAll('body > .video-modal').forEach(m => m.remove())

    this.appContainer.innerHTML = ''
    this.appContainer.appendChild(route.handler())
  }

  start(): void {
    this.resolve()
  }
}

export const router = new Router('app')
