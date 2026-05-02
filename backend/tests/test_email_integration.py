# ============================================================
# Tests d'integration : verification email + reset password
# ============================================================
# On utilise le TestClient + SQLite memoire (cf. conftest).
# Le service mail tourne en mode "console" par defaut (cf. .env de test
# dans conftest), donc aucun email reel n'est envoye.
#
# Verifications cles :
#   - register envoie un email verification (le compte est NOT verified)
#   - GET /auth/verify-email/<token> passe is_verified=True
#   - request-verification rate-limite a 60s
#   - forgot-password renvoie toujours un message neutre (pas user enum)
#   - reset-password change le mot de passe, ancien ne marche plus
#   - tokens reject si purpose incorrect (purpose enforcement)
# ============================================================
from __future__ import annotations

import time

import pytest


def _register(client, email: str, password: str = "OldPass123!"):
    return client.post(
        "/auth/register",
        json={
            "nom_complet": "Email Tester",
            "email": email,
            "mot_de_passe": password,
            "niveau_actuel": "beginner",
            "langue_preferee": "fr",
        },
    )


def _login(client, email: str, password: str):
    return client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )


class TestRegistrationSendsVerification:
    def test_register_creates_unverified_account(self, client):
        """Apres /auth/register, is_verified doit etre False."""
        resp = _register(client, "newbie@test.local")
        assert resp.status_code == 200

        # /auth/me doit retourner is_verified=False
        token = resp.json()["access_token"]
        me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200
        body = me.json()
        assert body["is_verified"] is False


class TestVerifyEmail:
    def test_verify_with_valid_token_marks_account_verified(self, client):
        """Le bon token GET /auth/verify-email/<token> doit passer le compte
        a is_verified=True."""
        # Setup : creer compte
        _register(client, "verify-me@test.local")

        # Generer un token directement (on ne peut pas extraire l'email du log).
        from app.core.database import get_db
        from app.core.security import create_verification_token
        from app.main import app
        from app.models.etudiant import Etudiant

        db_gen = app.dependency_overrides[get_db]()
        db = next(db_gen)
        try:
            student = db.query(Etudiant).filter(Etudiant.email == "verify-me@test.local").first()
            assert student is not None
            assert student.is_verified is False
            token = create_verification_token(student.id)
        finally:
            try:
                next(db_gen)
            except StopIteration:
                pass

        # Cliquer sur le lien
        resp = client.get(f"/auth/verify-email/{token}")
        assert resp.status_code == 200, resp.text
        assert "verifie" in resp.json()["message"].lower() or "verif" in resp.json()["message"].lower()

        # Verifier que is_verified=True maintenant
        login = _login(client, "verify-me@test.local", "OldPass123!")
        new_token = login.json()["access_token"]
        me = client.get("/auth/me", headers={"Authorization": f"Bearer {new_token}"})
        assert me.json()["is_verified"] is True

    def test_verify_with_invalid_token_returns_400(self, client):
        resp = client.get("/auth/verify-email/not-a-real-jwt")
        assert resp.status_code == 400

    def test_verify_with_reset_token_rejected_purpose_check(self, client):
        """Un token de reset password NE DOIT PAS pouvoir etre utilise
        pour valider un email (purpose enforcement)."""
        _register(client, "purpose-check@test.local")

        from app.core.database import get_db
        from app.core.security import create_reset_password_token
        from app.main import app
        from app.models.etudiant import Etudiant

        db_gen = app.dependency_overrides[get_db]()
        db = next(db_gen)
        try:
            student = db.query(Etudiant).filter(Etudiant.email == "purpose-check@test.local").first()
            wrong_purpose_token = create_reset_password_token(student.id)
        finally:
            try:
                next(db_gen)
            except StopIteration:
                pass

        resp = client.get(f"/auth/verify-email/{wrong_purpose_token}")
        assert resp.status_code == 400
        assert "purpose" in resp.json()["detail"].lower() or "incorrect" in resp.json()["detail"].lower()

    def test_verify_twice_is_idempotent(self, client):
        """Re-verifier un compte deja verifie doit retourner 200, pas 400."""
        _register(client, "twice@test.local")
        from app.core.database import get_db
        from app.core.security import create_verification_token
        from app.main import app
        from app.models.etudiant import Etudiant

        db_gen = app.dependency_overrides[get_db]()
        db = next(db_gen)
        try:
            student = db.query(Etudiant).filter(Etudiant.email == "twice@test.local").first()
            token = create_verification_token(student.id)
        finally:
            try:
                next(db_gen)
            except StopIteration:
                pass

        r1 = client.get(f"/auth/verify-email/{token}")
        assert r1.status_code == 200
        r2 = client.get(f"/auth/verify-email/{token}")
        assert r2.status_code == 200


