# Test Matrix — Week 0–4

Maps product areas to current implementation and primary tests.

| Area | Implemented? | Primary tests | Strategy |
| --- | --- | --- | --- |
| A. GitHub URL validation | Yes | `test_github_url*`, `test_github_url_security_extended` | Param matrix + Hypothesis |
| B. Repository import | Yes | `test_import_*`, API contract | Idempotency + HTTP |
| C. Job queue | Yes | `test_job_queue*`, `test_concurrency_queue` | Claim/lease/retry/race |
| D. Secure clone | Yes (mocked + flags) | `test_git_clone`, `test_security_boundaries` | Subprocess mocks |
| E. Discovery | Yes | `test_discovery*`, `test_discovery_extended`, retail goldens | FS matrix + caps |
| F. Language classification | Yes | `test_language_contract`, `test_classification_matrix` | Extension honesty |
| G. Source files persist | Yes | `test_source_files_persist`, `test_files_api` | Replace + filters |
| H. Snapshots | Yes | `test_snapshots` | Upsert + `.git` exclude |
| I. Python AST | Yes | `test_python_ast_*` | Fixtures + Hypothesis ids |
| J. QNames | Yes | AST matrix + deep fixtures | Package/`__init__` |
| K. Framework roles | Yes | `test_python_framework_*` | Positives + weak evidence |
| L. Import analysis | Yes | `test_python_framework_imports` | Local/stdlib/relative |
| M. Call extraction | Yes | `test_python_calls*` | resolved/ambiguous/unresolved |
| N. Symbol/call persist | Yes | `test_symbols_persist`, worker pipeline | Replace + stamps |
| O. Migrations 0001–0006 | Yes | `test_migrations_*` | File chain + live inspect |
| P. API routes Week 2–4 | Yes | `test_*_api*`, `test_api_filters_week04` | Filters + OpenAPI honesty |
| Q. Worker pipeline | Yes | `test_worker_pipeline` | Mocked clone e2e |
| R. Retail goldens | Yes (offline always) | `test_retail_discovery_golden` | Shape + optional full |
| S. Frontend wired UI | Partial | JobProgress, GraphPage, api, stubs | Component + client |
| T. Security | Yes | security_* + URL extended + injection filters | Local only |
| U. Cost / local-first | Docs + automated | `test_doc_contracts_week04`, `test_policy_docs` | Compose/CI/SDK bans |
| V. Doc contracts | Yes | `test_doc_contracts_week04` | Port, stages, parser stamp |
| W. Property-based | Partial | Hypothesis on URL/ids/classification | Deterministic profiles |
| X. Concurrency | Partial | `test_concurrency_queue` | Claim race |
| Y. Performance smoke | Yes | `test_*_perf`, `test_performance_smoke` | `@slow` generous budgets |
| Z. Search / embed | **Yes** (Ask deferred) | `test_search_week09`, `test_week09_day7_matrix`, SearchPage tests | Exact/semantic/hybrid + Validating; Ask = Week 10 |

## Scripts

See [`scripts/testing/README.md`](../../scripts/testing/README.md).
