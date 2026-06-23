export type Lang = 'en' | 'fr'

type Dict = Record<string, { en: string; fr: string }>

// Langue de secours UNIQUEMENT pour le rendu : ne sert pas à pré-sélectionner
// un choix dans les formulaires. La sélection au login/register est obligatoire.
const FALLBACK_LANG: Lang = 'en'

export const SUPPORTED_LANGS: ReadonlyArray<Lang> = ['en', 'fr']

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

  // Refined home page (hero, features, steps, stats, final CTA)
  'home.hero.kicker': { en: 'AI-powered • Adaptive • Verified Math', fr: 'IA pilotee • Adaptatif • Maths verifiees' },
  'home.hero.titleA': { en: 'Master', fr: 'Maitrise' },
  'home.hero.titleAccent': { en: 'numerical analysis', fr: "l'analyse numerique" },
  'home.hero.titleB': { en: 'one concept at a time.', fr: 'un concept a la fois.' },
  'home.hero.sub': {
    en: 'A focused workspace built for math students. Diagnose your level, follow a personalized path, and learn with explanations verified by symbolic computation.',
    fr: 'Un espace conçu pour les etudiants en maths. Diagnostique ton niveau, suis un parcours personnalise et apprends avec des explications verifiees par calcul symbolique.',
  },
  'home.hero.statConcepts': { en: 'concepts', fr: 'concepts' },
  'home.hero.statModules': { en: 'modules', fr: 'modules' },
  'home.hero.statLevels': { en: 'difficulty levels', fr: 'niveaux de difficulte' },

  'home.features.title': { en: 'Everything you need to learn the math', fr: 'Tout ce qu il faut pour apprendre les maths' },
  'home.features.sub': {
    en: 'Six tools that work together to keep you in the optimal learning zone.',
    fr: 'Six outils qui travaillent ensemble pour te maintenir dans la zone d apprentissage optimale.',
  },
  'home.feature.diagnostic': { en: 'Diagnostic calibration', fr: 'Calibration diagnostique' },
  'home.feature.diagnostic.desc': {
    en: 'A short quiz estimates your starting level so the platform recommends the right next step from day one.',
    fr: 'Un court quiz estime ton niveau de depart et recommande la bonne prochaine etape des le premier jour.',
  },
  'home.feature.content': { en: 'Multi-level lessons', fr: 'Cours multi-niveaux' },
  'home.feature.content.desc': {
    en: 'Each concept comes in three versions — simplified, standard, rigorous — adapted to your current mastery.',
    fr: 'Chaque concept en trois versions — simplifie, standard, rigoureux — adaptees a ta maitrise actuelle.',
  },
  'home.feature.bilingual': { en: 'Bilingual content', fr: 'Contenu bilingue' },
  'home.feature.bilingual.desc': {
    en: 'Switch between English and French at any moment — quiz, feedback and explanations follow you.',
    fr: 'Bascule entre anglais et francais a tout moment — quiz, feedback et explications te suivent.',
  },
  'home.visual.boardTitle': { en: 'Numerical notebook', fr: "Cahier d'analyse" },
  'home.visual.verified': { en: 'verified math', fr: 'maths verifiees' },

  'home.modules.eyebrow': { en: 'Study themes', fr: 'Themes a etudier' },
  'home.modules.title': { en: 'A calm path through numerical analysis', fr: "Un parcours calme dans l'analyse numerique" },
  'home.modules.sub': {
    en: 'The platform focuses on the core topics you need for scientific computing.',
    fr: 'La plateforme se concentre sur les notions essentielles du calcul scientifique.',
  },
  'home.module.interpolation': { en: 'Interpolation', fr: 'Interpolation' },
  'home.module.interpolation.desc': {
    en: 'Lagrange polynomials, approximation ideas and the role of nodes.',
    fr: 'Polynomes de Lagrange, approximation et role des points.',
  },
  'home.module.integration': { en: 'Numerical integration', fr: 'Integration numerique' },
  'home.module.integration.desc': {
    en: 'Quadrature, weights, error intuition and practical computation.',
    fr: "Quadrature, poids, intuition de l'erreur et calcul pratique.",
  },
  'home.module.ode': { en: 'Differential equations', fr: 'Equations differentielles' },
  'home.module.ode.desc': {
    en: 'Euler, Runge-Kutta and step-by-step reasoning for dynamic systems.',
    fr: 'Euler, Runge-Kutta et raisonnement progressif pour les systemes dynamiques.',
  },

  'home.steps.title': { en: 'How it works', fr: 'Comment ca marche' },
  'home.steps.sub': {
    en: 'Three steps to go from "where do I start?" to confident problem solving.',
    fr: 'Trois etapes pour passer de "par où commencer ?" a la resolution avec confiance.',
  },
  'home.steps.s1.label': { en: 'Step 01', fr: 'Etape 01' },
  'home.steps.s1.title': { en: 'Take the diagnostic', fr: 'Passe le diagnostic' },
  'home.steps.s1.desc': {
    en: 'A short adaptive quiz pinpoints your strengths, gaps, and the exact concept to start with.',
    fr: 'Un court quiz adaptatif identifie tes points forts, tes lacunes, et le concept exact pour commencer.',
  },
  'home.steps.s2.label': { en: 'Step 02', fr: 'Etape 02' },
  'home.steps.s2.title': { en: 'Follow your path', fr: 'Suis ton parcours' },
  'home.steps.s2.desc': {
    en: 'The knowledge graph orders concepts by prerequisites, so each new lesson builds on what you already know.',
    fr: 'Le graphe de connaissances ordonne les concepts par prerequis : chaque lecon repose sur ce que tu sais deja.',
  },
  'home.steps.s3.label': { en: 'Step 03', fr: 'Etape 03' },
  'home.steps.s3.title': { en: 'Practice with verified math', fr: 'Pratique avec des maths verifiees' },
  'home.steps.s3.desc': {
    en: 'Adaptive quizzes track your mastery; the AI tutor explains anything unclear, with formulas verified by SymPy.',
    fr: 'Les quiz adaptatifs suivent ta maitrise ; le tuteur IA explique toute zone d ombre, formules verifiees par SymPy.',
  },

  'home.cta.ready': { en: 'Ready to master the math?', fr: 'Pret a maitriser les maths ?' },
  'home.cta.readySub': {
    en: 'Create your free account in 30 seconds — your diagnostic starts right after.',
    fr: 'Cree ton compte gratuit en 30 secondes — ton diagnostic commence juste apres.',
  },
  'home.cta.start': { en: 'Start free', fr: 'Commencer gratuitement' },

  'auth.register.title': { en: 'Create your account', fr: 'Creer ton compte' },
  'auth.register.subtitle': {
    en: 'Choose your learning language to continue. This choice is required.',
    fr: "Choisis ta langue d'apprentissage pour continuer. Ce choix est obligatoire.",
  },
  'auth.login.title': { en: 'Welcome back', fr: 'Bon retour' },
  'auth.login.subtitle': { en: 'Sign in to continue your adaptive path.', fr: 'Connecte-toi pour continuer ton parcours adaptatif.' },
  'auth.langPrompt': {
    en: 'Select your language to continue. This choice is required.',
    fr: 'Choisis ta langue pour continuer. Ce choix est obligatoire.',
  },
  'auth.error.langRequired': {
    en: 'Please select a language before continuing.',
    fr: 'Merci de choisir une langue avant de continuer.',
  },
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

  // Erreur login enrichie : titre + sous-message + 2 CTA d'aide
  'auth.error.login.title': {
    en: "We couldn't sign you in",
    fr: 'Connexion impossible',
  },
  'auth.error.login.body': {
    en: 'The email or password is incorrect, or this account does not exist yet.',
    fr: "L'email ou le mot de passe est incorrect, ou ce compte n'existe pas encore.",
  },
  'auth.error.login.tipNoAccount': {
    en: "Don't have an account yet?",
    fr: 'Pas encore de compte ?',
  },
  'auth.error.login.tipForgot': {
    en: 'Forgot your password?',
    fr: 'Mot de passe oublie ?',
  },
  'auth.error.login.actionRegister': {
    en: 'Create one in 30 seconds',
    fr: 'Cree-en un en 30 secondes',
  },
  'auth.error.login.actionForgot': {
    en: 'Reset it here',
    fr: 'Reinitialise-le ici',
  },

  // ============================================================
  // Phase 3 : email verification + forgot password + reset password
  // ============================================================
  'auth.forgotLink': { en: 'Forgot password?', fr: 'Mot de passe oublie ?' },

  'auth.verify.title': { en: 'Email verification', fr: "Verification de l'email" },
  'auth.verify.checking': { en: 'Checking your verification link...', fr: 'Verification du lien en cours...' },
  'auth.verify.success': { en: 'Your account is now verified.', fr: 'Ton compte est maintenant verifie.' },
  'auth.verify.error': { en: 'Verification link invalid or expired.', fr: 'Lien de verification invalide ou expire.' },
  'auth.verify.goLogin': { en: 'Go to sign in', fr: 'Aller a la connexion' },

  'auth.unverifiedBanner.text': {
    en: 'Your email is not verified yet. Check your inbox for the verification link.',
    fr: "Ton email n'est pas encore verifie. Verifie ta boite de reception pour le lien.",
  },
  'auth.unverifiedBanner.resend': { en: 'Resend email', fr: "Renvoyer l'email" },
  'auth.unverifiedBanner.resent': { en: 'Verification email sent.', fr: 'Email de verification envoye.' },

  'auth.forgot.title': { en: 'Reset your password', fr: 'Reinitialise ton mot de passe' },
  'auth.forgot.intro': {
    en: 'Enter your email and we will send you a reset link.',
    fr: 'Entre ton email, nous t enverrons un lien de reinitialisation.',
  },
  'auth.forgot.submit': { en: 'Send reset link', fr: 'Envoyer le lien' },
  'auth.forgot.sending': { en: 'Sending...', fr: 'Envoi en cours...' },
  'auth.forgot.successTitle': { en: 'Check your inbox', fr: 'Verifie ta boite mail' },
  'auth.forgot.successBody': {
    en: 'A reset link has been sent. The link is valid for 1 hour.',
    fr: 'Un lien de reinitialisation a ete envoye. Il est valide 1 heure.',
  },
  'auth.forgot.notFoundTitle': {
    en: "Account doesn't exist",
    fr: "Ce compte n'existe pas",
  },
  'auth.forgot.notFoundBody': {
    en: 'No account found with this email. Create one to get started.',
    fr: "Aucun compte trouve avec cet email. Cree-en un pour commencer.",
  },
  'auth.forgot.notFoundCta': { en: 'Create an account', fr: 'Creer un compte' },
  'auth.forgot.tryAnother': { en: 'Try another email', fr: 'Essayer un autre email' },
  'auth.forgot.backToLogin': { en: 'Back to sign in', fr: 'Retour a la connexion' },

  'auth.reset.title': { en: 'Choose a new password', fr: 'Choisis un nouveau mot de passe' },
  'auth.reset.newPassword': { en: 'New password', fr: 'Nouveau mot de passe' },
  'auth.reset.confirmPassword': { en: 'Confirm password', fr: 'Confirme le mot de passe' },
  'auth.reset.submit': { en: 'Reset password', fr: 'Reinitialiser' },
  'auth.reset.success': {
    en: 'Password updated. You can sign in with your new password.',
    fr: 'Mot de passe mis a jour. Tu peux te connecter avec le nouveau.',
  },
  'auth.reset.errorMismatch': {
    en: 'The two passwords do not match.',
    fr: 'Les deux mots de passe ne correspondent pas.',
  },
  'auth.reset.errorMinLength': {
    en: 'Password must be at least 8 characters.',
    fr: 'Le mot de passe doit faire au moins 8 caracteres.',
  },
  'auth.reset.errorGeneric': {
    en: 'Reset failed. The link may be expired.',
    fr: 'Echec de la reinitialisation. Le lien est peut-etre expire.',
  },
  'auth.reset.intro': {
    en: 'Pick something strong you can remember. Both fields must match.',
    fr: 'Choisis quelque chose de solide que tu peux retenir. Les deux champs doivent correspondre.',
  },
  'auth.reset.sending': { en: 'Saving…', fr: 'Enregistrement…' },
  'auth.reset.successTitle': { en: 'Password updated', fr: 'Mot de passe mis a jour' },
  'auth.reset.successBody': {
    en: 'You can now sign in with your new password.',
    fr: 'Tu peux maintenant te connecter avec ton nouveau mot de passe.',
  },
  'auth.reset.errorTitle': { en: 'Link invalid or expired', fr: 'Lien invalide ou expire' },
  'auth.reset.errorBody': {
    en: 'Request a new reset link to continue.',
    fr: 'Demande un nouveau lien pour continuer.',
  },
  'auth.reset.requestNewLink': { en: 'Request a new link', fr: 'Demander un nouveau lien' },
  'auth.reset.strengthWeak':   { en: 'Weak',   fr: 'Faible' },
  'auth.reset.strengthMedium': { en: 'Medium', fr: 'Moyen' },
  'auth.reset.strengthGood':   { en: 'Good',   fr: 'Bon' },
  'auth.reset.strengthStrong': { en: 'Strong', fr: 'Excellent' },
  'auth.backToHome': { en: 'Back to home', fr: 'Retour a l\'accueil' },
  'auth.langInfo.title': {
    en: 'Your selected language will be used for:',
    fr: 'La langue choisie sera utilisee pour :',
  },
  'auth.langInfo.quiz': {
    en: 'The level-detection quiz used to personalize your path',
    fr: 'Le quiz de detection de niveau qui personnalise ton parcours',
  },
  'auth.langInfo.content': {
    en: 'Course content, exercises and reading materials',
    fr: 'Le contenu des cours, exercices et lectures',
  },
  'auth.langInfo.tutor': {
    en: 'AI tutor explanations and follow-up answers',
    fr: 'Les explications du tuteur IA et ses reponses',
  },
  'auth.langInfo.ui': {
    en: 'The whole interface (menus, buttons, messages)',
    fr: 'Toute l\'interface (menus, boutons, messages)',
  },
  'auth.langInfo.footnoteLogin': {
    en: 'You can change this at any time from the sidebar.',
    fr: 'Tu pourras la changer a tout moment depuis la barre laterale.',
  },
  'auth.langInfo.footnoteRegister': {
    en: 'The level-detection quiz starts right after sign-up — pick the language you\'re most comfortable with.',
    fr: 'Le quiz de detection de niveau demarre juste apres l\'inscription — choisis la langue dans laquelle tu es le plus a l\'aise.',
  },
  'auth.langInfo.quizMain': {
    en: 'Your level-detection quiz will be in this language.',
    fr: 'Ton quiz de detection de niveau sera dans cette langue.',
  },
  'auth.langInfo.quizNote': {
    en: 'You can change the language anytime once you are inside.',
    fr: 'Tu peux changer la langue a tout moment une fois connecte.',
  },

  'content.animation.caption': {
    en: 'Visual explanation generated with Manim',
    fr: 'Explication visuelle generee avec Manim',
  },
  // Bandeau cliquable au-dessus du cours qui devoile la video Manim.
  // Le wording evite le sec "Show animation" : on parle du contenu
  // ("animated demonstration" / "demonstration animee") plutot que de
  // l'action UI ("show"), c'est plus engageant et plus clair.
  'content.animation.toggle.title': {
    en: 'Watch the animated demonstration',
    fr: 'Voir la demonstration animee',
  },
  'content.animation.toggle.sub': {
    en: 'A short visual walkthrough of this method',
    fr: 'Une courte visualisation de cette methode',
  },

  'dashboard.title': { en: 'Dashboard', fr: 'Tableau de bord' },
  'dashboard.subtitle': { en: 'Your progress, priorities and next learning actions.', fr: 'Ta progression, tes priorites et les prochaines actions.' },
  'dashboard.hero.kicker': { en: 'Adaptive learning cockpit', fr: 'Cockpit apprentissage adaptatif' },
  'dashboard.hero.greeting': { en: 'Hi', fr: 'Bonjour' },
  'dashboard.hero.sub': {
    en: 'A clear view to pick up the right concept, launch an adaptive quiz and get help right when you need it.',
    fr: "Une vue claire pour reprendre le bon concept, lancer un quiz adapte et obtenir de l'aide au bon moment.",
  },
  'dashboard.hero.level': { en: 'Level', fr: 'Niveau' },
  'dashboard.hero.mode': { en: 'Mode', fr: 'Mode' },
  'dashboard.hero.modeValue': { en: 'Personalized', fr: 'Personnalise' },
  'dashboard.hero.cta.quiz': { en: 'Generate a quiz', fr: 'Generer un quiz' },
  'dashboard.hero.cta.path': { en: 'View learning path', fr: 'Voir le parcours' },
  'dashboard.mastery.title': { en: 'Overall mastery', fr: 'Maitrise globale' },
  'dashboard.mastery.caption': { en: 'Based on validated concepts.', fr: 'Basee sur les concepts valides.' },
  'dashboard.mastery.mastered': { en: 'Mastered', fr: 'Maitrises' },
  'dashboard.mastery.progress': { en: 'In progress', fr: 'En cours' },
  'dashboard.mastery.next': { en: 'Next', fr: 'A venir' },
  'dashboard.metric.total': { en: 'Total concepts', fr: 'Concepts totaux' },
  'dashboard.metric.mastered': { en: 'Mastered', fr: 'Maitrises' },
  'dashboard.metric.inprogress': { en: 'In progress', fr: 'En cours' },
  'dashboard.metric.todiscover': { en: 'To discover', fr: 'A decouvrir' },
  'dashboard.metric.trend.scope': { en: 'Scope', fr: 'Etendue' },
  'dashboard.metric.trend.active': { en: 'Active', fr: 'Actif' },
  'dashboard.metric.trend.queued': { en: 'Queued', fr: 'En file' },
  'dashboard.priorities.title': { en: 'Review priorities', fr: 'Priorites de revision' },
  'dashboard.priorities.subtitle': { en: 'The weak spots to work on first.', fr: 'Les points faibles a travailler en premier.' },
  'dashboard.priorities.courses': { en: 'Courses', fr: 'Cours' },
  'dashboard.priorities.empty': { en: 'No critical weakness for now.', fr: 'Aucune faiblesse critique pour le moment.' },
  'dashboard.priorities.needsPractice': { en: 'Needs practice', fr: 'A pratiquer' },
  'dashboard.priorities.mastery': { en: 'mastery', fr: 'de maitrise' },
  'dashboard.next.title': { en: 'Next step', fr: 'Prochaine etape' },
  'dashboard.next.subtitle': { en: 'Concepts ready to advance.', fr: 'Concepts prets pour avancer.' },
  'dashboard.next.empty': { en: 'Finish ongoing reviews to unlock the next steps.', fr: 'Termine les revisions en cours pour debloquer la suite.' },
  'dashboard.next.module': { en: 'Module', fr: 'Module' },
  'dashboard.next.level': { en: 'Level', fr: 'Niveau' },
  'dashboard.next.ready': { en: 'Ready', fr: 'Pret' },
  'dashboard.quick.concepts.title': { en: 'Explore concepts', fr: 'Explorer les concepts' },
  'dashboard.quick.concepts.desc': { en: 'See modules, levels and dependencies.', fr: 'Voir les modules, niveaux et dependances.' },
  'dashboard.quick.train.title': { en: 'Practice', fr: "S'entrainer" },
  'dashboard.quick.train.desc': { en: 'Generate a quiz targeted on a concept.', fr: 'Generer un quiz cible sur un concept.' },
  'dashboard.quick.tutor.title': { en: 'Ask the tutor', fr: 'Demander au tuteur' },
  'dashboard.quick.tutor.desc': { en: 'Get a tailored explanation.', fr: 'Obtenir une explication adaptee.' },
  'dashboard.error.firstQuiz': { en: 'Run a first quiz to build your progress profile.', fr: 'Lance un premier quiz pour creer ton profil de progression.' },
  'dashboard.error.afterDiagnostic': { en: 'Recommendations will appear after your diagnostic.', fr: 'Les recommandations apparaitront apres ton diagnostic.' },
  'dashboard.student.fallback': { en: 'Student', fr: 'Etudiant' },

  'concepts.subtitle': { en: 'Knowledge graph and module structure', fr: 'Graphe de connaissances et structure des modules' },
  'concepts.title': { en: 'Concept map', fr: 'Carte des concepts' },
  'concepts.intro': {
    en: 'A structured view of modules, levels and key notions of numerical analysis.',
    fr: "Une vue structuree des modules, niveaux et notions importantes de l'analyse numerique.",
  },
  'concepts.filter.all': { en: 'All concepts', fr: 'Tous les concepts' },
  'concepts.overview.concepts': { en: 'Concepts', fr: 'Concepts' },
  'concepts.overview.modules': { en: 'Modules', fr: 'Modules' },
  'concepts.overview.maxLevel': { en: 'Max level', fr: 'Niveau max' },
  'concepts.empty': { en: 'No concepts found.', fr: 'Aucun concept trouve.' },
  'concepts.card.fallback': { en: 'Concept', fr: 'Concept' },
  'concepts.card.level': { en: 'Level', fr: 'Niveau' },
  'concepts.card.desc.fallback': {
    en: 'Core concept in numerical analysis and scientific computing.',
    fr: "Concept central de l'analyse numerique et du calcul scientifique.",
  },
  'concepts.error.backend': {
    en: 'Backend not connected. Start the API service and reload this page.',
    fr: "Backend non connecte. Demarre l'API et recharge cette page.",
  },

  'tutor.title': { en: 'AI tutor', fr: 'Tuteur IA' },
  'tutor.subtitle': {
    en: 'Ask questions and receive adaptive explanations.',
    fr: 'Pose tes questions et recois des explications adaptees.',
  },
  'tutor.newSession': { en: 'New conversation', fr: 'Nouvelle conversation' },
  'tutor.welcome.title': { en: 'AI tutor — Numerical analysis', fr: 'Tuteur IA — Analyse numerique' },
  'tutor.welcome.line1': {
    en: 'Ask any question about numerical analysis.',
    fr: "Pose tes questions sur l'analyse numerique.",
  },
  'tutor.welcome.line2': {
    en: 'Answers are adapted to your current level.',
    fr: 'Les reponses sont adaptees a ton niveau actuel.',
  },
  'tutor.start': { en: 'Start a conversation', fr: 'Commencer une conversation' },
  'tutor.session.label': { en: 'Conversation', fr: 'Conversation' },
  'tutor.session.new': { en: 'New session', fr: 'Nouvelle session' },
  'tutor.input.placeholder': {
    en: 'Ask your question about numerical analysis...',
    fr: "Pose ta question sur l'analyse numerique...",
  },
  'tutor.empty.title': { en: 'No conversation.', fr: 'Aucune conversation.' },
  'tutor.empty.hint': {
    en: 'Click "New conversation" to start.',
    fr: 'Clique sur "Nouvelle conversation" pour commencer.',
  },
  'tutor.verified.true': { en: 'Math verified by SymPy', fr: 'Maths verifiees par SymPy' },
  'tutor.verified.false': { en: 'Formulas not verified', fr: 'Formules non verifiees' },
  'tutor.complexity.simplified': { en: 'Simplified', fr: 'Simplifie' },
  'tutor.complexity.standard': { en: 'Standard', fr: 'Standard' },
  'tutor.complexity.rigorous': { en: 'Rigorous', fr: 'Rigoureux' },
  'tutor.error.send': {
    en: 'Unable to reach the tutor. Try again in a moment.',
    fr: 'Impossible de joindre le tuteur. Reessaie dans un instant.',
  },

  // Selecteur LLM (picker IA)
  'tutor.picker.button': {
    en: 'AI model',
    fr: 'Modele IA',
  },
  'tutor.picker.title': {
    en: 'Choose your AI model',
    fr: 'Choisis ton modele IA',
  },
  'tutor.picker.subtitle': {
    en: 'Each model has its own strengths. Pick the one that fits your needs.',
    fr: 'Chaque modele a ses points forts. Choisis celui qui te convient.',
  },
  'tutor.picker.select': {
    en: 'Select this model',
    fr: 'Choisir ce modele',
  },
  'tutor.picker.selected': {
    en: 'Currently selected',
    fr: 'Actuellement selectionne',
  },
  'tutor.picker.cancel': {
    en: 'Cancel',
    fr: 'Annuler',
  },
  'tutor.picker.save': {
    en: 'Save',
    fr: 'Enregistrer',
  },

  // Tags d'attributs (utilises sur les cards)
  'tutor.picker.tag.offline': {
    en: 'Works offline',
    fr: 'Fonctionne hors-ligne',
  },
  'tutor.picker.tag.online': {
    en: 'Internet required',
    fr: 'Internet requis',
  },
  'tutor.picker.tag.free': {
    en: 'Free',
    fr: 'Gratuit',
  },
  'tutor.picker.tag.paid': {
    en: 'Paid (per use)',
    fr: 'Payant (a l\'usage)',
  },
  'tutor.picker.tag.finetuned': {
    en: 'Fine-tuned',
    fr: 'Fine-tune',
  },
  'tutor.picker.tag.generic': {
    en: 'General-purpose',
    fr: 'Generaliste',
  },
  'tutor.picker.tag.rgpd': {
    en: 'GDPR-safe',
    fr: 'RGPD-safe',
  },
  'tutor.picker.tag.cloud': {
    en: 'Data sent to cloud',
    fr: 'Donnees envoyees au cloud',
  },
  'tutor.picker.tag.slow': {
    en: 'Slower (~15-30s)',
    fr: 'Plus lent (~15-30s)',
  },
  'tutor.picker.tag.fast': {
    en: 'Fast (~2-5s)',
    fr: 'Rapide (~2-5s)',
  },
  'tutor.picker.tag.qualityGood': {
    en: 'Good quality',
    fr: 'Bonne qualite',
  },
  'tutor.picker.tag.qualityExcellent': {
    en: 'Excellent quality',
    fr: 'Qualite excellente',
  },

  'learningPath.subtitle': {
    en: 'Recommended sequence based on mastery and prerequisites.',
    fr: 'Sequence recommandee selon la maitrise et les prerequis.',
  },
  'learningPath.overall': { en: 'Overall mastery', fr: 'Maitrise globale' },
  'learningPath.overall.caption': {
    en: 'Progress calculated from mastered concepts and current work.',
    fr: 'Progression calculee a partir des concepts maitrises et en cours.',
  },
  'learningPath.mastered': { en: 'Mastered', fr: 'Maitrises' },
  'learningPath.inprogress': { en: 'In progress', fr: 'En cours' },
  'learningPath.todiscover': { en: 'To discover', fr: 'A decouvrir' },
  'learningPath.conceptsMastered': { en: 'concepts mastered', fr: 'concepts maitrises' },
  'learningPath.percentComplete': { en: '% complete', fr: '% acheves' },
  'learningPath.prereqLocked': { en: 'Prerequisites not met', fr: 'Prerequis non satisfaits' },
  'learningPath.ready': { en: 'Ready to start', fr: 'Pret a commencer' },
  'learningPath.empty': {
    en: 'Take your first quiz to generate your personalized learning path.',
    fr: 'Passe ton premier quiz pour generer ton parcours personnalise.',
  },
  'learningPath.cta.quiz': { en: 'Go to quizzes', fr: 'Aller aux quiz' },

  'content.subtitle': {
    en: 'Multi-level lessons with mathematical notation.',
    fr: 'Cours multi-niveaux avec notation mathematique.',
  },
  'content.title': { en: 'Course content', fr: 'Cours' },
  'content.intro': {
    en: 'Multi-level educational content with simplified, standard, and rigorous explanations.',
    fr: 'Contenus educatifs multi-niveaux : explications simplifiee, standard et rigoureuse.',
  },
  'content.sidebar.title': { en: 'CONCEPTS', fr: 'CONCEPTS' },
  'content.empty.select': {
    en: 'Select a concept from the sidebar to view its content.',
    fr: 'Selectionne un concept dans la barre laterale pour voir son contenu.',
  },
  'content.level.simplified': { en: 'Simplified', fr: 'Simplifie' },
  'content.level.standard': { en: 'Standard', fr: 'Standard' },
  'content.level.rigorous': { en: 'Rigorous', fr: 'Rigoureux' },
  'content.empty.run': {
    en: 'No content available. Run python scripts/seed_content.py.',
    fr: 'Aucun contenu disponible. Execute python scripts/seed_content.py.',
  },
  'content.error.backend': { en: 'Backend not connected.', fr: 'Backend non connecte.' },
  'content.askTutor': { en: 'Ask the tutor', fr: 'Demander au tuteur' },
  'content.askTutor.hint': {
    en: 'Open the AI tutor with this concept and a ready-to-send question.',
    fr: "Ouvre le tuteur IA avec ce concept et une question prete a envoyer.",
  },
  'content.askTutor.prefill': {
    en: 'Explain {concept} to me in another way, with a clear example.',
    fr: "Explique-moi {concept} d'une autre facon, avec un exemple clair.",
  },

  'onboarding.badge': { en: 'Initial calibration', fr: 'Calibration initiale' },
  'onboarding.title': { en: 'Take your diagnostic quiz', fr: 'Passe ton quiz de diagnostic' },
  'onboarding.intro': {
    en: 'This short quiz estimates your starting level and tailors the path ahead.',
    fr: 'Ce court quiz estime ton niveau de depart et adapte ton parcours.',
  },
  'onboarding.facts.questions': { en: 'Questions', fr: 'Questions' },
  'onboarding.facts.modules': { en: 'Modules', fr: 'Modules' },
  'onboarding.facts.path': { en: 'Adaptive path', fr: 'Parcours adaptatif' },
  'onboarding.start': { en: 'Start diagnostic', fr: 'Demarrer le diagnostic' },
  'onboarding.loading.title': { en: 'Generating your diagnostic', fr: 'Generation de ton diagnostic' },
  'onboarding.loading.sub': {
    en: 'The quiz is being prepared from the concept graph.',
    fr: 'Le quiz est en cours de preparation depuis le graphe de concepts.',
  },
  'onboarding.quizTitle': { en: 'Diagnostic quiz', fr: 'Quiz de diagnostic' },
  'onboarding.scoring.title': { en: 'Scoring your diagnostic', fr: 'Correction de ton diagnostic' },
  'onboarding.scoring.sub': {
    en: 'Your profile and mastery map are being updated.',
    fr: 'Ton profil et ta carte de maitrise sont en cours de mise a jour.',
  },
  'onboarding.complete.title': { en: 'Diagnostic complete', fr: 'Diagnostic termine' },
  'onboarding.startingLevel': { en: 'Your starting level is', fr: 'Ton niveau de depart est' },
  'onboarding.strengths': { en: 'Strengths', fr: 'Points forts' },
  'onboarding.nextSteps': { en: 'Next steps', fr: 'Prochaines etapes' },
  'onboarding.cta.dashboard': { en: 'Go to dashboard', fr: 'Aller au tableau de bord' },
  'onboarding.cta.path': { en: 'View learning path', fr: 'Voir le parcours' },
  'onboarding.retry': { en: 'Try again', fr: 'Reessayer' },
  'onboarding.question.of': { en: 'Question {n} of {total}', fr: 'Question {n} sur {total}' },
  'onboarding.true': { en: 'True', fr: 'Vrai' },
  'onboarding.false': { en: 'False', fr: 'Faux' },
  'onboarding.openAnswer': { en: 'Write your answer here...', fr: 'Ecris ta reponse ici...' },
  'onboarding.previous': { en: 'Previous', fr: 'Precedent' },
  'onboarding.next': { en: 'Next', fr: 'Suivant' },
  'onboarding.finish': { en: 'Finish diagnostic', fr: 'Terminer le diagnostic' },
  'onboarding.startingLevelIs': { en: 'Your starting level is', fr: 'Ton niveau de depart est' },
  'onboarding.summary.fallback': {
    en: 'Your adaptive learning path is ready.',
    fr: 'Ton parcours adaptatif est pret.',
  },
  'onboarding.strengths.fallback': { en: 'Diagnostic completed', fr: 'Diagnostic termine' },
  'onboarding.next.fallback1': { en: 'Open your dashboard', fr: 'Ouvre ton tableau de bord' },
  'onboarding.next.fallback2': { en: 'Follow the recommended path', fr: 'Suis le parcours recommande' },

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

  // ============================================================
  // Double mode pedagogique : Parcours (adaptive) vs Entrainement (practice)
  // ============================================================
  'quiz.mode.adaptive.title': { en: 'Path quiz', fr: 'Quiz du parcours' },
  'quiz.mode.adaptive.tagline': {
    en: 'The system picks the right difficulty for you and updates your mastery.',
    fr: 'Le systeme choisit la bonne difficulte et met a jour ta maitrise.',
  },
  'quiz.mode.adaptive.cta': { en: 'Continue my path', fr: 'Continuer mon parcours' },
  'quiz.mode.adaptive.badge': { en: 'Counts towards progression', fr: 'Compte dans la progression' },

  'quiz.mode.practice.title': { en: 'Free practice', fr: 'Entrainement libre' },
  'quiz.mode.practice.tagline': {
    en: 'Pick any concept and difficulty. Useful for revision but does NOT affect your mastery.',
    fr: 'Choisis le concept et la difficulte que tu veux. Utile pour reviser mais N\'AFFECTE PAS ta maitrise.',
  },
  'quiz.mode.practice.cta': { en: 'Start practice', fr: "Demarrer l'entrainement" },
  'quiz.mode.practice.badge': { en: 'No impact on progression', fr: 'Pas d\'impact sur la progression' },
  'quiz.mode.practice.warn': {
    en: 'Free practice mode — this attempt is for revision only and does not change your mastery.',
    fr: "Mode entrainement libre — cette tentative sert a reviser, elle ne modifie pas ta maitrise.",
  },

  'quiz.results.deltaMastery': { en: 'Mastery updated for', fr: 'Maitrise mise a jour pour' },
  'quiz.results.noDelta': { en: 'No mastery change (practice mode).', fr: 'Pas de changement de maitrise (mode entrainement).' },
  'quiz.results.modeAdaptive': { en: 'Path attempt', fr: 'Tentative du parcours' },
  'quiz.results.modePractice': { en: 'Practice attempt', fr: "Tentative d'entrainement" },
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
  return value === 'fr' ? 'fr' : FALLBACK_LANG
}

