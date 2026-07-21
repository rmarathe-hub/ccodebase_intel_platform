# Generalization validation — C# — Humanizr/Humanizer

- URL: https://github.com/Humanizr/Humanizer
- Generated: 2026-07-20T03:09:50.179029+00:00
- API: `http://127.0.0.1:8001`
- LLM enrichment: **OFF**
- Clone size limit: 52428800 bytes (unchanged)

## Checks

| Check | Result | Detail |
| --- | --- | --- |
| repository imported successfully | PASS | status=SUCCEEDED err=None:None |
| snapshot created | PASS | 0a4a78ef-8ebb-4d4b-838b-cdafaf7214c6 |
| files discovered | PASS | total=692 skipped=88 binaries=44 |
| chunks persisted | PASS | chunks=2029 unique_spans=2029 |
| no duplicate chunk spans | PASS | total=2029 unique=2029 |
| parser provenance stored | PASS | with_parser_name=2029 with_version=2029 |
| optional enrichment OFF | PASS | llm_enriched=0 |
| no fake verified symbols for non-deep langs | PASS | fake_deep=0 |
| generic-primary: verified_deep not claimed repository-wide | PASS | verified_deep_chunks=7 (incidental deep files allowed=False) |
| generic-primary: no deep c# symbols | PASS | symbol_totals={'total': 14, 'fake_deep': 0} |
| expected generic languages present in chunks | PASS | chunk_langs=['c#', 'configuration', 'documentation', 'python'] expected=['c#'] |
| deterministic repository summary | PASS | llm_summary_status=disabled |
| exact chunk search operational | PASS | Humanize→459; Pluralize→52; DateHumanize→79; TimeSpan→137 |
| relation kinds only from unified model | PASS | kinds={'imports': 7} |
| no orphan from_symbol dangling IDs | PASS | orphans=0 |
| no orphan to_symbol dangling IDs | PASS | orphans=0 |
| no cross-snapshot relation leakage | PASS | cross=0 |
| no duplicate structural relation keys | PASS | total=7 unique=7 |
| modules graph endpoint ok | PASS | nodes=8 edges=7 |
| modules graph no host path leakage | PASS | leaked=0 |
| packages graph endpoint ok | PASS | nodes=1 edges=0 |
| packages graph no host path leakage | PASS | leaked=0 |
| directory graph usable | PASS | nodes=119 edges=118 |
| directories graph no host path leakage | PASS | leaked=0 |
| generic c#: no invented verified call graph | PASS | c#_symbols=0 c#_calls=0 |
| invalid filter returns validation error | PASS | status=422 body={"detail":{"code":"invalid_support_level","message":"support_level must be deep, generic, mixed, or skip"}} |
| invalid confidence rejected | PASS | status=422 |
| graph node/edge limits applied | PASS | nodes=5 edges=4 |
| path_prefix filter accepted | PASS | nodes=27 |
| inferred=false filter respected | PASS | inferred_remaining=0 total_edges=118 |
| React Flow page wired to live graph APIs | PASS | {"loads_from_api": true, "no_fixture_data_in_page": true, "has_relation_filters": true, "has_language_filter": true, "has_support_level_filter": true, "has_depth_control": true, "has_generic_honesty_notice": true, "has_inferred_edge_styling": true, "selection_detail_panel": true, "uses_xyflow": true} |
| generic honesty notice present in Graph UI | PASS | GraphPage honesty copy checked |
| no regex structural parsing in chunking package | PASS | offenders=[] |
| re-index succeeded | PASS | status=SUCCEEDED duration_s=10.0 |
| stable content hashes on re-index | PASS | common=604 mismatches=0 |
| no duplicate chunks after re-index | PASS | total=2029 unique=2029 |
| deterministic chunk multiset on re-index | PASS | prev=2029 new=2029 |
| deterministic relationship multiset on re-index | PASS | prev=7 new=7 |
| deterministic call multiset on re-index | PASS | prev=55 new=55 |
| no duplicate relations after re-index | PASS | total=7 unique=7 |
| no cross-snapshot leakage after re-index | PASS | cross=0 |
| stable graph API output ordering | PASS | nodes=50 |

## Metrics

