# Week 7 validation — Config/Docs — docker/awesome-compose

- URL: https://github.com/docker/awesome-compose
- Generated: 2026-07-20T01:39:17.788415+00:00
- API: `http://127.0.0.1:8001`
- LLM enrichment: **OFF**

## Checks

| Check | Result | Detail |
| --- | --- | --- |
| repository imported successfully | PASS | status=SUCCEEDED err=None:None |
| worker completes without fatal errors | PASS | stage=completed duration_s=5.0 |
| snapshot created | PASS | 9202ad67-c514-470b-8d8e-5d844d787f26 |
| files discovered | PASS | total=479 skipped=124 binaries=50 |
| binary/ignored files skipped | PASS | skipped=124 binaries=50 |
| chunks persisted | PASS | chunks=956 unique_spans=956 |
| no duplicate chunk spans | PASS | total=956 unique=956 |
| parser provenance stored | PASS | with_parser_name=956 with_version=956 |
| content hashes stable (files) | PASS | distinct_file_hashes=311 |
| no fake verified symbols for non-deep langs | PASS | fake_deep_symbols=0 |
| chunks verified_deep honesty | PASS | verified_deep_chunks=116 llm_enriched=0 |
| optional enrichment OFF | PASS | llm_enriched=0 |
| generic repo has no deep symbols (or only incidental deep files) | PASS | symbol_langs=['java', 'javascript', 'python', 'typescript'] |
| expected generic languages present in chunks | PASS | chunk_langs=['c#', 'configuration', 'documentation', 'go', 'java', 'javascript', 'python', 'rust', 'sql', 'typescript'] expected=['configuration', 'documentation'] |
| deterministic repository summary generated | PASS | llm_summary_status=disabled chunk_total=956 |
| exact chunk search operational | PASS | docker-compose→31; postgres→60; redis→24; nginx→61 |
| validation stage (pipeline) | PASS | Worker marks SUCCEEDED after chunking; Embedding/Validating stages not yet wired (Week 9+). |
| no regex structural parsing in chunking package | PASS | offenders=[] |
| re-index succeeded | PASS | status=SUCCEEDED duration_s=5.0 |
| stable content hashes on re-index (common paths) | PASS | common=355 mismatches=0 sample=[] |
| no duplicate chunks after re-index | PASS | total=956 unique=956 |
| deterministic chunk output on re-index (same key multiset) | PASS | prev_chunks=956 new_chunks=956 count_equal=True |

## Metrics

