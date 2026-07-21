# Ask / RAG evaluation matrix

Compares four retrieval/answer modes on the shared hybrid-weight gold fixture:

1. **hybrid** — weighted exact∥semantic only
2. **rewrite** — NL query rewrite (≤4) + multi-query RRF
3. **rerank** — RRF + mock/LLM rerank (≤40)
4. **full_rag** — rewrite + rerank + context expand + grounded Ask answer

Metrics: Recall@5, Recall@10, MRR. Full RAG also reports citation correctness and unsupported-claim rate (mock answers over retrieved evidence).

- Queries: **16**
- Embeddings: **local** (local-hash-v1, 1536 dims)
- Ask mock: **True**
- Winner (MRR → R@5 → R@10 → −latency): **full_rag**
- Ranking: full_rag, rerank, hybrid, rewrite
- Keep LLM Ask path (gate): **False**

## Overall

| Mode | Recall@5 | Recall@10 | MRR | mean latency (ms) | p95 (ms) | cite OK | unsupported |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hybrid | 0.4375 | 0.4375 | 0.3264 | 5.6 | 6.2 | — | — |
| rewrite | 0.3750 | 0.4375 | 0.3167 | 10.3 | 16.2 | — | — |
| rerank | 0.4375 | 0.4375 | 0.3368 | 6.0 | 6.6 | — | — |
| full_rag | 0.4375 | 0.4375 | 0.3375 | 32.8 | 42.9 | 1.0000 | 0.0000 |

## Identifier-style queries

| Mode | Recall@5 | Recall@10 | MRR | n |
| --- | --- | --- | --- | --- |
| hybrid | 0.8750 | 0.8750 | 0.6458 | 8 |
| rewrite | 0.7500 | 0.8750 | 0.6250 | 8 |
| rerank | 0.8750 | 0.8750 | 0.6667 | 8 |
| full_rag | 0.8750 | 0.8750 | 0.6667 | 8 |

## Natural-language queries

| Mode | Recall@5 | Recall@10 | MRR | n |
| --- | --- | --- | --- | --- |
| hybrid | 0.0000 | 0.0000 | 0.0069 | 8 |
| rewrite | 0.0000 | 0.0000 | 0.0083 | 8 |
| rerank | 0.0000 | 0.0000 | 0.0069 | 8 |
| full_rag | 0.0000 | 0.0000 | 0.0083 | 8 |

## Recommendation

Retrieval winner on this fixture (mock Ask): **full_rag**. Citation correctness mean=1.0. LLM Ask path does not clearly beat hybrid on MRR/Recall@5 on this fixture; keep Ask opt-in for grounded NL answers, Search/hybrid for cheap lookup. Gate: keep the LLM Ask path only when it measurably improves retrieval or citation-validated answer quality.

## Per-query (winner mode)

| id | style | rank | MRR | R@5 | R@10 | top paths |
| --- | --- | --- | --- | --- | --- | --- |
| id-ping | identifier | 3 | 0.3333 | 1 | 1 | java/com/example/users/UserController.java, java/com/example/users/UserController.java, python/pkg/service.py |
| id-UserService | identifier | 1 | 1.0000 | 1 | 1 | java/com/example/users/UserService.java, java/com/example/users/UserService.java, polyglot/c/add.c |
| id-findById | identifier | 1 | 1.0000 | 1 | 1 | java/com/example/users/UserRepository.java, java/com/example/users/UserRepository.java, java/com/example/users/UserService.java |
| id-Greeter | identifier | 1 | 1.0000 | 1 | 1 | js_ts/pkg/greeter.ts, polyglot/cpp/greeter.cpp, polyglot/ruby/greeter.rb |
| id-Hello-go | identifier | 2 | 0.5000 | 1 | 1 | polyglot/cmd/hello/main.go, polyglot/cmd/hello/main.go, polyglot/scripts/hello.sh |
| id-APIRouter | identifier | — | 0.0000 | 0 | 0 | js_ts/pages/api/hello.ts, js_ts/pkg/helpers.ts, polyglot/pom.xml |
| id-helper-ts | identifier | 2 | 0.5000 | 1 | 1 | java/util/FallbackHelper.java, js_ts/pkg/helpers.ts, js_ts/pkg/service.ts |
| id-AuthService | identifier | 1 | 1.0000 | 1 | 1 | java/com/example/auth/AuthService.java, java/com/example/auth/AuthService.java, js_ts/pkg/service.ts |
| nl-async-fetch | natural_language | — | 0.0000 | 0 | 0 | js_ts/pkg/service.ts, polyglot/db/schema.sql, js_ts/pages/api/hello.ts |
| nl-user-lookup | natural_language | — | 0.0000 | 0 | 0 | js_ts/pages/api/hello.ts, python/pkg/service.py, python/pkg/service.py |
| nl-greeter-hello | natural_language | — | 0.0000 | 0 | 0 | java/com/example/users/api/UserApi.java, polyglot/cmd/hello/main.go, polyglot/c/add.c |
| nl-go-hello-world | natural_language | — | 0.0000 | 0 | 0 | polyglot/docs/ARCHITECTURE.md, polyglot/docker-compose.yml, java/com/example/common/BaseController.java |
| nl-architecture-docs | natural_language | — | 0.0000 | 0 | 0 | java/util/FallbackHelper.java, python/pkg/service.py, js_ts/pkg/greeter.ts |
| nl-nested-inner-method | natural_language | 15 | 0.0667 | 0 | 0 | java/util/FallbackHelper.java, java/com/example/users/UserService.java, polyglot/package.json |
| nl-spring-user-api | natural_language | — | 0.0000 | 0 | 0 | python/pkg/service.py, polyglot/Cargo.toml, polyglot/cmd/hello/main.go |
| nl-fastapi-ping-route | natural_language | — | 0.0000 | 0 | 0 | js_ts/pkg/greeter.ts, java/com/example/common/BaseController.java, polyglot/ruby/greeter.rb |
