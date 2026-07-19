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
| 7 | Spring fixture repository | Done |

## Artifacts

- `apps/api/app/services/java_parser.py` — tree-sitter extraction
  - Stamp: `java-treesitter`
  - Version: `6.6-treesitter`
- `apps/api/app/services/java_framework.py` — annotations + architecture pass
- `apps/api/app/services/java_inheritance.py` — EXTENDS / IMPLEMENTS resolution
- `apps/api/app/services/java_calls.py` — call sites with confidence
- `apps/api/app/services/java_symbols.py` — symbols + relations + calls
- `symbol_relations` table + `GET /api/v1/repositories/{id}/relations`
- `apps/api/tests/fixtures/spring_fixture/` — full Spring stack fixture
  - `Application`, `SecurityConfig`, `UserController`, `UserService`,
    `UserServiceImpl`, `UserRepository`, `UserEntity`
- `apps/api/tests/test_spring_fixture.py` — discovery / roles / relations / calls / API

### Framework roles

Annotation / naming: `spring_rest_controller`, `spring_controller`, `spring_service`,
`spring_repository`, `spring_component`, `spring_configuration`, `spring_entity`,
`spring_route`, `spring_interface`, `spring_implementation`

`@SpringBootApplication` maps to `spring_configuration` (same family as `@Configuration`).

### Inheritance (Day 4)

Resolve via FQN, import leaf, same-package, or unique project simple name.

### Architecture (Day 5)

Cross-file pass pairs IMPLEMENTS edges, tags interfaces / implementations, naming fallbacks.

### Calls (Day 6)

`helper()`, `this.helper()`, `repo.findById()`, `Type.method()` with field-type injection heuristics.

### Spring fixture (Day 7)

End-to-end matrix over a realistic Spring Boot slice: REST controller → service
interface → `@Service` impl → `@Repository` → `@Entity`, plus `@Configuration`
and `@SpringBootApplication`. Worker pipeline indexes the same fixture.

## Honesty

- Syntax errors fail closed (no `parser_name` stamp).
- No classpath / Maven / Gradle resolution.
- Annotation / architecture / call resolution are heuristics — not javac.
- Fixture is illustrative Spring shape, not a runnable Maven project.

## Git policy

Agent does not `git add` / `commit` / `push`. You review and commit manually.
