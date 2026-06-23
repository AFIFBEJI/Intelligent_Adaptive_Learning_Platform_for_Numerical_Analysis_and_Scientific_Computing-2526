# ============================================================
# Service LLM — Communication avec Ollama (Gemma fine-tune local)
# ============================================================
# C'est quoi ce fichier ?
#
# Ce service fait 3 choses :
# 1. CONSTRUIRE un prompt adaptatif (les instructions pour l'IA)
#    base sur le niveau de l'etudiant et le contexte Neo4j
# 2. PREFIXER la question avec les tags bilingues attendus par
#    le modele fine-tune Gemma E2B : [level: ...] [lang: ...]
# 3. APPELER Ollama (modele local, sur ton PC) pour generer la reponse
#
# C'est quoi Ollama ?
# Ollama est un logiciel gratuit qui fait tourner des modeles d'IA
# directement sur TON ordinateur. Pas besoin d'internet, pas de
# quota, pas de limite. Le modele utilise est gemma-numerical-e2b
# (4.95 Go en Q8_0), fine-tune sur 144 exemples bilingues d'analyse
# numerique. Loss finale : 3.22 (entraine le 27 avril 2026 sur T4).
#
# Le tuteur utilise Ollama pour rester local, predictable et RGPD-friendly.
#
# C'est quoi LangChain ?
# LangChain est l'assistant qui prepare le dossier (le prompt),
# le donne a l'expert (Ollama), et recupere sa reponse.
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
# Helpers bilingues : detection langue + mapping niveau
# ============================================================
# Mapping interne du niveau (mastery-based) vers les tags du dataset
# fine-tune (beginner / intermediate / advanced)
_COMPLEXITY_TO_TAG = {
    "simplified": "beginner",
    "standard": "intermediate",
    "rigorous": "advanced",
}

