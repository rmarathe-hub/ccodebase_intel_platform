# Generalization validation — Java — javalin/javalin

- URL: https://github.com/javalin/javalin
- Generated: 2026-07-20T03:06:31.953101+00:00
- API: `http://127.0.0.1:8001`
- LLM enrichment: **OFF**
- Clone size limit: 52428800 bytes (unchanged)

## Checks

| Check | Result | Detail |
| --- | --- | --- |
| repository imported successfully | PASS | status=SUCCEEDED err=None:None |
| snapshot created | PASS | a2330be1-a173-4d3c-9071-a86c6069cbfd |
| files discovered | PASS | total=500 skipped=77 binaries=12 |
| chunks persisted | PASS | chunks=669 unique_spans=669 |
| no duplicate chunk spans | PASS | total=669 unique=669 |
| parser provenance stored | PASS | with_parser_name=669 with_version=669 |
| optional enrichment OFF | PASS | llm_enriched=0 |
| no fake verified symbols for non-deep langs | PASS | fake_deep=0 |
| deep analysis for expected languages | PASS | symbol_langs=['java', 'javascript'] verified_deep_chunks=369 |
| deterministic repository summary | PASS | llm_summary_status=disabled |
| exact chunk search operational | PASS | Javalin→341; Context→92; Route→173; handler→163 |
| relation kinds only from unified model | PASS | kinds={'contains': 288, 'imports': 353, 'extends': 7, 'implements': 7} |
| no orphan from_symbol dangling IDs | PASS | orphans=0 |
| no orphan to_symbol dangling IDs | PASS | orphans=0 |
| no cross-snapshot relation leakage | PASS | cross=0 |
| no duplicate structural relation keys | PASS | total=655 unique=655 |
| IMPORTS/CONTAINS present for deep repo | PASS | edges={'contains': 288, 'imports': 353, 'extends': 7, 'implements': 7} |
| CALLS persisted with resolution labels | PASS | resolved=107 ambiguous=170 unresolved=1025 |
| EXTENDS/IMPLEMENTS present | PASS | extends=7 implements=7 |
| modules graph returns | PASS | nodes=133 edges=256 |
| modules graph no host path leakage | PASS | leaked=0 |
| packages graph returns | PASS | nodes=22 edges=0 |
| packages graph no host path leakage | PASS | leaked=0 |
| directory graph usable | PASS | nodes=234 edges=233 |
| directories graph no host path leakage | PASS | leaked=0 |
| callers/callees neighborhood API | PASS | center=io.javalin.TestPublicApi_Java.main d1_nodes=9 |
| call edges carry confidence labels | PASS | confidences_seen=['resolved', 'unresolved'] |
| ambiguous call symbols present | PASS | io.javalin.TestApiBuilderRouteRoles.testEmptyNestedScopeDoesNotAddRoles |
| unresolved/external calls present or documented | PASS | unresolved_samples=5 |
| symbol with no callers found | PASS | count=3 |
| callers/callees list endpoints | PASS | callers=0 callees=20 |
| Java interfaces vs classes distinguished | PASS | interfaces=11 classes=66 |
| EXTENDS/IMPLEMENTS edges persisted | PASS | edge_samples=14 kinds=['extends', 'implements'] |
| unresolved external parents/interfaces labeled | PASS | unresolved_or_unlinked_in_sample=11 |
| interface-to-implementation lookup API | PASS | [{"i": "io.javalin.testing.ThrowingBiConsumer", "n": 0}, {"i": "io.javalin.testtools.TestCase", "n": 0}, {"i": "io.javalin.apibuilder.EndpointGroup", "n": 0}] |
| invalid filter returns validation error | PASS | status=422 body={"detail":{"code":"invalid_support_level","message":"support_level must be deep, generic, mixed, or skip"}} |
| invalid confidence rejected | PASS | status=422 |
| graph node/edge limits applied | PASS | nodes=5 edges=4 |
| path_prefix filter accepted | PASS | nodes=0 |
| language filter on modules | PASS | requested=java seen=['java'] |
| inferred=false filter respected | PASS | inferred_remaining=0 total_edges=199 |
| React Flow page wired to live graph APIs | PASS | {"loads_from_api": true, "no_fixture_data_in_page": true, "has_relation_filters": true, "has_language_filter": true, "has_support_level_filter": true, "has_depth_control": true, "has_generic_honesty_notice": true, "has_inferred_edge_styling": true, "selection_detail_panel": true, "uses_xyflow": true} |
| generic honesty notice present in Graph UI | PASS | GraphPage honesty copy checked |
| no regex structural parsing in chunking package | PASS | offenders=[] |
| re-index succeeded | PASS | status=SUCCEEDED duration_s=5.0 |
| stable content hashes on re-index | PASS | common=423 mismatches=0 |
| no duplicate chunks after re-index | PASS | total=669 unique=669 |
| deterministic chunk multiset on re-index | PASS | prev=669 new=669 |
| deterministic relationship multiset on re-index | PASS | prev=655 new=655 |
| deterministic call multiset on re-index | PASS | prev=1302 new=1302 |
| no duplicate relations after re-index | PASS | total=655 unique=655 |
| no cross-snapshot leakage after re-index | PASS | cross=0 |
| stable graph API output ordering | PASS | nodes=50 |