```json
{
  "repository_id": "10497f4e-c9a0-4ef2-89a2-848a1b755adb",
  "snapshot_id": "0a4a78ef-8ebb-4d4b-838b-cdafaf7214c6",
  "commit_sha": "f9292aa90948de0aea2d4fa7d6549b1b2432c0fb",
  "indexing_duration_seconds": 10.04,
  "files": {
    "total": 692,
    "skipped": 88,
    "binaries": 44,
    "distinct_hashes": 600
  },
  "files_by_lang_level": [
    {
      "support_level": "generic",
      "language": "c#",
      "n": 454,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "configuration",
      "n": 106,
      "binaries": 0
    },
    {
      "support_level": "skip",
      "language": null,
      "n": 88,
      "binaries": 44
    },
    {
      "support_level": "generic",
      "language": "documentation",
      "n": 41,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "html",
      "n": 1,
      "binaries": 0
    },
    {
      "support_level": "deep",
      "language": "python",
      "n": 1,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "css",
      "n": 1,
      "binaries": 0
    }
  ],
  "chunks": {
    "total": 2029,
    "verified_deep": 7,
    "llm_enriched": 0,
    "unique_spans": 2029,
    "with_parser": 2029,
    "with_parser_version": 2029
  },
  "chunk_breakdown": [
    {
      "language": "c#",
      "support_level": "generic",
      "extraction_method": "line_window_fallback",
      "parser_name": "csharp-treesitter",
      "n": 703
    },
    {
      "language": "c#",
      "support_level": "generic",
      "extraction_method": "treesitter_node",
      "parser_name": "csharp-treesitter",
      "n": 667
    },
    {
      "language": "documentation",
      "support_level": "generic",
      "extraction_method": "markdown_ast",
      "parser_name": "mistune-ast",
      "n": 400
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "yaml-compose",
      "n": 230
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "json-stdlib",
      "n": 22
    },
    {
      "language": "python",
      "support_level": "deep",
      "extraction_method": "deep_symbol",
      "parser_name": "python-ast",
      "n": 7
    }
  ],
  "nodes_by_type": {
    "python:function": 7,
    "python:import": 7
  },
  "edges_by_kind": {
    "imports": 7
  },
  "edges_by_confidence": {
    "unresolved": 7
  },
  "call_totals": {
    "total": 55,
    "resolved": 8,
    "ambiguous": 0,
    "unresolved": 47
  },
  "inheritance_counts": [],
  "symbol_totals": {
    "total": 14,
    "fake_deep": 0
  },
  "language_mix": {
    "c#": 454,
    "configuration": 106,
    "documentation": 41,
    "html": 1,
    "css": 1,
    "python": 1
  }
}
```

## Exact search

