# Week 9 — Embeddings + retrieval foundation

## Status

| Day | Scope | Status |
| --- | --- | --- |
| 1 | Embedding schema + EmbeddingProvider (local default) | Done |
| 2 | Wire worker Embedding stage + persist vectors | Done |
| 3 | Semantic search API | Done |
| 4 | Hybrid ranking | Done |
| 5 | Worker Validating stage | Done |
| 6 | Functional Search UI | Done |
| 7 | Matrix / honesty / smoke | Done |

## Architecture (locked)

```text
Persisted chunks (Week 7) — parser ranges authoritative
        ↓
EmbeddingProvider (local-hash default; Azure optional)
        ↓
chunk_embeddings (pgvector, dims=1536) + model/version metadata
        ↓
Worker: Chunking → Embedding → Validating → Completed
        ↓
Search: exact | semantic | hybrid (API + Search UI)
```

### Days 1–2 shipped

- Migration `0009_chunk_embeddings` — pgvector `chunk_embeddings` table
- Migration `0010_embedding_dimensions_1536` — vector(64) → vector(1536)
- `EmbeddingProvider` protocol + factory (`local` | `azure_openai` | `none`)
- `LocalHashEmbeddingProvider` — deterministic CI-safe vectors
- `AzureOpenAIEmbeddingProvider` — Foundry v1 (`*.services.ai.azure.com`) or legacy Azure OpenAI;
  requests `dimensions=` from the API (no pad/truncate)
- Worker runs **Embedding** after Chunking
- Tests: `test_embeddings_week09.py`, `test_embeddings_persist_week09.py`

### Days 3–4 shipped

- `GET .../chunks/search?search_mode=exact|semantic|hybrid`
- Hybrid fusion (default 50/50) + path boost; configurable weights
- Hybrid weight eval on Azure embeddings: see `docs/testing/week9-hybrid-eval/`
- Product default remains **0.50 exact / 0.50 semantic**

### Day 5 shipped

- `app/services/snapshot_validation.py` — citation readiness, generic honesty,
  embedding count/dimension consistency
- Worker stage: Embedding → **Validating** → Completed
- `SnapshotValidationError` → retry with `snapshot_validation_failed`
- Tests: `test_snapshot_validation_week09.py`

### Day 6 shipped

- Functional Search UI (`apps/web/src/pages/SearchPage.tsx`)
- Modes: exact / semantic / hybrid; filters; citations `path:start-end`
- Honesty footer: exact offline; semantic needs embeddings; Ask not on this page
- Client: `fetchRepositoryChunksSearch` + `lib/chunks.ts`

### Day 7 shipped

- Matrix: mixed + polyglot worker → exact/semantic/hybrid + Validating completed
- Honesty: generic never `verified_deep`; semantic empty when embeddings disabled
- Tests: `test_week09_day7_matrix.py`
- Frontend SearchPage + stubs honesty updated

### Invariants

- Exact search remains independent of embeddings
- Disabling embeddings clears snapshot vectors and still completes the job
- No regex structural extraction; no deep claims for generic languages
- Parser ranges never altered by embedding or validating stages
- Ask / LLM-assisted RAG is **Week 10**, not part of Week 9 Search

## Artifacts

- `apps/api/alembic/versions/0009_chunk_embeddings.py`
- `apps/api/alembic/versions/0010_embedding_dimensions_1536.py`
- `apps/api/app/services/embeddings/`
- `apps/api/app/services/snapshot_validation.py`
- `apps/api/app/services/chunks_query.py`
- `apps/worker/worker/__main__.py`
- `apps/web/src/pages/SearchPage.tsx`
- `apps/api/tests/test_week09_day7_matrix.py`
- `docs/testing/week9-hybrid-eval/`
