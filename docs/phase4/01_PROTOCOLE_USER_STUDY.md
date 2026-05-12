# Phase 4 — Protocole expérimental de l'étude utilisateur

> **Projet :** Intelligent Adaptive Learning Platform for Numerical Analysis
> **Investigateur :** Yassine Ben Nessib (ESPRIT), encadré par Afif Beji
> **Date de rédaction :** 12 mai 2026
> **Période d'exécution prévue :** 26 mai 2026 → 6 juillet 2026 (6 semaines)
> **Cible :** IEEE Transactions on Learning Technologies (TLT) — IF ~3.7

---

## 1. Question de recherche et hypothèses

### 1.1 Question principale (RQ)

> **RQ :** Une plateforme adaptative combinant graphe de connaissances Neo4j,
> tutorat LLM ancré (GraphRAG) et vérification symbolique SymPy améliore-t-elle
> significativement l'apprentissage de l'analyse numérique par rapport à un
> cours en ligne statique équivalent ?

### 1.2 Hypothèses

| Code | Énoncé | Test stat | α |
|---|---|---|---|
| **H1** | Le gain d'apprentissage (post − pré) est significativement plus élevé dans le groupe **Adaptive** que dans le groupe **Control**. | t-test indépendant (ou Mann-Whitney si non-normal) sur la variable `learning_gain` | 0.05 |
| **H2** | Le temps moyen pour atteindre `mastery ≥ 70` sur les 5 concepts cibles est significativement plus court dans le groupe Adaptive. | t-test sur `time_to_mastery` | 0.05 |
| **H3** | La satisfaction subjective (échelle Likert 1-5 sur 6 items adaptés du *System Usability Scale*) est significativement plus élevée dans Adaptive. | t-test sur le score SUS-adapted total (6-30) | 0.05 |
| **H4 (exploratoire)** | La validation SymPy intercepte ≥ 90 % des erreurs mathématiques produites par le LLM. | Pourcentage d'erreurs détectées dans 200 réponses tuteur échantillonnées. | — |

---

## 2. Design expérimental

### 2.1 Type

**Quasi-experimental, between-subjects, pré-test / post-test à 2 bras.**

```
                    ┌──────────────────────────────────────┐
                    │            Pre-test (T0)             │
                    │   (commun aux 2 groupes, 20 min)     │
                    └──────────────────────────────────────┘
                                       │
                ┌──────────────────────┴──────────────────────┐
                ▼                                             ▼
        ┌───────────────┐                           ┌───────────────┐
        │ Group A       │                           │ Group B       │
        │ ADAPTIVE      │                           │ CONTROL       │
        │ Notre platforme│                          │ Notes statiques│
        │ + Tuteur LLM   │                          │ + Quiz fixes   │
        │ + Quiz adapt.  │                          │ (même contenu, │
        │ 4 semaines     │                          │  pas d'IA)     │
        └───────────────┘                           └───────────────┘
                │                                             │
                └──────────────────────┬──────────────────────┘
                                       ▼
                    ┌──────────────────────────────────────┐
                    │            Post-test (T1)            │
                    │       (mêmes concepts, 20 min)       │
                    │      + Questionnaire SUS adapté      │
                    └──────────────────────────────────────┘
```

### 2.2 Pourquoi pas un design within-subjects ?

Sequence effects + carry-over (un étudiant qui a vu le tuteur LLM ne peut pas "oublier" pour la suite). Between-subjects est le standard IEEE TLT pour ce type d'études EdTech.

### 2.3 Aléatorisation

- Stratification par **niveau initial** (3 strates basées sur le pré-test : faible <40%, moyen 40-70%, fort >70%).
- À l'intérieur de chaque strate, allocation 1:1 vers Adaptive / Control via random.org (seed enregistré).
- Allocation **non aveugle** côté étudiant (impossible d'aveugler la condition), mais aveugle côté analyste (le notebook d'analyse statistique reçoit `group_id ∈ {A, B}` sans connaître l'étiquette).

---

## 3. Participants

### 3.1 Taille d'échantillon

**Cible : n = 30 étudiants ESPRIT (15 par groupe).**

**Justification (G*Power 3.1) :**
- Test : t-test indépendant 2 groupes.
- Effet attendu : Cohen's d = 1.0 (effet large, typique des études adaptive learning vs statique — cf. Belland et al. 2017).
- α = 0.05, puissance = 0.80.
- → n minimal par groupe = **17**. On vise 30 total + buffer 5 (drop-out attendu 15-20%) = **35 inscrits initiaux**.

### 3.2 Critères d'inclusion

- Étudiant ESPRIT (3GL ou 4GL) inscrit en 2025-2026.
- A déjà suivi un cours d'analyse numérique (sinon impossible d'évaluer la connaissance préalable).
- Accepte le consentement éclairé.
- Disponible 4 semaines consécutives, ~3h/sem (engagement total ~12h).

