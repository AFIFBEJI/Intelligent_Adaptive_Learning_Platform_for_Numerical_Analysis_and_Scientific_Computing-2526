# ADR-004: Dual quiz mode `adaptive` vs `practice`

**Status**: ✅ Accepted
**Date**: May 12, 2026
**Author**: Yassine Ben Nessib, validated by the pedagogical angle of
Afif Beji

## Context

An adaptive learning system maintains a **mastery level** per concept
(0-100%), which then determines:

- The complexity level of upcoming content (`simplified`, `standard`,
  `rigorous` according to `mastery < 30 / 30-70 / > 70`).
- The recommended path (next unlocked concept).
- The tutor's feedback (conceptual orientation or deeper exploration).

**Pedagogical problem observed in pilot**: students avoid quizzes for
fear of "penalizing their mastery" → they don't practice. This is the
opposite of the intended effect: an adaptive system should ENCOURAGE
attempts, not penalize them.

## Options considered

### Option A: Single mode, all quizzes update mastery
- **+** Simple to implement.
- **+** Rich data for the adaptive engine.
- **−** Negative psychological effect: fear of testing → less practice.
- **−** A bad day damages visible progression.
- **−** Not aligned with recent pedagogical literature (Bjork & Bjork,
  2011, *Making things hard on yourself, but in a good way*).

### Option B: Single mode without mastery
- **+** No pressure.
- **−** We lose the signal for adaptation. The system no longer knows
  when a concept is mastered.
- **−** Contradicts the "personalized" objective.

### Option C: Dual mode + explicit pedagogical intent
`adaptive` quiz → updates mastery, generates a path.
`practice` quiz → free training, does NOT affect mastery.

- **+** Separates evaluation and training (metacognitive practice
  recommended by Nuthall, 2007).
- **+** Student can practice without fear, then "test themselves"
  formally when they feel ready.
- **+** Data still collected in the background (clickstreams, time,
  answers) → no loss for user-study analysis.
- **−** More code: 2 paths in the service.
- **−** UI must clearly differentiate the two modes.

## Decision

**Option C retained: dual mode encoded on the `Quiz` object.**

**Crucial implementation choice**: the mode is **on the Quiz**, NOT on
the `QuizResult`. Why?

- The mode is decided at quiz GENERATION (auto-selected difficulty by
  mastery vs manual "practice mode" choice).
- Putting the mode on the `QuizResult` would allow the student to submit
  the same quiz twice with different modes → data inconsistency.
- Single source of truth on Quiz side: guarantees longitudinal coherence.

**Implementation**: `backend/app/models/quiz.py:Quiz.mode`

```python
mode = Column(String(20), nullable=False, default="adaptive", index=True)
```

**Gate in the submit endpoint**: `backend/app/routers/quiz_dynamic.py`

```python
if quiz.mode == "adaptive":
    feedback_service.update_mastery_from_evaluations(db, etudiant_id, evaluations)
# In "practice" mode: we skip the update, mastery stays intact.
```

**UI**: a clear toggle "Practice mode (does not impact my level)" visible
before each generated quiz.

## Consequences

### Positive

- **Pedagogical effect**: we expect increased engagement
  (`session_count`, `quiz_attempts_count`) without degraded results.
  Testable hypothesis in the user study (cf. `docs/phase4/`).
- **Path safety**: a student who fails 5 practice quizzes in a row does
  not see their path collapse. Their unlocked prerequisites remain unlocked.
- **Paper metric**: we can compare in the user study the practice/adaptive
  ratio chosen by Adaptive vs Control students, and see whether heavy
  practice users progress better.

### Negative / accepted debt

- **More complex data analysis**: to compute the "true" learning gain, we
  must weight practice vs adaptive (a practice score doesn't exactly
  reflect the level; the student can bluff to train).
- **Risk of gaming**: a student could do 10 easy adaptive quizzes to boost
  their mastery, then take the post-test. Mitigation: the stratification
  algorithm uses the **pre-test** as baseline, not the current mastery.

### Evolution plan

- **If the user study shows that practice mode is NOT used**: remove the
  feature, simplify the code. Acceptable.
- **If overused (>80% practice)**: differentiated weighting
  (`mode=practice → 20% contribution to mastery` instead of 0%, to study).
- **Analytics tracking**: we already log `study_events.quiz_attempt` with
  the mode → data for empirical decision.

## References

- Bjork, R. A., & Bjork, E. L. (2011). *Making things hard on yourself,
  but in a good way: Creating desirable difficulties to enhance learning.*
- Nuthall, G. (2007). *The hidden lives of learners.* NZCER Press.
- Source files for this decision: `backend/app/models/quiz.py`,
  `backend/app/routers/quiz_dynamic.py:323-352`.
