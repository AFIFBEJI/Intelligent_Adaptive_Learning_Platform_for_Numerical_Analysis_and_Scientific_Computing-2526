// ============================================================
// StudyFlow - reusable student journey map
// ============================================================

import { getLang } from '../i18n'

export type StudyStepId = 'diagnostic' | 'path' | 'learn' | 'practice' | 'tutor'

interface StudyFlowOptions {
  compact?: boolean
  title?: string
  subtitle?: string
}

interface StudyFlowStep {
  id: StudyStepId
  token: string
  title: string
  desc: string
  href: string
}

function escapeHtml(s: string): string {
  return (s || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function labels() {
  const isFr = getLang() === 'fr'
  return {
    title: isFr ? "Boucle d'etude" : 'Study loop',
    subtitle: isFr
      ? 'Une progression lisible: diagnostiquer, comprendre, pratiquer, puis demander de l aide au bon moment.'
      : 'A clear progression: diagnose, understand, practice, then ask for help at the right moment.',
    current: isFr ? 'Etape actuelle' : 'Current step',
    steps: [
      {
        id: 'diagnostic',
        token: 'DX',
        title: 'Diagnostic',
        desc: isFr ? 'Calibrer ton niveau' : 'Calibrate your level',
        href: '/onboarding-quiz',
      },
      {
        id: 'path',
        token: '01',
        title: isFr ? 'Parcours' : 'Path',
        desc: isFr ? 'Choisir la suite logique' : 'Pick the logical next step',
        href: '/path',
      },
      {
        id: 'learn',
        token: '02',
        title: isFr ? 'Cours' : 'Learn',
        desc: isFr ? 'Lire au bon niveau' : 'Study at the right level',
        href: '/content',
      },
      {
        id: 'practice',
        token: '03',
        title: 'Quiz',
        desc: isFr ? 'Verifier et consolider' : 'Check and consolidate',
        href: '/quiz-ai',
      },
      {
        id: 'tutor',
        token: 'AI',
        title: isFr ? 'Tuteur' : 'Tutor',
        desc: isFr ? 'Debloquer les points flous' : 'Unblock unclear points',
        href: '/tutor',
      },
    ] satisfies StudyFlowStep[],
  }
}

function injectStudyFlowStyles(): void {
  if (document.querySelector('style[data-ds-study-flow]')) return
  const style = document.createElement('style')
  style.dataset.dsStudyFlow = 'true'
  style.textContent = `
    .study-flow {
      width: 100%;
      padding: var(--space-5);
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-sm);
    }
    .study-flow-head {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: var(--space-4);
      margin-bottom: var(--space-4);
    }
    .study-flow-kicker {
      margin: 0 0 var(--space-1);
      color: var(--brand-600);
      font-size: var(--text-xs);
      font-weight: var(--font-weight-extrabold);
      letter-spacing: 0.12em;
      text-transform: uppercase;
    }
    .study-flow-title {
      margin: 0;
      color: var(--text-primary);
      font-size: var(--text-xl);
      font-weight: var(--font-weight-extrabold);
      line-height: 1.2;
      letter-spacing: 0;
    }
    .study-flow-subtitle {
      margin: var(--space-1) 0 0;
      max-width: 760px;
      color: var(--text-muted);
      font-size: var(--text-sm);
      line-height: 1.55;
    }
    .study-flow-grid {
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: var(--space-3);
    }
    .study-flow-step {
      position: relative;
      min-height: 108px;
      display: grid;
      grid-template-columns: auto minmax(0, 1fr);
      align-items: flex-start;
      gap: var(--space-3);
      padding: var(--space-4);
      color: var(--text-secondary);
      text-decoration: none;
      background: rgba(148, 163, 184, 0.055);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      transition: transform var(--transition-fast), border-color var(--transition-fast), background var(--transition-fast), box-shadow var(--transition-fast);
    }
    .study-flow-step:hover {
      color: var(--text-primary);
      background: var(--bg-surface-hover);
      border-color: var(--border-emphasis);
      transform: translateY(-2px);
      box-shadow: var(--shadow-sm);
    }
    .study-flow-step.is-active {
      color: var(--text-primary);
      background: rgba(15, 118, 110, 0.09);
      border-color: var(--border-emphasis);
      box-shadow: inset 0 0 0 1px rgba(15, 118, 110, 0.08);
    }
    .study-flow-token {
      width: 36px;
      height: 36px;
      display: grid;
      place-items: center;
      flex: 0 0 auto;
      color: var(--brand-600);
      background: rgba(15, 118, 110, 0.1);
      border: 1px solid rgba(15, 118, 110, 0.22);
      border-radius: var(--radius-md);
      font-family: var(--font-mono);
      font-size: var(--text-xs);
      font-weight: var(--font-weight-extrabold);
      letter-spacing: 0;
    }
    .study-flow-step.is-active .study-flow-token {
      color: var(--text-on-inverse);
      background: var(--brand-gradient);
      border-color: rgba(15, 118, 110, 0.36);
      box-shadow: var(--shadow-glow-brand);
    }
    .study-flow-copy {
      min-width: 0;
    }
    .study-flow-step-title {
      display: flex;
      align-items: center;
      gap: var(--space-2);
      color: var(--text-primary);
      font-size: var(--text-sm);
      font-weight: var(--font-weight-extrabold);
      line-height: 1.25;
    }
    .study-flow-step-desc {
      margin-top: var(--space-1);
      color: var(--text-muted);
      font-size: var(--text-xs);
      font-weight: var(--font-weight-semibold);
      line-height: 1.45;
    }
    .study-flow-current {
      display: inline-flex;
      align-items: center;
      min-height: 22px;
      padding: 0.18rem 0.45rem;
      color: var(--success);
      background: var(--success-bg);
      border: 1px solid var(--success-border);
      border-radius: var(--radius-sm);
      font-size: 0.62rem;
      font-weight: var(--font-weight-extrabold);
      line-height: 1;
      white-space: nowrap;
    }
    .study-flow--compact {
      padding: var(--space-4);
    }
    .study-flow--compact .study-flow-head {
      margin-bottom: var(--space-3);
    }
    .study-flow--compact .study-flow-title {
      font-size: var(--text-lg);
    }
    .study-flow--compact .study-flow-step {
      min-height: 84px;
      padding: var(--space-3);
    }
    .study-flow--compact .study-flow-step-desc {
      display: none;
    }
    @media (max-width: 1120px) {
      .study-flow-grid {
        grid-template-columns: repeat(3, minmax(0, 1fr));
      }
    }
    @media (max-width: 720px) {
      .study-flow-head {
        flex-direction: column;
      }
      .study-flow-grid {
        grid-template-columns: 1fr;
      }
      .study-flow-step {
        min-height: 76px;
      }
    }
  `
  document.head.appendChild(style)
}

export function studyFlowHtml(activeStep: StudyStepId | null, opts: StudyFlowOptions = {}): string {
  injectStudyFlowStyles()
  const copy = labels()
  const title = opts.title || copy.title
  const subtitle = opts.subtitle || copy.subtitle
  const compactClass = opts.compact ? ' study-flow--compact' : ''

  return `
    <section class="study-flow${compactClass}" aria-label="${escapeHtml(copy.title)}">
      <div class="study-flow-head">
        <div>
          <p class="study-flow-kicker">${escapeHtml(copy.title)}</p>
          <h2 class="study-flow-title">${escapeHtml(title)}</h2>
          <p class="study-flow-subtitle">${escapeHtml(subtitle)}</p>
        </div>
      </div>
      <div class="study-flow-grid">
        ${copy.steps.map((step) => {
          const isActive = step.id === activeStep
          return `
            <a href="${escapeHtml(step.href)}" data-link class="study-flow-step${isActive ? ' is-active' : ''}"${isActive ? ' aria-current="step"' : ''}>
              <span class="study-flow-token">${escapeHtml(step.token)}</span>
              <span class="study-flow-copy">
                <span class="study-flow-step-title">
                  ${escapeHtml(step.title)}
                  ${isActive ? `<span class="study-flow-current">${escapeHtml(copy.current)}</span>` : ''}
                </span>
                <span class="study-flow-step-desc">${escapeHtml(step.desc)}</span>
              </span>
            </a>
          `
        }).join('')}
      </div>
    </section>
  `
}
