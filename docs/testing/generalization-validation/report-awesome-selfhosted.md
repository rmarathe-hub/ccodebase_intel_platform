# Generalization validation — Config/Docs — awesome-selfhosted/awesome-selfhosted

- URL: https://github.com/awesome-selfhosted/awesome-selfhosted
- Generated: 2026-07-20T03:07:30.982052+00:00
- API: `http://127.0.0.1:8001`
- LLM enrichment: **OFF**
- Clone size limit: 52428800 bytes (unchanged)

## Checks

| Check | Result | Detail |
| --- | --- | --- |
| repository imported successfully | PASS | status=SUCCEEDED err=None:None |
| snapshot created | PASS | 96886aaf-7291-43ce-b0f7-7041a4cf29d5 |
| files discovered | PASS | total=6 skipped=1 binaries=1 |
| chunks persisted | PASS | chunks=147 unique_spans=147 |
| no duplicate chunk spans | PASS | total=147 unique=147 |
| parser provenance stored | PASS | with_parser_name=147 with_version=147 |
| optional enrichment OFF | PASS | llm_enriched=0 |
| no fake verified symbols for non-deep langs | PASS | fake_deep=0 |
| generic-primary: verified_deep not claimed repository-wide | PASS | verified_deep_chunks=0 (incidental deep files allowed=True) |
| expected generic languages present in chunks | PASS | chunk_langs=['configuration', 'documentation'] expected=['configuration', 'documentation'] |
| deterministic repository summary | PASS | llm_summary_status=disabled |
| exact chunk search operational | PASS | self-hosted→32; docker→102; database→27; monitoring→11 |
| relation kinds only from unified model | PASS | kinds={} |
| no orphan from_symbol dangling IDs | PASS | orphans=0 |
| no orphan to_symbol dangling IDs | PASS | orphans=0 |
| no cross-snapshot relation leakage | PASS | cross=0 |
| no duplicate structural relation keys | PASS | total=0 unique=0 |
| modules graph endpoint ok | PASS | nodes=0 edges=0 |
| modules graph no host path leakage | PASS | leaked=0 |
| packages graph endpoint ok | PASS | nodes=0 edges=0 |
| packages graph no host path leakage | PASS | leaked=0 |
| directory graph usable | PASS | nodes=3 edges=2 |
| directories graph no host path leakage | PASS | leaked=0 |
| config/docs repo: no repository-wide deep call graph claimed | PASS | directory graph primary; incidental deep files allowed |
| invalid filter returns validation error | PASS | status=422 body={"detail":{"code":"invalid_support_level","message":"support_level must be deep, generic, mixed, or skip"}} |
| invalid confidence rejected | PASS | status=422 |
| graph node/edge limits applied | PASS | nodes=3 edges=2 |
| path_prefix filter accepted | PASS | nodes=0 |
| inferred=false filter respected | PASS | inferred_remaining=0 total_edges=2 |
| React Flow page wired to live graph APIs | PASS | {"loads_from_api": true, "no_fixture_data_in_page": true, "has_relation_filters": true, "has_language_filter": true, "has_support_level_filter": true, "has_depth_control": true, "has_generic_honesty_notice": true, "has_inferred_edge_styling": true, "selection_detail_panel": true, "uses_xyflow": true} |
| generic honesty notice present in Graph UI | PASS | GraphPage honesty copy checked |
| no regex structural parsing in chunking package | PASS | offenders=[] |
| re-index succeeded | PASS | status=SUCCEEDED duration_s=5.0 |
| stable content hashes on re-index | PASS | common=5 mismatches=0 |
| no duplicate chunks after re-index | PASS | total=147 unique=147 |
| deterministic chunk multiset on re-index | PASS | prev=147 new=147 |
| deterministic relationship multiset on re-index | PASS | prev=0 new=0 |
| deterministic call multiset on re-index | PASS | prev=0 new=0 |
| no duplicate relations after re-index | PASS | total=0 unique=0 |
| no cross-snapshot leakage after re-index | PASS | cross=0 |
| stable graph API output ordering | PASS | nodes=3 |

## Metrics

