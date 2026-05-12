# Paper IEEE TLT — Outline complet

> **Cible :** IEEE Transactions on Learning Technologies (TLT)
> **IF 2024 :** ~3.7 (Q1 Education & Educational Research)
> **Format :** Regular paper, 12-14 pages double-colonne IEEEtran
> **Soumission cible :** début août 2026

---

## Titre proposé (3 options à départager avec encadrant)

1. **"GraphRAG-Powered Adaptive Tutoring with Symbolic Verification: A
   Knowledge-Graph and LLM Approach to Numerical Analysis Education"**
2. **"NumeraTutor: An Adaptive Learning Platform Combining Neo4j Knowledge
   Graphs, LLM Tutoring, and SymPy Verification for Numerical Analysis"**
3. **"Reducing Hallucinations in AI Tutors: A Symbolic-Verification
   Framework for Adaptive Mathematics Education"**

Recommandation senior : **option 1** — explicite sur les 3 contributions
techniques (GraphRAG + symbolic verification + adaptive), positionne le
paper comme une *contribution méthodologique* plutôt qu'un simple
*system paper*.

---

## Abstract (≤ 250 mots, à finaliser après les résultats)

**Structure suggérée :**

> **Context** (2 phrases) — Les LLMs offrent des perspectives prometteuses
> pour le tutorat personnalisé, mais hallucinent fréquemment en
> mathématiques. Les plateformes adaptive learning existantes manquent
> d'ancrage formel et de raisonnement sur graphe.
>
> **Objective** (1 phrase) — Nous proposons et évaluons une plateforme
> combinant graphe de connaissances Neo4j, retrieval-augmented generation,
> et vérification symbolique SymPy, appliquée à l'enseignement de
> l'analyse numérique.
>
> **Method** (2 phrases) — Étude entre-sujets, n=30 étudiants ingénieurs,
> 2 conditions (Adaptive vs Static), 4 semaines, pré/post-test sur 5
> concepts (interpolation, intégration, moindres carrés, Newton-Raphson,
> bissection).
>
> **Results** (3 phrases) — [À remplir après analyse — typiquement : gain
> normalisé moyen d'apprentissage X% (Adaptive) vs Y% (Control), p=Z,
> Cohen's d=K. Temps jusqu'à mastery réduit de N%. SUS-adapted score
> M (Adaptive) vs L (Control).]
>
> **Contribution** (1 phrase) — Première démonstration empirique qu'une
> combinaison GraphRAG + vérification symbolique améliore
> significativement les résultats d'apprentissage en analyse numérique,
> avec un taux d'hallucination mathématique inférieur à 10%.

**Keywords** : adaptive learning, knowledge graph, large language models,
GraphRAG, symbolic verification, numerical analysis, intelligent tutoring
systems.

---

## I. Introduction (~1.5 page)

### Plan détaillé

**Para 1 — Motivation pédagogique** (200 mots)
- Demande croissante en compétences quantitatives.
- Taux d'échec persistant en analyse numérique (citer : NSF 2019, ESPRIT
  rapport interne si disponible).
- L'enseignement traditionnel ne s'adapte pas aux profils hétérogènes.

**Para 2 — Promesse et limites des LLMs en éducation** (200 mots)
- Capacité de tutorat personnalisé démontrée (Khan Academy, etc.).
- **Mais** : hallucinations mathématiques (cite Bender et al. 2021,
  Frieder et al. 2024 sur le math reasoning des LLMs).
- Études existantes : peu d'ancrage formel, peu de validation.

**Para 3 — Notre approche** (200 mots)
- Trois piliers : (1) Knowledge graph Neo4j pour raisonner sur prérequis,
  (2) GraphRAG pour ancrer le LLM dans du contenu vérifié, (3) SymPy pour
  intercepter les erreurs mathématiques résiduelles.
- Différence avec les ITS classiques (rule-based) et avec les LLM bruts.

**Para 4 — Contributions du paper** (150 mots, bulletted)

> Cet article apporte les contributions suivantes :
>
> 1. **Architecture technique** : intégration originale de Neo4j +
>    LLM (Gemma fine-tuné ou GPT-4o-mini) + SymPy pour le tutorat
>    mathématique.
> 2. **Méthodologie d'évaluation** : protocole expérimental rigoureux
>    entre-sujets sur 30 étudiants, en conditions écologiques.
> 3. **Évidence empirique** : amélioration significative du gain
>    d'apprentissage et de la satisfaction.
> 4. **Open data + open-source** : code et données pseudonymisées
>    disponibles pour reproductibilité.

