# ============================================================
# Fixtures partagees pour les tests d'integration
# ============================================================
# On utilise SQLite en memoire pour eviter de devoir spinner Postgres
# pour chaque test. La couche ORM SQLAlchemy est compatible.
# ============================================================
from __future__ import annotations

import os

# Charge le .env racine si python-dotenv est dispo. Cela permet aux tests
# d'utiliser le NEO4J_PASSWORD reel quand on lance pytest depuis backend/
# (plutot que d'avoir a setter les env vars manuellement).
try:
    from dotenv import load_dotenv
    # On cherche le .env a la racine du projet (un cran au-dessus de backend/).
    _here = os.path.dirname(os.path.abspath(__file__))
    _root_env = os.path.join(_here, "..", "..", ".env")
    if os.path.exists(_root_env):
        load_dotenv(_root_env, override=False)
except ImportError:
    pass

# Set env vars BEFORE importing the app, sinon pydantic-settings rate
# la lecture initiale et leve une ValidationError. setdefault = ne touche
# pas une var deja definie (par .env ou par le shell).
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_e2e.db")
os.environ.setdefault("NEO4J_URI", "bolt://localhost:7687")
os.environ.setdefault("NEO4J_USER", "neo4j")
os.environ.setdefault("NEO4J_PASSWORD", "test-password")
os.environ.setdefault("SECRET_KEY", "test-secret-key-only-for-pytest-32-bytes")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
os.environ.setdefault("LLM_PROVIDER", "openai")
os.environ.setdefault("LLM_MODEL_NAME", "gpt-4o-mini")
os.environ.setdefault("OPENAI_API_KEY", "test-dummy-key")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture(scope="session")
def test_engine():
    """Cree un engine SQLAlchemy SQLite en memoire partage entre threads."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Importer tous les modeles pour que Base.metadata les connaisse.
    from app.core.database import Base
    from app.models import etudiant, mastery, quiz, tutor  # noqa: F401

    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_engine):
    """Une session DB qui rollback apres chaque test pour isolation."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(test_engine, monkeypatch):
    """TestClient FastAPI qui pointe sur la DB SQLite de test.

    On override la dependency get_db pour utiliser notre engine de test.
    On stub aussi les services qui pingent Neo4j ou les LLMs en reseau,
    pour que les tests ne dependent pas d'une infrastructure externe.
    """
    # Stub Neo4j connection pour ne pas exiger un Neo4j up.
    import app.graph.neo4j_connection as neo_mod

    class _StubNeo4j:
        def run_query(self, query, params=None):
            return []

        def close(self):
            pass

    monkeypatch.setattr(neo_mod, "neo4j_conn", _StubNeo4j())

    # Override la fixture get_db.
    from app.core.database import get_db
    from app.main import app

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
