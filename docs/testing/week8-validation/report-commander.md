# Week 8 validation — TypeScript/JS — tj/commander.js

- URL: https://github.com/tj/commander.js
- Generated: 2026-07-20T02:31:38.869775+00:00
- API: `http://127.0.0.1:8001`
- LLM enrichment: **OFF**
- Clone size limit: 52428800 bytes (unchanged)

## Checks

| Check | Result | Detail |
| --- | --- | --- |
| repository imported successfully | PASS | status=SUCCEEDED err=None:None |
| snapshot created | PASS | a5135786-5aef-4d55-80e1-e7cf35eb60ea |
| files discovered | PASS | total=219 skipped=25 binaries=3 |
| chunks persisted | PASS | chunks=646 unique_spans=646 |
| no duplicate chunk spans | PASS | total=646 unique=646 |
| optional enrichment OFF | PASS | llm_enriched=0 |
| no fake verified symbols for non-deep langs | PASS | fake_deep=0 |
| deep analysis for expected languages | PASS | symbol_langs=['javascript', 'typescript'] verified_deep_chunks=323 |
| deterministic repository summary | PASS | llm_summary_status=disabled |
| exact chunk search operational | PASS | Command→344; Option→304; parse→97 |
| relation kinds only from unified model | PASS | kinds={'imports': 559, 'contains': 197, 'exports': 8} |
| no orphan from_symbol dangling IDs | PASS | orphans=0 |
| no orphan to_symbol dangling IDs | PASS | orphans=0 |
| no cross-snapshot relation leakage | PASS | cross=0 |
| no duplicate structural relation keys | PASS | total=764 unique=764 |
| IMPORTS/CONTAINS present for deep repo | PASS | edges={'imports': 559, 'contains': 197, 'exports': 8} |
| CALLS persisted with resolution labels | PASS | resolved=175 ambiguous=0 unresolved=654 |
| modules graph returns | PASS | nodes=192 edges=415 |
| modules graph no host path leakage | PASS | leaked=0 |
| packages graph returns | PASS | nodes=117 edges=23 |
| packages graph no host path leakage | PASS | leaked=0 |
| directory graph usable | PASS | nodes=10 edges=11 |
| directories graph no host path leakage | PASS | leaked=0 |
| callers/callees neighborhood API | PASS | center=lib.help.Help.formatHelp d1_nodes=3 |
| call edges carry confidence labels | PASS | confidences_seen=['resolved'] |
| ambiguous calls (optional sample) | PASS | no ambiguous calls in this snapshot (acceptable) |
| unresolved/external calls present or documented | PASS | unresolved_samples=5 |
| symbol with no callers found | PASS | count=3 |
| callers/callees list endpoints | PASS | callers=0 callees=20 |
| invalid filter returns validation error | PASS | status=422 body={"detail":{"code":"invalid_support_level","message":"support_level must be deep, generic, mixed, or skip"}} |
| invalid confidence rejected | PASS | status=422 |
| graph node/edge limits applied | PASS | nodes=5 edges=4 |
| path_prefix filter accepted | PASS | nodes=0 |
| language filter on modules | PASS | requested=javascript seen=['javascript'] |
| inferred=false filter respected | PASS | inferred_remaining=0 total_edges=9 |
| React Flow page wired to live graph APIs | PASS | {"loads_from_api": true, "no_fixture_data_in_page": true, "has_relation_filters": true, "has_language_filter": true, "has_support_level_filter": true, "has_depth_control": true, "has_generic_honesty_notice": true, "has_inferred_edge_styling": true, "selection_detail_panel": true, "uses_xyflow": true} |
| generic honesty notice present in Graph UI | PASS | GraphPage honesty copy checked |
| no regex structural parsing in chunking package | PASS | offenders=[] |
| re-index succeeded | PASS | status=SUCCEEDED duration_s=5.1 |
| stable content hashes on re-index | PASS | common=194 mismatches=0 |
| no duplicate chunks after re-index | PASS | total=646 unique=646 |
| deterministic chunk multiset on re-index | PASS | prev=646 new=646 |
| deterministic relationship multiset on re-index | PASS | prev=764 new=764 |
| deterministic call multiset on re-index | PASS | prev=829 new=829 |
| no duplicate relations after re-index | PASS | total=764 unique=764 |
| no cross-snapshot leakage after re-index | PASS | cross=0 |
| stable graph API output ordering | PASS | nodes=10 |