**Para 5 — Structure de l'article** (50 mots)

> La Section II passe en revue la littérature pertinente. La Section III
> décrit l'architecture du système. La Section IV présente le protocole
> expérimental. La Section V rapporte les résultats. La Section VI
> discute les implications et limites. La Section VII conclut.

---

## II. Related Work (~1.5 page, 4 sous-sections)

### II.A Adaptive Learning Systems

- Knewton, ALEKS, Mathia : ITS rule-based.
- DKT, Deep Knowledge Tracing (Piech et al. 2015).
- Limites : modélisation surface du savoir, pas d'ancrage explicite.

### II.B Knowledge Graphs in Education

- KG pour curriculum sequencing (Chen et al. 2020).
- KGs in MOOCs (Zhang et al. 2022).
- **Gap** : pas d'usage de KG comme contexte d'un LLM tuteur.

### II.C LLMs as Tutors

- Khanmigo (Khan Academy), Duolingo Max, ChatGPT EDU.
- Études d'efficacité limitées et controversées (Latif et al. 2023).
- Hallucinations en math : Frieder et al. 2024 sur MATH-LLM benchmark.

### II.D Symbolic Verification of LLM Outputs

- Math-LM, Lean4, Coq pour formalisation.
- Approches hybrides LLM + theorem prover (Polu & Sutskever 2020).
- **Gap** : peu d'usage en contexte pédagogique temps réel.

### II.E Positionnement de notre travail

Tableau comparatif :

| Système | Adaptive | KG | LLM Tutor | Symbolic Check | Eval Empirique |
|---|---|---|---|---|---|
| ALEKS | ✓ | ⊘ | ⊘ | ⊘ | ✓ |
| Khanmigo | ⊘ | ⊘ | ✓ | ⊘ | ⊘ |
| Latif 2023 | ⊘ | ⊘ | ✓ | ⊘ | ✓ |
| **Nous** | **✓** | **✓** | **✓** | **✓** | **✓** |

---

## III. System Architecture (~2.5 pages)

### III.A Vue d'ensemble (1 figure : "Figure 1: System architecture")

Pipeline complet : Frontend (React/TS) → FastAPI → {Auth, KG, Quiz,
Tutor} → {PostgreSQL, Neo4j, LLM provider} → SymPy verifier.

### III.B Knowledge Graph (Neo4j)

- Schéma : `(Module)-[:COVERS]->(Concept)-[:REQUIRES]->(Concept)`,
  `(Concept)-[:REMEDIATES_TO]->(Concept)`.
- 4 modules, 19 concepts, 49 relations.
- Bilingue (FR + EN).
- Tests d'intégrité automatisés en CI (test_seed_integrity.py : 15 assertions).

### III.C GraphRAG-Based Tutor

- Pseudo-algo : `find_concept(query) → fetch_prerequisites + mastery →
  inject_context → LLM call → SymPy check`.
- Choix du provider : Ollama (Gemma E2B fine-tuné, local) ou OpenAI
  (gpt-4o-mini, fallback cloud). Routage par config.
- Prompt adaptatif 3 niveaux selon mastery (simplified / standard / rigorous).

### III.D Symbolic Verification Layer

- `verify_equation`, `verify_derivative_claim`, `verify_integral_claim`.
- Détecte équations fausses, dérivées incorrectes, intégrales mal calculées.
- 17 tests unitaires garantissent la fiabilité.
- Latence moyenne mesurée : X ms (à remplir).

### III.E Adaptive Quiz Engine

- Banque 105 questions hand-curated bilingues + génération LLM optionnelle.
- Calibration auto post-diagnostic.
- Mode `adaptive` (met à jour mastery) vs `practice` (entraînement libre).

### III.F Implementation Stack (tableau)

| Couche | Technologie | Lignes |
|---|---|---|
| Backend | FastAPI 0.115, Python 3.11 | ~7,900 |
| Frontend | TypeScript 5.3 (vanilla SPA), Vite | ~10,800 |
| KG | Neo4j 5 | 19 concepts, 49 rels |
| DB | PostgreSQL 16 | 6 tables |
| LLM | Ollama (Gemma-E2B), OpenAI (gpt-4o-mini) | — |
| Symbolic | SymPy 1.13 | 4 endpoints verif |
| Containerization | Docker Compose | 4 services |

