# Week 6 — Java deep support

## Status

| Day | Scope | Status |
| --- | --- | --- |
| 1 | Java tree-sitter parser (packages, imports, types, methods, fields, …) | Done |
| 2 | Qualified Java symbols (`package.Type.member`) | Done |
| 3 | Annotation analysis | Not started |
| 4 | Inheritance (`EXTENDS` / `IMPLEMENTS`) | Not started |
| 5 | Spring architecture classification | Not started |
| 6 | Java call resolution | Not started |
| 7 | Spring fixture repository | Not started |

## Artifacts

- `apps/api/app/services/java_parser.py` — tree-sitter extraction
  - Stamp: `java-treesitter`
  - Version: `6.2-treesitter`
- `apps/api/app/services/java_symbols.py` — language-scoped persist
- `apps/api/tests/fixtures/java_deep/` — class / interface / enum / record / broken
- API + UI symbol kinds: `package`, `enum`, `enum_constant`, `record`, `field`, `constructor`

### Qualified names (Day 2)

Examples:

- `com.example.auth.AuthService`
- `com.example.auth.AuthService.login`
- `com.example.auth.AuthService.AuthService` (constructor)
- Path fallback when `package` is absent: `util.FallbackHelper.add`

## Honesty

- Syntax errors fail closed (no `parser_name` stamp).
- No classpath / Maven / Gradle resolution yet.
- Annotations are captured on modifiers when present; Spring roles are Day 3–5.
- Inheritance edges and call graphs are Day 4 / Day 6.

## Git policy

Agent does not `git add` / `commit` / `push`. You review and commit manually.
