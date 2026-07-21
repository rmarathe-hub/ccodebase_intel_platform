# Week 7 validation — TypeScript/JS — tj/commander.js

- URL: https://github.com/tj/commander.js
- Generated: 2026-07-20T01:39:07.052933+00:00
- API: `http://127.0.0.1:8001`
- LLM enrichment: **OFF**

## Checks

| Check | Result | Detail |
| --- | --- | --- |
| repository imported successfully | PASS | status=SUCCEEDED err=None:None |
| worker completes without fatal errors | PASS | stage=completed duration_s=5.1 |
| snapshot created | PASS | a5135786-5aef-4d55-80e1-e7cf35eb60ea |
| files discovered | PASS | total=219 skipped=25 binaries=3 |
| binary/ignored files skipped | PASS | skipped=25 binaries=3 |
| chunks persisted | PASS | chunks=646 unique_spans=646 |
| no duplicate chunk spans | PASS | total=646 unique=646 |
| parser provenance stored | PASS | with_parser_name=646 with_version=646 |
| content hashes stable (files) | PASS | distinct_file_hashes=194 |
| no fake verified symbols for non-deep langs | PASS | fake_deep_symbols=0 |
| chunks verified_deep honesty | PASS | verified_deep_chunks=323 llm_enriched=0 |
| optional enrichment OFF | PASS | llm_enriched=0 |
| deep parsers selected for expected languages | PASS | symbol_langs=['javascript', 'typescript'] expected=['javascript', 'typescript'] |
| deterministic repository summary generated | PASS | llm_summary_status=disabled chunk_total=646 |
| exact chunk search operational | PASS | Command→344; Option→304; parse→97 |
| validation stage (pipeline) | PASS | Worker marks SUCCEEDED after chunking; Embedding/Validating stages not yet wired (Week 9+). |
| no regex structural parsing in chunking package | PASS | offenders=[] |
| re-index succeeded | PASS | status=SUCCEEDED duration_s=5.0 |
| stable content hashes on re-index (common paths) | PASS | common=194 mismatches=0 sample=[] |
| no duplicate chunks after re-index | PASS | total=646 unique=646 |
| deterministic chunk output on re-index (same key multiset) | PASS | prev_chunks=646 new_chunks=646 count_equal=True |

## Metrics

```json
{
  "repository_id": "e0708b2c-eaea-4abe-b457-bb800c784966",
  "snapshot_id": "a5135786-5aef-4d55-80e1-e7cf35eb60ea",
  "commit_related_job": {
    "status": "SUCCEEDED",
    "stage": "completed",
    "error_code": null,
    "error_message": null
  },
  "indexing_duration_seconds": 5.05,
  "files": {
    "total": 219,
    "skipped": 25,
    "binaries": 3,
    "distinct_hashes": 194
  },
  "files_by_lang_level": [
    {
      "support_level": "deep",
      "language": "javascript",
      "n": 168,
      "binaries": 0,
      "skipped": 0
    },
    {
      "support_level": "skip",
      "language": null,
      "n": 25,
      "binaries": 3,
      "skipped": 25
    },
    {
      "support_level": "generic",
      "language": "documentation",
      "n": 13,
      "binaries": 0,
      "skipped": 0
    },
    {
      "support_level": "generic",
      "language": "configuration",
      "n": 10,
      "binaries": 0,
      "skipped": 0
    },
    {
      "support_level": "deep",
      "language": "typescript",
      "n": 3,
      "binaries": 0,
      "skipped": 0
    }
  ],
  "chunks": {
    "total": 646,
    "verified_deep": 323,
    "llm_enriched": 0,
    "distinct_content_hashes": 630,
    "unique_spans": 646,
    "with_parser": 646,
    "with_parser_version": 646
  },
  "chunk_breakdown": [
    {
      "language": "javascript",
      "support_level": "deep",
      "extraction_method": "deep_symbol",
      "parser_name": "javascript-treesitter",
      "n": 293
    },
    {
      "language": "documentation",
      "support_level": "generic",
      "extraction_method": "markdown_ast",
      "parser_name": "mistune-ast",
      "n": 284
    },
    {
      "language": "typescript",
      "support_level": "deep",
      "extraction_method": "deep_symbol",
      "parser_name": "typescript-treesitter",
      "n": 30
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "json-stdlib",
      "n": 22
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "yaml-compose",
      "n": 17
    }
  ],
  "symbols_by_language": [
    {
      "language": "javascript",
      "n": 857
    },
    {
      "language": "typescript",
      "n": 33
    }
  ],
  "parsers_seen": [
    "javascript-treesitter/deep_symbol",
    "json-stdlib/format_native",
    "mistune-ast/markdown_ast",
    "typescript-treesitter/deep_symbol",
    "yaml-compose/format_native"
  ],
  "deterministic_summary_status": "disabled",
  "language_mix": {
    "javascript": 168,
    "documentation": 13,
    "configuration": 10,
    "typescript": 3
  }
}
```

## Exact search

```json
[
  {
    "query": "Command",
    "total": 344,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "CHANGELOG.md",
        "start_line": 1,
        "end_line": 17,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 18,
        "end_line": 21,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 27,
        "end_line": 32,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 33,
        "end_line": 36,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 37,
        "end_line": 52,
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
    "total": 304,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "CHANGELOG.md",
        "start_line": 22,
        "end_line": 26,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 37,
        "end_line": 52,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 76,
        "end_line": 86,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 87,
        "end_line": 92,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 93,
        "end_line": 97,
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
    "query": "parse",
    "total": 97,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "CHANGELOG.md",
        "start_line": 76,
        "end_line": 86,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 87,
        "end_line": 92,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 111,
        "end_line": 119,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 120,
        "end_line": 127,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "mistune-ast"
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 202,
        "end_line": 205,
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
  "repository_id": "e0708b2c-eaea-4abe-b457-bb800c784966",
  "snapshot_id": "a5135786-5aef-4d55-80e1-e7cf35eb60ea",
  "status": "SUCCEEDED",
  "indexing_duration_seconds": 5.01,
  "files": {
    "total": 219,
    "skipped": 25,
    "binaries": 3,
    "distinct_hashes": 194
  },
  "chunks": {
    "total": 646,
    "verified_deep": 323,
    "llm_enriched": 0,
    "distinct_content_hashes": 630,
    "unique_spans": 646,
    "with_parser": 646,
    "with_parser_version": 646
  },
  "file_hash_mismatches": 0,
  "chunk_multiset_equal": true
}
```

## Validation errors / failures

- None

## Recommendations before Week 8

- None beyond continuing to Week 8 graphs.
