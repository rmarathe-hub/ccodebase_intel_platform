# Cost Policy

Hard rules for the Codebase Intelligence Platform temporary cloud deployment.
These limits are non-negotiable for Weeks 1–12.

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
| Unrestricted public AI calls | prohibited |

## Local-first default (Weeks 1–11)

Everything runs locally at expected platform cost **$0**:

- Docker Compose
- PostgreSQL with pgvector
- FastAPI
- React
- Background worker
- Local embeddings
- Ollama

No cloud resources may be created for development, indexing experiments, or CI.

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
