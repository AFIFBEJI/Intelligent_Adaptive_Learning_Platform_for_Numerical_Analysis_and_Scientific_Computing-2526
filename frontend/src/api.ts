const BASE_URL = '/api'

export type JsonValue =
  | string
  | number
  | boolean
  | null
  | JsonValue[]
  | { [key: string]: JsonValue }

export interface LoginRequest {
  email: string
  mot_de_passe: string
}

export interface RegisterRequest {
  nom_complet: string
  email: string
  mot_de_passe: string
  niveau_actuel: string
  langue_preferee: 'en' | 'fr'
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface Etudiant {
  id: number
  nom_complet: string
  email: string
  niveau_actuel: string
  langue_preferee: 'en' | 'fr'
  date_inscription: string
  is_active: boolean
  // Phase 3: True once the student has clicked the link in their
  // verification email. The dashboard can show a banner if False.
  is_verified?: boolean
}

export interface Concept {
  id: string
  name: string
  description: string
  level: string
  category: string
}

export interface LearningPath {
  etudiant_id: number
  concepts_to_improve: Array<{ id: string; name: string; mastery: number; status: string }>
  next_recommended: Array<{ id: string; name: string; level: string; category: string }>
  overall_progress: { total_concepts: number; mastered: number; in_progress: number }
}

export interface Quiz {
  id: number
  titre: string
  module: string
  difficulte: string
  questions: Array<{
    id: number
    question: string
    options: string[]
    correct_index: number
    points: number
  }>
  date_creation: string
}

export interface QuizResult {
  id: number
  etudiant_id: number
  quiz_id: number
  score: number
  temps_reponse: number
  reponses: JsonValue
  date_tentative: string
}

export interface QuizSubmit {
  etudiant_id: number
  score: number
  temps_reponse: number
  reponses: JsonValue
}

export type AiQuestionType = 'mcq' | 'open' | 'true_false' | 'numeric'
export type AiDifficulty = 'auto' | 'facile' | 'moyen' | 'difficile'

export interface AiQuizQuestion {
  id: number
  type: AiQuestionType
  question: string
  options?: string[] | null
  difficulty: Exclude<AiDifficulty, 'auto'>
  language?: 'en' | 'fr'
}

export interface AiQuizResponse {
  quiz_id: number
  titre: string
  module: string
  difficulte: string
  concept_id: string | null
  concept_name: string | null
  questions: AiQuizQuestion[]
  n_questions: number
  language: 'en' | 'fr'
  // 'adaptive' = official path (updates mastery)
  // 'practice' = free practice (no mastery impact)
  mode?: 'adaptive' | 'practice'
  date_creation: string
}

export interface AiQuizGenerateRequest {
  concept_id?: string | null
  topic?: string | null
  n_questions: number
  difficulty: AiDifficulty
  question_types: AiQuestionType[]
  use_llm?: boolean
  language?: 'en' | 'fr'
  // 'adaptive' (default) or 'practice' depending on what the student chooses.
  mode?: 'adaptive' | 'practice'
}

export interface AiStudentAnswer {
  question_id: number
  answer: string
}

export interface AiFeedbackCard {
  score: number
  n_correct: number
  n_total: number
  temps_reponse: number
  grade_label: string
  summary: string
  strengths: string[]
  weaknesses: string[]
  mistakes_detail: string[]
  next_steps: string[]
  recommended_concepts: string[]
}

export interface AiQuestionEvaluation {
  question_id: number
  question: string
  student_answer: string
  correct_answer: string
  is_correct: boolean
  partial_credit: number
  explanation: string
  concept_id?: string | null
}

export interface AiQuizSubmitResponse {
  attempt_id: number
  quiz_id: number
  score: number
  feedback_card: AiFeedbackCard
  evaluations: AiQuestionEvaluation[]
  date_tentative: string
  // Echo of the quiz pedagogical mode so the result page knows
  // whether to show the mastery delta (adaptive) or the "this
  // quiz does not affect progress" banner (practice).
  mode?: 'adaptive' | 'practice'
  // List of concept_ids whose mastery was updated (empty if practice).
  mastery_updated?: string[]
}

export interface AiAttemptSummary {
  id: number
  quiz_id: number
  quiz_titre: string
  score: number
  temps_reponse: number
  date_tentative: string
  grade_label?: string | null
}

export interface ContentItem {
  id: string
  level: string
  title: string
  body: string
}

export interface TutorSession {
  id: number
  etudiant_id: number
  concept_id: string | null
  created_at: string
  updated_at: string
  message_count: number
}

export interface TutorMessage {
  id: number
  role: 'student' | 'tutor'
  content: string
  verified: boolean | null
  concept_id: string | null
  created_at: string
}

export interface TutorAskRequest {
  question: string
  concept_id?: string
  /**
   * "ollama" | "openai" — chosen via the picker on the tutor page.
   * If empty, the backend uses the default provider from .env.
   */
  provider?: string
}

/** An LLM option returned by GET /tutor/llm-options. */
export interface LlmOption {
  id: string                   // "ollama" or "openai"
  name: string                 // e.g. "Gemma local (E2B)"
  model: string                // technical model name
  tagline_en: string
  tagline_fr: string
  description_en: string
  description_fr: string
  requires_internet: boolean
  is_paid: boolean
  is_finetuned: boolean
  speed: 'slow' | 'fast'
  quality: 'good' | 'excellent'
  privacy: 'rgpd_safe' | 'cloud'
  icon: string                 // 'laptop' | 'cloud' (for SVG rendering)
}

export interface LlmOptionsResponse {
  picker_enabled: boolean
  default_provider: string
  available: LlmOption[]
}

export interface TutorAskResponse {
  message_id: number
  content: string
  verified: boolean
  concept_name: string
  student_mastery: number
  complexity_level: string
  verification_details: JsonValue
}

export interface TutorSessionHistory {
  session_id: number
  concept_id: string | null
  messages: TutorMessage[]
}

class ApiService {
  private token: string | null = null

