# Week 12 — Temporary demo deploy + shutdown

## Status

| Day | Scope | Status |
| --- | --- | --- |
| 1–2 | Deploy API + worker + web (cost policy: min replicas 0) | Planned |
| 3 | Wire Azure embeddings + chat for Ask (kill switches on) | Planned |
| 4 | Auth or private access for Ask (no uncapped public Q&A) | Planned |
| 5 | Record demo: import → search → graph → Ask with citations | Planned |
| 6 | Export artifacts; set kill switches; revoke keys | Planned |
| 7 | Shutdown checklist: delete `rg-codeintel-demo` | Planned |

## Theme

Short-lived demo in Azure resource group **`rg-codeintel-demo`**, then delete.

## Hard rules

- Follow [deployment/cost-policy.md](./deployment/cost-policy.md)
- Follow [deployment/shutdown-checklist.md](./deployment/shutdown-checklist.md)
- Max temporary deploy window: 7 days
- Uncapped public Ask is prohibited
- Revoke Azure keys after recording; do not leave paid resources running

## Demo script (target)

1. Paste public GitHub URL  
2. Watch indexing stages through Validating → Ready  
3. Exact + hybrid search with citations  
4. Graph (module / directory / callers where deep)  
5. Ask one NL question with grounded citations  
6. Show “not enough evidence” honesty on a deliberately unsupported question  

## After demo

Delete `rg-codeintel-demo`, disable deploy workflows, verify billing lag is not new usage.
