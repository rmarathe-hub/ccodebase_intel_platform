# Generalization validation — C++ — fmtlib/fmt

- URL: https://github.com/fmtlib/fmt
- Generated: 2026-07-20T03:09:39.359190+00:00
- API: `http://127.0.0.1:8001`
- LLM enrichment: **OFF**
- Clone size limit: 52428800 bytes (unchanged)

## Checks

| Check | Result | Detail |
| --- | --- | --- |
| repository imported successfully | PASS | status=SUCCEEDED err=None:None |
| snapshot created | PASS | f97b564e-a470-40d3-8935-bc45460490ed |
| files discovered | PASS | total=142 skipped=24 binaries=1 |
| chunks persisted | PASS | chunks=3052 unique_spans=3052 |
| no duplicate chunk spans | PASS | total=3052 unique=3052 |
| parser provenance stored | PASS | with_parser_name=3052 with_version=3052 |
| optional enrichment OFF | PASS | llm_enriched=0 |
| no fake verified symbols for non-deep langs | PASS | fake_deep=0 |
| generic-primary: verified_deep not claimed repository-wide | PASS | verified_deep_chunks=106 (incidental deep files allowed=False) |
| generic-primary: no deep c++ symbols | PASS | symbol_totals={'total': 138, 'fake_deep': 0} |
| expected generic languages present in chunks | PASS | chunk_langs=['c', 'c++', 'configuration', 'documentation', 'python'] expected=['c++'] |
| deterministic repository summary | PASS | llm_summary_status=disabled |
| exact chunk search operational | PASS | format→838; formatter→124; print→413; fmt→957 |
| relation kinds only from unified model | PASS | kinds={'contains': 50, 'imports': 32} |
| no orphan from_symbol dangling IDs | PASS | orphans=0 |
| no orphan to_symbol dangling IDs | PASS | orphans=0 |
| no cross-snapshot relation leakage | PASS | cross=0 |
| no duplicate structural relation keys | PASS | total=82 unique=82 |
| modules graph endpoint ok | PASS | nodes=24 edges=25 |
| modules graph no host path leakage | PASS | leaked=0 |
| packages graph endpoint ok | PASS | nodes=3 edges=0 |
| packages graph no host path leakage | PASS | leaked=0 |
| directory graph usable | PASS | nodes=22 edges=21 |
| directories graph no host path leakage | PASS | leaked=0 |
| generic c++: no invented verified call graph | PASS | c++_symbols=0 c++_calls=0 |
| invalid filter returns validation error | PASS | status=422 body={"detail":{"code":"invalid_support_level","message":"support_level must be deep, generic, mixed, or skip"}} |
| invalid confidence rejected | PASS | status=422 |
| graph node/edge limits applied | PASS | nodes=5 edges=4 |
| path_prefix filter accepted | PASS | nodes=1 |
| inferred=false filter respected | PASS | inferred_remaining=0 total_edges=21 |
| React Flow page wired to live graph APIs | PASS | {"loads_from_api": true, "no_fixture_data_in_page": true, "has_relation_filters": true, "has_language_filter": true, "has_support_level_filter": true, "has_depth_control": true, "has_generic_honesty_notice": true, "has_inferred_edge_styling": true, "selection_detail_panel": true, "uses_xyflow": true} |
| generic honesty notice present in Graph UI | PASS | GraphPage honesty copy checked |
| no regex structural parsing in chunking package | PASS | offenders=[] |
| re-index succeeded | PASS | status=SUCCEEDED duration_s=5.0 |
| stable content hashes on re-index | PASS | common=118 mismatches=0 |
| no duplicate chunks after re-index | PASS | total=3052 unique=3052 |
| deterministic chunk multiset on re-index | PASS | prev=3052 new=3052 |
| deterministic relationship multiset on re-index | PASS | prev=82 new=82 |
| deterministic call multiset on re-index | PASS | prev=451 new=451 |
| no duplicate relations after re-index | PASS | total=82 unique=82 |
| no cross-snapshot leakage after re-index | PASS | cross=0 |
| stable graph API output ordering | PASS | nodes=22 |

## Metrics

