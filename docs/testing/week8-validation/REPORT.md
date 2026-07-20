# Week 8 validation rollup

- Generated: 2026-07-20T02:54:54.036944+00:00
- API: `http://127.0.0.1:8001`
- LLM enrichment: OFF
- Clone limit: 52428800 bytes (not weakened)
- **Rollup verdict: PASS — ready for Week 9**

## Per-repository summary

| Repository | Commit | Chunks | Relations | Calls | Duration (s) | Failures |
| --- | --- | --- | --- | --- | --- | --- |
| Python — fastapi/typer | `60af34b60ab2` | 2904 | `{ "imports": 2097, "contains": 366 }` | 6733 | 10.05 | 0 |
| Java — perwendel/spark | `1973e402f5d4` | 1582 | `{ "contains": 1340, "imports": 1032, "extends": 33, "implements": 19 }` | 3660 | 10.03 | 0 |
| TypeScript/JS — tj/commander.js | `ba6d13ddb424` | 646 | `{ "imports": 559, "contains": 197, "exports": 8 }` | 829 | 5.02 | 0 |
| Go — spf13/cobra | `adbc8813901b` | 825 | `{}` | 0 | 5.08 | 0 |
| Config/Docs — docker/awesome-compose | `30f4b7f6a6c3` | 956 | `{ "imports": 167, "contains": 41, "extends": 2, "implements": 1 }` | 255 | 5.03 | 0 |
| Mixed monorepo — supabase/supabase | `—` | n/a | `n/a` | n/a | 0.0 | 0 |

## Verdict

**PASS — ready for Week 9.**

Five Week-7-scale repositories completed the normal import → relationships → graph API → re-index path with enrichment OFF. Supabase was correctly rejected by existing clone safety (`clone_timeout` at 120s; GitHub size ≈2.4M KB) without weakening `git_clone_max_bytes`.

## Evidence highlights

| Repo | Deep vs generic | Notable findings |
| --- | --- | --- |
| typer | Python deep | IMPORTS+CONTAINS; CALLS with resolved/ambiguous/unresolved; module/package/directory + callers graphs |
| spark | Java deep | packages; EXTENDS/IMPLEMENTS; implementations API; call neighborhoods |
| commander | JS/TS deep | IMPORTS/EXPORTS/CONTAINS; call graph; external imports unresolved |
| cobra | Go generic | directory graph only; no invented Go call graph |
| awesome-compose | config/docs primary + incidental deep samples | directory graph; sample Java/JS labeled per-file — not repo-wide deep |
| supabase | not indexed | safety limits enforced; no optimistic deep claim |

## Defects found and fixed during validation

1. **Import job visibility race** — `get_db` commits after the HTTP response is sent; flush-only import allowed `GET /jobs/{id}` 404. Fixed by committing in `import_repository` / `retry_indexing_job`. Regression: `test_import_job_visible_without_dependency_teardown_commit`.
2. **Duplicate Java interface EXTENDS from grammar** — kind-aware extraction + dedupe in `java_parser._extract_inheritance`. Regression: `test_interface_extends_generic_no_duplicate_edges`.
3. **Collapsed EXTENDS provenance across duplicate FQCNs** — sample trees reusing packages lost per-file `source_file_id`. Fixed by resolving each edge with its file id and preferring `(source_file_id, qname)` symbol lookup. Regression: `test_duplicate_fqcn_across_sample_apps_keeps_per_file_extends`.

## Limitations (honest)

- Supabase was never fully indexed; multi-GB directory-graph stress was not exercised end-to-end. Limit enforcement itself passed.
- React Flow UI validated via source wiring to live `/graph/*` APIs plus API smoke (no separate browser E2E harness).
- Embedding / Validating worker stages remain unwired (Week 9+).

## Recommendations before Week 9

- Proceed to embeddings/retrieval with graph honesty preserved.
- Keep clone/discovery caps; optional sparse/subtree import for oversized monorepos can be a later opt-in.
- Do not treat inferred directory edges as verified-deep calls.

## Artifacts

- `docs/testing/week8-validation/run_validation.py`
- `docs/testing/week8-validation/report-typer.md`
- `docs/testing/week8-validation/report-spark.md`
- `docs/testing/week8-validation/report-commander.md`
- `docs/testing/week8-validation/report-cobra.md`
- `docs/testing/week8-validation/report-awesome-compose.md`
- `docs/testing/week8-validation/report-supabase.md`
