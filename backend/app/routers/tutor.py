# ============================================================
# Router du Tuteur IA — Les endpoints API
# ============================================================
# C'est quoi ce fichier ?
#
# C'est le "CONTRÔLEUR" du tuteur IA. Il définit les URLs
# (endpoints) que le frontend peut appeler pour interagir
# avec le tuteur.
#
# C'est quoi un Router dans FastAPI ?
# Imaginez un restaurant :
#   - Le CLIENT (frontend) passe une COMMANDE (requête HTTP)
#   - Le SERVEUR (ce router) reçoit la commande
#   - Le SERVEUR va en CUISINE (services RAG, LLM, Vérification)
#   - Le SERVEUR revient avec le PLAT (la réponse JSON)
#
# Ce router orchestre les 3 services qu'on a créés :
#   1. RAG Service → cherche le contexte dans Neo4j + PostgreSQL
#   2. LLM Service → envoie la question à Gemini avec le contexte
#   3. Verification Service → vérifie les maths avec SymPy
#
# Les endpoints sont :
#   POST /tutor/sessions              → créer une nouvelle session
#   GET  /tutor/sessions              → lister mes sessions
#   POST /tutor/sessions/{id}/ask     → poser une question
#   GET  /tutor/sessions/{id}/history → voir l'historique
#
# POURQUOI des sessions ?
# Comme WhatsApp ou Messenger, chaque "conversation" est une
# session séparée. Un étudiant peut avoir :
#   - Session 1 : questions sur Euler
#   - Session 2 : questions sur Lagrange
# Chaque session garde son historique de messages.
# ============================================================

import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# On importe nos modèles et services
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.tutor import (
    MessageResponse,
    SessionCreateRequest,
    SessionHistoryResponse,
    SessionResponse,
    # Schemas Pydantic (validation)
    TutorAskRequest,
    TutorAskResponse,
    TutorMessage,
    # Modèles SQLAlchemy (tables)
    TutorSession,
)
from app.services.llm_service import llm_service
from app.services.rag_service import rag_service
from app.services.verification_service import verification_service

logger = logging.getLogger(__name__)

# ============================================================
# Création du Router
# ============================================================
# APIRouter() crée un groupe d'endpoints avec un préfixe commun.
#
# prefix="/tutor" : tous les endpoints commencent par /tutor
#   → POST /tutor/sessions (pas juste /sessions)
#
# tags=["Tuteur IA"] : dans la documentation Swagger (/docs),
#   ces endpoints seront regroupés sous l'onglet "Tuteur IA"
#
# Swagger est la documentation AUTOMATIQUE de FastAPI.
# Allez sur http://localhost:8000/docs pour la voir !
# ============================================================
router = APIRouter(
    prefix="/tutor",
    tags=["Tuteur IA"],
)


# ============================================================
# ENDPOINT 1 : Créer une nouvelle session
# ============================================================
# POST /tutor/sessions
#
# Quand un étudiant commence une nouvelle conversation avec
# le tuteur, le frontend appelle cet endpoint pour créer
# une session vide.
#
# Qui peut appeler ? Seulement un étudiant CONNECTÉ
# (le token JWT est vérifié par get_current_user)
# ============================================================
@router.post(
    "/sessions",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer une nouvelle session de tutorat",
    description="Crée une conversation vide avec le tuteur IA. "
                "Optionnel : spécifier un concept_id pour cibler un sujet.",
)
async def create_session(
    # --- Les paramètres de la fonction ---
    # request : les données envoyées par le frontend (JSON)
    #   → concept_id optionnel
    request: SessionCreateRequest,

    # db : la connexion PostgreSQL
    #   → Depends(get_db) = FastAPI crée automatiquement une
    #     connexion et la ferme après la requête
    db: Session = Depends(get_db),

    # current_user : l'étudiant connecté
    #   → Depends(get_current_user) = FastAPI vérifie le token JWT
    #     et retourne l'objet Etudiant correspondant
    #   Si le token est invalide → erreur 401 automatique
    current_user_id: int = Depends(get_current_user),
):
    """
    Crée une nouvelle session de tutorat.

    Flux :
    1. On crée un objet TutorSession avec l'ID de l'étudiant
    2. On le sauvegarde dans PostgreSQL
    3. On retourne les infos de la session au frontend
    """
    # --- Étape 1 : Créer l'objet session ---
    # TutorSession() crée un objet Python qui REPRÉSENTE une ligne
    # dans la table tutor_sessions. Ce n'est pas encore dans la base !
    session = TutorSession(
        etudiant_id=current_user_id,
        concept_id=request.concept_id,
    )

    # --- Étape 2 : Sauvegarder dans PostgreSQL ---
    # db.add(session) → met la session dans la "file d'attente"
    # db.commit()     → écrit VRAIMENT dans la base de données
    # db.refresh()    → relit depuis la base pour avoir l'ID auto-généré
    db.add(session)
    db.commit()
    db.refresh(session)

    logger.info(
        f"Session créée : id={session.id}, "
        f"étudiant={current_user_id}, "
        f"concept={request.concept_id}"
    )

    # --- Étape 3 : Retourner la réponse ---
    # On construit manuellement la réponse car SessionResponse
    # attend un champ "message_count" qui n'est pas dans le modèle
    return SessionResponse(
        id=session.id,
        etudiant_id=session.etudiant_id,
        concept_id=session.concept_id,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=0,  # Nouvelle session → 0 messages
    )