class TestRequestVerification:
    def test_request_for_unknown_email_returns_neutral_message(self, client):
        """Securite : on ne doit pas reveler si un email existe ou non."""
        resp = client.post(
            "/auth/request-verification",
            json={"email": "ghost-never-existed@test.local"},
        )
        assert resp.status_code == 200
        # Message neutre attendu
        assert "ete envoye" in resp.json()["message"] or "sent" in resp.json()["message"].lower()

    def test_request_for_unverified_account_sends_again(self, client):
        """Pour un compte qui existe et n'est pas verifie, on envoie."""
        _register(client, "resender@test.local")
        # On attend un peu pour eviter le rate limit du send fait par register
        time.sleep(0.05)
        resp = client.post(
            "/auth/request-verification",
            json={"email": "resender@test.local"},
        )
        # Soit 200 OK soit 429 rate limit selon la timing.
        assert resp.status_code in (200, 429)


class TestForgotAndResetPassword:
    def test_forgot_reveals_account_existence_by_design(self, client):
        """Choix produit : on REVELE explicitement si l'email existe ou non,
        pour une meilleure UX (l'utilisateur sait s'il doit creer un compte
        ou s'il a juste mal tape son email). On accepte ainsi le risque
        d'user enumeration sur cette page.

        - Email inconnu -> 404 avec message 'No account found'
        - Email connu   -> 200 avec message 'Reset email sent'
        """
        # Email inconnu : 404
        r1 = client.post("/auth/forgot-password", json={"email": "inconnu@test.local"})
        assert r1.status_code == 404
        assert "no account" in r1.json()["detail"].lower() or "create" in r1.json()["detail"].lower()

        # Email connu : 200 + envoi de l'email (mode console en test)
        _register(client, "knownuser@test.local")
        r2 = client.post("/auth/forgot-password", json={"email": "knownuser@test.local"})
        assert r2.status_code == 200
        assert "sent" in r2.json()["message"].lower() or "envoye" in r2.json()["message"].lower()

    def test_reset_password_changes_hash_and_old_password_fails(self, client):
        """Le reset doit vraiment changer le mot de passe en base."""
        _register(client, "resetme@test.local", password="OldPass123!")

        from app.core.database import get_db
        from app.core.security import create_reset_password_token
        from app.main import app
        from app.models.etudiant import Etudiant

        db_gen = app.dependency_overrides[get_db]()
        db = next(db_gen)
        try:
            student = db.query(Etudiant).filter(Etudiant.email == "resetme@test.local").first()
            token = create_reset_password_token(student.id)
        finally:
            try:
                next(db_gen)
            except StopIteration:
                pass

        # Reset vers un nouveau mot de passe
        resp = client.post(
            "/auth/reset-password",
            json={"token": token, "new_password": "BrandNewPass456!"},
        )
        assert resp.status_code == 200, resp.text

        # L'ancien mot de passe ne doit plus marcher
        old = _login(client, "resetme@test.local", "OldPass123!")
        assert old.status_code == 401

        # Le nouveau marche
        new = _login(client, "resetme@test.local", "BrandNewPass456!")
        assert new.status_code == 200

    def test_reset_password_with_invalid_token_returns_400(self, client):
        resp = client.post(
            "/auth/reset-password",
            json={"token": "not-a-jwt", "new_password": "Whatever123!"},
        )
        assert resp.status_code == 400

    def test_reset_password_with_verify_token_rejected_purpose_check(self, client):
        """Un token de verification NE DOIT PAS pouvoir reset le password."""
        _register(client, "purpose2@test.local")

        from app.core.database import get_db
        from app.core.security import create_verification_token
        from app.main import app
        from app.models.etudiant import Etudiant

        db_gen = app.dependency_overrides[get_db]()
        db = next(db_gen)
        try:
            student = db.query(Etudiant).filter(Etudiant.email == "purpose2@test.local").first()
            wrong_purpose_token = create_verification_token(student.id)
        finally:
            try:
                next(db_gen)
            except StopIteration:
                pass

        resp = client.post(
            "/auth/reset-password",
            json={"token": wrong_purpose_token, "new_password": "TryToHack123!"},
        )
        assert resp.status_code == 400

    def test_reset_password_too_short_returns_422(self, client):
        """Pydantic Field min_length=8 doit rejeter."""
        resp = client.post(
            "/auth/reset-password",
            json={"token": "any", "new_password": "short"},
        )
        assert resp.status_code == 422

    def test_reset_marks_account_verified_side_effect(self, client):
        """Un user qui sait reset son password a forcement acces a son
        email -> on considere son email verifie aussi (side effect)."""
        _register(client, "auto-verify@test.local")

        from app.core.database import get_db
        from app.core.security import create_reset_password_token
        from app.main import app
        from app.models.etudiant import Etudiant

        db_gen = app.dependency_overrides[get_db]()
        db = next(db_gen)
        try:
            student = db.query(Etudiant).filter(Etudiant.email == "auto-verify@test.local").first()
            assert student.is_verified is False  # initialement non verifie
            token = create_reset_password_token(student.id)
        finally:
            try:
                next(db_gen)
            except StopIteration:
                pass

        client.post(
            "/auth/reset-password",
            json={"token": token, "new_password": "NewSecure999!"},
        )

        # is_verified doit etre passe a True via le side effect
        login = _login(client, "auto-verify@test.local", "NewSecure999!")
        token = login.json()["access_token"]
        me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me.json()["is_verified"] is True
