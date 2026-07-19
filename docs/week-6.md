# Week 6 — Java deep support

## Status

| Day | Scope | Status |
| --- | --- | --- |
| 1 | Java tree-sitter parser (packages, imports, types, methods, fields, …) | Done |
| 2 | Qualified Java symbols (`package.Type.member`) | Done |
| 3 | Annotation analysis | Done |
| 4 | Inheritance (`EXTENDS` / `IMPLEMENTS`) | Done |
| 5 | Spring architecture classification | Not started |
| 6 | Java call resolution | Not started |
| 7 | Spring fixture repository | Not started |

## Artifacts

- `apps/api/app/services/java_parser.py` — tree-sitter extraction
  - Stamp: `java-treesitter`
  - Version: `6.4-treesitter`
- `apps/api/app/services/java_framework.py` — Spring annotation → role heuristics
- `apps/api/app/services/java_inheritance.py` — EXTENDS / IMPLEMENTS resolution
- `apps/api/app/services/java_symbols.py` — language-scoped persist (symbols + relations)
- `symbol_relations` table + `GET /api/v1/repositories/{id}/relations`
- `apps/api/tests/fixtures/java_deep/` — auth types + Spring users sample

### Framework roles (Day 3)

`spring_rest_controller`, `spring_controller`, `spring_service`, `spring_repository`,
`spring_component`, `spring_configuration`, `spring_entity`, `spring_route`

### Inheritance (Day 4)

Resolve via FQN, import leaf, same-package, or unique project simple name.
Confidence: `resolved` | `ambiguous` | `unresolved`.

## Honesty

- Syntax errors fail closed (no `parser_name` stamp).
- No classpath / Maven / Gradle resolution.
- Annotation roles are name heuristics (not full Spring Boot wiring).
- Inheritance resolution is heuristic; Day 5 may refine architecture pairing.
- Call graphs are Day 6.

## Git policy

Agent does not `git add` / `commit` / `push`. You review and commit manually.
