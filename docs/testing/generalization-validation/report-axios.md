# Generalization validation — JavaScript — axios/axios

- URL: https://github.com/axios/axios
- Generated: 2026-07-20T03:06:42.710889+00:00
- API: `http://127.0.0.1:8001`
- LLM enrichment: **OFF**
- Clone size limit: 52428800 bytes (unchanged)

## Checks

| Check | Result | Detail |
| --- | --- | --- |
| repository imported successfully | PASS | status=SUCCEEDED err=None:None |
| snapshot created | PASS | 5411ad68-75d7-4ebf-a01f-0222618bddec |
| files discovered | PASS | total=456 skipped=54 binaries=39 |
| chunks persisted | PASS | chunks=2006 unique_spans=2006 |
| no duplicate chunk spans | PASS | total=2006 unique=2006 |
| parser provenance stored | PASS | with_parser_name=2006 with_version=2006 |
| optional enrichment OFF | PASS | llm_enriched=0 |
| no fake verified symbols for non-deep langs | PASS | fake_deep=0 |
| deep analysis for expected languages | PASS | symbol_langs=['javascript', 'typescript'] verified_deep_chunks=725 |
| deterministic repository summary | PASS | llm_summary_status=disabled |
| exact chunk search operational | PASS | axios→998; request→590; interceptor→146; adapter→130 |
| relation kinds only from unified model | PASS | kinds={'imports': 912, 'contains': 192, 'exports': 27} |
| no orphan from_symbol dangling IDs | PASS | orphans=0 |
| no orphan to_symbol dangling IDs | PASS | orphans=0 |
| no cross-snapshot relation leakage | PASS | cross=0 |
| no duplicate structural relation keys | PASS | total=1131 unique=1131 |
| IMPORTS/CONTAINS present for deep repo | PASS | edges={'imports': 912, 'contains': 192, 'exports': 27} |
| CALLS persisted with resolution labels | PASS | resolved=289 ambiguous=5 unresolved=1514 |
| modules graph returns | PASS | nodes=294 edges=588 |
| modules graph no host path leakage | PASS | leaked=0 |
| packages graph returns | PASS | nodes=161 edges=115 |
| packages graph no host path leakage | PASS | leaked=0 |
| directory graph usable | PASS | nodes=82 edges=142 |
| directories graph no host path leakage | PASS | leaked=0 |
| callers/callees neighborhood API | PASS | center=lib.adapters.fetch.factory d1_nodes=16 |
| call edges carry confidence labels | PASS | confidences_seen=['resolved'] |
| ambiguous call symbols present | PASS | lib.core.Axios.Axios._request |
| unresolved/external calls present or documented | PASS | unresolved_samples=5 |
| symbol with no callers found | PASS | count=3 |
| callers/callees list endpoints | PASS | callers=1 callees=20 |
| invalid filter returns validation error | PASS | status=422 body={"detail":{"code":"invalid_support_level","message":"support_level must be deep, generic, mixed, or skip"}} |
| invalid confidence rejected | PASS | status=422 |
| graph node/edge limits applied | PASS | nodes=5 edges=4 |
| path_prefix filter accepted | PASS | nodes=0 |
| language filter on modules | PASS | requested=typescript seen=['typescript'] |
| inferred=false filter respected | PASS | inferred_remaining=0 total_edges=81 |
| React Flow page wired to live graph APIs | PASS | {"loads_from_api": true, "no_fixture_data_in_page": true, "has_relation_filters": true, "has_language_filter": true, "has_support_level_filter": true, "has_depth_control": true, "has_generic_honesty_notice": true, "has_inferred_edge_styling": true, "selection_detail_panel": true, "uses_xyflow": true} |
| generic honesty notice present in Graph UI | PASS | GraphPage honesty copy checked |
| no regex structural parsing in chunking package | PASS | offenders=[] |
| re-index succeeded | PASS | status=SUCCEEDED duration_s=10.1 |
| stable content hashes on re-index | PASS | common=402 mismatches=0 |
| no duplicate chunks after re-index | PASS | total=2006 unique=2006 |
| deterministic chunk multiset on re-index | PASS | prev=2006 new=2006 |
| deterministic relationship multiset on re-index | PASS | prev=1131 new=1131 |
| deterministic call multiset on re-index | PASS | prev=1808 new=1808 |
| no duplicate relations after re-index | PASS | total=1131 unique=1131 |
| no cross-snapshot leakage after re-index | PASS | cross=0 |
| stable graph API output ordering | PASS | nodes=50 |

