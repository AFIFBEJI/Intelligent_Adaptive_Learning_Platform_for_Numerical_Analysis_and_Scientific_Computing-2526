// ============================================================
// QuizFeedbackCard — carte de feedback post-soumission
// ============================================================
//
// Extrait de quiz-ai.ts (13/05/2026, commit #4-pre-b) pour faire passer
// quiz-ai.ts sous le plafond de 1200 lignes. Cette extraction est une
// preparation pour le commit #4 qui ajoutera DANS ce composant une
// section hero "Next up: X" / "Practice again" pilotee par le score.
//
// Strictement presentationnel : pas d'acces a state, pas d'appel API.
// Les callbacks `onResetToSetup` et `onTryAgain` permettent a la page
// hote de gerer les transitions de phase. La map `conceptNames` permet
// d'afficher des noms lisibles pour les concepts dont le mastery a ete
// mis a jour, sans coupler le composant au cache global des concepts.
// ============================================================

import { getLang, t } from '../i18n'
import { nextStepHeroHtml } from './next-step-hero'
import type { AiQuizSubmitResponse, AiFeedbackCard } from '../api'

// ------------------------------------------------------------
// Helpers prives — duplique depuis quiz-ai.ts pour eviter un import
// circulaire et garder le composant auto-suffisant.
// ------------------------------------------------------------
// TODO backlog : `typesetMath` est duplique entre ce fichier, tutor.ts
// et quiz-ai.ts. A factoriser dans frontend/src/utils/mathjax.ts dans
// une passe ulterieure (hors scope #4).

declare const MathJax: {
  typesetPromise?: (elements?: Element[]) => Promise<void>
} | undefined

function escapeHtml(s: string): string {
  const div = document.createElement('div')
  div.textContent = s
  return div.innerHTML
}

function gradeColor(score: number): string {
  if (score >= 90) return '#16a34a'
  if (score >= 75) return '#22c55e'
  if (score >= 60) return '#eab308'
  if (score >= 40) return '#f97316'
  return '#ef4444'
}

async function typesetMath(root: HTMLElement): Promise<void> {
  if (typeof MathJax !== 'undefined' && MathJax?.typesetPromise) {
    try {
      await MathJax.typesetPromise([root])
    } catch (err) {
      console.warn('MathJax typeset failed:', err)
    }
  }
}

// ------------------------------------------------------------
// Public API
// ------------------------------------------------------------

export interface QuizFeedbackCardOptions {
  /** Reponse complete du backend (feedback_card + evaluations + mode +
   *  mastery_updated). Le composant ne touche pas a son contenu. */
  result: AiQuizSubmitResponse
  /** Lookup id concept -> nom localise. Vide si cache pas dispo —
   *  les ids sont alors affiches en fallback dans la zone "delta mastery". */
  conceptNames: Map<string, string>
  /** Prochain concept recommande par l'algorithme apres ce submit
   *  (next_recommended[0] d'un re-fetch /learning-path). Null si tous
   *  les concepts sont maitrises, ou si le re-fetch a echoue, ou si on
   *  vient de l'historique. Pilote le hero "Next up: X" pour score >=70. */
  nextConcept: { id: string; name: string } | null
  /** Concept cible du quiz (URL ?concept=). Null si quiz general adaptive
   *  ou practice libre. Pilote le hero "Practice again" pour score <70. */
  targetConceptId: string | null
  /** Clic sur "Back to setup" : la page reset l'etat et bascule en
   *  phase 'setup' (ou 'chooser'). Le composant n'a pas a connaitre la
   *  cible exacte. */
  onResetToSetup: () => void
  /** Clic sur "Try another quiz" : la page reset l'etat et bascule en
   *  phase 'chooser' pour permettre un nouveau choix de mode. */
  onTryAgain: () => void
}

