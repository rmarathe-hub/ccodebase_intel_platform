# Week 8 validation — Go — spf13/cobra

- URL: https://github.com/spf13/cobra
- Generated: 2026-07-20T02:31:44.110914+00:00
- API: `http://127.0.0.1:8001`
- LLM enrichment: **OFF**
- Clone size limit: 52428800 bytes (unchanged)

## Checks

| Check | Result | Detail |
| --- | --- | --- |
| repository imported successfully | PASS | status=SUCCEEDED err=None:None |
| snapshot created | PASS | f04aca69-53c2-49c0-b26f-b80def1307be |
| files discovered | PASS | total=66 skipped=6 binaries=1 |
| chunks persisted | PASS | chunks=825 unique_spans=825 |
| no duplicate chunk spans | PASS | total=825 unique=825 |
| optional enrichment OFF | PASS | llm_enriched=0 |
| no fake verified symbols for non-deep langs | PASS | fake_deep=0 |
| generic-primary: verified_deep not claimed repository-wide | PASS | verified_deep_chunks=0 (incidental deep files allowed=False) |
| cobra/generic: no deep Go symbols | PASS | symbol_totals={'total': 0, 'fake_deep': 0} |
| deterministic repository summary | PASS | llm_summary_status=disabled |
| exact chunk search operational | PASS | Command→629; Execute→230; Flag→272 |
| relation kinds only from unified model | PASS | kinds={} |
| no orphan from_symbol dangling IDs | PASS | orphans=0 |
| no orphan to_symbol dangling IDs | PASS | orphans=0 |
| no cross-snapshot relation leakage | PASS | cross=0 |
| no duplicate structural relation keys | PASS | total=0 unique=0 |
| modules graph endpoint ok | PASS | nodes=0 edges=0 |
| modules graph no host path leakage | PASS | leaked=0 |
| packages graph endpoint ok | PASS | nodes=0 edges=0 |
| packages graph no host path leakage | PASS | leaked=0 |
| directory graph usable | PASS | nodes=8 edges=7 |
| directories graph no host path leakage | PASS | leaked=0 |
| generic Go/unsupported: no invented verified call graph | PASS | go_symbols=0 go_calls=0 |
| invalid filter returns validation error | PASS | status=422 body={"detail":{"code":"invalid_support_level","message":"support_level must be deep, generic, mixed, or skip"}} |
| invalid confidence rejected | PASS | status=422 |
| graph node/edge limits applied | PASS | nodes=5 edges=4 |
| path_prefix filter accepted | PASS | nodes=0 |
| inferred=false filter respected | PASS | inferred_remaining=0 total_edges=7 |
| React Flow page wired to live graph APIs | PASS | {"loads_from_api": true, "no_fixture_data_in_page": true, "has_relation_filters": true, "has_language_filter": true, "has_support_level_filter": true, "has_depth_control": true, "has_generic_honesty_notice": true, "has_inferred_edge_styling": true, "selection_detail_panel": true, "uses_xyflow": true} |
| generic honesty notice present in Graph UI | PASS | GraphPage honesty copy checked |
| no regex structural parsing in chunking package | PASS | offenders=[] |
| re-index succeeded | PASS | status=SUCCEEDED duration_s=5.0 |
| stable content hashes on re-index | PASS | common=60 mismatches=0 |
| no duplicate chunks after re-index | PASS | total=825 unique=825 |
| deterministic chunk multiset on re-index | PASS | prev=825 new=825 |
| deterministic relationship multiset on re-index | PASS | prev=0 new=0 |
| deterministic call multiset on re-index | PASS | prev=0 new=0 |
| no duplicate relations after re-index | PASS | total=0 unique=0 |
| no cross-snapshot leakage after re-index | PASS | cross=0 |
| stable graph API output ordering | PASS | nodes=8 |

## Metrics

```json
{
  "repository_id": "fefc4049-b9ed-4995-bf8d-478a71921b94",
  "snapshot_id": "f04aca69-53c2-49c0-b26f-b80def1307be",
  "commit_sha": "adbc8813901bba65827259daa8e22ff94ec1f30e",
  "indexing_duration_seconds": 5.08,
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
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "documentation",
      "n": 18,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "configuration",
      "n": 6,
      "binaries": 0
    },
    {
      "support_level": "skip",
      "language": null,
      "n": 6,
      "binaries": 1
    }
  ],
  "chunks": {
    "total": 825,
    "verified_deep": 0,
    "llm_enriched": 0,
    "unique_spans": 825,
    "with_parser": 825
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
  "nodes_by_type": {},
  "edges_by_kind": {},
  "edges_by_confidence": {},
  "call_totals": {
    "total": 0,
    "resolved": 0,
    "ambiguous": 0,
    "unresolved": 0
  },
  "inheritance_counts": [],
  "symbol_totals": {
    "total": 0,
    "fake_deep": 0
  },
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
        "verified_deep": false
      },
      {
        "path": "active_help_test.go",
        "start_line": 29,
        "end_line": 82,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "active_help_test.go",
        "start_line": 84,
        "end_line": 167,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "active_help_test.go",
        "start_line": 169,
        "end_line": 229,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "active_help_test.go",
        "start_line": 231,
        "end_line": 264,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false
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
        "verified_deep": false
      },
      {
        "path": "active_help_test.go",
        "start_line": 84,
        "end_line": 167,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "active_help_test.go",
        "start_line": 169,
        "end_line": 229,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "active_help_test.go",
        "start_line": 231,
        "end_line": 264,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "active_help_test.go",
        "start_line": 266,
        "end_line": 317,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false
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
        "verified_deep": false
      },
      {
        "path": "active_help_test.go",
        "start_line": 266,
        "end_line": 317,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "bash_completions.go",
        "start_line": 29,
        "end_line": 34,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "bash_completions.go",
        "start_line": 116,
        "end_line": 195,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "bash_completions.go",
        "start_line": 196,
        "end_line": 275,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false
      }
    ],
    "citation_ok": true,
    "notes": []
  }
]
```

