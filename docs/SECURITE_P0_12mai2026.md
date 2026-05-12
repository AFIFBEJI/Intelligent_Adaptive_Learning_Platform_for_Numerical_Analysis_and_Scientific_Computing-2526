# Corrections de sécurité P0 — 12 mai 2026

> Suite à l'audit senior, application des 4 actions critiques.

## Fichiers modifiés

| Fichier | Nature | Quoi |
|---|---|---|
| `backend/app/routers/etudiants.py` | EDIT | Fix IDOR sur `GET /etudiants/` + `/etudiants/{id}` |
| `backend/app/schemas/etudiant.py` | EDIT | `EmailStr` + `min_length=8` sur password |
| `backend/app/core/rate_limit.py` | NEW | Module central pour les quotas slowapi |
| `backend/app/main.py` | EDIT | Branchement limiter + middleware + handler 429 |
| `backend/app/routers/auth.py` | EDIT | `@limiter.limit(...)` sur `/login`, `/forgot-password`, `/request-verification` |
| `backend/app/routers/tutor.py` | EDIT | `@limiter.limit(...)` sur `/sessions/{id}/ask` |
| `backend/app/routers/quiz_dynamic.py` | EDIT | `@limiter.limit(...)` sur `/generate` et `/diagnostic` |
| `backend/requirements.txt` | EDIT | `slowapi` + `email-validator` ajoutés |
| `frontend/index.html` | EDIT | Chargement DOMPurify CDN |
| `frontend/src/pages/tutor.ts` | EDIT | Sanitization XSS dans `formatTutorContent` |

## P0.1 — Fix IDOR `/etudiants/`

**Avant** : `GET /etudiants/` retournait la liste de **tous** les étudiants à n'importe quel user.
**Après** : ne retourne QUE le profil de l'utilisateur courant. `GET /etudiants/{id}` : 403 si ID ≠ user courant.

## P0.2 — Validation Pydantic stricte

**Avant** : `email: str` acceptait `"foo"` ; `mot_de_passe: str` acceptait `"a"`.
**Après** : `EmailStr` (RFC 5322) + password 8-128 caractères. Idem sur `EmailRequest`.
**Note** : `email-validator` ajouté à `requirements.txt`.

## P0.3 — Rate-limiting (slowapi)

| Endpoint | Quota | Raison |
|---|---|---|
| `POST /auth/login` | 10/min | Anti brute-force |
| `POST /auth/forgot-password` | 3/min | Anti-spam SMTP |
| `POST /auth/request-verification` | 3/min | Anti-spam SMTP |
| `POST /tutor/sessions/{id}/ask` | 20/min | Budget LLM (~$0.10/min max) |
| `POST /quiz-ai/generate` | 20/min | Budget LLM |
| `POST /quiz-ai/diagnostic` | 20/min | Budget LLM |

Constantes dans `app/core/rate_limit.py` — facile à ajuster.

## P0.4 — Sanitization XSS (DOMPurify)

**Avant** : `tutor.ts:1139` injectait `formatTutorContent(msg.content)` en innerHTML sans sanitization.
**Après** : DOMPurify 3.0.9 via CDN, whitelist stricte (`h1-3`, `strong`, `em`, `code`, `ul/ol/li`, `p`, `br`, `span`). Fail-closed : escape HTML brut si DOMPurify indispo.

## À faire côté utilisateur

```powershell
# 1. Installer les nouvelles dépendances
cd backend
pip install -r requirements.txt

# 2. Smoke test
uvicorn app.main:app --reload

# 3. Tests backend
pytest tests/test_auth_integration.py tests/test_email_integration.py -q

# 4. Build frontend
cd ../frontend
npm run build

# 5. Commit + push
cd ..
git add backend/app/core/rate_limit.py backend/app/main.py `
        backend/app/routers/auth.py backend/app/routers/etudiants.py `
        backend/app/routers/tutor.py backend/app/routers/quiz_dynamic.py `
        backend/app/schemas/etudiant.py backend/requirements.txt `
        frontend/index.html frontend/src/pages/tutor.ts `
        docs/SECURITE_P0_12mai2026.md docs/AUDIT_SENIOR_12mai2026.md
git commit -m "security(P0): rate-limit + IDOR fix + EmailStr + DOMPurify XSS"
git push origin ma-branche
```

## Tests E2E de sécurité

```bash
# 1. IDOR test
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/etudiants/
# Attendu : retourne UN seul étudiant.

# 2. Rate-limit test
for i in {1..15}; do
  curl -X POST http://localhost:8000/auth/login \
    -d "username=foo&password=bar" \
    -H "Content-Type: application/x-www-form-urlencoded"
done
# Attendu : 10 premières → 401, suivantes → 429.

# 3. EmailStr test
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"nom_complet":"X","email":"foo","mot_de_passe":"abc","langue_preferee":"fr"}'
# Attendu : 422 avec erreurs de validation.
```

## Effets de bord

- Tous les tests existants utilisent `xxx@test.local` (valide pour EmailStr) et passwords ≥ 8 chars. Pas de régression.
- Aucun appel au `/etudiants/` côté frontend détecté. Pas d'impact UI.
- Quotas généreux pour la démo. Augmenter `LLM_HEAVY_LIMIT` si besoin pendant la soutenance.

---

**Auteur** : audit + corrections appliquées
**Date** : 12 mai 2026
