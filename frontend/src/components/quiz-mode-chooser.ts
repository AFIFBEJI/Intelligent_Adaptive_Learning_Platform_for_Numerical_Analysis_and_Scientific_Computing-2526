// ============================================================
// QuizChooser + QuizModeChooser — choix de mode du quiz
// ============================================================
//
// Extrait de quiz-ai.ts (13/05/2026, commit #4-pre-a) pour faire passer
// quiz-ai.ts sous le plafond de 1200 lignes. La page hote etait a 1783
// lignes apres le WIP qui a ajoute renderModeChooser ; ce decoupage
// retire ~280 lignes (UI + CSS associee, pas la logique de transition).
//
// Deux variantes UI, deux APIs separees pour eviter de melanger les
// callbacks de chacune dans une seule interface :
//   - QuizChooser      : ecran d'accueil generique (sans concept cible).
//                        3 actions possibles : start adaptive, start
//                        practice (-> setup), open history.
//   - QuizModeChooser  : ecran cible quand /quiz-ai?concept=<id>. Affiche
//                        le nom du concept et demande Adaptive vs Practice.
//
// Les deux partagent les memes classes CSS .mode-chooser / .mode-card-big
// (auto-injectees une fois, idempotent). Le composant est strictement
// presentationnel : aucun acces a `state`, aucune navigation directe,
// aucune mutation d'API. Tout passe par les callbacks fournis par
// l'appelant — la page hote garde le controle de la state machine.
// ============================================================

import { api } from '../api'
import { getLang } from '../i18n'
import type { Concept } from '../api'

// Cache local des concepts pour resoudre le nom du concept cible. Le
// composant peut etre rendu plusieurs fois ; on garde le fetch a 1 seul
// appel reseau pour toute la session.
let _conceptsCache: Concept[] | null = null
let _conceptsFetching: Promise<Concept[]> | null = null
async function getCachedConcepts(): Promise<Concept[]> {
  if (_conceptsCache) return _conceptsCache
  if (_conceptsFetching) return _conceptsFetching
  _conceptsFetching = api.getConcepts()
    .then((list) => {
      _conceptsCache = list
      return list
    })
    .catch(() => [])
  return _conceptsFetching
}

function escapeHtml(s: string): string {
  const div = document.createElement('div')
  div.textContent = s
  return div.innerHTML
}

// ------------------------------------------------------------
// QuizChooser — ecran d'accueil generique (no concept_id)
// ------------------------------------------------------------

export interface QuizChooserOptions {
  /** Message d'erreur a afficher en banniere au-dessus des cartes. */
  error: string | null
  /** Carte "Adaptive" cliquee : la page doit lancer un quiz adaptive
   *  avec les defauts (pas de setup form). */
  onStartAdaptive: () => void
  /** Carte "Practice" cliquee : la page doit transitionner vers la
   *  phase 'setup' (formulaire). */
  onStartPractice: () => void
  /** Lien historique du toolbar : la page doit transitionner vers la
   *  phase 'history' et charger les tentatives. */
  onOpenHistory: () => void
}

