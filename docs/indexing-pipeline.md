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

- Heuristic sections via regex/simple tokens
- Labeled `heuristic section`, never verified symbols
- Config/doc structure for chunking

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
| Deep | Symbol-aware chunks preferred |
| Generic source | Blank lines, indentation, braces, comments, max tokens, overlap if needed |
| Configuration | Top-level keys, services, deps, stages, jobs |
| Documentation | Headings and README/architecture sections |

Chunk metadata includes file path, language, start/end line, chunk type, content hash.

### 9. Build embeddings

- Local embedding provider by default
- Optional hosted provider for temporary demo only
- Store model name, vector dimension, content hash, pipeline version in pgvector-backed tables

### 10. Validate

- Snapshot consistency
- No duplicate index for same commit + pipeline version (idempotency)
- Remove stale files/symbols/sections/edges/chunks/embeddings on re-index
- Citation path readiness: every chunk/symbol addressable by file + lines

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

1. Never execute cloned repository code
2. Never claim deep accuracy for generic files
3. Never emit AI answers without validated citations for factual code claims
4. Always isolate evidence to the selected repository snapshot

## Related docs

- [product-requirements.md](./product-requirements.md)
- [system-architecture.md](./system-architecture.md)
- [security-model.md](./security-model.md)
- [language-support.md](./language-support.md)
- [non-goals.md](./non-goals.md)
