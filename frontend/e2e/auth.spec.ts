// ============================================================
// E2E - Flow d'authentification complet
// ============================================================
// Verifie :
//  1. Qu'un nouveau compte peut etre cree avec choix de langue obligatoire
//  2. Qu'on est bien rediriger apres registration (token JWT pose)
//  3. Que le meme compte peut se reconnecter via /login
//  4. Que le dashboard s'affiche apres login
// ============================================================
import { test, expect } from '@playwright/test'
import { makeEmail, registerUser, loginUser, expectOnDashboard } from './helpers'

test.describe('Auth - registration + login + dashboard', () => {
  // On garde l'email genere pour pouvoir login dans le 2e test.
  let sharedEmail = ''
  const sharedPassword = 'TestE2E2026'

  test('1. registration cree un compte et pose le JWT en localStorage', async ({ page }) => {
    sharedEmail = makeEmail('register')

    const token = await registerUser(page, {
      email: sharedEmail,
      password: sharedPassword,
      lang: 'fr',
      fullName: 'E2E Test Register',
    })

    // Le JWT est pose en localStorage et a une vraie forme (3 segments base64).
    expect(token).toBeTruthy()
    expect(token.split('.').length).toBe(3)

    // Apres registration, on est rediriger vers une page authentifiee
    // (/onboarding-quiz ou /dashboard selon le flow).
    await expect(page).not.toHaveURL(/\/register/)
  })

  test('2. login d\'un compte existant pose le JWT et redirige', async ({ page }) => {
    // On utilise le compte cree dans le test precedent.
    test.skip(!sharedEmail, 'Le test 1 doit avoir tourne avant')

    const token = await loginUser(page, sharedEmail, sharedPassword)
    expect(token).toBeTruthy()
    expect(token.split('.').length).toBe(3)

    // On peut naviguer vers /dashboard sans etre re-redirige vers /login.
    await page.goto('/dashboard')
    await expectOnDashboard(page)
  })

  test('3. login avec mauvais mot de passe affiche une erreur', async ({ page }) => {
    test.skip(!sharedEmail, 'Le test 1 doit avoir tourne avant')

    await page.goto('/login')
    // Choisir une langue pour debloquer le bouton submit. La page est
    // re-rendue par router.navigate(), donc on attend explicitement que
    // #submit-btn soit enabled avant de remplir le formulaire.
    await page.locator('[data-lang="fr"]').first().click()
    await expect(page.locator('#submit-btn')).toBeEnabled({ timeout: 5_000 })
    await page.locator('input[type="email"]').fill(sharedEmail)
    await page.locator('input[type="password"]').fill('mauvais-pass-123')
    await page.locator('#submit-btn').click()

    // Soit on voit un message d'erreur, soit on reste sur /login.
    // Le frontend ne doit PAS poser de token.
    await page.waitForTimeout(2000)
    const token = await page.evaluate(() => localStorage.getItem('token'))
    expect(token).toBeFalsy()
    await expect(page).toHaveURL(/\/login/)
  })

  test('4. acceder a /dashboard sans token redirige vers /login', async ({ page }) => {
    // On efface tout l'etat avant d'essayer.
    await page.goto('/login')
    await page.evaluate(() => {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    })

    await page.goto('/dashboard')
    // Le router doit nous renvoyer sur /login.
    await expect(page).toHaveURL(/\/login/, { timeout: 5_000 })
  })
})
