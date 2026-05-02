# ============================================================
# Tests d'integration pour le router /auth
# ============================================================
# On utilise FastAPI TestClient + SQLite en memoire (cf. conftest).
# Pas besoin d'infrastructure externe pour ces tests.
# ============================================================
from __future__ import annotations


def _register_payload(email: str, password: str = "TestPass123!", lang: str = "fr") -> dict:
    return {
        "nom_complet": "Test User",
        "email": email,
        "mot_de_passe": password,
        "niveau_actuel": "beginner",
        "langue_preferee": lang,
    }


class TestRegister:
    def test_register_creates_account_and_returns_token(self, client):
        """POST /auth/register avec un email valide doit creer le compte
        et retourner un access_token JWT."""
        resp = client.post(
            "/auth/register",
            json=_register_payload("alice@test.local"),
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"
        # Le token JWT a 3 segments (header.payload.signature).
        assert body["access_token"].count(".") == 2

    def test_register_with_duplicate_email_returns_400(self, client):
        """Le meme email ne peut etre inscrit qu'une fois."""
        # 1er register OK
        resp1 = client.post(
            "/auth/register",
            json=_register_payload("bob@test.local"),
        )
        assert resp1.status_code == 200

        # 2e register avec meme email -> 400
        resp2 = client.post(
            "/auth/register",
            json=_register_payload("bob@test.local"),
        )
        assert resp2.status_code == 400
        assert "detail" in resp2.json()

    def test_register_without_lang_returns_422(self, client):
        """langue_preferee est obligatoire (Field(...) dans le schema)."""
        payload = _register_payload("charlie@test.local")
        del payload["langue_preferee"]
        resp = client.post("/auth/register", json=payload)
        assert resp.status_code == 422  # Pydantic validation error


class TestLogin:
    def test_login_with_correct_credentials_returns_token(self, client):
        """POST /auth/login avec les bons identifiants retourne un JWT."""
        # Setup : inscrire un compte
        client.post(
            "/auth/register",
            json=_register_payload("dave@test.local", password="MyPass789!"),
        )

        # Login OAuth2PasswordRequestForm = form-encoded, pas JSON.
        resp = client.post(
            "/auth/login",
            data={"username": "dave@test.local", "password": "MyPass789!"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["access_token"].count(".") == 2

    def test_login_with_wrong_password_returns_401(self, client):
        """Mauvais mot de passe -> 401, pas de token."""
        client.post(
            "/auth/register",
            json=_register_payload("eve@test.local", password="GoodPass!"),
        )

        resp = client.post(
            "/auth/login",
            data={"username": "eve@test.local", "password": "WrongPass!"},
        )
        assert resp.status_code == 401

    def test_login_with_unknown_email_returns_401(self, client):
        """Email inexistant -> 401 (pas de leak d'info via 404)."""
        resp = client.post(
            "/auth/login",
            data={"username": "ghost@test.local", "password": "any"},
        )
        assert resp.status_code == 401


class TestProtectedEndpoint:
    def test_me_with_valid_token_returns_profile(self, client):
        """GET /auth/me avec un token valide retourne le profil."""
        # Setup
        client.post(
            "/auth/register",
            json=_register_payload("frank@test.local"),
        )
        login = client.post(
            "/auth/login",
            data={"username": "frank@test.local", "password": "TestPass123!"},
        )
        token = login.json()["access_token"]

        resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["email"] == "frank@test.local"
        assert body["nom_complet"] == "Test User"

    def test_me_without_token_returns_401(self, client):
        resp = client.get("/auth/me")
        assert resp.status_code == 401

    def test_me_with_invalid_token_returns_401(self, client):
        resp = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert resp.status_code == 401

    def test_me_with_token_for_deleted_user_returns_401(self, client):
        """Hardening : si le user est supprime, son ancien JWT doit
        etre rejete (verification d'existence dans get_current_user)."""
        # Inscrire un user, recuperer son token, le supprimer manuellement.
        client.post(
            "/auth/register",
            json=_register_payload("ghost-user@test.local"),
        )
        login = client.post(
            "/auth/login",
            data={"username": "ghost-user@test.local", "password": "TestPass123!"},
        )
        token = login.json()["access_token"]

        # Supprimer le user en base directement via la session.
        from sqlalchemy.orm import sessionmaker

        from app.core.database import engine as _  # ensure model is loaded
        from app.core.database import get_db

        # On utilise le client.app pour acceder a l'engine de test.
        # On passe par dependency_overrides[get_db] qui a deja une session.
        from app.main import app
        from app.models.etudiant import Etudiant
        get_db_override = app.dependency_overrides.get(get_db)
        assert get_db_override is not None, "Test client doit avoir override get_db"
        db_gen = get_db_override()
        db = next(db_gen)
        try:
            user = db.query(Etudiant).filter(Etudiant.email == "ghost-user@test.local").first()
            assert user is not None
            db.delete(user)
            db.commit()
        finally:
            try:
                next(db_gen)
            except StopIteration:
                pass

        # Le token est cryptographiquement valide mais le user n'existe plus.
        resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401
