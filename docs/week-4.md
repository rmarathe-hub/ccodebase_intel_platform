# Week 4 — Python deep support

## Status

| Day | Scope | Status |
| --- | --- | --- |
| 1 | Richer Python AST (decorators, params, returns, docstrings, async, nested classes) | Done |
| 2 | Qualified names (`module.Class.method`, `__init__.py` packages) | Done |
| 3 | Framework metadata (FastAPI/Flask/Django/SQLAlchemy/Celery/Pydantic) | Done |
| 4 | Import resolution (absolute/relative, local vs external) | Done |
| 5 | Call extraction + confidence | Done |
| 6 | Python fixtures matrix | Done |
| 7 | UI verification (routes/models/callers/callees) | Done (local) |

## Day 7 artifacts

- `GET /repositories/{id}/symbols/{symbol_id}/callers`
- `GET /repositories/{id}/symbols/{symbol_id}/callees`
- Symbols page presets: All / Functions / Classes / Routes / Models
- Click a symbol → callers + callees panels
- Graph page: call-site list with confidence filters

## Honesty

- Call resolution remains heuristic (`resolved` / `ambiguous` / `unresolved`).
- Graph is a verification table, not a full interactive diagram yet.

## Git policy

Agent does not `git add` / `commit` / `push`. You review and commit manually.
