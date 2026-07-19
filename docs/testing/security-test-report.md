# Security Test Report — Week 0–4

**Scope:** Local, non-destructive tests only. No external attack targets. No Azure.

## Controls exercised

| Control | How verified |
| --- | --- |
| Public GitHub HTTPS only | Large accept/reject URL matrices |
| Reject credentials / SSH / file / git protocols | `test_github_url*` + security extended |
| Reject lookalike hosts / IPs / localhost | Extended matrix |
| Reject tree/blob/issue/PR/query/fragment URLs | Extended matrix |
| Clone: no `shell=True`, depth 1, no submodules | `test_security_boundaries` / clone mocks |
| Clone cleanup on failure | Existing security tests |
| Secret-path skip (`.env`, keys) | Discovery extended + contract |
| Symlink not followed | Discovery extended |
| Path traversal / ignored dirs pruned | Discovery + ignored dir matrix |
| API injection-like filters | `name_contains` SQL/HTML/path strings → 200, no traceback |
| No Search/Ask endpoints | OpenAPI absence assert |
| No paid SDK imports in `app/` | Doc contract scan |
| Compose has no Redis/K8s/Azure | Doc contract |
| CI does not provision Azure | Workflow text assert + review |

## Findings

| Severity | Finding | Action |
| --- | --- | --- |
| Info | Trailing newline on URL accepted after `str.strip()` | Documented |
| Info | Framework heuristic may label bare `Base` as SQLAlchemy | Decision-needed |
| Fixed (process) | CI previously skipped Postgres integration tests | Postgres service added |

## Residual risk

- Heuristic call resolution can mis-label confidence (by design; not a security boundary).
- Shared local Postgres is not multi-tenant isolated; tests use unique names + quarantine.
- Imported repository content is treated as untrusted evidence; execution is still forbidden and not performed by tests.
