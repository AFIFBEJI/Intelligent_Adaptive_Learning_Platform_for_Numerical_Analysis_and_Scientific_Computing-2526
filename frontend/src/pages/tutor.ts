// ============================================================
// Tutor Page — Chat IA avec Glassmorphism + MathJax
// ============================================================
// C'est quoi ce fichier ?
//
// C'est la page du TUTEUR IA. C'est ici que l'étudiant
// discute avec le tuteur IA local pour poser des questions
// sur l'analyse numérique.
//
// L'interface ressemble à WhatsApp/ChatGPT :
//   - À GAUCHE : liste des sessions (conversations passées)
//   - À DROITE : la conversation active avec les messages
//   - EN BAS : la zone de saisie pour écrire sa question
//
// FONCTIONNALITÉS SPÉCIALES :
//   - Rendu LaTeX avec MathJax (les formules sont jolies)
//   - Badge "Vérifié par SymPy" sur les réponses du tuteur
//   - Indicateur de niveau (simplifié/standard/rigoureux)
//   - Animation "en train d'écrire..." pendant que le tuteur répond
//
// C'est quoi MathJax ?
// C'est une librairie JavaScript qui transforme le LaTeX en
// jolies formules mathématiques dans le navigateur.
// Ex: $\frac{a}{b}$ → affiche une vraie fraction a/b
// On charge MathJax depuis un CDN (serveur externe gratuit).
// ============================================================

import { api } from '../api'
import type { TutorSession, TutorMessage, TutorAskResponse } from '../api'
import { createAppShell } from '../components/app-shell'