---

## IV. Experimental Method (~1.5 page)

(Largement transcrit de `01_PROTOCOLE_USER_STUDY.md` § 2-7.)

### IV.A Design

Quasi-experimental between-subjects, pré-post, 2 groupes Adaptive vs Control.

### IV.B Participants

n=30 (15 par groupe), étudiants ingénieurs, recrutés à ESPRIT.

### IV.C Materials

Pré/post-test 15 items chacun, mêmes 5 concepts, items isomorphes
(`03_PRE_POST_TEST.md`). Contre-balancing A/B.

### IV.D Procedure

(Diagramme Figure 2 : timeline de 6 semaines.)

### IV.E Measures

DV primaires : learning_gain, normalized_gain (Hake), time_to_mastery,
sus_score. DV secondaires : engagement, tutor_questions_count.

### IV.F Data Analysis Plan

Pré-enregistré. T-tests indépendants (Welch) ou Mann-Whitney selon
normalité (Shapiro-Wilk). Cohen's d. Correction Benjamini-Hochberg sur
H1-H3.

### IV.G Ethics

Consentement éclairé. RGPD + loi tunisienne 2004-63 (cf.
`02_CONSENTEMENT.md`). DPO ESPRIT informé.

---

## V. Results (~2 pages, structure à remplir après collecte)

### V.A Participant Characteristics (Table 1)

| | Adaptive (n=) | Control (n=) | p |
|---|---|---|---|
| Age (M ± SD) | | | |
| Sex (% F) | | | |
| Pre-test score (M ± SD) | | | |
| ... | | | |

### V.B Primary Outcomes

**H1 (Figure 3 : box plot des learning gains par groupe)**

> Le gain d'apprentissage moyen était de XX.X% (SD = X.X) dans le groupe
> Adaptive vs YY.Y% (SD = Y.Y) dans Control. Le t-test indépendant
> (Welch) révèle une différence significative, t(df) = ZZZ, p = .000X,
> Cohen's d = D.DD (effet [petit/moyen/grand]).

**H2 (Figure 4 : Kaplan-Meier survival pour mastery ≥ 70%)**

> Le temps moyen jusqu'à mastery ≥ 70 sur les 5 concepts cibles était de
> XX min (SD = X) dans Adaptive vs YY min (SD = Y) dans Control,
> p = .00X, d = D.DD.

**H3 (Table 2 : SUS-adapted scores)**

> Score SUS-adapted moyen : Adaptive = X.X / 30 (SD = X.X), Control =
> Y.Y / 30 (SD = Y.Y), p = .00X.

### V.C Secondary Outcomes

- Engagement : sessions, durées, quiz attempted.
- Corrélations : tutor_questions vs learning_gain (groupe Adaptive uniquement).

### V.D Exploratory Analyses

**H4 : Symbolic verification catch rate**

> Sur 200 réponses tuteur échantillonnées, SymPy a détecté X erreurs
> mathématiques (Y%), dont Z étaient des hallucinations critiques
> (équations fausses, dérivées incorrectes).

**Analyse qualitative (entretiens, n=5)** :

> Thèmes émergents : (1) appréciation du feedback ciblé, (2) frustration
> sur la latence parfois, (3) confiance dans les explications après
> vérification.

---

## VI. Discussion (~1.5 page)

### VI.A Principales conclusions

3 paragraphes résumant H1, H2, H3 et leur signification.

### VI.B Implications théoriques

- Confirme que l'ancrage formel (KG + SymPy) compense les hallucinations LLM.
- Le modèle d'adaptation par mastery + prérequis fonctionne en conditions
  écologiques.

### VI.C Implications pratiques

- Pour les enseignants : un design pédagogique scalable.
- Pour les éditeurs de plateformes : un blueprint reproductible.

### VI.D Limitations

1. **Échantillon limité** (n=30, monocentrique ESPRIT) : généralisabilité
   à confirmer.
2. **Effet Hawthorne / placebo** : impossible d'aveugler la condition.
3. **Durée d'étude (4 semaines)** : effets à long terme inconnus.
4. **Couverture mathématique** : 5 concepts seulement, pas tout le curriculum.
5. **Pas de mesure de la rétention** : pas de test différé à 1 mois.

