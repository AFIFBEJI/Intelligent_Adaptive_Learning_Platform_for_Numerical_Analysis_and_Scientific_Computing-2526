# ============================================================
# Service LLM — Communication avec Gemini + Ollama (Fallback)
# ============================================================
# C'est quoi ce fichier ?
#
# Ce service fait 3 choses :
# 1. CONSTRUIRE un prompt adaptatif (les instructions pour l'IA)
#    basé sur le niveau de l'étudiant et le contexte Neo4j
# 2. APPELER Gemini (Google, en ligne) pour générer la réponse
# 3. Si Gemini échoue (quota épuisé, erreur 429), BASCULER
#    automatiquement sur Ollama (modèle local, sur ton PC)
#
# C'est quoi le système de fallback ?
# Imagine un restaurant : tu commandes à un serveur (Gemini).
# Si ce serveur est occupé, un autre serveur (Ollama) prend
# ta commande automatiquement. Le client (l'étudiant) ne voit
# aucune différence — il reçoit juste sa réponse.
#
# C'est quoi Ollama ?
# C'est un logiciel gratuit qui fait tourner des modèles d'IA
# directement sur TON ordinateur. Pas besoin d'internet, pas
# de quota, pas de limite. Le modèle llama3.1:8b utilise ~5 Go
# de RAM (tu en as 32 Go, donc aucun problème).
#
# C'est quoi LangChain ?
# LangChain est l'assistant qui prépare le dossier (le prompt),
# le donne à l'expert (Gemini ou Ollama), et récupère sa réponse.
# Le code est IDENTIQUE pour Gemini et Ollama grâce à LangChain —
# on change juste le "connecteur" (ChatGoogleGenerativeAI vs ChatOllama).
# ============================================================

