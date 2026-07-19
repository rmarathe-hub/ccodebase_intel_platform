# Security Model

## Goals

1. Safe handling of untrusted public repository content
2. No leakage of host secrets, tokens, or credentials into answers or logs
3. Controlled import surface (no unrestricted public abuse)
4. Cost and compute bounds that prevent runaway cloud spend

## Trust boundaries

| Zone | Trust | Notes |
| --- | --- | --- |
| Operator laptop / local Docker | Trusted | Weeks 1–11 default |
| Imported GitHub repository | Untrusted | Treated as evidence only |
| AI model (Ollama / hosted) | Untrusted output | Must be citation-validated |
| Temporary Azure / Supabase | Semi-trusted | Short-lived; secrets revoked on teardown |

## Repository import controls

Allowed:

- Public HTTPS GitHub URLs: `https://github.com/{owner}/{repository}`

Rejected:

- Invalid hosts
- Embedded credentials
- Local filesystem paths
- Unsupported protocols
- Malformed repository names

Clone safeguards:

- Shallow clone only
- Randomized temporary directory
- Clone timeout
- Repository size limit
- No submodule checkout initially
- No package installation
- No execution of repository code
- Automatic cleanup of clone directories

## Untrusted code as evidence

Repository files may contain prompt-injection text, fake instructions, or credential-looking strings.

Rules:

- Files are **evidence only**, never executable instructions for the platform
- Prompts must instruct the model to ignore directive-like content inside code/docs
- Answers must not invent file paths or line ranges
- Citations must validate against retrieved evidence

## Secrets never exposed

Never return or include in model context / responses:

- Environment variables from the host or containers
- GitHub tokens
- API keys
- Host filesystem paths outside the cloned snapshot
- Database credentials
- Azure / Supabase secrets
- Files outside the imported repository snapshot

## AI provider controls

- Deterministic indexing and exact search must work with enrichment **disabled**
- Optional paid LLM enrichment is opt-in, budget-capped, cached, and CI-mocked
  (see [deployment/cost-policy.md](./deployment/cost-policy.md))
- Local Ollama (or similar) may be configured for Ask / enrichment when desired
- Hosted AI keys (local enrichment or Week 12) must be:
  - Project-specific
  - Usage-capped
  - Never hardcoded or logged
  - Revoked immediately after the temporary demo recording
  - Removed from Azure and GitHub secrets after teardown

## API and abuse limits (product policy)

- Unrestricted public imports: **prohibited**
- Unrestricted / uncapped public AI calls: **prohibited**
- Demo deployments should require authentication or private access during the short live window
- Rate limits and repository size caps apply to import, enrichment, and Ask

## Job and worker isolation

- Workers process one claimed job at a time under a lease
- Failed jobs do not leave credentials on disk
- Temporary clone directories are removed on success and failure
- Cross-repository isolation: queries never mix another repository's evidence into answers

## Data retention

- Local development databases may be reset with `make reset-db`
- Temporary cloud data is exported only as needed for documentation, then deleted with the resource group
- Do not retain production secrets after teardown

## Cloud cost as a security control

See [deployment/cost-policy.md](./deployment/cost-policy.md) and [deployment/shutdown-checklist.md](./deployment/shutdown-checklist.md).

Runaway spend is treated as an operational security failure:

- Resource group isolation: `rg-codeintel-demo`
- Min replicas 0, max 1
- Max deploy duration 7 days
- Max intended spend $10
- Mandatory post-delete billing checks

## Logging

- Log job stages and errors without dumping full file contents by default
- Redact tokens and Authorization headers
- Do not log raw model system prompts that include secrets

## Summary policy

```text
Validate URL → shallow clone in temp → never execute → index as data
→ retrieve evidence → draft answer → validate citations → respond
→ revoke keys → delete cloud → verify billing
```