## Metrics

```json
{
  "repository_id": "b2895b93-3e0c-4673-9e07-b403d5a906e0",
  "snapshot_id": "5411ad68-75d7-4ebf-a01f-0222618bddec",
  "commit_sha": "c44f8d0a910df99486da9175584b99f56a94a73b",
  "indexing_duration_seconds": 5.05,
  "files": {
    "total": 456,
    "skipped": 54,
    "binaries": 39,
    "distinct_hashes": 401
  },
  "files_by_lang_level": [
    {
      "support_level": "deep",
      "language": "javascript",
      "n": 205,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "documentation",
      "n": 134,
      "binaries": 0
    },
    {
      "support_level": "skip",
      "language": null,
      "n": 54,
      "binaries": 39
    },
    {
      "support_level": "generic",
      "language": "configuration",
      "n": 28,
      "binaries": 0
    },
    {
      "support_level": "deep",
      "language": "typescript",
      "n": 25,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "html",
      "n": 9,
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
    "total": 2006,
    "verified_deep": 725,
    "llm_enriched": 0,
    "unique_spans": 2006,
    "with_parser": 2006,
    "with_parser_version": 2006
  },
  "chunk_breakdown": [
    {
      "language": "documentation",
      "support_level": "generic",
      "extraction_method": "markdown_ast",
      "parser_name": "mistune-ast",
      "n": 1091
    },
    {
      "language": "javascript",
      "support_level": "deep",
      "extraction_method": "deep_symbol",
      "parser_name": "javascript-treesitter",
      "n": 580
    },
    {
      "language": "typescript",
      "support_level": "deep",
      "extraction_method": "deep_symbol",
      "parser_name": "typescript-treesitter",
      "n": 145
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "json-stdlib",
      "n": 120
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "yaml-compose",
      "n": 70
    }
  ],
  "nodes_by_type": {
    "javascript:import": 797,
    "javascript:function": 354,
    "javascript:method": 190,
    "typescript:import": 115,
    "typescript:function": 52,
    "typescript:interface": 48,
    "typescript:type_alias": 37,
    "javascript:class": 36,
    "javascript:export": 27,
    "typescript:class": 6,
    "typescript:method": 2
  },
  "edges_by_kind": {
    "imports": 912,
    "contains": 192,
    "exports": 27
  },
  "edges_by_confidence": {
    "ambiguous": 331,
    "resolved": 507,
    "unresolved": 293
  },
  "call_totals": {
    "total": 1808,
    "resolved": 289,
    "ambiguous": 5,
    "unresolved": 1514
  },
  "inheritance_counts": [],
  "symbol_totals": {
    "total": 1664,
    "fake_deep": 0
  },
  "language_mix": {
    "javascript": 205,
    "documentation": 134,
    "configuration": 28,
    "typescript": 25,
    "html": 9,
    "css": 1
  }
}
```

## Exact search

