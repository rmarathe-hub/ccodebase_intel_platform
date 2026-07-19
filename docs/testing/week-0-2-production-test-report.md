# Week 0–2 Production Test Report

**Date:** 2026-07-19  
**Repository:** `/Users/rohitmarathe/codebase_intel_platform`  
**Remote:** https://github.com/rmarathe-hub/ccodebase_intel_platform  
**Fixture:** https://github.com/rmarathe-hub/retail-retention-revenue-intel  
**Git policy:** No `git add` / `commit` / `push` performed by this workstream.

## 1. Repository areas inspected

| Area | Path / notes |
| --- | --- |
| API | `apps/api/app` (FastAPI, SQLAlchemy, Alembic, services) |
| Worker | `apps/worker` (clone → snapshot → SUCCEEDED; no parse yet) |
| Web | `apps/web` (Vite/React; Jobs + Dashboard wired) |
| Shared | `packages/{parser-core,parser-fixtures,shared-types}` (stubs) |
| Docs | Week 0–2 product/deployment/language docs |
| Infra | `docker-compose.yml` (Postgres/pgvector on host `5434`), Dockerfiles, CI |
| Scripts | `Makefile`, new `scripts/testing/*` |

## 2. Implemented features discovered (Week 0–2)

- Week 0 cost/shutdown/language-support policy docs
- Health / ready endpoints
- GitHub HTTPS URL validation (security-focused)
- Repository import + idempotent active-job reuse
- Job queue (`FOR UPDATE SKIP LOCKED`, lease, heartbeat, retry, recovery)
- Secure shallow clone (depth 1, no submodules, size/timeout, cleanup)
- Snapshot upsert + file count excluding `.git`
- Job stage labels/progress for UI pipeline
- Jobs UI with polling/retry (frontend)
- Language honesty constants (`app/core/language_contract.py`) — classification routing itself is Week 3+

**Not implemented (deferred):** file discovery pipeline, deep parsers, search/retrieval, hybrid AI answers, Azure demo.

## 3. Test architecture

Layers under `apps/api/tests/` and `apps/web/src/**/*.test.*`:

- Unit: URL matrix, clone mocks, stages, config, language contract, classification matrix, security boundaries, policy docs
- Integration/DB: models, constraints, migrations smoke, job queue, import service, concurrency claim race
- API contract: OpenAPI paths, import/jobs matrices, error safety
- Property-based: Hypothesis on URL round-trips / random strings / extensions
- Performance smoke: `@pytest.mark.slow`
- Frontend: JobProgress + jobs helpers (Vitest)
- Mutation: mutmut configured on `app` with focused test selection

## 4. Files created or modified

### Created (tests / docs / scripts)

- `apps/api/app/core/language_contract.py` (product constant module for honesty contract)
- Many new `apps/api/tests/test_*.py` (see test matrix)
- `apps/web/src/lib/jobs.test.ts`
- `apps/web/src/components/JobProgress.states.test.tsx`
- `scripts/testing/*.sh` + `scripts/testing/README.md`
- `docs/testing/week-0-2-production-test-report.md` (this file)
- `docs/testing/test-matrix.md`
- `docs/testing/known-gaps.md`

### Modified

- `apps/api/pyproject.toml` (dev deps, coverage, pytest markers, mutmut)
- `apps/api/tests/conftest.py` (xdist grouping hints)
- `apps/api/tests/test_snapshots.py` (macOS `.git` cleanup chmod)
- `.gitignore` (`coverage.xml`, `mutants/`)

## 5. Exact commands executed (representative)

```bash
# Baseline / full serial (recommended)
cd apps/api && .venv/bin/python -m pytest -q --randomly-seed=4242
cd apps/api && .venv/bin/python -m pytest -q --randomly-seed=9001

# Coverage (branch)
cd apps/api && .venv/bin/python -m pytest -q --cov=app --cov-branch --cov-report=term-missing

# Lint / types
cd apps/api && .venv/bin/ruff check . && .venv/bin/mypy app

# Frontend
cd apps/web && npm test && npm run typecheck && npm run lint

# Scripts
./scripts/testing/run-fast-unit.sh
./scripts/testing/run-integration.sh
./scripts/testing/run-coverage.sh
./scripts/testing/run-full.sh
./scripts/testing/run-slow.sh
./scripts/testing/run-frontend.sh
./scripts/testing/run-mutation.sh
```

**Environment assumptions:** local Postgres via Compose on `localhost:5434`, `apps/api/.venv`, `apps/web/node_modules`. No Azure credentials required.

