# Week 7 — Generic chunking + optional LLM enrichment

## Status

| Day | Scope | Status |
| --- | --- | --- |
| 1 | Chunk schema + deep symbol-aware chunks + generic Tree-sitter source chunks | Done |
| 2 | Multi-lang generic parsers + LangChain Azure enrichment (batched) | Done |
| 3 | Format-native configuration chunking | Done |
| 4 | Markdown / document AST chunking | Done |
| 5 | Deterministic + LLM-enhanced repository summaries | Done |
| 6 | Exact PostgreSQL chunk search (LLM-independent) | Done |
| 7 | Polyglot fixture matrix + worker E2E (full) | Done |

## Architecture (locked)

```text
Parser / AST (source of truth)
        ↓
Deterministic chunks + citations
        ↓
Priority batching + budget gate (first-party)
        ↓
LLMProvider → LangChain + Azure OpenAI (structured output)
        ↓
Validate against parser-derived evidence
        ↓
Persist enrichment + cache
```

See [language-support.md](./language-support.md), [indexing-pipeline.md](./indexing-pipeline.md),
and [llm-enrichment.md](./llm-enrichment.md).

### Days 1–2 shipped

- Migration `0008_chunks` + `llm_enrichment_cache`
- Deep symbol chunks: Python / Java / JS-TS (`extraction_method=deep_symbol`, `verified_deep=true`)
- Generic Tree-sitter: Go, Rust, C, C++, C#, Ruby, Shell
- SQL: SQLGlot tokenizer statement ranges
- Worker **Chunking** stage wired
- `AzureOpenAIProvider.enrich_batch` prefers **LangChain**; direct SDK only if LangChain unavailable (documented fallback)
- One enrichment call per logical batch; mock provider in tests; CI never requires paid APIs

### Days 3–4 shipped

- Config: JSON (brace-depth spans), YAML (`yaml.compose` marks), TOML (`tomllib` + `[section]` lines), XML (defusedxml SAX), Dockerfile (`dockerfile-parse` stages)
- Docs: Mistune AST headings → section chunks; fenced `#` text is not a heading
- Fixtures under `generic_polyglot/` (`package.json`, compose, Cargo, POM, Dockerfile, `ARCHITECTURE.md`)

### Days 5–6 shipped

- `GET /api/v1/repositories/{id}/summary` — `deterministic_summary` always; `llm_summary` separate when enrichment enabled (LangChain Azure)
- `GET /api/v1/repositories/{id}/chunks/search` — exact substring search; `search_mode=exact` (semantic/LLM rerank reserved for Week 9)
- Filters: language, path_prefix, support_level, chunk_type, extraction_method, parser_name, llm_enriched, validation_status

### Day 7 shipped

- Full matrix: discovery → classify → chunk → optional enrich → summary → exact search
- Worker E2E over `generic_polyglot`
- Asserts: no `re` imports in chunking package, no verified-deep pollution, LLM outage keeps deterministic chunks, batching (not 1-call-per-chunk), enrichment cache skips repeat calls
- Tests: `test_week07_day7_matrix.py`, `test_worker_pipeline_succeeds_with_generic_polyglot`

## Artifacts

- `apps/api/app/services/chunking/`
- `apps/api/app/services/llm/`
- `apps/api/app/services/repository_summary.py`
- `apps/api/app/services/chunks_query.py`
- `apps/api/tests/fixtures/generic_polyglot/`
- `apps/api/tests/test_chunking_week07.py`
- `apps/api/tests/test_config_docs_chunking.py`
- `apps/api/tests/test_summary_and_search.py`
- `apps/api/tests/test_week07_day7_matrix.py`

## Honesty

- Tree-sitter on generic languages ≠ verified deep
- LLM may not alter ranges or create verified symbols
- Deterministic indexing works with enrichment disabled

## Git policy

Agent does not `git add` / `commit` / `push`. You review and commit manually.
