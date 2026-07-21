# Week 11 — Product polish (import UX + reliability)

## Status

| Day | Scope | Status |
| --- | --- | --- |
| 1–2 | Repository import UX (paste URL → live stages → Ready) | Planned |
| 3 | Repo history / switch previously indexed repos; re-index | Planned |
| 4 | Failure UX (clone limits, partial support, cancel) | Planned |
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
