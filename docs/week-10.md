# Week 10 — Grounded Ask (LLM-assisted RAG)

## Status

| Day | Scope | Status |
| --- | --- | --- |
| 1 | Phase A — Candidate retrieval (exact ∥ semantic, RRF merge) | Done |
| 2 | Phase B — LLM rerank (≤40 candidates, validated IDs) | Done |
| 3 | Phase C — Query analysis / rewrite (NL only, ≤4) | Done |
| 4 | Phase D — Context expansion (depth caps) | Done |
| 5 | Phase D — Grounded `POST /ask` + citation validator | Done |
| 6 | Ask UI | Planned |
| 7 | Phase E — Eval matrix (hybrid vs rewrite vs rerank vs full RAG) | Planned |

## Architecture (locked)

```text
User question
    ↓
[Optional] Query analysis (NL only; never paraphrase exact identifiers)
    ↓
Candidate retrieval: exact ∥ semantic → merge/dedupe (RRF) + path/symbol boosts
    ↓
[Optional] LLM rerank (top 30–40 only; validated chunk_ids; hybrid fallback)
    ↓
Deterministic context expansion (depth=1 default; depth=2 if low confidence)
    ↓
Grounded answer generation + citation post-validation
    ↓
Ask UI
```

### Hard constraints

**Rerank**

- Rerank at most **30–40** candidates from the merged pool
- One batched request where possible
- Never rerank 100+ chunks
- LLM may only return IDs from the supplied candidate set
- Invalid IDs dropped; fail → deterministic hybrid ranking

**Context / graph expansion**

- Default expand **depth = 1** (neighbors + direct callers/callees where deep)
- Expand **depth = 2** only when retrieval confidence is low
- Hard token budget + dedupe overlapping context
- Deterministic assembly only (LLM does not invent relationships)

**Authority**

- Do not remove exact / semantic / hybrid search
- Do not use the LLM as the sole retriever
- `GET .../chunks/search` stays deterministic and cheap
- `POST .../ask` is opt-in, budgeted, cached, kill-switchable
- Repository text is untrusted data (prompt-injection resistant)
- Never invent files, symbols, ranges, or relationships
- Cite every substantive claim with `path:start-end`; post-validate citations

### Evaluation gate

Compare:

1. hybrid retrieval only  
2. hybrid + LLM query rewriting  
3. hybrid + LLM reranking  
4. full LLM-assisted RAG  

Metrics: Recall@5, Recall@10, MRR, citation correctness, unsupported-claim rate,
latency, tokens, estimated cost.

**Keep the LLM path only if it measurably improves retrieval or answer quality.**

### Cost / safety

- Cache analysis + rerank by query, snapshot, prompt version, candidate hashes
- Limit rewrites to 4; rerank ≤ 40
- Per-job budgets + kill switches (reuse `llm/budget.py` patterns)
- CI: Ask off / mocked; local-hash embeddings

## Prerequisites

Week 9 Days 5–7 complete (Validating + Search UI + matrix).

## Days 1–2 shipped

### Day 1 — RRF candidate retrieval

- `app/services/rag/candidates.py` — independent exact ∥ semantic pools (default 30 each)
- Reciprocal Rank Fusion (`ask_rrf_k=60`) + path boost
- Search mode: `search_mode=rrf` (hybrid weighted fusion unchanged)
- Config: `ask_candidate_exact_limit`, `ask_candidate_semantic_limit`, `ask_rrf_k`

### Day 2 — LLM rerank

- `app/services/rag/rerank.py` — cap **≤40** candidates; one batched call
- Structured JSON; invent `chunk_id`s dropped; empty/invalid → RRF fallback
- CI default: deterministic mock rerank (`ask_rerank_use_mock=true`)
- Live Azure chat when `ask_rerank_use_mock=false` + `AZURE_OPENAI_DEPLOYMENT` set
- Search mode: `search_mode=rerank`
- Tests: `tests/test_rag_week10_day1_2.py`

### Day 3 — Query analysis / rewrite

- `app/services/rag/query_analysis.py` — classify identifier / path / NL / architectural / debugging / mixed
- Rewrite **NL / architectural / mixed only**; identifiers and paths never paraphrased
- At most **4** retrieval queries (`ask_query_max_rewrites`); original always retained
- Kill switch: `ask_query_rewrite_enabled=false` → original only

### Day 4 — Context expansion

- `app/services/rag/context_expand.py` — same-file neighbors + deep callers/callees
- Default **depth=1**; **depth=2** only when retrieval confidence is low
- Hard token budget (`ask_context_token_budget`) + chunk-id dedupe; deterministic only
- `app/services/rag/pipeline.py` — `retrieve_ask_bundle` composes analyze → multi-query RRF → rerank → expand
- Tests: `tests/test_rag_week10_day3_4.py`

### Day 5 — Grounded Ask + citation validator

- `POST /api/v1/repositories/{id}/ask` — retrieve → answer → post-validate citations
- `app/services/rag/citations.py` — parse `path:start-end`; drop invented / out-of-evidence spans
- `app/services/rag/answer.py` — mock default (`ask_use_mock=true`); Azure chat when mock off
- Opt-in / kill-switch: `ask_enabled`, `llm_kill_switch`; budget via `EnrichmentBudget`
- Cache answers by snapshot + question + prompt + evidence ids (`ask_cache_enabled`)
- Response includes `answer`, validated `citations`, `evidence`, `analysis`, `validation`
- Tests: `tests/test_rag_week10_day5.py`