### 3.3 Critères d'exclusion

- Étudiant ayant participé au développement (Yassine + supervisé(s) éventuel(s)) — biais.
- Étudiant ayant déjà été exposé au prototype en démo (biais de familiarité).

### 3.4 Recrutement

- **Canal 1** : annonce dans les promo Discord/Slack ESPRIT 3GL et 4GL.
- **Canal 2** : email aux délégués de classe avec affiche en PDF (à préparer).
- **Canal 3** : 10 min de "pitch" à la fin du cours d'analyse numérique d'Afif Beji (encadrant) — 30 sec, lien Google Form.
- **Incitatif** : participation tirée au sort = 1 carte cadeau Amazon 50 TND par groupe (= 100 TND total, faible mais éthique pour étude académique).

### 3.5 Drop-out planning

- Définition : un participant qui ne complète pas le post-test ou qui n'utilise pas la plateforme ≥ 3 sessions sur 4 semaines.
- Stratégie : analyse en **intent-to-treat** (n initial) ET en **per-protocol** (n complétant). Reporter les deux.

---

## 4. Procédure (par participant)

### 4.1 Semaine 0 (jour 1) — Inscription + pré-test (~30 min)

1. L'étudiant clique sur le lien d'inscription envoyé par mail.
2. Lit + signe le formulaire de consentement (cf. `02_CONSENTEMENT.md`).
3. Crée un compte sur la plateforme (`/auth/register`).
4. Passe le pré-test (15-20 questions, ~20 min, cf. `03_PRE_POST_TEST.md`).
5. Le système assigne automatiquement le groupe (Adaptive ou Control) après stratification.
6. Notification par mail de la condition.

### 4.2 Semaines 1-4 — Phase intervention (~3h/sem)

**Groupe Adaptive** (notre plateforme) :
- Accès libre à la plateforme.
- Suit le parcours adaptatif : Module 1 (interpolation) → Module 2 (intégration) → Module 3 (approximation polynomiale & optimisation) → Module 4 (root-finding).
- Doit faire au moins **2 sessions par semaine** (logging automatique).
- Peut consulter le tuteur LLM librement, faire des quiz adaptifs.