# ============================================================
# ENDPOINT 2 : Lister mes sessions
# ============================================================
# GET /tutor/sessions
#
# Le frontend affiche la liste des conversations passées
# de l'étudiant (comme la liste de chats dans WhatsApp).
#
# Protection IDOR : un étudiant ne voit QUE ses propres sessions.
# IDOR = "Insecure Direct Object Reference" = un étudiant essaie
# d'accéder aux données d'un autre en changeant l'ID dans l'URL.
# On évite ça en filtrant avec current_user_id.
# ============================================================
@router.get(
    "/sessions",
    response_model=list[SessionResponse],
    summary="Lister mes sessions de tutorat",
    description="Retourne toutes les sessions de l'étudiant connecté, "
                "triées de la plus récente à la plus ancienne.",
)
async def list_sessions(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """
    Liste toutes les sessions de l'étudiant connecté.

    La requête SQL générée par SQLAlchemy ressemble à :
    SELECT * FROM tutor_sessions
    WHERE etudiant_id = 42
    ORDER BY updated_at DESC
    """
    # --- Requête SQLAlchemy ---
    # db.query(TutorSession) = "SELECT * FROM tutor_sessions"
    # .filter(...) = "WHERE etudiant_id = current_user_id"
    # .order_by(...desc()) = "ORDER BY updated_at DESC" (récent d'abord)
    # .all() = exécuter et retourner une liste Python
    sessions = (
        db.query(TutorSession)
        .filter(TutorSession.etudiant_id == current_user_id)
        .order_by(TutorSession.updated_at.desc())
        .all()
    )

    # Construire la réponse avec le nombre de messages
    result = []
    for s in sessions:
        # len(s.messages) utilise la RELATION SQLAlchemy définie
        # dans le modèle TutorSession : messages = relationship(...)
        # SQLAlchemy fait automatiquement le JOIN pour nous !
        result.append(
            SessionResponse(
                id=s.id,
                etudiant_id=s.etudiant_id,
                concept_id=s.concept_id,
                created_at=s.created_at,
                updated_at=s.updated_at,
                message_count=len(s.messages),
            )
        )

    return result


# ============================================================
# ENDPOINT 3 : Poser une question au tuteur (LE PLUS IMPORTANT)
# ============================================================
# POST /tutor/sessions/{session_id}/ask
#
# C'est l'endpoint PRINCIPAL de tout le projet.
# Il orchestre le pipeline complet :
#
#   Question de l'étudiant
#         ↓
#   [1] RAG Service → cherche le contexte (Neo4j + PostgreSQL)
#         ↓
#   [2] LLM Service → envoie à Gemini avec le contexte adaptatif
#         ↓
#   [3] Verification Service → vérifie les maths avec SymPy
#         ↓
#   Réponse vérifiée envoyée au frontend
#
# C'est ici que TOUT se connecte. Les 3 services qu'on a créés
# travaillent ensemble pour la première fois.
# ============================================================
@router.post(
    "/sessions/{session_id}/ask",
    response_model=TutorAskResponse,
    summary="Poser une question au tuteur IA",
    description="Envoie une question au tuteur. Le système utilise "
                "GraphRAG pour personnaliser la réponse et SymPy "
                "pour vérifier les formules mathématiques.",
)
async def ask_tutor(
    # --- Paramètre de chemin (path parameter) ---
    # {session_id} dans l'URL → devient un paramètre Python
    # Ex: POST /tutor/sessions/42/ask → session_id = 42
    session_id: int,

    # --- Corps de la requête (request body) ---
    # Le JSON envoyé par le frontend :
    # {"question": "Comment marche Euler ?", "concept_id": "concept_euler"}
    request: TutorAskRequest,

    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """
    Pipeline complet du tuteur IA adaptatif.

    C'est LA méthode qui fait tout fonctionner ensemble.
    """

    # ==========================================================
    # ÉTAPE 0 : Vérifier que la session existe et appartient à l'étudiant
    # ==========================================================
    # Protection IDOR : on vérifie que :
    # 1. La session existe (sinon → erreur 404)
    # 2. Elle appartient à l'étudiant connecté (sinon → erreur 403)
    #
    # Sans cette vérification, un étudiant pourrait envoyer
    # des messages dans la session d'un autre en changeant l'ID !
    session = db.query(TutorSession).filter(
        TutorSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} introuvable."
        )

    if session.etudiant_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cette session ne vous appartient pas."
        )

    # ==========================================================
    # ÉTAPE 1 : Sauvegarder le message de l'étudiant
    # ==========================================================
    # On sauvegarde d'abord la question dans la base pour garder
    # l'historique complet, même si Gemini tombe en panne ensuite.
    student_message = TutorMessage(
        session_id=session_id,
        role="student",
        content=request.question,
    )
    db.add(student_message)
    db.commit()

    logger.info(
        f"Message étudiant sauvegardé : session={session_id}, "
        f"longueur={len(request.question)} caractères"
    )

    # ==========================================================
    # ÉTAPE 2 : RAG — Construire le contexte personnalisé
    # ==========================================================
    # Le RAG Service va :
    # - Trouver quel concept correspond à la question
    # - Chercher les prérequis de ce concept dans Neo4j
    # - Récupérer la maîtrise de l'étudiant dans PostgreSQL
    # - Récupérer les ressources de remédiation
    #
    # Tout ça est emballé dans un objet ConceptContext qui sera
    # envoyé au LLM Service pour construire le prompt adaptatif.
    #
    # Le concept_id peut venir de 3 sources (par priorité) :
    # 1. La requête (l'étudiant a choisi un concept dans l'interface)
    # 2. La session (concept choisi à la création)
    # 3. Deviné automatiquement depuis la question (find_concept)
    concept_id = request.concept_id or session.concept_id

    context = rag_service.build_context(
        db=db,
        etudiant_id=current_user_id,
        question=request.question,
        concept_id=concept_id,
    )

    logger.info(
        f"Contexte RAG : concept={context.concept_name}, "
        f"maîtrise={context.student_mastery}%, "
        f"prérequis={len(context.prerequisites)}"
    )

    # ==========================================================
    # ÉTAPE 3 : Récupérer l'historique de conversation
    # ==========================================================
    # On envoie les derniers messages à Gemini pour qu'il ait
    # le contexte de la conversation (comme quand vous relisez
    # les messages précédents avant de répondre sur WhatsApp).
    #
    # On prend les 10 derniers messages (5 échanges aller-retour)
    # pour ne pas dépasser la limite de tokens de Gemini.
    previous_messages = (
        db.query(TutorMessage)
        .filter(TutorMessage.session_id == session_id)
        .order_by(TutorMessage.created_at.asc())
        .all()
    )

    # Convertir en format simple pour le LLM Service
    # [{"role": "student", "content": "..."}, {"role": "tutor", "content": "..."}]
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in previous_messages[:-1]  # Exclure le message qu'on vient d'ajouter
    ]

    # ==========================================================
    # ÉTAPE 4 : LLM — Générer la réponse avec Gemini
    # ==========================================================
    # Le LLM Service va :
    # 1. Construire un prompt adaptatif basé sur le contexte
    #    (niveau simplifié/standard/rigoureux selon la maîtrise)
    # 2. Envoyer le prompt + l'historique + la question à Gemini
    # 3. Retourner la réponse texte (avec du LaTeX)
    #
    # C'est un appel ASYNCHRONE (await) car Gemini met 1-3 secondes
    # à répondre. Pendant ce temps, le serveur peut traiter
    # d'autres requêtes (c'est l'avantage de l'async).
    llm_response = await llm_service.generate_response(
        question=request.question,
        context=context,
        conversation_history=conversation_history,
    )

    logger.info(
        f"Réponse Gemini reçue : {len(llm_response)} caractères"
    )

    # ==========================================================
    # ÉTAPE 5 : Vérification — Checker les maths avec SymPy
    # ==========================================================
    # Le Verification Service va :
    # 1. Extraire toutes les formules LaTeX de la réponse
    #    (tout ce qui est entre $...$ ou $$...$$)
    # 2. Pour chaque formule, essayer de la parser avec SymPy
    # 3. Si SymPy comprend → la formule est syntaxiquement correcte
    # 4. Retourner un résultat global (vérifié ou non)
    #
    # C'est l'architecture NEURO-SYMBOLIQUE :
    # - Neuro = Gemini génère la réponse (peut halluciner)
    # - Symbolique = SymPy vérifie les maths (100% fiable)
    verification_result = verification_service.verify_response(llm_response)

    is_verified = verification_result.get("verified", False)

    logger.info(
        f"Vérification SymPy : verified={is_verified}, "
        f"expressions={verification_result.get('total_expressions', 0)}"
    )

    # ==========================================================
    # ÉTAPE 6 : Sauvegarder la réponse du tuteur
    # ==========================================================
    # On sauvegarde la réponse de Gemini dans la base avec :
    # - role="tutor" (pour distinguer des messages étudiants)
    # - verified=True/False (résultat de la vérification SymPy)
    # - concept_id = le concept identifié par le RAG
    tutor_message = TutorMessage(
        session_id=session_id,
        role="tutor",
        content=llm_response,
        verified=is_verified,
        concept_id=context.concept_id or None,
    )
    db.add(tutor_message)

    # --- Mettre à jour la session ---
    # On met à jour le concept_id de la session si on en a trouvé un
    # (pour les prochaines questions dans cette session)
    # Et on met à jour updated_at pour le tri par date
    if context.concept_id and not session.concept_id:
        session.concept_id = context.concept_id

    session.updated_at = datetime.now(UTC)

    db.commit()
    db.refresh(tutor_message)

    logger.info(
        f"Réponse tuteur sauvegardée : message_id={tutor_message.id}"
    )

    # ==========================================================
    # ÉTAPE 7 : Retourner la réponse au frontend
    # ==========================================================
    # On emballe tout dans TutorAskResponse (le schema Pydantic)
    # Le frontend recevra un JSON comme :
    # {
    #   "message_id": 42,
    #   "content": "L'interpolation de Lagrange est...",
    #   "verified": true,
    #   "concept_name": "Lagrange Interpolation",
    #   "student_mastery": 45.0,
    #   "complexity_level": "standard",
    #   "verification_details": { ... }
    # }
    complexity_level = llm_service.get_complexity_level(context.student_mastery)

    return TutorAskResponse(
        message_id=tutor_message.id,
        content=llm_response,
        verified=is_verified,
        concept_name=context.concept_name,
        student_mastery=context.student_mastery,
        complexity_level=complexity_level,
        verification_details=verification_result,
    )


