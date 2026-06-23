import { createAppShell } from '../components/app-shell'
import { t } from '../i18n'

// ============================================================
// Home page - public landing for numerical analysis learners
// ============================================================

interface FeatureSpec {
  mark: string
  title: string
  desc: string
  tone: 'terracotta' | 'ochre' | 'clay' | 'graphite' | 'brass' | 'ink'
}

interface ModuleSpec {
  code: string
  title: string
  desc: string
}

interface StepSpec {
  label: string
  title: string
  desc: string
}

const FEATURE_TONE_STYLES: Record<FeatureSpec['tone'], string> = {
  terracotta: 'color: #115e59; background: rgba(15, 118, 110, 0.11); border-color: rgba(15, 118, 110, 0.24);',
  ochre: 'color: #8a5a07; background: rgba(183, 121, 31, 0.12); border-color: rgba(183, 121, 31, 0.26);',
  clay: 'color: #a23b4f; background: rgba(190, 69, 101, 0.1); border-color: rgba(190, 69, 101, 0.22);',
  graphite: 'color: #3155a6; background: rgba(49, 85, 166, 0.1); border-color: rgba(49, 85, 166, 0.22);',
  brass: 'color: #0e7490; background: rgba(14, 116, 144, 0.1); border-color: rgba(14, 116, 144, 0.22);',
  ink: 'color: #142231; background: rgba(15, 35, 51, 0.08); border-color: rgba(15, 35, 51, 0.16);',
}

function renderFeatureCard(f: FeatureSpec): string {
  return `
    <article class="hp-feature">
      <span class="hp-feature-mark" style="${FEATURE_TONE_STYLES[f.tone]}">${f.mark}</span>
      <h3>${f.title}</h3>
      <p>${f.desc}</p>
    </article>
  `
}

function renderModuleCard(m: ModuleSpec): string {
  return `
    <article class="hp-module-card">
      <span class="hp-module-code">${m.code}</span>
      <div>
        <h3>${m.title}</h3>
        <p>${m.desc}</p>
      </div>
    </article>
  `
}

function renderStep(idx: number, total: number, s: StepSpec): string {
  return `
    <article class="hp-step">
      <div class="hp-step-rail">
        <span class="hp-step-bullet">${String(idx).padStart(2, '0')}</span>
        ${idx < total ? '<span class="hp-step-line"></span>' : ''}
      </div>
      <div class="hp-step-body">
        <p class="hp-step-label">${s.label}</p>
        <h3 class="hp-step-title">${s.title}</h3>
        <p class="hp-step-desc">${s.desc}</p>
      </div>
    </article>
  `
}

