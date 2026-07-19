# LLM Enrichment Architecture

Optional semantic enrichment for parser-derived chunks and repository summaries.
Deterministic indexing and exact search must never depend on this path.

## Pipeline

```text
Parser/AST (source of truth)
        ↓
Deterministic chunks + citations
        ↓
LangChain pipeline (thin) ──or── direct Azure OpenAI SDK
        ↓
Azure OpenAI (structured output)
        ↓
Validation against parser-derived evidence
        ↓
Persist enrichment + cache
```

## Authority rules

1. Parsers own chunk boundaries, byte/line ranges, symbols, hashes, and citations.
2. The LLM may add labels, summaries, probable roles, and architecture interpretation.
3. The LLM must **not** invent ranges, alter boundaries, or create verified symbols.
4. Regex must **not** define structural extraction or chunk boundaries.

## LangChain vs direct SDK

Use LangChain only where it adds concrete value:

- Azure chat model wiring (`AzureChatOpenAI`)
- Structured output helpers
- Retries / prompt templates when they reduce custom code

Prefer the **direct Azure OpenAI SDK** (or first-party code) when it is simpler for:

- Budget metering and kill switches
- Content-hash caching and snapshot idempotency
- Batch packing and priority selection
- Evidence / schema validation
- Usage persistence

Do **not** use LangChain agents, autonomous tool loops, or free-running planners
for indexing enrichment.

All provider-specific types stay behind `LLMProvider` in `apps/api/app/services/llm/`.

## Batching and prioritization

Never default to one LLM call per chunk. Batch related high-priority chunks.

Priority order:

1. Repository summaries
2. README / architecture documentation
3. Top-level declarations
4. Entry-point candidates (filename hints are candidates only)
5. Configuration / build files
6. High-value search-result enrichment (search-time; optional)

## Cost and safety

| Control | Behavior |
| --- | --- |
| Default | `LLM_ENRICHMENT_ENABLED=false` |
| CI | Mocked; no paid calls |
| Caps | Requests, tokens, estimated USD per job + daily budget |
| Cache | `content_hash + parser_version + prompt_version + model/deployment` |
| Over budget | Skip enrichment; keep deterministic chunks |
| Secrets | Env-only; never logged |

See [deployment/cost-policy.md](./deployment/cost-policy.md).

## Target provider

When enrichment is enabled, the primary provider is **Azure OpenAI**
(`LLM_PROVIDER=azure_openai`) with deployment name, endpoint, and API version
from environment settings. Other providers remain swappable via `LLMProvider`.
