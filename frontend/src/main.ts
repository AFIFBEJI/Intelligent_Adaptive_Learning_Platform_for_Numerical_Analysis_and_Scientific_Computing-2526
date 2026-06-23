import { api } from './api'
import { applyDesignTokens } from './design/tokens'
import { initLangFromUser } from './i18n'
import { ConceptsPage } from './pages/concepts'
import { ContentPage } from './pages/content'
import { DashboardPage } from './pages/dashboard'
import { ForgotPasswordPage } from './pages/forgot-password'
import { HomePage } from './pages/home'
import { LearningPathPage } from './pages/learning-path'
import { LoginPage } from './pages/login'
import { OnboardingQuizPage } from './pages/onboarding-quiz'
import { QuizAiPage } from './pages/quiz-ai'
import { RegisterPage } from './pages/register'
import { ResetPasswordPage } from './pages/reset-password'
import { StudySusPage } from './pages/study-sus'
import { StudyTestPage } from './pages/study-test'
import { StudyWelcomePage } from './pages/study-welcome'
import { TutorPage } from './pages/tutor'
import { VerifyEmailPage } from './pages/verify-email'
import { router } from './router'

applyDesignTokens()
// initLangFromUser does NOT set any default language if the user
// has never chosen one: the mandatory selector at /login and /register
// handles the first selection.
initLangFromUser()

const token = localStorage.getItem('token')
if (token) {
  api.setToken(token)
}

router
  .addRoute('/', HomePage)
  .addRoute('/login', LoginPage)
  .addRoute('/register', RegisterPage)
  // Phase 3: 3 new auth routes (public, not requireAuth)
  .addRoute('/forgot-password', ForgotPasswordPage)
  .addRoute('/reset-password', ResetPasswordPage)
  .addRoute('/verify-email', VerifyEmailPage)
  .addRoute('/dashboard', DashboardPage, true)
  .addRoute('/concepts', ConceptsPage, true)
  .addRoute('/content', ContentPage, true)
  .addRoute('/path', LearningPathPage, true)
  .addRoute('/quiz', QuizAiPage, true)
  .addRoute('/quiz-ai', QuizAiPage, true)
  .addRoute('/onboarding-quiz', OnboardingQuizPage, true)
  .addRoute('/tutor', TutorPage, true)
  // Phase 4 - User study
  .addRoute('/study', StudyWelcomePage, true)
  .addRoute('/study/pretest', StudyTestPage, true)
  .addRoute('/study/posttest', StudyTestPage, true)
  .addRoute('/study/sus', StudySusPage, true)

router.start()