export function TutorPage(): HTMLElement {
  // ============================================================
  // ÉTAPE 1 : Initialisation
  // ============================================================
  // On crée le conteneur principal et on récupère les infos
  // de l'étudiant connecté depuis localStorage.

  const shell = createAppShell({
    activeRoute: '/tutor',
    pageTitle: 'AI tutor',
    pageSubtitle: 'Ask questions and receive adaptive explanations',
    fullBleed: true,
  })
  const container = document.createElement('div')
  const token = localStorage.getItem('token')
  if (token) api.setToken(token)

  // Variables d'état (l'état actuel de la page)
  let sessions: TutorSession[] = []        // Liste des sessions
  let activeSessionId: number | null = null // Session actuellement ouverte
  let messages: TutorMessage[] = []        // Messages de la session active
  let isLoading = false                     // Reponse du tuteur en cours

  // ============================================================
  // ÉTAPE 2 : Structure HTML + CSS
  // ============================================================
  // On utilise le même style glassmorphism que les autres pages
  // (fond sombre, bordures semi-transparentes, blur, etc.)

  const main = document.createElement('div')
  main.innerHTML = `
    <style>
      /* ---- Animations ---- */
      @keyframes slideUp { from{opacity:0;transform:translateY(25px)} to{opacity:1;transform:translateY(0)} }
      @keyframes fadeIn { from{opacity:0} to{opacity:1} }
      @keyframes slideIn { from{opacity:0;transform:translateX(-10px)} to{opacity:1;transform:translateX(0)} }
      @keyframes popIn { from{opacity:0;transform:scale(0.9)} to{opacity:1;transform:scale(1)} }
      @keyframes typing { 0%{opacity:0.3} 50%{opacity:1} 100%{opacity:0.3} }
      @keyframes shimmer { 0%{background-position:-200% 0} 100%{background-position:200% 0} }

      /* ---- Layout principal ---- */
      /* Le chat prend toute la hauteur de l'écran moins la navbar (64px) */
      .tutor-page {
        display:flex;
        height:100vh;
        position:relative;z-index:1;
        overflow:hidden;
      }

      /* ---- Sidebar : liste des sessions (à gauche) ---- */
      .tutor-sidebar {
        width:300px;
        min-width:300px;
        background:rgba(10,15,30,0.6);
        border-right:1px solid rgba(255,255,255,0.06);
        display:flex;flex-direction:column;
        backdrop-filter:blur(20px);
        animation:slideIn 0.4s ease;
      }

      .sidebar-header {
        padding:1.25rem;
        border-bottom:1px solid rgba(255,255,255,0.06);
      }

      .sidebar-title {
        font-size:1.1rem;font-weight:800;
        background:linear-gradient(135deg,#f1f5f9 0%,#38bdf8 50%,#818cf8 100%);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
        margin-bottom:0.75rem;
      }

      /* Bouton "Nouvelle conversation" */
      .new-session-btn {
        width:100%;padding:0.65rem 1rem;
        background:linear-gradient(135deg,rgba(56,189,248,0.15),rgba(129,140,248,0.15));
        border:1px solid rgba(56,189,248,0.25);
        border-radius:12px;color:#38bdf8;
        font-weight:600;font-size:0.85rem;
        cursor:pointer;transition:all 0.3s;
        display:flex;align-items:center;justify-content:center;gap:0.5rem;
      }
      .new-session-btn:hover {
        background:linear-gradient(135deg,rgba(56,189,248,0.25),rgba(129,140,248,0.25));
        border-color:rgba(56,189,248,0.5);
        transform:translateY(-1px);
        box-shadow:0 4px 15px rgba(56,189,248,0.2);
      }

      /* Liste des sessions */
      .session-list {
        flex:1;overflow-y:auto;padding:0.5rem;
      }
      .session-list::-webkit-scrollbar { width:4px; }
      .session-list::-webkit-scrollbar-thumb { background:rgba(56,189,248,0.2);border-radius:4px; }

      .session-item {
        padding:0.85rem 1rem;
        border-radius:12px;cursor:pointer;
        transition:all 0.2s;margin-bottom:0.25rem;
        border:1px solid transparent;
      }
      .session-item:hover {
        background:rgba(255,255,255,0.04);
        border-color:rgba(255,255,255,0.06);
      }
      .session-item.active {
        background:rgba(56,189,248,0.08);
        border-color:rgba(56,189,248,0.2);
      }
      .session-item-title {
        font-size:0.85rem;font-weight:600;color:#e2e8f0;
        margin-bottom:0.25rem;
        white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
      }
      .session-item-meta {
        font-size:0.72rem;color:#64748b;
        display:flex;justify-content:space-between;
      }

      /* ---- Zone de chat (à droite) ---- */
      .chat-area {
        flex:1;display:flex;flex-direction:column;
        background:rgba(5,10,25,0.4);
        animation:fadeIn 0.5s ease;
      }

      /* En-tête du chat */
      .chat-header {
        padding:1rem 1.5rem;
        border-bottom:1px solid rgba(255,255,255,0.06);
        background:rgba(10,15,30,0.5);
        backdrop-filter:blur(10px);
        display:flex;align-items:center;justify-content:space-between;
      }
      .chat-header-info h3 {
        font-size:1rem;font-weight:700;color:#f1f5f9;margin:0 0 0.2rem 0;
      }
      .chat-header-info span {
        font-size:0.75rem;color:#64748b;
      }

      /* Badges de niveau */
      .level-badge {
        font-size:0.68rem;font-weight:700;
        padding:0.25rem 0.7rem;border-radius:20px;
        letter-spacing:0.04em;
      }
      .level-simplified {
        background:rgba(52,211,153,0.12);color:#34d399;
        border:1px solid rgba(52,211,153,0.25);
      }
      .level-standard {
        background:rgba(56,189,248,0.12);color:#38bdf8;
        border:1px solid rgba(56,189,248,0.25);
      }
      .level-rigorous {
        background:rgba(168,85,247,0.12);color:#a855f7;
        border:1px solid rgba(168,85,247,0.25);
      }

      /* Zone des messages */
      .messages-container {
        flex:1;overflow-y:auto;padding:1.5rem;
        display:flex;flex-direction:column;gap:1rem;
        min-height:0;
      }
      .messages-container::-webkit-scrollbar { width:6px; }
      .messages-container::-webkit-scrollbar-thumb { background:rgba(56,189,248,0.15);border-radius:6px; }

      /* Message individuel */
      .message {
        max-width:80%;animation:popIn 0.3s ease;
      }
      .message-student {
        align-self:flex-end;
      }
      .message-tutor {
        align-self:flex-start;
      }

      .message-bubble {
        padding:1rem 1.25rem;
        border-radius:18px;
        font-size:0.9rem;line-height:1.7;
        word-wrap:break-word;
      }

      /* Bulle de l'étudiant (bleu, à droite) */
      .message-student .message-bubble {
        background:linear-gradient(135deg,rgba(56,189,248,0.2),rgba(129,140,248,0.2));
        border:1px solid rgba(56,189,248,0.25);
        color:#e2e8f0;
        border-bottom-right-radius:6px;
      }

      /* Bulle du tuteur (sombre, à gauche) */
      .message-tutor .message-bubble {
        background:rgba(255,255,255,0.04);
        border:1px solid rgba(255,255,255,0.08);
        color:#cbd5e1;
        border-bottom-left-radius:6px;
      }

      /* Badge de vérification SymPy */
      .verification-badge {
        display:inline-flex;align-items:center;gap:0.35rem;
        font-size:0.7rem;font-weight:600;
        padding:0.2rem 0.6rem;border-radius:8px;
        margin-top:0.5rem;
      }
      .verified-true {
        background:rgba(52,211,153,0.12);color:#34d399;
        border:1px solid rgba(52,211,153,0.25);
      }
      .verified-false {
        background:rgba(251,191,36,0.12);color:#fbbf24;
        border:1px solid rgba(251,191,36,0.25);
      }

      .message-time {
        font-size:0.65rem;color:#475569;
        margin-top:0.3rem;
        padding:0 0.5rem;
      }
      .message-student .message-time { text-align:right; }

      /* Animation "en train d'écrire" */
      .typing-indicator {
        display:flex;gap:0.3rem;padding:1rem 1.25rem;
        align-self:flex-start;
      }
      .typing-dot {
        width:8px;height:8px;border-radius:50%;
        background:rgba(56,189,248,0.5);
        animation:typing 1.2s infinite;
      }
      .typing-dot:nth-child(2) { animation-delay:0.2s; }
      .typing-dot:nth-child(3) { animation-delay:0.4s; }

      /* Écran d'accueil (pas de session sélectionnée) */
      .welcome-screen {
        flex:1;display:flex;flex-direction:column;
        align-items:center;justify-content:center;
        padding:2rem;text-align:center;
        animation:fadeIn 0.6s ease;
      }
      .welcome-icon {
        width:64px;height:64px;margin-bottom:1.5rem;
        display:grid;place-items:center;
        border-radius:var(--radius-md);
        color:#ffffff;
        background:var(--brand-gradient);
        font-size:var(--text-lg);
        font-weight:var(--font-weight-extrabold);
        box-shadow:var(--shadow-glow-brand);
      }
      .welcome-title {
        font-size:1.5rem;font-weight:800;
        background:linear-gradient(135deg,#f1f5f9 0%,#38bdf8 50%,#818cf8 100%);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
        margin-bottom:0.5rem;
      }
      .welcome-sub { color:#64748b;font-size:0.9rem;max-width:400px;line-height:1.6; }

      /* Zone de saisie (en bas) — TOUJOURS visible */
      .input-area {
        padding:1rem 1.5rem;
        border-top:1px solid rgba(255,255,255,0.06);
        background:rgba(10,15,30,0.5);
        backdrop-filter:blur(10px);
        flex-shrink:0;
      }
      .input-row {
        display:flex;gap:0.75rem;align-items:flex-end;
      }
      .input-wrapper {
        flex:1;position:relative;
      }
      .input-field {
        width:100%;padding:0.85rem 1.15rem;
        background:rgba(255,255,255,0.04);
        border:1px solid rgba(255,255,255,0.08);
        border-radius:16px;color:#e2e8f0;
        font-size:0.9rem;outline:none;
        transition:all 0.3s;resize:none;
        font-family:inherit;
        min-height:48px;max-height:120px;
      }
      .input-field::placeholder { color:#475569; }
      .input-field:focus {
        border-color:rgba(56,189,248,0.4);
        box-shadow:0 0 0 3px rgba(56,189,248,0.08);
      }

      .send-btn {
        width:48px;height:48px;
        background:linear-gradient(135deg,#38bdf8,#818cf8);
        border:none;border-radius:14px;
        color:white;cursor:pointer;
        display:flex;align-items:center;justify-content:center;
        transition:all 0.3s;flex-shrink:0;
      }
      .send-btn:hover:not(:disabled) {
        transform:translateY(-2px);
        box-shadow:0 6px 20px rgba(56,189,248,0.35);
      }
      .send-btn:disabled {
        opacity:0.4;cursor:not-allowed;
      }
      .send-btn svg { width:20px;height:20px; }

      /* Squelette de chargement */
      .skeleton {
        background:linear-gradient(90deg,rgba(255,255,255,0.03) 25%,rgba(255,255,255,0.06) 50%,rgba(255,255,255,0.03) 75%);
        background-size:200% 100%;
        animation:shimmer 1.5s infinite;
        border-radius:12px;
      }

      /* ---- Responsive (mobile) ---- */
      @media(max-width:768px) {
        .tutor-sidebar { width:100%;min-width:100%;position:absolute;left:-100%;
          transition:left 0.3s;z-index:10;height:100vh; }
        .tutor-sidebar.open { left:0; }
        .chat-area { width:100%; }
        .message { max-width:90%; }
        .mobile-toggle {
          display:flex !important;
        }
      }
      .mobile-toggle { display:none;cursor:pointer;padding:0.4rem;border-radius:8px;
        background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);
        color:#94a3b8;transition:all 0.2s; }
      .mobile-toggle:hover { background:rgba(255,255,255,0.1); }

      /* Style pour le rendu LaTeX (MathJax) */
      .message-bubble .MathJax { font-size:1em !important; }
      .message-bubble p { margin:0.5rem 0; }
      .message-bubble ol, .message-bubble ul { margin:0.5rem 0;padding-left:1.5rem; }
      .message-bubble code {
        background:rgba(0,0,0,0.3);padding:0.15rem 0.4rem;
        border-radius:4px;font-size:0.85em;color:#38bdf8;
      }
      .message-bubble pre {
        background:rgba(0,0,0,0.3);padding:0.8rem;
        border-radius:8px;overflow-x:auto;margin:0.5rem 0;
      }
      .message-bubble pre code { background:none;padding:0; }
    </style>

    <!-- ============================================ -->
    <!-- Structure HTML du chat                      -->
    <!-- ============================================ -->
    <div class="tutor-page">

      <!-- SIDEBAR : Liste des sessions -->
      <div class="tutor-sidebar" id="tutor-sidebar">
        <div class="sidebar-header">
          <div class="sidebar-title">Tuteur IA</div>
          <button class="new-session-btn" id="new-session-btn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            Nouvelle conversation
          </button>
        </div>
        <div class="session-list" id="session-list">
          <!-- Les sessions seront ajoutées ici par JavaScript -->
        </div>
      </div>

      <!-- ZONE DE CHAT -->
      <div class="chat-area" id="chat-area">
        <!-- Écran d'accueil (avant de sélectionner une session) -->
        <div class="welcome-screen" id="welcome-screen">
          <div class="welcome-icon">AI</div>
          <div class="welcome-title">Tuteur IA - Analyse Numerique</div>
          <div class="welcome-sub">
            Posez vos questions sur l'analyse numérique et le calcul scientifique.
            Les réponses sont adaptées à votre niveau et les formules sont vérifiées par SymPy.
          </div>
          <button class="new-session-btn" style="max-width:280px;margin-top:1.5rem" id="welcome-new-btn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            Commencer une conversation
          </button>
        </div>

        <!-- Chat actif (caché par défaut) -->
        <div id="active-chat" style="display:none;flex-direction:column;flex:1;overflow:hidden;">
          <!-- En-tête avec le nom du concept -->
          <div class="chat-header">
            <div style="display:flex;align-items:center;gap:0.75rem;">
              <button class="mobile-toggle" id="mobile-toggle">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
              </button>
              <div class="chat-header-info">
                <h3 id="chat-concept-name">Conversation</h3>
                <span id="chat-meta">Nouvelle session</span>
              </div>
            </div>
            <div id="chat-level-badge"></div>
          </div>

          <!-- Messages -->
          <div class="messages-container" id="messages-container"></div>

          <!-- Zone de saisie -->
          <div class="input-area">
            <div class="input-row">
              <div class="input-wrapper">
                <textarea
                  class="input-field"
                  id="question-input"
                  placeholder="Posez votre question sur l'analyse numérique..."
                  rows="1"
                ></textarea>
              </div>
              <button class="send-btn" id="send-btn" disabled>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `
  container.appendChild(main)

  // ============================================================
  // ÉTAPE 3 : Charger MathJax (rendu LaTeX)
  // ============================================================
  // MathJax est une librairie externe qui transforme le LaTeX
  // en jolies formules mathématiques.
  //
  // On le charge depuis un CDN (Content Delivery Network) :
  // un serveur externe qui héberge la librairie gratuitement.
  //
  // La configuration dit à MathJax :
  //   - Chercher le LaTeX entre $...$ (inline) et $$...$$ (bloc)
  //   - Utiliser le format SVG pour le rendu (plus joli)
  loadMathJax()

  // ============================================================
  // ÉTAPE 4 : Récupérer les éléments HTML
  // ============================================================
  // document.getElementById() cherche un élément par son attribut "id"
  // C'est comme dire "trouve-moi le bouton qui s'appelle send-btn"
  //
  // Le "!" après getElementById dit à TypeScript :
  // "je suis SÛR que cet élément existe, fais-moi confiance"
  // (sans le "!", TypeScript dirait "et si c'est null ?")

  setTimeout(() => {
    // setTimeout(..., 0) attend que le HTML soit ajouté au DOM
    // avant de chercher les éléments (sinon ils n'existent pas encore)

    const sessionList = main.querySelector('#session-list') as HTMLElement
    const welcomeScreen = main.querySelector('#welcome-screen') as HTMLElement
    const activeChat = main.querySelector('#active-chat') as HTMLElement
    const messagesContainer = main.querySelector('#messages-container') as HTMLElement
    const questionInput = main.querySelector('#question-input') as HTMLTextAreaElement
    const sendBtn = main.querySelector('#send-btn') as HTMLButtonElement
    const chatConceptName = main.querySelector('#chat-concept-name') as HTMLElement
    const chatMeta = main.querySelector('#chat-meta') as HTMLElement
    const chatLevelBadge = main.querySelector('#chat-level-badge') as HTMLElement
    const sidebar = main.querySelector('#tutor-sidebar') as HTMLElement
    const mobileToggle = main.querySelector('#mobile-toggle') as HTMLElement

    // ============================================================
    // ÉTAPE 5 : Event Listeners (écouter les clics)
    // ============================================================

    // --- Bouton "Nouvelle conversation" (sidebar + welcome) ---
    const newSessionBtn = main.querySelector('#new-session-btn') as HTMLElement
    const welcomeNewBtn = main.querySelector('#welcome-new-btn') as HTMLElement

    newSessionBtn?.addEventListener('click', createNewSession)
    welcomeNewBtn?.addEventListener('click', createNewSession)

    // --- Bouton Envoyer ---
    sendBtn?.addEventListener('click', sendMessage)

    // --- Entrée avec la touche Entrée ---
    // Enter = envoyer, Shift+Enter = nouvelle ligne
    questionInput?.addEventListener('keydown', (e: KeyboardEvent) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()  // Empêcher le saut de ligne
        sendMessage()
      }
    })

    // --- Activer/désactiver le bouton Envoyer ---
    // Le bouton est grisé si le champ est vide
    questionInput?.addEventListener('input', () => {
      sendBtn.disabled = !questionInput.value.trim() || isLoading
      // Auto-resize du textarea
      questionInput.style.height = 'auto'
      questionInput.style.height = Math.min(questionInput.scrollHeight, 120) + 'px'
    })

    // --- Toggle sidebar mobile ---
    mobileToggle?.addEventListener('click', () => {
      sidebar.classList.toggle('open')
    })

    // ============================================================
    // ÉTAPE 6 : Fonctions
    // ============================================================

    /**
     * Charge la liste des sessions depuis le backend.
     * Appelée au démarrage de la page.
     */
    async function loadSessions() {
      try {
        sessions = await api.getTutorSessions()
        renderSessionList()
      } catch (err) {
        console.error('Erreur chargement sessions:', err)
      }
    }

    /**
     * Affiche la liste des sessions dans la sidebar.
     */
    function renderSessionList() {
      if (!sessionList) return

      if (sessions.length === 0) {
        sessionList.innerHTML = `
          <div style="padding:2rem 1rem;text-align:center;color:#475569;font-size:0.8rem;">
            Aucune conversation.<br>Cliquez sur "Nouvelle conversation" pour commencer.
          </div>
        `
        return
      }

      sessionList.innerHTML = sessions.map(s => {
        const date = new Date(s.updated_at)
        const dateStr = date.toLocaleDateString('fr-FR', {
          day: 'numeric', month: 'short'
        })
        const timeStr = date.toLocaleTimeString('fr-FR', {
          hour: '2-digit', minute: '2-digit'
        })
        const isActive = s.id === activeSessionId

        return `
          <div class="session-item ${isActive ? 'active' : ''}"
               data-session-id="${s.id}">
            <div class="session-item-title">
              ${s.concept_id ? escapeHtml(s.concept_id.replace('concept_', '').replace(/_/g, ' ')) : 'Conversation #' + s.id}
            </div>
            <div class="session-item-meta">
              <span>${s.message_count} message${s.message_count > 1 ? 's' : ''}</span>
              <span>${dateStr} ${timeStr}</span>
            </div>
          </div>
        `
      }).join('')

      // Ajouter les event listeners aux sessions
      sessionList.querySelectorAll('.session-item').forEach(item => {
        item.addEventListener('click', () => {
          const id = parseInt(item.getAttribute('data-session-id') || '0')
          if (id) openSession(id)
        })
      })
    }

    /**
     * Crée une nouvelle session et l'ouvre.
     */
    async function createNewSession() {
      try {
        const session = await api.createTutorSession()
        sessions.unshift(session)  // Ajouter en tête de liste
        renderSessionList()
        openSession(session.id)
        // Fermer la sidebar en mobile
        sidebar.classList.remove('open')
      } catch (err: any) {
        console.error('Erreur création session:', err)
        alert('Erreur: ' + (err.message || 'Impossible de créer la session'))
      }
    }

    /**
     * Ouvre une session existante et charge ses messages.
     */
    async function openSession(sessionId: number) {
      activeSessionId = sessionId
      renderSessionList()  // Met à jour la sélection

      // Afficher le chat, cacher le welcome
      welcomeScreen.style.display = 'none'
      activeChat.style.display = 'flex'

      // Charger l'historique
      messagesContainer.innerHTML = `
        <div style="display:flex;flex-direction:column;gap:0.75rem;padding:2rem;">
          <div class="skeleton" style="height:60px;width:70%;"></div>
          <div class="skeleton" style="height:40px;width:50%;align-self:flex-end;"></div>
          <div class="skeleton" style="height:80px;width:75%;"></div>
        </div>
      `

      try {
        const history = await api.getTutorHistory(sessionId)
        messages = history.messages
        renderMessages()

        // Mettre à jour l'en-tête
        if (history.concept_id) {
          chatConceptName.textContent = history.concept_id
            .replace('concept_', '')
            .replace(/_/g, ' ')
            .replace(/\b\w/g, c => c.toUpperCase())
        } else {
          chatConceptName.textContent = 'Conversation #' + sessionId
        }
        chatMeta.textContent = `${messages.length} message${messages.length > 1 ? 's' : ''}`

      } catch (err) {
        console.error('Erreur chargement historique:', err)
        messagesContainer.innerHTML = `
          <div style="text-align:center;padding:2rem;color:#f87171;">
            Erreur lors du chargement de l'historique.
          </div>
        `
      }
    }

    /**
     * Affiche tous les messages dans la zone de chat.
     */
    function renderMessages() {
      if (!messagesContainer) return

      if (messages.length === 0) {
        messagesContainer.innerHTML = `
          <div style="text-align:center;padding:3rem;color:#475569;font-size:0.85rem;">
            <div style="font-size:2.5rem;margin-bottom:1rem;opacity:0.3;">&#128172;</div>
            Posez votre première question !<br>
            <span style="font-size:0.78rem;">
              Ex: "Explique-moi la méthode d'Euler" ou "Comment fonctionne Simpson ?"
            </span>
          </div>
        `
        return
      }

      messagesContainer.innerHTML = messages.map(msg => {
        const isStudent = msg.role === 'student'
        const time = new Date(msg.created_at).toLocaleTimeString('fr-FR', {
          hour: '2-digit', minute: '2-digit'
        })

        // Badge de vérification (seulement pour les messages du tuteur)
        let verificationHtml = ''
        if (!isStudent && msg.verified !== null) {
          verificationHtml = msg.verified
            ? '<div class="verification-badge verified-true">&#10003; Maths verifiees par SymPy</div>'
            : '<div class="verification-badge verified-false">&#9888; Formules non verifiees</div>'
        }

        return `
          <div class="message message-${isStudent ? 'student' : 'tutor'}">
            <div class="message-bubble">
              ${isStudent ? escapeHtml(msg.content) : formatTutorContent(msg.content)}
            </div>
            ${verificationHtml}
            <div class="message-time">${time}</div>
          </div>
        `
      }).join('')

      // Scroller tout en bas pour voir le dernier message
      messagesContainer.scrollTop = messagesContainer.scrollHeight

      // Déclencher le rendu MathJax pour les formules LaTeX
      renderMathInContainer(messagesContainer)
    }

    /**
     * Envoie la question au tuteur IA.
     * C'est la fonction la plus importante du frontend !
     */
    async function sendMessage() {
      const question = questionInput.value.trim()
      if (!question || isLoading || !activeSessionId) return

      // Désactiver l'input pendant le chargement
      isLoading = true
      questionInput.value = ''
      questionInput.style.height = 'auto'
      sendBtn.disabled = true

      // Ajouter le message de l'étudiant immédiatement
      // (optimistic UI : on affiche avant la réponse du serveur)
      const studentMsg: TutorMessage = {
        id: Date.now(),  // ID temporaire
        role: 'student',
        content: question,
        verified: null,
        concept_id: null,
        created_at: new Date().toISOString(),
      }
      messages.push(studentMsg)
      renderMessages()

      // Afficher l'animation "en train d'écrire..."
      const typingHtml = `
        <div class="typing-indicator" id="typing-indicator">
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
        </div>
      `
      messagesContainer.insertAdjacentHTML('beforeend', typingHtml)
      messagesContainer.scrollTop = messagesContainer.scrollHeight

      try {
        // --- Appel au backend ---
        // C'est ici qu'on déclenche tout le pipeline :
        //   Question → RAG → LLM local → SymPy → Réponse
        const response: TutorAskResponse = await api.askTutor(
          activeSessionId,
          { question }
        )

        // Enlever l'animation "en train d'écrire"
        const typingEl = messagesContainer.querySelector('#typing-indicator')
        typingEl?.remove()

        // Ajouter la réponse du tuteur
        const tutorMsg: TutorMessage = {
          id: response.message_id,
          role: 'tutor',
          content: response.content,
          verified: response.verified,
          concept_id: null,
          created_at: new Date().toISOString(),
        }
        messages.push(tutorMsg)
        renderMessages()

        // Mettre à jour l'en-tête avec les infos du concept
        if (response.concept_name) {
          chatConceptName.textContent = response.concept_name
        }
        chatMeta.textContent = `Maitrise: ${response.student_mastery.toFixed(0)}%`

        // Mettre à jour le badge de niveau
        updateLevelBadge(response.complexity_level)

        // Mettre à jour la session dans la sidebar
        const sessionIndex = sessions.findIndex(s => s.id === activeSessionId)
        if (sessionIndex >= 0) {
          sessions[sessionIndex].message_count = messages.length
          sessions[sessionIndex].updated_at = new Date().toISOString()
          renderSessionList()
        }

      } catch (err: any) {
        // Enlever l'animation "en train d'écrire"
        const typingEl = messagesContainer.querySelector('#typing-indicator')
        typingEl?.remove()

        // Afficher l'erreur dans le chat
        const errorMsg: TutorMessage = {
          id: Date.now(),
          role: 'tutor',
          content: `Erreur: ${err.message || "Impossible de contacter le tuteur IA. Verifiez votre connexion."}`,
          verified: null,
          concept_id: null,
          created_at: new Date().toISOString(),
        }
        messages.push(errorMsg)
        renderMessages()
      }

      isLoading = false
      sendBtn.disabled = !questionInput.value.trim()
    }

    /**
     * Met à jour le badge de niveau dans l'en-tête.
     */
    function updateLevelBadge(level: string) {
      if (!chatLevelBadge) return
      const labels: Record<string, string> = {
        simplified: 'Simplifie',
        standard: 'Standard',
        rigorous: 'Rigoureux',
      }
      chatLevelBadge.innerHTML = `
        <span class="level-badge level-${level}">
          ${labels[level] || level}
        </span>
      `
    }

    // ============================================================
    // ÉTAPE 7 : Charger les sessions au démarrage
    // ============================================================
    loadSessions()

  }, 0)  // Fin du setTimeout

  shell.setContent(container)
  return shell.element
}