# ============================================================
# ENDPOINT 4 : Voir l'historique d'une session
# ============================================================
# GET /tutor/sessions/{session_id}/history
#
# Le frontend appelle cet endpoint quand l'étudiant ouvre
# une conversation existante. Il retourne TOUS les messages
# de la session, triés par date.
# ============================================================
@router.get(
    "/sessions/{session_id}/history",
    response_model=SessionHistoryResponse,
    summary="Historique d'une session",
    description="Retourne tous les messages d'une session de tutorat, "
                "triés du plus ancien au plus récent.",
)
async def get_session_history(
    session_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """
    Retourne l'historique complet d'une session.

    Protection IDOR incluse : un étudiant ne peut voir
    que l'historique de SES propres sessions.
    """
    # --- Vérifier que la session existe et appartient à l'étudiant ---
    session = db.query(TutorSession).filter(
        TutorSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} introuvable."
        )

    if session.etudiant_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cette session ne vous appartient pas."
        )

    # --- Récupérer tous les messages ---
    # On utilise la RELATION SQLAlchemy : session.messages
    # C'est équivalent à :
    # SELECT * FROM tutor_messages
    # WHERE session_id = 42
    # ORDER BY created_at ASC
    #
    # Le ORDER BY est défini dans le modèle TutorSession :
    # order_by="TutorMessage.created_at"
    messages = [
        MessageResponse(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            verified=msg.verified,
            concept_id=msg.concept_id,
            created_at=msg.created_at,
        )
        for msg in session.messages
    ]

    return SessionHistoryResponse(
        session_id=session.id,
        concept_id=session.concept_id,
        messages=messages,
    )