## 6. Results (final clean serial runs)

| Suite | Collected / result | Runtime | Notes |
| --- | --- | --- | --- |
| API pytest seed 4242 | **370 passed**, 0 failed, 0 skipped, 0 xfailed | ~2.8s | 1 Starlette/httpx deprecation warning |
| API pytest seed 9001 | **370 passed** | ~2.6s | Order-independent |
| API coverage | **370 passed** | ~2.6s | See §7 |
| Web Vitest | **12 passed** (4 files) | ~1.0s | |
| Ruff | All checks passed | — | |
| mypy (`app`) | Success, 25 source files | — | |
| Web typecheck / lint | Passed | — | |
| xdist `-n auto` without careful grouping | Flaky on shared DB | — | **Do not use for CI**; scripts default to serial |

**Skipped / xfailed:** 0 in the final serial full suite (Postgres was available).

## 7. Coverage

Combined pytest-cov with `--cov-branch` (final run):

| Metric | Value |
| --- | --- |
| Line+branch combined Cover | **96%** |
| Statements | 615 |
| Missed statements | 27 |
| Branches | 92 |
| Partial branches | 4 |

### By module (highlights)

| Module | Cover | Notes |
| --- | --- | --- |
| `language_contract`, `snapshots`, `jobs`, `job_queue`, `import_repository`, entities/schemas | 100% or ≥96% | Core Week 2 |
| `github_url` | 98% | Line 119 hard to hit (empty part after split) |
| `git_clone` | 80% | Real subprocess/timeout/git-missing paths mocked |
| `db/deps.py` | 33% | Overridden in TestClient; production path lightly hit |
| `api/v1.py` | 96% | Lines 33–34: redundant `GitHubURLValidationError` catch (Pydantic validates first) |

**Justified exclusions / lower coverage:** `app/db/deps.py` dependency override in tests; subprocess OS error paths in `git_clone._run_git`; worker process itself not unit-tested in-process (clone/snapshot covered via API services).

## 8. Mutation testing

Configured via `[tool.mutmut]` in `apps/api/pyproject.toml`.

| Stat | Value |
| --- | --- |
| Mutants generated | 734 (entire `app` tree; mutmut 3 requires package copy) |
| Killed 🎉 | 146 |
| Survived 🙁 | 86 |
| No covering tests 🫥 | 502 (expected: focused test selection excludes most modules) |
| Score among tested mutants | **146 / (146+86) ≈ 63%** |

Interpretation: URL/language tests kill meaningful mutants in those modules; survivors and “no tests” rows outside that focus are expected. Prefer future runs with narrower `source_paths` once mutmut packaging supports partial trees without breaking imports.

## 9. Defects

| Item | Status |
| --- | --- |
| Pytest temp `.git` PermissionError on macOS | **Fixed in test** via chmod before teardown |
| ORM `session.delete(repo)` nulling FK vs DB CASCADE | Documented; tests use SQL `DELETE` to exercise cascade |
| xdist races on shared `indexing_jobs` | Documented; serial suite is the contract |
| Product bugs requiring production fixes | **None required** for Week 0–2 contracts |

## 10. Security findings (test-backed)

- Embedded credentials, SSH/file/local paths, injection-like URL payloads rejected
- Clone args include `--no-recurse-submodules` and `--depth 1`
- Oversized clone cleaned up; public errors omit DB URL / tracebacks
- No Azure SDKs / Redis / K8s in Compose or API deps
- Policy docs and ICS calendar present

## 11. Performance observations

Slow suite (`test_performance_smoke.py`) classifies thousands of extensions, counts 400 files, parses hundreds of URLs under generous thresholds (&lt;2–5s). Marked `@pytest.mark.slow`.

## 12. Documentation ↔ code mismatches

- Stage labels after `cloning` are UI placeholders until Week 3+; worker currently jumps to `SUCCEEDED` after snapshot
- Pydantic request validator turns GitHub URL errors into **422**; route-level 400 catch is largely unreachable
- Language deep/generic lists now mirrored in `language_contract.py` (honest constants ahead of discovery)

## 13. Deferred functionality (do not claim covered)

See `docs/testing/known-gaps.md`.

## 14. Reproduce all results

1. `docker compose up -d postgres` (port **5434**)
2. `make api-install && make web-install && make migrate`
3. `./scripts/testing/run-coverage.sh`
4. `./scripts/testing/run-full.sh` (twice with different `--randomly-seed` if desired)
5. Optional: `./scripts/testing/run-mutation.sh`
