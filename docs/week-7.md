# Week 7 — Generic chunking + optional LLM enrichment

## Status

| Day | Scope | Status |
| --- | --- | --- |
| 1 | Chunk schema + deep symbol-aware chunks + generic Tree-sitter source chunks | Not started |
| 2 | Multi-lang generic parsers + optional validated LLM classification | Not started |
| 3 | Format-native configuration chunking | Not started |
| 4 | Markdown / document AST chunking | Not started |
| 5 | Deterministic (+ optional LLM) repository summaries | Not started |
| 6 | Exact PostgreSQL chunk search (LLM-independent) | Not started |
| 7 | Polyglot fixture matrix + worker E2E | Not started |

## Architecture (locked)

Parser-authority + validated LLM enrichment. See [language-support.md](./language-support.md)
and [indexing-pipeline.md](./indexing-pipeline.md).

### Corrections vs earlier Week 7 sketch

- No regex structural extraction
- Python / Java / JS / TS chunk from **existing deep symbols** only
- Generic languages: Tree-sitter / format parsers → `generic_structure` / `heuristic_section`
- Paid LLM enrichment opt-in, CI-off, budgeted, cached; exact search never depends on it
- First cut: Go, Rust, C/C++, C#, Ruby, Shell, SQL + JSON/YAML/TOML/XML/Dockerfile/Markdown
- Remaining generic languages share the same interface later

## Planned artifacts

- `chunks` migration + model (provenance fields)
- `apps/api/app/services/chunking/`
- `apps/api/app/services/llm/` (`LLMProvider`, enrich, validate, budget, cache)
- Exact search API + worker Chunking stage
- `apps/api/tests/fixtures/generic_polyglot/`

## Honesty

- Tree-sitter on generic languages ≠ verified deep
- LLM may not alter ranges or create verified symbols
- Deterministic indexing works with enrichment disabled

## Git policy

Agent does not `git add` / `commit` / `push`. You review and commit manually.
