# Generalization validation — Rust — clap-rs/clap

- URL: https://github.com/clap-rs/clap
- Generated: 2026-07-20T03:07:09.563620+00:00
- API: `http://127.0.0.1:8001`
- LLM enrichment: **OFF**
- Clone size limit: 52428800 bytes (unchanged)

## Checks

| Check | Result | Detail |
| --- | --- | --- |
| repository imported successfully | PASS | status=SUCCEEDED err=None:None |
| snapshot created | PASS | 17829468-7dfa-4473-9ff9-8a47c415efc0 |
| files discovered | PASS | total=619 skipped=148 binaries=8 |
| chunks persisted | PASS | chunks=4468 unique_spans=4468 |
| no duplicate chunk spans | PASS | total=4468 unique=4468 |
| parser provenance stored | PASS | with_parser_name=4468 with_version=4468 |
| optional enrichment OFF | PASS | llm_enriched=0 |
| no fake verified symbols for non-deep langs | PASS | fake_deep=0 |
| generic-primary: verified_deep not claimed repository-wide | PASS | verified_deep_chunks=1 (incidental deep files allowed=False) |
| generic-primary: no deep rust symbols | PASS | symbol_totals={'total': 5, 'fake_deep': 0} |
| expected generic languages present in chunks | PASS | chunk_langs=['configuration', 'documentation', 'python', 'rust', 'shell'] expected=['rust'] |
| deterministic repository summary | PASS | llm_summary_status=disabled |
| exact chunk search operational | PASS | Command→2003; Arg→2221; Parser→666; clap→1247 |
| relation kinds only from unified model | PASS | kinds={'imports': 4} |
| no orphan from_symbol dangling IDs | PASS | orphans=0 |
| no orphan to_symbol dangling IDs | PASS | orphans=0 |
| no cross-snapshot relation leakage | PASS | cross=0 |
| no duplicate structural relation keys | PASS | total=4 unique=4 |
| modules graph endpoint ok | PASS | nodes=5 edges=4 |
| modules graph no host path leakage | PASS | leaked=0 |
| packages graph endpoint ok | PASS | nodes=1 edges=0 |
| packages graph no host path leakage | PASS | leaked=0 |
| directory graph usable | PASS | nodes=60 edges=59 |
| directories graph no host path leakage | PASS | leaked=0 |
| generic rust: no invented verified call graph | PASS | rust_symbols=0 rust_calls=0 |
| invalid filter returns validation error | PASS | status=422 body={"detail":{"code":"invalid_support_level","message":"support_level must be deep, generic, mixed, or skip"}} |
| invalid confidence rejected | PASS | status=422 |
| graph node/edge limits applied | PASS | nodes=5 edges=4 |
| path_prefix filter accepted | PASS | nodes=4 |
| inferred=false filter respected | PASS | inferred_remaining=0 total_edges=59 |
| React Flow page wired to live graph APIs | PASS | {"loads_from_api": true, "no_fixture_data_in_page": true, "has_relation_filters": true, "has_language_filter": true, "has_support_level_filter": true, "has_depth_control": true, "has_generic_honesty_notice": true, "has_inferred_edge_styling": true, "selection_detail_panel": true, "uses_xyflow": true} |
| generic honesty notice present in Graph UI | PASS | GraphPage honesty copy checked |
| no regex structural parsing in chunking package | PASS | offenders=[] |
| re-index succeeded | PASS | status=SUCCEEDED duration_s=5.0 |
| stable content hashes on re-index | PASS | common=471 mismatches=0 |
| no duplicate chunks after re-index | PASS | total=4468 unique=4468 |
| deterministic chunk multiset on re-index | PASS | prev=4468 new=4468 |
| deterministic relationship multiset on re-index | PASS | prev=4 new=4 |
| deterministic call multiset on re-index | PASS | prev=17 new=17 |
| no duplicate relations after re-index | PASS | total=4 unique=4 |
| no cross-snapshot leakage after re-index | PASS | cross=0 |
| stable graph API output ordering | PASS | nodes=50 |

