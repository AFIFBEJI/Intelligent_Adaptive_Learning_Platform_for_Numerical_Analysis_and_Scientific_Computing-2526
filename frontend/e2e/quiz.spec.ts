// ============================================================
// E2E - Quiz double-mode (parcours adaptive vs entrainement libre)
// ============================================================
// Verifie le coeur fonctionnel de la Phase 3 :
//  1. Le chooser /quiz-ai affiche bien 2 cartes (Path quiz + Free practice)
//  2. Click sur "Continuer mon parcours" lance un quiz adaptive
//  3. Le mode practice ouvre le formulaire avec banderole d'avertissement
//  4. La page resultat affiche le bon badge selon le mode
// ============================================================
import { test, expect } from '@playwright/test'
import { makeEmail, registerUser } from './helpers'

// NOTE: the /quiz-ai page was redesigned — the old 2-card chooser
// (adaptive + "free practice") was replaced by a single adaptive quiz
// + study-loop view. These tests target the removed practice UI
// (#card-practice, #setup-form, ...) so they are skipped until rewritten
// for the new design. The auth + smoke E2E specs still cover the
// critical user flows (registration, login, dashboard, landing pages).
test.describe.skip('Quiz - mode chooser et flow', () => {
  test.beforeEach(async ({ page }) => {
    // Chaque test s'execute avec un compte frais pour eviter les
    // mastery deja accumules qui changeraient le comportement adaptive.
    await registerUser(page, {
      email: makeEmail('quiz'),
      password: 'TestQuiz2026',
      lang: 'fr',
      fullName: 'Quiz E2E',
    })
  })

  test('1. /quiz-ai affiche le chooser avec les 2 cartes', async ({ page }) => {
    await page.goto('/quiz-ai')

    // Les 2 grosses cartes doivent etre visibles.
    await expect(page.locator('#card-adaptive')).toBeVisible({ timeout: 10_000 })
    await expect(page.locator('#card-practice')).toBeVisible()

    // Les badges distinctifs sont presents.
    await expect(page.getByText(/Counts towards progression|Compte dans la progression/i))
      .toBeVisible()
    await expect(page.getByText(/No impact on progression|Pas d'impact/i))
      .toBeVisible()
  })

  test('2. click sur "Path quiz" lance directement un quiz adaptive', async ({ page }) => {
    // Lancer un quiz adaptatif declenche la generation de questions via le LLM,
    // indisponible en CI (cle factice) -> on saute ce test en CI uniquement.
    test.skip(!!process.env.CI, 'Quiz generation needs a live LLM, not available in CI')
    await page.goto('/quiz-ai')
    await expect(page.locator('#card-adaptive')).toBeVisible()

    await page.locator('#card-adaptive').click()

    // On doit voir le quiz avec son titre et au moins une question.
    // Le pipeline RAG/quiz_service prend quelques secondes.
    await expect(page.locator('.quiz-ai-header h1, h1').first())
      .toBeVisible({ timeout: 30_000 })
    await expect(page.locator('#questions-list')).toBeVisible({ timeout: 30_000 })

    // Pas de bandeau "practice" car on est en mode adaptive.
    await expect(page.locator('.practice-banner')).toHaveCount(0)
  })

  test('3. click sur "Free practice" ouvre le formulaire avec warning', async ({ page }) => {
    await page.goto('/quiz-ai')
    await expect(page.locator('#card-practice')).toBeVisible()

    await page.locator('#card-practice').click()

    // On voit le formulaire des filtres + le warning.
    await expect(page.locator('#setup-form')).toBeVisible({ timeout: 5_000 })
    await expect(page.locator('#topic')).toBeVisible()
    await expect(page.locator('#n_questions')).toBeVisible()
    await expect(page.locator('#difficulty')).toBeVisible()

    // Le warning explicite "ne change pas la maitrise" doit etre present.
    await expect(page.getByText(/does not change your mastery|ne modifie pas ta maitrise/i))
      .toBeVisible()

    // Bouton retour vers le chooser.
    await expect(page.locator('#btn-back-chooser')).toBeVisible()
  })

  test('4. retour depuis setup practice revient au chooser', async ({ page }) => {
    await page.goto('/quiz-ai')
    await page.locator('#card-practice').click()

    await expect(page.locator('#setup-form')).toBeVisible()

    await page.locator('#btn-back-chooser').click()

    // On retrouve les 2 cartes du chooser.
    await expect(page.locator('#card-adaptive')).toBeVisible()
    await expect(page.locator('#card-practice')).toBeVisible()
  })

  test('5. lancer un quiz practice affiche la banderole pendant le quiz', async ({ page }) => {
    // Demarrer un quiz declenche la generation de questions (LLM), indispo en CI.
    test.skip(!!process.env.CI, 'Quiz generation needs a live LLM, not available in CI')
    await page.goto('/quiz-ai')
    await page.locator('#card-practice').click()

    // Garder defaults (5 questions, moyen, mcq+true_false coches).
    await page.getByRole('button', { name: /Start practice|Demarrer/i }).click()

    // La banderole pendant le quiz doit confirmer le mode practice.
    await expect(page.locator('.practice-banner')).toBeVisible({ timeout: 30_000 })
    await expect(page.locator('.practice-banner'))
      .toContainText(/does not change your mastery|ne modifie pas ta maitrise/i)
  })
})
