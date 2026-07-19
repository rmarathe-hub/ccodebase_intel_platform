# Week 3 — File discovery & classification

## Status

| Day | Scope | Status |
| --- | --- | --- |
| 1 | `source_files` schema, migration, language/discovery contracts, policy doc | Done (local) |
| 2 | Pure discovery walker + unit tests | Done (local) |
| 3 | Worker wiring + persist `source_files` | Not started |
| 4 | Files API + UI | Not started |
| 5 | Retail fixture golden tests | Not started |

## Day 1–2 artifacts

- `apps/api/app/core/language_contract.py` — DEEP/GENERIC/SKIP, ignore dirs, secrets, helpers
- `apps/api/app/models/entities.py` — `SourceFile`
- `apps/api/alembic/versions/0002_source_files.py`
- `apps/api/app/services/discovery.py` — `discover_repository` / `classify_file`
- `docs/discovery-policy.md`
- `apps/api/tests/test_discovery.py`

## Git policy

Agent does not `git add` / `commit` / `push`. You review and commit manually.
