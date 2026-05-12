# ADR-005: RAG by keywords vs embeddings (FAISS)

**Status**: ✅ Accepted (v1 keyword-based, v2 embeddings planned)
**Date**: May 12, 2026
**Author**: Yassine Ben Nessib

## Context

The GraphRAG pipeline works as follows (cf.
`backend/app/services/rag_service.py`):

1. The student asks a question: *"how does Simpson's method work?"*
2. The RAG must identify WHICH Neo4j concept (among 19) it corresponds to.
3. Once identified → we fetch prerequisites + mastery + resources.
4. We inject all of this into the LLM context.

Step 2 is crucial: if we identify the wrong concept, the entire
downstream context is incorrect.

**Scope**: 19 concepts across 4 modules (Interpolation, Integration,
Polynomial Approximation, Root finding). Restricted technical vocabulary
but with ambiguities (Newton interpolation vs Newton-Raphson).

## Options considered

### Option A: Keyword pattern matching (heuristic)
- **+** Trivial implementation (4× name + 1× description + category bonus).
- **+** No dependency (no embedding model to load).
- **+** Zero latency (< 1 ms).
- **+** Explainable: we know exactly why a concept matched.
- **−** Fragile: "Newton" matches both `concept_newton_interpolation` and
  `concept_newton_raphson`. Solution: ad-hoc rules with contextual bonuses.
- **−** Not robust to paraphrases ("area under the curve" ≠ "integral").
- **−** Not multilingual out-of-the-box (matching FR vs EN).

### Option B: Embeddings sentence-transformers + FAISS
- **+** Semantically robust: "area under the curve" gets close to
  "integral".
- **+** Natively multilingual (model `paraphrase-multilingual-mpnet-base-v2`).
- **+** State of the art in 2026.
- **−** 470 MB model to download at boot.
- **−** Added latency: ~100-300 ms per request.
- **−** Low interpretability: we don't know why a concept matched
  (black box).
- **−** Must manage a persistent FAISS index (rebuild on each seed).

### Option C: LLM-as-classifier (one-shot prompting)
- **+** No heavy ML dependency, just an API call.
- **+** Very precise with a good prompt.
- **−** Cost: one LLM call per question, doubles the latency.
- **−** Circular dependency: we use the LLM to route to... the LLM.
- **−** Hard to test (non-deterministic LLM).

## Decision

**Option A retained for v1, with planned migration to Option B in v2.**

**Reasons**:

1. **Limited scope**: only 19 concepts. Keyword matching remains
   manageable, and we can hand-tune the heuristics.
2. **Critical latency for the demo**: the tutor must respond quickly. A
   200 ms delta per request × 50 student questions = 10 seconds wasted
   unnecessarily.
3. **Explainability required for the paper**: we want to be able to say
   "this concept was identified because of this keyword" for transparency.
4. **No heavy ML dependency**: maximizes IEEE paper reproducibility (no
   model that changes across versions).

**Implementation**: `backend/app/services/rag_service.py:find_concept`

```python
def find_concept(question: str, lang: str) -> str | None:
    """Score each concept by:
    - 4× match in name (`concept.name_fr` or `name_en`)
    - 1× match in description
    - +8 bonus if question contains a category keyword
      (e.g., 'iteration' -> bonus for Module 4 root_finding).
    Returns the top-scoring concept_id, or None if no match.
    """
```

**Anti-collision heuristics** (notable Newton case):

- If question contains "interpolation" / "polynomial" → bonus to
  `concept_newton_interpolation`.
- If question contains "root" / "roots" / "zero" → bonus to
  `concept_newton_raphson`.
- If question contains "optimization" / "minimum" → bonus to
  `concept_newton_optimization`.

## Consequences

### Positive

- **Robust demo**: on the 105 hand-curated questions from the bank, the
  RAG identifies the right concept in > 90% of cases (measured by manual
  inspection).
- **Negligible latency**: < 1 ms per request, negligible compared to the
  ~3-15 s of the LLM.
- **No deployment surprises**: no model to download, the Docker image
  stays under 500 MB.
- **Paper explainability**: we can list exactly which keywords matched
  (paper appendix).

### Negative / accepted debt

- **Capped precision**: on very paraphrased questions ("area of a trapezoid
  between 2 points") the algorithm fails. Estimate: 8-12% false negatives
  on open student questions.
- **Maintenance**: adding a concept = adding its keywords. Tedious but OK
  for the current 19 concepts.
- **Not suitable for growth**: if we expand to 100+ concepts (linear
  algebra extension, PDEs), migration will be needed.
- **No fine logging**: we don't know IN which cases matching failed →
  hard to improve empirically. To fix: log top-3 scores in `study_events`.

### Evolution plan (v2 — embeddings)

**Trigger for migration**: if the user study reveals > 15% off-topic
tutor responses (wrong concept identified).

**v2 migration plan**:

1. Add `sentence-transformers` + `faiss-cpu` to dependencies.
2. At boot: encode the 19 (concept_name + description) into 768d vectors.
3. Store the FAISS index in `backend/app/data/concept_index.faiss`.
4. At runtime: encode the question + cosine similarity, top-1.
5. Keep the keyword scorer as fallback if embedding score < 0.5.
6. A/B test (50% users keyword, 50% embeddings) to empirically measure.

**Estimate**: 1-2 days of dev + 2 days of tuning. To be done during July
(Phase 4 user study ongoing but code frozen).

## References

- Lewis, P., et al. (2020). *Retrieval-Augmented Generation for
  Knowledge-Intensive NLP*. NeurIPS.
- sentence-transformers: https://www.sbert.net
- FAISS: https://github.com/facebookresearch/faiss
- Source file for this decision: `backend/app/services/rag_service.py:find_concept`
