# Week 0–4 Production Test Report

**Date:** 2026-07-19  
**Repository:** `/Users/rohitmarathe/codebase_intel_platform`  
**Remote:** https://github.com/rmarathe-hub/ccodebase_intel_platform  
**Fixture:** https://github.com/rmarathe-hub/retail-retention-revenue-intel  
**Git policy:** No `git add` / `commit` / `push` performed by this workstream.

This report supersedes Week 0–2 testing docs for **current capability**. Historical findings remain in [`week-0-2-production-test-report.md`](./week-0-2-production-test-report.md).

## 1. Architecture inspected

| Area | Notes |
| --- | --- |
| API | FastAPI routes in `apps/api/app/api/v1.py` + health/ready |
| Services | URL, import, job queue, clone, discovery, source_files, snapshots, Python AST/framework/imports/calls, query helpers |
| Worker | `apps/worker/worker/__main__.py`: clone → discover → parse+relationships → SUCCEEDED (no chunk/embed) |
| Web | Jobs, Files, Symbols, Graph wired; Search/Ask/Repo overview stubs |
| DB | Alembic head `0006_symbol_calls`; Postgres host port **5434** |
| CI | `.github/workflows/ci.yml` now runs Postgres service + alembic upgrade + pytest |

## 2. Completed features verified

- Week 0 cost/language/shutdown contracts
- GitHub HTTPS URL validation + import + job queue + secure shallow clone
- Discovery / classification / `source_files` / Files API+UI
- Retail offline golden (`retail_shape`) + gitignore exception for fixture `data/`
- Python AST symbols (rich metadata, QNames)
- Framework roles, import locality, call extraction + confidence
- Calls / callers / callees APIs; Symbols presets; Graph call-site table
- Worker end-to-end with mocked clone

## 3. Unimplemented (honestly not tested as complete)

Chunking, embeddings, Search API/UI, Ask/LLM/citations, Java/TS/JS deep parsers, generic heuristic sections, interactive graph diagram, auth, multi-tenant, private/non-GitHub imports, incremental indexing.

## 4. Baseline (before expansion)

| Check | Result |
| --- | --- |
| Collected | 456 |
| First full run (sandbox) | 454 passed, 2 failed (`PermissionError` writing `.git` under tmp — sandbox only) |
| Re-run of those 2 with full FS | **passed** |
| Ruff / MyPy | pass |
| Vitest | 16 passed / 7 files |
| Compose config | valid |
| Alembic head | `0006_symbol_calls` |

## 5. Final executed results (this session)

### API pytest

| Run | Seed | Result | Runtime |
| --- | --- | --- | --- |
| Serial #1 | 4242 | **591 passed** | ~5.9s |
| Serial #2 | 9001 | **591 passed** | ~5.1s |
| Coverage | 4242 | **591 passed**, **90% line/branch combined report** | ~5.7s |

Warnings: Starlette TestClient / `HTTP_422_UNPROCESSABLE_ENTITY` deprecation (dependency).

### Coverage (high level)

- **Overall:** ~90% statements (branch-aware report)
- Strong (≥94%): `github_url`, much of AST parser, many query/job modules fully covered
- Below 90% (justified focus next): `python_calls.py` (~72%), `discovery.py` (~87%), `git_clone.py` (~80%), `db/deps.py` (TestClient override)

HTML report: `apps/api/htmlcov/` (local artifact; gitignored via coverage patterns as applicable).

### Frontend

| Check | Result |
| --- | --- |
| Vitest | **26 passed / 10 files** |
| Typecheck | pass |
| ESLint | pass |
| Production build | pass |

### Static / infra

| Check | Result |
| --- | --- |
| Ruff | pass |
| MyPy (`app`) | pass |
| Docker Compose config | pass |
| Alembic heads | `0006_symbol_calls` |
| Live schema columns (0002–0006) | asserted |

### Mutation testing

Configured expanded mutmut selection (URL + language + framework + calls matrices) in `pyproject.toml`. **Not executed in this session** (tool run blocked by environment policy). Use `./scripts/testing/run-mutation.sh` locally and paste results into a follow-up.

## 6. Files created / modified

### Created (tests)

- `apps/api/tests/test_python_calls_matrix.py`
- `apps/api/tests/test_python_framework_matrix.py`
- `apps/api/tests/test_python_ast_matrix.py`
- `apps/api/tests/test_api_filters_week04.py`
- `apps/api/tests/test_worker_pipeline.py`
- `apps/api/tests/test_discovery_extended.py`
- `apps/api/tests/test_migrations_week04.py`
- `apps/api/tests/test_doc_contracts_week04.py`
- `apps/api/tests/test_github_url_security_extended.py`
- `apps/web/src/lib/api.test.ts`
- `apps/web/src/pages/stubs.test.tsx`
- `apps/web/src/pages/GraphPage.test.tsx`

### Created (scripts/docs)

- `scripts/testing/run-parser.sh`
- `scripts/testing/run-security.sh`
- `scripts/testing/run-worker-integration.sh`
- `scripts/testing/run-frontend-full.sh`
- `docs/testing/week-0-4-production-test-report.md` (this file)
- `docs/testing/security-test-report.md`
- `docs/testing/performance-smoke-report.md`
- `docs/testing/reproduction-guide.md`
- Updates: `test-matrix.md`, `known-gaps.md`, `scripts/testing/README.md`, `run-integration.sh`

### Modified (infra/test harness)

- `.github/workflows/ci.yml` — Postgres service on **5434**, `alembic upgrade head`, seeded pytest
- `apps/api/tests/conftest.py` — xdist postgres group hints
- `apps/api/pyproject.toml` — expanded mutmut selection

### Production bug fixes

**None required** for green suite. One **decision-needed** heuristic documented (bare `class Base` → `sqlalchemy_model`).

## 7. Defects / decision-needed

| Item | Status |
| --- | --- |
| Bare `Base` / `Model` leaf → SQLAlchemy role | **Decision-needed** — current heuristic; documented in framework matrix test |
| Trailing newline on GitHub URL accepted after `strip()` | Documented behavior (not a defect) |
| CI previously skipped all Postgres tests | **Fixed** in workflow (Postgres service) |
| `python_calls` branch coverage ~72% | Remaining gap; ambiguous path now tested |

## 8. Flakiness

- Two full serial runs with different randomly seeds: both **591 passed**
- Worker tests quarantine leftover QUEUED/RUNNING jobs on shared developer DB
- Prefer serial pytest on shared Postgres; xdist uses `loadgroup=postgres`

## 9. Reproduction

See [`reproduction-guide.md`](./reproduction-guide.md).