  setToken(token: string): void {
    this.token = token
  }

  clearToken(): void {
    this.token = null
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = { 'Content-Type': 'application/json' }
    if (this.token) headers.Authorization = `Bearer ${this.token}`
    return headers
  }

  private async request<T>(method: string, endpoint: string, body?: unknown): Promise<T> {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method,
      headers: this.getHeaders(),
      body: body === undefined ? undefined : JSON.stringify(body),
    })

    if (!response.ok) {
      await this.raiseApiError(response)
    }

    return response.json() as Promise<T>
  }

  private async raiseApiError(response: Response): Promise<never> {
    // Special 401 case: a token expired or the user was deleted in the DB.
    // We clear the state and redirect to /login. BUT careful: this
    // behavior must NOT apply to the auth endpoints themselves
    // (/auth/login, /auth/register, /auth/forgot-password, etc.). Otherwise
    // a wrong password at login triggers a hard-redirect that
    // wipes the error message in less than a second.
    //
    // We distinguish via the URL: if the request targets an endpoint starting
    // with /auth/, we just propagate the error normally (no redirect).
    const url = response.url || ''
    const isAuthEndpoint = /\/auth\/(login|register|forgot-password|reset-password|request-verification|verify-email)/.test(url)

    if (response.status === 401 && !isAuthEndpoint) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
      throw new Error('Session expiree, reconnexion...')
    }

    const error = await response.json().catch(() => ({ detail: 'Erreur serveur' }))
    throw new Error(error.detail || `Erreur ${response.status}`)
  }

  async login(data: LoginRequest): Promise<TokenResponse> {
    const formData = new URLSearchParams()
    formData.append('username', data.email)
    formData.append('password', data.mot_de_passe)

    const response = await fetch(`${BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData.toString(),
    })

    if (!response.ok) {
      await this.raiseApiError(response)
    }

    return response.json() as Promise<TokenResponse>
  }

  async register(data: RegisterRequest): Promise<TokenResponse> {
    return this.request<TokenResponse>('POST', '/auth/register', data)
  }

  // ============================================================
  // Phase 3: email verification + reset password
  // ============================================================
  async requestEmailVerification(email: string): Promise<{ message: string; detail?: string }> {
    return this.request('POST', '/auth/request-verification', { email })
  }

  async verifyEmail(token: string): Promise<{ message: string; detail?: string }> {
    // GET endpoint, we encode the token in the URL
    return this.request('GET', `/auth/verify-email/${encodeURIComponent(token)}`)
  }

  async forgotPassword(email: string): Promise<{ message: string; detail?: string }> {
    return this.request('POST', '/auth/forgot-password', { email })
  }

  async resetPassword(token: string, newPassword: string): Promise<{ message: string; detail?: string }> {
    return this.request('POST', '/auth/reset-password', {
      token,
      new_password: newPassword,
    })
  }

  async getMe(): Promise<Etudiant> {
    return this.request<Etudiant>('GET', '/auth/me')
  }

  async updateMyLanguage(lang: 'en' | 'fr'): Promise<Etudiant> {
    const user = await this.request<Etudiant>('PUT', '/auth/me/language', {
      langue_preferee: lang,
    })
    localStorage.setItem('user', JSON.stringify(user))
    localStorage.setItem('app_lang', user.langue_preferee)
    return user
  }

  async getConcepts(): Promise<Concept[]> {
    const lang = localStorage.getItem('app_lang') || 'en'
    return this.request<Concept[]>('GET', `/graph/concepts?lang=${lang}`)
  }

  async getLearningPath(etudiantId: number): Promise<LearningPath> {
    const lang = localStorage.getItem('app_lang') || 'en'
    return this.request<LearningPath>('GET', `/graph/learning-path/${etudiantId}?lang=${lang}`)
  }

  /**
   * (12/05/2026) Lists a concept's prerequisites (REQUIRES relation in
   * Neo4j). Used by /path to explain EXACTLY why a
   * concept is locked.
   */
  async getConceptPrerequisites(conceptId: string): Promise<Array<{ id: string; name: string; difficulty: string }>> {
    const lang = localStorage.getItem('app_lang') || 'en'
    return this.request('GET', `/graph/concepts/${encodeURIComponent(conceptId)}/prerequisites?lang=${lang}`)
  }

  async getRemediation(conceptId: string): Promise<unknown> {
    return this.request('GET', `/graph/remediation/${conceptId}`)
  }

  async getConceptContent(conceptId: string, level?: string): Promise<ContentItem[]> {
    const params = new URLSearchParams()
    if (level) params.append('level', level)
    params.append('lang', localStorage.getItem('app_lang') || 'en')

    return this.request<ContentItem[]>(
      'GET',
      `/graph/concepts/${conceptId}/content?${params.toString()}`,
    )
  }

  /**
   * Retrieves the Manim animation URL for a given concept. Returns
   * `null` if no animation is available yet (404 on the backend side).
   * The frontend must handle this case by simply not showing the
   * video player (most concepts do not have a video yet).
   */
  async getAnimationUrl(conceptId: string): Promise<string | null> {
    const lang = localStorage.getItem('app_lang') || 'en'
    try {
      const data = await this.request<{ url: string; available: boolean }>(
        'GET',
        `/animations/${conceptId}?lang=${lang}`,
      )
      return data.available ? data.url : null
    } catch {
      // 404 expected if no animation. We do not log to avoid spamming.
      return null
    }
  }

  async getQuizList(module?: string, difficulte?: string): Promise<Quiz[]> {
    const params = new URLSearchParams()
    if (module) params.append('module', module)
    if (difficulte) params.append('difficulte', difficulte)

    const query = params.toString()
    return this.request<Quiz[]>('GET', `/quiz/${query ? `?${query}` : ''}`)
  }

  async getQuiz(quizId: number): Promise<Quiz> {
    return this.request<Quiz>('GET', `/quiz/${quizId}`)
  }

  async submitQuiz(quizId: number, data: QuizSubmit): Promise<QuizResult> {
    return this.request<QuizResult>('POST', `/quiz/${quizId}/submit`, data)
  }

  async getMyResults(etudiantId: number): Promise<QuizResult[]> {
    return this.request<QuizResult[]>('GET', `/quiz/results/${etudiantId}`)
  }

  async generateAiQuiz(data: AiQuizGenerateRequest): Promise<AiQuizResponse> {
    return this.request<AiQuizResponse>('POST', '/quiz-ai/generate', data)
  }

  async generateDiagnosticQuiz(): Promise<AiQuizResponse> {
    return this.request<AiQuizResponse>('POST', '/quiz-ai/diagnostic', {})
  }

  async submitAiQuiz(
    quizId: number,
    data: {
      answers: AiStudentAnswer[]
      temps_reponse: number
      language?: 'en' | 'fr'
      // (12/05/2026) Allows switching the quiz to `practice` at submit
      // even if generated in `adaptive` — managed by the toggle in the UI.
      mode_override?: 'adaptive' | 'practice'
    },
  ): Promise<AiQuizSubmitResponse> {
    return this.request<AiQuizSubmitResponse>('POST', `/quiz-ai/${quizId}/submit`, data)
  }

  async listAiAttempts(): Promise<AiAttemptSummary[]> {
    return this.request<AiAttemptSummary[]>('GET', '/quiz-ai/attempts/list')
  }

  async getAiAttempt(attemptId: number): Promise<AiQuizSubmitResponse> {
    return this.request<AiQuizSubmitResponse>('GET', `/quiz-ai/attempts/${attemptId}`)
  }

  async createTutorSession(conceptId?: string): Promise<TutorSession> {
    return this.request<TutorSession>('POST', '/tutor/sessions', {
      concept_id: conceptId || null,
    })
  }

  async getTutorSessions(): Promise<TutorSession[]> {
    return this.request<TutorSession[]>('GET', '/tutor/sessions')
  }

  async getLlmOptions(): Promise<LlmOptionsResponse> {
    return this.request<LlmOptionsResponse>('GET', '/tutor/llm-options')
  }

  async askTutor(sessionId: number, data: TutorAskRequest): Promise<TutorAskResponse> {
    return this.request<TutorAskResponse>('POST', `/tutor/sessions/${sessionId}/ask`, data)
  }

  async getTutorHistory(sessionId: number): Promise<TutorSessionHistory> {
    return this.request<TutorSessionHistory>('GET', `/tutor/sessions/${sessionId}/history`)
  }

  // ============================================================
  // Phase 4 — User study endpoints (/study/*)
  // ============================================================
  async studyEnroll(): Promise<StudyEnrollResponse> {
    return this.request<StudyEnrollResponse>('POST', '/study/enroll', {})
  }

  async studyGetPretest(): Promise<StudyTestStartResponse> {
    return this.request<StudyTestStartResponse>('GET', '/study/pretest')
  }

  async studySubmitPretest(payload: StudyTestSubmitRequest): Promise<StudyTestSubmitResponse> {
    return this.request<StudyTestSubmitResponse>('POST', '/study/pretest', payload)
  }

  async studyGetPosttest(): Promise<StudyTestStartResponse> {
    return this.request<StudyTestStartResponse>('GET', '/study/posttest')
  }

  async studySubmitPosttest(payload: StudyTestSubmitRequest): Promise<StudyTestSubmitResponse> {
    return this.request<StudyTestSubmitResponse>('POST', '/study/posttest', payload)
  }

  async studySubmitSus(payload: StudySusSubmitRequest): Promise<StudySusSubmitResponse> {
    return this.request<StudySusSubmitResponse>('POST', '/study/sus', payload)
  }

  async studyWithdraw(reason: string): Promise<void> {
    await this.request<void>('POST', `/study/withdraw?reason=${encodeURIComponent(reason)}`, {})
  }
}

// ============================================================
// Phase 4 — interfaces user study
// ============================================================
export interface StudyEnrollResponse {
  participant_code: string
  test_version: 'A_then_B' | 'B_then_A'
  pretest_version: 'A' | 'B'
  already_enrolled: boolean
}

export interface StudyItem {
  id: string
  concept_id: string
  difficulty: 'easy' | 'medium' | 'hard'
  points: number
  question_fr: string
  question_en: string
  options: string[] | null
}

export interface StudyTestStartResponse {
  participant_code: string
  phase: 'pretest' | 'posttest'
  version: 'A' | 'B'
  items: StudyItem[]
  started_at: string
}

export interface StudyTestSubmitRequest {
  answers: Record<string, number | string>
  duration_seconds: number
}

export interface StudyTestSubmitResponse {
  participant_code: string
  phase: 'pretest' | 'posttest'
  score: number
  raw: number
  max: number
  per_item: Array<{
    id: string
    concept_id: string
    difficulty: string
    is_correct: boolean
    points_earned: number
    points_max: number
  }>
  group_assigned: string | null
}

export interface StudySusSubmitRequest {
  likert: number[]
  open_responses: Record<string, string>
}

export interface StudySusSubmitResponse {
  participant_code: string
  sus_score: number
  sus_score_normalized: number
}

export const api = new ApiService()
