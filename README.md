# Codebase Intelligence Platform

Import a public GitHub repository. Index it as structured evidence. Search with hybrid retrieval. Ask questions that cite real `path:start–end` ranges — or refuse to invent them.

This is a **local-first** full-stack system for codebase understanding: async workers, language-aware parsing, Postgres + pgvector retrieval, and a React product surface. The LLM is optional orchestration. **Persisted chunks and parser ranges are the source of truth.**

---

## Thesis

| Approach | Failure mode |
| --- | --- |
| Keyword search | Misses intent and structure |
| Unconstrained chat over code | Hallucinates paths, symbols, and line numbers |
| **This platform** | Retrieve first, answer second — citations validated against evidence |

**Index** → clone, discover, parse, chunk, embed, validate  
**Search** → exact · semantic · hybrid, with filters and citations  
**Ask** → optional LLM answers bound to retrieved evidence only  

The model may rank and phrase. It may not invent sources.

---

## Product surface

| | |
| --- | --- |
| **Import** | Public `https://github.com/{owner}/{repo}` → live pipeline stages → Ready |
| **Search** | Exact / semantic / hybrid over chunks; language & support-level filters |
| **Ask** | Grounded Q&A; citations post-validated before display |
| **Symbols / Graph** | Deep extraction for Python, Java, TypeScript, JavaScript |
| **Honesty** | Generic languages remain searchable — never promoted to verified deep |

**Deep:** Python · Java · TypeScript · JavaScript  
**Generic (searchable structure, not verified deep):** Go, Rust, C/C++, Ruby, SQL, Shell, docs, config, and more — [language contract](docs/language-support.md)

---

## System design

```text
React + TypeScript (Vite)
            │
            ▼
         FastAPI
      ┌─────┴──────┐
      ▼            ▼
 PostgreSQL    Background worker
 + pgvector    (durable job queue)
      │            │
      └─────┬──────┘
            ▼
   Snapshot → parse → chunk → embed → validate
            │
            ▼
   Hybrid retrieval → citation-validated Ask
```

| Layer | Choice |
| --- | --- |
| API | Python 3.12+ · FastAPI · SQLAlchemy · Alembic |
| Worker | Staged indexing jobs with progress & failure UX |
| Store | PostgreSQL + **pgvector** |
| Retrieval | Exact + semantic fusion · optional LLM rerank |
| Providers | Local defaults ($0) · optional Azure OpenAI |
| UI | React · TypeScript · Vite |
| Delivery | Docker Compose · Makefile · GitHub Actions |

Architecture & pipeline: [system-architecture.md](docs/system-architecture.md) · [indexing-pipeline.md](docs/indexing-pipeline.md)

---

## Monorepo

```text
apps/api        HTTP API, migrations, indexing & RAG services
apps/worker     Job runner — clone → index → embed → validate
apps/web        Product UI — import, search, ask, symbols, graph
packages/       Shared parsers & fixtures
docs/           PRD, contracts, security, architecture
scripts/        Dev ergonomics (worker watch, etc.)
```

---

## Run it

**Compose (fastest):**

```bash
make dev    # postgres + api + worker + web
```

Postgres on host **5434** (avoids clashing with local 5432).

**Local processes:**

```bash
make api-install && make web-install && make reset-db

# API
cd apps/api && . .venv/bin/activate && uvicorn app.main:app --reload --port 8001

# Worker (reloads on code change)
make worker-watch

# UI
cd apps/web && npm run dev
```

Open the Vite app → paste a public GitHub HTTPS URL → wait for Ready → Search / Ask.

Cloud embeddings and LLM are optional (`apps/api/.env.example`). Exact search and local embeddings run with no paid credentials.

---

## Engineering signal

What this repo is meant to demonstrate:

- **Durable async indexing** — clone → discover → parse → relationships → chunk → embed → validate → complete, with re-index and failure paths
- **Support-level contract** — deep vs generic persisted end-to-end; no regex cosplay as structure
- **Retrieval that degrades honestly** — Search works when embeddings/LLM are off; Ask stays evidence-bound when they are on
- **Grounded Ask** — merge candidates → optional rewrite/rerank → expand context → generate → **validate citations**
- **Index freshness** — pipeline version stamped on snapshots; stale indexes force full reindex
- **Cost & trust boundaries** — local-first defaults; paid SDKs isolated; import never executes repo code
- **CI as gate** — Ruff · MyPy · Pytest · TypeScript · ESLint · Vitest · Docker image builds on `main`

```bash
make ci
```

---

## Documentation

| | |
| --- | --- |
| [product-requirements.md](docs/product-requirements.md) | Problem, workflow, requirements |
| [system-architecture.md](docs/system-architecture.md) | Components & data model |
| [language-support.md](docs/language-support.md) | Deep vs generic contract |
| [indexing-pipeline.md](docs/indexing-pipeline.md) | Stages & invariants |
| [security-model.md](docs/security-model.md) | Import & trust boundaries |
| [non-goals.md](docs/non-goals.md) | Explicit scope cuts |

---

## License

See [LICENSE](LICENSE).
