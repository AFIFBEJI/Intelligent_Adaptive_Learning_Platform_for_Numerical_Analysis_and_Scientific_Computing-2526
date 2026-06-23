# Phase 4 — Implémentation backend `/study/*` (12 mai 2026)

> Code prêt à tester. Reste à connecter le frontend (3 pages).

## Fichiers créés

| Fichier | Rôle | Lignes |
|---|---|---|
| `backend/app/models/study.py` | Tables SQL : `study_participants`, `study_events` | ~95 |
| `backend/app/data/study_pretest.py` | Banque de 30 items pré/post-test (5 concepts × 6) + helpers `items_for_version()` et `grade_answers()` | ~330 |
| `backend/app/schemas/study.py` | Pydantic : EnrollResponse, TestStartResponse, TestSubmitRequest, SUS, ParticipantSummary | ~115 |
| `backend/app/routers/study.py` | Router REST `/study/*` : enroll, pretest GET/POST, posttest GET/POST, sus, withdraw, admin overview & list | ~340 |
| `backend/scripts/export_study_data.py` | Export CSV pseudonymisé pour analyse pandas/scipy | ~120 |

## Fichiers modifiés (hook)

- `backend/app/routers/__init__.py` — ajoute `study` aux imports
- `backend/app/main.py` — branche `study.router` dans `ROUTERS`
- `backend/app/core/config.py` — ajoute `STUDY_ADMIN_EMAILS` (whitelist admin)

## Endpoints exposés

| Method | Path | Auth | Rate-limit | Rôle |
|---|---|---|---|---|
| POST | `/study/enroll` | JWT | 3/min | Inscription dans l'étude + génère pseudonyme P### + contre-balancing A/B |
| GET | `/study/pretest` | JWT | — | Retourne 15 items du pré-test (version assignée) |
| POST | `/study/pretest` | JWT | 60/min | Submit pré-test → calcule score + stratifie + alloue groupe `adaptive`/`control` |
| GET | `/study/posttest` | JWT | — | Retourne 15 items du post-test (version inverse) |
| POST | `/study/posttest` | JWT | 60/min | Submit post-test |
| POST | `/study/sus` | JWT | 60/min | Questionnaire SUS-adapted 6 items Likert + 3 questions ouvertes |
| POST | `/study/withdraw` | JWT | — | Retrait RGPD avec raison optionnelle |
| GET | `/study/admin/overview` | JWT + admin | — | Stats globales (enroll, completed, by_group) |
| GET | `/study/admin/participants` | JWT + admin | — | Liste détaillée pseudonymisée |

## Stratification automatique

L'allocation `adaptive` / `control` est calculée à la soumission du pré-test :

1. **Strate** : low (< 40), mid (40-70), high (≥ 70) selon `pre_score`
2. Dans chaque strate, alternance pair → adaptive / impair → control
3. Garantit un équilibre 1:1 par strate sans dépendre du hasard pur

**Avantage** : statistiquement plus puissant qu'une randomisation simple, et reproductible.

## Schéma SQL généré au boot

```sql
CREATE TABLE study_participants (
    id INTEGER PRIMARY KEY,
    etudiant_id INTEGER UNIQUE NOT NULL REFERENCES etudiants(id) ON DELETE CASCADE,
    participant_code VARCHAR(16) UNIQUE NOT NULL,
    study_wave INTEGER NOT NULL DEFAULT 1,
    group_assigned VARCHAR(16),
    test_version VARCHAR(16) NOT NULL,
    pre_score FLOAT,
    post_score FLOAT,
    sus_score FLOAT,
    pre_answers JSON,
    post_answers JSON,
    sus_answers JSON,
    open_feedback JSON,
    enrolled_at TIMESTAMP NOT NULL,
    pre_test_started_at TIMESTAMP,
    pre_test_done_at TIMESTAMP,
    intervention_started_at TIMESTAMP,
    post_test_done_at TIMESTAMP,
    withdrawn_at TIMESTAMP,
    withdrawal_reason VARCHAR(255)
);

CREATE TABLE study_events (
    id INTEGER PRIMARY KEY,
    participant_id INTEGER NOT NULL REFERENCES study_participants(id) ON DELETE CASCADE,
    event_type VARCHAR(32) NOT NULL,
    payload JSON,
    timestamp TIMESTAMP NOT NULL
);
```

Les tables sont créées automatiquement au prochain démarrage par `Base.metadata.create_all()` dans `main.py:lifespan`.

## Tests rapides à faire (sur ta machine)

```powershell
# 1. Boot le serveur, vérifier les nouvelles routes
cd backend
uvicorn app.main:app --reload
# Ouvre http://localhost:8000/docs : tu dois voir le tag "Phase 4 - User Study"

# 2. Test fonctionnel manuel (avec un compte etudiant deja inscrit)
$TOKEN = "ton_jwt"

# Enroll
curl -X POST -H "Authorization: Bearer $TOKEN" http://localhost:8000/study/enroll

# GET pretest items
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/study/pretest

# Submit pretest (15 reponses, 0=premiere option, 1=seconde, etc.)
$body = @{
  answers = @{
    "A1"="2"; "A2"="1"; "A3"="1 - x**2"; "A4"="1"; "A5"="2";
    "A6"="2"; "A7"="1"; "A8"="1"; "A9"="1"; "A10"="1";
    "A11"="2"; "A12"="1"; "A13"="1"; "A14"="1"; "A15"="1"
  }
  duration_seconds = 1200
} | ConvertTo-Json
curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" `
  -d $body http://localhost:8000/study/pretest

# Vérifier dans la DB
psql ... -c "SELECT participant_code, group_assigned, pre_score FROM study_participants;"
```

## Frontend à coder (estimation : 2 jours)

Trois pages à créer dans `frontend/src/pages/` :

1. **`study-welcome.ts`** — affiche le consentement, bouton "J'accepte → POST /study/enroll", redirige vers pretest
2. **`study-test.ts`** — page unifiée pré-test ET post-test (selon `phase` param). GET items, render QCM, submit. Au submit, affiche le score puis redirige selon phase.
3. **`study-sus.ts`** — formulaire 6 sliders Likert + 3 textarea, POST /study/sus.

Idée pour l'admin : ajouter une page `study-admin.ts` qui appelle `/study/admin/overview` + `/study/admin/participants` et affiche un tableau filtré (gated par email côté backend, donc pas besoin de role côté front).

## À configurer dans `.env`

```bash
# Whitelist des emails admin de l'étude (séparés par virgules)
STUDY_ADMIN_EMAILS=eyabenncib100@gmail.com,afif.beji@esprit.tn
```

## Export pour analyse stats (semaine 7-8)

```powershell
cd backend
python -m scripts.export_study_data --out ../analysis/study_data.csv
```

Le CSV produit alimente directement le notebook Jupyter d'analyse (voir `01_PROTOCOLE_USER_STUDY.md` §7 pour le pseudo-code Python).

## Sécurité — récap

- ✅ Tous les endpoints `/study/*` requièrent JWT (auth)
- ✅ Endpoints admin gated par email whitelist (`STUDY_ADMIN_EMAILS`)
- ✅ Rate-limit sur enroll (3/min) + submit (60/min)
- ✅ `participant_code` généré côté serveur via `secrets.randbelow` (non-devinable)
- ✅ Pseudonymisation : le CSV d'export ne contient JAMAIS d'email ni de nom
- ✅ Withdraw idempotent + raison stockée pour conformité RGPD art. 17

---

**Version :** 1.0 — 12 mai 2026