```json
[
  {
    "query": "axios",
    "total": 998,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "AGENTS.md",
        "start_line": 1,
        "end_line": 6,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "AGENTS.md",
        "start_line": 29,
        "end_line": 36,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "AGENTS.md",
        "start_line": 43,
        "end_line": 50,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "AGENTS.md",
        "start_line": 51,
        "end_line": 57,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "AGENTS.md",
        "start_line": 58,
        "end_line": 64,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "request",
    "total": 590,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "AGENTS.md",
        "start_line": 7,
        "end_line": 10,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "AGENTS.md",
        "start_line": 43,
        "end_line": 50,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "AGENTS.md",
        "start_line": 51,
        "end_line": 57,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "AGENTS.md",
        "start_line": 58,
        "end_line": 64,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "AGENTS.md",
        "start_line": 65,
        "end_line": 71,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "interceptor",
    "total": 146,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "AGENTS.md",
        "start_line": 43,
        "end_line": 50,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "AGENTS.md",
        "start_line": 51,
        "end_line": 57,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "AGENTS.md",
        "start_line": 65,
        "end_line": 71,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "AGENTS.md",
        "start_line": 72,
        "end_line": 83,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 96,
        "end_line": 104,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "adapter",
    "total": 130,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "AGENTS.md",
        "start_line": 1,
        "end_line": 6,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "AGENTS.md",
        "start_line": 43,
        "end_line": 50,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "AGENTS.md",
        "start_line": 72,
        "end_line": 83,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "AGENTS.md",
        "start_line": 105,
        "end_line": 113,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 7,
        "end_line": 12,
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
    "node_count": 294,
    "edge_count": 588,
    "graph_type": "modules",
    "snapshot_id": "5411ad68-75d7-4ebf-a01f-0222618bddec",
    "filters": {
      "local_imports_only": false,
      "max_nodes": 500,
      "max_edges": 2000
    },
    "sample_nodes": [
      {
        "id": "@eslint/js",
        "label": "@eslint/js",
        "node_type": "module",
        "language": "javascript",
        "support_level": "generic",
        "path": null,
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "@rollup/plugin-alias",
        "label": "@rollup/plugin-alias",
        "node_type": "module",
        "language": "javascript",
        "support_level": "generic",
        "path": null,
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "@rollup/plugin-babel",
        "label": "@rollup/plugin-babel",
        "node_type": "module",
        "language": "javascript",
        "support_level": "generic",
        "path": null,
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "@rollup/plugin-commonjs",
        "label": "@rollup/plugin-commonjs",
        "node_type": "module",
        "language": "javascript",
        "support_level": "generic",
        "path": null,
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "@rollup/plugin-json",
        "label": "@rollup/plugin-json",
        "node_type": "module",
        "language": "javascript",
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
        "source": "docs..vitepress.theme",
        "target": "docs..vitepress.theme.style",
        "relation_kind": "imports",
        "confidence": "ambiguous",
        "language": "typescript",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "docs..vitepress.theme",
        "target": "vitepress",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "typescript",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "docs..vitepress.theme",
        "target": "vitepress/theme",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "typescript",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "docs..vitepress.theme",
        "target": "vue",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "typescript",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "docs.scripts.process-sponsors",
        "target": "axios",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": null
      }
    ]
  },
  "packages": {
    "node_count": 161,
    "edge_count": 115,
    "graph_type": "packages",
    "snapshot_id": "5411ad68-75d7-4ebf-a01f-0222618bddec",
    "filters": {
      "local_imports_only": true,
      "max_nodes": 500,
      "max_edges": 2000
    },
    "sample_nodes": [
      {
        "id": "docs..vitepress",
        "label": "docs..vitepress",
        "node_type": "package",
        "language": "typescript",
        "support_level": "deep",
        "path": null,
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "docs.scripts",
        "label": "docs.scripts",
        "node_type": "package",
        "language": "javascript",
        "support_level": "deep",
        "path": null,
        "symbol_count": 9,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "eslint",
        "label": "eslint",
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
        "id": "examples",
        "label": "examples",
        "node_type": "package",
        "language": "javascript",
        "support_level": "deep",
        "path": null,
        "symbol_count": 8,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "examples.abort-controller",
        "label": "examples.abort-controller",
        "node_type": "package",
        "language": "javascript",
        "support_level": "deep",
        "path": null,
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      }
    ],
    "sample_edges": [
      {
        "source": "gulpfile",
        "target": "scripts",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": true,
        "line": null
      },
      {
        "source": "index",
        "target": "lib",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": true,
        "line": null
      },
      {
        "source": "lib",
        "target": "lib.adapters",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": true,
        "line": null
      },
      {
        "source": "lib",
        "target": "lib.cancel",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 3,
        "inferred": true,
        "line": null
      },
      {
        "source": "lib",
        "target": "lib.core",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 5,
        "inferred": true,
        "line": null
      }
    ]
  },
  "directories": {
    "node_count": 82,
    "edge_count": 142,
    "graph_type": "directories",
    "snapshot_id": "5411ad68-75d7-4ebf-a01f-0222618bddec",
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
        "file_count": 26,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": ".devcontainer",
        "label": ".devcontainer",
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
        "file_count": 8,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "docs",
        "label": "docs",
        "node_type": "directory",
        "language": null,
        "support_level": "mixed",
        "path": null,
        "symbol_count": 0,
        "file_count": 3,
        "symbol_id": null,
        "kind": null
      }
    ],
    "sample_edges": [
      {
        "source": ".",
        "target": ".devcontainer",
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
        "target": "examples",
        "relation_kind": "contains",
        "confidence": "resolved",
        "language": null,
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": ".",
        "target": "lib",
        "relation_kind": "contains",
        "confidence": "resolved",
        "language": null,
        "weight": 1,
        "inferred": false,
        "line": null
      }
    ]
  },
  "calls_depth_1": {
    "center": "lib.adapters.fetch.factory",
    "node_count": 16,
    "edge_count": 24,
    "depth": 1,
    "sample_edges": [
      {
        "source": "4669bb64-df5b-4981-8469-1d38c96ddfa4",
        "target": "0112f02a-c0cf-48d8-9b30-a19df0c9e52e",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": 439
      },
      {
        "source": "4669bb64-df5b-4981-8469-1d38c96ddfa4",
        "target": "0112f02a-c0cf-48d8-9b30-a19df0c9e52e",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": 543
      },
      {
        "source": "4669bb64-df5b-4981-8469-1d38c96ddfa4",
        "target": "07b66271-56b0-41a4-bb14-2bfa7b6b4df8",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": 257
      },
      {
        "source": "4669bb64-df5b-4981-8469-1d38c96ddfa4",
        "target": "07b66271-56b0-41a4-bb14-2bfa7b6b4df8",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": 258
      },
      {
        "source": "4669bb64-df5b-4981-8469-1d38c96ddfa4",
        "target": "1b50447c-3a25-445c-826a-0bed5aec52b3",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": 367
      },
      {
        "source": "4669bb64-df5b-4981-8469-1d38c96ddfa4",
        "target": "1b50447c-3a25-445c-826a-0bed5aec52b3",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": 473
      },
      {
        "source": "4669bb64-df5b-4981-8469-1d38c96ddfa4",
        "target": "30dd7c51-3a5c-41e0-9e8c-ade2a788ddfc",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": 360
      },
      {
        "source": "4669bb64-df5b-4981-8469-1d38c96ddfa4",
        "target": "30dd7c51-3a5c-41e0-9e8c-ade2a788ddfc",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": 409
      }
    ]
  },
  "calls_depth_2": {
    "center": "lib.adapters.fetch.factory",
    "node_count": 28,
    "edge_count": 56,
    "depth": 2,
    "sample_edges": [
      {
        "source": "07b66271-56b0-41a4-bb14-2bfa7b6b4df8",
        "target": "d93abe20-764b-4a3d-aea3-86e882076dfb",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": 60
      },
      {
        "source": "158363b8-a81c-4cca-9d65-4981e6a767ab",
        "target": "07b66271-56b0-41a4-bb14-2bfa7b6b4df8",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": 46
      },
      {
        "source": "158363b8-a81c-4cca-9d65-4981e6a767ab",
        "target": "07b66271-56b0-41a4-bb14-2bfa7b6b4df8",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": 47
      },
      {
        "source": "2011da57-f278-4532-8086-3204250a704f",
        "target": "30dd7c51-3a5c-41e0-9e8c-ade2a788ddfc",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": 112
      },
      {
        "source": "4669bb64-df5b-4981-8469-1d38c96ddfa4",
        "target": "0112f02a-c0cf-48d8-9b30-a19df0c9e52e",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": 439
      },
      {
        "source": "4669bb64-df5b-4981-8469-1d38c96ddfa4",
        "target": "0112f02a-c0cf-48d8-9b30-a19df0c9e52e",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": 543
      },
      {
        "source": "4669bb64-df5b-4981-8469-1d38c96ddfa4",
        "target": "07b66271-56b0-41a4-bb14-2bfa7b6b4df8",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": 257
      },
      {
        "source": "4669bb64-df5b-4981-8469-1d38c96ddfa4",
        "target": "07b66271-56b0-41a4-bb14-2bfa7b6b4df8",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": 258
      }
    ]
  },
  "callers_api": {
    "total": 1,
    "sample": [
      {
        "id": "1151c0ed-eb05-43aa-84ac-51cf77d5284f",
        "snapshot_id": "5411ad68-75d7-4ebf-a01f-0222618bddec",
        "source_file_id": "7bedd932-2fde-44a1-81ae-e14b06dd21cb",
        "path": "lib/adapters/fetch.js",
        "caller_symbol_id": "9636c1c5-8015-4544-95fc-5ac8c22c4214",
        "caller_qualified_name": "lib.adapters.fetch.getFetch",
        "raw_callee": "factory",
        "qualified_expression": "factory",
        "line": 633,
        "candidate_qualified_name": "lib.adapters.fetch.factory",
        "confidence": "resolved",
        "language": "javascript",
        "created_at": "2026-07-20T03:05:25.197600Z"
      }
    ]
  },
  "callees_api": {
    "total": 20,
    "sample": [
      {
        "id": "d4a3f1f7-85b6-4269-8204-51824565a601",
        "snapshot_id": "5411ad68-75d7-4ebf-a01f-0222618bddec",
        "source_file_id": "7bedd932-2fde-44a1-81ae-e14b06dd21cb",
        "path": "lib/adapters/fetch.js",
        "caller_symbol_id": "4669bb64-df5b-4981-8469-1d38c96ddfa4",
        "caller_qualified_name": "lib.adapters.fetch.factory",
        "raw_callee": "utils.merge.call",
        "qualified_expression": "utils.merge.call",
        "line": 75,
        "candidate_qualified_name": null,
        "confidence": "unresolved",
        "language": "javascript",
        "created_at": "2026-07-20T03:05:25.197600Z"
      },
      {
        "id": "907d468f-b208-4e04-8f64-29a5d1509825",
        "snapshot_id": "5411ad68-75d7-4ebf-a01f-0222618bddec",
        "source_file_id": "7bedd932-2fde-44a1-81ae-e14b06dd21cb",
        "path": "lib/adapters/fetch.js",
        "caller_symbol_id": "4669bb64-df5b-4981-8469-1d38c96ddfa4",
        "caller_qualified_name": "lib.adapters.fetch.factory",
        "raw_callee": "isFunction",
        "qualified_expression": "isFunction",
        "line": 87,
        "candidate_qualified_name": null,
        "confidence": "unresolved",
        "language": "javascript",
        "created_at": "2026-07-20T03:05:25.197600Z"
      },
      {
        "id": "dcd0e917-95d2-4047-a9f9-9a0831e2587a",
        "snapshot_id": "5411ad68-75d7-4ebf-a01f-0222618bddec",
        "source_file_id": "7bedd932-2fde-44a1-81ae-e14b06dd21cb",
        "path": "lib/adapters/fetch.js",
        "caller_symbol_id": "4669bb64-df5b-4981-8469-1d38c96ddfa4",
        "caller_qualified_name": "lib.adapters.fetch.factory",
        "raw_callee": "isFunction",
        "qualified_expression": "isFunction",
        "line": 88,
        "candidate_qualified_name": null,
        "confidence": "unresolved",
        "language": "javascript",
        "created_at": "2026-07-20T03:05:25.197600Z"
      },
      {
        "id": "f972db57-47b1-459c-b11d-0589f1ba62d7",
        "snapshot_id": "5411ad68-75d7-4ebf-a01f-0222618bddec",
        "source_file_id": "7bedd932-2fde-44a1-81ae-e14b06dd21cb",
        "path": "lib/adapters/fetch.js",
        "caller_symbol_id": "4669bb64-df5b-4981-8469-1d38c96ddfa4",
        "caller_qualified_name": "lib.adapters.fetch.factory",
        "raw_callee": "isFunction",
        "qualified_expression": "isFunction",
        "line": 89,
        "candidate_qualified_name": null,
        "confidence": "unresolved",
        "language": "javascript",
        "created_at": "2026-07-20T03:05:25.197600Z"
      },
      {
        "id": "f3dcef8b-cbac-4470-a35e-1ccc39ebf5f6",
        "snapshot_id": "5411ad68-75d7-4ebf-a01f-0222618bddec",
        "source_file_id": "7bedd932-2fde-44a1-81ae-e14b06dd21cb",
        "path": "lib/adapters/fetch.js",
        "caller_symbol_id": "4669bb64-df5b-4981-8469-1d38c96ddfa4",
        "caller_qualified_name": "lib.adapters.fetch.factory",
        "raw_callee": "isFunction",
        "qualified_expression": "isFunction",
        "line": 95,
        "candidate_qualified_name": null,
        "confidence": "unresolved",
        "language": "javascript",
        "created_at": "2026-07-20T03:05:25.197600Z"
      }
    ]
  }
}
```

