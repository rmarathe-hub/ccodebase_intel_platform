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
- `parser_name` / `parser_version` remain null until a parser runs (Week 3 Day 3+ / Week 4).

## Out of scope for Days 1–2

Worker persistence of `source_files`, Files API, and deep parsers ship after Day 2.
