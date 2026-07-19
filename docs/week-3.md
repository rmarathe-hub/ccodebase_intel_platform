# Week 3 — File discovery & classification

## Status

| Day | Scope | Status |
| --- | --- | --- |
| 1 | `source_files` schema, migration, language/discovery contracts, policy doc | Done |
| 2 | Pure discovery walker + unit tests | Done |
| 3 | Worker wiring + persist `source_files` | Done (local) |
| 4 | Files API + UI | Done (local) |
| 5 | Retail fixture golden tests | Done (local) |
| 6 | Perf smoke + path hardening | Done (local) |

## Day 3–4 artifacts

- `apps/api/app/services/source_files.py` — replace rows for a snapshot
- `apps/api/app/services/files_query.py` — list repos / files
- `apps/api/app/schemas/files.py`
- `apps/api/app/api/v1.py` — `GET /repositories`, `GET /repositories/{id}/files`
- `apps/worker/worker/__main__.py` — clone → discover → persist → succeed
- `apps/web/src/pages/FilesPage.tsx` — browse with deep/generic/skip filters
- Tests: `test_source_files_persist.py`, `test_files_api.py`, `files.test.ts`

## Day 5–6 artifacts

- `apps/api/tests/fixtures/retail_retention_golden.json` — committed golden for the retail demo repo
- `apps/api/tests/fixtures/retail_shape/` + `retail_shape_golden.json` — always-offline mini tree
- `apps/api/tests/helpers/retail_fixture.py` — env / `.cache` / one-time shallow clone resolver
- `apps/api/tests/test_retail_discovery_golden.py` — golden + key-path policy checks
- `apps/api/tests/test_discovery_perf.py` — thousands-of-files smoke, ignore leak, normalize property

Fixture resolution order: `CODEINTEL_RETAIL_FIXTURE` → `.cache/retail-retention-revenue-intel` → one-time `git clone --depth 1`.

## Honesty note

Jobs mark **SUCCEEDED** after discovery. Later pipeline stages remain future work; the Jobs page copy states this explicitly. Day 6 does **not** ship Python AST → `symbols` (stretch deferred).

## Git policy

Agent does not `git add` / `commit` / `push`. You review and commit manually.