// ============================================================
// FONCTIONS UTILITAIRES (hors du composant)
// ============================================================

/**
 * Échappe les caractères HTML dangereux.
 *
 * POURQUOI ? Pour éviter les attaques XSS (Cross-Site Scripting).
 * Si un utilisateur envoie "<script>alert('hack')</script>",
 * sans escapeHtml, le navigateur exécuterait le script !
 * Avec escapeHtml, ça affiche juste le texte.
 */
function escapeHtml(text: string): string {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

/**
 * Formate le contenu du tuteur pour le rendu HTML.
 *
 * Transforme les marqueurs Markdown basiques en HTML :
 *   **gras** → <strong>gras</strong>
 *   *italique* → <em>italique</em>
 *   `code` → <code>code</code>
 *   Les numérotations (1. 2. 3.) → liste ordonnée
 *
 * Le LaTeX ($...$, $$...$$) est LAISSÉ TEL QUEL
 * car MathJax s'en occupera après le rendu.
 */
function formatTutorContent(content: string): string {
  // On protège le LaTeX d'abord (pour ne pas que le formatage Markdown
  // casse les formules). On remplace temporairement par des placeholders.
  const latexBlocks: string[] = []

  // Protéger $$...$$
  let formatted = content.replace(/\$\$[\s\S]+?\$\$/g, (match) => {
    latexBlocks.push(match)
    return `%%LATEX_BLOCK_${latexBlocks.length - 1}%%`
  })

  // Protéger $...$
  formatted = formatted.replace(/\$[^\$]+?\$/g, (match) => {
    latexBlocks.push(match)
    return `%%LATEX_BLOCK_${latexBlocks.length - 1}%%`
  })

  // Markdown basique
  formatted = formatted
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`(.+?)`/g, '<code>$1</code>')

  // Sauts de ligne → <br> (mais pas dans les blocs LaTeX)
  formatted = formatted.replace(/\n/g, '<br>')

  // Restaurer le LaTeX
  latexBlocks.forEach((block, i) => {
    formatted = formatted.replace(`%%LATEX_BLOCK_${i}%%`, block)
  })

  return formatted
}