### VI.E Travaux futurs

- Réplication multi-établissements (ENIT, ENIS, INSAT).
- Étude de rétention à 3 mois et 6 mois.
- Extension à d'autres domaines (algèbre linéaire, EDOs, optimisation
  convexe).
- Open-source de la plateforme sous licence MIT pour réutilisation.

---

## VII. Conclusion (~0.5 page)

3 paragraphes : (1) rappel du problème, (2) notre contribution résumée
en 3 phrases, (3) impact attendu et invitation à la communauté.

---

## Acknowledgments

Mr. Afif Beji (encadrant), ESPRIT School of Engineering, les 30 étudiants
participants.

---

## References (~40 réfs à viser)

**Seed bibliographique (à compléter avec Zotero) :**

1. Belland, B. R., et al. (2017). Synthesizing results from empirical research on
   computer-based scaffolding in STEM education. *Review of Educational Research*.
2. Bender, E. M., et al. (2021). On the dangers of stochastic parrots. *FAccT*.
3. Chen, P., et al. (2020). KnowEdu: A system to construct knowledge graph for
   education. *IEEE Access*.
4. Frieder, S., et al. (2024). Mathematical capabilities of ChatGPT. *NeurIPS*.
5. Hake, R. R. (1998). Interactive-engagement versus traditional methods.
   *American Journal of Physics*.
6. Khan Academy. (2023). Khanmigo: Generative AI for learning.
7. Latif, E., et al. (2023). AGI in education: A multidimensional literature
   review. *arXiv:2304.12479*.
8. Lewis, P., et al. (2020). Retrieval-augmented generation. *NeurIPS*.
9. Neo4j. (2024). Graph database documentation v5.
10. Piech, C., et al. (2015). Deep knowledge tracing. *NIPS*.
11. Polu, S., & Sutskever, I. (2020). Generative language modeling for automated
    theorem proving. *arXiv:2009.03393*.
12. Vanlehn, K. (2011). The relative effectiveness of human tutoring, intelligent
    tutoring systems, and other tutoring systems. *Educational Psychologist*.
13. Zhang, J., et al. (2022). A knowledge graph-based MOOC recommendation system.
    *IEEE TLT*.

---

## Figures à produire

1. **Figure 1** : Architecture système (diagramme blocs + flèches data flow).
2. **Figure 2** : Timeline de l'étude (Gantt 6 semaines).
3. **Figure 3** : Box plot learning_gain par groupe (matplotlib seaborn).
4. **Figure 4** : Kaplan-Meier time_to_mastery (lifelines Python).
5. **Figure 5** : Heatmap mastery × concept × groupe (seaborn).
6. **Figure 6** : Exemple d'écran tuteur avec SymPy verification banner.

---

## Tables à produire

1. **Table 1** : Caractéristiques participants par groupe.
2. **Table 2** : SUS-adapted item-level + score total.
3. **Table 3** : Corrélations DV primaires × DV secondaires.
4. **Table 4** (supplément) : Détail des 30 items pré/post-test.

---

## Checklist de soumission IEEE TLT

- ☐ Manuscrit IEEEtran double-colonne, ≤ 14 pages incluant refs.
- ☐ Abstract ≤ 250 mots.
- ☐ Statement of contributions explicite en intro.
- ☐ Méthodes reproductibles (code GitHub + données pseudonymisées Zenodo).
- ☐ IRB approval ou équivalent (lettre de l'encadrant ESPRIT).
- ☐ Conflict-of-interest disclosure (aucun).
- ☐ Author contributions (CRediT taxonomy).
- ☐ Cover letter expliquant la contribution + fit avec TLT.
- ☐ Suggested reviewers (3-5, hors institution).

---

## Calendrier de rédaction

| Semaine | Sections à attaquer |
|---|---|
| 7 | Sections I, II, III (déjà 80% en tête, descriptive) |
| 8 | Section IV + premiers résultats préliminaires Section V |
| 9 | Section V finalisée (graphes, stats), Section VI premier jet |
| 10 | Section VI/VII, Abstract, References, polish |
| 10 (fin) | Relecture encadrant + corrections, soumission |

---

**Version** : 1.0 — 12 mai 2026
**Cible journal** : IEEE Transactions on Learning Technologies
**Auteur** : Yassine Ben Nessib (Y.B.N.), Afif Beji (A.B.)
