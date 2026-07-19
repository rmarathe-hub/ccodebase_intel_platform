# Testing scripts (Week 0–4)

All scripts assume:

- `apps/api/.venv` exists (`make api-install`)
- Postgres is reachable for integration/full/coverage suites (default `localhost:5434`)
- `apps/web/node_modules` exists (`make web-install`)

| Script | Purpose |
| --- | --- |
| `run-fast-unit.sh` | Pure unit tests without Postgres |
| `run-parser.sh` | Python AST / framework / calls matrices |
| `run-security.sh` | URL, security boundaries, cost/doc contracts |
| `run-integration.sh` | Postgres-backed API/job/DB/worker tests |
| `run-worker-integration.sh` | Worker pipeline + Week 3–4 API filters |
| `run-slow.sh` | Performance smoke (`pytest -m slow`) |
| `run-coverage.sh` | Full API suite + branch coverage |
| `run-full.sh` | API pytest serial (random order) + web vitest |
| `run-mutation.sh` | Focused mutmut run (URL/language/framework/calls) |
| `run-frontend.sh` | Vitest only |
| `run-frontend-full.sh` | typecheck + lint + vitest + production build |

Example:

```bash
chmod +x scripts/testing/*.sh
./scripts/testing/run-fast-unit.sh
./scripts/testing/run-parser.sh
./scripts/testing/run-security.sh
./scripts/testing/run-integration.sh
./scripts/testing/run-coverage.sh
./scripts/testing/run-frontend-full.sh
./scripts/testing/run-full.sh
```

Do not run Azure, Redis, Kubernetes, or paid services from these scripts.
Never `git add` / `commit` / `push` from these scripts.