import asyncio
import logging

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import get_settings
from app.services.rag_service import ConceptContext

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMService:
    """
    Service qui gère toute la communication avec les modèles d'IA.

    Il a 4 responsabilités :
    1. Déterminer le niveau de complexité (simplifié/standard/rigoureux)
    2. Construire le prompt système avec le contexte de l'étudiant
    3. Appeler Gemini (en priorité) pour générer la réponse
    4. Si Gemini échoue → basculer automatiquement sur Ollama (local)

    Architecture de fallback :
    ┌──────────┐    erreur 429    ┌──────────┐
    │  Gemini  │ ───────────────→ │  Ollama  │
    │ (Google) │   (quota épuisé) │ (local)  │
    └──────────┘                  └──────────┘
    """

    def __init__(self):
        """
        Initialise les connexions aux modèles d'IA.

        On initialise DEUX modèles :
        1. Gemini (en ligne) — meilleur en maths, mais quota limité
        2. Ollama (local) — pas de quota, mais un peu moins bon

        Si Gemini n'est pas configuré (pas de clé API), on utilise
        directement Ollama. Si Ollama n'est pas installé non plus,
        le tuteur IA est désactivé.
        """
        # --- Modèle 1 : Gemini (en ligne, prioritaire) ---
        self.gemini_llm = None
        if settings.GOOGLE_API_KEY:
            try:
                self.gemini_llm = ChatGoogleGenerativeAI(
                    model=settings.GEMINI_MODEL,
                    google_api_key=settings.GOOGLE_API_KEY,
                    temperature=settings.LLM_TEMPERATURE,
                    max_output_tokens=settings.LLM_MAX_TOKENS,
                )
                print(f"  ✅ Gemini initialisé : {settings.GEMINI_MODEL}")
            except Exception as e:
                print(f"  ⚠️ Gemini non disponible : {e}")
        else:
            print("  ⚠️ GOOGLE_API_KEY non configurée — Gemini désactivé")

        # --- Modèle 2 : Ollama (local, fallback) ---
        # On essaie d'importer ChatOllama. Si le package n'est pas
        # installé ou Ollama n'est pas lancé, on met ollama_llm = None.
        self.ollama_llm = None
        try:
            from langchain_ollama import ChatOllama
            self.ollama_llm = ChatOllama(
                model=settings.OLLAMA_MODEL,
                temperature=settings.LLM_TEMPERATURE,
                num_predict=settings.LLM_MAX_TOKENS,
                # base_url = l'adresse du serveur Ollama sur ton PC
                # Par défaut, Ollama écoute sur http://localhost:11434
                base_url=settings.OLLAMA_BASE_URL,
            )
            print(f"  ✅ Ollama initialisé : {settings.OLLAMA_MODEL}")
        except ImportError:
            print("  ⚠️ langchain-ollama non installé — pip install langchain-ollama")
        except Exception as e:
            print(f"  ⚠️ Ollama non disponible : {e}")

        # --- Résumé de ce qui est disponible ---
        if self.gemini_llm and self.ollama_llm:
            print("  🚀 Mode HYBRIDE : Gemini (principal) + Ollama (fallback)")
        elif self.gemini_llm:
            print("  🌐 Mode GEMINI uniquement (pas de fallback)")
        elif self.ollama_llm:
            print("  💻 Mode OLLAMA uniquement (local)")
        else:
            print("  ❌ AUCUN modèle disponible ! Configurez Gemini ou Ollama.")

    # ----------------------------------------------------------
    # MÉTHODE 1 : Déterminer le niveau de complexité
    # ----------------------------------------------------------
    def get_complexity_level(self, mastery: float) -> str:
        """
        Convertit le pourcentage de maîtrise en niveau de complexité.

        C'est la clé de l'apprentissage adaptatif :
        - Un débutant reçoit des explications simples avec des analogies
        - Un intermédiaire reçoit des formules avec des exemples
        - Un avancé reçoit des preuves rigoureuses

        Seuils :
        - [0%, 30%)   → "simplified"  (débutant)
        - [30%, 70%)  → "standard"    (intermédiaire)
        - [70%, 100%] → "rigorous"    (avancé)

        Paramètres :
            mastery : niveau de maîtrise (0 à 100)

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
    # MÉTHODE 2 : Construire le prompt système
    # ----------------------------------------------------------
    def build_system_prompt(self, context: ConceptContext) -> str:
        """
        Construit le prompt système envoyé au modèle d'IA.

        C'est le prompt le plus important de toute l'application.
        Il dit au modèle :
        - QUI il est (un tuteur expert en analyse numérique)
        - QUEL concept l'étudiant étudie
        - QUEL est son niveau (pour adapter la complexité)
        - QUELS prérequis il maîtrise ou non
        - COMMENT répondre (LaTeX, étape par étape, etc.)

        C'est grâce à ce prompt que les réponses sont personnalisées.
        Sans lui, l'IA donnerait une réponse générique identique
        pour tous les étudiants.

        Paramètres :
            context : le ConceptContext rempli par le RAG Service

        Retourne :
            Le prompt système (string) à envoyer au modèle
        """
        complexity = self.get_complexity_level(context.student_mastery)

        # --- Construire la section des prérequis ---
        # On liste chaque prérequis avec le niveau de maîtrise de l'étudiant
        # pour que l'IA sache quoi l'étudiant comprend déjà ou pas
        prereqs_text = ""
        weak_prereqs = []  # Prérequis faibles (< 70%)

        for prereq in context.prerequisites:
            mastery = prereq.get("mastery", 0)
            status_emoji = "✅" if prereq["status"] == "mastered" else "⚠️"
            prereqs_text += f"  {status_emoji} {prereq['name']} : {mastery:.0f}% de maîtrise\n"

            # Identifier les prérequis faibles
            if mastery < settings.MASTERY_THRESHOLD:
                weak_prereqs.append(prereq["name"])

        # --- Construire la section des ressources ---
        resources_text = ""
        for resource in context.resources:
            resources_text += f"  - {resource.get('title', 'Ressource')} ({resource.get('type', 'document')})\n"

        # --- Instructions selon le niveau ---
        # C'est ici que l'adaptivité se passe !
        if complexity == "simplified":
            complexity_instructions = """
NIVEAU DE L'ÉTUDIANT : DÉBUTANT (maîtrise < 30%)
Instructions spéciales :
- Utilise un langage SIMPLE et des analogies du quotidien
- Commence par le concept le plus basique avant d'aller plus loin
- Donne des exemples NUMÉRIQUES concrets (pas juste des formules abstraites)
- Évite les preuves mathématiques formelles
- Si des prérequis sont faibles, EXPLIQUE-LES brièvement d'abord
- Encourage l'étudiant ("C'est normal de trouver ça difficile au début")
"""
        elif complexity == "standard":
            complexity_instructions = """
NIVEAU DE L'ÉTUDIANT : INTERMÉDIAIRE (maîtrise 30-70%)
Instructions spéciales :
- Équilibre entre rigueur mathématique et clarté
- Utilise les formules LaTeX avec des explications de chaque terme
- Donne un exemple numérique après chaque formule
- Mentionne les cas particuliers importants
- Compare avec les méthodes alternatives quand c'est pertinent
"""
        else:  # rigorous
            complexity_instructions = """