## Metrics

```json
{
  "repository_id": "14e539f1-2704-479a-8ac4-c8678546f6c9",
  "snapshot_id": "a2330be1-a173-4d3c-9071-a86c6069cbfd",
  "commit_sha": "6600d23a36eca699d57cca14110c3fb181222ed9",
  "indexing_duration_seconds": 5.05,
  "files": {
    "total": 500,
    "skipped": 77,
    "binaries": 12,
    "distinct_hashes": 415
  },
  "files_by_lang_level": [
    {
      "support_level": "generic",
      "language": "kotlin",
      "n": 303,
      "binaries": 0
    },
    {
      "support_level": "skip",
      "language": null,
      "n": 77,
      "binaries": 12
    },
    {
      "support_level": "deep",
      "language": "java",
      "n": 64,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "configuration",
      "n": 25,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "documentation",
      "n": 12,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "html",
      "n": 11,
      "binaries": 0
    },
    {
      "support_level": "deep",
      "language": "javascript",
      "n": 6,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "css",
      "n": 2,
      "binaries": 0
    }
  ],
  "chunks": {
    "total": 669,
    "verified_deep": 369,
    "llm_enriched": 0,
    "unique_spans": 669,
    "with_parser": 669,
    "with_parser_version": 669
  },
  "chunk_breakdown": [
    {
      "language": "java",
      "support_level": "deep",
      "extraction_method": "deep_symbol",
      "parser_name": "java-treesitter",
      "n": 368
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "defusedxml-sax",
      "n": 150
    },
    {
      "language": "documentation",
      "support_level": "generic",
      "extraction_method": "markdown_ast",
      "parser_name": "mistune-ast",
      "n": 124
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "yaml-compose",
      "n": 26
    },
    {
      "language": "javascript",
      "support_level": "deep",
      "extraction_method": "deep_symbol",
      "parser_name": "javascript-treesitter",
      "n": 1
    }
  ],
  "nodes_by_type": {
    "java:import": 353,
    "java:method": 278,
    "java:field": 72,
    "java:class": 66,
    "java:package": 61,
    "java:interface": 11,
    "java:constructor": 10,
    "java:enum_constant": 6,
    "java:enum": 2,
    "javascript:function": 1,
    "java:record": 1
  },
  "edges_by_kind": {
    "contains": 288,
    "imports": 353,
    "extends": 7,
    "implements": 7
  },
  "edges_by_confidence": {
    "resolved": 433,
    "unresolved": 222
  },
  "call_totals": {
    "total": 1302,
    "resolved": 107,
    "ambiguous": 170,
    "unresolved": 1025
  },
  "inheritance_counts": [
    {
      "relation_kind": "extends",
      "confidence": "unresolved",
      "n": 7
    },
    {
      "relation_kind": "implements",
      "confidence": "unresolved",
      "n": 4
    },
    {
      "relation_kind": "implements",
      "confidence": "resolved",
      "n": 3
    }
  ],
  "symbol_totals": {
    "total": 861,
    "fake_deep": 0
  },
  "language_mix": {
    "kotlin": 303,
    "java": 64,
    "configuration": 25,
    "documentation": 12,
    "html": 11,
    "javascript": 6,
    "css": 2
  }
}
```

