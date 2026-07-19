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

```text
Parser / AST (source of truth)
        ↓
Deterministic chunks + citations
        ↓
Priority batching + budget gate (first-party)
        ↓
LLMProvider → Azure OpenAI structured output
        (LangChain only as thin orchestration adapter)
        ↓
Validate against parser-derived evidence
        ↓
Persist enrichment + cache
```

See [language-support.md](./language-support.md), [indexing-pipeline.md](./indexing-pipeline.md),
and [llm-enrichment.md](./llm-enrichment.md).

### Provider and LangChain boundary

| Layer | Owner |
| --- | --- |
| Chunk boundaries, ranges, symbols, hashes, citations | Deterministic parsers |
| Priority selection, batch packing, budget, kill switch, cache | First-party (`app/services/llm/`) |
| Schema + source-range validation | First-party Pydantic validators |
| Azure OpenAI chat + structured output | `LLMProvider` (LangChain `AzureChatOpenAI` **or** direct Azure SDK where simpler) |
| Agents / free tool loops | **Forbidden** for indexing enrichment |

Default enrichment target when enabled: **Azure OpenAI**.
LangChain is an orchestration adapter only — not an agent runtime and not the parser.

### Cost controls

- Do **not** make one LLM call per chunk; batch related prioritized chunks
- Prioritize: repository summaries, README/docs, top-level decls, entry-point candidates, config/build, high-value search results
- Cache by content hash + parser version + prompt version + model/deployment
- Caps: max requests/job, max tokens/job, estimated cost/job, daily budget
- Over budget → keep deterministic index; skip enrichment only
- CI: enrichment off; providers mocked; no paid calls

### Corrections vs earlier Week 7 sketch

- No regex structural extraction
- Python / Java / JS / TS chunk from **existing deep symbols** only
- Generic languages: Tree-sitter / format parsers → `generic_structure` / `heuristic_section`
- Remaining generic languages share the same parser interface later
- First cut: Go, Rust, C/C++, C#, Ruby, Shell, SQL + JSON/YAML/TOML/XML/Dockerfile/Markdown

## Planned artifacts

- `chunks` migration + model (provenance fields)
- `apps/api/app/services/chunking/`
- `apps/api/app/services/llm/` — `LLMProvider`, schemas, validate, budget, cache, Azure adapter
- Exact search API + worker Chunking stage
- `apps/api/tests/fixtures/generic_polyglot/`
- Optional pyproject extra `[llm]` for LangChain / Azure OpenAI SDKs

## Honesty

- Tree-sitter on generic languages ≠ verified deep
- LLM may not alter ranges or create verified symbols
- Deterministic indexing works with enrichment disabled

## Git policy

Agent does not `git add` / `commit` / `push`. You review and commit manually.
