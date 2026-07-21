# Indexing Pipeline

## Purpose

Turn a public GitHub repository into searchable, citable, support-level-aware intelligence without executing untrusted code.

## End-to-end flow

```text
Import repository
→ Clone
→ Discover files
→ Detect language
→ Select deep or generic processor
→ Extract structure
→ Create chunks
→ Build embeddings
→ Search
→ Answer with citations
```

## Stages (job progress)

Jobs report progress through:

```text
Queued
Cloning
Discovering files
Parsing
Building relationships
Chunking
Embedding
Validating
Completed
```

Statuses: `QUEUED` | `RUNNING` | `SUCCEEDED` | `FAILED` | `CANCELLED`

## Stage details

### 1. Import and validate

- Accept `https://github.com/{owner}/{repository}`
- Reject invalid hosts, embedded credentials, local paths, bad names
- Create `repositories` row and enqueue `indexing_jobs`

### 2. Clone

- Shallow clone into a randomized temp directory
- Enforce timeout and size limits
- Record `branch` + `commit_sha` on `repository_snapshots`
- No submodules, no installs, no execution
- Cleanup always runs

### 3. Discover files

Walk the snapshot and ignore:

```text
.git, node_modules, .venv, venv, target, dist, build,
coverage, vendor, __pycache__, generated, minified,
binary, media, large lock files
```

Persist `source_files` with path, size, line count, content hash, flags (`is_test_file`, `is_generated`, `is_vendor`).

### 4. Detect language

Extension/filename registry maps to language or content class (source, config, docs).
See [language-support.md](./language-support.md).

### 5. Select processor

```text
ProcessingStrategy:
  DEEP    = "deep"
  GENERIC = "generic"
  SKIP    = "skip"
```

Every file stores:

- `language`
- `support_level`
- `parser_name`
- `parser_version`

### 6. Extract structure

**Deep (Python / Java / TS / JS):**

- Symbols: functions, methods, classes, interfaces, imports/exports
- Qualified names
- Framework metadata (common patterns)
- Call extraction with resolution confidence
- Inheritance / implements where resolvable (Java priority)

**Generic:**

- Tree-sitter or format-native parsers extract structural candidates
- Labeled `generic_structure` / `heuristic_section`, never verified `Symbol` rows
- Optional LLM enrichment after parsing (labels/summaries only; ranges stay parser-owned)
- No regex-based structural extraction — see [language-support.md](./language-support.md)

### 7. Build relationships

Relationship types:

```text
IMPORTS, EXPORTS, CALLS, EXTENDS, IMPLEMENTS,
REFERENCES, INSTANTIATES, CONTAINS
```

Call resolution labels: `RESOLVED` | `AMBIGUOUS` | `UNRESOLVED`

Generic graphs emphasize directories and marked inferred edges.

### 8. Create chunks

| Support | Chunking |
| --- | --- |
| Deep | Symbol-aware chunks from existing deep parsers (Python / Java / JS / TS) |
| Generic source | Syntax-tree node boundaries (Tree-sitter); token limits only after AST split |
| Configuration | Format-native parsers (JSON, YAML, TOML, XML, Dockerfile, …) |
| Documentation | Markdown / document AST heading hierarchy |

Chunk metadata includes file path, language, support level, start/end line, chunk type,
content hash, extraction method, parser provenance, and optional LLM provenance.

Oversized nodes split by child syntax nodes first; deterministic line windows only as
a labeled final fallback (`extraction_method` records the fallback).

### 9. Optional LLM enrichment + embeddings

- Parser ranges are authoritative; LLM never alters boundaries or creates verified symbols
- Enrichment is opt-in, budget-capped, cached, and skipped when disabled / over budget
- Exact search must work with enrichment off
- Embeddings: worker Embedding stage persists `chunk_embeddings` (pgvector);
  local-hash provider is the CI/default; Azure optional.
  Search modes: `exact` (default), `semantic`, `hybrid` (Week 9 Days 3–4).
  Worker Validating stage checks citation readiness + embedding consistency (Day 5).
  Functional Search UI: Week 9 Day 6. Ask / LLM RAG: Week 10.

### 10. Validate

- Snapshot consistency
- No duplicate index for same commit + pipeline version (idempotency)
- Remove stale files/symbols/sections/edges/chunks/embeddings on re-index
- Citation path readiness: every chunk/symbol addressable by file + lines
- LLM structured output validated against schema + source ranges before persist
## Incremental indexing (Week 11)

Compare:

```text
commit SHA, file path, content hash, parser version, embedding version
```

Reprocess only added/modified files and relationship-affected files when implemented.
Full re-index remains the correct fallback.

## Downstream consumers

| Consumer | Uses |
| --- | --- |
| Search | Exact, symbol/section, semantic, hybrid |
| Graphs | Modules, packages, directories, callers/callees |
| Ask | Retrieval tools + citation validation |
| UI | Jobs progress, overview stats, Monaco jumps |

## Safety invariants

1. Never execute cloned repository code, install its deps, or run its build tools
2. Never claim deep accuracy for generic files
3. Never emit AI answers without validated citations for factual code claims
4. Always isolate evidence to the selected repository snapshot
5. Never use regex for structural extraction (chunk / section / config / heading boundaries)
6. Never let LLM output override parser-derived ranges

## Related docs

- [product-requirements.md](./product-requirements.md)
- [system-architecture.md](./system-architecture.md)
- [security-model.md](./security-model.md)
- [language-support.md](./language-support.md)
- [non-goals.md](./non-goals.md)