## Exact search

```json
[
  {
    "query": "Javalin",
    "total": 341,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": ".github/copilot-instructions.md",
        "start_line": 1,
        "end_line": 6,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": ".github/copilot-instructions.md",
        "start_line": 17,
        "end_line": 22,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": ".github/copilot-instructions.md",
        "start_line": 23,
        "end_line": 31,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": ".github/copilot-instructions.md",
        "start_line": 36,
        "end_line": 49,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": ".github/copilot-instructions.md",
        "start_line": 50,
        "end_line": 55,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "Context",
    "total": 92,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": ".github/copilot-instructions.md",
        "start_line": 86,
        "end_line": 114,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": ".github/copilot-instructions.md",
        "start_line": 183,
        "end_line": 207,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": ".github/copilot-instructions.md",
        "start_line": 210,
        "end_line": 240,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": ".github/copilot-instructions.md",
        "start_line": 391,
        "end_line": 392,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": ".github/copilot-instructions.md",
        "start_line": 393,
        "end_line": 425,
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
    "total": 173,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": ".github/copilot-instructions.md",
        "start_line": 36,
        "end_line": 49,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": ".github/copilot-instructions.md",
        "start_line": 63,
        "end_line": 79,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": ".github/copilot-instructions.md",
        "start_line": 86,
        "end_line": 114,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": ".github/copilot-instructions.md",
        "start_line": 183,
        "end_line": 207,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": ".github/copilot-instructions.md",
        "start_line": 210,
        "end_line": 240,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "handler",
    "total": 163,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": ".github/copilot-instructions.md",
        "start_line": 86,
        "end_line": 114,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": ".github/copilot-instructions.md",
        "start_line": 208,
        "end_line": 209,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": ".github/copilot-instructions.md",
        "start_line": 210,
        "end_line": 240,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": ".github/copilot-instructions.md",
        "start_line": 241,
        "end_line": 257,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": ".github/copilot-instructions.md",
        "start_line": 313,
        "end_line": 346,
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
    "node_count": 133,
    "edge_count": 256,
    "graph_type": "modules",
    "snapshot_id": "a2330be1-a173-4d3c-9071-a86c6069cbfd",
    "filters": {
      "local_imports_only": false,
      "max_nodes": 500,
      "max_edges": 2000
    },
    "sample_nodes": [
      {
        "id": "io.javalin",
        "label": "io.javalin",
        "node_type": "module",
        "language": "java",
        "support_level": "generic",
        "path": null,
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "io.javalin.TestBeforeMatched.MyRole",
        "label": "io.javalin.TestBeforeMatched.MyRole",
        "node_type": "module",
        "language": "java",
        "support_level": "generic",
        "path": null,
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "io.javalin.apibuilder",
        "label": "io.javalin.apibuilder",
        "node_type": "module",
        "language": "java",
        "support_level": "generic",
        "path": null,
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "io.javalin.apibuilder.ApiBuilder",
        "label": "io.javalin.apibuilder.ApiBuilder",
        "node_type": "module",
        "language": "java",
        "support_level": "generic",
        "path": null,
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "io.javalin.compression",
        "label": "io.javalin.compression",
        "node_type": "module",
        "language": "java",
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
        "source": "javalin-ssl.src.test.java.io.javalin.community.ssl.JavaAPITests",
        "target": "io.javalin",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "javalin-ssl.src.test.java.io.javalin.community.ssl.JavaAPITests",
        "target": "java.io",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "javalin-testtools.src.main.java.io.javalin.testtools.TestCase",
        "target": "io.javalin",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "javalin-testtools.src.test.java.io.javalin.testtools.JavaApp",
        "target": "io.javalin",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "javalin-testtools.src.test.java.io.javalin.testtools.JavaApp",
        "target": "io.javalin.apibuilder.ApiBuilder",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": null
      }
    ]
  },
  "packages": {
    "node_count": 22,
    "edge_count": 0,
    "graph_type": "packages",
    "snapshot_id": "a2330be1-a173-4d3c-9071-a86c6069cbfd",
    "filters": {
      "local_imports_only": true,
      "max_nodes": 500,
      "max_edges": 2000
    },
    "sample_nodes": [
      {
        "id": "javalin",
        "label": "javalin",
        "node_type": "package",
        "language": "java",
        "support_level": "deep",
        "path": null,
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "javalin-micrometer.src.main",
        "label": "javalin-micrometer.src.main",
        "node_type": "package",
        "language": "java",
        "support_level": "deep",
        "path": null,
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "javalin-ssl.src.main",
        "label": "javalin-ssl.src.main",
        "node_type": "package",
        "language": "java",
        "support_level": "deep",
        "path": null,
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "javalin-ssl.src.test.java.io.javalin.community.ssl",
        "label": "javalin-ssl.src.test.java.io.javalin.community.ssl",
        "node_type": "package",
        "language": "java",
        "support_level": "deep",
        "path": null,
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "javalin-testtools.src.main.java.io.javalin.testtools",
        "label": "javalin-testtools.src.main.java.io.javalin.testtools",
        "node_type": "package",
        "language": "java",
        "support_level": "deep",
        "path": null,
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      }
    ],
    "sample_edges": []
  },
  "directories": {
    "node_count": 234,
    "edge_count": 233,
    "graph_type": "directories",
    "snapshot_id": "a2330be1-a173-4d3c-9071-a86c6069cbfd",
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
        "file_count": 4,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "jacoco-coverage-report",
        "label": "jacoco-coverage-report",
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
        "id": "javalin",
        "label": "javalin",
        "node_type": "directory",
        "language": null,
        "support_level": "mixed",
        "path": null,
        "symbol_count": 0,
        "file_count": 2,
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
        "target": "jacoco-coverage-report",
        "relation_kind": "contains",
        "confidence": "resolved",
        "language": null,
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": ".",
        "target": "javalin",
        "relation_kind": "contains",
        "confidence": "resolved",
        "language": null,
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": ".",
        "target": "javalin-bom",
        "relation_kind": "contains",
        "confidence": "resolved",
        "language": null,
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": ".",
        "target": "javalin-bundle",
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
    "center": "io.javalin.TestPublicApi_Java.main",
    "node_count": 9,
    "edge_count": 18,
    "depth": 1,
    "sample_edges": [
      {
        "source": "cdbfc687-0d2c-496a-b524-81c517604093",
        "target": "03acf3f5-4369-4bf9-861c-5898d37fcd8a",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 94
      },
      {
        "source": "cdbfc687-0d2c-496a-b524-81c517604093",
        "target": "03acf3f5-4369-4bf9-861c-5898d37fcd8a",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 95
      },
      {
        "source": "cdbfc687-0d2c-496a-b524-81c517604093",
        "target": "16e8abca-a943-4039-9c3e-87361f04fbae",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 126
      },
      {
        "source": "cdbfc687-0d2c-496a-b524-81c517604093",
        "target": "1b3b758b-ee6b-496c-a404-d38db2bf166f",
        "relation_kind": "calls",
        "confidence": "unresolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 66
      },
      {
        "source": "cdbfc687-0d2c-496a-b524-81c517604093",
        "target": "1b3b758b-ee6b-496c-a404-d38db2bf166f",
        "relation_kind": "calls",
        "confidence": "unresolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 67
      },
      {
        "source": "cdbfc687-0d2c-496a-b524-81c517604093",
        "target": "63ef9308-1d15-4c47-ab54-7f2db010bdb1",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 96
      },
      {
        "source": "cdbfc687-0d2c-496a-b524-81c517604093",
        "target": "63ef9308-1d15-4c47-ab54-7f2db010bdb1",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 97
      },
      {
        "source": "cdbfc687-0d2c-496a-b524-81c517604093",
        "target": "798bb9cc-14ac-42f9-b460-002e0e62f5eb",
        "relation_kind": "calls",
        "confidence": "unresolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 64
      }
    ]
  },
  "calls_depth_2": {
    "center": "io.javalin.TestPublicApi_Java.main",
    "node_count": 34,
    "edge_count": 65,
    "depth": 2,
    "sample_edges": [
      {
        "source": "1a8cb011-f048-4432-b345-241eefdf7ce9",
        "target": "03acf3f5-4369-4bf9-861c-5898d37fcd8a",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 109
      },
      {
        "source": "1a8cb011-f048-4432-b345-241eefdf7ce9",
        "target": "16e8abca-a943-4039-9c3e-87361f04fbae",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 113
      },
      {
        "source": "1a8cb011-f048-4432-b345-241eefdf7ce9",
        "target": "1b3b758b-ee6b-496c-a404-d38db2bf166f",
        "relation_kind": "calls",
        "confidence": "unresolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 111
      },
      {
        "source": "1a8cb011-f048-4432-b345-241eefdf7ce9",
        "target": "798bb9cc-14ac-42f9-b460-002e0e62f5eb",
        "relation_kind": "calls",
        "confidence": "unresolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 106
      },
      {
        "source": "1a8cb011-f048-4432-b345-241eefdf7ce9",
        "target": "8552dbe2-668e-40ad-896c-9dc53211a5d5",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 112
      },
      {
        "source": "1a8cb011-f048-4432-b345-241eefdf7ce9",
        "target": "ae5572bd-0381-4147-8533-e414c9e04b9e",
        "relation_kind": "calls",
        "confidence": "unresolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 107
      },
      {
        "source": "247e41f3-1ce8-40da-bb26-f39ded10946d",
        "target": "ae5572bd-0381-4147-8533-e414c9e04b9e",
        "relation_kind": "calls",
        "confidence": "unresolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 21
      },
      {
        "source": "4b58d0a4-c96c-4b73-96aa-1f20f368c365",
        "target": "ae5572bd-0381-4147-8533-e414c9e04b9e",
        "relation_kind": "calls",
        "confidence": "unresolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 38
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
        "id": "e58adab3-c841-4eb9-b5e4-b5d8a70d154b",
        "snapshot_id": "a2330be1-a173-4d3c-9071-a86c6069cbfd",
        "source_file_id": "3acb3a06-2e7a-46dd-935b-c87cc8a6d8af",
        "path": "javalin/src/test/java/io/javalin/TestPublicApi_Java.java",
        "caller_symbol_id": "cdbfc687-0d2c-496a-b524-81c517604093",
        "caller_qualified_name": "io.javalin.TestPublicApi_Java.main",
        "raw_callee": "start",
        "qualified_expression": "start",
        "line": 36,
        "candidate_qualified_name": null,
        "confidence": "ambiguous",
        "language": "java",
        "created_at": "2026-07-20T03:05:21.343831Z"
      },
      {
        "id": "984fe6a0-c8f8-4477-aa4c-def84e7381a6",
        "snapshot_id": "a2330be1-a173-4d3c-9071-a86c6069cbfd",
        "source_file_id": "3acb3a06-2e7a-46dd-935b-c87cc8a6d8af",
        "path": "javalin/src/test/java/io/javalin/TestPublicApi_Java.java",
        "caller_symbol_id": "cdbfc687-0d2c-496a-b524-81c517604093",
        "caller_qualified_name": "io.javalin.TestPublicApi_Java.main",
        "raw_callee": "Javalin.create",
        "qualified_expression": "Javalin.create",
        "line": 40,
        "candidate_qualified_name": null,
        "confidence": "ambiguous",
        "language": "java",
        "created_at": "2026-07-20T03:05:21.343831Z"
      },
      {
        "id": "3d5bf068-9f45-4e35-b4df-bc08b8fb53cf",
        "snapshot_id": "a2330be1-a173-4d3c-9071-a86c6069cbfd",
        "source_file_id": "3acb3a06-2e7a-46dd-935b-c87cc8a6d8af",
        "path": "javalin/src/test/java/io/javalin/TestPublicApi_Java.java",
        "caller_symbol_id": "cdbfc687-0d2c-496a-b524-81c517604093",
        "caller_qualified_name": "io.javalin.TestPublicApi_Java.main",
        "raw_callee": "config.appData",
        "qualified_expression": "config.appData",
        "line": 41,
        "candidate_qualified_name": null,
        "confidence": "unresolved",
        "language": "java",
        "created_at": "2026-07-20T03:05:21.343831Z"
      },
      {
        "id": "82c79947-f62b-4184-811c-e6602a3aa455",
        "snapshot_id": "a2330be1-a173-4d3c-9071-a86c6069cbfd",
        "source_file_id": "3acb3a06-2e7a-46dd-935b-c87cc8a6d8af",
        "path": "javalin/src/test/java/io/javalin/TestPublicApi_Java.java",
        "caller_symbol_id": "cdbfc687-0d2c-496a-b524-81c517604093",
        "caller_qualified_name": "io.javalin.TestPublicApi_Java.main",
        "raw_callee": "Instant.ofEpochMilli",
        "qualified_expression": "Instant.ofEpochMilli",
        "line": 42,
        "candidate_qualified_name": "java.time.Instant.ofEpochMilli",
        "confidence": "unresolved",
        "language": "java",
        "created_at": "2026-07-20T03:05:21.343831Z"
      },
      {
        "id": "c21dfe32-a9ae-4e91-901d-8d1341059d02",
        "snapshot_id": "a2330be1-a173-4d3c-9071-a86c6069cbfd",
        "source_file_id": "3acb3a06-2e7a-46dd-935b-c87cc8a6d8af",
        "path": "javalin/src/test/java/io/javalin/TestPublicApi_Java.java",
        "caller_symbol_id": "cdbfc687-0d2c-496a-b524-81c517604093",
        "caller_qualified_name": "io.javalin.TestPublicApi_Java.main",
        "raw_callee": "config.validation.register",
        "qualified_expression": "config.validation.register",
        "line": 42,
        "candidate_qualified_name": null,
        "confidence": "unresolved",
        "language": "java",
        "created_at": "2026-07-20T03:05:21.343831Z"
      }
    ]
  }
}
```

