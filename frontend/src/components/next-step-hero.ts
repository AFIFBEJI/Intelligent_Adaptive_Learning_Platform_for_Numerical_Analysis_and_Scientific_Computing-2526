// ============================================================
// NextStepHero — composant reutilisable pour la guidance adaptative
// ============================================================
//
// Extrait depuis learning-path.ts (12/05/2026) pour mutualiser le pattern
// "un seul CTA primaire visible au-dessus du fold". Sera reutilise sur :
//   - /path         : prochain concept recommande par l'algo (existant)
//   - /dashboard    : "Today's plan" hero (commit UX #3)
//   - /quiz-ai      : feedback post-quiz "Next up: <X>" (commit UX #4)
//
// Le composant est strictement presentationnel : pas de fetch, pas de
// routing, pas de localStorage. Les chaines sont fournies par l'appelant
// (deja i18n-traduites) — ca permet de garder le composant decouple du
// systeme d'i18n et reutilisable pour des contextes ou les strings ne
// vivent pas dans i18n.ts (ex: messages dynamiques contenant un nom de
// concept).
// ============================================================

function escapeHtml(s: string): string {
  return (s || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

export interface NextStepHeroCta {
  /** URL pour <a href="...">. L'appelant doit fournir une URL safe
   *  (typiquement: `/route?param=${encodeURIComponent(value)}`). */
  href: string
  /** Texte du bouton, deja localise. HTML-escape par le composant. */
  label: string
}

export interface NextStepHeroOptions {
  /** Petit label all-caps au-dessus du titre (ex: "YOUR NEXT STEP"). */
  eyebrow: string
  /** Titre principal — typiquement le nom du concept, ou un message de
   *  completion pour la variante 'done'. */
  title: string
  /** Paragraphe explicatif sous le titre. */
  description: string
  /** Bouton primaire (CTA brand-gradient avec fleche). Omis -> pas affiche. */
  primaryCta?: NextStepHeroCta
  /** Bouton secondaire (outline). Omis -> pas affiche. */
  secondaryCta?: NextStepHeroCta
  /** 'next' (defaut) = teal guidance ; 'done' = green completion. */
  variant?: 'next' | 'done'
}

// Idempotent — appele automatiquement par nextStepHeroHtml().
// Export prive : pas besoin de l'invoquer manuellement depuis les pages.
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
 * Renvoie le HTML (escape) du hero "next step".
 *
 * Side-effect: injecte les styles dans <head> au premier appel (idempotent).
 * Cela permet a l'appelant de juste faire `container.innerHTML = nextStepHeroHtml(...)`
 * sans avoir a gerer le CSS separement.
 *
 * Toutes les chaines (eyebrow, title, description, labels) sont
 * HTML-escape — l'appelant peut donc passer un concept name brut sans
 * risque XSS.
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
