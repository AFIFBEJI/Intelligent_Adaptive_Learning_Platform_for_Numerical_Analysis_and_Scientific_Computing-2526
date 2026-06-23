# ============================================================
# AI Tutor models — PostgreSQL tables + Pydantic schemas
# ============================================================
# This file contains 2 kinds of things :
#
# 1. SQLAlchemy MODELS (classes that represent PostgreSQL tables)
#    Each class = a table in the database
#    Each attribute = a column in the table
#
# 2. Pydantic SCHEMAS (classes that validate incoming/outgoing data)
#    When a student sends a request to the API, Pydantic checks
#    that the data is in the right format BEFORE processing it.
#    E.g.: if the schema says "score: float" and the student sends "abc",
#    Pydantic automatically rejects the request with a clear error.
#
# WHY separate SQLAlchemy and Pydantic ?
# - SQLAlchemy = how the data is STORED (in PostgreSQL)
# - Pydantic = how the data is SENT/RECEIVED (via the API)
# We do not want to send the password to the frontend, for example.
# ============================================================

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

# We import Base from our existing database.py file
# Base is the parent class of all SQLAlchemy models
# All models that inherit from Base will be created as tables
from app.core.database import Base

# ============================================================
# PART 1 : SQLAlchemy MODELS (PostgreSQL Tables)
# ============================================================

class TutorSession(Base):
    """
    Table : tutor_sessions

    Represents a conversation SESSION with the AI tutor.
    It is like a "discussion thread" — a student can have
    several sessions (one per concept they study, for example).

    Columns :
    - id : unique identifier (auto-incremented)
    - etudiant_id : which student (link to the etudiants table)
    - concept_id : which Neo4j concept is discussed (optional)
    - created_at : when the session was created
    - updated_at : last activity in the session
    """
    __tablename__ = "tutor_sessions"

    # Primary key : a unique number for each session
    # primary_key=True : this is the unique identifier
    # index=True : creates an index for fast lookups
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key to the "etudiants" table
    # ForeignKey("etudiants.id") = this column POINTS to the "id" column
    # of the "etudiants" table. It is a link between the two tables.
    # ondelete="CASCADE" = if we delete the student, their sessions are
    # also deleted automatically (no orphan data)
    etudiant_id = Column(
        Integer,
        ForeignKey("etudiants.id", ondelete="CASCADE"),
        nullable=False,  # Required : a session always belongs to a student
        index=True        # Index to quickly find "all the sessions of student X"
    )

    # The ID of the Neo4j concept discussed in this session
    # nullable=True : optional, because the student can ask general questions
    # String(255) : text limited to 255 characters
    concept_id = Column(String(255), nullable=True)

    # Timestamps (automatic dates)
    # default=lambda: ... : the date is computed automatically at creation
    # The lambda is important : without it, the date would be the same for all sessions
    # (the server start date, not the creation date)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),  # Updates itself automatically
        nullable=False
    )

    # SQLAlchemy relationship : allows accessing the messages of a session
    # session.messages → list of all the TutorMessage of this session
    # back_populates="session" : bidirectional link (message.session → the session)
    # cascade="all, delete-orphan" : if we delete the session, the messages are deleted
    messages = relationship(
        "TutorMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="TutorMessage.created_at"  # Messages sorted by date
    )

    def __repr__(self):
        """Textual representation useful for debugging."""
        return f"<TutorSession(id={self.id}, etudiant={self.etudiant_id}, concept={self.concept_id})>"


class TutorMessage(Base):
    """
    Table : tutor_messages

    Represents a MESSAGE in a conversation.
    Each message is either from the student ("student") or from the AI tutor ("tutor").

    Columns :
    - id : unique identifier
    - session_id : in which session (link to tutor_sessions)
    - role : "student" or "tutor"
    - content : the message text
    - verified : whether the math was verified by SymPy (only for the tutor)
    - concept_id : the concept identified by the RAG (only for the tutor)
    - created_at : when the message was sent
    """
    __tablename__ = "tutor_messages"

    id = Column(Integer, primary_key=True, index=True)

    # Link to the session
    session_id = Column(
        Integer,
        ForeignKey("tutor_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Who sent the message : "student" or "tutor"
    # String(20) : max 20 characters
    role = Column(String(20), nullable=False)

    # The message content (can be very long → Text instead of String)
    # Text = unlimited text (unlike String(255) which is limited)
    content = Column(Text, nullable=False)

    # Were the mathematical formulas verified by SymPy ?
    # Only relevant for tutor messages
    # None for student messages
    verified = Column(Boolean, nullable=True, default=None)

    # The concept identified by the RAG for this message
    concept_id = Column(String(255), nullable=True)

    # Message creation date
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True  # Index to sort messages by date
    )

    # Inverse relationship : access the session from a message
    # message.session → the parent TutorSession object
    session = relationship("TutorSession", back_populates="messages")

    def __repr__(self):
        return f"<TutorMessage(id={self.id}, role={self.role}, verified={self.verified})>"


# ============================================================
# PART 2 : Pydantic SCHEMAS (API Validation)
# ============================================================
# These classes define the FORMAT of the data that comes into and
# goes out of our API. They are separate from the SQLAlchemy models
# because we do not want to expose all the columns to the frontend.

class TutorAskRequest(BaseModel):
    """
    What the student SENDS when asking a question.

    Example JSON request :
    {
        "question": "How does Lagrange interpolation work ?",
        "concept_id": "concept_lagrange",  // optional
        "provider": "openai"               // optional : "ollama" or "openai"
    }

    The `provider` field lets the user explicitly choose the LLM to use
    for this request (local Gemma vs cloud GPT-4o-mini). If empty, we use
    the default provider configured in .env.
    """
    question: str                           # The student's question (required)
    concept_id: str | None = None           # ID of the chosen concept (optional)
    provider: str | None = None             # "ollama" or "openai" (optional)


class TutorAskResponse(BaseModel):
    """
    What the server RETURNS after the LLM (Ollama) response.

    Example JSON response :
    {
        "message_id": 42,
        "content": "Lagrange interpolation is...",
        "verified": true,
        "concept_name": "Lagrange Interpolation",
        "student_mastery": 45.0,
        "complexity_level": "standard",
        "verification_details": { ... }
    }
    """
    message_id: int                         # ID of the saved message
    content: str                            # The LLM (Ollama) response
    verified: bool                          # Math verified ? (True/False)
    concept_name: str                       # Name of the identified concept
    student_mastery: float                  # Student's mastery (0-100)
    complexity_level: str                   # "simplified", "standard", "rigorous"
    verification_details: dict[str, Any] | None = None  # SymPy details


class SessionCreateRequest(BaseModel):
    """
    What the student SENDS to create a new session.

    Example :
    {
        "concept_id": "concept_euler"   <- optional
    }
    """
    concept_id: str | None = None


class SessionResponse(BaseModel):
    """
    Session info returned by the API.
    """
    id: int
    etudiant_id: int
    concept_id: str | None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    class Config:
        from_attributes = True  # Allows converting a SQLAlchemy object to Pydantic


class MessageResponse(BaseModel):
    """
    An individual message returned by the API.
    """
    id: int
    role: str                               # "student" or "tutor"
    content: str
    verified: bool | None
    concept_id: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class SessionHistoryResponse(BaseModel):
    """
    The complete history of a session (all the messages).
    """
    session_id: int
    concept_id: str | None
    messages: list[MessageResponse]