export function renderQuizChooser(root: HTMLElement, opts: QuizChooserOptions): void {
  injectQuizChooserStyles()
  const labels = chooserLabels(getLang())
  root.innerHTML = `
    <div class="quiz-ai-page">
      <div class="quiz-ai-toolbar">
        <button class="btn-link" id="btn-history">${escapeHtml(labels.history)}</button>
      </div>

      ${opts.error ? `<div class="alert-error">${escapeHtml(opts.error)}</div>` : ''}

      <div class="mode-chooser">
        <button type="button" class="mode-card-big mode-adaptive" id="card-adaptive">
          <div class="mode-card-icon-wrap"><span class="mode-card-icon" aria-hidden="true">▲</span></div>
          <h3 class="mode-card-title">${escapeHtml(labels.adaptiveTitle)}</h3>
          <p class="mode-card-desc">${escapeHtml(labels.adaptiveTagline)}</p>
          <div class="mode-card-tags">
            <span class="mode-badge mode-badge-good">${escapeHtml(labels.adaptiveBadge)}</span>
          </div>
          <span class="mode-card-cta">${escapeHtml(labels.adaptiveCta)} <span aria-hidden="true">→</span></span>
        </button>

        <button type="button" class="mode-card-big mode-practice" id="card-practice">
          <div class="mode-card-icon-wrap"><span class="mode-card-icon" aria-hidden="true">⚙</span></div>
          <h3 class="mode-card-title">${escapeHtml(labels.practiceTitle)}</h3>
          <p class="mode-card-desc">${escapeHtml(labels.practiceTagline)}</p>
          <div class="mode-card-tags">
            <span class="mode-badge mode-badge-warn">${escapeHtml(labels.practiceBadge)}</span>
          </div>
          <span class="mode-card-cta">${escapeHtml(labels.practiceCta)} <span aria-hidden="true">→</span></span>
        </button>
      </div>
    </div>
  `
  root.querySelector('#card-adaptive')?.addEventListener('click', () => opts.onStartAdaptive())
  root.querySelector('#card-practice')?.addEventListener('click', () => opts.onStartPractice())
  root.querySelector('#btn-history')?.addEventListener('click', () => opts.onOpenHistory())
}

// ------------------------------------------------------------
// QuizModeChooser — variante cible (avec concept_id)
// ------------------------------------------------------------

export interface QuizModeChooserOptions {
  /** Concept cible (vient de ?concept=<id> dans l'URL). */
  conceptId: string
  /** Message d'erreur a afficher en banniere. */
  error: string | null
  /** Mode choisi : la page doit appeler api.generateAiQuiz avec ce mode
   *  et le conceptId, puis transitionner vers la phase 'quiz'. */
  onSelectMode: (mode: 'adaptive' | 'practice') => void
  /** Lien "Retour au parcours" du toolbar : la page doit naviguer vers /path
   *  ET reset le pendingConceptId. */
  onBackToPath: () => void
}

