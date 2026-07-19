# Week 0–2 Test Matrix

Maps required coverage areas to what is implemented and how it is tested.

| Area | Implemented? | Primary tests | Strategy |
| --- | --- | --- | --- |
| A. Repository import | Yes (URL + queue job) | `test_github_url*`, `test_import_*`, `test_api_contract_matrix`, `test_security_boundaries` | Param matrix + Hypothesis + API |
| B. File discovery / filtering | **Constants only** | `test_language_contract`, `test_classification_matrix` | Extension → DEEP/GENERIC/SKIP honesty |
| C. Parsing / structural analysis | No (Week 3+) | — | Deferred; see known-gaps |
| D. Indexing pipeline / jobs | Partial (queue through clone/snapshot → SUCCEEDED) | `test_job_*`, `test_concurrency_queue`, `test_coverage_edges` | State helpers + DB + race smoke |
| E. Database / migrations | Yes (initial schema) | `test_models`, `test_db_constraints`, `test_migrations_smoke`, `test_snapshots` | Constraints + live inspect |
| F. API | Yes (import/jobs/health) | `test_import_api`, `test_api_contract_matrix`, `test_cors_and_errors`, `test_health` | Status/schema/error matrix |
| G. Search / retrieval | No | — | Deferred |
| H. Frontend | Partial (Jobs/Dashboard) | `JobProgress*.test.tsx`, `jobs.test.ts`, `PageShell.test.tsx` | Component + helper unit |
| I. Configuration | Yes | `test_settings`, `test_config_matrix` | Defaults + CORS parsing |
| J. Security | Yes (URL/clone boundaries) | `test_security_boundaries`, URL injection matrix | Local mocks only |
| K. Cost / deployment policy | Docs | `test_policy_docs` | Artifact presence + banned deps |
| L. Reliability / observability | Partial | Error response tests; clone cleanup | Safe public errors |
| M. Performance smoke | Yes | `test_performance_smoke` (`slow`) | Generous thresholds |

## Parameterization highlights

- Valid / invalid / injection-like GitHub URLs
- DEEP vs GENERIC vs SKIP extensions (case variants, nested paths)
- Job stages labels/progress monotonicity
- Import payload wrong types / malformed JSON
- Job ID invalid UUID / path-like segments

## Scripts

| Script | Scope |
| --- | --- |
| `scripts/testing/run-fast-unit.sh` | No Postgres |
| `scripts/testing/run-integration.sh` | Postgres modules |
| `scripts/testing/run-slow.sh` | Performance |
| `scripts/testing/run-coverage.sh` | Full API + branch cov |
| `scripts/testing/run-full.sh` | API serial + web (set `FULL_PARALLEL=1` only with care) |
| `scripts/testing/run-mutation.sh` | mutmut subset |
| `scripts/testing/run-frontend.sh` | Vitest |

**Parallel note:** Shared developer Postgres makes xdist flaky for job-queue tests. Prefer serial for CI and local confidence.
