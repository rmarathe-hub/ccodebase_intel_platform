# Week 7 validation — Python — fastapi/typer

- URL: https://github.com/fastapi/typer
- Generated: 2026-07-20T01:38:51.243239+00:00
- API: `http://127.0.0.1:8001`
- LLM enrichment: **OFF**

## Checks

| Check | Result | Detail |
| --- | --- | --- |
| repository imported successfully | PASS | status=SUCCEEDED err=None:None |
| worker completes without fatal errors | PASS | stage=completed duration_s=10.1 |
| snapshot created | PASS | 6440e822-d927-45cf-82df-c8c7031f4fef |
| files discovered | PASS | total=773 skipped=18 binaries=11 |
| binary/ignored files skipped | PASS | skipped=18 binaries=11 |
| chunks persisted | PASS | chunks=2904 unique_spans=2904 |
| no duplicate chunk spans | PASS | total=2904 unique=2904 |
| parser provenance stored | PASS | with_parser_name=2904 with_version=2904 |
| content hashes stable (files) | PASS | distinct_file_hashes=637 |
| no fake verified symbols for non-deep langs | PASS | fake_deep_symbols=0 |
| chunks verified_deep honesty | PASS | verified_deep_chunks=2161 llm_enriched=0 |
| optional enrichment OFF | PASS | llm_enriched=0 |
| deep parsers selected for expected languages | PASS | symbol_langs=['javascript', 'python'] expected=['python'] |
| deterministic repository summary generated | PASS | llm_summary_status=disabled chunk_total=2904 |
| exact chunk search operational | PASS | Typer→1076; command→528; Option→603; callback→185 |
| validation stage (pipeline) | PASS | Worker marks SUCCEEDED after chunking; Embedding/Validating stages not yet wired (Week 9+). |
| no regex structural parsing in chunking package | PASS | offenders=[] |
| re-index succeeded | PASS | status=SUCCEEDED duration_s=10.0 |
| stable content hashes on re-index (common paths) | PASS | common=755 mismatches=0 sample=[] |
| no duplicate chunks after re-index | PASS | total=2904 unique=2904 |
| deterministic chunk output on re-index (same key multiset) | PASS | prev_chunks=2904 new_chunks=2904 count_equal=True |

## Metrics

```json
{
  "repository_id": "07f7c912-8073-4bf2-bd38-2b046eb8ceb2",
  "snapshot_id": "6440e822-d927-45cf-82df-c8c7031f4fef",
  "commit_related_job": {
    "status": "SUCCEEDED",
    "stage": "completed",
    "error_code": null,
    "error_message": null
  },
  "indexing_duration_seconds": 10.1,
  "files": {
    "total": 773,
    "skipped": 18,
    "binaries": 11,
    "distinct_hashes": 637
  },
  "files_by_lang_level": [
    {
      "support_level": "deep",
      "language": "python",
      "n": 635,
      "binaries": 0,
      "skipped": 0
    },
    {
      "support_level": "generic",
      "language": "documentation",
      "n": 83,
      "binaries": 0,
      "skipped": 0
    },
    {
      "support_level": "generic",
      "language": "configuration",
      "n": 26,
      "binaries": 0,
      "skipped": 0
    },
    {
      "support_level": "skip",
      "language": null,
      "n": 18,
      "binaries": 11,
      "skipped": 18
    },
    {
      "support_level": "generic",
      "language": "shell",
      "n": 6,
      "binaries": 0,
      "skipped": 0
    },
    {
      "support_level": "generic",
      "language": "css",
      "n": 2,
      "binaries": 0,
      "skipped": 0
    },
    {
      "support_level": "deep",
      "language": "javascript",
      "n": 2,
      "binaries": 0,
      "skipped": 0
    },
    {
      "support_level": "generic",
      "language": "html",
      "n": 1,
      "binaries": 0,
      "skipped": 0
    }
  ],
  "chunks": {
    "total": 2904,
    "verified_deep": 2161,
    "llm_enriched": 0,
    "distinct_content_hashes": 2457,
    "unique_spans": 2904,
    "with_parser": 2904,
    "with_parser_version": 2904
  },
  "chunk_breakdown": [
    {
      "language": "python",
      "support_level": "deep",
      "extraction_method": "deep_symbol",
      "parser_name": "python-ast",
      "n": 2142
    },
    {
      "language": "documentation",
      "support_level": "generic",
      "extraction_method": "markdown_ast",
      "parser_name": "mistune-ast",
      "n": 564
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "yaml-compose",
      "n": 155
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "tomllib",
      "n": 23
    },
    {
      "language": "javascript",
      "support_level": "deep",
      "extraction_method": "deep_symbol",
      "parser_name": "javascript-treesitter",
      "n": 19
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "dockerfile-parse",
      "n": 1
    }
  ],
  "symbols_by_language": [
    {
      "language": "python",
      "n": 4239
    },
    {
      "language": "javascript",
      "n": 19
    }
  ],
  "parsers_seen": [
    "dockerfile-parse/format_native",
    "javascript-treesitter/deep_symbol",
    "mistune-ast/markdown_ast",
    "python-ast/deep_symbol",
    "tomllib/format_native",
    "yaml-compose/format_native"
  ],
  "deterministic_summary_status": "disabled",
  "language_mix": {
    "python": 635,
    "documentation": 83,
    "configuration": 26,
    "shell": 6,
    "css": 2,
    "javascript": 2,
    "html": 1
  }
}
```