```json
{
  "repository_id": "fbbf6457-8d89-4191-8f5a-a86da1cff1a9",
  "snapshot_id": "9202ad67-c514-470b-8d8e-5d844d787f26",
  "commit_related_job": {
    "status": "SUCCEEDED",
    "stage": "completed",
    "error_code": null,
    "error_message": null
  },
  "indexing_duration_seconds": 5.05,
  "files": {
    "total": 479,
    "skipped": 124,
    "binaries": 50,
    "distinct_hashes": 311
  },
  "files_by_lang_level": [
    {
      "support_level": "generic",
      "language": "configuration",
      "n": 142,
      "binaries": 0,
      "skipped": 0
    },
    {
      "support_level": "skip",
      "language": null,
      "n": 124,
      "binaries": 50,
      "skipped": 124
    },
    {
      "support_level": "generic",
      "language": "documentation",
      "n": 81,
      "binaries": 0,
      "skipped": 0
    },
    {
      "support_level": "deep",
      "language": "javascript",
      "n": 47,
      "binaries": 0,
      "skipped": 0
    },
    {
      "support_level": "deep",
      "language": "typescript",
      "n": 15,
      "binaries": 0,
      "skipped": 0
    },
    {
      "support_level": "generic",
      "language": "css",
      "n": 15,
      "binaries": 0,
      "skipped": 0
    },
    {
      "support_level": "deep",
      "language": "python",
      "n": 13,
      "binaries": 0,
      "skipped": 0
    },
    {
      "support_level": "deep",
      "language": "java",
      "n": 11,
      "binaries": 0,
      "skipped": 0
    },
    {
      "support_level": "generic",
      "language": "html",
      "n": 9,
      "binaries": 0,
      "skipped": 0
    },
    {
      "support_level": "generic",
      "language": "sql",
      "n": 6,
      "binaries": 0,
      "skipped": 0
    },
    {
      "support_level": "generic",
      "language": "rust",
      "n": 5,
      "binaries": 0,
      "skipped": 0
    },
    {
      "support_level": "generic",
      "language": "c#",
      "n": 5,
      "binaries": 0,
      "skipped": 0
    },
    {
      "support_level": "generic",
      "language": "go",
      "n": 4,
      "binaries": 0,
      "skipped": 0
    },
    {
      "support_level": "generic",
      "language": "shell",
      "n": 1,
      "binaries": 0,
      "skipped": 0
    },
    {
      "support_level": "generic",
      "language": "php",
      "n": 1,
      "binaries": 0,
      "skipped": 0
    }
  ],
  "chunks": {
    "total": 956,
    "verified_deep": 116,
    "llm_enriched": 0,
    "distinct_content_hashes": 751,
    "unique_spans": 956,
    "with_parser": 956,
    "with_parser_version": 956
  },
  "chunk_breakdown": [
    {
      "language": "documentation",
      "support_level": "generic",
      "extraction_method": "markdown_ast",
      "parser_name": "mistune-ast",
      "n": 250
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "json-stdlib",
      "n": 238
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "yaml-compose",
      "n": 177
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "dockerfile-parse",
      "n": 92
    },
    {
      "language": "javascript",
      "support_level": "deep",
      "extraction_method": "deep_symbol",
      "parser_name": "javascript-treesitter",
      "n": 52
    },
    {
      "language": "java",
      "support_level": "deep",
      "extraction_method": "deep_symbol",
      "parser_name": "java-treesitter",
      "n": 41
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "defusedxml-sax",
      "n": 34
    },
    {
      "language": "rust",
      "support_level": "generic",
      "extraction_method": "treesitter_node",
      "parser_name": "rust-treesitter",
      "n": 21
    },
    {
      "language": "python",
      "support_level": "deep",
      "extraction_method": "deep_symbol",
      "parser_name": "python-ast",
      "n": 13
    },
    {
      "language": "go",
      "support_level": "generic",
      "extraction_method": "treesitter_node",
      "parser_name": "go-treesitter",
      "n": 12
    },
    {
      "language": "typescript",
      "support_level": "deep",
      "extraction_method": "deep_symbol",
      "parser_name": "typescript-treesitter",
      "n": 8
    },
    {
      "language": "sql",
      "support_level": "generic",
      "extraction_method": "sqlglot_tokenizer",
      "parser_name": "sqlglot",
      "n": 6
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "tomllib",
      "n": 6
    },
    {
      "language": "c#",
      "support_level": "generic",
      "extraction_method": "treesitter_node",
      "parser_name": "csharp-treesitter",
      "n": 4
    },
    {
      "language": "typescript",
      "support_level": "deep",
      "extraction_method": "deep_symbol",
      "parser_name": "tsx-treesitter",
      "n": 2
    }
  ],
  "symbols_by_language": [
    {
      "language": "javascript",
      "n": 118
    },
    {
      "language": "java",
      "n": 107
    },
    {
      "language": "typescript",
      "n": 44
    },
    {
      "language": "python",
      "n": 38
    }
  ],
  "parsers_seen": [
    "csharp-treesitter/treesitter_node",
    "defusedxml-sax/format_native",
    "dockerfile-parse/format_native",
    "go-treesitter/treesitter_node",
    "java-treesitter/deep_symbol",
    "javascript-treesitter/deep_symbol",
    "json-stdlib/format_native",
    "mistune-ast/markdown_ast",
    "python-ast/deep_symbol",
    "rust-treesitter/treesitter_node",
    "sqlglot/sqlglot_tokenizer",
    "tomllib/format_native",
    "tsx-treesitter/deep_symbol",
    "typescript-treesitter/deep_symbol",
    "yaml-compose/format_native"
  ],
  "deterministic_summary_status": "disabled",
  "language_mix": {
    "configuration": 142,
    "documentation": 81,
    "javascript": 47,
    "css": 15,
    "typescript": 15,
    "python": 13,
    "java": 11,
    "html": 9,
    "sql": 6,
    "c#": 5,
    "rust": 5,
    "go": 4,
    "php": 1,
    "shell": 1
  }
}
```