```json
{
  "repository_id": "5efde7f2-bd6c-4acb-9a0c-547adf03db2e",
  "snapshot_id": "f97b564e-a470-40d3-8935-bc45460490ed",
  "commit_sha": "b5d1e5404bd678df41f20d0f053222a6c60fe74b",
  "indexing_duration_seconds": 5.07,
  "files": {
    "total": 142,
    "skipped": 24,
    "binaries": 1,
    "distinct_hashes": 118
  },
  "files_by_lang_level": [
    {
      "support_level": "generic",
      "language": "c++",
      "n": 46,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "c",
      "n": 26,
      "binaries": 0
    },
    {
      "support_level": "skip",
      "language": null,
      "n": 24,
      "binaries": 1
    },
    {
      "support_level": "generic",
      "language": "configuration",
      "n": 22,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "documentation",
      "n": 17,
      "binaries": 0
    },
    {
      "support_level": "deep",
      "language": "python",
      "n": 4,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "shell",
      "n": 1,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "css",
      "n": 1,
      "binaries": 0
    },
    {
      "support_level": "deep",
      "language": "javascript",
      "n": 1,
      "binaries": 0
    }
  ],
  "chunks": {
    "total": 3052,
    "verified_deep": 106,
    "llm_enriched": 0,
    "unique_spans": 3052,
    "with_parser": 3052,
    "with_parser_version": 3052
  },
  "chunk_breakdown": [
    {
      "language": "c",
      "support_level": "generic",
      "extraction_method": "treesitter_node",
      "parser_name": "c-treesitter",
      "n": 1755
    },
    {
      "language": "c++",
      "support_level": "generic",
      "extraction_method": "treesitter_node",
      "parser_name": "cpp-treesitter",
      "n": 738
    },
    {
      "language": "c++",
      "support_level": "generic",
      "extraction_method": "line_window_fallback",
      "parser_name": "cpp-treesitter",
      "n": 143
    },
    {
      "language": "documentation",
      "support_level": "generic",
      "extraction_method": "markdown_ast",
      "parser_name": "mistune-ast",
      "n": 131
    },
    {
      "language": "c",
      "support_level": "generic",
      "extraction_method": "line_window_fallback",
      "parser_name": "c-treesitter",
      "n": 107
    },
    {
      "language": "python",
      "support_level": "deep",
      "extraction_method": "deep_symbol",
      "parser_name": "python-ast",
      "n": 106
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "yaml-compose",
      "n": 72
    }
  ],
  "nodes_by_type": {
    "python:method": 50,
    "python:function": 37,
    "python:import": 32,
    "python:class": 19
  },
  "edges_by_kind": {
    "contains": 50,
    "imports": 32
  },
  "edges_by_confidence": {
    "resolved": 50,
    "unresolved": 32
  },
  "call_totals": {
    "total": 451,
    "resolved": 105,
    "ambiguous": 0,
    "unresolved": 346
  },
  "inheritance_counts": [],
  "symbol_totals": {
    "total": 138,
    "fake_deep": 0
  },
  "language_mix": {
    "c++": 46,
    "c": 26,
    "configuration": 22,
    "documentation": 17,
    "python": 4,
    "css": 1,
    "shell": 1,
    "javascript": 1
  }
}
```

## Exact search