## Callers / callees samples

```json
{
  "multi_caller": {
    "qn": "io.javalin.apibuilder.ApiBuilder.prefixPath",
    "callers": 49
  },
  "multi_callee": {
    "qn": "io.javalin.TestPublicApi_Java.main",
    "callees": 153
  },
  "ambiguous_symbol": {
    "id": "383cda4d-860a-4180-a174-6735fd4ef0f3",
    "qualified_name": "io.javalin.TestApiBuilderRouteRoles.testEmptyNestedScopeDoesNotAddRoles",
    "language": "java",
    "kind": "method"
  },
  "unresolved_samples": [
    {
      "caller_qualified_name": "io.javalin.Javalin.stop",
      "raw_callee": "isStopped",
      "confidence": "unresolved",
      "line": 139,
      "language": "java"
    },
    {
      "caller_qualified_name": "io.javalin.Javalin.stop",
      "raw_callee": "isStopping",
      "confidence": "unresolved",
      "line": 139,
      "language": "java"
    },
    {
      "caller_qualified_name": "io.javalin.apibuilder.ApiBuilder.setStaticJavalin",
      "raw_callee": "staticJavalin.set",
      "confidence": "unresolved",
      "line": 38,
      "language": "java"
    },
    {
      "caller_qualified_name": "io.javalin.apibuilder.ApiBuilder.clearStaticJavalin",
      "raw_callee": "staticJavalin.remove",
      "confidence": "unresolved",
      "line": 47,
      "language": "java"
    },
    {
      "caller_qualified_name": "io.javalin.apibuilder.ApiBuilder.path",
      "raw_callee": "Collections.emptyList",
      "confidence": "unresolved",
      "line": 56,
      "language": "java"
    }
  ],
  "no_callers": [
    {
      "id": "383cda4d-860a-4180-a174-6735fd4ef0f3",
      "qualified_name": "io.javalin.TestApiBuilderRouteRoles.testEmptyNestedScopeDoesNotAddRoles",
      "kind": "method",
      "language": "java"
    },
    {
      "id": "978df42a-3a9b-490d-b639-ac4e3eca05be",
      "qualified_name": "io.javalin.TestApiBuilderRouteRoles.testDeepNestingAccumulatesRoles",
      "kind": "method",
      "language": "java"
    },
    {
      "id": "2c59ba25-6e88-43ba-a2e3-42ac0d77abd0",
      "qualified_name": "io.javalin.TestApiBuilderRouteRoles.testPathWithoutRolesIsUnaffected",
      "kind": "method",
      "language": "java"
    }
  ],
  "multi_caller_symbol": {
    "id": "41ce7047-e14c-4035-9e24-0b825109f99f",
    "qualified_name": "io.javalin.apibuilder.ApiBuilder.prefixPath",
    "kind": "method",
    "language": "java",
    "start_line": 77,
    "end_line": 79
  },
  "multi_callee_symbol": {
    "id": "cdbfc687-0d2c-496a-b524-81c517604093",
    "qualified_name": "io.javalin.TestPublicApi_Java.main",
    "kind": "method",
    "language": "java",
    "start_line": 35,
    "end_line": 223
  }
}
```

