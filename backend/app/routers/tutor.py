# ============================================================
# AI Tutor Router — The API endpoints
# ============================================================
# What is this file?
#
# It is the "CONTROLLER" of the AI tutor. It defines the URLs
# (endpoints) that the frontend can call to interact
# with the tutor.
#
# What is a Router in FastAPI?
# Imagine a restaurant:
#   - The CLIENT (frontend) places an ORDER (HTTP request)
#   - The WAITER (this router) receives the order
#   - The WAITER goes to the KITCHEN (RAG, LLM, Verification services)
#   - The WAITER comes back with the DISH (the JSON response)
#
# This router orchestrates the 3 services we created:
#   1. RAG Service -> searches the context in Neo4j + PostgreSQL
#   2. LLM Service -> sends the question to the LLM (Ollama / local fine-tuned Gemma) with the context
#   3. Verification Service -> checks the math with SymPy
#
# The endpoints are:
#   POST /tutor/sessions              -> create a new session
#   GET  /tutor/sessions              -> list my sessions
#   POST /tutor/sessions/{id}/ask     -> ask a question
#   GET  /tutor/sessions/{id}/history -> view the history
#
# WHY sessions?
# Like WhatsApp or Messenger, each "conversation" is a
# separate session. A student can have:
#   - Session 1: questions about Euler
#   - Session 2: questions about Lagrange
# Each session keeps its own message history.
# ============================================================

import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

# We import our models and services
from app.core.config import get_settings
from app.core.database import get_db
from app.core.i18n import http_msg, lang_from_user
from app.core.rate_limit import LLM_HEAVY_LIMIT, limiter
from app.core.security import get_current_user
from app.models.etudiant import Etudiant
from app.models.tutor import (
    MessageResponse,
    SessionCreateRequest,
    SessionHistoryResponse,
    SessionResponse,
    # Pydantic schemas (validation)
    TutorAskRequest,
    TutorAskResponse,
    TutorMessage,
    # SQLAlchemy models (tables)
    TutorSession,
)
from app.services.llm_service import llm_service
from app.services.rag_service import rag_service
from app.services.verification_service import verification_service

logger = logging.getLogger(__name__)

# ============================================================
# Creation of the Router
# ============================================================
# APIRouter() creates a group of endpoints with a common prefix.
#
# prefix="/tutor": all endpoints start with /tutor
#   -> POST /tutor/sessions (not just /sessions)
#
# tags=["Tuteur IA"]: in the Swagger documentation (/docs),
#   these endpoints will be grouped under the "Tuteur IA" tab
#
# Swagger is the AUTOMATIC documentation of FastAPI.
# Go to http://localhost:8000/docs to see it!
# ============================================================
router = APIRouter(
    prefix="/tutor",
    tags=["Tuteur IA"],
)


