# Week 5 — TypeScript & JavaScript deep support

## Status

| Day | Scope | Status |
| --- | --- | --- |
| 1 | Tree-sitter parser interfaces (TS / TSX / JS / JSX) | Done |
| 2 | Symbol extraction (functions, arrows, classes, methods, interfaces, type aliases, imports, exports, React components) | Done |
| 3 | Module resolution (aliases, index files) | Not started |
| 4 | Framework metadata (Express / Nest / Next) | Not started (React component heuristic started in Day 2) |
| 5 | Call extraction | Not started |
| 6 | Fixture matrix | Not started |
| 7 | Mixed frontend/backend repository test | Not started |

## Day 1–2 artifacts

- `apps/api/app/services/js_ts_parser.py` — parser classes + extraction
  - `TypeScriptTreeSitterParser` → `typescript-treesitter`
  - `TSXTreeSitterParser` → `tsx-treesitter`
  - `JavaScriptTreeSitterParser` → `javascript-treesitter`
  - `JSXTreeSitterParser` → `jsx-treesitter`
  - Stamp version: `5.2-treesitter`
- `apps/api/app/services/js_ts_symbols.py` — persist JS/TS symbols (language-scoped replace)
- Worker runs Python persist then JS/TS persist
- Symbol kinds extended: `interface`, `type_alias`, `export`
- React PascalCase + JSX → `framework_role=react_component` (heuristic)

## Honesty

- Syntax errors fail closed (no `parser_name` stamp).
- Java remains DEEP-classified but unparsed.
- No JS/TS call graph yet (Day 5).
- No TS path-alias resolution yet (Day 3).

## Git policy

Agent does not `git add` / `commit` / `push`. You review and commit manually.
