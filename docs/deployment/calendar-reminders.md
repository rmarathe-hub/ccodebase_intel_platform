# Calendar Reminders

Week 0 requires reminders around the temporary Week 12 deploy window.
Import [reminders.ics](./reminders.ics) into Apple Calendar, Google Calendar, or Outlook, then **edit the dates** to match your actual deployment week.

## Required reminders

| Reminder | When | Purpose |
| --- | --- | --- |
| Deployment evening | Evening of deploy day (Week 12 Day 2) | Confirm resources only in `rg-codeintel-demo`, replicas capped, budgets on |
| Demo-recording evening | Evening of recording day (Week 12 Day 5) | Finish recording, then start teardown the next day |
| Day after deletion | 24 hours after RG delete | First billing check |
| Seven days after deletion | 7 days after RG delete | Second billing check |
| Next billing cycle | On/after next Azure invoice date | Final billing verification |

## Suggested alert text

### Deployment evening

```text
Codeintel deploy gate: confirm rg-codeintel-demo only, min replicas 0, max 1,
Supabase Free, AI key capped. Do not leave resources overnight uncapped.
```

### Demo-recording evening

```text
Codeintel recording done? Export screenshots/video, then follow
docs/deployment/shutdown-checklist.md tomorrow.
```

### Day after deletion

```text
Codeintel billing check (+24h): Azure + Supabase. Confirm RG gone, AI key revoked.
```

### Seven days after deletion

```text
Codeintel billing check (+7d): Azure + Supabase. Investigate any unexpected charges.
```

### Next billing cycle

```text
Codeintel final billing verification: review full statement; confirm $0 ongoing.
```

## How to set dates

Placeholder dates in `reminders.ics` use a fictional deploy window:

- Deploy evening: **2026-10-06**
- Recording evening: **2026-10-09**
- +24h billing: **2026-10-11**
- +7d billing: **2026-10-17**
- Next billing cycle: **2026-11-01**

Replace these with your real Week 12 dates before relying on them.

## Import steps (quick)

**Apple Calendar:** File → Import → select `reminders.ics`

**Google Calendar:** Settings → Import & export → Import → select `reminders.ics`

**Outlook:** File → Open & Export → Import/Export → import an iCalendar (`.ics`) file