## Metrics

```json
{
  "repository_id": "e0708b2c-eaea-4abe-b457-bb800c784966",
  "snapshot_id": "a5135786-5aef-4d55-80e1-e7cf35eb60ea",
  "commit_sha": "ba6d13ddb4243e5913367734f8c159089ffe7834",
  "indexing_duration_seconds": 5.02,
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
      "binaries": 0
    },
    {
      "support_level": "skip",
      "language": null,
      "n": 25,
      "binaries": 3
    },
    {
      "support_level": "generic",
      "language": "documentation",
      "n": 13,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "configuration",
      "n": 10,
      "binaries": 0
    },
    {
      "support_level": "deep",
      "language": "typescript",
      "n": 3,
      "binaries": 0
    }
  ],
  "chunks": {
    "total": 646,
    "verified_deep": 323,
    "llm_enriched": 0,
    "unique_spans": 646,
    "with_parser": 646
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
  "nodes_by_type": {
    "javascript:import": 557,
    "javascript:method": 195,
    "javascript:function": 78,
    "javascript:class": 20,
    "typescript:interface": 9,
    "javascript:export": 7,
    "typescript:class": 7,
    "typescript:type_alias": 6,
    "typescript:function": 6,
    "typescript:method": 2,
    "typescript:import": 2,
    "typescript:export": 1
  },
  "edges_by_kind": {
    "imports": 559,
    "contains": 197,
    "exports": 8
  },
  "edges_by_confidence": {
    "unresolved": 397,
    "resolved": 245,
    "ambiguous": 122
  },
  "call_totals": {
    "total": 829,
    "resolved": 175,
    "ambiguous": 0,
    "unresolved": 654
  },
  "inheritance_counts": [],
  "symbol_totals": {
    "total": 890,
    "fake_deep": 0
  },
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
        "verified_deep": false
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 18,
        "end_line": 21,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 27,
        "end_line": 32,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 33,
        "end_line": 36,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 37,
        "end_line": 52,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
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
        "verified_deep": false
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 37,
        "end_line": 52,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 76,
        "end_line": 86,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 87,
        "end_line": 92,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 93,
        "end_line": 97,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
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
        "verified_deep": false
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 87,
        "end_line": 92,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 111,
        "end_line": 119,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 120,
        "end_line": 127,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGELOG.md",
        "start_line": 202,
        "end_line": 205,
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
    "node_count": 192,
    "edge_count": 415,
    "graph_type": "modules",
    "snapshot_id": "a5135786-5aef-4d55-80e1-e7cf35eb60ea",
    "filters": {
      "local_imports_only": false,
      "max_nodes": 500,
      "max_edges": 2000
    },
    "sample_nodes": [
      {
        "id": ".prettierrc",
        "label": ".prettierrc",
        "node_type": "module",
        "language": "javascript",
        "support_level": "deep",
        "path": ".prettierrc.js",
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
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
        "id": "chalk",
        "label": "chalk",
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
        "id": "child_process",
        "label": "child_process",
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
        "id": "commander",
        "label": "commander",
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
        "source": "eslint.config",
        "target": "@eslint/js",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "eslint.config",
        "target": "eslint-config-prettier",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "eslint.config",
        "target": "globals",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "eslint.config",
        "target": "typescript-eslint",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "examples.action-this",
        "target": "commander",
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
    "node_count": 117,
    "edge_count": 23,
    "graph_type": "packages",
    "snapshot_id": "a5135786-5aef-4d55-80e1-e7cf35eb60ea",
    "filters": {
      "local_imports_only": true,
      "max_nodes": 500,
      "max_edges": 2000
    },
    "sample_nodes": [
      {
        "id": ".prettierrc",
        "label": ".prettierrc",
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
        "symbol_count": 34,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "index",
        "label": "index",
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
        "id": "lib",
        "label": "lib",
        "node_type": "package",
        "language": "javascript",
        "support_level": "deep",
        "path": null,
        "symbol_count": 182,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      }
    ],
    "sample_edges": [
      {
        "source": "index",
        "target": "lib",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 6,
        "inferred": true,
        "line": null
      },
      {
        "source": "tests.argument.choices",
        "target": "tests",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": true,
        "line": null
      },
      {
        "source": "tests.argument.custom-processing",
        "target": "tests",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": true,
        "line": null
      },
      {
        "source": "tests.command.action",
        "target": "tests",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": true,
        "line": null
      },
      {
        "source": "tests.command.addHelpOption",
        "target": "tests",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": true,
        "line": null
      }
    ]
  },
  "directories": {
    "node_count": 10,
    "edge_count": 11,
    "graph_type": "directories",
    "snapshot_id": "a5135786-5aef-4d55-80e1-e7cf35eb60ea",
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
        "file_count": 15,
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
        "file_count": 3,
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
        "id": "docs",
        "label": "docs",
        "node_type": "directory",
        "language": null,
        "support_level": "generic",
        "path": null,
        "symbol_count": 0,
        "file_count": 6,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "examples",
        "label": "examples",
        "node_type": "directory",
        "language": null,
        "support_level": "deep",
        "path": null,
        "symbol_count": 0,
        "file_count": 37,
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
      },
      {
        "source": ".",
        "target": "lib",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 6,
        "inferred": true,
        "line": null
      }
    ]
  },
  "calls_depth_1": {
    "center": "lib.help.Help.formatHelp",
    "node_count": 3,
    "edge_count": 6,
    "depth": 1,
    "sample_edges": [
      {
        "source": "68bf2ee1-e16b-4f33-b688-cfd1f8467467",
        "target": "c0058c33-acd8-4fbe-90e0-936e43fa8699",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": 478
      },
      {
        "source": "68bf2ee1-e16b-4f33-b688-cfd1f8467467",
        "target": "c0058c33-acd8-4fbe-90e0-936e43fa8699",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": 494
      },
      {
        "source": "68bf2ee1-e16b-4f33-b688-cfd1f8467467",
        "target": "c0058c33-acd8-4fbe-90e0-936e43fa8699",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": 507
      },
      {
        "source": "68bf2ee1-e16b-4f33-b688-cfd1f8467467",
        "target": "c0058c33-acd8-4fbe-90e0-936e43fa8699",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": 524
      },
      {
        "source": "68bf2ee1-e16b-4f33-b688-cfd1f8467467",
        "target": "f244b88c-b476-4af8-bbbf-177b8f3acca2",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": 482
      },
      {
        "source": "68bf2ee1-e16b-4f33-b688-cfd1f8467467",
        "target": "f244b88c-b476-4af8-bbbf-177b8f3acca2",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": 512
      }
    ]
  },
  "calls_depth_2": {
    "center": "lib.help.Help.formatHelp",
    "node_count": 3,
    "edge_count": 6,
    "depth": 2,
    "sample_edges": [
      {
        "source": "68bf2ee1-e16b-4f33-b688-cfd1f8467467",
        "target": "c0058c33-acd8-4fbe-90e0-936e43fa8699",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": 478
      },
      {
        "source": "68bf2ee1-e16b-4f33-b688-cfd1f8467467",
        "target": "c0058c33-acd8-4fbe-90e0-936e43fa8699",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": 494
      },
      {
        "source": "68bf2ee1-e16b-4f33-b688-cfd1f8467467",
        "target": "c0058c33-acd8-4fbe-90e0-936e43fa8699",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": 507
      },
      {
        "source": "68bf2ee1-e16b-4f33-b688-cfd1f8467467",
        "target": "c0058c33-acd8-4fbe-90e0-936e43fa8699",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": 524
      },
      {
        "source": "68bf2ee1-e16b-4f33-b688-cfd1f8467467",
        "target": "f244b88c-b476-4af8-bbbf-177b8f3acca2",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": 482
      },
      {
        "source": "68bf2ee1-e16b-4f33-b688-cfd1f8467467",
        "target": "f244b88c-b476-4af8-bbbf-177b8f3acca2",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": 512
      }
    ]
  },
  "callers_api": {
    "total": 0,
    "sample": []
  },
  "callees_api": {
    "total": 20,
    "sample": [
      {
        "id": "52904f40-2c22-47a3-a732-c341ae80474f",
        "snapshot_id": "a5135786-5aef-4d55-80e1-e7cf35eb60ea",
        "source_file_id": "2a97a37f-4c1d-4e61-84fa-17d90586b51a",
        "path": "lib/help.js",
        "caller_symbol_id": "68bf2ee1-e16b-4f33-b688-cfd1f8467467",
        "caller_qualified_name": "lib.help.Help.formatHelp",
        "raw_callee": "helper.padWidth",
        "qualified_expression": "helper.padWidth",
        "line": 445,
        "candidate_qualified_name": null,
        "confidence": "unresolved",
        "language": "javascript",
        "created_at": "2026-07-20T02:23:57.200589Z"
      },
      {
        "id": "5aa887ce-9a15-4b7a-8f55-ceebefad287d",
        "snapshot_id": "a5135786-5aef-4d55-80e1-e7cf35eb60ea",
        "source_file_id": "2a97a37f-4c1d-4e61-84fa-17d90586b51a",
        "path": "lib/help.js",
        "caller_symbol_id": "68bf2ee1-e16b-4f33-b688-cfd1f8467467",
        "caller_qualified_name": "lib.help.Help.formatHelp",
        "raw_callee": "helper.styleTitle",
        "qualified_expression": "helper.styleTitle",
        "line": 454,
        "candidate_qualified_name": null,
        "confidence": "unresolved",
        "language": "javascript",
        "created_at": "2026-07-20T02:23:57.200589Z"
      },
      {
        "id": "a9ac4f4b-e9e7-4351-b297-e01992c26a7a",
        "snapshot_id": "a5135786-5aef-4d55-80e1-e7cf35eb60ea",
        "source_file_id": "2a97a37f-4c1d-4e61-84fa-17d90586b51a",
        "path": "lib/help.js",
        "caller_symbol_id": "68bf2ee1-e16b-4f33-b688-cfd1f8467467",
        "caller_qualified_name": "lib.help.Help.formatHelp",
        "raw_callee": "helper.commandUsage",
        "qualified_expression": "helper.commandUsage",
        "line": 454,
        "candidate_qualified_name": null,
        "confidence": "unresolved",
        "language": "javascript",
        "created_at": "2026-07-20T02:23:57.200589Z"
      },
      {
        "id": "3a98b0d2-f590-41eb-ad5a-fbde20d8774f",
        "snapshot_id": "a5135786-5aef-4d55-80e1-e7cf35eb60ea",
        "source_file_id": "2a97a37f-4c1d-4e61-84fa-17d90586b51a",
        "path": "lib/help.js",
        "caller_symbol_id": "68bf2ee1-e16b-4f33-b688-cfd1f8467467",
        "caller_qualified_name": "lib.help.Help.formatHelp",
        "raw_callee": "helper.styleUsage",
        "qualified_expression": "helper.styleUsage",
        "line": 454,
        "candidate_qualified_name": null,
        "confidence": "unresolved",
        "language": "javascript",
        "created_at": "2026-07-20T02:23:57.200589Z"
      },
      {
        "id": "77532b4e-ecdb-4034-b888-4ea9501cdece",
        "snapshot_id": "a5135786-5aef-4d55-80e1-e7cf35eb60ea",
        "source_file_id": "2a97a37f-4c1d-4e61-84fa-17d90586b51a",
        "path": "lib/help.js",
        "caller_symbol_id": "68bf2ee1-e16b-4f33-b688-cfd1f8467467",
        "caller_qualified_name": "lib.help.Help.formatHelp",
        "raw_callee": "helper.commandDescription",
        "qualified_expression": "helper.commandDescription",
        "line": 459,
        "candidate_qualified_name": null,
        "confidence": "unresolved",
        "language": "javascript",
        "created_at": "2026-07-20T02:23:57.200589Z"
      }
    ]
  }
}
```

