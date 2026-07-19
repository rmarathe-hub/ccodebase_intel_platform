# Language Support Contract

This project supports two explicit levels of repository intelligence.
Every indexed file must record which level applied and which parser produced it.

## Support levels

| Level | Value | Promise |
| --- | --- | --- |
| Deep | `deep` | Full structural analysis where implemented |
| Generic | `generic` | Broad searchable support without compiler-level static analysis |
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
- Symbol-aware chunking
- Exact definition and reference navigation
- File-and-line citations

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
- Exact-text search
- Semantic search
- Line-based / heuristic chunking
- File summaries
- Citation-backed explanations
- Directory and configuration analysis
- Repository statistics
- Heuristic section detection (labeled, not verified symbols)

### Generic support does **not** initially promise

- Accurate function-call graphs
- Complete symbol resolution
- Inheritance graphs
- Framework-specific dependency resolution
- Compiler-level static analysis

### Public messaging for generic languages

> Semantic search, file exploration and citation-backed explanations are supported. Complete symbol and call-graph analysis is currently limited to deeply supported languages.

---

## Routing rules

```text
Detect language / content class
        │
        ▼
   In deep set? ──yes──► DEEP processor
        │
        no
        ▼
   Textual & allowed? ──yes──► GENERIC processor
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

## Honesty rules

1. Verified deep symbols and generic heuristic sections must be distinguishable in APIs and UI.
2. AI answers must set `support_level` accurately for the evidence used.
3. Graphs for generic repositories are directory/config/build oriented and must mark inferred edges.
4. Do not claim LSP or compiler accuracy for any language in marketing or README claims.
