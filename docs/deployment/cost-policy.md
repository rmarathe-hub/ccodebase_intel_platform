# Cost Policy

Hard rules for the Codebase Intelligence Platform temporary cloud deployment
and for optional paid LLM enrichment during local development.

## Hard limits

| Rule | Value |
| --- | --- |
| Maximum deployment duration | 7 days |
| Maximum intended spend | $10 |
| Azure minimum replicas | 0 |
| Azure maximum API replicas | 1 |
| Azure maximum worker replicas | 1 |
| Paid Redis | prohibited |
| Paid managed PostgreSQL | prohibited |
| Virtual machines | prohibited |
| Kubernetes | prohibited |
| Unrestricted public imports | prohibited |
| Unrestricted / uncapped public AI calls | prohibited |

## Local-first default (Weeks 1–11)

Deterministic indexing (clone, discover, parse, chunk, exact search) runs locally
at expected platform cost **$0** when LLM enrichment is disabled:

- Docker Compose
- PostgreSQL with pgvector
- FastAPI
- React
- Background worker

No Azure resources may be created for development, indexing experiments, or CI.
CI must never require a paid API call.

## Optional paid LLM enrichment (local / demo)

Paid provider APIs (Azure OpenAI primary; OpenAI, Anthropic, or another
configured provider) are **permitted only when explicitly enabled** for semantic
enrichment of parser-derived chunks and summaries. See [llm-enrichment.md](../llm-enrichment.md).

Rules:

| Rule | Requirement |
| --- | --- |
| Default | Enrichment **disabled** (`LLM_ENRICHMENT_ENABLED=false`) |
| CI | Enrichment **disabled**; providers mocked |
| Deterministic path | Must succeed with enrichment off |
| Exact search | Must not depend on LLM |
| Opt-in | Environment / settings flag only (opt-in; never default-on) |
| Batching | Related prioritized chunks per request — **not** one call per chunk |
| Priority | Summaries, README/docs, top-level decls, entry candidates, config/build |
| Caps | Max requests, tokens, and estimated cost **per indexing job** |
| Daily budget | Configurable project daily spend ceiling |
| Kill switch | Immediate disable without deleting deterministic index |
| Caching | Cache by content hash + parser version + prompt version + model/deployment |
| Over budget | Keep parser-derived chunks; skip enrichment only |
| Keys | Never hardcoded; never logged; never committed |
| Primary provider | Azure OpenAI when `LLM_PROVIDER=azure_openai` |
| LangChain | Thin adapter only; no agents for indexing enrichment |

Uncapped bulk enrichment and unrestricted public Ask endpoints remain prohibited.

Local Ollama (or similar) may be used when configured; it does not replace the
requirement that hosted keys stay capped and revocable.

## Temporary cloud window (Week 12 only)

Deploy only after the application is complete and the billing gate passes.

Allowed resources (must all live in one resource group):

- Resource group: `rg-codeintel-demo`
- Azure Container Registry
- Azure Container Apps (API + worker, min replicas = 0, max = 1)
- Required logging resource only if needed for Container Apps
- Static frontend hosting
- Supabase Free (or equivalent free Postgres)
- Tightly limited AI API key if needed for the recording

## Prohibited during the demo window

- Any resource outside `rg-codeintel-demo`
- Scale-out beyond 1 replica for API or worker
- Always-on replicas (minimum must remain 0)
- Paid Redis, paid managed Postgres, VMs, AKS/Kubernetes
- Public, unauthenticated repository import endpoints
- Uncapped hosted AI usage
- Long-lived production secrets retained after teardown

## Billing gate (must pass before deploy)

- [ ] Eligible Azure spending limit remains enabled (if available)
- [ ] Subscription budget exists
- [ ] Resource-group budget exists for `rg-codeintel-demo`
- [ ] Billing alerts reach an active email
- [ ] Dedicated Azure resource group is ready and empty (or only intended resources)
- [ ] API minimum replicas = 0, maximum = 1
- [ ] Worker minimum replicas = 0, maximum = 1
- [ ] Supabase remains Free
- [ ] AI key is project-specific with a minimized usage cap
- [ ] Shutdown reminders are scheduled

## After recording

1. Revoke the AI key.
2. Disable deployment workflows.
3. Export benchmarks and screenshots.
4. Delete the Azure resource group `rg-codeintel-demo`.
5. Delete or pause Supabase.
6. Verify billing after 24 hours, seven days, and the next billing cycle.

See [shutdown-checklist.md](./shutdown-checklist.md).

## Spend breach response

If spend approaches or exceeds the $10 intended maximum:

1. Stop the demo immediately.
2. Scale Container Apps to 0 / stop running revisions.
3. Revoke AI keys.
4. Delete `rg-codeintel-demo`.
5. Confirm no orphaned resources remain outside the resource group.
6. Document the cause in the project README limitations section.
