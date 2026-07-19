# Week 3 — File discovery & classification

## Status

| Day | Scope | Status |
| --- | --- | --- |
| 1 | `source_files` schema, migration, language/discovery contracts, policy doc | Done |
| 2 | Pure discovery walker + unit tests | Done |
| 3 | Worker wiring + persist `source_files` | Done |
| 4 | Files API + UI | Done |
| 5 | Retail fixture golden tests | Done |
| 6 | Perf smoke + path hardening | Done |
| 7 | Python AST → `symbols` + Symbols API/UI | Done (local) |

## Day 7 artifacts

- `apps/api/alembic/versions/0003_symbols.py` — `symbols` table
- `apps/api/app/services/python_ast_parser.py` — stdlib `ast` extractor (`python-ast`)
- `apps/api/app/services/symbols.py` — persist + stamp `parser_name` / `parser_version`
- `apps/api/app/api/v1.py` — `GET /repositories/{id}/symbols`
- Worker: clone → discover → **PARSING** → persist symbols → SUCCEEDED
- `apps/web/src/pages/SymbolsPage.tsx` — browse verified Python symbols
- Tests: `test_python_ast_parser.py`, `test_symbols_persist.py`, `test_symbols_api.py`, `symbols.test.ts`

## Honesty note

Jobs mark **SUCCEEDED** after discovery **and** Python AST parsing. Still not done:
relationships, chunking, embeddings, or deep parsers for Java / TypeScript / JavaScript.
Syntax-error Python files stay without `parser_name` and contribute no symbols.

## Git policy

Agent does not `git add` / `commit` / `push`. You review and commit manually.
