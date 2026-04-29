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

export type AiQuestionType = 'mcq' | 'open' | 'true_false'
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
    if (response.status === 401) {
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
    return this.request<Concept[]>('GET', '/graph/concepts')
  }

  async getLearningPath(etudiantId: number): Promise<LearningPath> {
    return this.request<LearningPath>('GET', `/graph/learning-path/${etudiantId}`)
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
    data: { answers: AiStudentAnswer[]; temps_reponse: number; language?: 'en' | 'fr' },
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

  async askTutor(sessionId: number, data: TutorAskRequest): Promise<TutorAskResponse> {
    return this.request<TutorAskResponse>('POST', `/tutor/sessions/${sessionId}/ask`, data)
  }

  async getTutorHistory(sessionId: number): Promise<TutorSessionHistory> {
    return this.request<TutorSessionHistory>('GET', `/tutor/sessions/${sessionId}/history`)
  }
}

export const api = new ApiService()
