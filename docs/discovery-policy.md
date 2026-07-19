# Discovery Policy (Week 3)

Local-first rules for walking cloned repositories. No code from the repository
is executed. Symlinks are never followed.

## Support levels

Every discovered path is labeled:

| Level | Meaning |
| --- | --- |
| `deep` | Eligible for structural analysis (Python, Java, TypeScript, JavaScript) |
| `generic` | Searchable / browsable text formats |
| `skip` | Not indexed for analysis (still may be recorded with a skip reason) |

Authoritative constants live in `apps/api/app/core/language_contract.py`.

## Ignored directories (subtree pruned)

`.git`, `node_modules`, `.venv`, `venv`, `target`, `dist`, `build`, `coverage`,
`vendor`, `__pycache__`, `.tox`, `.mypy_cache`, `.pytest_cache`, `.ruff_cache`,
`.next`, `.nuxt`, `Pods`, `DerivedData`, `.idea`, `.vscode`, `htmlcov`, and
similar package/cache folders.

## Skip reasons

| Reason | When |
| --- | --- |
| `ignored_dir` | Path segment is an ignored directory |
| `binary` | Binary extension or null-byte / low-text content sniff |
| `oversized` | File exceeds `discovery_max_file_bytes` (default 1 MiB) |
| `unsupported_ext` | Extension not in the language map |
| `secret_path` | `.env*`, `*.pem` / `*.key`, credential filenames |
| `symlink` | Symlink entry (not followed) |
| `unreadable` | Stat/read failure or escape outside repo root |
| `empty_name` | Degenerate relative path |

## Safety caps

| Setting | Default |
| --- | --- |
| `discovery_max_file_bytes` | 1 MiB |
| `discovery_max_files` | 50_000 |
| `discovery_binary_sample_bytes` | 8192 |

## Honesty

- Generic languages must never be reported as deep symbols.
- SKIP files must carry `skip_reason`.
- After Week 3 Day 7, successfully parsed deep **Python** files set
  `parser_name=python-ast` and populate `symbols`.
- After Week 5 Days 1–2, successfully parsed deep **TypeScript / JavaScript**
  (including TSX/JSX) files set `parser_name` to the matching `*-treesitter`
  stamp and populate symbols.
- After Week 6 Days 1–2, successfully parsed deep **Java** files set
  `parser_name=java-treesitter` and populate symbols.
- Retail golden tests assert classification levels/paths, not content hashes (fixture docs may change).

## Fixture golden tests (Days 5–6)

- Offline shape: `apps/api/tests/fixtures/retail_shape/`
- Full retail: cached under `.cache/retail-retention-revenue-intel` or `CODEINTEL_RETAIL_FIXTURE`
- Perf smoke: discovery of thousands of tiny files stays under a generous wall-clock budget

## Day 7 — Python symbols

- Parser: stdlib `ast` only (no execution)
- Kinds: `class`, `function`, `method`, `import`
- Relationships / callers / callees are out of scope for Week 3

## Historical note (Week 3)

At the end of Week 3, deep parsers for Java / TypeScript / JavaScript, relationship
graphs, chunking, and embeddings were still future work. Those deep parsers shipped
in Weeks 5–6. Chunking / enrichment / exact search follow the Week 7+ contracts in
[language-support.md](./language-support.md) and [indexing-pipeline.md](./indexing-pipeline.md).
