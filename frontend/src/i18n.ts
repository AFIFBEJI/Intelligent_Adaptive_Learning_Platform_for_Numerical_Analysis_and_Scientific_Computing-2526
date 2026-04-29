export type Lang = 'en' | 'fr'

type Dict = Record<string, { en: string; fr: string }>

const DEFAULT_LANG: Lang = 'en'

const DICT: Dict = {
  'sidebar.brand.name': { en: 'Numera', fr: 'Numera' },
  'sidebar.brand.sub': { en: 'Adaptive learning', fr: 'Apprentissage adaptatif' },
  'sidebar.dashboard': { en: 'Dashboard', fr: 'Tableau de bord' },
  'sidebar.path': { en: 'Learning path', fr: 'Parcours' },
  'sidebar.concepts': { en: 'Concepts', fr: 'Concepts' },
  'sidebar.content': { en: 'Course content', fr: 'Cours' },
  'sidebar.quiz': { en: 'Quizzes', fr: 'Quiz' },
  'sidebar.tutor': { en: 'AI tutor', fr: 'Tuteur IA' },
  'sidebar.group.parcours': { en: 'Progress', fr: 'Progression' },
  'sidebar.group.apprendre': { en: 'Learn', fr: 'Apprendre' },
  'sidebar.group.pratiquer': { en: 'Practice', fr: 'Pratiquer' },
  'sidebar.group.aide': { en: 'Support', fr: 'Aide' },
  'sidebar.student': { en: 'Student', fr: 'Etudiant' },
  'sidebar.logout': { en: 'Sign out', fr: 'Deconnexion' },
  'sidebar.login': { en: 'Sign in', fr: 'Connexion' },
  'language.label': { en: 'Learning language', fr: "Langue d'apprentissage" },
  'language.current': { en: 'Current language', fr: 'Langue actuelle' },
  'language.english': { en: 'English', fr: 'Anglais' },
  'language.french': { en: 'French', fr: 'Francais' },
  'language.switchHelp': {
    en: 'New quizzes, feedback and course content will use this language.',
    fr: 'Les nouveaux quiz, feedbacks et cours utiliseront cette langue.',
  },
  'topbar.adaptive': { en: 'Adaptive', fr: 'Adaptatif' },

  'home.badge': { en: 'AI learning for numerical analysis', fr: "Apprentissage IA pour l'analyse numerique" },
  'home.title': { en: 'Adaptive Learning Platform for Numerical Analysis', fr: "Plateforme d'apprentissage adaptatif pour l'analyse numerique" },
  'home.subtitle': {
    en: 'A focused workspace for diagnostics, personalized paths, verified explanations and adaptive quizzes.',
    fr: 'Un espace de travail clair pour diagnostics, parcours personnalises, explications verifiees et quiz adaptatifs.',
  },
  'home.cta.register': { en: 'Create account', fr: 'Creer un compte' },
  'home.cta.login': { en: 'Sign in', fr: 'Connexion' },
  'home.feature.graph': { en: 'Knowledge graph', fr: 'Graphe de connaissances' },
  'home.feature.graph.desc': {
    en: 'Concepts are organized by dependencies, modules and remediation resources.',
    fr: 'Les concepts sont organises par dependances, modules et ressources de remediation.',
  },
  'home.feature.quiz': { en: 'Adaptive quizzes', fr: 'Quiz adaptatifs' },
  'home.feature.quiz.desc': {
    en: 'Questions, answer types and feedback follow the selected language and your current mastery.',
    fr: 'Les questions, types de reponse et retours suivent la langue choisie et ton niveau actuel.',
  },
  'home.feature.tutor': { en: 'AI tutor', fr: 'Tuteur IA' },
  'home.feature.tutor.desc': {
    en: 'Ask questions and receive structured explanations with LaTeX and verification.',
    fr: 'Pose tes questions et recois des explications structurees avec LaTeX et verification.',
  },
  'home.visual.diagnostic': { en: 'Diagnostic', fr: 'Diagnostic' },
  'home.visual.diagnostic.desc': { en: 'Initial mastery calibration', fr: 'Calibration initiale du niveau' },
  'home.visual.graph': { en: 'Graph', fr: 'Graphe' },
  'home.visual.graph.desc': { en: 'Prerequisites and dependencies', fr: 'Prerequis et dependances' },
  'home.visual.content': { en: 'Content', fr: 'Cours' },
  'home.visual.content.desc': { en: 'Simple, standard, rigorous levels', fr: 'Niveaux simple, standard et rigoureux' },
  'home.visual.quiz': { en: 'Quiz', fr: 'Quiz' },
  'home.visual.quiz.desc': { en: 'Adaptive feedback cards', fr: 'Cartes de feedback adaptatives' },
  'home.visual.tutor': { en: 'Tutor', fr: 'Tuteur' },
  'home.visual.tutor.desc': { en: 'Verified explanations', fr: 'Explications verifiees' },

  'auth.register.title': { en: 'Create your account', fr: 'Creer ton compte' },
  'auth.register.subtitle': {
    en: 'Choose your learning language. English is selected by default.',
    fr: "Choisis ta langue d'apprentissage. L'anglais est selectionne par defaut.",
  },
  'auth.login.title': { en: 'Welcome back', fr: 'Bon retour' },
  'auth.login.subtitle': { en: 'Sign in to continue your adaptive path.', fr: 'Connecte-toi pour continuer ton parcours adaptatif.' },
  'auth.fullName': { en: 'Full name', fr: 'Nom complet' },
  'auth.email': { en: 'Email', fr: 'Email' },
  'auth.password': { en: 'Password', fr: 'Mot de passe' },
  'auth.language': { en: 'Learning language', fr: "Langue d'apprentissage" },
  'auth.english': { en: 'English', fr: 'Anglais' },
  'auth.french': { en: 'French', fr: 'Francais' },
  'auth.register.submit': { en: 'Create account', fr: 'Creer le compte' },
  'auth.register.loading': { en: 'Creating account...', fr: 'Creation du compte...' },
  'auth.login.submit': { en: 'Sign in', fr: 'Se connecter' },
  'auth.login.loading': { en: 'Signing in...', fr: 'Connexion...' },
  'auth.haveAccount': { en: 'Already have an account?', fr: 'Deja un compte ?' },
  'auth.needAccount': { en: 'Need an account?', fr: 'Besoin d un compte ?' },
  'auth.goLogin': { en: 'Sign in', fr: 'Connexion' },
  'auth.goRegister': { en: 'Create one', fr: 'Creer un compte' },
  'auth.error.register': { en: 'Registration failed.', fr: "L'inscription a echoue." },
  'auth.error.login': { en: 'Invalid email or password.', fr: 'Email ou mot de passe incorrect.' },

  'dashboard.title': { en: 'Dashboard', fr: 'Tableau de bord' },
  'dashboard.subtitle': { en: 'Your progress, priorities and next learning actions.', fr: 'Ta progression, tes priorites et les prochaines actions.' },
  'level.beginner': { en: 'Beginner', fr: 'Debutant' },
  'level.intermediate': { en: 'Intermediate', fr: 'Intermediaire' },
  'level.advanced': { en: 'Advanced', fr: 'Avance' },

  'quiz.title': { en: 'Adaptive quiz', fr: 'Quiz adaptatif' },
  'quiz.subtitle': {
    en: 'Generate, answer and review feedback in your selected language.',
    fr: 'Genere, reponds et revise les retours dans ta langue choisie.',
  },
  'quiz.history': { en: 'View history', fr: "Voir l'historique" },
  'quiz.setup.concept': { en: 'Topic / concept', fr: 'Sujet / concept' },
  'quiz.setup.autoConcept': { en: 'Automatic choice based on my level', fr: 'Choix automatique selon mon niveau' },
  'quiz.setup.conceptHint': {
    en: 'Choose a concept or keep automatic mode so the platform targets your weakest prerequisites.',
    fr: 'Choisis un concept ou garde le mode automatique pour cibler tes prerequis fragiles.',
  },
  'quiz.setup.adaptiveTitle': { en: 'Adaptive setup', fr: 'Reglage adaptatif' },
  'quiz.setup.adaptiveText': {
    en: 'Auto difficulty uses your mastery score. The selected language is applied to new questions, answers and feedback.',
    fr: 'La difficulte auto utilise ton score de maitrise. La langue choisie est appliquee aux nouvelles questions, reponses et feedbacks.',
  },
  'quiz.setup.languageTitle': { en: 'Quiz language', fr: 'Langue du quiz' },
  'quiz.setup.languageHint': {
    en: 'Switch here before generating a quiz. Existing attempts keep the language used when they were created.',
    fr: 'Change ici avant de generer un quiz. Les tentatives existantes gardent leur langue de creation.',
  },
  'quiz.setup.questions': { en: 'Number of questions', fr: 'Nombre de questions' },
  'quiz.setup.difficulty': { en: 'Difficulty', fr: 'Difficulte' },
  'quiz.setup.types': { en: 'Question types', fr: 'Types de questions' },
  'quiz.setup.generate': { en: 'Generate quiz', fr: 'Generer le quiz' },
  'quiz.difficulty.auto': { en: 'Automatic by level', fr: 'Automatique selon le niveau' },
  'quiz.difficulty.facile': { en: 'Easy', fr: 'Facile' },
  'quiz.difficulty.moyen': { en: 'Medium', fr: 'Moyen' },
  'quiz.difficulty.difficile': { en: 'Hard', fr: 'Difficile' },
  'quiz.type.mcq': { en: 'Multiple choice', fr: 'QCM' },
  'quiz.type.true_false': { en: 'True / false', fr: 'Vrai / faux' },
  'quiz.type.open': { en: 'Open answer', fr: 'Reponse ouverte' },
  'quiz.error.types': { en: 'Choose at least one question type.', fr: 'Choisis au moins un type de question.' },
  'quiz.error.generate': { en: 'Unable to generate the quiz.', fr: 'Impossible de generer le quiz.' },
  'quiz.error.submit': { en: 'Unable to submit the quiz.', fr: 'Impossible de soumettre le quiz.' },
  'quiz.loading.generate': { en: 'Preparing adaptive questions for your current level...', fr: 'Preparation de questions adaptees a ton niveau...' },
  'quiz.loading.submit': { en: 'Scoring answers and preparing feedback...', fr: 'Correction des reponses et preparation du feedback...' },
  'quiz.meta.module': { en: 'Module', fr: 'Module' },
  'quiz.meta.difficulty': { en: 'Difficulty', fr: 'Difficulte' },
  'quiz.meta.language': { en: 'Language', fr: 'Langue' },
  'quiz.meta.questions': { en: 'questions', fr: 'questions' },
  'quiz.meta.answered': { en: 'answered', fr: 'repondues' },
  'quiz.meta.correct': { en: 'correct', fr: 'correctes' },
  'quiz.action.cancel': { en: 'Cancel', fr: 'Annuler' },
  'quiz.action.submit': { en: 'Submit quiz', fr: 'Soumettre le quiz' },
  'quiz.action.backSetup': { en: 'Back to setup', fr: 'Retour aux reglages' },
  'quiz.action.again': { en: 'Generate another quiz', fr: 'Generer un autre quiz' },
  'quiz.confirm.leave': { en: 'Leave this quiz? Your answers will be lost.', fr: 'Quitter ce quiz ? Tes reponses seront perdues.' },
  'quiz.answer.true': { en: 'True', fr: 'Vrai' },
  'quiz.answer.false': { en: 'False', fr: 'Faux' },
  'quiz.answer.placeholder': { en: 'Type your answer: number, formula, or keyword...', fr: 'Saisis ta reponse : nombre, formule ou mot-cle...' },
  'quiz.feedback.recommended': { en: 'Recommended next actions', fr: 'Actions recommandees' },
  'quiz.feedback.review': { en: 'Review this concept', fr: 'Reviser ce concept' },
  'quiz.feedback.practice': { en: 'Practice it again', fr: 'S entrainer encore' },
  'quiz.feedback.tutor': { en: 'Ask the AI tutor', fr: 'Demander au tuteur IA' },
  'quiz.feedback.path': { en: 'View learning path', fr: 'Voir le parcours' },
  'quiz.feedback.details': { en: 'View question details', fr: 'Voir le detail des questions' },
  'quiz.feedback.yourAnswer': { en: 'Your answer', fr: 'Ta reponse' },
  'quiz.feedback.expected': { en: 'Expected', fr: 'Attendu' },
  'quiz.feedback.empty': { en: '(empty)', fr: '(vide)' },
  'quiz.feedback.summary.strengths': { en: 'Strengths', fr: 'Points forts' },
  'quiz.feedback.summary.review': { en: 'To review', fr: 'A revoir' },
  'quiz.feedback.summary.mistakes': { en: 'Mistake details', fr: 'Details des erreurs' },
  'quiz.feedback.summary.next': { en: 'Next steps', fr: 'Prochaines etapes' },
  'quiz.history.title': { en: 'Quiz attempts', fr: 'Tentatives de quiz' },
  'quiz.history.back': { en: 'Back', fr: 'Retour' },
  'quiz.history.empty': { en: 'No attempts yet.', fr: 'Aucune tentative pour le moment.' },
  'quiz.history.date': { en: 'Date', fr: 'Date' },
  'quiz.history.quiz': { en: 'Quiz', fr: 'Quiz' },
  'quiz.history.score': { en: 'Score', fr: 'Score' },
  'quiz.history.time': { en: 'Time', fr: 'Temps' },
  'quiz.history.result': { en: 'Result', fr: 'Resultat' },
  'quiz.history.details': { en: 'Details', fr: 'Details' },
}