## Callers / callees samples

```json
{
  "ambiguous_calls": [],
  "multi_caller": {
    "qn": "lib.command.Command.error",
    "callers": 8
  },
  "multi_callee": {
    "qn": "lib.help.Help.formatHelp",
    "callees": 48
  },
  "ambiguous_symbol": null,
  "unresolved_samples": [
    {
      "caller_qualified_name": "examples.arguments-custom-processing.myParseInt",
      "raw_callee": "parseInt",
      "confidence": "unresolved",
      "line": 12,
      "language": "javascript"
    },
    {
      "caller_qualified_name": "examples.arguments-custom-processing.myParseInt",
      "raw_callee": "isNaN",
      "confidence": "unresolved",
      "line": 13,
      "language": "javascript"
    },
    {
      "caller_qualified_name": "examples.color-help-replacement.MyHelp.prepareContext",
      "raw_callee": "super.prepareContext",
      "confidence": "unresolved",
      "line": 27,
      "language": "javascript"
    },
    {
      "caller_qualified_name": "examples.color-help-replacement.MyHelp.displayWidth",
      "raw_callee": "stripAnsi",
      "confidence": "unresolved",
      "line": 34,
      "language": "javascript"
    },
    {
      "caller_qualified_name": "examples.color-help-replacement.MyHelp.boxWrap",
      "raw_callee": "wrapAnsi",
      "confidence": "unresolved",
      "line": 38,
      "language": "javascript"
    }
  ],
  "no_callers": [
    {
      "id": "388afcd0-be1b-4fe8-895c-b239db78fe09",
      "qualified_name": "examples.arguments-custom-processing.mySum",
      "kind": "function",
      "language": "javascript"
    },
    {
      "id": "b9007cdc-6bf3-48fc-bf45-d8cff39de34b",
      "qualified_name": "examples.color-help-replacement.MyHelp.constructor",
      "kind": "method",
      "language": "javascript"
    },
    {
      "id": "aafede42-6f4c-473e-91b9-4a181495df89",
      "qualified_name": "examples.color-help-replacement.MyHelp.prepareContext",
      "kind": "method",
      "language": "javascript"
    }
  ],
  "multi_caller_symbol": {
    "id": "3d13f8a5-021e-4130-b55a-77ef37d8dfa3",
    "qualified_name": "lib.command.Command.error",
    "kind": "method",
    "language": "javascript",
    "start_line": 1952,
    "end_line": 1970
  },
  "multi_callee_symbol": {
    "id": "68bf2ee1-e16b-4f33-b688-cfd1f8467467",
    "qualified_name": "lib.help.Help.formatHelp",
    "kind": "method",
    "language": "javascript",
    "start_line": 444,
    "end_line": 528
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
  "modules_lang_javascript": {
    "node_count": 100,
    "edge_count": 186,
    "filters": {
      "language": "javascript",
      "local_imports_only": false,
      "max_nodes": 100,
      "max_edges": 200
    }
  },
  "inferred_false": {
    "node_count": 10,
    "edge_count": 9,
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
  "repository_id": "e0708b2c-eaea-4abe-b457-bb800c784966",
  "snapshot_id": "a5135786-5aef-4d55-80e1-e7cf35eb60ea",
  "commit_sha": "ba6d13ddb4243e5913367734f8c159089ffe7834",
  "status": "SUCCEEDED",
  "indexing_duration_seconds": 5.06,
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
    "with_parser": 646
  },
  "edges_by_kind": {
    "imports": 559,
    "contains": 197,
    "exports": 8
  },
  "call_totals": {
    "total": 829,
    "resolved": 175,
    "ambiguous": 0,
    "unresolved": 654
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
