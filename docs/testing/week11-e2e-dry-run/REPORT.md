# Week 11 Day 7 — E2E dry run

- Generated: 2026-07-21T21:53:04.877506+00:00
- Fixture: `apps/api/tests/fixtures/mixed_frontend_backend` (mocked clone)
- Path: import → Ready → Search → Ask → Graph → summary → re-index unchanged → cancel
- Verdict: **PASS** (11/11)

## Checks

| Step | Pass | Detail |
| --- | --- | --- |
| import | yes | repo=66974112… job=8f67a536… |
| indexing_ready | yes | status=SUCCEEDED stage=completed info=index_full |
| repo_list | yes | n=50 |
| summary_support_mix | yes | files=8 mix={'generic': 1, 'deep': 7} |
| search_exact | yes | total=2 mode=exact |
| search_hybrid | yes | total=13 |
| ask_grounded | yes | status=ok citations=8 budget_used=1 |
| ask_budget | yes | used=1 |
| graph_modules | yes | nodes=9 edges=5 |
| reindex_unchanged | yes | info=index_unchanged msg=mode=unchanged reason=same_commit added=0 removed=0 changed=0 unchanged=8 ratio=0.000 |
| cancel_queued | yes | job=92236229… |

## Notes

- Clone is mocked for CI; live public GitHub import remains the demo path.
- Ask uses mock answers over retrieved evidence (citation-validated).
- Search stays deterministic; Ask stays budgeted.
