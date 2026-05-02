# ============================================================
# Tests d'integration pour le router /quiz (legacy static)
# ============================================================
# Verifie le coeur fonctionnel : la mise a jour du mastery est
# CONDITIONNELLE au mode du quiz (adaptive vs practice).
# ============================================================
from __future__ import annotations

import pytest


@pytest.fixture
def auth_headers(client):
    """Cree un compte de test et retourne le header Authorization pret a l'emploi."""
    client.post(
        "/auth/register",
        json={
            "nom_complet": "Quiz Tester",
            "email": "quiz-tester@test.local",
            "mot_de_passe": "QuizTest123!",
            "niveau_actuel": "beginner",
            "langue_preferee": "fr",
        },
    )
    login = client.post(
        "/auth/login",
        data={"username": "quiz-tester@test.local", "password": "QuizTest123!"},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _make_quiz_via_orm(client, mode: str = "adaptive"):
    """Cree un quiz directement via la DB (court-circuite l'API).
    Retourne l'id du quiz cree."""
    from app.core.database import get_db
    from app.main import app
    from app.models.quiz import Quiz

    db_gen = app.dependency_overrides[get_db]()
    db = next(db_gen)
    try:
        quiz = Quiz(
            titre=f"Test quiz {mode}",
            module="Interpolation",
            difficulte="facile",
            questions=[
                {"id": 1, "question": "2+2?", "options": ["3", "4"], "correct_index": 1, "points": 1},
                {"id": 2, "question": "1+1?", "options": ["1", "2"], "correct_index": 1, "points": 1},
            ],
            source="static",
            mode=mode,
        )
        db.add(quiz)
        db.commit()
        db.refresh(quiz)
        return quiz.id
    finally:
        try:
            next(db_gen)
        except StopIteration:
            pass


class TestQuizSubmit:
    def test_submit_adaptive_updates_mastery(self, client, auth_headers):
        """En mode adaptive, le submit doit mettre a jour le concept_mastery."""
        quiz_id = _make_quiz_via_orm(client, mode="adaptive")

        resp = client.post(
            f"/quiz/{quiz_id}/submit",
            headers=auth_headers,
            json={"score": 80.0, "temps_reponse": 120, "reponses": None},
        )
        assert resp.status_code == 200, resp.text

        # Verifier qu'une ligne ConceptMastery a ete creee.
        from app.core.database import get_db
        from app.main import app
        from app.models.mastery import ConceptMastery

        db_gen = app.dependency_overrides[get_db]()
        db = next(db_gen)
        try:
            mastery_count = db.query(ConceptMastery).count()
            assert mastery_count >= 1, "Mode adaptive doit creer au moins une mastery"
        finally:
            try:
                next(db_gen)
            except StopIteration:
                pass

    def test_submit_practice_does_NOT_update_mastery(self, client, auth_headers):
        """En mode practice, le submit ne doit PAS toucher au mastery."""
        # Compter les mastery avant.
        from app.core.database import get_db
        from app.main import app
        from app.models.mastery import ConceptMastery

        def _count_mastery():
            db_gen = app.dependency_overrides[get_db]()
            db = next(db_gen)
            try:
                return db.query(ConceptMastery).count()
            finally:
                try:
                    next(db_gen)
                except StopIteration:
                    pass

        before = _count_mastery()

        quiz_id = _make_quiz_via_orm(client, mode="practice")
        resp = client.post(
            f"/quiz/{quiz_id}/submit",
            headers=auth_headers,
            json={"score": 80.0, "temps_reponse": 60, "reponses": None},
        )
        assert resp.status_code == 200, resp.text

        after = _count_mastery()
        assert before == after, (
            f"Mode practice ne doit PAS creer de mastery (before={before}, after={after})"
        )

    def test_submit_unknown_quiz_returns_404(self, client, auth_headers):
        resp = client.post(
            "/quiz/99999/submit",
            headers=auth_headers,
            json={"score": 50.0, "temps_reponse": 30},
        )
        assert resp.status_code == 404

    def test_submit_without_auth_returns_401(self, client):
        quiz_id = _make_quiz_via_orm(client, mode="adaptive")
        resp = client.post(
            f"/quiz/{quiz_id}/submit",
            json={"score": 80.0, "temps_reponse": 60},
        )
        assert resp.status_code == 401


class TestQuizList:
    def test_list_quiz_requires_auth(self, client):
        resp = client.get("/quiz/")
        assert resp.status_code == 401

    def test_list_quiz_with_auth_returns_200(self, client, auth_headers):
        _make_quiz_via_orm(client, mode="adaptive")
        resp = client.get("/quiz/", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)
        assert len(body) >= 1