export function HomePage(): HTMLElement {
  const shell = createAppShell({ activeRoute: '/', layout: 'public' })
  const page = document.createElement('main')
  page.className = 'hp'

  const features: FeatureSpec[] = [
    { mark: 'KG', title: t('home.feature.graph'), desc: t('home.feature.graph.desc'), tone: 'terracotta' },
    { mark: 'QZ', title: t('home.feature.quiz'), desc: t('home.feature.quiz.desc'), tone: 'ochre' },
    { mark: 'AI', title: t('home.feature.tutor'), desc: t('home.feature.tutor.desc'), tone: 'graphite' },
    { mark: 'DX', title: t('home.feature.diagnostic'), desc: t('home.feature.diagnostic.desc'), tone: 'clay' },
    { mark: 'LV', title: t('home.feature.content'), desc: t('home.feature.content.desc'), tone: 'brass' },
    { mark: 'FR', title: t('home.feature.bilingual'), desc: t('home.feature.bilingual.desc'), tone: 'ink' },
  ]

  const modules: ModuleSpec[] = [
    { code: 'INT', title: t('home.module.interpolation'), desc: t('home.module.interpolation.desc') },
    { code: 'NUM', title: t('home.module.integration'), desc: t('home.module.integration.desc') },
    { code: 'ODE', title: t('home.module.ode'), desc: t('home.module.ode.desc') },
  ]

  const steps: StepSpec[] = [
    { label: t('home.steps.s1.label'), title: t('home.steps.s1.title'), desc: t('home.steps.s1.desc') },
    { label: t('home.steps.s2.label'), title: t('home.steps.s2.title'), desc: t('home.steps.s2.desc') },
    { label: t('home.steps.s3.label'), title: t('home.steps.s3.title'), desc: t('home.steps.s3.desc') },
  ]

  page.innerHTML = `
    <style>
      .hp {
        max-width: var(--content-max-width);
        margin: 0 auto;
        padding: var(--space-10) var(--content-padding-x) var(--space-16);
        display: flex;
        flex-direction: column;
        gap: var(--space-16);
      }

      .hp-hero {
        display: grid;
        grid-template-columns: minmax(0, 1.04fr) minmax(360px, 0.96fr);
        gap: var(--space-10);
        align-items: center;
        min-height: calc(100vh - var(--topbar-height) - 6rem);
      }
      .hp-hero-copy {
        display: flex;
        flex-direction: column;
        gap: var(--space-5);
      }
      .hp-eyebrow {
        display: inline-flex;
        align-items: center;
        gap: var(--space-2);
        align-self: flex-start;
        padding: 0.42rem 0.82rem;
        color: var(--brand-600);
        background: rgba(15, 118, 110, 0.1);
        border: 1px solid rgba(15, 118, 110, 0.22);
        border-radius: var(--radius-full);
        font-size: var(--text-xs);
        font-weight: var(--font-weight-bold);
        letter-spacing: 0.12em;
        text-transform: uppercase;
      }
      .hp-eyebrow::before {
        content: "";
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--brand-500);
        box-shadow: 0 0 0 4px rgba(15, 118, 110, 0.16);
      }
      .hp-title {
        margin: 0;
        max-width: 17ch;
        color: var(--text-primary);
        font-family: var(--font-serif);
        font-size: clamp(2.65rem, 5.2vw, var(--text-6xl));
        line-height: 1.04;
        letter-spacing: 0;
        font-weight: 600;
      }
      .hp-title-accent {
        color: var(--brand-600);
        font-style: italic;
      }
      .hp-sub {
        margin: 0;
        max-width: 58ch;
        color: var(--text-secondary);
        font-size: var(--text-lg);
        line-height: var(--line-height-relaxed);
      }
      .hp-cta-row {
        display: flex;
        flex-wrap: wrap;
        gap: var(--space-3);
        margin-top: var(--space-2);
      }
      .hp-cta-row .ds-btn {
        min-height: 50px;
        padding: 0.85rem 1.4rem;
        font-size: var(--text-md);
      }
      .hp-trust {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: var(--space-3);
        padding-top: var(--space-5);
        border-top: 1px solid var(--border-subtle);
        margin-top: var(--space-2);
        max-width: 560px;
      }
      .hp-trust-item {
        min-height: 82px;
        padding: var(--space-4);
        background: rgba(255, 255, 255, 0.66);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-lg);
      }
      .hp-trust-num {
        display: block;
        color: var(--brand-600);
        font-family: var(--font-serif);
        font-size: var(--text-3xl);
        font-weight: 700;
        line-height: 1;
      }
      .hp-trust-label {
        display: block;
        margin-top: var(--space-1);
        color: var(--text-muted);
        font-size: var(--text-xs);
        font-weight: var(--font-weight-bold);
        letter-spacing: 0.08em;
        text-transform: uppercase;
      }

      .hp-study-board {
        position: relative;
        min-height: 520px;
        padding: var(--space-6);
        background:
          linear-gradient(rgba(15, 35, 51, 0.045) 1px, transparent 1px),
          linear-gradient(90deg, rgba(15, 35, 51, 0.045) 1px, transparent 1px),
          rgba(255, 255, 255, 0.86);
        background-size: 28px 28px, 28px 28px, auto;
        border: 1px solid var(--border-default);
        border-radius: var(--radius-xl);
        box-shadow: var(--shadow-md);
        overflow: hidden;
      }
      .hp-study-board::before {
        content: "\\222B";
        position: absolute;
        right: -0.5rem;
        top: -2.8rem;
        color: rgba(15, 35, 51, 0.07);
        font-family: var(--font-serif);
        font-size: 17rem;
        line-height: 1;
        font-style: italic;
      }
      .hp-board-head {
        position: relative;
        z-index: 1;
        display: flex;
        justify-content: space-between;
        gap: var(--space-4);
        align-items: flex-start;
        margin-bottom: var(--space-6);
      }
      .hp-board-kicker {
        margin: 0 0 var(--space-2);
        color: var(--brand-600);
        font-size: var(--text-xs);
        font-weight: var(--font-weight-bold);
        letter-spacing: 0.12em;
        text-transform: uppercase;
      }
      .hp-board-title {
        margin: 0;
        color: var(--text-primary);
        font-family: var(--font-serif);
        font-size: var(--text-3xl);
        font-weight: 600;
      }
      .hp-board-chip {
        padding: 0.34rem 0.7rem;
        color: var(--warning);
        background: var(--warning-bg);
        border: 1px solid var(--warning-border);
        border-radius: var(--radius-full);
        font-size: var(--text-xs);
        font-weight: var(--font-weight-bold);
        white-space: nowrap;
      }
      .hp-platform-map {
        position: relative;
        z-index: 1;
        padding: var(--space-5);
        background: rgba(255, 255, 255, 0.88);
        border: 1px solid rgba(15, 118, 110, 0.18);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-sm);
      }
      .hp-map-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: var(--space-3);
        margin-bottom: var(--space-4);
      }
      .hp-map-title {
        margin: 0;
        color: var(--text-primary);
        font-size: var(--text-lg);
        font-weight: 800;
      }
      .hp-map-status {
        color: var(--success);
        background: var(--success-bg);
        border: 1px solid var(--success-border);
        border-radius: var(--radius-md);
        padding: 0.26rem 0.58rem;
        font-size: var(--text-xs);
        font-weight: 800;
        white-space: nowrap;
      }
      .hp-path-row {
        display: grid;
        grid-template-columns: 1fr 34px 1fr 34px 1fr 34px 1fr;
        align-items: center;
        gap: var(--space-2);
      }
      .hp-path-node {
        min-height: 106px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        gap: var(--space-2);
        padding: var(--space-3);
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
      }
      .hp-path-node.is-active {
        border-color: var(--border-emphasis);
        background: rgba(15, 118, 110, 0.08);
      }
      .hp-path-node strong {
        color: var(--text-primary);
        font-size: var(--text-sm);
        font-weight: 800;
      }
      .hp-path-node span {
        color: var(--text-muted);
        font-size: var(--text-xs);
        line-height: 1.35;
      }
      .hp-path-token {
        width: 34px;
        height: 34px;
        display: grid;
        place-items: center;
        color: var(--brand-600);
        background: rgba(15, 118, 110, 0.1);
        border: 1px solid rgba(15, 118, 110, 0.2);
        border-radius: var(--radius-md);
        font-size: var(--text-xs);
        font-weight: 800;
      }
      .hp-path-line {
        height: 2px;
        background: linear-gradient(90deg, rgba(15, 118, 110, 0.28), rgba(49, 85, 166, 0.28));
        border-radius: var(--radius-full);
      }
      .hp-preview-grid {
        position: relative;
        z-index: 1;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: var(--space-3);
        margin-top: var(--space-4);
      }
      .hp-preview-card {
        min-height: 118px;
        padding: var(--space-4);
        background: rgba(255, 255, 255, 0.82);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-lg);
      }
      .hp-preview-card strong {
        display: block;
        color: var(--text-primary);
        font-size: var(--text-sm);
        font-weight: 800;
      }
      .hp-preview-card span {
        display: block;
        margin-top: var(--space-2);
        color: var(--text-muted);
        font-size: var(--text-sm);
        line-height: 1.45;
      }
      .hp-preview-value {
        color: var(--brand-600) !important;
        font-size: var(--text-3xl) !important;
        font-weight: 800;
        line-height: 1;
      }
      .hp-meter {
        height: 8px;
        margin-top: var(--space-3);
        background: var(--bg-surface-3);
        border-radius: var(--radius-full);
        overflow: hidden;
      }
      .hp-meter-fill {
        width: 64%;
        height: 100%;
        background: var(--brand-gradient);
        border-radius: inherit;
      }
      .hp-next-card {
        position: relative;
        z-index: 1;
        margin-top: var(--space-4);
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: var(--space-4);
        padding: var(--space-4);
        background: rgba(15, 118, 110, 0.07);
        border: 1px dashed rgba(15, 118, 110, 0.24);
        border-radius: var(--radius-lg);
      }
      .hp-next-card strong {
        color: var(--text-primary);
        font-size: var(--text-sm);
        font-weight: 800;
      }
      .hp-next-card span {
        color: var(--text-muted);
        font-size: var(--text-sm);
      }
      .hp-next-badge {
        flex: 0 0 auto;
        color: var(--brand-600);
        background: rgba(15, 118, 110, 0.1);
        border: 1px solid rgba(15, 118, 110, 0.22);
        border-radius: var(--radius-md);
        padding: 0.42rem 0.72rem;
        font-size: var(--text-xs);
        font-weight: 800;
      }
      .hp-equation-card {
        position: relative;
        z-index: 1;
        padding: var(--space-5);
        background: rgba(255, 255, 255, 0.86);
        border: 1px solid rgba(15, 118, 110, 0.18);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-sm);
      }
      .hp-equation {
        margin: 0;
        color: var(--text-primary);
        font-family: var(--font-serif);
        font-size: clamp(1.45rem, 3vw, 2.25rem);
        font-style: italic;
        font-weight: 600;
        line-height: 1.35;
      }
      .hp-equation small {
        display: block;
        margin-top: var(--space-2);
        color: var(--text-muted);
        font-family: var(--font-sans);
        font-size: 0.72rem;
        font-style: normal;
        font-weight: var(--font-weight-bold);
        letter-spacing: 0.08em;
        text-transform: uppercase;
      }
      .hp-board-flow {
        position: relative;
        z-index: 1;
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: var(--space-3);
        margin-top: var(--space-4);
      }
      .hp-board-node {
        min-height: 104px;
        padding: var(--space-4);
        background: rgba(255, 255, 255, 0.82);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-lg);
      }
      .hp-board-node strong {
        display: block;
        color: var(--brand-600);
        font-size: var(--text-sm);
        font-weight: var(--font-weight-extrabold);
        letter-spacing: 0.08em;
        text-transform: uppercase;
      }
      .hp-board-node span {
        display: block;
        margin-top: var(--space-2);
        color: var(--text-muted);
        font-size: var(--text-sm);
        line-height: 1.45;
      }
      .hp-board-footer {
        position: relative;
        z-index: 1;
        margin-top: var(--space-4);
        padding: var(--space-4);
        color: var(--text-secondary);
        background: rgba(15, 118, 110, 0.07);
        border: 1px dashed rgba(15, 118, 110, 0.24);
        border-radius: var(--radius-lg);
        font-family: var(--font-serif);
        font-size: var(--text-xl);
        font-style: italic;
      }

      .hp-section-head {
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
        text-align: center;
        max-width: 720px;
        margin: 0 auto var(--space-8);
      }
      .hp-section-eyebrow {
        margin: 0;
        color: var(--brand-600);
        font-size: var(--text-xs);
        font-weight: var(--font-weight-bold);
        letter-spacing: 0.16em;
        text-transform: uppercase;
      }
      .hp-section-title {
        margin: 0;
        color: var(--text-primary);
        font-family: var(--font-serif);
        font-size: clamp(1.9rem, 3.4vw, var(--text-4xl));
        font-weight: 600;
        line-height: 1.15;
        letter-spacing: 0;
      }
      .hp-section-sub {
        margin: 0;
        color: var(--text-muted);
        font-size: var(--text-md);
        line-height: var(--line-height-relaxed);
      }
      .hp-features-grid,
      .hp-modules-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: var(--space-5);
      }
      .hp-feature,
      .hp-module-card {
        position: relative;
        padding: var(--space-6);
        background: var(--bg-surface);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-sm);
        transition: transform var(--transition-base), border-color var(--transition-base), box-shadow var(--transition-base);
      }
      .hp-feature:hover,
      .hp-module-card:hover {
        transform: translateY(-3px);
        border-color: var(--border-emphasis);
        box-shadow: var(--shadow-md);
      }
      .hp-feature-mark {
        display: inline-grid;
        place-items: center;
        min-width: 44px;
        height: 44px;
        margin-bottom: var(--space-4);
        padding: 0 var(--space-2);
        border: 1px solid;
        border-radius: var(--radius-md);
        font-family: var(--font-mono);
        font-size: 0.85rem;
        font-weight: 800;
      }
      .hp-feature h3,
      .hp-module-card h3 {
        margin: 0 0 var(--space-2);
        color: var(--text-primary);
        font-size: var(--text-lg);
        font-weight: var(--font-weight-bold);
      }
      .hp-feature p,
      .hp-module-card p {
        margin: 0;
        color: var(--text-muted);
        font-size: var(--text-sm);
        line-height: var(--line-height-relaxed);
      }
      .hp-module-card {
        display: flex;
        gap: var(--space-4);
        align-items: flex-start;
      }
      .hp-module-code {
        display: grid;
        place-items: center;
        width: 52px;
        height: 52px;
        flex: 0 0 auto;
        color: var(--text-on-inverse);
        background: var(--bg-inverse);
        border-radius: var(--radius-md);
        font-family: var(--font-mono);
        font-size: var(--text-xs);
        font-weight: 800;
        letter-spacing: 0.06em;
      }

      .hp-steps {
        display: flex;
        flex-direction: column;
        gap: 0;
        max-width: 900px;
        margin: 0 auto;
      }
      .hp-step {
        display: grid;
        grid-template-columns: 64px minmax(0, 1fr);
        gap: var(--space-5);
        padding: var(--space-2) 0;
      }
      .hp-step-rail {
        display: flex;
        flex-direction: column;
        align-items: center;
      }
      .hp-step-bullet {
        display: grid;
        place-items: center;
        width: 48px;
        height: 48px;
        color: var(--brand-600);
        background: rgba(15, 118, 110, 0.1);
        border: 1px solid rgba(15, 118, 110, 0.28);
        border-radius: 50%;
        font-family: var(--font-serif);
        font-size: var(--text-lg);
        font-weight: 700;
        font-style: italic;
      }
      .hp-step-line {
        flex: 1;
        width: 1px;
        margin-top: var(--space-2);
        min-height: 64px;
        background: linear-gradient(180deg, rgba(15, 118, 110, 0.26), rgba(15, 118, 110, 0.04));
      }
      .hp-step-body {
        padding: var(--space-3) 0 var(--space-5);
      }
      .hp-step-label {
        margin: 0 0 var(--space-1);
        color: var(--brand-600);
        font-size: var(--text-xs);
        font-weight: var(--font-weight-bold);
        letter-spacing: 0.14em;
        text-transform: uppercase;
      }
      .hp-step-title {
        margin: 0 0 var(--space-2);
        color: var(--text-primary);
        font-family: var(--font-serif);
        font-size: var(--text-2xl);
        font-weight: 600;
      }
      .hp-step-desc {
        margin: 0;
        max-width: 62ch;
        color: var(--text-muted);
        font-size: var(--text-md);
        line-height: var(--line-height-relaxed);
      }

      .hp-final-cta {
        position: relative;
        padding: var(--space-12) var(--space-8);
        text-align: center;
        background:
          radial-gradient(ellipse at 50% 0%, rgba(15, 118, 110, 0.12), transparent 60%),
          var(--bg-surface);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-xl);
        box-shadow: var(--shadow-md);
        overflow: hidden;
      }
      .hp-final-cta::before {
        content: "\\2211";
        position: absolute;
        top: -3rem;
        left: 5%;
        color: rgba(15, 35, 51, 0.06);
        font-family: var(--font-serif);
        font-size: 18rem;
        font-style: italic;
        font-weight: 700;
        line-height: 1;
        pointer-events: none;
      }
      .hp-final-cta::after {
        content: "\\03C0";
        position: absolute;
        bottom: -4rem;
        right: 6%;
        color: rgba(183, 121, 31, 0.08);
        font-family: var(--font-serif);
        font-size: 16rem;
        font-style: italic;
        font-weight: 700;
        line-height: 1;
        pointer-events: none;
      }
      .hp-final-title {
        position: relative;
        z-index: 1;
        margin: 0 0 var(--space-3);
        color: var(--text-primary);
        font-family: var(--font-serif);
        font-size: clamp(2rem, 4vw, var(--text-5xl));
        font-weight: 600;
        line-height: 1.1;
      }
      .hp-final-sub {
        position: relative;
        z-index: 1;
        margin: 0 auto var(--space-6);
        max-width: 56ch;
        color: var(--text-muted);
        font-size: var(--text-md);
        line-height: var(--line-height-relaxed);
      }
      .hp-final-actions {
        position: relative;
        z-index: 1;
        display: inline-flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: var(--space-3);
      }
      .hp-final-actions .ds-btn {
        min-height: 52px;
        padding: 0.9rem 1.6rem;
        font-size: var(--text-md);
      }

      @media (max-width: 980px) {
        .hp-hero { grid-template-columns: 1fr; min-height: auto; }
        .hp-study-board { min-height: auto; }
        .hp-features-grid,
        .hp-modules-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      }
      @media (max-width: 640px) {
        .hp { gap: var(--space-12); padding-top: var(--space-6); padding-bottom: var(--space-12); }
        .hp-trust,
        .hp-board-flow,
        .hp-path-row,
        .hp-preview-grid,
        .hp-features-grid,
        .hp-modules-grid { grid-template-columns: 1fr; }
        .hp-path-line { width: 2px; height: 20px; justify-self: center; }
        .hp-cta-row .ds-btn,
        .hp-final-actions .ds-btn { width: 100%; }
        .hp-study-board { padding: var(--space-5); }
        .hp-board-head { flex-direction: column; }
        .hp-next-card { align-items: flex-start; flex-direction: column; }
        .hp-step { grid-template-columns: 48px minmax(0, 1fr); gap: var(--space-3); }
        .hp-step-bullet { width: 40px; height: 40px; font-size: var(--text-md); }
        .hp-final-cta { padding: var(--space-8) var(--space-5); }
      }
    </style>

    <section class="hp-hero">
      <div class="hp-hero-copy">
        <span class="hp-eyebrow">${t('home.hero.kicker')}</span>
        <h1 class="hp-title">
          ${t('home.hero.titleA')}
          <span class="hp-title-accent">${t('home.hero.titleAccent')}</span>
          ${t('home.hero.titleB')}
        </h1>
        <p class="hp-sub">${t('home.hero.sub')}</p>

        <div class="hp-cta-row">
          <a href="/register" data-link class="ds-btn ds-btn-primary">${t('home.cta.register')} &rarr;</a>
          <a href="/login" data-link class="ds-btn ds-btn-secondary">${t('home.cta.login')}</a>
        </div>

        <div class="hp-trust" aria-label="Platform numbers">
          <div class="hp-trust-item">
            <span class="hp-trust-num">19</span>
            <span class="hp-trust-label">${t('home.hero.statConcepts')}</span>
          </div>
          <div class="hp-trust-item">
            <span class="hp-trust-num">4</span>
            <span class="hp-trust-label">${t('home.hero.statModules')}</span>
          </div>
          <div class="hp-trust-item">
            <span class="hp-trust-num">3</span>
            <span class="hp-trust-label">${t('home.hero.statLevels')}</span>
          </div>
        </div>
      </div>

      <aside class="hp-study-board" aria-hidden="true">
        <div class="hp-board-head">
          <div>
            <p class="hp-board-kicker">${t('topbar.adaptive')}</p>
            <h2 class="hp-board-title">${t('sidebar.path')}</h2>
          </div>
          <span class="hp-board-chip">${t('topbar.adaptive')}</span>
        </div>
        <div class="hp-platform-map">
          <div class="hp-map-head">
            <h3 class="hp-map-title">${t('learningPath.overall')}</h3>
            <span class="hp-map-status">64%</span>
          </div>
          <div class="hp-path-row">
            <div class="hp-path-node">
              <span class="hp-path-token">01</span>
              <strong>${t('home.visual.diagnostic')}</strong>
              <span>${t('home.visual.diagnostic.desc')}</span>
            </div>
            <div class="hp-path-line"></div>
            <div class="hp-path-node is-active">
              <span class="hp-path-token">02</span>
              <strong>${t('home.visual.content')}</strong>
              <span>${t('home.visual.content.desc')}</span>
            </div>
            <div class="hp-path-line"></div>
            <div class="hp-path-node">
              <span class="hp-path-token">03</span>
              <strong>${t('home.visual.quiz')}</strong>
              <span>${t('home.visual.quiz.desc')}</span>
            </div>
            <div class="hp-path-line"></div>
            <div class="hp-path-node">
              <span class="hp-path-token">04</span>
              <strong>${t('home.visual.tutor')}</strong>
              <span>${t('home.visual.tutor.desc')}</span>
            </div>
          </div>
        </div>
        <div class="hp-preview-grid">
          <div class="hp-preview-card">
            <strong>${t('dashboard.mastery.title')}</strong>
            <span class="hp-preview-value">64%</span>
            <div class="hp-meter"><div class="hp-meter-fill"></div></div>
          </div>
          <div class="hp-preview-card">
            <strong>${t('home.visual.graph')}</strong>
            <span>${t('home.visual.graph.desc')}</span>
          </div>
        </div>
        <div class="hp-next-card">
          <div>
            <strong>${t('learningPath.ready')}</strong>
            <span>${t('home.visual.quiz.desc')}</span>
          </div>
          <span class="hp-next-badge">${t('sidebar.quiz')}</span>
        </div>
      </aside>
    </section>

    <section>
      <header class="hp-section-head">
        <p class="hp-section-eyebrow">${t('topbar.adaptive')} AI</p>
        <h2 class="hp-section-title">${t('home.features.title')}</h2>
        <p class="hp-section-sub">${t('home.features.sub')}</p>
      </header>
      <div class="hp-features-grid">
        ${features.map(renderFeatureCard).join('')}
      </div>
    </section>

    <section>
      <header class="hp-section-head">
        <p class="hp-section-eyebrow">${t('home.modules.eyebrow')}</p>
        <h2 class="hp-section-title">${t('home.modules.title')}</h2>
        <p class="hp-section-sub">${t('home.modules.sub')}</p>
      </header>
      <div class="hp-modules-grid">
        ${modules.map(renderModuleCard).join('')}
      </div>
    </section>

    <section>
      <header class="hp-section-head">
        <p class="hp-section-eyebrow">${t('home.steps.title')}</p>
        <h2 class="hp-section-title">${t('home.steps.title')}</h2>
        <p class="hp-section-sub">${t('home.steps.sub')}</p>
      </header>
      <div class="hp-steps">
        ${steps.map((s, i) => renderStep(i + 1, steps.length, s)).join('')}
      </div>
    </section>

    <section class="hp-final-cta">
      <h2 class="hp-final-title">${t('home.cta.ready')}</h2>
      <p class="hp-final-sub">${t('home.cta.readySub')}</p>
      <div class="hp-final-actions">
        <a href="/register" data-link class="ds-btn ds-btn-primary">${t('home.cta.start')} &rarr;</a>
        <a href="/login" data-link class="ds-btn ds-btn-secondary">${t('home.cta.login')}</a>
      </div>
    </section>
  `

  shell.setContent(page)
  return shell.element
}
