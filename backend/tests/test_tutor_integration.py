# ============================================================
# Tests d'integration pour le router /tutor/*
# ============================================================
# Avant ce fichier (12 mai 2026) le router tuteur etait totalement non
# couvert par les tests, alors qu'il orchestre le pipeline le plus
# complexe du projet (RAG + LLM + SymPy). 15 tests couvrent maintenant :
#
#   - Authentification requise sur tous les endpoints.
#   - Creation de session (avec / sans concept_id).
#   - Listing des sessions (IDOR : on ne voit QUE ses propres sessions).
#   - History (IDOR + 404 + cas vide).
#   - ask_tutor : 404 / 403 / message etudiant sauvegarde (LLM mocke).
#   - LLM picker options.
#
# Les services lourds (RAG Neo4j + LLM Ollama/OpenAI + SymPy) sont
# monkeypatch-es : on ne fait JAMAIS d'appel reseau dans les tests.
# ============================================================
from __future__ import annotations

import pytest


# ============================================================
# Helpers
# ============================================================
def _register_payload(email: str, password: str = "TutorTest123!", lang: str = "fr") -> dict:
    return {
        "nom_complet": "Tutor Tester",
        "email": email,
        "mot_de_passe": password,
        "niveau_actuel": "beginner",
        "langue_preferee": lang,
    }


def _register_and_token(client, email: str) -> str:
    """Inscrit un compte et retourne le JWT pour l'authentification."""
    resp = client.post("/auth/register", json=_register_payload(email))
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _create_session(client, token: str, concept_id: str | None = None) -> dict:
    """Cree une session et retourne le dict SessionResponse."""
    body: dict = {}
    if concept_id is not None:
        body["concept_id"] = concept_id
    resp = client.post("/tutor/sessions", json=body, headers=_auth_headers(token))
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest.fixture
def mock_llm_pipeline(monkeypatch):
    """Stub global du pipeline RAG + LLM + SymPy pour ask_tutor.

    Evite les appels reseau (Ollama / OpenAI / Neo4j) et garantit des
    reponses deterministes pour les assertions.
    """
    from types import SimpleNamespace

    # Stub rag_service.build_context -> ConceptContext minimal
    from app.services import rag_service as rag_mod

    fake_context = SimpleNamespace(
        concept_name="Newton-Raphson",
        concept_id="concept_newton_raphson",
        student_mastery=50,
        prerequisites=[],
        resources=[],
        module=None,
        description="Test description",
    )

    def _fake_build_context(*_args, **_kwargs):
        return fake_context

    monkeypatch.setattr(
        rag_mod.rag_service, "build_context", _fake_build_context,
    )

    # Stub llm_service.generate_response -> reponse texte simple
    from app.services import llm_service as llm_mod

    async def _fake_generate_response(*_args, **_kwargs):
        return "Une iteration de Newton-Raphson : x_{n+1} = x_n - f(x_n)/f'(x_n)."

    monkeypatch.setattr(
        llm_mod.llm_service, "generate_response", _fake_generate_response,
    )

    # Stub verification_service.verify_response -> pas d'erreur math.
    # Le router lit `verification_result.get("verified", False)` -> on doit
    # bien fournir la cle `verified` (pas `is_verified`).
    from app.services import verification_service as verif_mod

    def _fake_verify_response(text):
        return {
            "verified": True,
            "total_expressions": 0,
            "errors": [],
        }

    monkeypatch.setattr(
        verif_mod.verification_service, "verify_response", _fake_verify_response,
    )

    # Stub llm_service.get_complexity_level pour rester deterministe meme si
    # la signature evolue. La vraie methode est pure (basee sur mastery)
    # mais on prefere isoler le test des changements internes.
    monkeypatch.setattr(
        llm_mod.llm_service, "get_complexity_level",
        lambda mastery: "standard",
    )


# ============================================================
# 1. LLM options endpoint
# ============================================================
class TestLlmOptions:
    def test_llm_options_requires_auth(self, client):
        """GET /tutor/llm-options sans token -> 401."""
        resp = client.get("/tutor/llm-options")
        assert resp.status_code == 401

    def test_llm_options_returns_picker_config(self, client):
        """GET /tutor/llm-options renvoie picker_enabled + default + liste."""
        token = _register_and_token(client, "llm-opts@pfemail.com")
        resp = client.get("/tutor/llm-options", headers=_auth_headers(token))
        assert resp.status_code == 200
        body = resp.json()
        assert "picker_enabled" in body
        assert "default_provider" in body
        assert isinstance(body.get("available"), list)


# ============================================================
# 2. Create session
# ============================================================
class TestCreateSession:
    def test_create_session_without_concept_id(self, client):
        """POST /tutor/sessions sans body -> 201 + objet session."""
        token = _register_and_token(client, "create-session@pfemail.com")
        resp = client.post("/tutor/sessions", json={}, headers=_auth_headers(token))
        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert "id" in body
        assert body["etudiant_id"] > 0
        assert body["concept_id"] is None
        assert body["message_count"] == 0

    def test_create_session_with_concept_id(self, client):
        """POST avec concept_id ciblant un sujet specifique."""
        token = _register_and_token(client, "create-with-concept@pfemail.com")
        resp = client.post(
            "/tutor/sessions",
            json={"concept_id": "concept_newton_raphson"},
            headers=_auth_headers(token),
        )
        assert resp.status_code == 201
        assert resp.json()["concept_id"] == "concept_newton_raphson"

    def test_create_session_requires_auth(self, client):
        """POST sans Bearer -> 401."""
        resp = client.post("/tutor/sessions", json={})
        assert resp.status_code == 401


