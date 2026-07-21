# Week 7 validation — Java — perwendel/spark

- URL: https://github.com/perwendel/spark
- Generated: 2026-07-20T01:39:01.878325+00:00
- API: `http://127.0.0.1:8001`
- LLM enrichment: **OFF**

## Checks

| Check | Result | Detail |
| --- | --- | --- |
| repository imported successfully | PASS | status=SUCCEEDED err=None:None |
| worker completes without fatal errors | PASS | stage=completed duration_s=5.1 |
| snapshot created | PASS | 999b1470-c3c7-4f9c-a054-10b619ab7c94 |
| files discovered | PASS | total=213 skipped=15 binaries=6 |
| binary/ignored files skipped | PASS | skipped=15 binaries=6 |
| chunks persisted | PASS | chunks=1582 unique_spans=1582 |
| no duplicate chunk spans | PASS | total=1582 unique=1582 |
| parser provenance stored | PASS | with_parser_name=1582 with_version=1582 |
| content hashes stable (files) | PASS | distinct_file_hashes=198 |
| no fake verified symbols for non-deep langs | PASS | fake_deep_symbols=0 |
| chunks verified_deep honesty | PASS | verified_deep_chunks=1547 llm_enriched=0 |
| optional enrichment OFF | PASS | llm_enriched=0 |
| deep parsers selected for expected languages | PASS | symbol_langs=['java'] expected=['java'] |
| deterministic repository summary generated | PASS | llm_summary_status=disabled chunk_total=1582 |
| exact chunk search operational | PASS | Route→340; Spark→201; before→116; exception→552 |
| validation stage (pipeline) | PASS | Worker marks SUCCEEDED after chunking; Embedding/Validating stages not yet wired (Week 9+). |
| no regex structural parsing in chunking package | PASS | offenders=[] |
| re-index succeeded | PASS | status=SUCCEEDED duration_s=10.1 |
| stable content hashes on re-index (common paths) | PASS | common=198 mismatches=0 sample=[] |
| no duplicate chunks after re-index | PASS | total=1582 unique=1582 |
| deterministic chunk output on re-index (same key multiset) | PASS | prev_chunks=1582 new_chunks=1582 count_equal=True |

## Metrics

```json
{
  "repository_id": "bf7bfeb4-2a0f-4086-8563-6277782e1d22",
  "snapshot_id": "999b1470-c3c7-4f9c-a054-10b619ab7c94",
  "commit_related_job": {
    "status": "SUCCEEDED",
    "stage": "completed",
    "error_code": null,
    "error_message": null
  },
  "indexing_duration_seconds": 5.08,
  "files": {
    "total": 213,
    "skipped": 15,
    "binaries": 6,
    "distinct_hashes": 198
  },
  "files_by_lang_level": [
    {
      "support_level": "deep",
      "language": "java",
      "n": 184,
      "binaries": 0,
      "skipped": 0
    },
    {
      "support_level": "skip",
      "language": null,
      "n": 15,
      "binaries": 6,
      "skipped": 15
    },
    {
      "support_level": "generic",
      "language": "configuration",
      "n": 5,
      "binaries": 0,
      "skipped": 0
    },
    {
      "support_level": "generic",
      "language": "documentation",
      "n": 4,
      "binaries": 0,
      "skipped": 0
    },
    {
      "support_level": "generic",
      "language": "html",
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
      "language": "css",
      "n": 1,
      "binaries": 0,
      "skipped": 0
    }
  ],
  "chunks": {
    "total": 1582,
    "verified_deep": 1547,
    "llm_enriched": 0,
    "distinct_content_hashes": 1557,
    "unique_spans": 1582,
    "with_parser": 1582,
    "with_parser_version": 1582
  },
  "chunk_breakdown": [
    {
      "language": "java",
      "support_level": "deep",
      "extraction_method": "deep_symbol",
      "parser_name": "java-treesitter",
      "n": 1547
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "defusedxml-sax",
      "n": 25
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "yaml-compose",
      "n": 10
    }
  ],
  "symbols_by_language": [
    {
      "language": "java",
      "n": 3165
    }
  ],
  "parsers_seen": [
    "defusedxml-sax/format_native",
    "java-treesitter/deep_symbol",
    "yaml-compose/format_native"
  ],
  "deterministic_summary_status": "disabled",
  "language_mix": {
    "java": 184,
    "configuration": 5,
    "documentation": 4,
    "javascript": 2,
    "html": 2,
    "css": 1
  }
}
```

## Exact search

