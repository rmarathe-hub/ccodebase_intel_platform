# Week 4 — Python deep support

## Status

| Day | Scope | Status |
| --- | --- | --- |
| 1 | Richer Python AST (decorators, params, returns, docstrings, async, nested classes) | Done |
| 2 | Qualified names (`module.Class.method`, `__init__.py` packages) | Done |
| 3 | Framework metadata (FastAPI/Flask/Django/SQLAlchemy/Celery/Pydantic) | Done (local) |
| 4 | Import resolution (absolute/relative, local vs external) | Done (local) |
| 5 | Call extraction + confidence | Not started |
| 6 | Python fixtures matrix | Not started |
| 7 | UI verification (routes/models/callers/callees) | Not started |

## Day 3–4 artifacts

- `apps/api/app/services/python_framework.py` — heuristic role detection
- `apps/api/app/services/python_imports.py` — relative resolve + locality
- `apps/api/alembic/versions/0005_framework_imports.py`
- Symbols API filters: `framework_role`, `is_local_import`
- Symbols UI role filters + local-imports toggle
- `parser_version` stamped as `4.2-{py}-stdlib`

## Honesty

- Framework roles are **common-pattern** matches (decorators/bases), not full framework support.
- Import locality uses the snapshot’s known Python modules; unresolved third-party packages are labeled external.
- Call graphs are still Day 5+.

## Git policy

Agent does not `git add` / `commit` / `push`. You review and commit manually.
