# Generalization validation — Go — go-chi/chi

- URL: https://github.com/go-chi/chi
- Generated: 2026-07-20T03:07:04.048802+00:00
- API: `http://127.0.0.1:8001`
- LLM enrichment: **OFF**
- Clone size limit: 52428800 bytes (unchanged)

## Checks

| Check | Result | Detail |
| --- | --- | --- |
| repository imported successfully | PASS | status=SUCCEEDED err=None:None |
| snapshot created | PASS | be02a4b4-be2b-4531-bdfb-205c87d6182b |
| files discovered | PASS | total=99 skipped=9 binaries=1 |
| chunks persisted | PASS | chunks=577 unique_spans=577 |
| no duplicate chunk spans | PASS | total=577 unique=577 |
| parser provenance stored | PASS | with_parser_name=577 with_version=577 |
| optional enrichment OFF | PASS | llm_enriched=0 |
| no fake verified symbols for non-deep langs | PASS | fake_deep=0 |
| generic-primary: verified_deep not claimed repository-wide | PASS | verified_deep_chunks=0 (incidental deep files allowed=False) |
| generic-primary: no deep go symbols | PASS | symbol_totals={'total': 0, 'fake_deep': 0} |
| expected generic languages present in chunks | PASS | chunk_langs=['configuration', 'documentation', 'go'] expected=['go'] |
| deterministic repository summary | PASS | llm_summary_status=disabled |
| exact chunk search operational | PASS | Router→136; Route→185; middleware→90; chi→150 |
| relation kinds only from unified model | PASS | kinds={} |
| no orphan from_symbol dangling IDs | PASS | orphans=0 |
| no orphan to_symbol dangling IDs | PASS | orphans=0 |
| no cross-snapshot relation leakage | PASS | cross=0 |
| no duplicate structural relation keys | PASS | total=0 unique=0 |
| modules graph endpoint ok | PASS | nodes=0 edges=0 |
| modules graph no host path leakage | PASS | leaked=0 |
| packages graph endpoint ok | PASS | nodes=0 edges=0 |
| packages graph no host path leakage | PASS | leaked=0 |
| directory graph usable | PASS | nodes=23 edges=22 |
| directories graph no host path leakage | PASS | leaked=0 |
| generic go: no invented verified call graph | PASS | go_symbols=0 go_calls=0 |
| invalid filter returns validation error | PASS | status=422 body={"detail":{"code":"invalid_support_level","message":"support_level must be deep, generic, mixed, or skip"}} |
| invalid confidence rejected | PASS | status=422 |
| graph node/edge limits applied | PASS | nodes=5 edges=4 |
| path_prefix filter accepted | PASS | nodes=0 |
| inferred=false filter respected | PASS | inferred_remaining=0 total_edges=22 |
| React Flow page wired to live graph APIs | PASS | {"loads_from_api": true, "no_fixture_data_in_page": true, "has_relation_filters": true, "has_language_filter": true, "has_support_level_filter": true, "has_depth_control": true, "has_generic_honesty_notice": true, "has_inferred_edge_styling": true, "selection_detail_panel": true, "uses_xyflow": true} |
| generic honesty notice present in Graph UI | PASS | GraphPage honesty copy checked |
| no regex structural parsing in chunking package | PASS | offenders=[] |
| re-index succeeded | PASS | status=SUCCEEDED duration_s=5.0 |
| stable content hashes on re-index | PASS | common=90 mismatches=0 |
| no duplicate chunks after re-index | PASS | total=577 unique=577 |
| deterministic chunk multiset on re-index | PASS | prev=577 new=577 |
| deterministic relationship multiset on re-index | PASS | prev=0 new=0 |
| deterministic call multiset on re-index | PASS | prev=0 new=0 |
| no duplicate relations after re-index | PASS | total=0 unique=0 |
| no cross-snapshot leakage after re-index | PASS | cross=0 |
| stable graph API output ordering | PASS | nodes=23 |

## Metrics