```json
[
  {
    "query": "Route",
    "total": 340,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "src/main/java/spark/Access.java",
        "start_line": 24,
        "end_line": 34,
        "language": "java",
        "support_level": "deep",
        "verified_deep": true,
        "parser_name": "java-treesitter"
      },
      {
        "path": "src/main/java/spark/Access.java",
        "start_line": 30,
        "end_line": 32,
        "language": "java",
        "support_level": "deep",
        "verified_deep": true,
        "parser_name": "java-treesitter"
      },
      {
        "path": "src/main/java/spark/CustomErrorPages.java",
        "start_line": 30,
        "end_line": 122,
        "language": "java",
        "support_level": "deep",
        "verified_deep": true,
        "parser_name": "java-treesitter"
      },
      {
        "path": "src/main/java/spark/CustomErrorPages.java",
        "start_line": 54,
        "end_line": 71,
        "language": "java",
        "support_level": "deep",
        "verified_deep": true,
        "parser_name": "java-treesitter"
      },
      {
        "path": "src/main/java/spark/CustomErrorPages.java",
        "start_line": 98,
        "end_line": 100,
        "language": "java",
        "support_level": "deep",
        "verified_deep": true,
        "parser_name": "java-treesitter"
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "Spark",
    "total": 201,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": ".github/workflows/ci.yml",
        "start_line": 1,
        "end_line": 1,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "yaml-compose"
      },
      {
        "path": "pom.xml",
        "start_line": 9,
        "end_line": 9,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "defusedxml-sax"
      },
      {
        "path": "pom.xml",
        "start_line": 10,
        "end_line": 10,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "defusedxml-sax"
      },
      {
        "path": "pom.xml",
        "start_line": 13,
        "end_line": 13,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "defusedxml-sax"
      },
      {
        "path": "pom.xml",
        "start_line": 15,
        "end_line": 15,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "defusedxml-sax"
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "before",
    "total": 116,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "config/spark_formatter_intellij.xml",
        "start_line": 25,
        "end_line": 40,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false,
        "parser_name": "defusedxml-sax"
      },
      {
        "path": "src/main/java/spark/embeddedserver/EmbeddedServer.java",
        "start_line": 28,
        "end_line": 85,
        "language": "java",
        "support_level": "deep",
        "verified_deep": true,
        "parser_name": "java-treesitter"
      },
      {
        "path": "src/main/java/spark/embeddedserver/jetty/websocket/WebSocketServletContextHandlerFactory.java",
        "start_line": 33,
        "end_line": 71,
        "language": "java",
        "support_level": "deep",
        "verified_deep": true,
        "parser_name": "java-treesitter"
      },
      {
        "path": "src/main/java/spark/embeddedserver/jetty/websocket/WebSocketServletContextHandlerFactory.java",
        "start_line": 44,
        "end_line": 69,
        "language": "java",
        "support_level": "deep",
        "verified_deep": true,
        "parser_name": "java-treesitter"
      },
      {
        "path": "src/main/java/spark/http/matching/BeforeFilters.java",
        "start_line": 30,
        "end_line": 61,
        "language": "java",
        "support_level": "deep",
        "verified_deep": true,
        "parser_name": "java-treesitter"
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "exception",
    "total": 552,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "src/main/java/spark/Base64.java",
        "start_line": 19,
        "end_line": 57,
        "language": "java",
        "support_level": "deep",
        "verified_deep": true,
        "parser_name": "java-treesitter"
      },
      {
        "path": "src/main/java/spark/Base64.java",
        "start_line": 43,
        "end_line": 54,
        "language": "java",
        "support_level": "deep",
        "verified_deep": true,
        "parser_name": "java-treesitter"
      },
      {
        "path": "src/main/java/spark/CustomErrorPages.java",
        "start_line": 30,
        "end_line": 122,
        "language": "java",
        "support_level": "deep",
        "verified_deep": true,
        "parser_name": "java-treesitter"
      },
      {
        "path": "src/main/java/spark/CustomErrorPages.java",
        "start_line": 54,
        "end_line": 71,
        "language": "java",
        "support_level": "deep",
        "verified_deep": true,
        "parser_name": "java-treesitter"
      },
      {
        "path": "src/main/java/spark/embeddedserver/EmbeddedServerFactory.java",
        "start_line": 26,
        "end_line": 42,
        "language": "java",
        "support_level": "deep",
        "verified_deep": true,
        "parser_name": "java-treesitter"
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
  "repository_id": "bf7bfeb4-2a0f-4086-8563-6277782e1d22",
  "snapshot_id": "999b1470-c3c7-4f9c-a054-10b619ab7c94",
  "status": "SUCCEEDED",
  "indexing_duration_seconds": 10.06,
  "files": {
    "total": 213,
    "skipped": 15,
    "binaries": 6,
    "distinct_hashes": 198
  },
  "chunks": {
    "total": 1582,
    "verified_deep": 1547,
    "llm_enriched": 0,
    "distinct_content_hashes": 1557,
    "unique_spans": 1582,
    "with_parser": 1582,
    "with_parser_version": 1582
  },
  "file_hash_mismatches": 0,
  "chunk_multiset_equal": true
}
```

## Validation errors / failures

- None

## Recommendations before Week 8

- None beyond continuing to Week 8 graphs.
