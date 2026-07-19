# Week 5 — TypeScript & JavaScript deep support

## Status

| Day | Scope | Status |
| --- | --- | --- |
| 1 | Tree-sitter parser interfaces (TS / TSX / JS / JSX) | Done |
| 2 | Symbol extraction (functions, arrows, classes, methods, interfaces, type aliases, imports, exports, React components) | Done |
| 3 | Module resolution (relative, index, named/default exports, basic TS path aliases) | Done |
| 4 | Framework metadata (Express / NestJS / Next.js / React) | Done |
| 5 | Call extraction | Not started |
| 6 | Fixture matrix | Not started |
| 7 | Mixed frontend/backend repository test | Not started |

## Artifacts

- `apps/api/app/services/js_ts_parser.py` — parsers + extraction + framework pass
  - Stamps: `typescript-treesitter` / `tsx-treesitter` / `javascript-treesitter` / `jsx-treesitter`
  - Version: `5.4-treesitter`
- `apps/api/app/services/js_ts_imports.py` — relative / index / tsconfig `paths` resolution
- `apps/api/app/services/js_ts_framework.py` — Express / Nest / Next / React heuristics
- `apps/api/app/services/js_ts_symbols.py` — persist with known modules + aliases

### Framework roles added

`express_route`, `nestjs_controller`, `nestjs_service`, `nestjs_route`, `nextjs_page`, `nextjs_route` (plus existing `react_component`).

## Honesty

- Syntax errors fail closed (no `parser_name` stamp).
- Alias resolution is tsconfig `paths` only — not full Node resolution.
- Framework roles are heuristic (decorators, Express call sites, Next path layout).
- Java remains DEEP-classified but unparsed.
- No JS/TS call graph yet (Day 5).

## Git policy

Agent does not `git add` / `commit` / `push`. You review and commit manually.
