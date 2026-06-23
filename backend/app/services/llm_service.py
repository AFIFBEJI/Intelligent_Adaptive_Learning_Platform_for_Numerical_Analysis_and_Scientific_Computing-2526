# ============================================================
# LLM Service — Communication with Ollama (local fine-tuned Gemma)
# ============================================================
# What is this file?
#
# This service does 3 things:
# 1. BUILD an adaptive prompt (the instructions for the AI)
#    based on the student's level and the Neo4j context
# 2. PREFIX the question with the bilingual tags expected by
#    the fine-tuned Gemma E2B model: [level: ...] [lang: ...]
# 3. CALL Ollama (local model, on your PC) to generate the answer
#
# What is Ollama?
# Ollama is a free software that runs AI models
# directly on YOUR computer. No internet needed, no
# quota, no limit. The model used is gemma-numerical-e2b
# (4.95 GB in Q8_0), fine-tuned on 144 bilingual numerical-analysis
# examples. Final loss: 3.22 (trained on April 27, 2026 on a T4).
#
# The tutor uses Ollama to stay local, predictable and GDPR-friendly.
#
# What is LangChain?
# LangChain is the assistant that prepares the file (the prompt),
# gives it to the expert (Ollama), and retrieves its answer.
# ============================================================

import logging
import re
import time

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.core.config import get_settings
from app.services.rag_service import ConceptContext

logger = logging.getLogger(__name__)
settings = get_settings()


# ============================================================
# Bilingual helpers: language detection + level mapping
# ============================================================
# Internal mapping of the (mastery-based) level to the fine-tune
# dataset tags (beginner / intermediate / advanced)
_COMPLEXITY_TO_TAG = {
    "simplified": "beginner",
    "standard": "intermediate",
    "rigorous": "advanced",
}

# Map the student's GLOBAL level (Etudiant.niveau_actuel) to the content
# complexity and to a representative mastery value. This lets the tutor and
# the quizzes adapt to the student's OVERALL level (beginner / intermediate /
# advanced) rather than to the mastery of one specific concept.
_LEVEL_TO_COMPLEXITY = {
    "beginner": "simplified",
    "intermediate": "standard",
    "advanced": "rigorous",
}
_LEVEL_TO_MASTERY = {
    "beginner": 15.0,
    "intermediate": 50.0,
    "advanced": 85.0,
}

# Marker words for quick language detection (FR vs EN)
_FR_MARKERS = {
    "qu'est", "qu est", "comment", "pourquoi", "quelle", "quel",
    "donne", "expliquer", "explique", "calculer", "calcul",
    "trouver", "demontrer", "definir", "le", "la", "les", "des",
    "une", "un", "est-ce", "que", "pour", "avec", "sans",
}
_EN_MARKERS = {
    "what", "how", "why", "which", "when", "explain", "calculate",
    "find", "prove", "define", "the", "is", "are", "compute",
    "derive", "describe", "evaluate", "show",
}


def detect_language(text: str) -> str:
    """
    Detect whether the question is in French or English.
    Simple method by counting marker words (sufficient for short Q/A).
    Returns 'fr' or 'en'.
    """
    if not text:
        return "fr"
    words = set(re.findall(r"[a-zA-Z']+", text.lower()))
    fr_score = len(words & _FR_MARKERS)
    en_score = len(words & _EN_MARKERS)
    return "en" if en_score > fr_score else "fr"


def normalize_language(language: str | None, fallback_text: str = "") -> str:
    """Return a supported language code, defaulting to English."""
    if language in {"en", "fr"}:
        return language
    if fallback_text:
        return detect_language(fallback_text)
    return "en"


def wrap_with_bilingual_tags(
    question: str,
    complexity: str,
    language: str | None = None,
) -> str:
    """
    Prefix the user question with the tags [level: ...] [lang: ...]
    expected by the bilingual fine-tuned Gemma E2B model.

    Example:
        Input  : "Qu'est-ce que l'interpolation de Lagrange ?", "simplified"
        Output : "[level: beginner] [lang: fr] Qu'est-ce que l'interpolation de Lagrange ?"
    """
    lang = normalize_language(language, question)
    level = _COMPLEXITY_TO_TAG.get(complexity, "intermediate")
    return f"[level: {level}] [lang: {lang}] {question}"


