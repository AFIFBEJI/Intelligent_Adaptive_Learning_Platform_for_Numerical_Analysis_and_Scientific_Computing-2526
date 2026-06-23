# ============================================================
# Test d'integration : endpoint /health
# ============================================================
# Verifie que l'app demarre et que /health retourne le bon JSON.
# ============================================================
from __future__ import annotations


def test_health_endpoint_returns_200(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "version" in body
    assert "llm" in body
    assert "provider" in body["llm"]
    assert "model" in body["llm"]
    assert "initialized" in body["llm"]
