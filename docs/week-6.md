# Week 6 — Java deep support

## Status

| Day | Scope | Status |
| --- | --- | --- |
| 1 | Java tree-sitter parser (packages, imports, types, methods, fields, …) | Done |
| 2 | Qualified Java symbols (`package.Type.member`) | Done |
| 3 | Annotation analysis | Done |
| 4 | Inheritance (`EXTENDS` / `IMPLEMENTS`) | Done |
| 5 | Spring architecture classification | Done |
| 6 | Java call resolution | Done |
| 7 | Spring fixture repository | Not started |

## Artifacts

- `apps/api/app/services/java_parser.py` — tree-sitter extraction
  - Stamp: `java-treesitter`
  - Version: `6.6-treesitter`
- `apps/api/app/services/java_framework.py` — annotations + architecture pass
- `apps/api/app/services/java_inheritance.py` — EXTENDS / IMPLEMENTS resolution
- `apps/api/app/services/java_calls.py` — call sites with confidence
- `apps/api/app/services/java_symbols.py` — symbols + relations + calls
- `symbol_relations` table + `GET /api/v1/repositories/{id}/relations`

### Framework roles

Annotation / naming: `spring_rest_controller`, `spring_controller`, `spring_service`,
`spring_repository`, `spring_component`, `spring_configuration`, `spring_entity`,
`spring_route`, `spring_interface`, `spring_implementation`

### Inheritance (Day 4)

Resolve via FQN, import leaf, same-package, or unique project simple name.

### Architecture (Day 5)

Cross-file pass pairs IMPLEMENTS edges, tags interfaces / implementations, naming fallbacks.

### Calls (Day 6)

`helper()`, `this.helper()`, `repo.findById()`, `Type.method()` with field-type injection heuristics.

## Honesty

- Syntax errors fail closed (no `parser_name` stamp).
- No classpath / Maven / Gradle resolution.
- Annotation / architecture / call resolution are heuristics — not javac.
- Day 7 ships a fuller Spring fixture repository.

## Git policy

Agent does not `git add` / `commit` / `push`. You review and commit manually.
