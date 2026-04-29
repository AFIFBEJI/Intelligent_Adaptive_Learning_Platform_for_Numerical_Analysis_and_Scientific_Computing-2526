import { createAppShell } from '../components/app-shell'
import { t } from '../i18n'

function feature(title: string, body: string, mark: string): string {
  return `
    <article class="home-feature">
      <div class="home-feature-mark">${mark}</div>
      <h3>${title}</h3>
      <p>${body}</p>
    </article>
  `
}

export function HomePage(): HTMLElement {
  const shell = createAppShell({ activeRoute: '/', layout: 'public' })
  const page = document.createElement('main')
  page.className = 'home-page'
  page.innerHTML = `
    <style>
      .home-page {
        min-height: calc(100vh - var(--topbar-height));
        display: grid;
        grid-template-columns: minmax(0, 1.05fr) minmax(320px, 0.95fr);
        align-items: center;
        gap: var(--space-10);
        padding: var(--space-10) 0 var(--space-8);
      }
      .home-copy { display: flex; flex-direction: column; gap: var(--space-5); }
      .home-title {
        margin: 0;
        max-width: 760px;
        color: var(--text-primary);
        font-size: var(--text-5xl);
        line-height: 1.05;
        letter-spacing: 0;
      }
      .home-subtitle {
        margin: 0;
        max-width: 640px;
        color: var(--text-muted);
        font-size: var(--text-lg);
        line-height: var(--line-height-relaxed);
      }
      .home-actions { display: flex; flex-wrap: wrap; gap: var(--space-3); }
      .home-visual {
        border: 1px solid var(--border-default);
        border-radius: var(--radius-md);
        background: var(--bg-surface);
        box-shadow: var(--shadow-md);
        padding: var(--space-5);
      }
      .home-map {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: var(--space-3);
      }
      .home-node {
        min-height: 88px;
        padding: var(--space-4);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        background: var(--bg-surface-2);
      }
      .home-node strong { display: block; color: var(--text-primary); margin-bottom: var(--space-2); }
      .home-node span { color: var(--text-muted); font-size: var(--text-xs); line-height: 1.5; }
      .home-node.primary {
        grid-column: span 2;
        background: rgba(20,184,166,0.1);
        border-color: var(--info-border);
      }
      .home-features {
        grid-column: 1 / -1;
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: var(--space-4);
      }
      .home-feature {
        padding: var(--space-5);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-md);
        background: var(--bg-surface);
        box-shadow: var(--shadow-sm);
      }
      .home-feature-mark {
        width: 34px;
        height: 34px;
        display: grid;
        place-items: center;
        margin-bottom: var(--space-4);
        color: #06111f;
        background: var(--brand-100);
        border-radius: var(--radius-md);
        font-weight: var(--font-weight-extrabold);
      }
      .home-feature h3 { margin: 0 0 var(--space-2); font-size: var(--text-lg); }
      .home-feature p { margin: 0; color: var(--text-muted); line-height: var(--line-height-relaxed); }
      @media (max-width: 900px) {
        .home-page { grid-template-columns: 1fr; padding-top: var(--space-8); }
        .home-features { grid-template-columns: 1fr; }
      }
      @media (max-width: 560px) {
        .home-title { font-size: var(--text-4xl); }
        .home-map { grid-template-columns: 1fr; }
        .home-node.primary { grid-column: span 1; }
        .home-actions .ds-btn { width: 100%; }
      }
    </style>

    <section class="home-copy">
      <p class="ds-eyebrow">${t('home.badge')}</p>
      <h1 class="home-title">${t('home.title')}</h1>
      <p class="home-subtitle">${t('home.subtitle')}</p>
      <div class="home-actions">
        <a href="/register" data-link class="ds-btn ds-btn-primary">${t('home.cta.register')}</a>
        <a href="/login" data-link class="ds-btn ds-btn-secondary">${t('home.cta.login')}</a>
      </div>
    </section>

    <aside class="home-visual" aria-label="Learning system preview">
      <div class="home-map">
        <div class="home-node primary"><strong>${t('home.visual.diagnostic')}</strong><span>${t('home.visual.diagnostic.desc')}</span></div>
        <div class="home-node"><strong>${t('home.visual.graph')}</strong><span>${t('home.visual.graph.desc')}</span></div>
        <div class="home-node"><strong>${t('home.visual.content')}</strong><span>${t('home.visual.content.desc')}</span></div>
        <div class="home-node"><strong>${t('home.visual.quiz')}</strong><span>${t('home.visual.quiz.desc')}</span></div>
        <div class="home-node"><strong>${t('home.visual.tutor')}</strong><span>${t('home.visual.tutor.desc')}</span></div>
      </div>
    </aside>

    <section class="home-features">
      ${feature(t('home.feature.graph'), t('home.feature.graph.desc'), 'G')}
      ${feature(t('home.feature.quiz'), t('home.feature.quiz.desc'), 'Q')}
      ${feature(t('home.feature.tutor'), t('home.feature.tutor.desc'), 'T')}
    </section>
  `
  shell.setContent(page)
  return shell.element
}