NIVEAU DE L'ÉTUDIANT : AVANCÉ (maîtrise > 70%)
Instructions spéciales :
- Sois rigoureux mathématiquement (preuves, théorèmes, lemmes)
- Discute la convergence, la stabilité, la complexité algorithmique
- Compare les ordres d'erreur entre méthodes (O(h²) vs O(h⁴))
- Mentionne les applications en ingénierie et calcul scientifique
- Pose des questions de réflexion pour approfondir
"""

        # --- Assemblage du prompt final ---
        prompt = f"""Tu es un tuteur expert en Analyse Numérique et Calcul Scientifique.
Tu travailles pour une plateforme d'apprentissage adaptatif à ESPRIT (école d'ingénieurs).

CONCEPT ACTUEL : {context.concept_name}
{f"DESCRIPTION : {context.description}" if context.description else ""}
{f"MODULE : {context.module_name}" if context.module_name else ""}
{f"DIFFICULTÉ : {context.difficulty}" if context.difficulty else ""}

MAÎTRISE DE L'ÉTUDIANT SUR CE CONCEPT : {context.student_mastery:.0f}%

{complexity_instructions}

PRÉREQUIS DE L'ÉTUDIANT :
{prereqs_text if prereqs_text else "  Aucun prérequis enregistré."}

{f"⚠️ ATTENTION : L'étudiant a des LACUNES sur : {', '.join(weak_prereqs)}. Adapte ton explication en conséquence." if weak_prereqs else ""}

RESSOURCES DISPONIBLES :
{resources_text if resources_text else "  Aucune ressource spécifique."}

RÈGLES STRICTES :
1. Utilise la notation LaTeX pour TOUTES les formules mathématiques
   Exemples : $f(x) = x^2$, $\\int_a^b f(x)dx$, $\\frac{{{{dy}}}}{{{{dx}}}}$
2. Structure ta réponse en étapes numérotées
3. RESTE dans le domaine de l'analyse numérique — refuse poliment les questions hors-sujet
4. Si l'étudiant a des prérequis faibles, commence par un rappel rapide
5. Termine par une suggestion : soit un exercice, soit le prochain concept à étudier
6. Réponds en FRANÇAIS
7. Sois encourageant et bienveillant

