# Week 9 — Embeddings + retrieval foundation

## Status

| Day | Scope | Status |
| --- | --- | --- |
| 1 | Embedding schema + EmbeddingProvider (local default) | Done |
| 2 | Wire worker Embedding stage + persist vectors | Done |
| 3 | Semantic search API | Planned |
| 4 | Hybrid ranking | Planned |
| 5 | Worker Validating stage | Planned |
| 6 | Functional Search UI | Planned |
| 7 | Matrix / honesty / smoke | Planned |

## Architecture (locked)

```text
Persisted chunks (Week 7) — parser ranges authoritative
        ↓
EmbeddingProvider (local-hash default; Azure optional)
        ↓
chunk_embeddings (pgvector, dims=64) + model/version metadata
        ↓
Worker: Chunking → Embedding → (Validating later) → Completed
        ↓
Search: exact (exists) | semantic | hybrid (Days 3–4)
```

### Days 1–2 shipped

- Migration `0009_chunk_embeddings` — pgvector `chunk_embeddings` table
- `EmbeddingProvider` protocol + factory (`local` | `azure_openai` | `none`)
- `LocalHashEmbeddingProvider` — deterministic CI-safe vectors (no ML / network)
- Optional `AzureOpenAIEmbeddingProvider` (pad/truncate to platform dims)
- Settings: `embeddings_enabled`, `embedding_provider`, `embedding_model`,
  `embedding_version`, `embedding_dimensions`, `embedding_batch_size`
- `replace_embeddings_for_snapshot` — idempotent by content hash + model/version
- Worker runs **Embedding** after Chunking; Validating still deferred
- Tests: `test_embeddings_week09.py`, `test_embeddings_persist_week09.py`,
  worker pipeline asserts one embedding per chunk

### Invariants

- Exact search remains independent of embeddings
- Disabling embeddings clears snapshot vectors and still completes the job
- No regex structural extraction; no deep claims for generic languages
- Parser ranges never altered by embedding stage

## Artifacts

- `apps/api/alembic/versions/0009_chunk_embeddings.py`
- `apps/api/app/services/embeddings/`
- `apps/api/app/models/entities.py` (`ChunkEmbedding`)
- `apps/worker/worker/__main__.py` (Embedding stage)
- `apps/api/tests/test_embeddings_week09.py`
- `apps/api/tests/test_embeddings_persist_week09.py`
