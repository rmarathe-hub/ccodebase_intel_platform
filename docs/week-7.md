# Week 7 — Generic chunking + optional LLM enrichment

## Status

| Day | Scope | Status |
| --- | --- | --- |
| 1 | Chunk schema + deep symbol-aware chunks + generic Tree-sitter source chunks | Done |
| 2 | Multi-lang generic parsers + LangChain Azure enrichment (batched) | Done |
| 3 | Format-native configuration chunking | Not started |
| 4 | Markdown / document AST chunking | Not started |
| 5 | Deterministic + LLM-enhanced repository summaries | Not started |
| 6 | Exact PostgreSQL chunk search (LLM-independent) | Not started |
| 7 | Polyglot fixture matrix + worker E2E (full) | Not started |

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

### Artifacts

- `apps/api/app/services/chunking/`
- `apps/api/app/services/llm/`
- `apps/api/tests/fixtures/generic_polyglot/`
- `apps/api/tests/test_chunking_week07.py`

## Honesty

- Tree-sitter on generic languages ≠ verified deep
- LLM may not alter ranges or create verified symbols
- Deterministic indexing works with enrichment disabled

## Git policy

Agent does not `git add` / `commit` / `push`. You review and commit manually.
