# Codebase Intelligence Platform

**Import a public GitHub repo. Index it. Search it. Ask grounded questions with file-and-line citations.**

A local-first monorepo that turns unfamiliar codebases into searchable structure and citation-validated answers — without treating an LLM as the source of truth.

Built as a full-stack systems project: async indexing workers, language-aware parsers, hybrid retrieval over Postgres + pgvector, and a React product UI with an honest support model (deep vs generic languages).

---

## Why this exists

Keyword search misses intent. Chatbots invent paths and line numbers. This platform sits in between:

1. **Index** — clone, discover, parse, chunk, embed, validate (async job pipeline)
2. **Search** — exact, semantic, and hybrid retrieval with filters and citations
3. **Ask** — optional LLM answers that only cite evidence the retriever actually returned

Parser ranges and persisted chunks are authoritative. The model may rank and phrase; it may not invent sources.

---

## What you can do

| Surface | Capability |
| --- | --- |
| **Import** | Paste a public `https://github.com/{owner}/{repo}` URL → live stages → Ready |
| **Search** | Exact / semantic / hybrid over chunks; language & support-level filters |
| **Ask** | Grounded Q&A with post-validated `path:start-end` citations |
| **Symbols & graph** | Deep symbols/relationships for Python, Java, TypeScript, JavaScript |
| **Honesty** | Generic languages stay searchable but never claimed as verified deep |

**Deep support:** Python, Java, TypeScript, JavaScript  
**Generic (structural/searchable, not verified deep):** Go, Rust, C/C++, Ruby, SQL, Shell, docs, config, and more — see [docs/language-support.md](docs/language-support.md)

---

## Architecture at a glance

```text
React + TypeScript (Vite)
            │
            ▼
         FastAPI
      ┌─────┴──────┐
      ▼            ▼
 PostgreSQL    Background worker
 + pgvector    (Postgres job queue)
      │            │
      └─────┬──────┘
            ▼
   Snapshots → parse → chunks → embeddings → validate
            │
            ▼
   Hybrid retrieval → citation-validated Ask
```

| Layer | Stack |
| --- | --- |
| API | Python 3.12+, FastAPI, SQLAlchemy, Alembic |
| Worker | Same codebase; staged indexing jobs with progress |
| Data | PostgreSQL + **pgvector** |
| Retrieval | Exact + semantic + hybrid fusion; optional LLM rerank |
| LLM / embeddings | Local defaults ($0); optional Azure OpenAI |
| Web | React, TypeScript, Vite |
| Ops | Docker Compose, Makefile, GitHub Actions CI |

Details: [docs/system-architecture.md](docs/system-architecture.md) · [docs/indexing-pipeline.md](docs/indexing-pipeline.md)

---

## Repository layout

```text
apps/
  api/       FastAPI app, migrations, indexing & RAG services
  worker/    Background job runner (clone → index → embed → validate)
  web/       Product UI (import, search, ask, symbols, graph)
packages/    Shared parser packages & fixtures
docs/        PRD, architecture, language contract, weekly build notes
infrastructure/
scripts/     Dev helpers (e.g. worker watch / auto-reload)
```

---

## Quick start

### Option A — Docker Compose (recommended)

```bash
make dev          # postgres + api + worker + web
```

Postgres is published on host port **5434** (avoids clashing with a local 5432).

### Option B — Local processes

```bash
make api-install
make web-install
make reset-db                 # postgres + migrate

# terminal 1 — API
cd apps/api && . .venv/bin/activate && uvicorn app.main:app --reload --port 8001

# terminal 2 — worker (auto-restarts on code changes)
make worker-watch

# terminal 3 — UI
cd apps/web && npm run dev
```

Open the Vite URL (typically `http://localhost:5173`), paste a public GitHub HTTPS URL, wait for indexing, then use **Search** and **Ask**.

Optional Azure embeddings / LLM: copy `apps/api/.env.example` → `.env` and set provider keys. Exact search and local embeddings work without cloud credentials.

---

## Engineering highlights

- **Durable async indexing** — staged jobs (clone → discover → parse → relationships → chunk → embed → validate → complete) with failure UX and re-index
- **Language honesty contract** — deep vs generic support levels persisted and surfaced in API/UI; no regex “fake structure”
- **Hybrid retrieval** — exact + semantic fusion over chunk embeddings; Search stays usable when embeddings/LLM are off
- **Grounded Ask pipeline** — candidate merge → optional rewrite/rerank → context expansion → answer with citation validation
- **Index freshness** — pipeline version stamped on snapshots; stale indexes can force a full reindex so answers match current chunking/retrieval
- **Local-first cost model** — deterministic local embeddings by default; paid SDKs optional and isolated
- **CI as a product** — Ruff, MyPy, Pytest, TypeScript, ESLint, Vitest, and Docker image builds on every `main` push/PR

---

## Quality & CI

```bash
make ci           # lint + tests + local Docker image builds
```

GitHub Actions runs the same class of checks:

- **Python** — Ruff, MyPy, Pytest  
- **Frontend** — typecheck, ESLint, Vitest, production build  
- **Docker** — api / worker / web image builds  

Product and language contracts live under `docs/` (requirements, non-goals, security model, discovery policy).

---

## Docs map

| Doc | What it covers |
| --- | --- |
| [product-requirements.md](docs/product-requirements.md) | Problem, workflow, functional requirements |
| [system-architecture.md](docs/system-architecture.md) | Components and data model |
| [language-support.md](docs/language-support.md) | Deep vs generic contract |
| [indexing-pipeline.md](docs/indexing-pipeline.md) | Job stages and invariants |
| [security-model.md](docs/security-model.md) | Import/trust boundaries |
| [non-goals.md](docs/non-goals.md) | Explicit scope cuts |

---

## License

See [LICENSE](LICENSE).