export function normalizeLang(value: unknown): Lang {
  return value === 'fr' ? 'fr' : DEFAULT_LANG
}

export function getStoredUser(): { langue_preferee?: Lang; niveau_actuel?: string; nom_complet?: string; id?: number } | null {
  try {
    const raw = localStorage.getItem('user')
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function getLang(): Lang {
  const stored = localStorage.getItem('app_lang')
  if (stored === 'fr' || stored === 'en') return stored
  return normalizeLang(getStoredUser()?.langue_preferee)
}

export function setLang(lang: Lang): void {
  localStorage.setItem('app_lang', lang)
  document.documentElement.lang = lang

  const user = getStoredUser()
  if (user) {
    localStorage.setItem('user', JSON.stringify({ ...user, langue_preferee: lang }))
  }
}

export function initLangFromUser(): Lang {
  const lang = getLang()
  setLang(lang)
  return lang
}

export function t(key: string): string {
  const item = DICT[key]
  if (!item) return key
  return item[getLang()] || item.en
}

export function languageName(lang: Lang): string {
  return lang === 'fr' ? t('language.french') : t('language.english')
}

export function tLevel(level?: string | null): string {
  const normalized = (level || 'beginner').toLowerCase()
  if (normalized.startsWith('av') || normalized === 'advanced') return t('level.advanced')
  if (normalized.startsWith('inter')) return t('level.intermediate')
  return t('level.beginner')
}

export function formatDateTime(value: string): string {
  try {
    return new Date(value).toLocaleString(getLang() === 'fr' ? 'fr-FR' : 'en-US', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return value
  }
}
