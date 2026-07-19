# Known Gaps — Week 0–2 Test Scope

Honest deferrals. Do not treat these as failing tests; they are **not yet product features**.

## Week 3+ product gaps (no tests claiming behavior)

1. **File discovery / ignore / vendor / binary / size policies** — only extension→support-level constants exist today.
2. **Deep parsers** for Python, Java, TypeScript, JavaScript (AST/Tree-sitter, symbols, ranges).
3. **Generic searchable extraction** for C/C++/C#/Go/Rust/Ruby/PHP/Kotlin/Swift/Scala/Shell/SQL/HTML/CSS/config/docs beyond classification constants.
4. **Structural graphs** (calls, inheritance, imports as edges).
5. **Chunking / embedding / validation stages** — UI labels exist; worker does not execute them yet.
6. **Search API** (filename, path, symbol, text, filters, pagination, snippets, citations).
7. **Hybrid retrieval / AI answers** / citation validation.
8. **Real GitHub network failures** (rate limit, private repo, redirects) end-to-end — covered via mocks/validation only; live clone of retail fixture is optional manual.
9. **Worker process integration test** as a separate process (in-process services covered).
10. **Alembic downgrade / upgrade-after-downgrade** cycle automation (upgrade/head + schema inspect covered).
11. **Browser E2E** (Playwright/Cypress) for Jobs import UX — component tests only.
12. **Isolated ephemeral Postgres per test run** — suite uses shared Compose DB with cleanup; CI should prefer disposable DB when available.

## Test engineering gaps

| Gap | Mitigation |
| --- | --- |
| xdist flaky on shared jobs table | Serial default in scripts; document in report |
| mutmut mutates entire `app` with focused tests → many “no tests” | Report score among killed+survived; narrow later |
| `db/deps.py` low coverage | Expected with TestClient override |
| Live network clone not in every run | Mocked clone; retail URL used as identity fixture |

## Decision-needed (ambiguous contracts)

- Whether route-level `GitHubURLValidationError` → 400 should remain given Pydantic already returns 422.
- Whether vendor/`node_modules`/`dist` skip rules belong in language_contract now or only in Week 3 discovery.

## Azure / cost

Resource group `rg-codeintel-demo` must remain unused. Suite does not create cloud resources or call paid APIs.