## Exact search

```json
[
  {
    "query": "docker-compose",
    "total": 31,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "angular/README.md",
        "start_line": 31,
        "end_line": 48,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "fastapi/README.md",
        "start_line": 29,
        "end_line": 33,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "minecraft/README.md",
        "start_line": 39,
        "end_line": 82,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "nginx-flask-mysql/README.md",
        "start_line": 44,
        "end_line": 58,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "nginx-golang-mysql/README.md",
        "start_line": 54,
        "end_line": 70,
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
    "query": "postgres",
    "total": 60,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "gitea-postgres/compose.yaml",
        "start_line": 1,
        "end_line": 26,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "yaml-compose"
      },
      {
        "path": "gitea-postgres/compose.yaml",
        "start_line": 2,
        "end_line": 15,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "yaml-compose"
      },
      {
        "path": "gitea-postgres/compose.yaml",
        "start_line": 15,
        "end_line": 26,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "yaml-compose"
      },
      {
        "path": "gitea-postgres/README.md",
        "start_line": 1,
        "end_line": 28,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "gitea-postgres/README.md",
        "start_line": 29,
        "end_line": 42,
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
    "query": "redis",
    "total": 24,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "CONTRIBUTING.md",
        "start_line": 51,
        "end_line": 103,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "flask-redis/app.py",
        "start_line": 8,
        "end_line": 11,
        "language": "python",
        "support_level": "deep",
        "verified_deep": true,
        "parser_name": "python-ast"
      },
      {
        "path": "flask-redis/compose.yaml",
        "start_line": 1,
        "end_line": 19,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "yaml-compose"
      },
      {
        "path": "flask-redis/compose.yaml",
        "start_line": 2,
        "end_line": 6,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "yaml-compose"
      },
      {
        "path": "flask-redis/compose.yaml",
        "start_line": 6,
        "end_line": 19,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "yaml-compose"
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "nginx",
    "total": 61,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "elasticsearch-logstash-kibana/compose.yaml",
        "start_line": 1,
        "end_line": 46,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "yaml-compose"
      },
      {
        "path": "elasticsearch-logstash-kibana/compose.yaml",
        "start_line": 18,
        "end_line": 37,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "yaml-compose"
      },
      {
        "path": "elasticsearch-logstash-kibana/README.md",
        "start_line": 56,
        "end_line": 58,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "nginx-aspnet-mysql/proxy/Dockerfile",
        "start_line": 1,
        "end_line": 2,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "dockerfile-parse"
      },
      {
        "path": "nginx-aspnet-mysql/README.md",
        "start_line": 2,
        "end_line": 47,
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
  "repository_id": "fbbf6457-8d89-4191-8f5a-a86da1cff1a9",
  "snapshot_id": "9202ad67-c514-470b-8d8e-5d844d787f26",
  "status": "SUCCEEDED",
  "indexing_duration_seconds": 5.01,
  "files": {
    "total": 479,
    "skipped": 124,
    "binaries": 50,
    "distinct_hashes": 311
  },
  "chunks": {
    "total": 956,
    "verified_deep": 116,
    "llm_enriched": 0,
    "distinct_content_hashes": 751,
    "unique_spans": 956,
    "with_parser": 956,
    "with_parser_version": 956
  },
  "file_hash_mismatches": 0,
  "chunk_multiset_equal": true
}
```

## Validation errors / failures

- None

## Recommendations before Week 8

- None beyond continuing to Week 8 graphs.
