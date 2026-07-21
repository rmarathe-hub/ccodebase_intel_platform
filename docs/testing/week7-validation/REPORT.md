# Week 7 validation rollup

Post–Day 7 real-repository validation of the **deterministic** indexing pipeline
(LLM enrichment **OFF**).

- Generated: 2026-07-20T01:39:17Z
- API: `http://127.0.0.1:8001` (port 8000 was occupied by another local project)
- Postgres: `localhost:5434`
- Runner: [`run_validation.py`](./run_validation.py)
- Per-repo reports: `report-*.md`

## Verdict

**PASS — ready for Week 8.** All five repositories imported, indexed, summarized,
exact-searched, and re-indexed with stable content hashes and identical chunk
multisets. Zero fake verified symbols on non-deep languages. No `re` imports in
the chunking package. No production-logic changes required.

| Repository | Import | Files | Chunks | Symbols | Search | Re-index deterministic | Failures |
| --- | --- | --- | --- | ---: | ---: | --- | ---: |
| [fastapi/typer](https://github.com/fastapi/typer) (Python deep) | PASS | 773 | 2904 | 4258 | PASS | PASS | 0 |
| [perwendel/spark](https://github.com/perwendel/spark) (Java deep) | PASS | 213 | 1582 | 3165 | PASS | PASS | 0 |
| [tj/commander.js](https://github.com/tj/commander.js) (JS/TS deep) | PASS | 219 | 646 | 890 | PASS | PASS | 0 |
| [spf13/cobra](https://github.com/spf13/cobra) (Go generic) | PASS | 66 | 825 | 0 | PASS | PASS | 0 |
| [docker/awesome-compose](https://github.com/docker/awesome-compose) (config/docs) | PASS | 479 | 956 | 307* | PASS | PASS | 0 |

\*awesome-compose contains incidental sample apps (Python/JS/Java/TS); those are
correctly deep. Compose YAML / docs stay generic. No fake deep symbols outside
`python|java|javascript|typescript`.

## Honesty checks (all PASS)

| Check | Result |
| --- | --- |
| Binary / ignored files skipped | PASS (e.g. typer 18 skip / 11 binary; awesome-compose 124 skip / 50 binary) |
| Parser provenance on chunks | PASS (parser_name + parser_version on all chunks) |
| No duplicate chunk spans | PASS |
| Enrichment OFF → `llm_enriched=0` | PASS |
| Go (cobra): `verified_deep=0`, symbols=0 | PASS |
| No `import re` in `app/services/chunking` | PASS |
| Deterministic summary with enrichment disabled | PASS (`llm_summary_status=disabled`) |
| Re-index: file hash mismatches | 0 across all repos |
| Re-index: chunk key multiset equal | PASS across all repos |

## Exact search citation samples

| Repo | Query | Hits | Example citation |
| --- | --- | ---: | --- |
| typer | `Option` | 603 | `docs/features.md:39-44` (documentation, mistune-ast) |
| spark | `Route` | 340 | `src/main/java/spark/Access.java:24-34` (java, java-treesitter, verified_deep) |
| commander | `Command` | 344 | `CHANGELOG.md:1-17` (documentation) |
| cobra | `Command` | 629 | `active_help.go:47-53` (go, go-treesitter, **verified_deep=false**) |
| awesome-compose | `postgres` | 60 | `gitea-postgres/compose.yaml:1-26` (yaml-compose) |
| awesome-compose | `nginx` | 61 | compose YAML sections (configuration, not deep) |

All representative queries returned ≥1 hit with path + line range.

## Indexing durations (wall clock, clone+index; enrichment off)

Approx. first successful job per repo (from worker logs): typer ~6–10s, spark ~3s,
commander ~2s, cobra ~1s, awesome-compose ~2s (clone dominated for compose ~15MB).

## Known pipeline gap (documented, not a regression)

Worker marks jobs **SUCCEEDED after Chunking**. Job stages `embedding` and
`validating` exist in the enum but are **not wired** yet (Week 9+). This does not
block Week 8 graphs.

## Recommendations before Week 8

1. **Proceed to Week 8** (module/package/directory graph APIs + React Flow).
2. Keep enrichment default-off for CI and local demos unless explicitly testing LLM.
3. When building graphs, treat cobra-style Go edges as **generic / inferred only**.
4. awesome-compose is a good polyglot fixture: assert UI never promotes incidental
   deep sample-app symbols as “the repo is a Java/Python project.”
5. Port **8000** may be taken by other local stacks; use **8001** or stop conflicting
   containers when running this validation again:
   `python docs/testing/week7-validation/run_validation.py http://127.0.0.1:8001`

## How to re-run

```bash
# Postgres on 5434; API + worker with enrichment off
cd apps/api && .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8001
# other terminal:
PYTHONPATH=apps/api:apps/worker apps/api/.venv/bin/python -m worker
# validation:
apps/api/.venv/bin/python docs/testing/week7-validation/run_validation.py http://127.0.0.1:8001
```
