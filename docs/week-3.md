# Week 3 — File discovery & classification

## Status

| Day | Scope | Status |
| --- | --- | --- |
| 1 | `source_files` schema, migration, language/discovery contracts, policy doc | Done |
| 2 | Pure discovery walker + unit tests | Done |
| 3 | Worker wiring + persist `source_files` | Done (local) |
| 4 | Files API + UI | Done (local) |
| 5 | Retail fixture golden tests | Not started |

## Day 3–4 artifacts

- `apps/api/app/services/source_files.py` — replace rows for a snapshot
- `apps/api/app/services/files_query.py` — list repos / files
- `apps/api/app/schemas/files.py`
- `apps/api/app/api/v1.py` — `GET /repositories`, `GET /repositories/{id}/files`
- `apps/worker/worker/__main__.py` — clone → discover → persist → succeed
- `apps/web/src/pages/FilesPage.tsx` — browse with deep/generic/skip filters
- Tests: `test_source_files_persist.py`, `test_files_api.py`, `files.test.ts`

## Honesty note

Jobs mark **SUCCEEDED** after discovery. Later pipeline stages remain future work; the Jobs page copy states this explicitly.

## Git policy

Agent does not `git add` / `commit` / `push`. You review and commit manually.