## Metrics

```json
{
  "repository_id": "c0e8754a-d06b-48be-a146-a1634a763bfe",
  "snapshot_id": "17829468-7dfa-4473-9ff9-8a47c415efc0",
  "commit_sha": "0838e824e6d91e49c9c75fa7c5447e05178da560",
  "indexing_duration_seconds": 5.05,
  "files": {
    "total": 619,
    "skipped": 148,
    "binaries": 8,
    "distinct_hashes": 466
  },
  "files_by_lang_level": [
    {
      "support_level": "generic",
      "language": "rust",
      "n": 329,
      "binaries": 0
    },
    {
      "support_level": "skip",
      "language": null,
      "n": 148,
      "binaries": 8
    },
    {
      "support_level": "generic",
      "language": "documentation",
      "n": 73,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "configuration",
      "n": 37,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "shell",
      "n": 31,
      "binaries": 0
    },
    {
      "support_level": "deep",
      "language": "python",
      "n": 1,
      "binaries": 0
    }
  ],
  "chunks": {
    "total": 4468,
    "verified_deep": 1,
    "llm_enriched": 0,
    "unique_spans": 4468,
    "with_parser": 4468,
    "with_parser_version": 4468
  },
  "chunk_breakdown": [
    {
      "language": "rust",
      "support_level": "generic",
      "extraction_method": "treesitter_node",
      "parser_name": "rust-treesitter",
      "n": 2892
    },
    {
      "language": "documentation",
      "support_level": "generic",
      "extraction_method": "markdown_ast",
      "parser_name": "mistune-ast",
      "n": 1057
    },
    {
      "language": "rust",
      "support_level": "generic",
      "extraction_method": "line_window_fallback",
      "parser_name": "rust-treesitter",
      "n": 204
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "tomllib",
      "n": 184
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "yaml-compose",
      "n": 99
    },
    {
      "language": "shell",
      "support_level": "generic",
      "extraction_method": "treesitter_node",
      "parser_name": "bash-treesitter",
      "n": 31
    },
    {
      "language": "python",
      "support_level": "deep",
      "extraction_method": "deep_symbol",
      "parser_name": "python-ast",
      "n": 1
    }
  ],
  "nodes_by_type": {
    "python:import": 4,
    "python:function": 1
  },
  "edges_by_kind": {
    "imports": 4
  },
  "edges_by_confidence": {
    "unresolved": 4
  },
  "call_totals": {
    "total": 17,
    "resolved": 0,
    "ambiguous": 0,
    "unresolved": 17
  },
  "inheritance_counts": [],
  "symbol_totals": {
    "total": 5,
    "fake_deep": 0
  },
  "language_mix": {
    "rust": 329,
    "documentation": 73,
    "configuration": 37,
    "shell": 31,
    "python": 1
  }
}
```

## Exact search

