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
        Initialise la connexion au modele Ollama local.

        Le modele utilise est gemma-numerical-e2b (Gemma 3n E2B fine-tune
        avec LoRA r=16, 3 epochs, dataset bilingue 144 exemples). Servi
        en local via Ollama sur le port 11434.
        """
        self.ollama_llm = None
        try:
            from langchain_ollama import ChatOllama
            # Headers pour bypasser la page d'avertissement ngrok free
            # (utile uniquement si on bascule en mode tunnel pour demo) :
            # - ngrok-skip-browser-warning : contourne la page interstitielle
            # - User-Agent : evite le blocage Cloudflare sur trycloudflare.com
            ollama_headers = {
                "ngrok-skip-browser-warning": "true",
                "User-Agent": "Mozilla/5.0 (compatible; Backend-Tutor-IA/1.0)",
            }
            self.ollama_llm = ChatOllama(
                model=settings.OLLAMA_MODEL,
                temperature=settings.LLM_TEMPERATURE,
                num_predict=settings.LLM_MAX_TOKENS,
                # num_ctx = taille TOTALE de la fenetre de contexte (input + output)
                # Le Modelfile_E2B definit num_ctx=1024 par defaut, ce qui est trop juste
                # pour les quiz multi-concepts (prompt ~500 tokens + JSON ~1500 tokens).
                # On override a 4096 ici via les options runtime — Ollama autorise
                # ce genre de surcharge per-request sans recreer le modele.
                num_ctx=4096,
                # base_url = l'adresse du serveur Ollama
                # Local : http://localhost:11434
                # Distant via ngrok/cloudflare : https://xxxxx.ngrok-free.app
                base_url=settings.OLLAMA_BASE_URL,
                client_kwargs={"headers": ollama_headers},
            )
            logger.info("Ollama initialise : %s", settings.OLLAMA_MODEL)
            if settings.OLLAMA_BASE_URL and "localhost" not in settings.OLLAMA_BASE_URL:
                logger.info("Ollama via tunnel : %s", settings.OLLAMA_BASE_URL)
            logger.info("Mode OLLAMA-only actif")
        except ImportError:
            logger.warning("langchain-ollama non installe - pip install langchain-ollama")
        except Exception as e:
            logger.warning("Ollama non disponible : %s", e)

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
        # Pourquoi async ? Parce que le modele met 10-30 secondes a repondre.
        # Pendant ce temps, notre serveur peut traiter d'autres requetes.
        t_start = time.time()
        response = await self.ollama_llm.ainvoke(msg_objects)
        elapsed = time.time() - t_start

        n_chars = len(response.content)
        # Estimation grossiere : ~4 chars par token en francais
        tokens_per_sec = (n_chars / 4) / elapsed if elapsed > 0 else 0
        logger.info(
            "Reponse Ollama (%s) : %.1fs, %d chars (~%.1f tok/s)",
            settings.OLLAMA_MODEL, elapsed, n_chars, tokens_per_sec,
        )

        return response.content

    # ----------------------------------------------------------
    # METHODE 4 : Generer la reponse adaptative (Ollama uniquement)
    # ----------------------------------------------------------
    async def generate_response(
        self, question: str, context: ConceptContext,
        conversation_history: list[dict[str, str]] = None,
        language: str = "en",
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
        # Si Ollama n'est pas disponible
        if self.ollama_llm is None:
            return (
                "⚠️ Le tuteur IA n'est pas configure.\n\n"
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

        # --- Appel Ollama ---
        try:
            start_time = time.time()
            logger.info(
                "OLLAMA START model=%s complexity=%s lang=%s question=%s...",
                settings.OLLAMA_MODEL,
                complexity,
                language,
                question[:80],
            )

            response = await self._call_ollama(messages)

            elapsed = time.time() - start_time
            response_words = len(response.split()) if response else 0
            speed = response_words / elapsed if elapsed > 0 else 0

            logger.info(
                "OLLAMA DONE %.1fs, ~%d words, %.1f w/s, response=%s...",
                elapsed,
                response_words,
                speed,
                response[:100],
            )
            return response

        except Exception as e:
            logger.error("Echec Ollama : %s", e)
            return (
                f"❌ Le tuteur IA est temporairement indisponible.\n\n"
                f"Erreur : {str(e)}\n\n"
                "💡 Verifiez :\n"
                "1. Qu'Ollama est lance : `ollama serve`\n"
                f"2. Que le modele est present : `ollama list` (cherchez '{settings.OLLAMA_MODEL}')\n"
                "3. Que le port 11434 est accessible : `curl http://localhost:11434/api/version`"
            )


# Instance globale (reutilisee partout)
llm_service = LLMService()