IMPORTANT : Tu es un tuteur pédagogique, pas un chatbot généraliste.
Si la question n'est pas liée à l'analyse numérique ou au calcul scientifique,
réponds poliment que tu es spécialisé dans ce domaine et redirige l'étudiant."""

        return prompt

    # ----------------------------------------------------------
    # MÉTHODE 3 : Appeler un modèle LLM (Gemini ou Ollama)
    # ----------------------------------------------------------
    async def _call_llm(self, llm, messages: list, model_name: str) -> str:
        """
        Appelle un modèle LLM via LangChain et retourne sa réponse.

        Cette méthode est RÉUTILISABLE pour n'importe quel modèle
        LangChain (Gemini, Ollama, OpenAI, etc.). C'est le principe
        de l'abstraction : on écrit le code UNE fois, et on change
        juste le "connecteur" (le paramètre llm).

        Paramètres :
            llm : le modèle LangChain à appeler (Gemini ou Ollama)
            messages : la liste de messages (system + historique + question)
            model_name : le nom du modèle (pour les logs)

        Retourne :
            La réponse du modèle (string)

        Lève une exception si l'appel échoue.
        """
        # ChatPromptTemplate.from_messages() crée un template de conversation
        # On lui passe nos messages, et il les formate pour le modèle
        prompt = ChatPromptTemplate.from_messages(messages)

        # Le "|" (pipe) est un concept LangChain :
        # prompt | llm signifie : "prends le prompt, envoie-le au LLM"
        # C'est comme un pipeline Unix : ls | grep "txt"
        chain = prompt | llm

        # ainvoke = appel ASYNCHRONE (le "a" = async)
        # Pourquoi async ? Parce que le modèle met 1-10 secondes à répondre.
        # Pendant ce temps, notre serveur peut traiter d'autres requêtes.
        response = await chain.ainvoke({})

        logger.info(
            f"Réponse {model_name} reçue ({len(response.content)} caractères)"
        )

        return response.content

    # ----------------------------------------------------------
    # MÉTHODE 4 : Générer la réponse adaptative (avec fallback)
    # ----------------------------------------------------------
    async def generate_response(
        self, question: str, context: ConceptContext,
        conversation_history: list[dict[str, str]] = None
    ) -> str:
        """
        Envoie la question au modèle d'IA et retourne la réponse.
        Si Gemini échoue (quota, erreur), bascule sur Ollama automatiquement.

        C'est la méthode principale appelée par le router.
        Elle suit cette logique :

        1. Construire les messages (system + historique + question)
        2. Essayer Gemini d'abord (meilleur en maths)
        3. Si Gemini échoue (429 = quota épuisé) → essayer Ollama
        4. Si les deux échouent → retourner un message d'erreur

        L'étudiant ne voit JAMAIS quel modèle a répondu.
        Pour lui, c'est toujours "le tuteur IA".

        Paramètres :
            question : la question de l'étudiant
            context : le ConceptContext rempli par le RAG Service
            conversation_history : les messages précédents (pour le contexte)

        Retourne :
            La réponse du modèle (string avec du LaTeX)
        """
        # Si AUCUN modèle n'est disponible
        if self.gemini_llm is None and self.ollama_llm is None:
            return (
                "⚠️ Le tuteur IA n'est pas configuré.\n\n"
                "**Option 1** — Gemini (en ligne, gratuit) :\n"
                "1. Allez sur https://aistudio.google.com\n"
                "2. Cliquez 'Get API Key'\n"
                "3. Ajoutez GOOGLE_API_KEY=votre_clé dans .env\n\n"
                "**Option 2** — Ollama (local, illimité) :\n"
                "1. Installez Ollama : https://ollama.com\n"
                "2. Lancez : ollama pull llama3.1:8b\n"
                "3. pip install langchain-ollama\n\n"
                "Puis redémarrez le serveur."
            )

        # --- Construire les messages pour LangChain ---
        # LangChain utilise un format de "messages" comme une conversation :
        # - "system" : les instructions (notre prompt adaptatif)
        # - "human" : les messages de l'étudiant
        # - "ai" : les réponses précédentes du modèle
        messages = []

        # Message système (le briefing)
        system_prompt = self.build_system_prompt(context)
        messages.append(("system", system_prompt))

        # Historique de conversation (si disponible)
        # Ça permet au modèle de se "souvenir" des échanges précédents
        if conversation_history:
            for msg in conversation_history[-6:]:  # Garder les 6 derniers messages
                role = "human" if msg["role"] == "student" else "ai"
                messages.append((role, msg["content"]))

        # La question actuelle de l'étudiant
        messages.append(("human", question))

        # --- Stratégie : Gemini avec RETRY automatique ---
        # Le quota Gemini se réinitialise en quelques secondes.
        # Au lieu de basculer directement sur Ollama (lent),
        # on réessaye Gemini jusqu'à 3 fois avec 10s d'attente.
        # C'est BEAUCOUP plus rapide que d'utiliser Ollama.
        if self.gemini_llm:
            max_retries = 3  # Nombre de tentatives
            for attempt in range(max_retries):
                try:
                    response = await self._call_llm(
                        self.gemini_llm, messages, f"Gemini ({settings.GEMINI_MODEL})"
                    )
                    return response

                except Exception as e:
                    error_str = str(e)
                    is_quota_error = (
                        "429" in error_str
                        or "RESOURCE_EXHAUSTED" in error_str
                        or "quota" in error_str.lower()
                    )

                    if is_quota_error and attempt < max_retries - 1:
                        # Quota épuisé mais on a encore des tentatives
                        wait_time = 15  # Attendre 15 secondes
                        print(
                            f"  ⏳ Gemini quota épuisé, attente {wait_time}s "
                            f"(tentative {attempt + 1}/{max_retries})..."
                        )
                        await asyncio.sleep(wait_time)
                        continue  # Réessayer
                    elif is_quota_error:
                        # Toutes les tentatives Gemini échouées → Ollama
                        print("  🔄 Gemini toujours épuisé → basculement sur Ollama...")
                        break  # Sortir de la boucle, aller vers Ollama
                    else:
                        # Erreur NON liée au quota
                        if self.ollama_llm:
                            print("  🔄 Erreur Gemini → tentative Ollama...")
                            break
                        return f"❌ Erreur Gemini : {error_str}"

        # --- Fallback : Ollama (local) ---
        if self.ollama_llm:
            try:
                response = await self._call_llm(
                    self.ollama_llm, messages, f"Ollama ({settings.OLLAMA_MODEL})"
                )
                return response

            except Exception as e:
                return (
                    f"❌ Les deux modèles ont échoué.\n\n"
                    f"Ollama : {str(e)}\n\n"
                    "💡 Vérifiez qu'Ollama est lancé (ollama serve)"
                )

        # --- Aucun modèle disponible (ne devrait jamais arriver ici) ---
        return "❌ Aucun modèle IA disponible. Vérifiez votre configuration."


# Instance globale (réutilisée partout)
llm_service = LLMService()