```json
[
  {
    "query": "Command",
    "total": 2003,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "Cargo.toml",
        "start_line": 109,
        "end_line": 126,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "Cargo.toml",
        "start_line": 324,
        "end_line": 329,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "Cargo.toml",
        "start_line": 445,
        "end_line": 450,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "Cargo.toml",
        "start_line": 451,
        "end_line": 456,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "Cargo.toml",
        "start_line": 512,
        "end_line": 517,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "Arg",
    "total": 2221,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "Cargo.toml",
        "start_line": 13,
        "end_line": 26,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "Cargo.toml",
        "start_line": 36,
        "end_line": 99,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "Cargo.toml",
        "start_line": 103,
        "end_line": 108,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "Cargo.toml",
        "start_line": 109,
        "end_line": 126,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "Cargo.toml",
        "start_line": 127,
        "end_line": 130,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "Parser",
    "total": 666,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "Cargo.toml",
        "start_line": 109,
        "end_line": 126,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 243,
        "end_line": 248,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 286,
        "end_line": 291,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 292,
        "end_line": 297,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 304,
        "end_line": 309,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "clap",
    "total": 1247,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "Cargo.toml",
        "start_line": 1,
        "end_line": 12,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "Cargo.toml",
        "start_line": 13,
        "end_line": 26,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "Cargo.toml",
        "start_line": 109,
        "end_line": 126,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "Cargo.toml",
        "start_line": 134,
        "end_line": 147,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "Cargo.toml",
        "start_line": 148,
        "end_line": 183,
        "language": "configuration",
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
    "node_count": 5,
    "edge_count": 4,
    "graph_type": "modules",
    "snapshot_id": "17829468-7dfa-4473-9ff9-8a47c415efc0",
    "filters": {
      "local_imports_only": false,
      "max_nodes": 500,
      "max_edges": 2000
    },
    "sample_nodes": [
      {
        "id": ".github.workflows.release-notes",
        "label": ".github.workflows.release-notes",
        "node_type": "module",
        "language": "python",
        "support_level": "deep",
        "path": ".github/workflows/release-notes.py",
        "symbol_count": 1,
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
      },
      {
        "id": "re",
        "label": "re",
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
        "id": "sys",
        "label": "sys",
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
        "source": ".github.workflows.release-notes",
        "target": "argparse",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": ".github.workflows.release-notes",
        "target": "pathlib",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": ".github.workflows.release-notes",
        "target": "re",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": ".github.workflows.release-notes",
        "target": "sys",
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
    "snapshot_id": "17829468-7dfa-4473-9ff9-8a47c415efc0",
    "filters": {
      "local_imports_only": true,
      "max_nodes": 500,
      "max_edges": 2000
    },
    "sample_nodes": [
      {
        "id": ".github.workflows",
        "label": ".github.workflows",
        "node_type": "package",
        "language": "python",
        "support_level": "deep",
        "path": null,
        "symbol_count": 1,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      }
    ],
    "sample_edges": []
  },
  "directories": {
    "node_count": 60,
    "edge_count": 59,
    "graph_type": "directories",
    "snapshot_id": "17829468-7dfa-4473-9ff9-8a47c415efc0",
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
        "file_count": 11,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": ".cargo",
        "label": ".cargo",
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
        "id": ".github",
        "label": ".github",
        "node_type": "directory",
        "language": null,
        "support_level": "mixed",
        "path": null,
        "symbol_count": 0,
        "file_count": 3,
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
        "file_count": 3,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": ".github/workflows",
        "label": ".github/workflows",
        "node_type": "directory",
        "language": null,
        "support_level": "mixed",
        "path": null,
        "symbol_count": 0,
        "file_count": 10,
        "symbol_id": null,
        "kind": null
      }
    ],
    "sample_edges": [
      {
        "source": ".",
        "target": ".cargo",
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
        "target": "clap_bench",
        "relation_kind": "contains",
        "confidence": "resolved",
        "language": null,
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": ".",
        "target": "clap_builder",
        "relation_kind": "contains",
        "confidence": "resolved",
        "language": null,
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": ".",
        "target": "clap_complete",
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
    "language": "rust",
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
    "node_count": 4,
    "edge_count": 3
  },
  "inferred_false": {
    "node_count": 60,
    "edge_count": 59,
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
  "repository_id": "c0e8754a-d06b-48be-a146-a1634a763bfe",
  "snapshot_id": "17829468-7dfa-4473-9ff9-8a47c415efc0",
  "commit_sha": "0838e824e6d91e49c9c75fa7c5447e05178da560",
  "status": "SUCCEEDED",
  "indexing_duration_seconds": 5.04,
  "files": {
    "total": 619,
    "skipped": 148,
    "binaries": 8,
    "distinct_hashes": 466
  },
  "chunks": {
    "total": 4468,
    "verified_deep": 1,
    "llm_enriched": 0,
    "distinct_content_hashes": 4310,
    "unique_spans": 4468,
    "with_parser": 4468,
    "with_parser_version": 4468
  },
  "edges_by_kind": {
    "imports": 4
  },
  "call_totals": {
    "total": 17,
    "resolved": 0,
    "ambiguous": 0,
    "unresolved": 17
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
