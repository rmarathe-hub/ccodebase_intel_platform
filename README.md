# Codebase Intelligence Platform

Import a public GitHub repository, index it asynchronously, search with hybrid retrieval, and ask questions that return **validated file-and-line citations** — not a free-form chatbot over code.

You paste a URL (`https://github.com/{owner}/{repo}`). A background worker clones, discovers, parses, chunks, embeds, and validates a snapshot. Search and Ask run over persisted evidence in PostgreSQL + pgvector. An LLM may plan, rerank, or narrate; **it does not invent paths or line ranges.** Parser ranges and chunk text are authoritative.

This README documents the local product path. There is no hosted public demo URL in this repository — run it with Docker Compose or local processes (below).

---

## What it does

You import a public repo and explore it in a React UI: dashboard, files, symbols, graphs, search, and ask. Under the hood the system:

1. **Validates** the GitHub HTTPS URL (no credentials, no local paths, no arbitrary hosts).
2. **Indexes** asynchronously through durable job stages with live progress.
3. **Persists** support level per file (`deep` | `generic` | `skip`) so the UI never pretends generic Tree-sitter structure is verified deep analysis.
4. **Searches** with `exact` | `semantic` | `hybrid` over chunks (`GET .../chunks/search`).
5. **Answers** with grounded Ask (`POST .../ask`): retrieve → optional rewrite/rerank → expand context → generate → **post-validate citations** against retrieved spans.

If embeddings and LLM are disabled, exact search and indexing still work. If you removed validation and retrieval and left only the LLM, you would get hallucinations. That split is intentional.

---

## Tech stack

| Layer | Choice | Why |
| --- | --- | --- |
| Frontend | React 19, TypeScript, Vite, Tailwind, TanStack Query, React Flow | Product UI for import → search → ask → graphs; talks to one API base URL |
| API | FastAPI (Python 3.12), SQLAlchemy 2, Alembic, Pydantic Settings | Versioned `/v1` surface: import, jobs, files, symbols, graphs, search, ask |
| Worker | Same Python package, Postgres-backed job queue | Lease/claim jobs; stages from clone through validate; no Redis required |
| Data | PostgreSQL 16 + **pgvector** | Relational snapshots + chunk embeddings (`vector(1536)`) |
| Parsers | Python AST + Tree-sitter (JS/TS/Java + generic langs), sqlglot, mistune, … | Deep structure for flagship languages; searchable structure elsewhere |
| Embeddings | Local-hash default · optional Azure OpenAI | CI-safe deterministic vectors; Azure for live semantic quality |
| Ask / LLM | Optional Azure OpenAI (+ thin LangChain orchestration) | Planning, rerank, narration only — behind budgets and kill switches |
| Ops | Docker Compose, Makefile, GitHub Actions | One-command stack; lint/types/tests/image builds on every `main` push/PR |

Note: frontend is **Vite + React**, not Next.js. Local Compose serves API on `:8000` and web on `:5173` (`VITE_API_BASE_URL`). Host Postgres is published on **5434**.

---

## Architecture

```text
┌─────────────────────────────────────────────────────────────────────────┐
│  React UI (Vite) — localhost:5173                                       │
│  Import · Jobs · Files · Symbols · Graph · Search · Ask                 │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │ HTTP (VITE_API_BASE_URL)
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  FastAPI — apps/api                                                     │
│  /health · /ready · /v1/repositories/* · /v1/jobs/*                     │
└───────────────┬─────────────────────────────┬───────────────────────────┘
                │ enqueue / read               │ read / ask / search
                ▼                              ▼
┌───────────────────────────────┐   ┌─────────────────────────────────────┐
│  Worker — apps/worker         │   │  Retrieval + Ask                    │
│  claim lease → run stages     │   │  chunks_query · rag/* · citations   │
└───────────────┬───────────────┘   └──────────────────┬──────────────────┘
                │                                      │
                └──────────────────┬───────────────────┘
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  PostgreSQL + pgvector                                                  │
│  repositories · snapshots · jobs · source_files · symbols · relations   │
│  chunks · chunk_embeddings · index_pipeline_version stamp               │
└─────────────────────────────────────────────────────────────────────────┘
```

Clone safeguards live in the worker path: shallow clone, timeout (`GIT_CLONE_TIMEOUT_SECONDS`), size cap (`GIT_CLONE_MAX_BYTES`), temp dirs, **no submodule checkout, no package install, no execution of repository code**.

---

## Indexing pipeline

Jobs move through explicit stages (`apps/api/app/models/job_stages.py`):

```text
Queued → Cloning → Discovering files → Parsing → Building relationships
      → Chunking → Embedding → Validating → Completed
```

