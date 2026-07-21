# Week 11 — Product polish (import UX + reliability)

## Status

| Day | Scope | Status |
| --- | --- | --- |
| 1–2 | Repository import UX (paste URL → live stages → Ready) | Done |
| 3 | Repo history / switch previously indexed repos; re-index | Done |
| 4 | Failure UX (clone limits, partial support, cancel) | Done |
| 5 | Incremental indexing best-effort (full re-index fallback OK) | Planned |
| 6 | Search + Ask polish (filters, empty states, per-repo Ask budget) | Planned |
| 7 | End-to-end dry run (import → search → ask → graph) | Planned |

## Theme

Make the demo path feel like a product: paste a public GitHub URL and explore
without editing validation scripts.

## Pipeline UX

```text
Paste GitHub URL
        ↓
Choose branch or use default
        ↓
Start indexing
        ↓
Cloning → Discovering → Parsing → Relationships → Chunking → Embedding → Validating → Ready
        ↓
Open workspace: Files / Symbols / Graph / Search / Ask
```

## Constraints

- Full re-index remains acceptable if incremental is time-boxed (see non-goals)
- Generic vs deep honesty must stay visible in import + Ask failure messages
- Ask remains budgeted; Search stays deterministic
- No private-repo OAuth required for the public demo path (Week 12 may add auth gate)

## Exit criteria

You can paste a public GitHub URL, watch stages, then search / graph / ask with citations.

## Days 1–2 shipped

- Dashboard is the primary import path: URL + optional branch → **Start indexing**
- Live stage tracker (Cloning → … → Validating → **Ready**) with workspace links on success
- Shared `ImportRepositoryPanel` on Dashboard + Jobs
- Optional `branch` on `POST /repositories/import`; empty = remote default HEAD
- Worker shallow-clones with `--branch` only when a branch was requested
- Tests: `DashboardPage.test.tsx`, updated `JobProgress` / `jobs` / `api` client tests

## Days 3–4 shipped

- Repository overview: list previously indexed repos, switch selection, language + support mix
- Dashboard **Previously indexed** list → `/repositories/:id`
- `POST /repositories/{id}/reindex` queues a full re-index (or returns the active job)
- Workspace links carry `?repo=` so Search / Ask / Graph / Files / Symbols open the selected repo
- `POST /jobs/{id}/cancel` for QUEUED/RUNNING; worker stops between stages without retry
- Failure UX: human titles/hints for `repo_too_large`, `clone_timeout`, `clone_failed`, cancel
- Partial-support honesty callout when generic/skip files are present
- Tests: `test_cancel_reindex_week11.py`, `RepositoryOverviewPage.test.tsx`, `jobErrors.test.ts`