```json
[
  {
    "query": "Humanize",
    "total": 459,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "AGENTS.md",
        "start_line": 6,
        "end_line": 9,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "AGENTS.md",
        "start_line": 10,
        "end_line": 15,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "AGENTS.md",
        "start_line": 26,
        "end_line": 30,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "AGENTS.md",
        "start_line": 31,
        "end_line": 37,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "AGENTS.md",
        "start_line": 38,
        "end_line": 42,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "Pluralize",
    "total": 52,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "docs/locale-yaml-how-to.md",
        "start_line": 215,
        "end_line": 409,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "docs/locale-yaml-reference.md",
        "start_line": 141,
        "end_line": 521,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "docs/locale-yaml-reference.md",
        "start_line": 1166,
        "end_line": 2058,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "docs/quick-start.md",
        "start_line": 63,
        "end_line": 72,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "docs/quick-start.md",
        "start_line": 159,
        "end_line": 170,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "DateHumanize",
    "total": 79,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "ARCHITECTURE.md",
        "start_line": 15,
        "end_line": 69,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "docs/extensibility.md",
        "start_line": 146,
        "end_line": 166,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "docs/migration-v3.md",
        "start_line": 55,
        "end_line": 150,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "docs/migration-v3.md",
        "start_line": 151,
        "end_line": 212,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "src/Benchmarks/FormatterBenchmarks.cs",
        "start_line": 7,
        "end_line": 45,
        "language": "c#",
        "support_level": "generic",
        "verified_deep": false
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "TimeSpan",
    "total": 137,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "docs/_config.yml",
        "start_line": 3,
        "end_line": 3,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "docs/extensibility.md",
        "start_line": 146,
        "end_line": 166,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "docs/index.md",
        "start_line": 1,
        "end_line": 4,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "docs/index.md",
        "start_line": 22,
        "end_line": 28,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "docs/locale-yaml-how-to.md",
        "start_line": 215,
        "end_line": 409,
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
    "node_count": 8,
    "edge_count": 7,
    "graph_type": "modules",
    "snapshot_id": "0a4a78ef-8ebb-4d4b-838b-cdafaf7214c6",
    "filters": {
      "local_imports_only": false,
      "max_nodes": 500,
      "max_edges": 2000
    },
    "sample_nodes": [
      {
        "id": ".agents.skills.add-locale-batch.scripts.locale_batch_status",
        "label": ".agents.skills.add-locale-batch.scripts.locale_batch_status",
        "node_type": "module",
        "language": "python",
        "support_level": "deep",
        "path": ".agents/skills/add-locale-batch/scripts/locale_batch_status.py",
        "symbol_count": 7,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
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
        "id": "argparse",
        "label": "argparse",
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
        "id": "json",
        "label": "json",
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
        "id": "pathlib",
        "label": "pathlib",
        "node_type": "module",
        "language": "python",
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
        "source": ".agents.skills.add-locale-batch.scripts.locale_batch_status",
        "target": "__future__",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": ".agents.skills.add-locale-batch.scripts.locale_batch_status",
        "target": "argparse",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": ".agents.skills.add-locale-batch.scripts.locale_batch_status",
        "target": "json",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": ".agents.skills.add-locale-batch.scripts.locale_batch_status",
        "target": "pathlib",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": ".agents.skills.add-locale-batch.scripts.locale_batch_status",
        "target": "subprocess",
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
    "node_count": 1,
    "edge_count": 0,
    "graph_type": "packages",
    "snapshot_id": "0a4a78ef-8ebb-4d4b-838b-cdafaf7214c6",
    "filters": {
      "local_imports_only": true,
      "max_nodes": 500,
      "max_edges": 2000
    },
    "sample_nodes": [
      {
        "id": ".agents.skills.add-locale-batch.scripts",
        "label": ".agents.skills.add-locale-batch.scripts",
        "node_type": "package",
        "language": "python",
        "support_level": "deep",
        "path": null,
        "symbol_count": 7,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      }
    ],
    "sample_edges": []
  },
  "directories": {
    "node_count": 119,
    "edge_count": 118,
    "graph_type": "directories",
    "snapshot_id": "0a4a78ef-8ebb-4d4b-838b-cdafaf7214c6",
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
        "file_count": 8,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": ".agents",
        "label": ".agents",
        "node_type": "directory",
        "language": null,
        "support_level": "mixed",
        "path": null,
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": ".agents/skills",
        "label": ".agents/skills",
        "node_type": "directory",
        "language": null,
        "support_level": "mixed",
        "path": null,
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": ".agents/skills/add-locale",
        "label": ".agents/skills/add-locale",
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
        "id": ".agents/skills/add-locale-batch",
        "label": ".agents/skills/add-locale-batch",
        "node_type": "directory",
        "language": null,
        "support_level": "mixed",
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
        "target": ".agents",
        "relation_kind": "contains",
        "confidence": "resolved",
        "language": null,
        "weight": 1,
        "inferred": false,
        "line": null
      },
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
        "target": "docs",
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
        "target": "tests",
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
    "language": "c#",
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
    "node_count": 27,
    "edge_count": 26
  },
  "inferred_false": {
    "node_count": 119,
    "edge_count": 118,
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
  "repository_id": "10497f4e-c9a0-4ef2-89a2-848a1b755adb",
  "snapshot_id": "0a4a78ef-8ebb-4d4b-838b-cdafaf7214c6",
  "commit_sha": "f9292aa90948de0aea2d4fa7d6549b1b2432c0fb",
  "status": "SUCCEEDED",
  "indexing_duration_seconds": 10.04,
  "files": {
    "total": 692,
    "skipped": 88,
    "binaries": 44,
    "distinct_hashes": 600
  },
  "chunks": {
    "total": 2029,
    "verified_deep": 7,
    "llm_enriched": 0,
    "distinct_content_hashes": 2011,
    "unique_spans": 2029,
    "with_parser": 2029,
    "with_parser_version": 2029
  },
  "edges_by_kind": {
    "imports": 7
  },
  "call_totals": {
    "total": 55,
    "resolved": 8,
    "ambiguous": 0,
    "unresolved": 47
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
