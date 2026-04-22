# ============================================================
# Modèles du Tuteur IA — Tables PostgreSQL + Schemas Pydantic
# ============================================================
# Ce fichier contient 2 types de choses :
#
# 1. MODÈLES SQLAlchemy (classes qui représentent des tables PostgreSQL)
#    Chaque classe = une table dans la base de données
#    Chaque attribut = une colonne dans la table
#
# 2. SCHEMAS Pydantic (classes qui valident les données entrantes/sortantes)
#    Quand un étudiant envoie une requête à l'API, Pydantic vérifie
#    que les données sont au bon format AVANT de les traiter.
#    Ex: si le schema dit "score: float" et l'étudiant envoie "abc",
#    Pydantic rejette automatiquement la requête avec une erreur claire.
#
# POURQUOI séparer SQLAlchemy et Pydantic ?
# - SQLAlchemy = comment les données sont STOCKÉES (dans PostgreSQL)
# - Pydantic = comment les données sont ENVOYÉES/REÇUES (via l'API)
# On ne veut pas envoyer le mot de passe au frontend, par exemple.
# ============================================================

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

# On importe Base depuis notre fichier database.py existant
# Base est la classe mère de tous les modèles SQLAlchemy
# Tous les modèles qui héritent de Base seront créés comme tables
from app.core.database import Base

# ============================================================
# PARTIE 1 : MODÈLES SQLAlchemy (Tables PostgreSQL)
# ============================================================

class TutorSession(Base):
    """
    Table : tutor_sessions

    Représente une SESSION de conversation avec le tuteur IA.
    C'est comme un "fil de discussion" — un étudiant peut avoir
    plusieurs sessions (une par concept qu'il étudie, par exemple).

    Colonnes :
    - id : identifiant unique (auto-incrémenté)
    - etudiant_id : quel étudiant (lien vers la table etudiants)
    - concept_id : quel concept Neo4j est discuté (optionnel)
    - created_at : quand la session a été créée
    - updated_at : dernière activité dans la session
    """
    __tablename__ = "tutor_sessions"

    # Clé primaire : un numéro unique pour chaque session
    # primary_key=True : c'est l'identifiant unique
    # index=True : crée un index pour des recherches rapides
    id = Column(Integer, primary_key=True, index=True)

    # Clé étrangère vers la table "etudiants"
    # ForeignKey("etudiants.id") = cette colonne POINTE vers la colonne "id"
    # de la table "etudiants". C'est un lien entre les deux tables.
    # ondelete="CASCADE" = si on supprime l'étudiant, ses sessions sont
    # aussi supprimées automatiquement (pas de données orphelines)
    etudiant_id = Column(
        Integer,
        ForeignKey("etudiants.id", ondelete="CASCADE"),
        nullable=False,  # Obligatoire : une session appartient toujours à un étudiant
        index=True        # Index pour chercher rapidement "toutes les sessions de l'étudiant X"
    )

    # L'ID du concept Neo4j discuté dans cette session
    # nullable=True : optionnel, car l'étudiant peut poser des questions générales
    # String(255) : texte limité à 255 caractères
    concept_id = Column(String(255), nullable=True)

    # Timestamps (dates automatiques)
    # default=lambda: ... : la date est calculée automatiquement à la création
    # Le lambda est important : sans lui, la date serait la même pour toutes les sessions
    # (la date du démarrage du serveur, pas celle de la création)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),  # Se met à jour automatiquement
        nullable=False
    )

    # Relation SQLAlchemy : permet d'accéder aux messages d'une session
    # session.messages → liste de tous les TutorMessage de cette session
    # back_populates="session" : lien bidirectionnel (message.session → la session)
    # cascade="all, delete-orphan" : si on supprime la session, les messages sont supprimés
    messages = relationship(
        "TutorMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="TutorMessage.created_at"  # Messages triés par date
    )

    def __repr__(self):
        """Représentation textuelle pour le debug (ex: print(session))"""
        return f"<TutorSession(id={self.id}, etudiant={self.etudiant_id}, concept={self.concept_id})>"


