# Language Support Contract

This project supports two explicit levels of repository intelligence.
Every indexed file must record which level applied and which parser produced it.

## Support levels

| Level | Value | Promise |
| --- | --- | --- |
| Deep | `deep` | Full structural analysis where implemented |
| Generic | `generic` | Parser-derived searchable structure without verified deep semantics |
| Skip | `skip` | Not indexed (ignored, binary, generated, vendor, oversized, etc.) |

## Per-file metadata (required)

Every indexed file stores at least:

| Field | Purpose |
| --- | --- |
| `language` | Detected language or content class |
| `support_level` | `deep`, `generic`, or `skip` |
| `parser_name` | Parser or pipeline that processed the file |
| `parser_version` | Version of that parser/pipeline |

UI, search results, graphs, and AI answers must not present generic/heuristic results as verified deep symbols.

---

## Deep code intelligence

These languages receive full structural analysis:

- Python
- Java
- TypeScript
- JavaScript

### Deep support includes

- Symbol extraction
- Functions and methods
- Classes and interfaces
- Imports and exports
- Caller/callee relationships
- Inheritance and implementations (especially Java)
- Framework-aware architecture detection (common patterns only)
- Symbol-aware chunking (from existing AST / tree-sitter symbols)
- Exact definition and reference navigation
- File-and-line citations

Deep languages **must not** be routed through the generic Tree-sitter chunk
pipeline. Chunks for these languages are derived from verified deep symbols.

### Deep languages and expected parsers

| Language | Typical parser name (illustrative) |
| --- | --- |
| Python | `python-ast` |
| Java | `java-treesitter` |
| TypeScript / TSX | `typescript-treesitter` / `tsx-treesitter` |
| JavaScript / JSX | `javascript-treesitter` / `jsx-treesitter` |

Exact parser package names may evolve; `parser_name` + `parser_version` on each file are the source of truth.

---

## Generic repository intelligence

These languages and content types receive broad searchable support:

- C
- C++
- C#
- Go
- Rust
- Ruby
- PHP
- Kotlin
- Swift
- Scala
- Shell
- SQL
- HTML
- CSS
- Configuration files
- Documentation files

### Generic support includes

- Language detection
- File browsing
- Syntax highlighting
- Exact-text search over parser-derived chunks
- Optional semantic search (later) and optional LLM enrichment
- Parser-derived structural chunks (Tree-sitter or format-native parsers)
- File / repository summaries (deterministic always; LLM optional)
- Citation-backed explanations grounded in parser ranges
- Directory and configuration analysis
- Repository statistics

Parser-derived generic sections are labeled:

```text
support_level = generic
verified_deep = false
chunk_type = generic_structure | heuristic_section | …
```

Tree-sitter syntax extraction for generic languages does **not** qualify as
verified deep semantic analysis.

### First-cut generic parsers (Week 7)

| Content | Parser approach |
| --- | --- |
| Go, Rust, C, C++, C#, Ruby, Shell | Tree-sitter (maintained grammars) |
| SQL | SQLGlot when dialect supported; else Tree-sitter SQL |
| JSON / package.json | Standard JSON parser |
| YAML (Actions, compose) | Safe YAML parser |
| TOML / Cargo | `tomllib` or maintained TOML parser |
| XML / Maven | Hardened XML (no external entities) |
| Dockerfile | Maintained Dockerfile parser |
| Markdown | Markdown AST (not regex headings) |

Remaining generic languages (PHP, Kotlin, Swift, Scala, …) use the same
parser interface and ship afterward.

### Generic support does **not** promise

- Accurate function-call graphs
- Complete symbol resolution
- Inheritance graphs
- Framework-specific dependency resolution
- Compiler-level static analysis
- Verified `Symbol` rows for generic files

### Public messaging for generic languages

> Semantic search, file exploration and citation-backed explanations are supported. Complete symbol and call-graph analysis is currently limited to deeply supported languages.

---

## Parsing architecture (authority)

```text
1. Deterministic parser / syntax tree
2. Parser-derived source boundaries (byte/line ranges)
3. Optional LLM semantic enrichment
4. Schema validation
5. Source-range validation
6. Persistent provenance + confidence
7. Fail closed
```

The deterministic parser is authoritative for ranges, nesting, file structure,
configuration keys, Markdown headings, and citation locations.

The LLM may add labels, summaries, probable roles, entry-point likelihood, and
architecture interpretation. It must **never** invent ranges, alter boundaries,
or create verified deep symbols.

### Regex policy

- **Forbidden** for syntax parsing, chunk boundaries, section detection, brace
  matching, Markdown headings, config/SQL structure, or symbol extraction.
- **Allowed** only for trivial non-structural checks (simple validation,
  extension maps, allowlists, filename candidate hints such as `main.go`).
- Filename hints are evidence **candidates**, not verified entry points.
- Prefer string comparisons, suffix maps, enums, and parser APIs when practical.

### Optional LLM enrichment

- Opt-in; disabled by default and in CI
- Not required for deterministic indexing or exact search
- Prioritize entry points, top-level decls, README/architecture, config/build
- Strict structured output + evidence validation
- Budget / cache / kill-switch controls — see [deployment/cost-policy.md](./deployment/cost-policy.md)

---

## Routing rules

```text
Detect language / content class
        │
        ▼
   In deep set? ──yes──► DEEP processor (existing parsers → symbols → symbol chunks)
        │
        no
        ▼
   Textual & allowed? ──yes──► GENERIC processor (Tree-sitter / format parsers → chunks)
        │
        no
        ▼
       SKIP
```

### Processing strategy enum

```text
DEEP    = "deep"
GENERIC = "generic"
SKIP    = "skip"
```

## Product display matrix

```text
Deep code intelligence:
Python, Java, TypeScript and JavaScript

Generic repository intelligence:
C, C++, C#, Go, Rust, Ruby, PHP, Kotlin, Swift, Scala,
Shell, SQL, HTML/CSS, configuration and documentation files
```

UI labels must distinguish categories such as:

- Verified deep symbol
- Parser-derived generic structure
- LLM-enriched heuristic
- Raw text fallback

## Honesty rules

1. Verified deep symbols and generic parser-derived / LLM-enriched sections must be distinguishable in APIs and UI.
2. AI answers must set `support_level` accurately for the evidence used.
3. Graphs for generic repositories are directory/config/build oriented and must mark inferred edges.
4. Do not claim LSP or compiler accuracy for any language in marketing or README claims.
5. Do not execute imported repository code, install its dependencies, or run its build tools.
