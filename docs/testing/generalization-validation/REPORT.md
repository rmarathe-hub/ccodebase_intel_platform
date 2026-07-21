# Generalization validation rollup

- Generated: 2026-07-20T03:09:50.182534+00:00
- API: `http://127.0.0.1:8001`
- LLM enrichment: OFF
- Clone limit: 52428800 bytes (not weakened)
- **Rollup verdict: PASS**

## Purpose

Determine whether the platform generalizes to **unseen** public repositories (not used in Week 7/8 validation), across deep languages, generic languages, and config/docs.

Production logic was not modified for this run. The only harness fix was aligning validation language aliases with the platform contract (`c++` / `c#`).

## Verdict

**PASS**

The platform generalized successfully across all 10 repositories.

## Per-repository summary

| Repository | Commit | Chunks | Relations | Calls | Re-index | Failures |
| --- | --- | --- | --- | --- | --- | --- |
| Python API — pallets/flask | `36e4a824f340` | 1037 | imports 576, contains 332 | 3841 | PASS | 0 |
| Python CLI — pallets/click | `333c28d79cd9` | 1694 | imports 560, contains 411 | 6231 | PASS | 0 |
| Java — javalin/javalin | `6600d23a36ec` | 669 | contains 288, imports 353, extends 7, implements 7 | 1302 | PASS | 0 |
| JavaScript — axios/axios | `c44f8d0a910d` | 2006 | imports 912, contains 192, exports 27 | 1808 | PASS | 0 |
| TypeScript — colinhacks/zod | `912f0f51b0ce` | 2373 | imports 1280, contains 280, exports 267 | 2647 | PASS | 0 |
| Go — go-chi/chi | `8b258c7bb28f` | 577 | {} | 0 | PASS | 0 |
| Rust — clap-rs/clap | `0838e824e6d9` | 4468 | imports 4 (incidental deep only) | 17 (incidental) | PASS | 0 |
| C++ — fmtlib/fmt | `b5d1e5404bd6` | 3052 | contains/imports from incidental Python only | 451 (incidental) | PASS | 0 |
| C# — Humanizr/Humanizer | `f9292aa90948` | 2029 | imports 7 (incidental Python) | 55 (incidental) | PASS | 0 |
| Config/Docs — awesome-selfhosted | `9f4f907cf300` | 147 | {} | 0 | PASS | 0 |

## Deep vs generic honesty

| Repo | Mode | Assessment |
| --- | --- | --- |
| flask, click | Python deep | Verified Python symbols; IMPORTS/CONTAINS; CALLS with resolved/ambiguous/unresolved; module/package/directory + callers graphs |
| javalin | Java deep | Verified Java symbols; EXTENDS/IMPLEMENTS; implementations API; call neighborhoods |
| axios, zod | JS/TS deep | IMPORTS/EXPORTS/CONTAINS; verified-deep chunks; call graph |
| chi | Go generic | Directory graph; **0 Go symbols / 0 Go calls** — no invented deep call graph |
| clap | Rust generic | Directory graph; **0 Rust symbols / 0 Rust calls**; incidental Python edges only |
| fmt | C++ generic | Directory graph; **0 C++ symbols / 0 C++ calls**; incidental Python (test helpers) labeled per-file |
| humanizer | C# generic | Directory graph; **0 C# symbols / 0 C# calls**; incidental Python only |
| awesome-selfhosted | Docs/config | Documentation + configuration chunks; heading/section structure via mistune/yaml parsers; directory graph; exact citations |

## Validation coverage (all repos)

- Import → snapshot → discover → classify → parse → chunk → relationships → persist → summarize → exact search → graph APIs → re-index
- Enrichment OFF (`llm_enriched=0` everywhere)
- No regex structural parsing in chunking package
- Parser provenance (`parser_name` + `parser_version`) on all chunks
- No duplicate chunk spans; deterministic chunk/relation/call multisets on re-index
- No orphan relation IDs; no cross-snapshot leakage
- Exact search returns path/line citations with deterministic ordering smoke
- Graph filters (support_level, confidence, caps, path_prefix, inferred=false) validated

## Limitations (honest, not failures)

- Embedding / Validating worker stages remain unwired; jobs succeed after chunking + relationships.
- Generic languages intentionally lack verified symbols and deep call graphs; incidental deep files inside otherwise-generic repos (e.g. Python helpers in fmt/clap/Humanizer) are analyzed as deep **per-file**, not as repository-wide deep support.
- React Flow UI validated via source wiring + live `/graph/*` API smoke (no separate browser E2E).
- Clone/discovery safety caps unchanged (50 MiB).

## Production defects

None found. No production code changes were required for this generalization set.

Harness-only correction: validation expected language ids `cpp`/`csharp`; platform contract uses `c++`/`c#`. Fixed in `run_validation.py` only.

## Artifacts

- `docs/testing/generalization-validation/run_validation.py`
- `docs/testing/generalization-validation/report-flask.md`
- `docs/testing/generalization-validation/report-click.md`
- `docs/testing/generalization-validation/report-javalin.md`
- `docs/testing/generalization-validation/report-axios.md`
- `docs/testing/generalization-validation/report-zod.md`
- `docs/testing/generalization-validation/report-chi.md`
- `docs/testing/generalization-validation/report-clap.md`
- `docs/testing/generalization-validation/report-fmt.md`
- `docs/testing/generalization-validation/report-humanizer.md`
- `docs/testing/generalization-validation/report-awesome-selfhosted.md`
- `docs/testing/generalization-validation/run.log`