## Callers / callees samples

```json
{
  "multi_caller": {
    "qn": "lib.defaults.own",
    "callers": 15
  },
  "multi_callee": {
    "qn": "lib.adapters.fetch.factory",
    "callees": 77
  },
  "ambiguous_symbol": {
    "id": "bc074931-3cfd-47e5-b6ab-1d97fdbf5492",
    "qualified_name": "lib.core.Axios.Axios._request",
    "language": "javascript",
    "kind": "method"
  },
  "unresolved_samples": [
    {
      "caller_qualified_name": "gulpfile.getContributors",
      "raw_callee": "axios.get",
      "confidence": "unresolved",
      "line": 29,
      "language": "javascript"
    },
    {
      "caller_qualified_name": "lib.adapters.fetch.getFetch",
      "raw_callee": "map.set",
      "confidence": "unresolved",
      "line": 633,
      "language": "javascript"
    },
    {
      "caller_qualified_name": "lib.adapters.http.setProxy",
      "raw_callee": "readProxyField",
      "confidence": "unresolved",
      "line": 330,
      "language": "javascript"
    },
    {
      "caller_qualified_name": "lib.adapters.http.setProxy",
      "raw_callee": "readProxyField",
      "confidence": "unresolved",
      "line": 330,
      "language": "javascript"
    },
    {
      "caller_qualified_name": "lib.adapters.http.setProxy",
      "raw_callee": "readProxyField",
      "confidence": "unresolved",
      "line": 331,
      "language": "javascript"
    }
  ],
  "no_callers": [
    {
      "id": "82cbd28b-507d-4254-a4e1-d67bf1d32112",
      "qualified_name": "lib.core.AxiosHeaders.AxiosHeaders.concat",
      "kind": "method",
      "language": "javascript"
    },
    {
      "id": "45858017-39cf-4c76-9a2a-9a65af08110e",
      "qualified_name": "lib.helpers.deprecatedMethod.deprecatedMethod",
      "kind": "function",
      "language": "javascript"
    },
    {
      "id": "02c5c8c6-a86d-47f6-a029-ecc74ed13b8a",
      "qualified_name": "lib.helpers.estimateDataURLDecodedBytes.estimatePercentDecodedBase64Bytes",
      "kind": "function",
      "language": "javascript"
    }
  ],
  "multi_caller_symbol": {
    "id": "739c5e9a-4d25-440e-bc83-a1e0a8c4d7b9",
    "qualified_name": "lib.defaults.own",
    "kind": "function",
    "language": "javascript",
    "start_line": 11,
    "end_line": 11
  },
  "multi_callee_symbol": {
    "id": "4669bb64-df5b-4981-8469-1d38c96ddfa4",
    "qualified_name": "lib.adapters.fetch.factory",
    "kind": "function",
    "language": "javascript",
    "start_line": 68,
    "end_line": 614
  }
}
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
  "modules_lang_typescript": {
    "node_count": 36,
    "edge_count": 42,
    "filters": {
      "language": "typescript",
      "local_imports_only": false,
      "max_nodes": 100,
      "max_edges": 200
    }
  },
  "inferred_false": {
    "node_count": 82,
    "edge_count": 81,
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
    "calls_depth_1",
    "calls_depth_2",
    "callers_api",
    "callees_api"
  ],
  "note": "React Flow page loads graph endpoints via apps/web/src/lib/api.ts; validated statically + via live API responses used by that page."
}
```

## Re-index

```json
{
  "repository_id": "b2895b93-3e0c-4673-9e07-b403d5a906e0",
  "snapshot_id": "5411ad68-75d7-4ebf-a01f-0222618bddec",
  "commit_sha": "c44f8d0a910df99486da9175584b99f56a94a73b",
  "status": "SUCCEEDED",
  "indexing_duration_seconds": 10.07,
  "files": {
    "total": 456,
    "skipped": 54,
    "binaries": 39,
    "distinct_hashes": 401
  },
  "chunks": {
    "total": 2006,
    "verified_deep": 725,
    "llm_enriched": 0,
    "distinct_content_hashes": 1788,
    "unique_spans": 2006,
    "with_parser": 2006,
    "with_parser_version": 2006
  },
  "edges_by_kind": {
    "imports": 912,
    "contains": 192,
    "exports": 27
  },
  "call_totals": {
    "total": 1808,
    "resolved": 289,
    "ambiguous": 5,
    "unresolved": 1514
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

- Checks passed: 48/48
- Checks failed: 0