```json
[
  {
    "query": "format",
    "total": 838,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "ChangeLog.md",
        "start_line": 1,
        "end_line": 223,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "ChangeLog.md",
        "start_line": 224,
        "end_line": 297,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "ChangeLog.md",
        "start_line": 298,
        "end_line": 470,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "ChangeLog.md",
        "start_line": 471,
        "end_line": 571,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "ChangeLog.md",
        "start_line": 572,
        "end_line": 598,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "formatter",
    "total": 124,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "ChangeLog.md",
        "start_line": 1,
        "end_line": 223,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "ChangeLog.md",
        "start_line": 224,
        "end_line": 297,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "ChangeLog.md",
        "start_line": 298,
        "end_line": 470,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "ChangeLog.md",
        "start_line": 599,
        "end_line": 631,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "ChangeLog.md",
        "start_line": 632,
        "end_line": 656,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "print",
    "total": 413,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "ChangeLog.md",
        "start_line": 1,
        "end_line": 223,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "ChangeLog.md",
        "start_line": 298,
        "end_line": 470,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "ChangeLog.md",
        "start_line": 471,
        "end_line": 571,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "ChangeLog.md",
        "start_line": 666,
        "end_line": 891,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "ChangeLog.md",
        "start_line": 919,
        "end_line": 939,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "fmt",
    "total": 957,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "ChangeLog.md",
        "start_line": 1,
        "end_line": 223,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "ChangeLog.md",
        "start_line": 224,
        "end_line": 297,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "ChangeLog.md",
        "start_line": 298,
        "end_line": 470,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "ChangeLog.md",
        "start_line": 471,
        "end_line": 571,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "ChangeLog.md",
        "start_line": 572,
        "end_line": 598,
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
    "node_count": 24,
    "edge_count": 25,
    "graph_type": "modules",
    "snapshot_id": "f97b564e-a470-40d3-8935-bc45460490ed",
    "filters": {
      "local_imports_only": false,
      "max_nodes": 500,
      "max_edges": 2000
    },
    "sample_nodes": [
      {
        "id": "__future__",
        "label": "__future__",
        "node_type": "module",
        "language": "python",
        "support_level": "generic",
        "path": null,
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "collections",
        "label": "collections",
        "node_type": "module",
        "language": "python",
        "support_level": "generic",
        "path": null,
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "csv",
        "label": "csv",
        "node_type": "module",
        "language": "python",
        "support_level": "generic",
        "path": null,
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "datetime",
        "label": "datetime",
        "node_type": "module",
        "language": "python",
        "support_level": "generic",
        "path": null,
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "doc.fmt",
        "label": "doc.fmt",
        "node_type": "module",
        "language": "javascript",
        "support_level": "deep",
        "path": "doc/fmt.js",
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      }
    ],
    "sample_edges": [
      {
        "source": "support.docopt",
        "target": "re",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "support.docopt",
        "target": "sys",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "support.printable",
        "target": "collections",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "support.printable",
        "target": "csv",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "support.printable",
        "target": "os",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": null
      }
    ]
  },
  "packages": {
    "node_count": 3,
    "edge_count": 0,
    "graph_type": "packages",
    "snapshot_id": "f97b564e-a470-40d3-8935-bc45460490ed",
    "filters": {
      "local_imports_only": true,
      "max_nodes": 500,
      "max_edges": 2000
    },
    "sample_nodes": [
      {
        "id": "doc",
        "label": "doc",
        "node_type": "package",
        "language": "javascript",
        "support_level": "deep",
        "path": null,
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "support",
        "label": "support",
        "node_type": "package",
        "language": "python",
        "support_level": "deep",
        "path": null,
        "symbol_count": 87,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "support.python.mkdocstrings_handlers",
        "label": "support.python.mkdocstrings_handlers",
        "node_type": "package",
        "language": "python",
        "support_level": "deep",
        "path": null,
        "symbol_count": 19,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      }
    ],
    "sample_edges": []
  },
  "directories": {
    "node_count": 22,
    "edge_count": 21,
    "graph_type": "directories",
    "snapshot_id": "f97b564e-a470-40d3-8935-bc45460490ed",
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
        "support_level": "mixed",
        "path": null,
        "symbol_count": 0,
        "file_count": 5,
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
        "file_count": 5,
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
        "file_count": 9,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "doc",
        "label": "doc",
        "node_type": "directory",
        "language": null,
        "support_level": "mixed",
        "path": null,
        "symbol_count": 0,
        "file_count": 7,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "include",
        "label": "include",
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
        "target": "include",
        "relation_kind": "contains",
        "confidence": "resolved",
        "language": null,
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": ".",
        "target": "src",
        "relation_kind": "contains",
        "confidence": "resolved",
        "language": null,
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": ".",
        "target": "support",
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
    "language": "c++",
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
    "node_count": 1,
    "edge_count": 0
  },
  "inferred_false": {
    "node_count": 22,
    "edge_count": 21,
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
  "repository_id": "5efde7f2-bd6c-4acb-9a0c-547adf03db2e",
  "snapshot_id": "f97b564e-a470-40d3-8935-bc45460490ed",
  "commit_sha": "b5d1e5404bd678df41f20d0f053222a6c60fe74b",
  "status": "SUCCEEDED",
  "indexing_duration_seconds": 5.02,
  "files": {
    "total": 142,
    "skipped": 24,
    "binaries": 1,
    "distinct_hashes": 118
  },
  "chunks": {
    "total": 3052,
    "verified_deep": 106,
    "llm_enriched": 0,
    "distinct_content_hashes": 2908,
    "unique_spans": 3052,
    "with_parser": 3052,
    "with_parser_version": 3052
  },
  "edges_by_kind": {
    "contains": 50,
    "imports": 32
  },
  "call_totals": {
    "total": 451,
    "resolved": 105,
    "ambiguous": 0,
    "unresolved": 346
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