class LLMService:
    """
    Service that manages all communication with the local Ollama AI model.

    It has 3 responsibilities:
    1. Determine the complexity level (simplified/standard/rigorous)
    2. Build the system prompt with the student's context
    3. Call Ollama (local fine-tuned Gemma) to generate the answer

    Architecture:
    ┌──────────────────────────────────────┐
    │  Ollama (gemma-numerical-e2b, local) │
    └──────────────────────────────────────┘
    If Ollama is not running, the tutor returns a clear error.
    """

    def __init__(self):
        """
        Initialize BOTH LLM clients (Ollama + OpenAI) in parallel.

        Architecture:
          - `self._clients`: dict { "ollama": <ChatOllama>, "openai": <ChatOpenAI> }
            contains the clients that succeeded in their initialization.
          - `self.provider`: DEFAULT provider (used when the caller
            does not explicitly specify a provider).
          - `self.llm`: shortcut to `self._clients[self.provider]`,
            kept for compatibility with the existing code.

        Advantage of pre-loading both: the user can switch between
        local Gemma and GPT-4o-mini per request without restarting the backend.
        """
        self._clients: dict[str, object] = {}
        self._models: dict[str, str] = {}

        # Default provider from .env (used if the request specifies nothing)
        self.provider = (settings.LLM_PROVIDER or "ollama").lower().strip()

        # We try to initialize BOTH, regardless of the default provider.
        # That way, the user can switch live if the other is available.
        self._init_ollama()
        self._init_openai()

        # Shortcuts for compatibility with the existing code.
        self.llm = self._clients.get(self.provider)
        self.model_name = self._models.get(self.provider, settings.OLLAMA_MODEL)
        # Safeguard: keep the `ollama_llm` attribute for the old
        # call sites that might have referenced it before the refactor.
        self.ollama_llm = self.llm

    # ----------------------------------------------------------
    # Client resolution based on a possible override
    # ----------------------------------------------------------
    def resolve_provider(self, override: str | None = None) -> str:
        """Return the effective provider to use for this call.

        - If `override` is passed and that provider is available, we use it.
        - Otherwise we fall back to the default provider (`self.provider`).
        - Otherwise we take the first available client (any one).
        """
        if override:
            o = override.lower().strip()
            if o in self._clients:
                return o
        if self.provider in self._clients:
            return self.provider
        # Last resort: first available client
        if self._clients:
            return next(iter(self._clients.keys()))
        return self.provider  # may return a name but without a client (detected later)

    def llm_for(self, override: str | None = None):
        """Return the LangChain client matching the requested provider,
        or None if none is available."""
        prov = self.resolve_provider(override)
        return self._clients.get(prov)

    def model_name_for(self, override: str | None = None) -> str:
        """Return the name of the model used for this call."""
        prov = self.resolve_provider(override)
        return self._models.get(prov, "unknown")

    def available_providers(self) -> list[str]:
        """List of the providers actually available (initialized successfully)."""
        return list(self._clients.keys())

    def _init_ollama(self) -> None:
        """Initialize Ollama (local provider). Stores the client in self._clients['ollama']."""
        try:
            from langchain_ollama import ChatOllama
            # Headers to bypass ngrok free / Cloudflare in demo tunnel mode.
            ollama_headers = {
                "ngrok-skip-browser-warning": "true",
                "User-Agent": "Mozilla/5.0 (compatible; Backend-Tutor-IA/1.0)",
            }
            # If the user forced LLM_MODEL_NAME and the default is ollama,
            # we use it. Otherwise (e.g. default openai), we take OLLAMA_MODEL.
            model_to_use = (
                settings.LLM_MODEL_NAME
                if self.provider == "ollama" and settings.LLM_MODEL_NAME
                else settings.OLLAMA_MODEL
            )
            client = ChatOllama(
                model=model_to_use,
                temperature=settings.LLM_TEMPERATURE,
                num_predict=settings.LLM_MAX_TOKENS,
                num_ctx=4096,
                base_url=settings.OLLAMA_BASE_URL,
                client_kwargs={"headers": ollama_headers},
            )
            self._clients["ollama"] = client
            self._models["ollama"] = model_to_use
            logger.info("Provider 'ollama' charge : model=%s", model_to_use)
        except ImportError:
            logger.warning("langchain-ollama non installe - le provider 'ollama' ne sera pas disponible")
        except Exception as e:
            logger.warning("Provider 'ollama' indisponible : %s", e)

    def bind_json(self, override: str | None = None):
        """
        Return a variant of the LLM forced to produce valid JSON.

        Unifies the two providers:
          - Ollama: uses .bind(format="json")
          - OpenAI: uses .bind(response_format={"type": "json_object"})

        Used by quiz_service and feedback_service to avoid
        malformed LLM responses (text before/after the JSON).

        If `override` is specified, uses that precise provider.
        """
        client = self.llm_for(override)
        if client is None:
            return None
        prov = self.resolve_provider(override)
        if prov == "openai":
            return client.bind(response_format={"type": "json_object"})
        return client.bind(format="json")

    def _init_openai(self) -> None:
        """Initialize OpenAI (cloud provider). Stores the client in self._clients['openai']."""
        if not settings.OPENAI_API_KEY:
            logger.info(
                "Provider 'openai' non charge : OPENAI_API_KEY vide dans .env. "
                "Pour activer GPT-4o-mini, ajoute la cle depuis https://platform.openai.com/api-keys"
            )
            return
        try:
            from langchain_openai import ChatOpenAI
            # If the default is openai and a specific name is given, we use it.
            # Otherwise we take gpt-4o-mini (best quality/price ratio).
            model_to_use = (
                settings.LLM_MODEL_NAME
                if self.provider == "openai" and settings.LLM_MODEL_NAME
                else "gpt-4o-mini"
            )
            client = ChatOpenAI(
                model=model_to_use,
                api_key=settings.OPENAI_API_KEY,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS,
                timeout=60,
            )
            self._clients["openai"] = client
            self._models["openai"] = model_to_use
            logger.info("Provider 'openai' charge : model=%s", model_to_use)
        except ImportError:
            logger.error(
                "langchain-openai non installe. Lance : "
                "pip install langchain-openai"
            )
        except Exception as e:
            logger.error("OpenAI non disponible : %s", e)

    # ----------------------------------------------------------
    # METHOD 1: Determine the complexity level
    # ----------------------------------------------------------
    def get_complexity_level(self, mastery: float) -> str:
        """
        Convert the mastery percentage into a complexity level.

        This is the key to adaptive learning:
        - A beginner receives simple explanations with analogies
        - An intermediate receives formulas with examples
        - An advanced learner receives rigorous proofs

        Thresholds:
        - [0%, 30%)   -> "simplified"  (beginner)
        - [30%, 70%)  -> "standard"    (intermediate)
        - [70%, 100%] -> "rigorous"    (advanced)

        Parameters:
            mastery: mastery level (0 to 100)

        Returns:
            "simplified", "standard", or "rigorous"
        """
        if mastery < 30:
            return "simplified"
        elif mastery < 70:
            return "standard"
        else:
            return "rigorous"

    def complexity_from_level(self, niveau: str | None) -> str:
        """Map the student's GLOBAL level (niveau_actuel) to a content complexity.

        Used so the tutor adapts to the student's OVERALL level rather than to
        the mastery of one specific concept.
        """
        return _LEVEL_TO_COMPLEXITY.get((niveau or "beginner").lower(), "simplified")

    def mastery_from_level(self, niveau: str | None) -> float:
        """Representative mastery value for the student's global level
        (consumed by the quiz difficulty thresholds)."""
        return _LEVEL_TO_MASTERY.get((niveau or "beginner").lower(), 15.0)

    # ----------------------------------------------------------
    # METHOD 2: Build the system prompt
    # ----------------------------------------------------------
    def build_system_prompt(self, context: ConceptContext, language: str = "en") -> str:
        """
        Build the system prompt sent to the AI model.

        It is the most important prompt of the whole application.
        It tells the model:
        - WHO it is (a tutor expert in numerical analysis)
        - WHICH concept the student is studying
        - WHAT their level is (to adapt the complexity)
        - WHICH prerequisites they master or not
        - HOW to answer (LaTeX, step by step, etc.)

        It is thanks to this prompt that the answers are personalized.
        Without it, the AI would give an identical generic answer
        for all students.

        Parameters:
            context: the ConceptContext filled by the RAG Service

        Returns:
            The system prompt (string) to send to the model
        """
        # Adapt to the student's GLOBAL level (niveau_actuel), not to the
        # mastery of this specific concept.
        complexity = self.complexity_from_level(getattr(context, "student_level", "beginner"))
        language = normalize_language(language)

        # --- Build the prerequisites section ---
        prereqs_text = ""
        weak_prereqs = []  # Weak prerequisites (< 70%)

        for prereq in context.prerequisites:
            mastery = prereq.get("mastery", 0)
            status_emoji = "✅" if prereq["status"] == "mastered" else "⚠️"
            prereqs_text += f"  {status_emoji} {prereq['name']} : {mastery:.0f}% de maitrise\n"

            # Identify the weak prerequisites
            if mastery < settings.MASTERY_THRESHOLD:
                weak_prereqs.append(prereq["name"])

        # --- Build the resources section ---
        resources_text = ""
        for resource in context.resources:
            resources_text += f"  - {resource.get('title', 'Ressource')} ({resource.get('type', 'document')})\n"

        # --- Instructions per level ---
        if complexity == "simplified":
            complexity_instructions = """
NIVEAU DE L'ETUDIANT : DEBUTANT (maitrise < 30%)
Instructions speciales :
- Utilise un langage SIMPLE et des analogies du quotidien
- Commence par le concept le plus basique avant d'aller plus loin
- Donne des exemples NUMERIQUES concrets (pas juste des formules abstraites)
- Evite les preuves mathematiques formelles
- Si des prerequis sont faibles, EXPLIQUE-LES brievement d'abord
- Encourage l'etudiant ("C'est normal de trouver ca difficile au debut")
"""
        elif complexity == "standard":
            complexity_instructions = """
NIVEAU DE L'ETUDIANT : INTERMEDIAIRE (maitrise 30-70%)
Instructions speciales :
- Equilibre entre rigueur mathematique et clarte
- Utilise les formules LaTeX avec des explications de chaque terme
- Donne un exemple numerique apres chaque formule
- Mentionne les cas particuliers importants
- Compare avec les methodes alternatives quand c'est pertinent
"""
        else:  # rigorous
            complexity_instructions = """
NIVEAU DE L'ETUDIANT : AVANCE (maitrise > 70%)
Instructions speciales :
- Sois rigoureux mathematiquement (preuves, theoremes, lemmes)
- Discute la convergence, la stabilite, la complexite algorithmique
- Compare les ordres d'erreur entre methodes (O(h²) vs O(h⁴))
- Mentionne les applications en ingenierie et calcul scientifique
- Pose des questions de reflexion pour approfondir
"""

        language_rule = (
            "Reponds exclusivement en FRANCAIS. Traduis les titres, explications, "
            "conseils, exercices et feedbacks en francais."
            if language == "fr"
            else
            "Answer exclusively in ENGLISH. Translate headings, explanations, "
            "advice, exercises and feedback into English."
        )

        # --- Assembly of the final prompt ---
        prompt = f"""Tu es un tuteur expert en Analyse Numerique et Calcul Scientifique.
Tu travailles pour une plateforme d'apprentissage adaptatif a ESPRIT (ecole d'ingenieurs).

CONCEPT ACTUEL : {context.concept_name}
{f"DESCRIPTION : {context.description}" if context.description else ""}
{f"MODULE : {context.module_name}" if context.module_name else ""}
{f"DIFFICULTE : {context.difficulty}" if context.difficulty else ""}

MAITRISE DE L'ETUDIANT SUR CE CONCEPT : {context.student_mastery:.0f}%

{complexity_instructions}

PREREQUIS DE L'ETUDIANT :
{prereqs_text if prereqs_text else "  Aucun prerequis enregistre."}

{f"⚠️ ATTENTION : L'etudiant a des LACUNES sur : {', '.join(weak_prereqs)}. Adapte ton explication en consequence." if weak_prereqs else ""}

RESSOURCES DISPONIBLES :
{resources_text if resources_text else "  Aucune ressource specifique."}

REGLES STRICTES :
1. Utilise la notation LaTeX pour TOUTES les formules mathematiques
   Exemples : $f(x) = x^2$, $\\int_a^b f(x)dx$, $\\frac{{{{dy}}}}{{{{dx}}}}$
2. Structure ta reponse en etapes numerotees
3. RESTE dans le domaine de l'analyse numerique — refuse poliment les questions hors-sujet
4. Si l'etudiant a des prerequis faibles, commence par un rappel rapide
5. Termine par une suggestion : soit un exercice, soit le prochain concept a etudier
6. {language_rule}
7. Sois encourageant et bienveillant

IMPORTANT : Tu es un tuteur pedagogique, pas un chatbot generaliste.
Si la question n'est pas liee a l'analyse numerique ou au calcul scientifique,
reponds poliment que tu es specialise dans ce domaine et redirige l'etudiant."""

        return prompt

    # ----------------------------------------------------------
    # METHOD 3: Call Ollama via LangChain
    # ----------------------------------------------------------
    async def _call_ollama(self, messages: list) -> str:
        """
        Call Ollama via LangChain and return its answer.

        Parameters:
            messages: the list of messages (system + history + question)

        Returns:
            The model's answer (string)

        Raises an exception if the call fails.
        """
        # IMPORTANT: we DO NOT USE ChatPromptTemplate.from_messages() here
        # because it interprets the prompt's {...} as template variables.
        # The LaTeX formulas ($\frac{dy}{dx}$) and the JSON in the prompts
        # contain {} that crash the parser.
        # Instead, we convert our (role, content) tuples into Message objects
        # and call llm.ainvoke() directly (no template interpolation).
        msg_objects = []
        for role, content in messages:
            if role == "system":
                msg_objects.append(SystemMessage(content=content))
            elif role == "human":
                msg_objects.append(HumanMessage(content=content))
            elif role == "ai":
                msg_objects.append(AIMessage(content=content))

        # ainvoke = ASYNCHRONOUS call (the "a" = async)
        # Why async? Because the model takes 1-30 seconds to answer.
        # During that time, our server can handle other requests.
        # Depending on the provider, the LLM used is self.llm (Ollama OR OpenAI).
        t_start = time.time()
        response = await self.llm.ainvoke(msg_objects)
        elapsed = time.time() - t_start

        n_chars = len(response.content)
        # Rough estimate: ~4 chars per token in French
        tokens_per_sec = (n_chars / 4) / elapsed if elapsed > 0 else 0
        logger.info(
            "Reponse %s (%s) : %.1fs, %d chars (~%.1f tok/s)",
            self.provider, self.model_name, elapsed, n_chars, tokens_per_sec,
        )

        return response.content

    # ----------------------------------------------------------
    # METHOD 4: Generate the adaptive answer (Ollama only)
    # ----------------------------------------------------------
    async def generate_response(
        self, question: str, context: ConceptContext,
        conversation_history: list[dict[str, str]] = None,
        language: str = "en",
        provider_override: str | None = None,
    ) -> str:
        """
        Send the question to the local Gemma model and return the answer.

        This is the main method called by the router.
        It follows this logic:

        1. Build the messages (system + history + tagged question)
        2. Call Ollama (gemma-numerical-e2b)
        3. If Ollama fails -> return a clear error message

        Parameters:
            question: the student's question
            context: the ConceptContext filled by the RAG Service
            conversation_history: the previous messages (for the context)

        Returns:
            The model's answer (string with LaTeX)
        """
        # Resolution of the effective provider for this call.
        # If the frontend sent provider_override="openai" but OpenAI
        # is not loaded, we fall back to the default provider.
        active_provider = self.resolve_provider(provider_override)
        active_client = self.llm_for(provider_override)
        active_model = self.model_name_for(provider_override)

        # If the LLM is not available (according to the resolved provider)
        if active_client is None:
            if active_provider == "openai":
                return (
                    "⚠️ Le tuteur IA (OpenAI) n'est pas configure.\n\n"
                    "**Configuration requise** :\n"
                    "1. Cree un compte sur https://platform.openai.com/signup\n"
                    "2. Genere une cle API : https://platform.openai.com/api-keys\n"
                    "3. Ajoute dans .env : OPENAI_API_KEY=sk-...\n"
                    "4. pip install langchain-openai\n\n"
                    "Puis redemarrez le serveur backend."
                )
            return (
                "⚠️ Le tuteur IA (Ollama) n'est pas configure.\n\n"
                "**Configuration requise** :\n"
                "1. Installez Ollama : https://ollama.com\n"
                "2. Importez le modele Gemma fine-tune :\n"
                "   `ollama create gemma-numerical-e2b -f Module de Math/Modelfile_E2B`\n"
                "3. Verifiez : `ollama list` doit afficher gemma-numerical-e2b\n"
                "4. Assurez-vous qu'Ollama tourne : `ollama serve`\n"
                "5. pip install langchain-ollama\n\n"
                "Puis redemarrez le serveur backend."
            )

        # --- Build the messages for LangChain ---
        # LangChain uses a "messages" format like a conversation:
        # - "system": the instructions (our adaptive prompt)
        # - "human": the student's messages
        # - "ai": the model's previous answers
        messages = []

        language = normalize_language(language, question)

        # System message (the briefing)
        system_prompt = self.build_system_prompt(context, language=language)
        messages.append(("system", system_prompt))

        # Conversation history (if available)
        # This lets the model "remember" the previous exchanges
        if conversation_history:
            for msg in conversation_history[-6:]:  # Keep the last 6 messages
                role = "human" if msg["role"] == "student" else "ai"
                messages.append((role, msg["content"]))

        # The student's current question prefixed with the bilingual tags
        # [level: beginner|intermediate|advanced] [lang: fr|en] that the
        # fine-tuned Gemma E2B model expects to adapt its style and language.
        complexity = self.get_complexity_level(context.student_mastery)
        tagged_question = wrap_with_bilingual_tags(question, complexity, language)
        logger.info("Tagged question: %s...", tagged_question[:80])
        messages.append(("human", tagged_question))

        # --- Call the LLM (Ollama or OpenAI depending on active_provider) ---
        try:
            start_time = time.time()
            provider_label = active_provider.upper()
            logger.info(
                "%s START model=%s complexity=%s lang=%s question=%s...",
                provider_label,
                active_model,
                complexity,
                language,
                question[:80],
            )

            response = await self._call_with_client(messages, active_client, active_provider, active_model)

            elapsed = time.time() - start_time
            response_words = len(response.split()) if response else 0
            speed = response_words / elapsed if elapsed > 0 else 0

            logger.info(
                "%s DONE %.1fs, ~%d words, %.1f w/s, response=%s...",
                provider_label,
                elapsed,
                response_words,
                speed,
                response[:100],
            )
            return response

        except Exception as e:
            logger.error("Echec %s : %s", active_provider, e)
            return (
                f"❌ Le tuteur IA ({active_provider}) est temporairement indisponible.\n\n"
                f"Erreur : {str(e)}\n\n"
                "💡 Verifie :\n"
                "1. Qu'Ollama est lance (`ollama serve`) si tu utilises Gemma local\n"
                "2. Que ta cle OpenAI est valide si tu utilises GPT-4o-mini\n"
                "3. Que ta connexion internet fonctionne (pour OpenAI)"
            )

    async def _call_with_client(self, messages: list, client, provider: str, model: str) -> str:
        """Call a specific LLM client (Ollama or OpenAI) with the messages.

        Variant of _call_ollama that takes the client as a parameter, to let
        generate_response switch dynamically between Ollama and OpenAI.
        """
        msg_objects = []
        for role, content in messages:
            if role == "system":
                msg_objects.append(SystemMessage(content=content))
            elif role == "human":
                msg_objects.append(HumanMessage(content=content))
            elif role == "ai":
                msg_objects.append(AIMessage(content=content))

        t_start = time.time()
        response = await client.ainvoke(msg_objects)
        elapsed = time.time() - t_start

        n_chars = len(response.content)
        tokens_per_sec = (n_chars / 4) / elapsed if elapsed > 0 else 0
        logger.info(
            "Reponse %s (%s) : %.1fs, %d chars (~%.1f tok/s)",
            provider, model, elapsed, n_chars, tokens_per_sec,
        )
        return response.content


# Global instance (reused everywhere)
llm_service = LLMService()
