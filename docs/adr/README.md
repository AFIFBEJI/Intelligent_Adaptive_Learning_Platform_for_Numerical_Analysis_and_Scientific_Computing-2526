# Architecture Decision Records (ADRs)

> An ADR documents **a structuring technical decision**: its context, the
> options considered, the decision made, and its consequences. Format
> inspired by Michael Nygard (2011).
>
> **Why ADRs in an undergraduate final-year project?**
> The defense committee will inevitably ask: *"Why did you choose X
> instead of Y?"*. These documents show that decisions are not arbitrary
> but result from a documented comparative analysis.

## Index

| # | Title | Status | Date |
|---|---|---|---|
| [001](./001-llm-provider-selection.md) | LLM provider selection (Ollama + OpenAI, not Claude) | ✅ Accepted | May 12, 2026 |
| [002](./002-frontend-framework.md) | No UI framework (Vanilla TypeScript vs React) | ✅ Accepted | May 12, 2026 |
| [003](./003-database-migrations.md) | Lightweight boot-time migrations vs Alembic | ✅ Accepted | May 12, 2026 |
| [004](./004-adaptive-vs-practice-mode.md) | Dual quiz mode `adaptive` vs `practice` | ✅ Accepted | May 12, 2026 |
| [005](./005-rag-retrieval-strategy.md) | RAG by keywords vs embeddings (FAISS) | ✅ Accepted | May 12, 2026 |

## Standard format

Each ADR follows the structure:

```
# ADR-XXX: Short title

## Status
Accepted | Proposed | Deprecated | Superseded by ADR-YYY

## Context
What problem are we solving? What constraints (technical, budget, deadline)?

## Options considered
List of alternatives, with their strengths and weaknesses.

## Decision
The chosen solution + main reason.

## Consequences

### Positive
Immediate and long-term benefits.

### Negative / accepted debt
The trade-offs we accept.

### Evolution plan
How we revisit this decision if the project grows.
```

## How to add a new ADR

1. Copy `_template.md` (if present) or use an existing ADR as inspiration
2. Increment the number (006, 007...)
3. Set status to `Proposed`, then `Accepted` after review
4. Update this index
5. If an ADR supersedes another: note `Superseded by ADR-XXX` in the older one
