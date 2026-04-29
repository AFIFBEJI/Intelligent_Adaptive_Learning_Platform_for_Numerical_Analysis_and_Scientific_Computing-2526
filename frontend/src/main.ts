import { api } from './api'
import { applyDesignTokens } from './design/tokens'
import { initLangFromUser } from './i18n'
import { ConceptsPage } from './pages/concepts'
import { ContentPage } from './pages/content'
import { DashboardPage } from './pages/dashboard'
import { HomePage } from './pages/home'
import { LearningPathPage } from './pages/learning-path'
import { LoginPage } from './pages/login'
import { OnboardingQuizPage } from './pages/onboarding-quiz'
import { QuizAiPage } from './pages/quiz-ai'
import { RegisterPage } from './pages/register'
import { TutorPage } from './pages/tutor'
import { router } from './router'

applyDesignTokens()
initLangFromUser()

const token = localStorage.getItem('token')
if (token) {
  api.setToken(token)
}

router
  .addRoute('/', HomePage)
  .addRoute('/login', LoginPage)
  .addRoute('/register', RegisterPage)
  .addRoute('/dashboard', DashboardPage, true)
  .addRoute('/concepts', ConceptsPage, true)
  .addRoute('/content', ContentPage, true)
  .addRoute('/path', LearningPathPage, true)
  .addRoute('/quiz', QuizAiPage, true)
  .addRoute('/quiz-ai', QuizAiPage, true)
  .addRoute('/onboarding-quiz', OnboardingQuizPage, true)
  .addRoute('/tutor', TutorPage, true)

router.start()
