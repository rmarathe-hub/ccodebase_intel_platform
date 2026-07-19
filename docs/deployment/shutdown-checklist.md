# Shutdown Checklist

Use this checklist at the end of the Week 12 temporary deployment.
Target resource group: **`rg-codeintel-demo`**.

Complete every item. Do not skip billing verification.

## Pre-shutdown exports

Before deleting anything, export evidence locally:

- [ ] Evaluation results and benchmark numbers
- [ ] Screenshots and demo video / GIFs
- [ ] Schema / migration notes needed for docs
- [ ] Any production logs needed for documentation (no secrets)

## Revoke access and secrets

- [ ] Revoke AI API key
- [ ] Remove production secrets from Azure
- [ ] Remove production secrets from GitHub (Actions secrets / variables)
- [ ] Verify the revoked AI key fails when called

## Disable recreation

- [ ] Disable deployment workflow
- [ ] Disable scheduled jobs / cron workflows
- [ ] Remove repository webhooks (if any)
- [ ] Remove or invalidate Azure deploy credentials
- [ ] Confirm Terraform / deploy scripts cannot run automatically

## Delete Azure

- [ ] Delete Azure resource group `rg-codeintel-demo`
- [ ] Verify registry deletion (ACR)
- [ ] Verify Container Apps deletion
- [ ] Verify logging-resource deletion (Log Analytics / App Insights if created)
- [ ] Search Azure for leftover project resources by name:
  - project name / `codeintel`
  - Container Apps
  - Container Registry
  - Log Analytics
  - Application Insights
  - Storage
  - Managed environments
- [ ] Confirm nothing remains outside the deleted resource group

## Handle Supabase

- [ ] Delete or pause Supabase
- [ ] If kept: confirm Free plan only; no paid add-ons

## Billing verification

- [ ] Check billing after 24 hours
- [ ] Check billing after 7 days
- [ ] Check next billing statement

## Sign-off

| Field | Value |
| --- | --- |
| Shutdown date (UTC) | |
| Person who deleted the RG | |
| AI key revoked? | yes / no |
| Supabase deleted or paused? | deleted / paused |
| Orphan resources found? | none / list |
| Notes | |

When complete, the Definition of Done items for Azure teardown, AI key revocation, Supabase Free/deleted, and final billing verification may be checked.