# ============================================================
# ENDPOINT 1: Create a new session
# ============================================================
# POST /tutor/sessions
#
# When a student starts a new conversation with
# the tutor, the frontend calls this endpoint to create
# an empty session.
#
# Who can call it? Only a LOGGED-IN student
# (the JWT token is verified by get_current_user)
# ============================================================
@router.get(
    "/llm-options",
    summary="Liste des LLM disponibles pour le tuteur",
    description=(
        "Retourne la liste des modèles LLM configurés et disponibles "
        "(Ollama local, OpenAI cloud, etc.) avec leurs métadonnées pour "
        "alimenter le sélecteur côté frontend."
    ),
)
def list_llm_options(
    current_user_id: int = Depends(get_current_user),
):
    """Endpoint used by the frontend to display the AI picker modal.

    The frontend calls this on loading the Tutor page. If `picker_enabled`
    is False, the frontend completely hides the picker. If True, it displays
    a modal with the options returned in `available`.

    Returned format:
    {
        "picker_enabled": true,
        "default_provider": "openai",
        "available": [
            {
                "id": "ollama",
                "name": "Gemma local (E2B)",
                "model": "gemma-numerical-e2b",
                "tagline": "Runs on your computer, no internet needed",
                "requires_internet": false,
                "is_paid": false,
                "is_finetuned": true,
                "speed": "slow",
                "quality": "good",
                "privacy": "rgpd_safe",
                "icon": "laptop"
            },
            {
                "id": "openai",
                "name": "GPT-4o-mini",
                "model": "gpt-4o-mini",
                "tagline": "OpenAI cloud, premium quality",
                "requires_internet": true,
                "is_paid": true,
                "is_finetuned": false,
                "speed": "fast",
                "quality": "excellent",
                "privacy": "cloud",
                "icon": "cloud"
            }
        ]
    }
    """
    settings = get_settings()
    available = []

    # STATIC metadata for each known provider. The frontend
    # uses it to render the comparison cards.
    PROVIDER_METADATA = {
        "ollama": {
            "id": "ollama",
            "name": "Gemma local (E2B)",
            "tagline_en": "Runs on your computer, no internet needed",
            "tagline_fr": "Tourne sur ton ordinateur, sans internet",
            "description_en": (
                "Fine-tuned on 144 bilingual numerical analysis examples. "
                "100% local inference via Ollama, zero cost, GDPR compliant. "
                "Slower than cloud but privacy-safe."
            ),
            "description_fr": (
                "Fine-tuné sur 144 exemples bilingues d'analyse numérique. "
                "Inférence 100% locale via Ollama, coût nul, RGPD-safe. "
                "Plus lent que le cloud mais respect total des données."
            ),
            "requires_internet": False,
            "is_paid": False,
            "is_finetuned": True,
            "speed": "slow",      # ~15-30s
            "quality": "good",
            "privacy": "rgpd_safe",
            "icon": "laptop",
        },
        "openai": {
            "id": "openai",
            "name": "GPT-4o-mini",
            "tagline_en": "OpenAI cloud, premium quality",
            "tagline_fr": "Cloud OpenAI, qualité supérieure",
            "description_en": (
                "OpenAI's cloud model. Excellent reasoning and bilingual. "
                "Requires internet, sends data to OpenAI servers, charges per use "
                "(~$0.0005 per question). Faster and more accurate on complex topics."
            ),
            "description_fr": (
                "Modèle cloud d'OpenAI. Excellent raisonnement et bilingue parfait. "
                "Nécessite internet, données envoyées chez OpenAI, payant à l'usage "
                "(~$0.0005 par question). Plus rapide et précis sur les sujets complexes."
            ),
            "requires_internet": True,
            "is_paid": True,
            "is_finetuned": False,
            "speed": "fast",      # ~2-5s
            "quality": "excellent",
            "privacy": "cloud",
            "icon": "cloud",
        },
    }

    # We return ONLY the providers actually available (loaded
    # successfully at backend startup).
    for provider_id in llm_service.available_providers():
        meta = PROVIDER_METADATA.get(provider_id)
        if meta is None:
            continue
        # Enrich with the effective model name
        meta_copy = dict(meta)
        meta_copy["model"] = llm_service.model_name_for(provider_id)
        available.append(meta_copy)

    return {
        "picker_enabled": settings.LLM_PICKER_ENABLED,
        "default_provider": llm_service.provider,
        "available": available,
    }


@router.post(
    "/sessions",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer une nouvelle session de tutorat",
    description="Crée une conversation vide avec le tuteur IA. "
                "Optionnel : spécifier un concept_id pour cibler un sujet.",
)
async def create_session(
    # --- The function parameters ---
    # request: the data sent by the frontend (JSON)
    #   -> optional concept_id
    request: SessionCreateRequest,

    # db: the PostgreSQL connection
    #   -> Depends(get_db) = FastAPI automatically creates a
    #     connection and closes it after the request
    db: Session = Depends(get_db),

    # current_user: the logged-in student
    #   -> Depends(get_current_user) = FastAPI verifies the JWT token
    #     and returns the corresponding Etudiant object
    #   If the token is invalid -> automatic 401 error
    current_user_id: int = Depends(get_current_user),
):
    """
    Create a new tutoring session.

    Flow:
    1. We create a TutorSession object with the student's ID
    2. We save it in PostgreSQL
    3. We return the session info to the frontend
    """
    # --- Step 1: Create the session object ---
    # TutorSession() creates a Python object that REPRESENTS a row
    # in the tutor_sessions table. It is not in the database yet!
    session = TutorSession(
        etudiant_id=current_user_id,
        concept_id=request.concept_id,
    )

    # --- Step 2: Save in PostgreSQL ---
    # db.add(session) -> puts the session in the "queue"
    # db.commit()     -> ACTUALLY writes to the database
    # db.refresh()    -> re-reads from the database to get the auto-generated ID
    db.add(session)
    db.commit()
    db.refresh(session)

    logger.info(
        f"Session créée : id={session.id}, "
        f"étudiant={current_user_id}, "
        f"concept={request.concept_id}"
    )

    # --- Step 3: Return the response ---
    # We build the response manually because SessionResponse
    # expects a "message_count" field that is not in the model
    return SessionResponse(
        id=session.id,
        etudiant_id=session.etudiant_id,
        concept_id=session.concept_id,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=0,  # New session -> 0 messages
    )


