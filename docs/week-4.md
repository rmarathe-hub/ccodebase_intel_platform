# Week 4 — Python deep support

## Status

| Day | Scope | Status |
| --- | --- | --- |
| 1 | Richer Python AST (decorators, params, returns, docstrings, async, nested classes) | Done |
| 2 | Qualified names (`module.Class.method`, `__init__.py` packages) | Done |
| 3 | Framework metadata (FastAPI/Flask/Django/SQLAlchemy/Celery/Pydantic) | Done |
| 4 | Import resolution (absolute/relative, local vs external) | Done |
| 5 | Call extraction + confidence | Done (local) |
| 6 | Python fixtures matrix | Done (local) |
| 7 | UI verification (routes/models/callers/callees) | Not started |

## Day 5–6 artifacts

- `apps/api/app/services/python_calls.py` — call extraction + heuristic resolution
- `apps/api/alembic/versions/0006_symbol_calls.py` — `symbol_calls` table
- Worker stage `building_relationships` persists call sites after parsing
- `GET /api/v1/repositories/{id}/calls` with confidence filter
- Offline fixture: `apps/api/tests/fixtures/python_deep/`
- `parser_version` stamped as `4.3-{py}-stdlib`

## Honesty

- Call resolution is name/import based (`resolved` / `ambiguous` / `unresolved`), not a type checker.
- Framework roles remain pattern-only.
- Callers/callees UI is Day 7.

## Git policy

Agent does not `git add` / `commit` / `push`. You review and commit manually.
