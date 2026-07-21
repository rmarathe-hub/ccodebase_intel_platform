# Known Gaps — current

Honest deferrals after Weeks 0–7. Update as Week 8+ lands.

## Product features not implemented (do not test as complete)

1. ~~Embedding / validating job stages~~ — Embedding + Validating wired Week 9 Days 1–2 + 5
2. ~~Functional Search UI~~ — Search page (exact / semantic / hybrid) Week 9 Day 6
3. Ask API / citation-validated answers (Week 10)
4. ~~Semantic / hybrid search modes (exact only until Week 9 Days 3–4)~~ — `search_mode=exact|semantic|hybrid` shipped Week 9 Days 3–4
5. ~~Format-native configuration + Markdown AST chunking — Week 7 Days 3–4~~ (done)
6. ~~Deterministic + LLM-enhanced repository summaries — Week 7 Day 5~~ (done)
7. ~~Interactive graph visualization~~ — React Flow + accuracy matrix shipped Week 8 Days 6–7
8. Authentication / multi-tenancy
9. Private repository import / non-GitHub hosts
10. Incremental indexing
11. `packages/parser-core` deep pipeline (Python / JS-TS / Java logic lives under `apps/api/app/services`)

## Implemented and no longer gaps

- Deep parsers + symbols for Python, Java, TypeScript, JavaScript
- Call extraction (Python / JS-TS / Java) with confidence
- Java inheritance / Spring architecture roles
- Mixed frontend/backend and Spring fixture matrices
- Chunk schema + deep symbol-aware chunks + generic Tree-sitter (Go/Rust/C/C++/C#/Ruby/Shell) + SQLGlot
- Worker Chunking stage + optional batched LangChain/Azure enrichment (mocked in CI)
- Format-native config chunks (JSON/YAML/TOML/XML/Dockerfile) + Mistune Markdown sections
- Repository summary API (deterministic + optional LLM) and exact chunk search API
- Week 7 Day 7 polyglot matrix + worker E2E (generic languages stay non-deep)
- Week 7 real-repo validation (typer / spark / commander.js / cobra / awesome-compose) — see [week7-validation/REPORT.md](./week7-validation/REPORT.md)
- Week 8 Day 1–2: `RelationKind`, structural IMPORTS/EXPORTS/CONTAINS, module/package graph APIs
- Week 8 Day 3–4: call neighborhood graph, implementations API, directory graph API
- Week 8 Day 5–6: graph filters (`filters` echo) + React Flow Graph page
- Week 8 Day 7: graph accuracy matrix (circular imports, ambiguous calls, implementations, mixed langs, directory scale)
- Week 9 Day 1–2: `chunk_embeddings` (pgvector) + `EmbeddingProvider` + worker Embedding stage (local-hash default)
- Week 9 Day 3–4: semantic + hybrid chunk search (`search_mode`, scores, filters)
- Week 9 Day 5: worker Validating stage (`snapshot_validation.py`)
- Week 9 Day 6: functional Search UI (exact / semantic / hybrid)
- Week 9 Day 7: retrieval matrix / honesty / smoke (`test_week09_day7_matrix.py`)
- Week 9 hybrid weight eval (30/70, 50/50, 70/30): see [week9-hybrid-eval/REPORT.md](./week9-hybrid-eval/REPORT.md)

## Architecture decisions locked for Week 7+

- Parser-authority + optional LLM enrichment (no regex structural extraction)
- Deep languages chunk from existing verified symbols only
- Generic languages stay `support_level=generic`, `verified_deep=false`
- Paid LLM enrichment opt-in; CI mocks providers; exact search works offline
- Azure OpenAI primary; LangChain thin adapter only (no indexing agents)
- First-cut generic languages: Go, Rust, C/C++, C#, Ruby, Shell, SQL + JSON/YAML/TOML/XML/Dockerfile/Markdown
- Remaining generic languages share the same parser interface later

## Test / engineering gaps

| Gap | Notes |
| --- | --- |
| `python_calls.py` branch coverage ~72% | Ambiguous path covered; more attr/import-alias branches remain |
| Alembic upgrade→downgrade→upgrade automation | Head + chain file checks + live schema; full ephemeral DB cycle still light |
| Real `git` clone against local bare repo | Most clone tests mock `_run_git` |
| Browser E2E (Playwright) | Component tests only |
| Mutation suite runtime | Config expanded; run `run-mutation.sh` and record score |
| Shared developer Postgres residue | Worker tests quarantine QUEUED/RUNNING jobs; prefer disposable DB in CI (now provided) |
| Frontend page coverage | Graph + stubs + api client added; Jobs/Files/Symbols pages still mostly untested as components |
| Coverage `fail_under` | Still `0` — intentional until gate agreed |

## Decision-needed

- Whether bare class bases `Base` / `Model` should keep `sqlalchemy_model` without a `sqlalchemy` path hint (current behavior; tested as documented heuristic).
- Whether GitHub URL trailing whitespace beyond `strip()` should be rejected (newlines currently stripped then accepted).
- Whether CI should enforce coverage fail_under (suggested 80–85% once stable).

## Azure / cost

Resource group `rg-codeintel-demo` must remain unused unless explicitly instructed.
CI must not call paid APIs. Optional local enrichment follows
[deployment/cost-policy.md](../deployment/cost-policy.md).
