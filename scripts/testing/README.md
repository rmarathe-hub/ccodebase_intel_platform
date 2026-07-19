# Testing scripts (Week 0–2)

All scripts assume:

- `apps/api/.venv` exists (`make api-install`)
- Postgres is reachable for integration/full/coverage suites (default `localhost:5434`)
- `apps/web/node_modules` exists (`make web-install`)

| Script | Purpose |
| --- | --- |
| `run-fast-unit.sh` | Pure unit tests without Postgres |
| `run-integration.sh` | Postgres-backed API/job/DB tests |
| `run-slow.sh` | Performance smoke (`pytest -m slow`) |
| `run-coverage.sh` | Full API suite + branch coverage |
| `run-full.sh` | API pytest serial (random order) + web vitest. Optional `FULL_PARALLEL=1` uses xdist `--dist loadgroup` (still prefer serial on shared DB) |
| `run-mutation.sh` | Focused mutmut run |
| `run-frontend.sh` | Vitest only |

Example:

```bash
chmod +x scripts/testing/*.sh
./scripts/testing/run-fast-unit.sh
./scripts/testing/run-integration.sh
./scripts/testing/run-coverage.sh
./scripts/testing/run-full.sh
```

Do not run Azure, Redis, Kubernetes, or paid services from these scripts.
