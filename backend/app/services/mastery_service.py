"""Source unique de verite pour la mise a jour du niveau de maitrise.

Pourquoi ce service ?
=====================
Avant le 12 mai 2026, la logique de mise a jour de `ConceptMastery` etait
DUPLIQUEE dans deux endroits :

1. `routers/quiz.py:update_mastery` (formule EWMA 0.6 * old + 0.4 * new)
2. `services/feedback_service.py:update_mastery_from_evaluations`
   (meme formule + agregation des partial_credits par concept)

Risque : si la formule evolue (ex: moving average, decay temporel), il faut
penser a maintenir les deux endroits. C'est la source classique de divergence
silencieuse et de regressions difficiles a diagnostiquer.

L'audit senior du 12/05/2026 a flag cette duplication comme dette P1.
Ce module est la solution : une seule fonction de calcul, deux APIs
(unitaire + aggregator) qui partagent l'implementation.

Formule canonique
=================
Pour chaque concept, le mastery est mis a jour par une moyenne ponderee :

    new_mastery = round(0.6 * old + 0.4 * new_score, 1)

Si l'etudiant n'avait pas de ligne ConceptMastery pour ce concept, on en
cree une initialisee avec `new_score`.

Choix de la formule (justifie dans l'ADR a venir) :
- 60% de poids historique : evite que le mastery oscille trop sur un quiz
  raté isole (un mauvais jour ne plombe pas la progression).
- 40% sur le nouveau score : reactif quand-meme aux progres reels.
- Arrondi a 1 decimale : evite la pollution des floats sur de longues
  series (`32.07000000001` -> `32.1`).
"""
from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.mastery import ConceptMastery

# ============================================================
# Constantes (centralisees pour ajustement futur via ADR)
# ============================================================
OLD_WEIGHT = 0.6
NEW_WEIGHT = 0.4

# Sanity check : les deux poids doivent sommer a 1.0 (sinon on ne fait
# plus une moyenne ponderee mais un drift). Si tu modifies les valeurs,
# garde toujours cette propriete.
assert OLD_WEIGHT + NEW_WEIGHT == 1.0, "OLD_WEIGHT + NEW_WEIGHT doit egaler 1.0"


# ============================================================
# API 1 — Application unitaire (un seul concept, un seul score)
# ============================================================
def apply_mastery_delta(
    db: Session,
    etudiant_id: int,
    concept_id: str,
    new_score: float,
) -> ConceptMastery:
    """Met a jour (ou cree) la ligne ConceptMastery d'un etudiant.

    new_score : 0-100 (le score percu par l'etudiant sur ce concept).

    Cette fonction NE COMMIT PAS. Le caller est responsable du commit
    (souvent en fin de transaction quiz/evaluation pour grouper plusieurs
    updates).

    Retourne l'objet ConceptMastery (cree ou modifie). Utile pour les
    tests qui veulent assert sur l'etat resultat.
    """
    mastery = (
        db.query(ConceptMastery)
        .filter(
            ConceptMastery.etudiant_id == etudiant_id,
            ConceptMastery.concept_neo4j_id == concept_id,
        )
        .first()
    )
    now = datetime.now(UTC)
    if mastery is None:
        mastery = ConceptMastery(
            etudiant_id=etudiant_id,
            concept_neo4j_id=concept_id,
            niveau_maitrise=round(new_score, 1),
            derniere_mise_a_jour=now,
        )
        db.add(mastery)
    else:
        mastery.niveau_maitrise = round(
            mastery.niveau_maitrise * OLD_WEIGHT + new_score * NEW_WEIGHT,
            1,
        )
        mastery.derniere_mise_a_jour = now
    return mastery


# ============================================================
# API 2 — Aggregator depuis une liste d'evaluations quiz
# ============================================================
def update_mastery_from_evaluations(
    db: Session,
    etudiant_id: int,
    evaluations,  # list[QuestionEvaluation] - on evite l'import circulaire
) -> dict[str, float]:
    """Met a jour les mastery a partir d'une liste d'evaluations de questions.

    Chaque evaluation a un `concept_id` (Neo4j) et un `partial_credit` (0.0-1.0).
    On groupe par concept et on calcule la moyenne des partial_credits, puis on
    applique le delta. Les evaluations sans concept_id sont ignorees (ex:
    questions hors taxonomie).

    Retourne {concept_id: new_score_percent} pour les concepts effectivement
    touches (utile pour le logging et les tests).
    """
    # Grouper les partial_credits par concept (un quiz peut tester plusieurs
    # concepts a la fois ; on aggrege par moyenne intra-concept).
    by_concept: dict[str, list[float]] = {}
    for e in evaluations:
        if not getattr(e, "concept_id", None):
            continue
        by_concept.setdefault(e.concept_id, []).append(e.partial_credit)

    updated: dict[str, float] = {}
    for concept_id, scores in by_concept.items():
        # Score moyen normalise sur 100.
        new_score = (sum(scores) / len(scores)) * 100.0
        apply_mastery_delta(db, etudiant_id, concept_id, new_score)
        updated[concept_id] = round(new_score, 1)
    return updated
