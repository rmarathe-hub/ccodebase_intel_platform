# Known Gaps — Week 0–4

Honest deferrals and remaining test/engineering gaps **after** Weeks 0–4 implementation.

> Historical Week 0–2 gap list claimed discovery/parsers/graphs were absent. Those product features now exist; this file is the current source of truth.

## Product features not implemented (do not test as complete)

1. Chunking / embedding / validating job stages (labels exist; worker skips work)
2. Search API and functional Search UI
3. Ask API / LLM answers / citation validation
4. Deep parsers for Java, TypeScript, JavaScript (classified DEEP; no parser stamp/symbols)
5. Generic heuristic section extraction
6. Interactive graph visualization (Graph page is a call-site table)
7. Authentication / multi-tenancy
8. Private repository import / non-GitHub hosts
9. Incremental indexing
10. packages/parser-core deep pipeline (Python logic lives under `apps/api/app/services`)

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

Resource group `rg-codeintel-demo` must remain unused. Suite does not create cloud resources or call paid APIs. CI workflow does not reference Azure.