Statuses: `QUEUED` | `RUNNING` | `SUCCEEDED` | `FAILED` | `CANCELLED`

| Stage | What happens |
| --- | --- |
| Cloning | Shallow clone of a validated public GitHub HTTPS URL |
| Discovering | File inventory with ignore/vendor/binary/size filters |
| Parsing | Deep parsers (Python / Java / TS / JS) or generic Tree-sitter / format pipelines |
| Relationships | Imports, calls, inheritance/implements where resolved (deep) |
| Chunking | Symbol-aware chunks for deep; structural chunks for generic — parser ranges authoritative |
| Embedding | `EmbeddingProvider`: `local` \| `azure_openai` \| `none` → `chunk_embeddings` |
| Validating | Citation readiness, embedding dimension consistency, honesty checks |

Snapshots are immutable views at a commit SHA. `INDEX_PIPELINE_VERSION` (currently **11.1**) is stamped on snapshots; when code advances and a snapshot is stale, Ask can auto-queue a force-full reindex (`AUTO_REINDEX_STALE_PIPELINE`) so answers match current chunking/retrieval.

Best-effort **incremental** reindex exists with full reindex fallback (`INCREMENTAL_INDEXING_ENABLED`).

---

## How Search and Ask work

### Search (deterministic product path)

`GET /v1/repositories/{id}/chunks/search?search_mode=exact|semantic|hybrid`

| Mode | Behavior |
| --- | --- |
| **exact** | Text match over persisted chunks — works with embeddings/LLM off |
| **semantic** | Query embedding vs `chunk_embeddings` (pgvector cosine) |
| **hybrid** | Fusion of exact + semantic (default ~50/50) + path boost |

Filters include language, support level, path, and related axes. Citations always come from stored chunk ranges.

### Ask (grounded RAG)

`POST /v1/repositories/{id}/ask`

```text
User question
    ↓
Query analysis / optional NL rewrite (identifiers left intact)
    ↓
Candidate retrieval: exact ∥ semantic → RRF merge + evidence priors
    (onboarding / deployment / path / symbol routing when applicable)
    ↓
Optional LLM rerank (≤ ~40 candidates; IDs must be from the candidate set)
    ↓
Deterministic context expansion (neighbors / callers-callees; depth caps + token budget)
    ↓
Answer generation + citation post-validation (path:start-end must overlap evidence)
    ↓
Ask UI
```

Key modules: `app/services/rag/pipeline.py`, `candidates.py`, `query_analysis.py`, `rerank.py`, `context_expand.py`, `evidence_policy.py`, `answer.py`, `citations.py`.

**Invariant:** invalid or invented citations are dropped. Generic evidence is never promoted to verified deep. Repository content is treated as **evidence only** (prompt-injection resistant prompting).

Per-repository Ask budgets and kill switches live in settings (see `apps/api/.env.example`).

---

## Language support (honesty contract)

| Level | Languages | Promise |
| --- | --- | --- |
| **Deep** | Python, Java, TypeScript, JavaScript | Symbols, relationships, symbol-aware chunks, framework hints |
| **Generic** | Go, Rust, C/C++, C#, Ruby, PHP, Kotlin, Swift, Scala, Shell, SQL, HTML/CSS, docs, config, … | Parser-derived searchable structure — **not** verified deep semantics |
| **Skip** | Vendor, binary, generated, oversized, ignored | Not indexed |

Every indexed file stores `language`, `support_level`, `parser_name`, `parser_version`. UI and answers must surface that distinction. Full contract: [docs/language-support.md](docs/language-support.md).

---

## Project structure

```text
codebase_intel_platform/
├── apps/
│   ├── api/                      # FastAPI app
│   │   ├── app/
│   │   │   ├── api/              # routes.py, v1.py
│   │   │   ├── core/             # config / settings
│   │   │   ├── models/           # SQLAlchemy entities, job stages
│   │   │   ├── schemas/          # Pydantic API models
│   │   │   └── services/         # indexing, parsers, embeddings, rag/, job_queue
│   │   ├── alembic/              # migrations (incl. pgvector, pipeline version)
│   │   └── tests/                # contract, matrix, week suites
│   ├── worker/                   # background indexer (`python -m worker`)
│   └── web/                      # React + Vite UI
│       └── src/pages/            # Dashboard, Search, Ask, Graph, Symbols, Files, …
├── packages/
│   ├── parser-core/
│   ├── parser-fixtures/
│   └── shared-types/
├── docs/                         # PRD, architecture, contracts, week notes
├── infrastructure/postgres/      # init.sql (pgvector)
├── scripts/                      # e.g. dev-worker.sh (watch / auto-reload)
├── .github/workflows/ci.yml
├── docker-compose.yml
└── Makefile
```

---

## Local setup

