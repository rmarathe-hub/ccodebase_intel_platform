# Week 8 — Unified relationships and interactive graphs

## Status

| Day | Scope | Status |
| --- | --- | --- |
| 1 | Unified `RelationKind` + structural IMPORTS/EXPORTS/CONTAINS edges | Done |
| 2 | Module + package graph builders + APIs | Done |
| 3 | Deep caller/callee graph neighborhoods + implementations API | Not started |
| 4 | Generic directory graph | Not started |
| 5 | Graph API polish (filters, depth) | Not started |
| 6 | React Flow Graph page | Not started |
| 7 | Graph accuracy matrix | Not started |

## Architecture (locked)

```text
Deep language parsers
        ↓
Symbols + CALLS (symbol_calls) + Java EXTENDS/IMPLEMENTS (symbol_relations)
        ↓
Structural relation pass (IMPORTS / EXPORTS / CONTAINS → symbol_relations)
        ↓
Module / package graph aggregation
        ↓
Graph APIs (+ React Flow UI later)
```

- **CALLS** stay in `symbol_calls` (high-volume call sites).
- **RelationKind** enum is the shared vocabulary; `/relations` validates against it.
- Generic languages must not gain verified-deep call/inheritance graphs (Week 8 Day 4+).

### Day 1 shipped

- `app/models/relation_kinds.py` — `RelationKind` + confidence constants
- `app/services/relationships.py` — `replace_structural_relations_for_snapshot`
- Worker **Building relationships** stage now runs structural pass after language persist
- `/relations` accepts `imports`, `exports`, `contains`, `extends`, `implements`, …
- Tests: `test_week08_day1_relations.py`

### Day 2 shipped

- `app/services/graphs.py` — module + package graph builders from IMPORTS
- `GET /api/v1/repositories/{id}/graph/modules`
- `GET /api/v1/repositories/{id}/graph/packages`
- Schemas: `app/schemas/graphs.py`
- Tests: `test_week08_day2_graphs.py`

## Artifacts

- `apps/api/app/models/relation_kinds.py`
- `apps/api/app/services/relationships.py`
- `apps/api/app/services/graphs.py`
- `apps/api/app/schemas/graphs.py`
- `apps/api/tests/test_week08_day1_relations.py`
- `apps/api/tests/test_week08_day2_graphs.py`

## Git policy

Agent does not `git add` / `commit` / `push`. You review and commit manually.