# Mots-marqueurs pour la detection rapide de langue (FR vs EN)
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
    Detecte si la question est en francais ou en anglais.
    Methode simple par comptage de mots-marqueurs (suffisant pour Q/R courtes).
    Retourne 'fr' ou 'en'.
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
    Prefixe la question utilisateur avec les tags [level: ...] [lang: ...]
    attendus par le modele fine-tune Gemma E2B bilingue.

    Exemple :
        Input  : "Qu'est-ce que l'interpolation de Lagrange ?", "simplified"
        Output : "[level: beginner] [lang: fr] Qu'est-ce que l'interpolation de Lagrange ?"
    """
    lang = normalize_language(language, question)
    level = _COMPLEXITY_TO_TAG.get(complexity, "intermediate")
    return f"[level: {level}] [lang: {lang}] {question}"


class LLMService:
    """
    Service qui gere toute la communication avec le modele d'IA local Ollama.

    Il a 3 responsabilites :
    1. Determiner le niveau de complexite (simplifie/standard/rigoureux)
    2. Construire le prompt systeme avec le contexte de l'etudiant
    3. Appeler Ollama (Gemma fine-tune local) pour generer la reponse

    Architecture :
    ┌──────────────────────────────────────┐
    │  Ollama (gemma-numerical-e2b, local) │
    └──────────────────────────────────────┘
    Si Ollama n'est pas lance, le tuteur retourne une erreur claire.
    """

    def __init__(self):
        """
        Initialise les DEUX clients LLM (Ollama + OpenAI) en parallele.

        Architecture :
          - `self._clients` : dict { "ollama": <ChatOllama>, "openai": <ChatOpenAI> }
            contient les clients qui ont reussi leur initialisation.
          - `self.provider` : provider PAR DEFAUT (utilise quand l'appelant
            ne specifie pas explicitement un provider).
          - `self.llm` : raccourci vers `self._clients[self.provider]`,
            conserve pour la compatibilite avec le code existant.

        Avantage de pre-charger les deux : l'utilisateur peut basculer entre
        Gemma local et GPT-4o-mini par requete sans redemarrer le backend.
        """
        self._clients: dict[str, object] = {}
        self._models: dict[str, str] = {}

        # Provider par defaut depuis .env (utilise si la requete ne specifie rien)
        self.provider = (settings.LLM_PROVIDER or "ollama").lower().strip()

        # On essaie d'initialiser les DEUX, peu importe le provider par defaut.
        # Comme ca, l'utilisateur peut switcher en live si l'autre est dispo.
        self._init_ollama()
        self._init_openai()

        # Raccourcis pour la compatibilite avec le code existant.
        self.llm = self._clients.get(self.provider)
        self.model_name = self._models.get(self.provider, settings.OLLAMA_MODEL)
        # Garde-fou : conserver l'attribut `ollama_llm` pour les anciens
        # points d'appel qui auraient pu y faire reference avant le refactor.
        self.ollama_llm = self.llm

    # ----------------------------------------------------------
    # Resolution du client en fonction d'un override eventuel
    # ----------------------------------------------------------
    def resolve_provider(self, override: str | None = None) -> str:
        """Retourne le provider effectif a utiliser pour cet appel.

        - Si `override` est passe et que ce provider est disponible, on l'utilise.
        - Sinon on tombe sur le provider par defaut (`self.provider`).
        - Sinon on prend le premier client disponible (n'importe lequel).
        """
        if override:
            o = override.lower().strip()
            if o in self._clients:
                return o
        if self.provider in self._clients:
            return self.provider
        # Dernier recours : premier client disponible
        if self._clients:
            return next(iter(self._clients.keys()))
        return self.provider  # peut renvoyer un nom mais sans client (sera detecte plus tard)

    def llm_for(self, override: str | None = None):
        """Retourne le client LangChain correspondant au provider demande,
        ou None si aucun n'est disponible."""
        prov = self.resolve_provider(override)
        return self._clients.get(prov)

    def model_name_for(self, override: str | None = None) -> str:
        """Retourne le nom du modele utilise pour cet appel."""
        prov = self.resolve_provider(override)
        return self._models.get(prov, "unknown")

    def available_providers(self) -> list[str]:
        """Liste des providers effectivement disponibles (initialises avec succes)."""
        return list(self._clients.keys())

    def _init_ollama(self) -> None:
        """Initialise Ollama (provider local). Stocke le client dans self._clients['ollama']."""
        try:
            from langchain_ollama import ChatOllama
            # Headers pour bypasser ngrok free / Cloudflare en mode tunnel demo.
            ollama_headers = {
                "ngrok-skip-browser-warning": "true",
                "User-Agent": "Mozilla/5.0 (compatible; Backend-Tutor-IA/1.0)",
            }
            # Si l'utilisateur a force LLM_MODEL_NAME et que le defaut est ollama,
            # on l'utilise. Sinon (ex: defaut openai), on prend OLLAMA_MODEL.
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
        Retourne une variante du LLM forcee a produire du JSON valide.

        Unifie les deux providers :
          - Ollama : utilise .bind(format="json")
          - OpenAI : utilise .bind(response_format={"type": "json_object"})

        Utilise par quiz_service et feedback_service pour eviter les
        reponses LLM mal formees (texte avant/apres le JSON).

        Si `override` est specifie, utilise ce provider precis.
        """
        client = self.llm_for(override)
        if client is None:
            return None
        prov = self.resolve_provider(override)
        if prov == "openai":
            return client.bind(response_format={"type": "json_object"})
        return client.bind(format="json")

    def _init_openai(self) -> None:
        """Initialise OpenAI (provider cloud). Stocke le client dans self._clients['openai']."""
        if not settings.OPENAI_API_KEY:
            logger.info(
                "Provider 'openai' non charge : OPENAI_API_KEY vide dans .env. "
                "Pour activer GPT-4o-mini, ajoute la cle depuis https://platform.openai.com/api-keys"
            )
            return
        try:
            from langchain_openai import ChatOpenAI
            # Si le defaut est openai et qu'un nom precis est specifie, on l'utilise.
            # Sinon on prend gpt-4o-mini (meilleur rapport qualite/prix).
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
    # METHODE 1 : Determiner le niveau de complexite
    # ----------------------------------------------------------
    def get_complexity_level(self, mastery: float) -> str:
        """
        Convertit le pourcentage de maitrise en niveau de complexite.

        C'est la cle de l'apprentissage adaptatif :
        - Un debutant recoit des explications simples avec des analogies
        - Un intermediaire recoit des formules avec des exemples
        - Un avance recoit des preuves rigoureuses

        Seuils :
        - [0%, 30%)   → "simplified"  (debutant)
        - [30%, 70%)  → "standard"    (intermediaire)
        - [70%, 100%] → "rigorous"    (avance)

        Parametres :
            mastery : niveau de maitrise (0 a 100)

        Retourne :
            "simplified", "standard", ou "rigorous"
        """
        if mastery < 30:
            return "simplified"
        elif mastery < 70:
            return "standard"
        else:
            return "rigorous"

    # ----------------------------------------------------------
    # METHODE 2 : Construire le prompt systeme
    # ----------------------------------------------------------
    def build_system_prompt(self, context: ConceptContext, language: str = "en") -> str:
        """
        Construit le prompt systeme envoye au modele d'IA.

        C'est le prompt le plus important de toute l'application.
        Il dit au modele :
        - QUI il est (un tuteur expert en analyse numerique)
        - QUEL concept l'etudiant etudie
        - QUEL est son niveau (pour adapter la complexite)
        - QUELS prerequis il maitrise ou non
        - COMMENT repondre (LaTeX, etape par etape, etc.)

        C'est grace a ce prompt que les reponses sont personnalisees.
        Sans lui, l'IA donnerait une reponse generique identique
        pour tous les etudiants.

        Parametres :
            context : le ConceptContext rempli par le RAG Service

        Retourne :
            Le prompt systeme (string) a envoyer au modele
        """
        complexity = self.get_complexity_level(context.student_mastery)
        language = normalize_language(language)

        # --- Construire la section des prerequis ---
        prereqs_text = ""
        weak_prereqs = []  # Prerequis faibles (< 70%)

        for prereq in context.prerequisites:
            mastery = prereq.get("mastery", 0)
            status_emoji = "✅" if prereq["status"] == "mastered" else "⚠️"
            prereqs_text += f"  {status_emoji} {prereq['name']} : {mastery:.0f}% de maitrise\n"

            # Identifier les prerequis faibles
            if mastery < settings.MASTERY_THRESHOLD:
                weak_prereqs.append(prereq["name"])

        # --- Construire la section des ressources ---
        resources_text = ""
        for resource in context.resources:
            resources_text += f"  - {resource.get('title', 'Ressource')} ({resource.get('type', 'document')})\n"

        # --- Instructions selon le niveau ---
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

        # --- Assemblage du prompt final ---
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
    # METHODE 3 : Appeler Ollama via LangChain
    # ----------------------------------------------------------
    async def _call_ollama(self, messages: list) -> str:
        """
        Appelle Ollama via LangChain et retourne sa reponse.

        Parametres :
            messages : la liste de messages (system + historique + question)

        Retourne :
            La reponse du modele (string)

        Leve une exception si l'appel echoue.
        """
        # IMPORTANT : on N'UTILISE PAS ChatPromptTemplate.from_messages() ici
        # parce qu'il interprete les {...} du prompt comme des variables de template.
        # Les formules LaTeX ($\frac{dy}{dx}$) et les JSON dans les prompts
        # contiennent des {} qui plantent le parser.
        # A la place, on convertit nos tuples (role, content) en objets Message
        # et on appelle llm.ainvoke() directement (pas de template interpolation).
        msg_objects = []
        for role, content in messages:
            if role == "system":
                msg_objects.append(SystemMessage(content=content))
            elif role == "human":
                msg_objects.append(HumanMessage(content=content))
            elif role == "ai":
                msg_objects.append(AIMessage(content=content))

        # ainvoke = appel ASYNCHRONE (le "a" = async)
        # Pourquoi async ? Parce que le modele met 1-30 secondes a repondre.
        # Pendant ce temps, notre serveur peut traiter d'autres requetes.
        # Selon le provider, le LLM utilise est self.llm (Ollama OU OpenAI).
        t_start = time.time()
        response = await self.llm.ainvoke(msg_objects)
        elapsed = time.time() - t_start

        n_chars = len(response.content)
        # Estimation grossiere : ~4 chars par token en francais
        tokens_per_sec = (n_chars / 4) / elapsed if elapsed > 0 else 0
        logger.info(
            "Reponse %s (%s) : %.1fs, %d chars (~%.1f tok/s)",
            self.provider, self.model_name, elapsed, n_chars, tokens_per_sec,
        )

        return response.content

    # ----------------------------------------------------------
    # METHODE 4 : Generer la reponse adaptative (Ollama uniquement)
    # ----------------------------------------------------------
    async def generate_response(
        self, question: str, context: ConceptContext,
        conversation_history: list[dict[str, str]] = None,
        language: str = "en",
        provider_override: str | None = None,
    ) -> str:
        """
        Envoie la question au modele Gemma local et retourne la reponse.

        C'est la methode principale appelee par le router.
        Elle suit cette logique :

        1. Construire les messages (system + historique + question taggee)
        2. Appeler Ollama (gemma-numerical-e2b)
        3. Si Ollama echoue -> retourner un message d'erreur clair

        Parametres :
            question : la question de l'etudiant
            context : le ConceptContext rempli par le RAG Service
            conversation_history : les messages precedents (pour le contexte)

        Retourne :
            La reponse du modele (string avec du LaTeX)
        """
        # Resolution du provider effectif pour cet appel.
        # Si le frontend a envoye provider_override="openai" mais qu'OpenAI
        # n'est pas charge, on tombe sur le provider par defaut.
        active_provider = self.resolve_provider(provider_override)
        active_client = self.llm_for(provider_override)
        active_model = self.model_name_for(provider_override)

        # Si le LLM n'est pas disponible (selon le provider resolu)
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

        # --- Construire les messages pour LangChain ---
        # LangChain utilise un format de "messages" comme une conversation :
        # - "system" : les instructions (notre prompt adaptatif)
        # - "human" : les messages de l'etudiant
        # - "ai" : les reponses precedentes du modele
        messages = []

        language = normalize_language(language, question)

        # Message systeme (le briefing)
        system_prompt = self.build_system_prompt(context, language=language)
        messages.append(("system", system_prompt))

        # Historique de conversation (si disponible)
        # Ca permet au modele de se "souvenir" des echanges precedents
        if conversation_history:
            for msg in conversation_history[-6:]:  # Garder les 6 derniers messages
                role = "human" if msg["role"] == "student" else "ai"
                messages.append((role, msg["content"]))

        # La question actuelle de l'etudiant prefixee avec les tags bilingues
        # [level: beginner|intermediate|advanced] [lang: fr|en] que le modele
        # fine-tune Gemma E2B attend pour adapter son style et sa langue.
        complexity = self.get_complexity_level(context.student_mastery)
        tagged_question = wrap_with_bilingual_tags(question, complexity, language)
        logger.info("Tagged question: %s...", tagged_question[:80])
        messages.append(("human", tagged_question))

        # --- Appel du LLM (Ollama ou OpenAI selon active_provider) ---
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
        """Appelle un client LLM specifique (Ollama ou OpenAI) avec les messages.

        Variante de _call_ollama qui prend le client en parametre, pour permettre
        a generate_response de basculer dynamiquement entre Ollama et OpenAI.
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


# Instance globale (reutilisee partout)
llm_service = LLMService()