**Groupe Control** (matériel statique) :
- Reçoit un **PDF statique** (généré depuis le contenu de la plateforme, version "rigorous" pour tous).
- Reçoit un **quiz fixe** par module (les mêmes pour tous, pas d'adaptation).
- Pas d'accès au tuteur LLM, pas de feedback personnalisé.
- Engagement attendu équivalent (~3h/sem).

**Activité loggée automatiquement** :
- Connexions, durée des sessions
- Nombre de quiz tentés, scores, temps de réponse
- Nombre de questions au tuteur, longueur des réponses
- Évolution `mastery` par concept

### 4.3 Semaine 5 — Post-test + questionnaire (~30 min)

1. Post-test (15-20 questions, **même périmètre** que pré-test mais items différents pour éviter l'effet d'apprentissage du test, cf. §6).
2. Questionnaire SUS-adapté (6 items Likert 1-5) + 3 questions ouvertes :
   - Qu'est-ce qui t'a le plus aidé ?
   - Qu'est-ce qui t'a frustré ?
   - Recommanderais-tu cette plateforme à un autre étudiant ?
3. (Optionnel — groupe Adaptive uniquement) : entretien semi-directif 15 min avec 5 volontaires pour feedback qualitatif.

---

## 5. Mesures (variables)

### 5.1 Variable indépendante (IV)

- **Condition** : `{Adaptive, Control}` — variable nominale à 2 niveaux.

### 5.2 Variables dépendantes (DV) primaires

| Variable | Calcul | Source |
|---|---|---|
| `learning_gain` | `post_test_score − pre_test_score` (en pourcentage, range −100 à +100) | Pré/post-test |
| `normalized_gain` | `(post − pre) / (100 − pre)` — *Hake's gain* (1998), standard EdTech | Pré/post-test |
| `time_to_mastery` | Temps cumulé (minutes) jusqu'à atteindre `mastery ≥ 70` sur les 5 concepts cibles | `ConceptMastery` + logs |
| `sus_score` | Score Likert agrégé (6-30) | Questionnaire post |

### 5.3 Variables dépendantes secondaires

| Variable | Calcul |
|---|---|
| `session_count` | Nombre de connexions à la plateforme |
| `tutor_questions_count` | Nombre de questions posées au tuteur (group Adaptive uniquement) |
| `quiz_attempts_count` | Nombre de tentatives de quiz |
| `avg_quiz_score` | Score moyen sur tous les quiz |
| `engagement_score` | (session_count × avg_session_duration) / target |

### 5.4 Variables exploratoires (paper § Discussion)

- `sympy_validation_catch_rate` : % de réponses du tuteur où SymPy a corrigé/flaggé une erreur math (échantillon manuel de 200 réponses).
- `concept_difficulty_perceived` : pour chaque concept, score de difficulté ressenti (item Likert 1-5).
- `tutor_satisfaction_score` : 3 items Likert sur la qualité du tuteur (clarté, pertinence, justesse math).

---

## 6. Pré/post-test : équivalence et fiabilité

### 6.1 Construction des 2 versions

- **Banque commune** : 30 items couvrant les 5 concepts cibles, niveaux easy/medium/hard balancés.
- Items mappés sur les concepts Neo4j (`concept_lagrange`, `concept_simpson`, `concept_newton_raphson`, `concept_bissection`, `concept_least_squares`).
- Version A (pré-test) : 15 items tirés au hasard.
- Version B (post-test) : les 15 items restants.
- **Validation d'équivalence** : pilote sur 5 étudiants → comparer scores moyens A vs B → écart < 5 points.

### 6.2 Fiabilité

- Alpha de Cronbach calculé après collecte (cible ≥ 0.7).
- Test-retest sur 3 étudiants pilotes (espacement 1 semaine) : corrélation cible r ≥ 0.7.

### 6.3 Contre-balancing

50% des participants reçoivent A en pré / B en post, 50% l'inverse. Réduit le biais d'item-specificité.

---

## 7. Plan d'analyse statistique

### 7.1 Tests primaires (H1, H2, H3)

```python
# Pseudo-code Python (pandas + scipy.stats)
import pandas as pd
from scipy import stats

df = pd.read_csv("user_study_data.csv")

# H1 : learning gain
adaptive_gain = df[df.group == "Adaptive"].learning_gain
control_gain  = df[df.group == "Control"].learning_gain

# Vérifier normalité (Shapiro-Wilk)
_, p_adaptive = stats.shapiro(adaptive_gain)
_, p_control  = stats.shapiro(control_gain)

if p_adaptive > 0.05 and p_control > 0.05:
    # Normalité OK → t-test indépendant (Welch)
    t, p = stats.ttest_ind(adaptive_gain, control_gain, equal_var=False)
else:
    # Non-normal → Mann-Whitney U
    t, p = stats.mannwhitneyu(adaptive_gain, control_gain, alternative="greater")

# Effect size (Cohen's d)
import numpy as np
pooled_std = np.sqrt(((adaptive_gain.std()**2) + (control_gain.std()**2)) / 2)
cohens_d = (adaptive_gain.mean() - control_gain.mean()) / pooled_std

print(f"t={t:.3f}, p={p:.4f}, Cohen's d={cohens_d:.3f}")
```

Reporter dans le paper : moyenne ± SD par groupe, t (ou U), p, Cohen's d (ou r), 95% CI.

### 7.2 Tests secondaires

- ANCOVA si tu veux contrôler pour le niveau initial (`pre_test_score` en covariable).
- Régression linéaire multiple `learning_gain ~ group + tutor_questions_count + session_count` pour identifier les médiateurs (group Adaptive uniquement).

### 7.3 Correction multiple

3 tests primaires (H1, H2, H3) → **Bonferroni-Holm** ou **Benjamini-Hochberg (FDR)**. Choisir Holm si tu veux contrôler le FWER, BH si tu acceptes un FDR < 5%.

### 7.4 Données manquantes

- < 10% par variable : *listwise deletion* OK.
- 10-30% : imputation multiple (`sklearn.impute.IterativeImputer` ou `mice` en R).
- > 30% : analyse de sensibilité + drop la variable.

---

## 8. Logging / instrumentation à ajouter dans la plateforme

**À implémenter cette semaine (avant lancement) :**

| Évènement | Endpoint à instrumenter | Champs |
|---|---|---|
| `study.pretest.start` | `/study/pretest/start` (NEW) | user_id, timestamp, group_assigned |
| `study.pretest.submit` | `/study/pretest/submit` (NEW) | user_id, score, answers, time_taken |
| `study.session.start` | middleware `/api/*` | user_id, timestamp |
| `study.session.end` | middleware (inactivity 5 min) | user_id, duration |
| `study.quiz.attempt` | `/quiz-ai/{id}/submit` (existant, ajouter event) | user_id, quiz_id, score, time |
| `study.tutor.question` | `/tutor/sessions/{id}/ask` (existant, ajouter event) | user_id, session_id, char_count, concept_id |
| `study.posttest.submit` | `/study/posttest/submit` (NEW) | user_id, score, answers, sus_responses |

Stockage : table SQL `study_events(id, user_id, event_type, timestamp, payload JSON)`.

Conseil : tu peux extraire toute la donnée nécessaire de `ConceptMastery` + `QuizResult` + `TutorMessage` existants, **pas besoin de créer 7 nouveaux endpoints**. Crée juste un script `scripts/export_study_data.py` qui agrège tout dans un CSV par participant à la fin.

---

## 9. Éthique et RGPD

- **Consentement éclairé** : signé avant le pré-test (cf. `02_CONSENTEMENT.md`).
- **Données pseudonymisées** : pas d'email ni de nom dans les exports CSV — uniquement un `participant_id` opaque.
- **Droit de retrait** : à tout moment, suppression complète des données sur demande à eyabenncib100@gmail.com.
- **Conservation** : 5 ans (durée standard recherche académique), puis suppression.
- **Stockage** : base SQLite chiffrée locale + sauvegarde sur disque chiffré ESPRIT. Pas de cloud externe.
- **DPO ESPRIT** : informer le délégué RGPD ESPRIT avant le lancement (formulaire interne à demander).

---

## 10. Timeline détaillée

| Semaine | Dates | Activité |
|---|---|---|
| **−2** | 12-25 mai | Préparation : finaliser ce protocole, valider avec encadrant, écrire pré/post-test, créer le matériel Control (PDF + quiz fixes), instrumenter le logging. |
| **−1** | 19-25 mai | Pilote sur 3-5 étudiants volontaires (test du flow complet) + ajustements. |
| **1** | 26 mai - 1er juin | Recrutement + inscriptions + pré-test. Verrouiller n=30. |
| **2-5** | 2 - 29 juin | Phase intervention (4 semaines actives) + monitoring drop-outs. |
| **6** | 30 juin - 6 juil | Post-test + entretiens qualitatifs. |
| **7-8** | 7 - 20 juil | Analyse statistique + rédaction draft paper. |
| **9** | 21 - 27 juil | Relecture encadrant + corrections. |
| **10** | 28 juil - 3 août | Soumission IEEE TLT + finalisation rapport PFE. |

**Soutenance probable : mi-août 2026.**

---

## 11. Risques et plan de mitigation

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| Drop-out > 30% | Moyenne | Élevé | Buffer +5 recrutements ; rappels mail hebdomadaires ; carte cadeau loterie. |
| Effet d'apprentissage du pré-test | Faible | Moyen | Items différents pré/post (cf. §6) + contre-balancing. |
| Bug critique en plein milieu de l'étude | Moyenne | Élevé | Freeze du code pendant la phase intervention (pas de déploiement nouveau). Hotfix-only. |
| Pas assez d'étudiants ESPRIT recrutés | Moyenne | Élevé | Élargir : étudiants ENIT, INSAT, IPEIT en backup. |
| LLM indisponible (rate-limit OpenAI / Ollama planté) | Faible | Élevé | Fallback automatique Ollama → OpenAI déjà en place. Procédure de redémarrage rapide doc-mentée. |
| Données perdues | Faible | Catastrophique | Backup quotidien automatique de la DB SQLite vers disque chiffré. |
| Effet placebo (groupe Adaptive plus motivé car "high-tech") | Élevée | Moyen | À discuter dans § Limitations du paper. Pas de mitigation totalement possible. |

---

## 12. Livrables attendus

- ✅ `01_PROTOCOLE_USER_STUDY.md` (ce document)
- 🟡 `02_CONSENTEMENT.md` (formulaire bilingue) → en cours
- 🟡 `03_PRE_POST_TEST.md` (30 items + grille de correction) → en cours
- 🟡 `04_PAPER_OUTLINE.md` (structure IEEE TLT prête à remplir) → en cours
- ⬜ Affiche A4 de recrutement (à dériver)
- ⬜ Google Form d'inscription (à créer la semaine -2)
- ⬜ Script Python `scripts/export_study_data.py` (à coder la semaine -1)
- ⬜ Notebook Jupyter d'analyse `analysis/study_analysis.ipynb` (à coder la semaine 7)

---

**Auteur :** Yassine Ben Nessib, supervisé par Afif Beji
**Version :** 1.0 — 12 mai 2026
**Prochaine révision :** après validation encadrant (cible 19 mai)