## Graphs

```json
{
  "modules": {
    "node_count": 0,
    "edge_count": 0,
    "graph_type": "modules",
    "snapshot_id": "f04aca69-53c2-49c0-b26f-b80def1307be",
    "filters": {
      "local_imports_only": false,
      "max_nodes": 500,
      "max_edges": 2000
    },
    "sample_nodes": [],
    "sample_edges": []
  },
  "packages": {
    "node_count": 0,
    "edge_count": 0,
    "graph_type": "packages",
    "snapshot_id": "f04aca69-53c2-49c0-b26f-b80def1307be",
    "filters": {
      "local_imports_only": true,
      "max_nodes": 500,
      "max_edges": 2000
    },
    "sample_nodes": [],
    "sample_edges": []
  },
  "directories": {
    "node_count": 8,
    "edge_count": 7,
    "graph_type": "directories",
    "snapshot_id": "f04aca69-53c2-49c0-b26f-b80def1307be",
    "filters": {
      "include_files": false,
      "max_nodes": 500,
      "max_edges": 2000
    },
    "sample_nodes": [
      {
        "id": ".",
        "label": "/",
        "node_type": "directory",
        "language": null,
        "support_level": "generic",
        "path": null,
        "symbol_count": 0,
        "file_count": 32,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": ".github",
        "label": ".github",
        "node_type": "directory",
        "language": null,
        "support_level": "generic",
        "path": null,
        "symbol_count": 0,
        "file_count": 2,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": ".github/workflows",
        "label": ".github/workflows",
        "node_type": "directory",
        "language": null,
        "support_level": "generic",
        "path": null,
        "symbol_count": 0,
        "file_count": 2,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "doc",
        "label": "doc",
        "node_type": "directory",
        "language": null,
        "support_level": "generic",
        "path": null,
        "symbol_count": 0,
        "file_count": 11,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "site",
        "label": "site",
        "node_type": "directory",
        "language": null,
        "support_level": "generic",
        "path": null,
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      }
    ],
    "sample_edges": [
      {
        "source": ".",
        "target": ".github",
        "relation_kind": "contains",
        "confidence": "resolved",
        "language": null,
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": ".",
        "target": "doc",
        "relation_kind": "contains",
        "confidence": "resolved",
        "language": null,
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": ".",
        "target": "site",
        "relation_kind": "contains",
        "confidence": "resolved",
        "language": null,
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": ".github",
        "target": ".github/workflows",
        "relation_kind": "contains",
        "confidence": "resolved",
        "language": null,
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "site",
        "target": "site/content",
        "relation_kind": "contains",
        "confidence": "resolved",
        "language": null,
        "weight": 1,
        "inferred": false,
        "line": null
      }
    ]
  },
  "generic_calls_honesty": {
    "go_symbols": 0,
    "go_calls": 0
  }
}
```

## Callers / callees samples

```json
{}
```

## Inheritance / implementations

```json
{
  "skipped": "not applicable"
}
```

## API filters

```json
{
  "invalid_support_level": {
    "_http_status": 422,
    "_body": "{\"detail\":{\"code\":\"invalid_support_level\",\"message\":\"support_level must be deep, generic, mixed, or skip\"}}"
  },
  "invalid_confidence": {
    "_http_status": 422,
    "_body": "{\"detail\":{\"code\":\"invalid_confidence\",\"message\":\"confidence must be resolved, ambiguous, or unresolved\"}}"
  },
  "capped_directories": {
    "node_count": 5,
    "edge_count": 4,
    "filters": {
      "include_files": false,
      "max_nodes": 5,
      "max_edges": 5
    }
  },
  "path_prefix_src": {
    "node_count": 0,
    "edge_count": 0
  },
  "inferred_false": {
    "node_count": 8,
    "edge_count": 7,
    "inferred_edges_remaining": 0
  }
}
```

## React Flow UI (static + API-backed)

```json
{
  "loads_from_api": true,
  "no_fixture_data_in_page": true,
  "has_relation_filters": true,
  "has_language_filter": true,
  "has_support_level_filter": true,
  "has_depth_control": true,
  "has_generic_honesty_notice": true,
  "has_inferred_edge_styling": true,
  "selection_detail_panel": true,
  "uses_xyflow": true,
  "api_graphs_exercised": [
    "modules",
    "packages",
    "directories",
    "generic_calls_honesty"
  ],
  "note": "React Flow page loads graph endpoints via apps/web/src/lib/api.ts; validated statically + via live API responses used by that page."
}
```

## Re-index

```json
{
  "repository_id": "fefc4049-b9ed-4995-bf8d-478a71921b94",
  "snapshot_id": "f04aca69-53c2-49c0-b26f-b80def1307be",
  "commit_sha": "adbc8813901bba65827259daa8e22ff94ec1f30e",
  "status": "SUCCEEDED",
  "indexing_duration_seconds": 5.04,
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
    "with_parser": 825
  },
  "edges_by_kind": {},
  "call_totals": {
    "total": 0,
    "resolved": 0,
    "ambiguous": 0,
    "unresolved": 0
  },
  "chunk_multiset_equal": true,
  "relation_multiset_equal": true,
  "call_multiset_equal": true,
  "file_hash_mismatches": 0
}
```

## Failures and limitations

- None

## Recommendation before Week 9

- Proceed; no repo-specific blockers.
