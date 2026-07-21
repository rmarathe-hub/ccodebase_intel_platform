# Week 9 hybrid weight evaluation

Configs compared (semantic / exact):

- **exact70_sem30** — 30% semantic / 70% exact
- **exact50_sem50** — 50% semantic / 50% exact
- **exact30_sem70** — 70% semantic / 30% exact

Metrics: Recall@5, Recall@10, MRR (mean reciprocal rank of first gold hit).
Gold labels are path + content token matches on the fixture corpus.

- Queries: **16**
- Embeddings: **azure_openai** (text-embedding-3-small, 1536 dims)
- Winner (MRR → R@5 → R@10): **exact70_sem30**
- Ranking: exact70_sem30, exact50_sem50, exact30_sem70
- Product default: **exact50_sem50** (configurable `hybrid_w_exact` / `hybrid_w_semantic`)

## Overall

| Config | exact | semantic | Recall@5 | Recall@10 | MRR | mean latency (ms) | p95 latency (ms) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| exact70_sem30 | 0.70 | 0.30 | 0.8125 | 0.9375 | 0.6840 | 452.3 | 604.9 |
| exact50_sem50 | 0.50 | 0.50 | 0.8125 | 0.9375 | 0.6840 | 428.3 | 563.3 |
| exact30_sem70 | 0.30 | 0.70 | 0.8125 | 0.9375 | 0.6788 | 411.7 | 510.9 |

## Identifier-style queries

| Config | Recall@5 | Recall@10 | MRR | n |
| --- | --- | --- | --- | --- |
| exact70_sem30 | 0.8750 | 0.8750 | 0.6458 | 8 |
| exact50_sem50 | 0.8750 | 0.8750 | 0.6458 | 8 |
| exact30_sem70 | 0.8750 | 0.8750 | 0.6354 | 8 |

## Natural-language queries

| Config | Recall@5 | Recall@10 | MRR | n |
| --- | --- | --- | --- | --- |
| exact70_sem30 | 0.7500 | 1.0000 | 0.7222 | 8 |
| exact50_sem50 | 0.7500 | 1.0000 | 0.7222 | 8 |
| exact30_sem70 | 0.7500 | 1.0000 | 0.7222 | 8 |

## Recommendation

Measured winner on this fixture corpus (azure_openai embeddings, 1536 dims): **exact70_sem30**. Identifier queries favor higher exact weight; natural-language quality depends on embedding model strength. **Default remains 50/50 exact/semantic** plus path exact-match boosts as a balanced baseline; **query-aware weighting** (identifier → raise exact, NL → raise semantic) is the strongest final design.

Path boost (+0.05 when the query substring appears in the path) remains enabled for all configs (exact-match style boost).

## Per-query (winner config)

| id | style | rank | MRR | R@5 | R@10 | top paths |
| --- | --- | --- | --- | --- | --- | --- |
| id-ping | identifier | 1 | 1.0000 | 1 | 1 | python/pkg/service.py, java/com/example/users/UserController.java, java/com/example/users/UserController.java |
| id-UserService | identifier | 1 | 1.0000 | 1 | 1 | java/com/example/users/UserService.java, java/com/example/users/UserService.java, java/com/example/users/UserService.java |
| id-findById | identifier | 1 | 1.0000 | 1 | 1 | java/com/example/users/UserRepository.java, java/com/example/users/UserService.java, java/com/example/users/UserRepository.java |
| id-Greeter | identifier | 3 | 0.3333 | 1 | 1 | polyglot/ruby/greeter.rb, polyglot/cpp/greeter.cpp, js_ts/pkg/greeter.ts |
| id-Hello-go | identifier | 2 | 0.5000 | 1 | 1 | polyglot/scripts/hello.sh, polyglot/cmd/hello/main.go, polyglot/cmd/hello/main.go |
| id-APIRouter | identifier | — | 0.0000 | 0 | 0 | polyglot/docs/ARCHITECTURE.md, java/com/example/users/UserController.java, js_ts/server/app.js |
| id-helper-ts | identifier | 3 | 0.3333 | 1 | 1 | java/com/example/users/UserService.java, java/util/FallbackHelper.java, js_ts/pkg/helpers.ts |
| id-AuthService | identifier | 1 | 1.0000 | 1 | 1 | java/com/example/auth/AuthService.java, java/com/example/auth/AuthService.java, polyglot/docs/ARCHITECTURE.md |
| nl-async-fetch | natural_language | 9 | 0.1111 | 0 | 1 | js_ts/pages/api/hello.ts, js_ts/server/app.js, js_ts/pkg/service.ts |
| nl-user-lookup | natural_language | 6 | 0.1667 | 0 | 1 | java/com/example/users/api/UserApi.java, java/com/example/users/UserRepository.java, java/com/example/users/api/UserApi.java |
| nl-greeter-hello | natural_language | 1 | 1.0000 | 1 | 1 | js_ts/pkg/greeter.ts, js_ts/pkg/greeter.ts, js_ts/pkg/service.ts |
| nl-go-hello-world | natural_language | 1 | 1.0000 | 1 | 1 | polyglot/cmd/hello/main.go, polyglot/cpp/greeter.cpp, polyglot/ruby/greeter.rb |
| nl-architecture-docs | natural_language | 1 | 1.0000 | 1 | 1 | polyglot/docs/ARCHITECTURE.md, polyglot/docs/ARCHITECTURE.md, polyglot/pom.xml |
| nl-nested-inner-method | natural_language | 1 | 1.0000 | 1 | 1 | python/pkg/service.py, java/com/example/users/UserService.java, python/pkg/service.py |
| nl-spring-user-api | natural_language | 1 | 1.0000 | 1 | 1 | java/com/example/users/UserService.java, java/com/example/users/UserService.java, java/com/example/auth/AuthService.java |
| nl-fastapi-ping-route | natural_language | 2 | 0.5000 | 1 | 1 | polyglot/docs/ARCHITECTURE.md, python/pkg/service.py, js_ts/pkg/service.ts |