export function renderQuizFeedbackCard(
  root: HTMLElement,
  opts: QuizFeedbackCardOptions,
): void {
  injectQuizFeedbackCardStyles()

  const res = opts.result
  const card = res.feedback_card

  // Recommandations contextuelles : concepts ou l'etudiant a echoue
  // (extraits des evaluations) + concepts recommandes par le moteur.
  const failedConceptIds = Array.from(new Set(
    res.evaluations
      .filter((e) => !e.is_correct && e.concept_id)
      .map((e) => e.concept_id!),
  )).slice(0, 3)

  const recoSection =
    (failedConceptIds.length > 0 || (card.recommended_concepts || []).length > 0)
      ? `
        <div class="fb-recommendations">
          <div class="fb-recommendations-title">${escapeHtml(t('quiz.feedback.recommended'))}</div>
          <div class="fb-reco-actions">
            ${failedConceptIds.map((cid) => `
              <a href="/content?concept=${encodeURIComponent(cid)}" data-link class="fb-reco-chip">
                ${escapeHtml(t('quiz.feedback.review'))}
              </a>
              <a href="/quiz-ai?concept=${encodeURIComponent(cid)}" data-link class="fb-reco-chip">
                ${escapeHtml(t('quiz.feedback.practice'))}
              </a>
            `).join('')}
            <a href="/tutor" data-link class="fb-reco-chip">${escapeHtml(t('quiz.feedback.tutor'))}</a>
            <a href="/path" data-link class="fb-reco-chip">${escapeHtml(t('quiz.feedback.path'))}</a>
          </div>
        </div>
      `
      : ''

  // Bandeau de mode + delta mastery.
  // En mode adaptive, on liste les concepts dont le mastery a ete mis a
  // jour (resolution best-effort via la map fournie par l'appelant).
  // En mode practice, on affiche le message "n'impacte pas le niveau".
  const isPractice = res.mode === 'practice'
  const masteryUpdated = res.mastery_updated || []
  const updatedNames = masteryUpdated.map((cid) => opts.conceptNames.get(cid) || cid)

  const modeBanner = isPractice
    ? `<div class="results-mode-badge practice">⚠ ${escapeHtml(t('quiz.results.modePractice'))}</div>`
    : `<div class="results-mode-badge adaptive">✓ ${escapeHtml(t('quiz.results.modeAdaptive'))}</div>`

  const deltaSection = isPractice
    ? `<div class="delta-mastery">${escapeHtml(t('quiz.results.noDelta'))}</div>`
    : (updatedNames.length > 0
        ? `<div class="delta-mastery"><strong>${escapeHtml(t('quiz.results.deltaMastery'))} :</strong> ${updatedNames.map((n) => escapeHtml(n)).join(', ')}</div>`
        : '')

  // ============================================================
  // (13/05/2026) CTA hero : "Next up: X" si reussi, "Practice again"
  // sinon. Reuse le composant NextStepHero pour la consistance visuelle
  // avec /path et /dashboard. La logique :
  //   - score >= 70 + nextConcept dispo -> "Great! Next up: <name>" + bouton
  //   - score >= 70 + tout maitrise      -> variant 'done', pas de CTA
  //   - score <  70 + targetConcept     -> "Keep practicing" + practice + tutor
  //   - sinon (history view, quiz libre) -> pas de hero, juste la card
  // ============================================================
  const score = card.score
  const isFr = getLang() === 'fr'
  const passed = score >= 70
  let ctaHero = ''
  if (passed && opts.nextConcept) {
    ctaHero = nextStepHeroHtml({
      eyebrow: isFr ? 'BIEN JOUE ! SUITE :' : 'GREAT! NEXT UP:',
      title: opts.nextConcept.name,
      description: isFr
        ? 'Tu as bien gere ce concept. Lance-toi sur la prochaine etape recommandee.'
        : "You've handled this concept well. Tackle the next recommended step.",
      primaryCta: {
        href: `/quiz-ai?concept=${encodeURIComponent(opts.nextConcept.id)}`,
        label: isFr ? 'Demarrer le concept suivant' : 'Start next concept',
      },
    })
  } else if (passed && !opts.nextConcept && !isPractice) {
    // Mode adaptive + tout maitrise = pas de concept suivant a proposer.
    // En mode practice, on n'affiche pas ce hero "tout maitrise" parce
    // qu'on n'a juste pas refetch le path (le score practice ne compte pas).
    ctaHero = nextStepHeroHtml({
      eyebrow: isFr ? 'BRAVO !' : 'WELL DONE!',
      title: isFr ? 'Tous les concepts disponibles maitrises' : 'All available concepts mastered',
      description: isFr
        ? 'Repasse en mode practice pour consolider tes acquis.'
        : 'Revisit in practice mode to consolidate what you have learned.',
      variant: 'done',
    })
  } else if (!passed && opts.targetConceptId) {
    const conceptName = opts.conceptNames.get(opts.targetConceptId) || opts.targetConceptId
    ctaHero = nextStepHeroHtml({
      eyebrow: isFr ? 'CONTINUE A T\'ENTRAINER' : 'KEEP PRACTICING',
      title: conceptName,
      description: isFr
        ? `Tu as ${Math.round(score)}% sur ce concept. Refais un quiz pour solidifier, ou demande de l'aide au tuteur.`
        : `You scored ${Math.round(score)}% on this concept. Practice again to lock it in, or ask the tutor for help.`,
      primaryCta: {
        href: `/quiz-ai?concept=${encodeURIComponent(opts.targetConceptId)}`,
        label: isFr ? 'Refaire ce concept' : 'Practice again',
      },
      secondaryCta: {
        href: `/tutor?concept=${encodeURIComponent(opts.targetConceptId)}`,
        label: isFr ? 'Demander au tuteur' : 'Ask the tutor',
      },
    })
  }

  root.innerHTML = `
    <div class="quiz-ai-page">
      ${ctaHero ? `<div class="feedback-cta-wrap">${ctaHero}</div>` : ''}
      <div class="feedback-card">
        ${modeBanner}
        ${renderScoreRing(card)}
        ${deltaSection}
        ${renderFeedbackBody(card)}
        ${renderEvaluations(res.evaluations)}
        ${recoSection}
        <div class="fb-actions">
          <button class="btn-secondary" id="btn-back">${escapeHtml(t('quiz.action.backSetup'))}</button>
          <button class="btn-primary" id="btn-again">${escapeHtml(t('quiz.action.again'))}</button>
        </div>
      </div>
    </div>
  `

  root.querySelector('#btn-back')?.addEventListener('click', () => opts.onResetToSetup())
  root.querySelector('#btn-again')?.addEventListener('click', () => opts.onTryAgain())

  void typesetMath(root)
}