/**
 * Charge MathJax depuis le CDN.
 *
 * MathJax est une librairie qui transforme le LaTeX
 * ($x^2$, $$\int f(x)dx$$) en jolies formules dans le navigateur.
 *
 * On le configure pour :
 *   - Détecter le LaTeX entre $...$ et $$...$$
 *   - Utiliser le rendu SVG (plus joli que HTML)
 */
function loadMathJax() {
  // Vérifier si MathJax est déjà chargé
  if ((window as any).MathJax) return

  // Configuration de MathJax
  // On la met dans window.MathJax AVANT de charger le script
  // car MathJax lit cette config au démarrage
  ;(window as any).MathJax = {
    tex: {
      // Les délimiteurs LaTeX à détecter
      inlineMath: [['$', '$']],          // $x^2$ → inline
      displayMath: [['$$', '$$']],       // $$\int...$$ → bloc centré
      processEscapes: true,              // \$ → affiche un vrai $
    },
    svg: {
      fontCache: 'global',  // Cache les polices pour de meilleures performances
    },
    startup: {
      // Ne pas scanner automatiquement la page au chargement
      // On déclenchera le rendu manuellement avec typeset()
      typeset: false,
    },
  }

  // Charger le script MathJax depuis le CDN
  const script = document.createElement('script')
  script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js'
  script.async = true  // Charger sans bloquer la page
  document.head.appendChild(script)
}

/**
 * Déclenche le rendu MathJax dans un conteneur.
 *
 * Appelée après chaque ajout de message contenant du LaTeX.
 * MathJax scanne le conteneur et transforme les $...$ en formules.
 */
function renderMathInContainer(container: HTMLElement) {
  const MJ = (window as any).MathJax
  if (MJ && MJ.typesetPromise) {
    // typesetPromise([elements]) dit à MathJax :
    // "scanne ces éléments et transforme le LaTeX en formules"
    MJ.typesetPromise([container]).catch((err: any) => {
      console.warn('MathJax typeset error:', err)
    })
  }
}
