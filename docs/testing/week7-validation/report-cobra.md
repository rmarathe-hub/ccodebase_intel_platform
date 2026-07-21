# Week 7 validation — Go — spf13/cobra

- URL: https://github.com/spf13/cobra
- Generated: 2026-07-20T01:39:12.168164+00:00
- API: `http://127.0.0.1:8001`
- LLM enrichment: **OFF**

## Checks

| Check | Result | Detail |
| --- | --- | --- |
| repository imported successfully | PASS | status=SUCCEEDED err=None:None |
| worker completes without fatal errors | PASS | stage=completed duration_s=5.0 |
| snapshot created | PASS | f04aca69-53c2-49c0-b26f-b80def1307be |
| files discovered | PASS | total=66 skipped=6 binaries=1 |
| binary/ignored files skipped | PASS | skipped=6 binaries=1 |
| chunks persisted | PASS | chunks=825 unique_spans=825 |
| no duplicate chunk spans | PASS | total=825 unique=825 |
| parser provenance stored | PASS | with_parser_name=825 with_version=825 |
| content hashes stable (files) | PASS | distinct_file_hashes=60 |
| no fake verified symbols for non-deep langs | PASS | fake_deep_symbols=0 |
| chunks verified_deep honesty | PASS | verified_deep_chunks=0 llm_enriched=0 |
| optional enrichment OFF | PASS | llm_enriched=0 |
| generic repo has no deep symbols (or only incidental deep files) | PASS | symbol_langs=[] |
| expected generic languages present in chunks | PASS | chunk_langs=['configuration', 'documentation', 'go'] expected=['go'] |
| deterministic repository summary generated | PASS | llm_summary_status=disabled chunk_total=825 |
| exact chunk search operational | PASS | Command→629; Execute→230; Flag→272 |
| validation stage (pipeline) | PASS | Worker marks SUCCEEDED after chunking; Embedding/Validating stages not yet wired (Week 9+). |
| no regex structural parsing in chunking package | PASS | offenders=[] |
| re-index succeeded | PASS | status=SUCCEEDED duration_s=5.0 |
| stable content hashes on re-index (common paths) | PASS | common=60 mismatches=0 sample=[] |
| no duplicate chunks after re-index | PASS | total=825 unique=825 |
| deterministic chunk output on re-index (same key multiset) | PASS | prev_chunks=825 new_chunks=825 count_equal=True |

## Metrics

```json
{
  "repository_id": "fefc4049-b9ed-4995-bf8d-478a71921b94",
  "snapshot_id": "f04aca69-53c2-49c0-b26f-b80def1307be",
  "commit_related_job": {
    "status": "SUCCEEDED",
    "stage": "completed",
    "error_code": null,
    "error_message": null
  },
  "indexing_duration_seconds": 5.04,
  "files": {
    "total": 66,
    "skipped": 6,
    "binaries": 1,
    "distinct_hashes": 60
  },
  "files_by_lang_level": [
    {
      "support_level": "generic",
      "language": "go",
      "n": 36,
      "binaries": 0,
      "skipped": 0
    },
    {
      "support_level": "generic",
      "language": "documentation",
      "n": 18,
      "binaries": 0,
      "skipped": 0
    },
    {
      "support_level": "generic",
      "language": "configuration",
      "n": 6,
      "binaries": 0,
      "skipped": 0
    },
    {
      "support_level": "skip",
      "language": null,
      "n": 6,
      "binaries": 1,
      "skipped": 6
    }
  ],
  "chunks": {
    "total": 825,
    "verified_deep": 0,
    "llm_enriched": 0,
    "distinct_content_hashes": 821,
    "unique_spans": 825,
    "with_parser": 825,
    "with_parser_version": 825
  },
  "chunk_breakdown": [
    {
      "language": "go",
      "support_level": "generic",
      "extraction_method": "treesitter_node",
      "parser_name": "go-treesitter",
      "n": 656
    },
    {
      "language": "documentation",
      "support_level": "generic",
      "extraction_method": "markdown_ast",
      "parser_name": "mistune-ast",
      "n": 130
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "yaml-compose",
      "n": 28
    },
    {
      "language": "go",
      "support_level": "generic",
      "extraction_method": "line_window_fallback",
      "parser_name": "go-treesitter",
      "n": 11
    }
  ],
  "symbols_by_language": [],
  "parsers_seen": [
    "go-treesitter/line_window_fallback",
    "go-treesitter/treesitter_node",
    "mistune-ast/markdown_ast",
    "yaml-compose/format_native"
  ],
  "deterministic_summary_status": "disabled",
  "language_mix": {
    "go": 36,
    "documentation": 18,
    "configuration": 6
  }
}
```

## Exact search

```json
[
  {
    "query": "Command",
    "total": 629,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "active_help.go",
        "start_line": 47,
        "end_line": 53,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "go-treesitter"
      },
      {
        "path": "active_help_test.go",
        "start_line": 29,
        "end_line": 82,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "go-treesitter"
      },
      {
        "path": "active_help_test.go",
        "start_line": 84,
        "end_line": 167,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "go-treesitter"
      },
      {
        "path": "active_help_test.go",
        "start_line": 169,
        "end_line": 229,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "go-treesitter"
      },
      {
        "path": "active_help_test.go",
        "start_line": 231,
        "end_line": 264,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "go-treesitter"
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "Execute",
    "total": 230,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "active_help_test.go",
        "start_line": 29,
        "end_line": 82,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "go-treesitter"
      },
      {
        "path": "active_help_test.go",
        "start_line": 84,
        "end_line": 167,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "go-treesitter"
      },
      {
        "path": "active_help_test.go",
        "start_line": 169,
        "end_line": 229,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "go-treesitter"
      },
      {
        "path": "active_help_test.go",
        "start_line": 231,
        "end_line": 264,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "go-treesitter"
      },
      {
        "path": "active_help_test.go",
        "start_line": 266,
        "end_line": 317,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "go-treesitter"
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "Flag",
    "total": 272,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "active_help_test.go",
        "start_line": 231,
        "end_line": 264,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "go-treesitter"
      },
      {
        "path": "active_help_test.go",
        "start_line": 266,
        "end_line": 317,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "go-treesitter"
      },
      {
        "path": "bash_completions.go",
        "start_line": 29,
        "end_line": 34,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "go-treesitter"
      },
      {
        "path": "bash_completions.go",
        "start_line": 116,
        "end_line": 195,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "go-treesitter"
      },
      {
        "path": "bash_completions.go",
        "start_line": 196,
        "end_line": 275,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "go-treesitter"
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
  "repository_id": "fefc4049-b9ed-4995-bf8d-478a71921b94",
  "snapshot_id": "f04aca69-53c2-49c0-b26f-b80def1307be",
  "status": "SUCCEEDED",
  "indexing_duration_seconds": 5.02,
  "files": {
    "total": 66,
    "skipped": 6,
    "binaries": 1,
    "distinct_hashes": 60
  },
  "chunks": {
    "total": 825,
    "verified_deep": 0,
    "llm_enriched": 0,
    "distinct_content_hashes": 821,
    "unique_spans": 825,
    "with_parser": 825,
    "with_parser_version": 825
  },
  "file_hash_mismatches": 0,
  "chunk_multiset_equal": true
}
```

## Validation errors / failures

- None

## Recommendations before Week 8

- None beyond continuing to Week 8 graphs.
