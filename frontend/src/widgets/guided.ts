/**
 * Entry point for the guided examples.
 * API consumed by pages/content.ts: hasGuided(id), mountGuided(el, id, lang)
 */

import { GScript, Lang, mountScript } from './guided_core'
import { GUIDED_INTERPOLATION } from './guided_scripts_interpolation'
import { GUIDED_INTEGRATION } from './guided_scripts_integration'
import { GUIDED_APPROXIMATION } from './guided_scripts_approximation'
import { GUIDED_ROOTFINDING } from './guided_scripts_rootfinding'

const SCRIPTS: Record<string, GScript> = {
  ...GUIDED_INTERPOLATION,
  ...GUIDED_INTEGRATION,
  ...GUIDED_APPROXIMATION,
  ...GUIDED_ROOTFINDING,
}

export function hasGuided(conceptId: string): boolean {
  return conceptId in SCRIPTS
}

export function mountGuided(container: HTMLElement, conceptId: string, lang: Lang): void {
  const script = SCRIPTS[conceptId]
  if (!script) return
  mountScript(container, script, lang)
}
