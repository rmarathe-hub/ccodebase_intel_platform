# Week 4 — Python deep support

## Status

| Day | Scope | Status |
| --- | --- | --- |
| 1 | Richer Python AST (decorators, params, returns, docstrings, async, nested classes) | Done (local) |
| 2 | Qualified names (`module.Class.method`, `__init__.py` packages) | Done (local) |
| 3 | Framework metadata (FastAPI/Flask/… patterns) | Not started |
| 4 | Import resolution | Not started |
| 5 | Call extraction + confidence | Not started |
| 6 | Python fixtures matrix | Not started |
| 7 | UI verification (routes/models/callers/callees) | Not started |

## Day 1–2 artifacts

- `apps/api/app/services/python_ast_parser.py` — Day 1–2 extractor + `module_qualified_name` / `qualify`
- `apps/api/alembic/versions/0004_symbol_metadata.py` — docstring / decorators / parameters / return / is_async
- Persist + API + Symbols UI surface the new fields
- `parser_version` stamped as `4.1-{py}-stdlib`

## Honesty

- Metadata is structural from stdlib `ast` only (no execution).
- Framework detection is still Day 3+ (decorators are stored as strings, not classified as routes/models yet).
- Import/call graphs are not started.

## Git policy

Agent does not `git add` / `commit` / `push`. You review and commit manually.