export function getStoredUser(): { langue_preferee?: Lang; niveau_actuel?: string; nom_complet?: string; id?: number } | null {
  try {
    const raw = localStorage.getItem('user')
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

/**
 * Retourne la langue actuellement choisie par l'utilisateur.
 * Si aucune langue n'a encore été choisie (avant login/register),
 * retourne la langue de secours pour permettre le rendu de la page de choix.
 * Pour vérifier qu'un choix explicite a été fait, utiliser hasChosenLang().
 */
export function getLang(): Lang {
  const stored = localStorage.getItem('app_lang')
  if (stored === 'fr' || stored === 'en') return stored
  const fromUser = getStoredUser()?.langue_preferee
  if (fromUser === 'fr' || fromUser === 'en') return fromUser
  return FALLBACK_LANG
}

/**
 * True si l'utilisateur a explicitement choisi une langue (via login/register)
 * et qu'elle est persistée dans localStorage. Aucune détection automatique
 * de navigator.language n'est effectuée — le choix doit être manuel.
 */
export function hasChosenLang(): boolean {
  const stored = localStorage.getItem('app_lang')
  return stored === 'en' || stored === 'fr'
}

export function clearLang(): void {
  localStorage.removeItem('app_lang')
  document.documentElement.removeAttribute('lang')
}

export function setLang(lang: Lang): void {
  if (lang !== 'en' && lang !== 'fr') return
  localStorage.setItem('app_lang', lang)
  document.documentElement.lang = lang

  const user = getStoredUser()
  if (user) {
    localStorage.setItem('user', JSON.stringify({ ...user, langue_preferee: lang }))
  }
}

/**
 * À appeler au démarrage et après login : applique la langue stockée
 * (ou celle du profil utilisateur). Ne définit JAMAIS de langue par défaut
 * si rien n'est stocké — le choix au login/register reste obligatoire.
 */
export function initLangFromUser(): Lang | null {
  const stored = localStorage.getItem('app_lang')
  if (stored === 'fr' || stored === 'en') {
    document.documentElement.lang = stored
    return stored
  }
  const fromUser = getStoredUser()?.langue_preferee
  if (fromUser === 'fr' || fromUser === 'en') {
    setLang(fromUser)
    return fromUser
  }
  // Aucune langue choisie : on ne fixe rien, le formulaire de login
  // ou register imposera le choix.
  return null
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
