// ============================================================
// NextStepHero — reusable component for adaptive guidance
// ============================================================
//
// Extracted from learning-path.ts (12/05/2026) to share the pattern
// "a single primary CTA visible above the fold". Will be reused on:
//   - /path         : next concept recommended by the algo (existing)
//   - /dashboard    : "Today's plan" hero (commit UX #3)
//   - /quiz-ai      : post-quiz feedback "Next up: <X>" (commit UX #4)
//
// The component is strictly presentational: no fetch, no
// routing, no localStorage. The strings are provided by the caller
// (already i18n-translated) — this keeps the component decoupled from the
// i18n system and reusable for contexts where the strings do not
// live in i18n.ts (e.g. dynamic messages containing a
// concept name).
// ============================================================

function escapeHtml(s: string): string {
  return (s || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

export interface NextStepHeroCta {
  /** URL for <a href="...">. The caller must provide a safe URL
   *  (typically: `/route?param=${encodeURIComponent(value)}`). */
  href: string
  /** Button text, already localized. HTML-escaped by the component. */
  label: string
}

export interface NextStepHeroOptions {
  /** Small all-caps label above the title (e.g. "YOUR NEXT STEP"). */
  eyebrow: string
  /** Main title — typically the concept name, or a
   *  completion message for the 'done' variant. */
  title: string
  /** Explanatory paragraph under the title. */
  description: string
  /** Primary button (brand-gradient CTA with arrow). Omitted -> not shown. */
  primaryCta?: NextStepHeroCta
  /** Secondary button (outline). Omitted -> not shown. */
  secondaryCta?: NextStepHeroCta
  /** 'next' (default) = teal guidance; 'done' = green completion. */
  variant?: 'next' | 'done'
}

// Idempotent — called automatically by nextStepHeroHtml().
// Private export: no need to invoke it manually from the pages.
function injectNextStepHeroStyles(): void {
  if (document.querySelector('style[data-ds-next-step-hero]')) return
  const style = document.createElement('style')
  style.dataset.dsNextStepHero = 'true'
  style.textContent = `
    @keyframes nextStepPulseGlow {
      0%, 100% { box-shadow: 0 0 0 0 rgba(15, 118, 110, 0.35); }
      50%      { box-shadow: 0 0 0 12px rgba(15, 118, 110, 0); }
    }
    .next-step-hero {
      background: linear-gradient(135deg, rgba(15, 118, 110, 0.18), rgba(20, 184, 166, 0.08));
      border: 1px solid rgba(15, 118, 110, 0.45);
      border-radius: var(--radius-md);
      padding: var(--space-6);
      text-align: center;
      position: relative;
    }
    .next-step-hero::before {
      content: '';
      position: absolute;
      inset: -1px;
      border-radius: var(--radius-md);
      pointer-events: none;
      animation: nextStepPulseGlow 2.4s ease-out infinite;
    }
    .next-step-eyebrow {
      font-size: 0.78rem;
      font-weight: 800;
      letter-spacing: 0.14em;
      color: var(--brand-primary);
      margin-bottom: 10px;
    }
    .next-step-title {
      font-size: 2rem;
      font-weight: 800;
      color: var(--text-primary);
      margin: 0 0 10px;
      letter-spacing: -0.01em;
      line-height: 1.15;
    }
    .next-step-sub {
      color: var(--text-muted);
      max-width: 620px;
      margin: 0 auto var(--space-4);
      line-height: 1.55;
    }
    .next-step-actions {
      display: flex;
      gap: 12px;
      justify-content: center;
      flex-wrap: wrap;
    }
    .next-step-cta {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 14px 28px;
      background: var(--brand-gradient, linear-gradient(135deg, #0f766e, #14b8a6));
      color: var(--text-on-inverse, #fff);
      border-radius: 10px;
      font-weight: 800;
      text-decoration: none;
      font-size: 1.05rem;
      box-shadow: var(--shadow-md, 0 4px 14px rgba(15, 118, 110, 0.35));
      transition: transform 0.15s, box-shadow 0.15s;
    }
    .next-step-cta:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 22px rgba(15, 118, 110, 0.45);
    }
    .next-step-secondary {
      display: inline-flex;
      align-items: center;
      padding: 13px 22px;
      background: transparent;
      border: 1.5px solid rgba(255, 255, 255, 0.18);
      color: var(--text-primary);
      border-radius: 10px;
      font-weight: 600;
      text-decoration: none;
      transition: all 0.15s;
    }
    .next-step-secondary:hover {
      border-color: var(--brand-primary);
      color: var(--brand-primary);
    }
    .next-step-hero-done {
      background: linear-gradient(135deg, rgba(34, 197, 94, 0.18), rgba(16, 185, 129, 0.06));
      border-color: rgba(34, 197, 94, 0.45);
    }
    @media (max-width: 640px) {
      .next-step-title { font-size: 1.4rem; }
      .next-step-cta { width: 100%; justify-content: center; }
      .next-step-secondary { width: 100%; justify-content: center; }
    }
  `
  document.head.appendChild(style)
}

/**
 * Returns the (escaped) HTML of the "next step" hero.
 *
 * Side-effect: injects the styles into <head> on the first call (idempotent).
 * This lets the caller just do `container.innerHTML = nextStepHeroHtml(...)`
 * without having to handle the CSS separately.
 *
 * All strings (eyebrow, title, description, labels) are
 * HTML-escaped — the caller can therefore pass a raw concept name without
 * XSS risk.
 */
export function nextStepHeroHtml(opts: NextStepHeroOptions): string {
  injectNextStepHeroStyles()

  const variantClass = opts.variant === 'done' ? ' next-step-hero-done' : ''

  const primary = opts.primaryCta
    ? `<a href="${escapeHtml(opts.primaryCta.href)}" data-link class="next-step-cta">${escapeHtml(opts.primaryCta.label)} <span aria-hidden="true">→</span></a>`
    : ''

  const secondary = opts.secondaryCta
    ? `<a href="${escapeHtml(opts.secondaryCta.href)}" data-link class="next-step-secondary">${escapeHtml(opts.secondaryCta.label)}</a>`
    : ''

  const actions = (primary || secondary)
    ? `<div class="next-step-actions">${primary}${secondary}</div>`
    : ''

  return `
    <section class="next-step-hero${variantClass}">
      <div class="next-step-eyebrow">${escapeHtml(opts.eyebrow)}</div>
      <h2 class="next-step-title">${escapeHtml(opts.title)}</h2>
      <p class="next-step-sub">${escapeHtml(opts.description)}</p>
      ${actions}
    </section>
  `
}