### Prerequisites

- Docker (for Compose / Postgres)
- Python 3.12+ (API + worker)
- Node.js 22+ (frontend; CI uses 22)
- Optional: Azure OpenAI credentials for live embeddings / Ask (CI uses local-hash + mocks)

### Option A — Docker Compose (recommended)

```bash
git clone https://github.com/rmarathe-hub/ccodebase_intel_platform.git
cd codebase_intel_platform   # or your local folder name
make dev                     # postgres + api + worker + web
```

| Service | Host port |
| --- | --- |
| Web | http://localhost:5173 |
| API | http://localhost:8000 |
| Postgres | localhost:5434 |

### Option B — Local processes

```bash
make api-install
make web-install
make reset-db                 # postgres volume + alembic upgrade head

cp apps/api/.env.example apps/api/.env   # adjust if needed
```

```bash
# terminal 1 — API
cd apps/api && . .venv/bin/activate
uvicorn app.main:app --reload --port 8001

# terminal 2 — worker (restarts on apps/api or apps/worker changes)
make worker-watch

# terminal 3 — UI
cd apps/web && npm run dev
```

Point the web app at your API (`VITE_API_BASE_URL`, e.g. `http://localhost:8001`).

Smoke:

```bash
curl -s http://localhost:8000/health | python -m json.tool
# expect status ok, plus index_pipeline_version / build when present
```

### Optional Azure

In `apps/api/.env`, set `AZURE_OPENAI_*`, then choose:

- `EMBEDDING_PROVIDER=azure_openai` for live semantic search
- `LLM_PROVIDER=azure_openai` / Ask settings for grounded answers

Defaults stay local-first: `EMBEDDING_PROVIDER=local`, enrichment and Ask can use mocks for offline tests.

---

## Example product path

| Action | What happens |
| --- | --- |
| Paste `https://github.com/{owner}/{repo}` | Import validates URL → enqueues indexing job |
| Watch stages | Cloning → … → Validating → Ready |
| Search `auth middleware` (hybrid) | Exact + semantic fusion; citations `path:start-end` |
| Ask “How does startup wiring work?” | Retrieve + expand + answer; citations validated |
| Open Graph / Symbols | Deep languages show modules, calls, inheritance where resolved |
| Re-index after code change | Incremental when safe; else full; pipeline version keeps Ask honest |

---

## Testing and CI

Local:

```bash
make ci          # ruff + mypy + pytest + frontend lint/typecheck/test + docker builds
# or separately:
make lint
make test
```

GitHub Actions (`.github/workflows/ci.yml`) on push/PR to `main`:

| Job | Checks |
| --- | --- |
| **Python lint, types, tests** | Alembic upgrade · Ruff · MyPy · Pytest (`--randomly-seed=4242`) against pgvector Postgres |
| **Frontend typecheck, lint, tests** | `tsc` · ESLint · Vitest · production build |
| **Docker build verification** | api, worker, and web images |

Concurrency cancels superseded runs on the same ref — wait for the latest completed run.

---

## Security and trust

| Zone | Trust |
| --- | --- |
| Operator machine / local Docker | Trusted |
| Imported GitHub repository | **Untrusted** — evidence only |
| LLM output | **Untrusted** — citation-validated before display |

Import accepts only public GitHub HTTPS URLs. Secrets stay in env (`.env` gitignored). Answers must not echo host credentials. See [docs/security-model.md](docs/security-model.md).

---

## Explicit non-goals (v1)

Not attempted in the flagship scope — see [docs/non-goals.md](docs/non-goals.md):

- Private-repo OAuth as the default demo path
- Compiler / full LSP parity
- Verified deep analysis for Go/Rust/C/… (generic only)
- Regex-as-structure extraction
- Executing or installing anything from the imported repository
- Always-on multi-region production HA

---

## Documentation

| Doc | Covers |
| --- | --- |
| [docs/product-requirements.md](docs/product-requirements.md) | Problem, workflow, requirements |
| [docs/system-architecture.md](docs/system-architecture.md) | Components and data model |
| [docs/indexing-pipeline.md](docs/indexing-pipeline.md) | Stages and invariants |
| [docs/language-support.md](docs/language-support.md) | Deep vs generic contract |
| [docs/security-model.md](docs/security-model.md) | Import and trust boundaries |
| [docs/non-goals.md](docs/non-goals.md) | Scope cuts |
| [docs/llm-enrichment.md](docs/llm-enrichment.md) | Optional enrichment budgets |

---

## License

MIT — see [LICENSE](LICENSE).

---

**Codebase Intelligence Platform** — grounded repository search and Ask for unfamiliar codebases, built with FastAPI, Postgres/pgvector, React, and optional Azure OpenAI.