## Exact search

```json
[
  {
    "query": "Typer",
    "total": 1076,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "docs/about/index.md",
        "start_line": 1,
        "end_line": 3,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "docs/alternatives.md",
        "start_line": 1,
        "end_line": 4,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "docs/alternatives.md",
        "start_line": 5,
        "end_line": 10,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "docs/alternatives.md",
        "start_line": 11,
        "end_line": 103,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "docs/contributing.md",
        "start_line": 1,
        "end_line": 4,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "command",
    "total": 528,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "docs/alternatives.md",
        "start_line": 11,
        "end_line": 103,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "docs/contributing.md",
        "start_line": 9,
        "end_line": 148,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "docs/environment-variables.md",
        "start_line": 162,
        "end_line": 289,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "docs/features.md",
        "start_line": 45,
        "end_line": 65,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "docs/index.md",
        "start_line": 1,
        "end_line": 47,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "Option",
    "total": 603,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "docs/alternatives.md",
        "start_line": 11,
        "end_line": 103,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "docs/features.md",
        "start_line": 39,
        "end_line": 44,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "docs/features.md",
        "start_line": 45,
        "end_line": 65,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "docs/index.md",
        "start_line": 1,
        "end_line": 47,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "docs/index.md",
        "start_line": 79,
        "end_line": 124,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "callback",
    "total": 185,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "docs/features.md",
        "start_line": 39,
        "end_line": 44,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "docs/reference/context.md",
        "start_line": 1,
        "end_line": 39,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "docs/release-notes.md",
        "start_line": 538,
        "end_line": 541,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "docs/release-notes.md",
        "start_line": 787,
        "end_line": 842,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "docs/release-notes.md",
        "start_line": 1479,
        "end_line": 1496,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      }
    ],
    "citation_ok": true,
    "notes": []
  }
]
```

## Re-index

```json
{
  "repository_id": "07f7c912-8073-4bf2-bd38-2b046eb8ceb2",
  "snapshot_id": "6440e822-d927-45cf-82df-c8c7031f4fef",
  "status": "SUCCEEDED",
  "indexing_duration_seconds": 10.05,
  "files": {
    "total": 773,
    "skipped": 18,
    "binaries": 11,
    "distinct_hashes": 637
  },
  "chunks": {
    "total": 2904,
    "verified_deep": 2161,
    "llm_enriched": 0,
    "distinct_content_hashes": 2457,
    "unique_spans": 2904,
    "with_parser": 2904,
    "with_parser_version": 2904
  },
  "file_hash_mismatches": 0,
  "chunk_multiset_equal": true
}
```

## Validation errors / failures

- None

## Recommendations before Week 8

- None beyond continuing to Week 8 graphs.