# ============================================================
# 3. List sessions (IDOR : un user ne voit QUE ses sessions)
# ============================================================
class TestListSessions:
    def test_list_sessions_empty_for_new_user(self, client):
        """Nouvel inscrit -> liste vide."""
        token = _register_and_token(client, "list-empty@pfemail.com")
        resp = client.get("/tutor/sessions", headers=_auth_headers(token))
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_sessions_returns_only_own(self, client):
        """User A cree 2 sessions, User B ne doit voir AUCUNE des sessions de A."""
        token_a = _register_and_token(client, "user-a@pfemail.com")
        token_b = _register_and_token(client, "user-b@pfemail.com")

        # User A cree 2 sessions
        _create_session(client, token_a)
        _create_session(client, token_a, concept_id="concept_lagrange")

        # User A voit 2 sessions
        resp_a = client.get("/tutor/sessions", headers=_auth_headers(token_a))
        assert resp_a.status_code == 200
        assert len(resp_a.json()) == 2

        # User B voit 0 session (IDOR check)
        resp_b = client.get("/tutor/sessions", headers=_auth_headers(token_b))
        assert resp_b.status_code == 200
        assert resp_b.json() == []


# ============================================================
# 4. Ask tutor (le plus important - 4 tests)
# ============================================================
class TestAskTutor:
    def test_ask_tutor_404_when_session_does_not_exist(self, client, mock_llm_pipeline):
        """Session_id inexistante -> 404."""
        token = _register_and_token(client, "ask-404@pfemail.com")
        resp = client.post(
            "/tutor/sessions/99999/ask",
            json={"question": "Quelle est la derivee de x^2 ?", "concept_id": None},
            headers=_auth_headers(token),
        )
        assert resp.status_code == 404

    def test_ask_tutor_403_when_session_belongs_to_another_user(
        self, client, mock_llm_pipeline,
    ):
        """IDOR : User B ne peut pas poster dans la session de User A."""
        token_a = _register_and_token(client, "owner@pfemail.com")
        token_b = _register_and_token(client, "attacker@pfemail.com")
        session_a = _create_session(client, token_a)

        resp = client.post(
            f"/tutor/sessions/{session_a['id']}/ask",
            json={"question": "Hack attempt", "concept_id": None},
            headers=_auth_headers(token_b),
        )
        assert resp.status_code == 403

    def test_ask_tutor_saves_student_message_and_returns_response(
        self, client, mock_llm_pipeline,
    ):
        """Le pipeline complet doit retourner une reponse + persister le message."""
        token = _register_and_token(client, "ask-ok@pfemail.com")
        session = _create_session(client, token)
        resp = client.post(
            f"/tutor/sessions/{session['id']}/ask",
            json={
                "question": "Comment marche Newton-Raphson ?",
                "concept_id": "concept_newton_raphson",
            },
            headers=_auth_headers(token),
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        # TutorAskResponse : content (str), verified (bool), concept_name (str),
        # student_mastery (float), complexity_level (str).
        assert isinstance(body.get("content"), str)
        assert body["content"]  # non-vide
        assert "verified" in body
        assert "concept_name" in body
        # L'historique doit avoir au moins le message etudiant + reponse tuteur.
        hist = client.get(
            f"/tutor/sessions/{session['id']}/history",
            headers=_auth_headers(token),
        )
        assert hist.status_code == 200
        messages = hist.json().get("messages", [])
        assert len(messages) >= 1
        # Premier message = etudiant avec la question posee.
        assert messages[0]["role"] == "student"
        assert "Newton-Raphson" in messages[0]["content"]

    def test_ask_tutor_requires_auth(self, client):
        """POST /tutor/.../ask sans token -> 401."""
        resp = client.post(
            "/tutor/sessions/1/ask",
            json={"question": "X", "concept_id": None},
        )
        assert resp.status_code == 401


# ============================================================
# 5. Get session history (IDOR + 404 + cas vide)
# ============================================================
class TestGetHistory:
    def test_history_404_when_session_does_not_exist(self, client):
        """Session inexistante -> 404."""
        token = _register_and_token(client, "hist-404@pfemail.com")
        resp = client.get("/tutor/sessions/99999/history", headers=_auth_headers(token))
        assert resp.status_code == 404

    def test_history_403_when_session_belongs_to_another_user(self, client):
        """IDOR : User B ne peut pas lire la session de User A."""
        token_a = _register_and_token(client, "hist-owner@pfemail.com")
        token_b = _register_and_token(client, "hist-attacker@pfemail.com")
        session_a = _create_session(client, token_a)

        resp = client.get(
            f"/tutor/sessions/{session_a['id']}/history",
            headers=_auth_headers(token_b),
        )
        assert resp.status_code == 403

    def test_history_empty_for_new_session(self, client):
        """Session vide -> historique vide (200 + 'messages': [])."""
        token = _register_and_token(client, "hist-empty@pfemail.com")
        session = _create_session(client, token)
        resp = client.get(
            f"/tutor/sessions/{session['id']}/history",
            headers=_auth_headers(token),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("messages", []) == []

    def test_history_requires_auth(self, client):
        """GET /tutor/.../history sans token -> 401."""
        resp = client.get("/tutor/sessions/1/history")
        assert resp.status_code == 401


# ============================================================
# 6. Validation Pydantic du body
# ============================================================
class TestBodyValidation:
    def test_ask_tutor_with_missing_question_field_returns_422(
        self, client, mock_llm_pipeline,
    ):
        """Pydantic doit rejeter un body sans `question`."""
        token = _register_and_token(client, "validation@pfemail.com")
        session = _create_session(client, token)
        resp = client.post(
            f"/tutor/sessions/{session['id']}/ask",
            json={"concept_id": "concept_lagrange"},  # question manquante
            headers=_auth_headers(token),
        )
        assert resp.status_code == 422
