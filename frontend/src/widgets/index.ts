/**
 * Interactive widget system for the /content page.
 *
 * Each widget is a TypeScript module exporting a `mount(container)` function
 * that renders a JSXGraph board inside the given container. The user can
 * drag points / sliders and see the math update in real time, complementing
 * the Manim animations (which are static once rendered).
 *
 * To add a new widget for concept "concept_xxx":
 *   1. Create src/widgets/<module>/<concept>.ts exporting `mount(container, lang)`
 *   2. Add an entry to WIDGET_REGISTRY below
 *   3. The /content page will pick it up automatically
 *
 * JSXGraph is loaded globally via index.html (CDN). We declare its global
 * type here for TypeScript.
 */

// ---- Module 1 : Interpolation ----
import { mountPolynomialBasicsWidget } from './interpolation/polynomial_basics'
import { mountLagrangeWidget } from './interpolation/lagrange'
import { mountDividedDifferencesWidget } from './interpolation/divided_differences'
import { mountNewtonInterpolationWidget } from './interpolation/newton_interpolation'
import { mountSplineInterpolationWidget } from './interpolation/spline_interpolation'

// ---- Module 2 : Numerical Integration ----
import { mountRiemannSumsWidget } from './integration/riemann_sums'
import { mountDefiniteIntegralsWidget } from './integration/definite_integrals'
import { mountTrapezoidalWidget } from './integration/trapezoidal'
import { mountSimpsonWidget } from './integration/simpson'
import { mountGaussianQuadratureWidget } from './integration/gaussian_quadrature'

// ---- Module 3 : Approximation & Optimization ----
import { mountLeastSquaresWidget } from './approximation/least_squares'
import { mountOrthogonalPolynomialsWidget } from './approximation/orthogonal_polynomials'
import { mountMinimaxApproximationWidget } from './approximation/minimax_approximation'
import { mountGradientDescentWidget } from './approximation/gradient_descent'
import { mountNewtonOptimizationWidget } from './approximation/newton_optimization'

// ---- Module 4 : Solving Non-linear Equations ----
import { mountBisectionWidget } from './root_finding/bissection'
import { mountFixedPointWidget } from './root_finding/fixed_point'
import { mountNewtonRaphsonWidget } from './root_finding/newton_raphson'
import { mountSecantWidget } from './root_finding/secant'

/** Function signature every widget must implement. */
export type WidgetMount = (container: HTMLElement, lang: 'en' | 'fr') => void

/** Map concept_id -> mount function. 19 widgets, full coverage. */
export const WIDGET_REGISTRY: Record<string, WidgetMount> = {
  // Module 1 : Interpolation
  concept_polynomial_basics:    mountPolynomialBasicsWidget,
  concept_lagrange:             mountLagrangeWidget,
  concept_divided_differences:  mountDividedDifferencesWidget,
  concept_newton_interpolation: mountNewtonInterpolationWidget,
  concept_spline_interpolation: mountSplineInterpolationWidget,
  // Module 2 : Integration
  concept_riemann_sums:         mountRiemannSumsWidget,
  concept_definite_integrals:   mountDefiniteIntegralsWidget,
  concept_trapezoidal:          mountTrapezoidalWidget,
  concept_simpson:              mountSimpsonWidget,
  concept_gaussian_quadrature:  mountGaussianQuadratureWidget,
  // Module 3 : Approximation
  concept_least_squares:          mountLeastSquaresWidget,
  concept_orthogonal_polynomials: mountOrthogonalPolynomialsWidget,
  concept_minimax_approximation:  mountMinimaxApproximationWidget,
  concept_gradient_descent:       mountGradientDescentWidget,
  concept_newton_optimization:    mountNewtonOptimizationWidget,
  // Module 4 : Root Finding
  concept_bissection:           mountBisectionWidget,
  concept_fixed_point:          mountFixedPointWidget,
  concept_newton_raphson:       mountNewtonRaphsonWidget,
  concept_secant:               mountSecantWidget,
}

/** Returns true if an interactive widget exists for this concept. */
export function hasWidget(conceptId: string): boolean {
  return conceptId in WIDGET_REGISTRY
}

/**
 * Mount the widget for `conceptId` into `container`. No-op if no widget
 * exists for this concept (so the caller can call this unconditionally).
 */
export function mountWidget(container: HTMLElement, conceptId: string, lang: 'en' | 'fr'): void {
  const fn = WIDGET_REGISTRY[conceptId]
  if (!fn) return
  fn(container, lang)
}

// Re-export shared constants/types pour que les widgets puissent
// continuer a faire `import { WIDGET_COLORS } from '../index'`.
// Note : les NOUVEAUX widgets devraient plutot importer depuis
// './shared' directement, pour eviter la dependance circulaire avec
// le registry ci-dessus.
export { WIDGET_COLORS } from './shared'
export type { JsxBoard, JsxElement } from './shared'
