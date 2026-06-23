# ADR-001: LLM provider selection

**Status**: ✅ Accepted
**Date**: May 12, 2026
**Author**: Yassine Ben Nessib, validated by Afif Beji (supervisor)

## Context

The AI tutor is the core of the project (PFE Phase 2). It must produce
rigorous mathematical explanations, bilingual (FR/EN), with controlled
cost and response latency under 5 seconds.

**Constraints**:

- **Budget**: academic project, no cloud infrastructure funding.
- **GDPR**: we process student data (questions asked to the tutor) →
  must be able to run locally if needed.
- **Defense latency**: live demo in August 2026 → the LLM must be
  responsive even if Internet is unstable.
- **Paper reproducibility**: 6 months after publication, the experiment
  must remain reproducible (a proprietary model that silently changes
  would break reproducibility).
- **Mathematical quality**: numerical analysis = SymPy + LaTeX +
  multi-step reasoning. Not all LLMs are equal on this (cf. Frieder et
  al. 2024 on the MATH-LLM benchmark).

## Options considered

### Option A: OpenAI only (GPT-4o-mini)
- **+** Excellent math quality (gpt-4o-mini scores 84% on MATH).
- **+** Perfectly bilingual.
- **+** Low latency (~2-5 s).
- **−** Marginal cost: ~$0.0005 / question × 30 students × 50 questions =
  ~$0.75 for the study. Acceptable but risk of budget leakage if abuse.
- **−** Internet dependency (problem during demo if campus is down).
- **−** GDPR: data leaves to OpenAI (US).
- **−** No reproducibility: OpenAI can retire gpt-4o-mini without notice.

### Option B: Anthropic Claude
- **+** Very good math quality (Claude 3.5 Sonnet ~75% on MATH).
- **+** Bilingual.
- **−** Same problems as OpenAI (cloud, paid, GDPR).
- **−** Less French documentation.

### Option C: Google Gemini
- **+** Free up to a certain quota.
- **−** Quota changes frequently, unstable.
- **−** Math quality inferior to GPT-4o or Claude.
- **−** GDPR: data sent to Google.

### Option D: Ollama local (open-source model)
- **+** 100% local, perfect GDPR.
- **+** Free, reproducible.
- **+** No Internet dependency.
- **−** Lower quality on 7-8B models (Gemma, Llama).
- **−** Higher latency (~15-30 s on CPU, ~3-8 s on consumer GPU).
- **−** More complex setup (install Ollama, download model, create Modelfile).

### Option E: Hybrid Ollama + OpenAI (with runtime selection)
- **+** Combines advantages: Ollama for privacy/cost, OpenAI for quality.
- **+** Frontend `picker`: the user or teacher chooses based on context.
- **+** Automatic fallback: if Ollama is down → OpenAI.
- **+** Enables empirical comparison for the paper (fine-tuned Gemma
  quality vs GPT-4o-mini).
- **−** More code to maintain (two providers).
- **−** More complex E2E tests (mock providers).

## Decision

**Option E retained: hybrid Ollama + OpenAI strategy, with runtime selection.**

**Configured models**:

- **Ollama (local, default)**: `gemma-numerical-e2b` (Gemma 2-2B
  fine-tuned on 144 bilingual numerical analysis examples, loss 3.22 on T4).
- **OpenAI (cloud, fallback)**: `gpt-4o-mini` (excellent quality/price
  ratio, $0.15 / M input tokens).

**Implementation**: `backend/app/services/llm_service.py`
- Dict `_clients = {"ollama": ..., "openai": ...}` initialized at boot.
- `generate_response(provider_override=...)` routes to the right client.
- `available_providers()` exposes what works to the frontend for the picker.
- `bind_json()` unifies JSON-mode between Ollama (`format="json"`) and
  OpenAI (`response_format=json_object`).

**Default choice**: Ollama, because (1) free, (2) GDPR, (3) guaranteed
available during defense demo even if Internet is down.

## Consequences

### Positive

- **Robust defense demo**: if OpenAI has an outage, we switch to Ollama
  in one frontend click (picker).
- **Scientific originality**: the IEEE paper can empirically compare
  fine-tuned Gemma vs gpt-4o-mini on the same 25-30 students → publishable
  result ("can we replace a cloud LLM with a local 7B fine-tune?").
- **GDPR-safe by default**: as long as we stay on Ollama, no data leaves
  the ESPRIT infrastructure.
- **Controlled cost**: ~$5-10 total for the user study (15 students ×
  OpenAI), the other 15 on free Ollama.

### Negative / accepted debt

- **Doubled provider code**: `llm_service.py` is ~600 lines (vs ~300 if
  single provider). Acceptable because well isolated in a single file.
- **Tests must mock both providers**: we have a single global mock in
  `test_tutor_integration.py:mock_llm_pipeline`. Not a major overhead.
- **Prompt maintenance in duplicate**: for now, prompts are identical, but
  eventually we might have prompts adapted to Gemma vs GPT (Gemma prefers
  more directive prompts).

### Evolution plan

- **If project deployed at larger scale**: add a 3rd provider (Anthropic
  Claude) for vendor diversity and to avoid OpenAI dependency.
- **If fine-tuned Gemma outperforms gpt-4o-mini in the user study**: make
  Ollama the default and OpenAI backup only (×10 savings).
- **If OpenAI releases a better model (gpt-5)**: just change
  `LLM_MODEL_NAME` in `.env`, no code change.

## References

- Frieder, S., et al. (2024). *Mathematical capabilities of ChatGPT*. NeurIPS.
- Ollama docs: https://ollama.com/library
- OpenAI pricing: https://platform.openai.com/docs/pricing
- Source file for this decision: `backend/app/services/llm_service.py`