```json
{
  "repository_id": "c10a8cfe-ba5f-4948-a108-4d5424ff2ae9",
  "snapshot_id": "96886aaf-7291-43ce-b0f7-7041a4cf29d5",
  "commit_sha": "9f4f907cf300856e15d8af20640f45019ca7fa7b",
  "indexing_duration_seconds": 5.05,
  "files": {
    "total": 6,
    "skipped": 1,
    "binaries": 1,
    "distinct_hashes": 5
  },
  "files_by_lang_level": [
    {
      "support_level": "generic",
      "language": "documentation",
      "n": 4,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "configuration",
      "n": 1,
      "binaries": 0
    },
    {
      "support_level": "skip",
      "language": null,
      "n": 1,
      "binaries": 1
    }
  ],
  "chunks": {
    "total": 147,
    "verified_deep": 0,
    "llm_enriched": 0,
    "unique_spans": 147,
    "with_parser": 147,
    "with_parser_version": 147
  },
  "chunk_breakdown": [
    {
      "language": "documentation",
      "support_level": "generic",
      "extraction_method": "markdown_ast",
      "parser_name": "mistune-ast",
      "n": 145
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "yaml-compose",
      "n": 2
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
    "documentation": 4,
    "configuration": 1
  }
}
```

## Exact search

```json
[
  {
    "query": "self-hosted",
    "total": 32,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "non-free.md",
        "start_line": 76,
        "end_line": 87,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "non-free.md",
        "start_line": 95,
        "end_line": 101,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "non-free.md",
        "start_line": 289,
        "end_line": 295,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "non-free.md",
        "start_line": 296,
        "end_line": 304,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "non-free.md",
        "start_line": 305,
        "end_line": 319,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "docker",
    "total": 102,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "non-free.md",
        "start_line": 53,
        "end_line": 59,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "non-free.md",
        "start_line": 60,
        "end_line": 68,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "non-free.md",
        "start_line": 76,
        "end_line": 87,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "non-free.md",
        "start_line": 88,
        "end_line": 94,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "non-free.md",
        "start_line": 109,
        "end_line": 115,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "database",
    "total": 27,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "non-free.md",
        "start_line": 7,
        "end_line": 50,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "non-free.md",
        "start_line": 125,
        "end_line": 134,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "non-free.md",
        "start_line": 195,
        "end_line": 201,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "README.md",
        "start_line": 15,
        "end_line": 120,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "README.md",
        "start_line": 123,
        "end_line": 164,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "monitoring",
    "total": 11,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "non-free.md",
        "start_line": 125,
        "end_line": 134,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "README.md",
        "start_line": 15,
        "end_line": 120,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "README.md",
        "start_line": 191,
        "end_line": 229,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "README.md",
        "start_line": 287,
        "end_line": 313,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "README.md",
        "start_line": 483,
        "end_line": 502,
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
    "snapshot_id": "96886aaf-7291-43ce-b0f7-7041a4cf29d5",
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
    "snapshot_id": "96886aaf-7291-43ce-b0f7-7041a4cf29d5",
    "filters": {
      "local_imports_only": true,
      "max_nodes": 500,
      "max_edges": 2000
    },
    "sample_nodes": [],
    "sample_edges": []
  },
  "directories": {
    "node_count": 3,
    "edge_count": 2,
    "graph_type": "directories",
    "snapshot_id": "96886aaf-7291-43ce-b0f7-7041a4cf29d5",
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
        "file_count": 3,
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
        "id": ".github/ISSUE_TEMPLATE",
        "label": ".github/ISSUE_TEMPLATE",
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
        "source": ".github",
        "target": ".github/ISSUE_TEMPLATE",
        "relation_kind": "contains",
        "confidence": "resolved",
        "language": null,
        "weight": 1,
        "inferred": false,
        "line": null
      }
    ]
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
    "node_count": 3,
    "edge_count": 2,
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
    "node_count": 3,
    "edge_count": 2,
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
    "directories"
  ],
  "note": "React Flow page loads graph endpoints via apps/web/src/lib/api.ts; validated statically + via live API responses used by that page."
}
```

## Re-index

```json
{
  "repository_id": "c10a8cfe-ba5f-4948-a108-4d5424ff2ae9",
  "snapshot_id": "96886aaf-7291-43ce-b0f7-7041a4cf29d5",
  "commit_sha": "9f4f907cf300856e15d8af20640f45019ca7fa7b",
  "status": "SUCCEEDED",
  "indexing_duration_seconds": 5.03,
  "files": {
    "total": 6,
    "skipped": 1,
    "binaries": 1,
    "distinct_hashes": 5
  },
  "chunks": {
    "total": 147,
    "verified_deep": 0,
    "llm_enriched": 0,
    "distinct_content_hashes": 146,
    "unique_spans": 147,
    "with_parser": 147,
    "with_parser_version": 147
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

- Checks passed: 41/41
- Checks failed: 0