class TutorMessage(Base):
    """
    Table : tutor_messages

    Représente un MESSAGE dans une conversation.
    Chaque message est soit de l'étudiant ("student"), soit du tuteur IA ("tutor").

    Colonnes :
    - id : identifiant unique
    - session_id : dans quelle session (lien vers tutor_sessions)
    - role : "student" ou "tutor"
    - content : le texte du message
    - verified : si les maths ont été vérifiées par SymPy (seulement pour le tuteur)
    - concept_id : le concept identifié par le RAG (seulement pour le tuteur)
    - created_at : quand le message a été envoyé
    """
    __tablename__ = "tutor_messages"

    id = Column(Integer, primary_key=True, index=True)

    # Lien vers la session
    session_id = Column(
        Integer,
        ForeignKey("tutor_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Qui a envoyé le message : "student" ou "tutor"
    # String(20) : max 20 caractères
    role = Column(String(20), nullable=False)

    # Le contenu du message (peut être très long → Text au lieu de String)
    # Text = texte illimité (contrairement à String(255) qui est limité)
    content = Column(Text, nullable=False)

    # Est-ce que les formules mathématiques ont été vérifiées par SymPy ?
    # Seulement pertinent pour les messages du tuteur
    # None pour les messages de l'étudiant
    verified = Column(Boolean, nullable=True, default=None)

    # Le concept identifié par le RAG pour ce message
    concept_id = Column(String(255), nullable=True)

    # Date de création du message
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True  # Index pour trier les messages par date
    )

    # Relation inverse : accéder à la session depuis un message
    # message.session → l'objet TutorSession parent
    session = relationship("TutorSession", back_populates="messages")

    def __repr__(self):
        return f"<TutorMessage(id={self.id}, role={self.role}, verified={self.verified})>"


# ============================================================
# PARTIE 2 : SCHEMAS Pydantic (Validation API)
# ============================================================
# Ces classes définissent le FORMAT des données qui entrent et
# sortent de notre API. Elles sont séparées des modèles SQLAlchemy
# car on ne veut pas exposer toutes les colonnes au frontend.

class TutorAskRequest(BaseModel):
    """
    Ce que l'étudiant ENVOIE quand il pose une question.

    Exemple de requête JSON :
    {
        "question": "Comment fonctionne l'interpolation de Lagrange ?",
        "concept_id": "concept_lagrange"   ← optionnel
    }
    """
    question: str                           # La question de l'étudiant (obligatoire)
    concept_id: str | None = None        # ID du concept choisi (optionnel)


class TutorAskResponse(BaseModel):
    """
    Ce que le serveur RETOURNE après la réponse de Gemini.

    Exemple de réponse JSON :
    {
        "message_id": 42,
        "content": "L'interpolation de Lagrange est...",
        "verified": true,
        "concept_name": "Lagrange Interpolation",
        "student_mastery": 45.0,
        "complexity_level": "standard",
        "verification_details": { ... }
    }
    """
    message_id: int                         # ID du message sauvegardé
    content: str                            # La réponse de Gemini
    verified: bool                          # Maths vérifiées ? (True/False)
    concept_name: str                       # Nom du concept identifié
    student_mastery: float                  # Maîtrise de l'étudiant (0-100)
    complexity_level: str                   # "simplified", "standard", "rigorous"
    verification_details: dict[str, Any] | None = None  # Détails SymPy


class SessionCreateRequest(BaseModel):
    """
    Ce que l'étudiant ENVOIE pour créer une nouvelle session.

    Exemple :
    {
        "concept_id": "concept_euler"   ← optionnel
    }
    """
    concept_id: str | None = None


class SessionResponse(BaseModel):
    """
    Infos d'une session retournées par l'API.
    """
    id: int
    etudiant_id: int
    concept_id: str | None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    class Config:
        from_attributes = True  # Permet de convertir un objet SQLAlchemy en Pydantic


class MessageResponse(BaseModel):
    """
    Un message individuel retourné par l'API.
    """
    id: int
    role: str                               # "student" ou "tutor"
    content: str
    verified: bool | None
    concept_id: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class SessionHistoryResponse(BaseModel):
    """
    L'historique complet d'une session (tous les messages).
    """
    session_id: int
    concept_id: str | None
    messages: list[MessageResponse]