# ============================================================
# ENDPOINT 2: List my sessions
# ============================================================
# GET /tutor/sessions
#
# The frontend displays the list of the student's past
# conversations (like the chat list in WhatsApp).
#
# IDOR protection: a student sees ONLY their own sessions.
# IDOR = "Insecure Direct Object Reference" = a student tries
# to access another's data by changing the ID in the URL.
# We avoid that by filtering with current_user_id.
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
    List all the sessions of the logged-in student.

    The SQL query generated by SQLAlchemy looks like:
    SELECT * FROM tutor_sessions
    WHERE etudiant_id = 42
    ORDER BY updated_at DESC
    """
    # --- SQLAlchemy query ---
    # db.query(TutorSession) = "SELECT * FROM tutor_sessions"
    # .filter(...) = "WHERE etudiant_id = current_user_id"
    # .order_by(...desc()) = "ORDER BY updated_at DESC" (most recent first)
    # .all() = execute and return a Python list
    sessions = (
        db.query(TutorSession)
        .filter(TutorSession.etudiant_id == current_user_id)
        .order_by(TutorSession.updated_at.desc())
        .all()
    )

    # Build the response with the message count
    result = []
    for s in sessions:
        # len(s.messages) uses the SQLAlchemy RELATION defined
        # in the TutorSession model: messages = relationship(...)
        # SQLAlchemy automatically does the JOIN for us!
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
# ENDPOINT 3: Ask a question to the tutor (THE MOST IMPORTANT)
# ============================================================
# POST /tutor/sessions/{session_id}/ask
#
# This is the MAIN endpoint of the whole project.
# It orchestrates the complete pipeline:
#
#   Student's question
#         |
#   [1] RAG Service -> searches the context (Neo4j + PostgreSQL)
#         |
#   [2] LLM Service -> sends to the LLM (Ollama / local fine-tuned Gemma) with the adaptive context
#         |
#   [3] Verification Service -> checks the math with SymPy
#         |
#   Verified response sent to the frontend
#
# This is where EVERYTHING connects. The 3 services we created
# work together for the first time.
# ============================================================
@router.post(
    "/sessions/{session_id}/ask",
    response_model=TutorAskResponse,
    summary="Poser une question au tuteur IA",
    description="Envoie une question au tuteur. Le système utilise "
                "GraphRAG pour personnaliser la réponse et SymPy "
                "pour vérifier les formules mathématiques.",
)
@limiter.limit(LLM_HEAVY_LIMIT)
async def ask_tutor(
    # SECURITY: slowapi requires a parameter named exactly `request`
    # (FastAPI Request) to extract the IP. The Pydantic body is renamed
    # `payload` to avoid the collision.
    request: Request,

    # --- Path parameter ---
    # {session_id} in the URL -> becomes a Python parameter
    # Ex: POST /tutor/sessions/42/ask -> session_id = 42
    session_id: int,

    # --- Request body ---
    # The JSON sent by the frontend:
    # {"question": "Comment marche Euler ?", "concept_id": "concept_euler"}
    payload: TutorAskRequest,

    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """
    Complete pipeline of the adaptive AI tutor.

    This is THE method that makes everything work together.
    """

    # ==========================================================
    # STEP 0: Verify that the session exists and belongs to the student
    # ==========================================================
    # IDOR protection: we verify that:
    # 1. The session exists (otherwise -> 404 error)
    # 2. It belongs to the logged-in student (otherwise -> 403 error)
    #
    # Without this verification, a student could send
    # messages in another's session by changing the ID!
    session = db.query(TutorSession).filter(
        TutorSession.id == session_id
    ).first()

    if not session:
        lang = lang_from_user(db, current_user_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=http_msg("tutor.session_not_found", lang, id=session_id)
        )

    if session.etudiant_id != current_user_id:
        lang = lang_from_user(db, current_user_id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=http_msg("tutor.session_forbidden", lang)
        )

    # ==========================================================
    # STEP 1: Save the student's message
    # ==========================================================
    # We first save the question in the database to keep
    # the complete history, even if the LLM (Ollama / local fine-tuned Gemma) fails afterwards.
    student_message = TutorMessage(
        session_id=session_id,
        role="student",
        content=payload.question,
    )
    db.add(student_message)
    db.commit()

    logger.info(
        f"Message étudiant sauvegardé : session={session_id}, "
        f"longueur={len(payload.question)} caractères"
    )

    # ==========================================================
    # STEP 2: RAG — Build the personalized context
    # ==========================================================
    # The RAG Service will:
    # - Find which concept corresponds to the question
    # - Search the prerequisites of this concept in Neo4j
    # - Retrieve the student's mastery in PostgreSQL
    # - Retrieve the remediation resources
    #
    # All of this is wrapped in a ConceptContext object that will be
    # sent to the LLM Service to build the adaptive prompt.
    #
    # The concept_id can come from 2 sources (by priority):
    # 1. The request (the student chose a concept in the interface)
    # 2. Automatically guessed from the question (find_concept)
    #
    # IMPORTANT: we do NOT use session.concept_id as a fallback because
    # it would lock the tutor on the first concept of the session.
    # If the student asks several questions on different topics within
    # the same conversation, we want the RAG to re-guess each time
    # the most relevant concept for the current question.
    concept_id = payload.concept_id

    # We first retrieve the preferred language so the RAG returns the
    # names / descriptions / resources directly in the right language.
    etudiant_pref = db.query(Etudiant).filter(Etudiant.id == current_user_id).first()
    user_lang = getattr(etudiant_pref, "langue_preferee", "en") or "en"

    context = rag_service.build_context(
        db=db,
        etudiant_id=current_user_id,
        question=payload.question,
        concept_id=concept_id,
        lang=user_lang,
    )

    logger.info(
        f"Contexte RAG : concept={context.concept_name}, "
        f"maîtrise={context.student_mastery}%, "
        f"prérequis={len(context.prerequisites)}"
    )

    # ==========================================================
    # STEP 3: Retrieve the conversation history
    # ==========================================================
    # We send the latest messages to the LLM (Ollama / local fine-tuned Gemma) so it has
    # the context of the conversation (like when you reread
    # the previous messages before replying on WhatsApp).
    #
    # We take the last 10 messages (5 back-and-forth exchanges)
    # so as not to exceed the LLM's token limit (Ollama / local fine-tuned Gemma).
    previous_messages = (
        db.query(TutorMessage)
        .filter(TutorMessage.session_id == session_id)
        .order_by(TutorMessage.created_at.asc())
        .all()
    )

    # Convert to a simple format for the LLM Service
    # [{"role": "student", "content": "..."}, {"role": "tutor", "content": "..."}]
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in previous_messages[:-1]  # Exclude the message we just added
    ]

    # ==========================================================
    # STEP 4: LLM — Generate the response with the LLM (Ollama / local fine-tuned Gemma)
    # ==========================================================
    # The LLM Service will:
    # 1. Build an adaptive prompt based on the context
    #    (simplified/standard/rigorous level according to mastery)
    # 2. Send the prompt + history + question to the LLM (Ollama / local fine-tuned Gemma)
    # 3. Return the text response (with LaTeX)
    #
    # It is an ASYNCHRONOUS call (await) because the LLM (Ollama / local fine-tuned Gemma) takes 1-3 seconds
    # to respond. Meanwhile, the server can process
    # other requests (this is the advantage of async).
    # user_lang was already retrieved above for the RAG; we reuse it.
    # The provider_override is passed by the frontend (AI picker); if None,
    # the service uses the default provider from .env (LLM_PROVIDER).
    llm_response = await llm_service.generate_response(
        question=payload.question,
        context=context,
        conversation_history=conversation_history,
        language=user_lang,
        provider_override=payload.provider,
    )

    logger.info(
        "Réponse LLM (%s / %s) reçue : %d caractères",
        llm_service.provider,
        llm_service.model_name,
        len(llm_response),
    )

    # ==========================================================
    # STEP 5: Verification — Check the math with SymPy
    # ==========================================================
    # The Verification Service will:
    # 1. Extract all the LaTeX formulas from the response
    #    (everything between $...$ or $$...$$)
    # 2. For each formula, try to parse it with SymPy
    # 3. If SymPy understands -> the formula is syntactically correct
    # 4. Return a global result (verified or not)
    #
    # This is the NEURO-SYMBOLIC architecture:
    # - Neuro = the LLM (Ollama / local fine-tuned Gemma) generates the response (can hallucinate)
    # - Symbolic = SymPy checks the math (100% reliable)
    verification_result = verification_service.verify_response(llm_response)

    is_verified = verification_result.get("verified", False)

    logger.info(
        f"Vérification SymPy : verified={is_verified}, "
        f"expressions={verification_result.get('total_expressions', 0)}"
    )

    # ==========================================================
    # STEP 6: Save the tutor's response
    # ==========================================================
    # We save the LLM's response (Ollama / local fine-tuned Gemma) in the database with:
    # - role="tutor" (to distinguish from student messages)
    # - verified=True/False (result of the SymPy verification)
    # - concept_id = the concept identified by the RAG
    tutor_message = TutorMessage(
        session_id=session_id,
        role="tutor",
        content=llm_response,
        verified=is_verified,
        concept_id=context.concept_id or None,
    )
    db.add(tutor_message)

    # --- Update the session ---
    # We update the session's concept_id if we found one
    # (for the next questions in this session)
    # And we update updated_at for sorting by date
    if context.concept_id and not session.concept_id:
        session.concept_id = context.concept_id

    session.updated_at = datetime.now(UTC)

    db.commit()
    db.refresh(tutor_message)

    logger.info(
        f"Réponse tuteur sauvegardée : message_id={tutor_message.id}"
    )

    # ==========================================================
    # STEP 7: Return the response to the frontend
    # ==========================================================
    # We wrap everything in TutorAskResponse (the Pydantic schema)
    # The frontend will receive a JSON like:
    # {
    #   "message_id": 42,
    #   "content": "L'interpolation de Lagrange est...",
    #   "verified": true,
    #   "concept_name": "Lagrange Interpolation",
    #   "student_mastery": 45.0,
    #   "complexity_level": "standard",
    #   "verification_details": { ... }
    # }
    # Reported level reflects the student's GLOBAL level (niveau_actuel),
    # which is what now drives the tutor's adaptation.
    complexity_level = llm_service.complexity_from_level(
        getattr(context, "student_level", "beginner")
    )

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
# ENDPOINT 4: View the history of a session
# ============================================================
# GET /tutor/sessions/{session_id}/history
#
# The frontend calls this endpoint when the student opens
# an existing conversation. It returns ALL the messages
# of the session, sorted by date.
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
    Return the complete history of a session.

    IDOR protection included: a student can only see
    the history of THEIR own sessions.
    """
    # --- Verify that the session exists and belongs to the student ---
    session = db.query(TutorSession).filter(
        TutorSession.id == session_id
    ).first()

    if not session:
        lang = lang_from_user(db, current_user_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=http_msg("tutor.session_not_found", lang, id=session_id)
        )

    if session.etudiant_id != current_user_id:
        lang = lang_from_user(db, current_user_id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=http_msg("tutor.session_forbidden", lang)
        )

    # --- Retrieve all the messages ---
    # We use the SQLAlchemy RELATION: session.messages
    # It is equivalent to:
    # SELECT * FROM tutor_messages
    # WHERE session_id = 42
    # ORDER BY created_at ASC
    #
    # The ORDER BY is defined in the TutorSession model:
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