// ------------------------------------------------------------
// Renderers prives
// ------------------------------------------------------------

function renderScoreRing(card: AiFeedbackCard): string {
  const color = gradeColor(card.score)
  const pct = Math.max(0, Math.min(100, card.score))
  const circumference = 2 * Math.PI * 54
  const dash = (pct / 100) * circumference

  return `
    <div class="score-ring">
      <svg width="140" height="140" viewBox="0 0 140 140">
        <circle cx="70" cy="70" r="54" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="14"/>
        <circle cx="70" cy="70" r="54" fill="none" stroke="${color}" stroke-width="14"
          stroke-dasharray="${dash} ${circumference}" stroke-linecap="round"
          transform="rotate(-90 70 70)"/>
        <text x="70" y="74" text-anchor="middle" font-size="28" font-weight="700" fill="var(--text-primary)">
          ${pct.toFixed(0)}
        </text>
        <text x="70" y="94" text-anchor="middle" font-size="11" fill="var(--text-muted)">/ 100</text>
      </svg>
      <div class="grade-label" style="color:${color}">${escapeHtml(card.grade_label)}</div>
      <div class="score-meta">
        <strong>${card.n_correct}</strong> / ${card.n_total} ${escapeHtml(t('quiz.meta.correct'))}
        <span class="score-meta-sep">/</span>
        ${card.temps_reponse}s
      </div>
    </div>
  `
}

function renderFeedbackBody(card: AiFeedbackCard): string {
  const section = (title: string, items: string[], cls: string): string => {
    if (!items || items.length === 0) return ''
    return `
      <section class="fb-section ${cls}">
        <h3>${escapeHtml(title)}</h3>
        <ul>${items.map((x) => `<li>${escapeHtml(x)}</li>`).join('')}</ul>
      </section>
    `
  }
  return `
    <div class="fb-body">
      <blockquote class="fb-summary">${escapeHtml(card.summary)}</blockquote>
      ${section(t('quiz.feedback.summary.strengths'), card.strengths, 'fb-strengths')}
      ${section(t('quiz.feedback.summary.review'), card.weaknesses, 'fb-weaknesses')}
      ${section(t('quiz.feedback.summary.mistakes'), card.mistakes_detail, 'fb-mistakes')}
      ${section(t('quiz.feedback.summary.next'), card.next_steps, 'fb-nexts')}
    </div>
  `
}

interface EvaluationRow {
  question_id: number
  question: string
  student_answer: string
  correct_answer: string
  is_correct: boolean
  partial_credit: number
  explanation: string
}

function renderEvaluations(evals: EvaluationRow[]): string {
  if (!evals || evals.length === 0) return ''
  return `
    <details class="eval-details">
      <summary>${escapeHtml(t('quiz.feedback.details'))} (${evals.length})</summary>
      <div class="eval-list">
        ${evals.map((e) => `
          <div class="eval-row ${e.is_correct ? 'eval-ok' : 'eval-ko'}">
            <div class="eval-head">
              <span class="eval-icon">${e.is_correct ? 'OK' : 'NO'}</span>
              <strong>Q${e.question_id}</strong>
              <span class="eval-pc">${(e.partial_credit * 100).toFixed(0)}%</span>
            </div>
            <div class="eval-q">${escapeHtml(e.question)}</div>
            <div class="eval-ans">
              <div><em>${escapeHtml(t('quiz.feedback.yourAnswer'))}:</em> ${escapeHtml(e.student_answer || t('quiz.feedback.empty'))}</div>
              <div><em>${escapeHtml(t('quiz.feedback.expected'))}:</em> ${escapeHtml(e.correct_answer)}</div>
            </div>
            ${e.explanation ? `<div class="eval-exp">${escapeHtml(e.explanation)}</div>` : ''}
          </div>
        `).join('')}
      </div>
    </details>
  `
}