export function renderQuizModeChooser(root: HTMLElement, opts: QuizModeChooserOptions): void {
  injectQuizChooserStyles()
  const isFr = getLang() === 'fr'
  // Fallback title derived from conceptId : "concept_polynomial_basics"
  // -> "Polynomial Basics". Remplace par le vrai name une fois le cache
  // resolu (cf. block .then() plus bas).
  const fallbackTitle = opts.conceptId
    .replace(/^concept_/, '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())

  root.innerHTML = `
    <div class="quiz-ai-page">
      <div class="quiz-ai-toolbar">
        <button class="btn-link" id="btn-back-path">← ${escapeHtml(isFr ? 'Retour au parcours' : 'Back to path')}</button>
      </div>

      <div class="mode-chooser-header">
        <p class="mode-chooser-eyebrow">${escapeHtml(isFr ? 'Quiz cible' : 'Targeted quiz')}</p>
        <h2 class="mode-chooser-title" id="concept-title">${escapeHtml(fallbackTitle)}</h2>
        <p class="mode-chooser-sub">${escapeHtml(isFr
          ? 'Choisis comment ce quiz doit compter pour toi.'
          : 'Pick how you want this quiz to count.')}</p>
      </div>

      ${opts.error ? `<div class="alert-error">${escapeHtml(opts.error)}</div>` : ''}

      <div class="mode-chooser">
        <button type="button" class="mode-card-big mode-adaptive" id="card-adaptive">
          <div class="mode-card-icon-wrap"><span class="mode-card-icon" aria-hidden="true">▲</span></div>
          <h3 class="mode-card-title">${escapeHtml(isFr ? 'Adaptive' : 'Adaptive')}</h3>
          <p class="mode-card-desc">${escapeHtml(isFr
            ? 'Ton score met a jour ton niveau de maitrise. Recommande pour progresser.'
            : 'Your score updates your mastery level. Recommended to advance.')}</p>
          <div class="mode-card-tags">
            <span class="mode-badge mode-badge-good">${escapeHtml(isFr ? 'Compte pour ma progression' : 'Counts towards progress')}</span>
          </div>
          <span class="mode-card-cta">${escapeHtml(isFr ? 'Demarrer le quiz adaptive' : 'Start adaptive quiz')} <span aria-hidden="true">→</span></span>
        </button>

        <button type="button" class="mode-card-big mode-practice" id="card-practice">
          <div class="mode-card-icon-wrap"><span class="mode-card-icon" aria-hidden="true">⚙</span></div>
          <h3 class="mode-card-title">${escapeHtml(isFr ? 'Practice' : 'Practice')}</h3>
          <p class="mode-card-desc">${escapeHtml(isFr
            ? "Entrainement libre. Le score n'impacte pas ta progression. Utile pour reviser sans pression."
            : 'Free training. Score does NOT affect your level. Useful to revise without pressure.')}</p>
          <div class="mode-card-tags">
            <span class="mode-badge mode-badge-warn">${escapeHtml(isFr ? "N'impacte pas mon niveau" : 'No impact on level')}</span>
          </div>
          <span class="mode-card-cta">${escapeHtml(isFr ? 'Demarrer en practice' : 'Start practice')} <span aria-hidden="true">→</span></span>
        </button>
      </div>
    </div>
  `

  // Resolution asynchrone du vrai nom du concept (le fallback derive de
  // l'id reste affiche tant que la promesse ne resout pas).
  void getCachedConcepts()
    .then((concepts) => {
      const found = concepts.find((c) => c.id === opts.conceptId)
      if (found?.name) {
        const el = root.querySelector('#concept-title') as HTMLElement | null
        if (el) el.textContent = found.name
      }
    })
    .catch(() => { /* fallback already shown */ })

  root.querySelector('#btn-back-path')?.addEventListener('click', () => opts.onBackToPath())
  root.querySelector('#card-adaptive')?.addEventListener('click', () => opts.onSelectMode('adaptive'))
  root.querySelector('#card-practice')?.addEventListener('click', () => opts.onSelectMode('practice'))
}

// ------------------------------------------------------------
// i18n labels for the generic chooser
// ------------------------------------------------------------
// On ne passe pas par i18n.ts pour rester decouple : ces labels n'ont
// jamais existe sous forme de cles t() avant ce refactor (le code
// d'origine appelait t('quiz.mode.adaptive.title') etc., qui SONT dans
// i18n.ts). On les re-route ici via une lookup explicite pour eviter
// d'importer t() et son etat global dans le composant.

function chooserLabels(lang: 'fr' | 'en') {
  if (lang === 'fr') {
    return {
      history: 'Voir l\'historique',
      adaptiveTitle: 'Adaptive',
      adaptiveTagline: 'Le systeme ajuste les questions a ton niveau, et chaque score met a jour ton parcours adaptatif.',
      adaptiveBadge: 'Compte pour ma progression',
      adaptiveCta: 'Demarrer un quiz adaptive',
      practiceTitle: 'Practice',
      practiceTagline: 'Choisis le concept, le nombre de questions et la difficulte. Les scores ne modifient pas ton niveau.',
      practiceBadge: "N'impacte pas mon niveau",
      practiceCta: 'Configurer un quiz',
    }
  }
  return {
    history: 'View history',
    adaptiveTitle: 'Adaptive',
    adaptiveTagline: 'The system tailors questions to your level, and every score updates your adaptive journey.',
    adaptiveBadge: 'Counts towards progress',
    adaptiveCta: 'Start an adaptive quiz',
    practiceTitle: 'Practice',
    practiceTagline: 'Pick a concept, question count and difficulty. Scores do not affect your level.',
    practiceBadge: 'No impact on level',
    practiceCta: 'Configure a quiz',
  }
}

// ------------------------------------------------------------
// CSS injection (idempotent) — partage par les 2 variantes
// ------------------------------------------------------------

function injectQuizChooserStyles(): void {
  if (document.querySelector('style[data-ds-quiz-chooser]')) return
  const style = document.createElement('style')
  style.dataset.dsQuizChooser = 'true'
  style.textContent = `
    .mode-chooser {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: var(--space-5);
      margin-top: var(--space-4);
    }
    @media (max-width: 768px) {
      .mode-chooser { grid-template-columns: 1fr; }
    }
    .mode-card-big {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      gap: var(--space-3);
      padding: var(--space-6) var(--space-5);
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: var(--radius-lg);
      cursor: pointer;
      text-align: left;
      font-family: inherit;
      transition: transform var(--transition-fast), border-color var(--transition-fast),
                  box-shadow var(--transition-fast), background var(--transition-fast);
      min-height: 280px;
      position: relative;
    }
    .mode-card-big.mode-adaptive { border-top: 4px solid var(--brand-500); }
    .mode-card-big.mode-practice { border-top: 4px solid var(--text-muted); }
    .mode-card-big:hover {
      transform: translateY(-3px);
      border-color: var(--border-emphasis);
      box-shadow: var(--shadow-md);
      background: var(--bg-surface-hover);
    }
    .mode-card-big:active { transform: translateY(-1px); }
    .mode-card-icon-wrap {
      width: 56px; height: 56px;
      border-radius: var(--radius-md);
      display: flex; align-items: center; justify-content: center;
      flex-shrink: 0;
    }
    .mode-adaptive .mode-card-icon-wrap { background: rgba(15,118,110,0.12); color: var(--brand-600); }
    .mode-practice .mode-card-icon-wrap { background: var(--bg-surface-2); color: var(--text-secondary); }
    .mode-card-icon { font-size: 1.6rem; font-weight: 800; }
    .mode-card-title {
      margin: 0;
      font-size: 1.4rem; font-weight: 800;
      color: var(--text-primary);
      letter-spacing: -0.01em;
    }
    .mode-card-desc {
      margin: 0;
      color: var(--text-muted);
      font-size: 0.95rem; line-height: 1.55;
      flex: 1;
    }
    .mode-card-tags { display: flex; flex-wrap: wrap; gap: var(--space-2); }
    .mode-card-cta {
      display: inline-flex; align-items: center; gap: var(--space-2);
      margin-top: var(--space-2);
      padding: 0.6rem 1rem;
      border-radius: var(--radius-md);
      background: var(--brand-gradient);
      color: var(--text-on-inverse);
      font-weight: 700; font-size: 0.92rem;
      transition: gap var(--transition-fast), background var(--transition-fast);
    }
    .mode-card-big:hover .mode-card-cta { gap: var(--space-3); }
    .mode-badge {
      display: inline-flex; align-items: center;
      min-height: 26px; padding: 4px 10px;
      border-radius: var(--radius-md);
      font-size: 0.72rem; font-weight: 800;
      letter-spacing: 0.03em; flex-shrink: 0;
    }
    .mode-badge-good { background: var(--success-bg); color: var(--success); border: 1px solid var(--success-border); }
    .mode-badge-warn { background: var(--warning-bg); color: var(--warning); border: 1px solid var(--warning-border); }
    .mode-chooser-header {
      margin: var(--space-4) auto var(--space-5);
      text-align: center;
      max-width: 640px;
      padding: 0 var(--space-3);
    }
    .mode-chooser-eyebrow {
      font-size: 0.85rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: var(--brand-primary);
      margin-bottom: 8px;
    }
    .mode-chooser-title {
      font-size: 2.2rem;
      font-weight: 800;
      color: var(--text-primary);
      margin: 0 0 12px;
      line-height: 1.2;
      letter-spacing: -0.01em;
    }
    .mode-chooser-sub {
      color: var(--text-muted);
      font-size: 1.05rem;
      max-width: 520px;
      margin: 0 auto;
      line-height: 1.5;
    }
    @media (max-width: 640px) {
      .mode-chooser-title { font-size: 1.7rem; }
      .mode-chooser-sub { font-size: 0.95rem; }
    }
  `
  document.head.appendChild(style)
}