```json
{
  "repository_id": "3e1c1fb4-ca53-4495-ab45-a7cd9346d601",
  "snapshot_id": "be02a4b4-be2b-4531-bdfb-205c87d6182b",
  "commit_sha": "8b258c7bb28f97a5f2a856ff7ef962578fec9215",
  "indexing_duration_seconds": 5.04,
  "files": {
    "total": 99,
    "skipped": 9,
    "binaries": 1,
    "distinct_hashes": 90
  },
  "files_by_lang_level": [
    {
      "support_level": "generic",
      "language": "go",
      "n": 78,
      "binaries": 0
    },
    {
      "support_level": "skip",
      "language": null,
      "n": 9,
      "binaries": 1
    },
    {
      "support_level": "generic",
      "language": "documentation",
      "n": 8,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "configuration",
      "n": 4,
      "binaries": 0
    }
  ],
  "chunks": {
    "total": 577,
    "verified_deep": 0,
    "llm_enriched": 0,
    "unique_spans": 577,
    "with_parser": 577,
    "with_parser_version": 577
  },
  "chunk_breakdown": [
    {
      "language": "go",
      "support_level": "generic",
      "extraction_method": "treesitter_node",
      "parser_name": "go-treesitter",
      "n": 496
    },
    {
      "language": "documentation",
      "support_level": "generic",
      "extraction_method": "markdown_ast",
      "parser_name": "mistune-ast",
      "n": 64
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "yaml-compose",
      "n": 16
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "json-stdlib",
      "n": 1
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
    "go": 78,
    "documentation": 8,
    "configuration": 4
  }
}
```

## Exact search

```json
[
  {
    "query": "Router",
    "total": 136,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "CHANGELOG.md",
        "start_line": 104,
        "end_line": 154,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 162,
        "end_line": 169,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 205,
        "end_line": 214,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 215,
        "end_line": 221,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 228,
        "end_line": 234,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "Route",
    "total": 185,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "CHANGELOG.md",
        "start_line": 104,
        "end_line": 154,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 155,
        "end_line": 161,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 162,
        "end_line": 169,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 205,
        "end_line": 214,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 215,
        "end_line": 221,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "middleware",
    "total": 90,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "chain.go",
        "start_line": 6,
        "end_line": 8,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "chain.go",
        "start_line": 12,
        "end_line": 14,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "chain.go",
        "start_line": 18,
        "end_line": 20,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "chain.go",
        "start_line": 24,
        "end_line": 28,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "chain.go",
        "start_line": 36,
        "end_line": 49,
        "language": "go",
        "support_level": "generic",
        "verified_deep": false
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "chi",
    "total": 150,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "CHANGELOG.md",
        "start_line": 3,
        "end_line": 7,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 8,
        "end_line": 12,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 13,
        "end_line": 18,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 19,
        "end_line": 23,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 24,
        "end_line": 28,
        "language": "documentation",
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
    "snapshot_id": "be02a4b4-be2b-4531-bdfb-205c87d6182b",
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
    "snapshot_id": "be02a4b4-be2b-4531-bdfb-205c87d6182b",
    "filters": {
      "local_imports_only": true,
      "max_nodes": 500,
      "max_edges": 2000
    },
    "sample_nodes": [],
    "sample_edges": []
  },
  "directories": {
    "node_count": 23,
    "edge_count": 22,
    "graph_type": "directories",
    "snapshot_id": "be02a4b4-be2b-4531-bdfb-205c87d6182b",
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
        "file_count": 16,
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
        "file_count": 1,
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
        "file_count": 1,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "_examples",
        "label": "_examples",
        "node_type": "directory",
        "language": null,
        "support_level": "generic",
        "path": null,
        "symbol_count": 0,
        "file_count": 1,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "_examples/custom-handler",
        "label": "_examples/custom-handler",
        "node_type": "directory",
        "language": null,
        "support_level": "generic",
        "path": null,
        "symbol_count": 0,
        "file_count": 1,
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
        "target": "_examples",
        "relation_kind": "contains",
        "confidence": "resolved",
        "language": null,
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": ".",
        "target": "middleware",
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
        "source": "_examples",
        "target": "_examples/custom-handler",
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
    "language": "go",
    "symbols": 0,
    "calls": 0
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
    "node_count": 23,
    "edge_count": 22,
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
  "repository_id": "3e1c1fb4-ca53-4495-ab45-a7cd9346d601",
  "snapshot_id": "be02a4b4-be2b-4531-bdfb-205c87d6182b",
  "commit_sha": "8b258c7bb28f97a5f2a856ff7ef962578fec9215",
  "status": "SUCCEEDED",
  "indexing_duration_seconds": 5.04,
  "files": {
    "total": 99,
    "skipped": 9,
    "binaries": 1,
    "distinct_hashes": 90
  },
  "chunks": {
    "total": 577,
    "verified_deep": 0,
    "llm_enriched": 0,
    "distinct_content_hashes": 573,
    "unique_spans": 577,
    "with_parser": 577,
    "with_parser_version": 577
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

## Recommendation

- No repo-specific blockers.

## Pass/fail: **PASS**

- Checks passed: 42/42
- Checks failed: 0
