# Product Requirements

## Product name

Codebase Intelligence Platform

## Problem

Engineers waste time navigating unfamiliar repositories: finding where authentication lives, how a request flows to persistence, which callers touch a worker, and whether an AI answer is grounded in real code. Existing search is either keyword-only or LLM-only without structural truth.

## Solution

Import a public GitHub repository, index it asynchronously, and provide:

1. Structural intelligence for deeply supported languages
2. Broad searchable intelligence for other textual languages
3. Hybrid retrieval (exact + semantic + symbol/graph signals)
4. Citation-validated AI answers with file-and-line evidence

## Core user workflow

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

## Primary users

- Engineers exploring unfamiliar codebases
- Reviewers preparing demos / portfolio evaluations
- Developers asking architecture and dependency questions

## Language support (contract)

See [language-support.md](./language-support.md).

| Level | Languages |
| --- | --- |
| Deep | Python, Java, TypeScript, JavaScript |
| Generic | C, C++, C#, Go, Rust, Ruby, PHP, Kotlin, Swift, Scala, Shell, SQL, HTML, CSS, configuration, documentation |

## Functional requirements

### Repository import

- Accept public GitHub HTTPS URLs only: `https://github.com/{owner}/{repository}`
- Validate host, reject credentials, local paths, and unsupported protocols
- Clone shallowly with size/timeout limits
- Never execute repository code, install packages, or check out submodules initially
- Process asynchronously with durable jobs and progress stages

### Indexing

- Discover and filter files (ignore vendor, build, binary, generated, oversized)
- Route each file to `deep`, `generic`, or `skip`
- Persist per-file `language`, `support_level`, `parser_name`, `parser_version`
- Deep: symbols, relationships, framework metadata, symbol-aware chunks from existing parsers
- Generic: Tree-sitter / format-native structural chunks (not verified symbols); optional LLM labels
- No regex-based structural extraction; parser ranges are authoritative

### Search

- Exact-text search over persisted chunks (must work with LLM enrichment disabled)
- Symbol and generic-structure search (clearly distinguished)
- Semantic search via embeddings (later stage; local default when added)
- Hybrid ranking across vector, exact, path, graph, and type signals
- Filters: repository, snapshot, language, support level, path, chunk type, extraction method, test/docs/config

### Graphs

- Deep: module/package graphs, callers/callees, inheritance/implements where resolved
- Generic: directory hierarchy and clearly marked inferred edges
- Relationship types: IMPORTS, EXPORTS, CALLS, EXTENDS, IMPLEMENTS, REFERENCES, INSTANTIATES, CONTAINS

### Ask (AI answers)

- Optional LLM providers behind `LLMProvider` (Azure OpenAI primary when enabled)
- LangChain only as thin orchestration; no free-running agents for indexing
- Structured answers with citations: file, start/end line, claim
- Validate citations against retrieved evidence before display
- Surface support-level and limitations honestly
- Treat repository content as evidence only (prompt-injection defenses)
- Never invent source ranges or promote generic evidence to verified deep

### UI surfaces

- Dashboard
- Repository overview
- Search
- Ask
- Symbols
- Graph
- Files (Monaco viewer with citation highlight)
- Jobs / indexing progress

## Non-functional requirements

| Area | Requirement |
| --- | --- |
| Cost | Weeks 1–11 local at $0; Week 12 temporary deploy ≤7 days, ≤$10 intended |
| Security | No secrets leakage; no unrestricted public import/AI; sandbox clone |
| Reliability | Durable job queue with leases, heartbeats, retries, idempotency |
| Honesty | Never present heuristic matches as verified deep symbols |
| Evaluability | Publish recall/MRR/citation-validity and indexing timing metrics |
| Reconstructability | `git clone` + Docker Compose + migrate/seed rebuilds the demo |

## Success criteria (flagship Definition of Done)

- Public GitHub import and durable indexing work
- Deep parsing for Python, Java, TypeScript, JavaScript
- Generic processing for listed languages/config/docs
- Exact, semantic, and hybrid search evaluated
- Callers/callees for deep languages; Java inheritance/interfaces
- Citation-validated AI answers
- Incremental indexing (or documented stretch if deferred)
- Evaluation metrics, README, demo video, temporary deploy + full teardown

## Out of scope

See [non-goals.md](./non-goals.md).