// ------------------------------------------------------------
// CSS injection (idempotent)
// ------------------------------------------------------------

function injectQuizFeedbackCardStyles(): void {
  if (document.querySelector('style[data-ds-quiz-feedback-card]')) return
  const style = document.createElement('style')
  style.dataset.dsQuizFeedbackCard = 'true'
  style.textContent = `
    .feedback-cta-wrap { margin-bottom: var(--space-5); }
    .feedback-card { background: var(--bg-surface); border-radius: 12px; padding: 32px; box-shadow: var(--shadow-md); }
    .score-ring { text-align: center; margin-bottom: 24px; }
    .grade-label { font-size: 1.3rem; font-weight: 700; margin: 8px 0 4px; }
    .score-meta { color: var(--text-muted); font-size: 0.95rem; }
    .score-meta-sep { color: var(--text-subtle); margin: 0 6px; }
    .fb-summary { background: rgba(15,118,110,0.08); border-left: 4px solid var(--brand-500); padding: 16px 20px; margin: 16px 0; border-radius: 4px; font-size: 1.05rem; }
    .fb-section { margin: 20px 0; }
    .fb-section h3 { font-size: 1.05rem; margin: 0 0 10px; }
    .fb-section ul { margin: 0; padding-left: 22px; }
    .fb-section li { margin: 6px 0; line-height: 1.5; }
    .fb-strengths h3 { color: var(--success); }
    .fb-weaknesses h3 { color: #fb923c; }
    .fb-mistakes h3 { color: var(--danger); }
    .fb-nexts h3 { color: var(--brand-600); }
    .eval-details { margin-top: 20px; }
    .eval-details summary { cursor: pointer; font-weight: 600; padding: 8px 0; }
    .eval-list { display: flex; flex-direction: column; gap: 12px; margin-top: 12px; }
    .eval-row { padding: 14px; border-radius: 8px; border: 1px solid var(--border-default); }
    .eval-ok { background: var(--success-bg); border-color: var(--success-border); }
    .eval-ko { background: var(--danger-bg); border-color: var(--danger-border); }
    .eval-head { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; font-size: 0.9rem; }
    .eval-icon { font-size: 1.2rem; font-weight: 700; }
    .eval-ok .eval-icon { color: var(--success); }
    .eval-ko .eval-icon { color: var(--danger); }
    .eval-pc { margin-left: auto; color: var(--text-muted); font-size: 0.85rem; }
    .eval-q { font-size: 0.95rem; margin-bottom: 8px; }
    .eval-ans { display: flex; gap: 24px; font-size: 0.9rem; color: var(--text-secondary); }
    .eval-ans em { color: var(--text-muted); font-style: normal; font-weight: 500; margin-right: 4px; }
    .eval-exp { margin-top: 10px; padding-top: 10px; border-top: 1px dashed var(--border-default); color: var(--text-secondary); font-size: 0.92rem; font-style: italic; line-height: 1.6; }
    .fb-actions { display: flex; justify-content: center; gap: 12px; margin-top: 28px; flex-wrap: wrap; }
    .fb-recommendations { margin: 24px 0 0; padding: 20px; background: rgba(15,118,110,0.06); border: 1px solid rgba(15,118,110,0.2); border-radius: 12px; }
    .fb-recommendations-title { font-size: 0.78rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--brand-600); margin: 0 0 12px; }
    .fb-reco-actions { display: flex; gap: 8px; flex-wrap: wrap; }
    .fb-reco-chip { display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; border-radius: 999px; background: var(--bg-surface); border: 1px solid var(--border-default); color: var(--text-secondary); font-size: 0.85rem; font-weight: 600; text-decoration: none; transition: all 0.15s; }
    .fb-reco-chip:hover { border-color: var(--border-emphasis); color: var(--brand-600); background: rgba(15,118,110,0.1); }
    .results-mode-badge { display: inline-flex; align-items: center; padding: 5px 12px; border-radius: var(--radius-md); font-size: 0.8rem; font-weight: 700; margin-bottom: var(--space-3); }
    .results-mode-badge.adaptive { background: var(--success-bg); color: var(--success); border: 1px solid var(--success-border); }
    .results-mode-badge.practice { background: var(--warning-bg); color: var(--warning); border: 1px solid var(--warning-border); }
    .delta-mastery { padding: 12px 16px; margin: var(--space-3) 0; border-radius: var(--radius-md); background: rgba(15,118,110,0.08); border: 1px solid rgba(15,118,110,0.22); font-size: 0.92rem; }
    .delta-mastery strong { color: var(--brand-600); }
  `
  document.head.appendChild(style)
}