## Inheritance / implementations

```json
{
  "extends_implements_samples": [
    {
      "relation_kind": "extends",
      "confidence": "unresolved",
      "from_qualified_name": "io.javalin.examples.CopilotInstructionsPatternValidation.TestPlugin",
      "raw_target": "Plugin",
      "candidate_qualified_name": "io.javalin.plugin.Plugin",
      "linked": true,
      "language": "java",
      "line": 181
    },
    {
      "relation_kind": "extends",
      "confidence": "unresolved",
      "from_qualified_name": "io.javalin.examples.JRate",
      "raw_target": "ContextPlugin",
      "candidate_qualified_name": "io.javalin.plugin.ContextPlugin",
      "linked": true,
      "language": "java",
      "line": 31
    },
    {
      "relation_kind": "extends",
      "confidence": "unresolved",
      "from_qualified_name": "io.javalin.testing.TestServlet",
      "raw_target": "HttpServlet",
      "candidate_qualified_name": "jakarta.servlet.http.HttpServlet",
      "linked": true,
      "language": "java",
      "line": 16
    },
    {
      "relation_kind": "extends",
      "confidence": "unresolved",
      "from_qualified_name": "io.javalin.testing.ThrowingBiConsumer",
      "raw_target": "BiConsumer",
      "candidate_qualified_name": "java.util.function.BiConsumer",
      "linked": true,
      "language": "java",
      "line": 12
    },
    {
      "relation_kind": "extends",
      "confidence": "unresolved",
      "from_qualified_name": "io.javalin.testing.TypedException",
      "raw_target": "Exception",
      "candidate_qualified_name": null,
      "linked": false,
      "language": "java",
      "line": 10
    },
    {
      "relation_kind": "extends",
      "confidence": "unresolved",
      "from_qualified_name": "io.javalin.TestPublicApi_Java.TestContextPlugin",
      "raw_target": "ContextPlugin",
      "candidate_qualified_name": "io.javalin.plugin.ContextPlugin",
      "linked": true,
      "language": "java",
      "line": 29
    },
    {
      "relation_kind": "extends",
      "confidence": "unresolved",
      "from_qualified_name": "io.javalin.TestValidation_Java.CustomException",
      "raw_target": "RuntimeException",
      "candidate_qualified_name": null,
      "linked": false,
      "language": "java",
      "line": 21
    },
    {
      "relation_kind": "implements",
      "confidence": "unresolved",
      "from_qualified_name": "io.javalin.examples.HelloWorldAuth.JRole",
      "raw_target": "RouteRole",
      "candidate_qualified_name": "io.javalin.security.RouteRole",
      "linked": true,
      "language": "java",
      "line": 25
    },
    {
      "relation_kind": "implements",
      "confidence": "resolved",
      "from_qualified_name": "io.javalin.routeoverview.TestRouteOverviewInJava.InnerHandlerImplementation",
      "raw_target": "Handler",
      "candidate_qualified_name": "io.javalin.http.Handler",
      "linked": true,
      "language": "java",
      "line": 38
    },
    {
      "relation_kind": "implements",
      "confidence": "unresolved",
      "from_qualified_name": "io.javalin.routeoverview.VisualTest.CrudHandlerImpl",
      "raw_target": "CrudHandler",
      "candidate_qualified_name": "io.javalin.apibuilder.CrudHandler",
      "linked": true,
      "language": "java",
      "line": 109
    },
    {
      "relation_kind": "implements",
      "confidence": "resolved",
      "from_qualified_name": "io.javalin.routeoverview.VisualTest.HandlerImplementation",
      "raw_target": "Handler",
      "candidate_qualified_name": "io.javalin.http.Handler",
      "linked": true,
      "language": "java",
      "line": 103
    },
    {
      "relation_kind": "implements",
      "confidence": "resolved",
      "from_qualified_name": "io.javalin.routeoverview.VisualTest.ImplementingClass",
      "raw_target": "Handler",
      "candidate_qualified_name": "io.javalin.http.Handler",
      "linked": true,
      "language": "java",
      "line": 97
    },
    {
      "relation_kind": "implements",
      "confidence": "unresolved",
      "from_qualified_name": "io.javalin.TestApiBuilderRouteRoles.Role",
      "raw_target": "RouteRole",
      "candidate_qualified_name": "io.javalin.security.RouteRole",
      "linked": true,
      "language": "java",
      "line": 24
    },
    {
      "relation_kind": "implements",
      "confidence": "unresolved",
      "from_qualified_name": "io.javalin.testing.SerializableObject",
      "raw_target": "Serializable",
      "candidate_qualified_name": "java.io.Serializable",
      "linked": true,
      "language": "java",
      "line": 5
    }
  ],
  "interface_count": 11,
  "class_count": 66,
  "implementations_api": [
    {
      "interface": "io.javalin.testing.ThrowingBiConsumer",
      "total": 0,
      "sample": []
    },
    {
      "interface": "io.javalin.testtools.TestCase",
      "total": 0,
      "sample": []
    },
    {
      "interface": "io.javalin.apibuilder.EndpointGroup",
      "total": 0,
      "sample": []
    }
  ]
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
  "modules_lang_java": {
    "node_count": 100,
    "edge_count": 194,
    "filters": {
      "language": "java",
      "local_imports_only": false,
      "max_nodes": 100,
      "max_edges": 200
    }
  },
  "inferred_false": {
    "node_count": 200,
    "edge_count": 199,
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
  "repository_id": "14e539f1-2704-479a-8ac4-c8678546f6c9",
  "snapshot_id": "a2330be1-a173-4d3c-9071-a86c6069cbfd",
  "commit_sha": "6600d23a36eca699d57cca14110c3fb181222ed9",
  "status": "SUCCEEDED",
  "indexing_duration_seconds": 5.03,
  "files": {
    "total": 500,
    "skipped": 77,
    "binaries": 12,
    "distinct_hashes": 415
  },
  "chunks": {
    "total": 669,
    "verified_deep": 369,
    "llm_enriched": 0,
    "distinct_content_hashes": 621,
    "unique_spans": 669,
    "with_parser": 669,
    "with_parser_version": 669
  },
  "edges_by_kind": {
    "contains": 288,
    "imports": 353,
    "extends": 7,
    "implements": 7
  },
  "call_totals": {
    "total": 1302,
    "resolved": 107,
    "ambiguous": 170,
    "unresolved": 1025
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

- Checks passed: 53/53
- Checks failed: 0
