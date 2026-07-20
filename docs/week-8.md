# Week 8 — Unified relationships and interactive graphs

## Status

| Day | Scope | Status |
| --- | --- | --- |
| 1 | Unified `RelationKind` + structural IMPORTS/EXPORTS/CONTAINS edges | Done |
| 2 | Module + package graph builders + APIs | Done |
| 3 | Deep caller/callee graph neighborhoods + implementations API | Done |
| 4 | Generic directory graph | Done |
| 5 | Graph API polish (filters, depth) | Done |
| 6 | React Flow Graph page | Done |
| 7 | Graph accuracy matrix | Not started |

## Architecture (locked)

```text
Deep language parsers
        ↓
Symbols + CALLS (symbol_calls) + Java EXTENDS/IMPLEMENTS (symbol_relations)
        ↓
Structural relation pass (IMPORTS / EXPORTS / CONTAINS → symbol_relations)
        ↓
Module / package / call / directory graph aggregation
        ↓
Post-build filters (language, support_level, relation_kind, path, caps)
        ↓
Graph APIs + React Flow UI
```

- **CALLS** stay in `symbol_calls` (high-volume call sites); call **graphs** read from that table.
- **RelationKind** enum is the shared vocabulary; `/relations` validates against it.
- Generic languages must not gain verified-deep call/inheritance graphs.

### Day 1 shipped

- `app/models/relation_kinds.py` — `RelationKind` + confidence constants
- `app/services/relationships.py` — `replace_structural_relations_for_snapshot`
- Worker **Building relationships** stage runs structural pass after language persist
- `/relations` accepts `imports`, `exports`, `contains`, `extends`, `implements`, …
- Tests: `test_week08_day1_relations.py`

### Day 2 shipped

- `app/services/graphs.py` — module + package graph builders from IMPORTS
- `GET /api/v1/repositories/{id}/graph/modules`
- `GET /api/v1/repositories/{id}/graph/packages`
- Schemas: `app/schemas/graphs.py`
- Tests: `test_week08_day2_graphs.py`

### Day 3 shipped

- `build_call_neighborhood_graph` — BFS over `symbol_calls` with confidence filter
- `GET /api/v1/repositories/{id}/graph/calls?symbol_id=&depth=&confidence=`
- `GET /api/v1/repositories/{id}/symbols/{symbol_id}/implementations` (Java IMPLEMENTS)
- Tests: `test_week08_day3_call_graph.py`

### Day 4 shipped

- `build_directory_graph` — directory hierarchy + optional file leaves
- Inferred cross-directory IMPORTS when module targets resolve within snapshot
- `GET /api/v1/repositories/{id}/graph/directories?include_files=`
- Tests: `test_week08_day4_directories.py`

### Day 5 shipped

- Shared `apply_graph_filters` / `filters_echo` (`app/services/graph_filters.py`)
- All graph endpoints accept: `support_level`, `relation_kind`, `confidence`, `path_prefix`, `max_nodes`, `max_edges` (plus existing language / depth / include_files / local_imports_only)
- Response includes `filters` echo of applied query params
- Tests: `test_week08_day5_filters.py`

### Day 6 shipped

- `@xyflow/react` Graph page: Modules / Packages / Directories / Calls
- UI filters: language, support level, confidence, path prefix, local imports, depth, center symbol
- Deterministic layered layout (no paid layout service)
- Frontend API clients + Vitest coverage
- Honesty notice: generic directory graphs do not invent deep call edges

## Artifacts

- `apps/api/app/models/relation_kinds.py`
- `apps/api/app/services/relationships.py`
- `apps/api/app/services/graphs.py`
- `apps/api/app/services/graph_filters.py`
- `apps/api/app/schemas/graphs.py`
- `apps/api/app/schemas/implementations.py`
- `apps/web/src/pages/GraphPage.tsx`
- `apps/web/src/lib/graphs.ts`
- `apps/api/tests/test_week08_day1_relations.py` … `test_week08_day5_filters.py`

## Git policy

Agent does not `git add` / `commit` / `push`. You review and commit manually.
