# System Architecture

## High-level diagram

```text
React + TypeScript frontend
            │
            ▼
        FastAPI API
            │
      ┌─────┴───────────┐
      ▼                 ▼
PostgreSQL          Background worker
+ pgvector          PostgreSQL job queue
      │                 │
      └────────┬────────┘
               ▼
      Repository snapshots
               │
      ┌────────┴─────────┐
      ▼                  ▼
Deep parsers       Generic text pipeline
Python/Java/       Other textual languages
TS/JavaScript
      │                  │
      └────────┬─────────┘
               ▼
     Hybrid retrieval system
               │
               ▼
   Citation-validated AI answers
```

## Monorepo layout (target)

```text
codebase-intelligence/
├── apps/
│   ├── api/          # FastAPI HTTP API
│   ├── worker/       # Background indexing worker
│   └── web/          # React + Vite frontend
├── packages/
│   ├── parser-core/
│   ├── parser-fixtures/
│   └── shared-types/
├── docs/
├── infrastructure/
├── scripts/
├── docker-compose.yml
└── Makefile
```

## Runtime components

| Component | Responsibility |
| --- | --- |
| `web` | UI: import, jobs, search, ask, symbols, graphs, file viewer |
| `api` | Auth-ready HTTP surface, repository/job/search/ask APIs |
| `worker` | Claims jobs, clones, indexes, embeds, validates |
| `postgres` | Relational data + pgvector embeddings + job queue |
| Local embeddings | Batch vectors for chunks/symbols/sections |
| Ollama (local) | Default LLM for Ask; optional hosted provider later |

## Data model (initial / evolving)

Core entities introduced early:

- `users`
- `repositories`
- `repository_snapshots`
- `indexing_jobs`
- `source_files` (with language + support_level + parser metadata)
- symbols / heuristic sections
- relationships / graph edges
- chunks + embeddings

Snapshots are immutable views of a repository at a commit SHA. Indexing jobs attach to snapshots and report stage + progress.

## Job queue

PostgreSQL-backed queue using `FOR UPDATE SKIP LOCKED`:

- Job claiming and worker lease
- Heartbeat / expired-lease recovery
- Retry with backoff
- Idempotent processing per commit + pipeline version

Statuses: `QUEUED`, `RUNNING`, `SUCCEEDED`, `FAILED`, `CANCELLED`

## Parsing strategy

```text
File discovered
    │
    ▼
Language detection (extension / filename)
    │
    ▼
ProcessingStrategy: DEEP | GENERIC | SKIP
    │
    ├─ DEEP → existing AST / Tree-sitter → symbols + relationships + symbol-aware chunks
    ├─ GENERIC → Tree-sitter / format-native parsers → generic_structure chunks
    │            (+ optional validated LLM enrichment; never verified Symbol rows)
    └─ SKIP → ignored with reason
```

Deep parsers for Python / Java / JS / TS live under `apps/api/app/services`
(not a separate generic Tree-sitter path). Regex must not define structural
boundaries — see [language-support.md](./language-support.md).

## Retrieval architecture

Query classification routes to tools / ranking signals:

- Exact text
- Symbol / heuristic section
- Semantic vector (pgvector)
- Graph proximity (callers, callees, imports)
- Configuration / documentation boosts

Hybrid ranker combines scores; UI exposes Hybrid / Semantic / Symbols / Exact / Config / Docs tabs.

## Ask architecture

```text
User question
  → retrieve evidence via tools (search, symbols, ranges, graph)
  → LLM drafts structured answer + citations
  → citation validator checks file/snapshot/lines/retrieval/support_level
  → response to UI with badges + expandable evidence
```

Providers:

- Optional `LLMProvider` abstraction for enrichment / Ask (OpenAI, Azure OpenAI,
  Anthropic, or another configured provider)
- Local Ollama when configured
- Enrichment and Ask remain opt-in / capped; deterministic index never depends on them

## Local vs temporary cloud

| Phase | Topology |
| --- | --- |
| Weeks 1–11 | Docker Compose: web, api, worker, postgres; LLM enrichment opt-in |
| Week 12 | Temporary Azure Container Apps + ACR + static frontend + Supabase Free + capped AI key, all under `rg-codeintel-demo`, then deleted |

Cost and teardown rules: [deployment/cost-policy.md](./deployment/cost-policy.md).

## Key API groups (target)

```http
GET  /health
GET  /ready

POST /api/v1/repositories/import
GET  /api/v1/jobs/{job_id}
GET  /api/v1/repositories/{id}/jobs
POST /api/v1/jobs/{job_id}/retry

GET  /api/v1/repositories/{id}/graph/modules
GET  /api/v1/repositories/{id}/graph/packages
GET  /api/v1/repositories/{id}/graph/directories
GET  /api/v1/symbols/{id}/callers
GET  /api/v1/symbols/{id}/callees
GET  /api/v1/symbols/{id}/implementations
```

Search and Ask endpoints are added with hybrid retrieval and citation payloads.

## Design principles

1. Local-first and reconstructible
2. Honest deep vs generic contracts in every layer
3. Durable async indexing over fragile sync imports
4. Citations required for AI claims
5. Cost ceiling enforced by architecture (no Redis/K8s/paid Postgres for demo)
