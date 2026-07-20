# Week 8 validation — Java — perwendel/spark

- URL: https://github.com/perwendel/spark
- Generated: 2026-07-20T02:31:33.468854+00:00
- API: `http://127.0.0.1:8001`
- LLM enrichment: **OFF**
- Clone size limit: 52428800 bytes (unchanged)

## Checks

| Check | Result | Detail |
| --- | --- | --- |
| repository imported successfully | PASS | status=SUCCEEDED err=None:None |
| snapshot created | PASS | 999b1470-c3c7-4f9c-a054-10b619ab7c94 |
| files discovered | PASS | total=213 skipped=15 binaries=6 |
| chunks persisted | PASS | chunks=1582 unique_spans=1582 |
| no duplicate chunk spans | PASS | total=1582 unique=1582 |
| optional enrichment OFF | PASS | llm_enriched=0 |
| no fake verified symbols for non-deep langs | PASS | fake_deep=0 |
| deep analysis for expected languages | PASS | symbol_langs=['java'] verified_deep_chunks=1547 |
| deterministic repository summary | PASS | llm_summary_status=disabled |
| exact chunk search operational | PASS | Route→340; Spark→201; before→116; exception→552 |
| relation kinds only from unified model | PASS | kinds={'contains': 1340, 'imports': 1032, 'extends': 33, 'implements': 19} |
| no orphan from_symbol dangling IDs | PASS | orphans=0 |
| no orphan to_symbol dangling IDs | PASS | orphans=0 |
| no cross-snapshot relation leakage | PASS | cross=0 |
| no duplicate structural relation keys | PASS | total=2424 unique=2424 |
| IMPORTS/CONTAINS present for deep repo | PASS | edges={'contains': 1340, 'imports': 1032, 'extends': 33, 'implements': 19} |
| CALLS persisted with resolution labels | PASS | resolved=624 ambiguous=689 unresolved=2347 |
| EXTENDS/IMPLEMENTS present | PASS | extends=33 implements=19 |
| modules graph returns | PASS | nodes=275 edges=559 |
| modules graph no host path leakage | PASS | leaked=0 |
| packages graph returns | PASS | nodes=43 edges=0 |
| packages graph no host path leakage | PASS | leaked=0 |
| directory graph usable | PASS | nodes=61 edges=60 |
| directories graph no host path leakage | PASS | leaked=0 |
| callers/callees neighborhood API | PASS | center=spark.GenericIntegrationTest.setup d1_nodes=15 |
| call edges carry confidence labels | PASS | confidences_seen=['unresolved'] |
| ambiguous call symbols present | PASS | spark.CustomErrorPages.getFor |
| unresolved/external calls present or documented | PASS | unresolved_samples=5 |
| symbol with no callers found | PASS | count=3 |
| callers/callees list endpoints | PASS | callers=0 callees=20 |
| Java interfaces vs classes distinguished | PASS | interfaces=15 classes=189 |
| EXTENDS/IMPLEMENTS edges persisted | PASS | edge_samples=40 kinds=['extends', 'implements'] |
| unresolved external parents/interfaces labeled | PASS | unresolved_or_unlinked_in_sample=14 |
| interface-to-implementation lookup API | PASS | [{"i": "spark.ExceptionHandler", "n": 1}, {"i": "spark.Filter", "n": 1}, {"i": "spark.ResponseTransformer", "n": 1}] |
| invalid filter returns validation error | PASS | status=422 body={"detail":{"code":"invalid_support_level","message":"support_level must be deep, generic, mixed, or skip"}} |
| invalid confidence rejected | PASS | status=422 |
| graph node/edge limits applied | PASS | nodes=5 edges=4 |
| path_prefix filter accepted | PASS | nodes=56 |
| language filter on modules | PASS | requested=java seen=['java'] |
| inferred=false filter respected | PASS | inferred_remaining=0 total_edges=60 |
| React Flow page wired to live graph APIs | PASS | {"loads_from_api": true, "no_fixture_data_in_page": true, "has_relation_filters": true, "has_language_filter": true, "has_support_level_filter": true, "has_depth_control": true, "has_generic_honesty_notice": true, "has_inferred_edge_styling": true, "selection_detail_panel": true, "uses_xyflow": true} |
| generic honesty notice present in Graph UI | PASS | GraphPage honesty copy checked |
| no regex structural parsing in chunking package | PASS | offenders=[] |
| re-index succeeded | PASS | status=SUCCEEDED duration_s=10.0 |
| stable content hashes on re-index | PASS | common=198 mismatches=0 |
| no duplicate chunks after re-index | PASS | total=1582 unique=1582 |
| deterministic chunk multiset on re-index | PASS | prev=1582 new=1582 |
| deterministic relationship multiset on re-index | PASS | prev=2424 new=2424 |
| deterministic call multiset on re-index | PASS | prev=3660 new=3660 |
| no duplicate relations after re-index | PASS | total=2424 unique=2424 |
| no cross-snapshot leakage after re-index | PASS | cross=0 |
| stable graph API output ordering | PASS | nodes=50 |

## Metrics

```json
{
  "repository_id": "bf7bfeb4-2a0f-4086-8563-6277782e1d22",
  "snapshot_id": "999b1470-c3c7-4f9c-a054-10b619ab7c94",
  "commit_sha": "1973e402f5d4c1442ad34a1d38ed0758079f7773",
  "indexing_duration_seconds": 10.03,
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
      "binaries": 0
    },
    {
      "support_level": "skip",
      "language": null,
      "n": 15,
      "binaries": 6
    },
    {
      "support_level": "generic",
      "language": "configuration",
      "n": 5,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "documentation",
      "n": 4,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "html",
      "n": 2,
      "binaries": 0
    },
    {
      "support_level": "deep",
      "language": "javascript",
      "n": 2,
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
    "total": 1582,
    "verified_deep": 1547,
    "llm_enriched": 0,
    "unique_spans": 1582,
    "with_parser": 1582
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
  "nodes_by_type": {
    "java:method": 1260,
    "java:import": 1032,
    "java:field": 379,
    "java:class": 189,
    "java:package": 184,
    "java:constructor": 80,
    "java:enum_constant": 23,
    "java:interface": 15,
    "java:enum": 3
  },
  "edges_by_kind": {
    "contains": 1340,
    "imports": 1032,
    "extends": 33,
    "implements": 19
  },
  "edges_by_confidence": {
    "resolved": 1686,
    "unresolved": 738
  },
  "call_totals": {
    "total": 3660,
    "resolved": 624,
    "ambiguous": 689,
    "unresolved": 2347
  },
  "inheritance_counts": [
    {
      "relation_kind": "extends",
      "confidence": "resolved",
      "n": 20
    },
    {
      "relation_kind": "extends",
      "confidence": "unresolved",
      "n": 13
    },
    {
      "relation_kind": "implements",
      "confidence": "resolved",
      "n": 13
    },
    {
      "relation_kind": "implements",
      "confidence": "unresolved",
      "n": 6
    }
  ],
  "symbol_totals": {
    "total": 3165,
    "fake_deep": 0
  },
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
        "verified_deep": true
      },
      {
        "path": "src/main/java/spark/Access.java",
        "start_line": 30,
        "end_line": 32,
        "language": "java",
        "support_level": "deep",
        "verified_deep": true
      },
      {
        "path": "src/main/java/spark/CustomErrorPages.java",
        "start_line": 30,
        "end_line": 122,
        "language": "java",
        "support_level": "deep",
        "verified_deep": true
      },
      {
        "path": "src/main/java/spark/CustomErrorPages.java",
        "start_line": 54,
        "end_line": 71,
        "language": "java",
        "support_level": "deep",
        "verified_deep": true
      },
      {
        "path": "src/main/java/spark/CustomErrorPages.java",
        "start_line": 98,
        "end_line": 100,
        "language": "java",
        "support_level": "deep",
        "verified_deep": true
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
        "verified_deep": false
      },
      {
        "path": "pom.xml",
        "start_line": 9,
        "end_line": 9,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "pom.xml",
        "start_line": 10,
        "end_line": 10,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "pom.xml",
        "start_line": 13,
        "end_line": 13,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "pom.xml",
        "start_line": 15,
        "end_line": 15,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
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
        "verified_deep": false
      },
      {
        "path": "src/main/java/spark/embeddedserver/EmbeddedServer.java",
        "start_line": 28,
        "end_line": 85,
        "language": "java",
        "support_level": "deep",
        "verified_deep": true
      },
      {
        "path": "src/main/java/spark/embeddedserver/jetty/websocket/WebSocketServletContextHandlerFactory.java",
        "start_line": 33,
        "end_line": 71,
        "language": "java",
        "support_level": "deep",
        "verified_deep": true
      },
      {
        "path": "src/main/java/spark/embeddedserver/jetty/websocket/WebSocketServletContextHandlerFactory.java",
        "start_line": 44,
        "end_line": 69,
        "language": "java",
        "support_level": "deep",
        "verified_deep": true
      },
      {
        "path": "src/main/java/spark/http/matching/BeforeFilters.java",
        "start_line": 30,
        "end_line": 61,
        "language": "java",
        "support_level": "deep",
        "verified_deep": true
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
        "verified_deep": true
      },
      {
        "path": "src/main/java/spark/Base64.java",
        "start_line": 43,
        "end_line": 54,
        "language": "java",
        "support_level": "deep",
        "verified_deep": true
      },
      {
        "path": "src/main/java/spark/CustomErrorPages.java",
        "start_line": 30,
        "end_line": 122,
        "language": "java",
        "support_level": "deep",
        "verified_deep": true
      },
      {
        "path": "src/main/java/spark/CustomErrorPages.java",
        "start_line": 54,
        "end_line": 71,
        "language": "java",
        "support_level": "deep",
        "verified_deep": true
      },
      {
        "path": "src/main/java/spark/embeddedserver/EmbeddedServerFactory.java",
        "start_line": 26,
        "end_line": 42,
        "language": "java",
        "support_level": "deep",
        "verified_deep": true
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
    "node_count": 275,
    "edge_count": 559,
    "graph_type": "modules",
    "snapshot_id": "999b1470-c3c7-4f9c-a054-10b619ab7c94",
    "filters": {
      "local_imports_only": false,
      "max_nodes": 500,
      "max_edges": 2000
    },
    "sample_nodes": [
      {
        "id": "com.google.gson",
        "label": "com.google.gson",
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
        "id": "freemarker.template",
        "label": "freemarker.template",
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
        "id": "java",
        "label": "java",
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
        "id": "java.io",
        "label": "java.io",
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
        "id": "java.lang.ClassLoader",
        "label": "java.lang.ClassLoader",
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
        "source": "src.main.java.spark.Access",
        "target": "spark.routematch",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "src.main.java.spark.CustomErrorPages",
        "target": "java.util",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "src.main.java.spark.CustomErrorPages",
        "target": "org.slf4j",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "java",
        "weight": 2,
        "inferred": false,
        "line": null
      },
      {
        "source": "src.main.java.spark.ExceptionMapper",
        "target": "java.util",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "java",
        "weight": 2,
        "inferred": false,
        "line": null
      },
      {
        "source": "src.main.java.spark.Experimental",
        "target": "java.lang.annotation",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "java",
        "weight": 4,
        "inferred": false,
        "line": null
      }
    ]
  },
  "packages": {
    "node_count": 43,
    "edge_count": 0,
    "graph_type": "packages",
    "snapshot_id": "999b1470-c3c7-4f9c-a054-10b619ab7c94",
    "filters": {
      "local_imports_only": true,
      "max_nodes": 500,
      "max_edges": 2000
    },
    "sample_nodes": [
      {
        "id": "src.main.java.spark",
        "label": "src.main.java.spark",
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
        "id": "src.main.java.spark.embeddedserver",
        "label": "src.main.java.spark.embeddedserver",
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
        "id": "src.main.java.spark.embeddedserver.jetty",
        "label": "src.main.java.spark.embeddedserver.jetty",
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
        "id": "src.main.java.spark.embeddedserver.jetty.websocket",
        "label": "src.main.java.spark.embeddedserver.jetty.websocket",
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
        "id": "src.main.java.spark.globalstate",
        "label": "src.main.java.spark.globalstate",
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
    "node_count": 61,
    "edge_count": 60,
    "graph_type": "directories",
    "snapshot_id": "999b1470-c3c7-4f9c-a054-10b619ab7c94",
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
        "file_count": 4,
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
        "file_count": 0,
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
        "id": "changeset",
        "label": "changeset",
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
        "id": "config",
        "label": "config",
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
        "target": "changeset",
        "relation_kind": "contains",
        "confidence": "resolved",
        "language": null,
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": ".",
        "target": "config",
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
        "source": ".github",
        "target": ".github/workflows",
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
    "center": "spark.GenericIntegrationTest.setup",
    "node_count": 15,
    "edge_count": 48,
    "depth": 1,
    "sample_edges": [
      {
        "source": "0e0d3a60-54fe-48ae-ae2f-d7b82eda2f81",
        "target": "04c1a223-c6bb-42da-b832-fa3abd98ab37",
        "relation_kind": "calls",
        "confidence": "unresolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 152
      },
      {
        "source": "0e0d3a60-54fe-48ae-ae2f-d7b82eda2f81",
        "target": "05598c61-3eab-4292-9316-da3070454427",
        "relation_kind": "calls",
        "confidence": "unresolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 91
      },
      {
        "source": "0e0d3a60-54fe-48ae-ae2f-d7b82eda2f81",
        "target": "05598c61-3eab-4292-9316-da3070454427",
        "relation_kind": "calls",
        "confidence": "unresolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 92
      },
      {
        "source": "0e0d3a60-54fe-48ae-ae2f-d7b82eda2f81",
        "target": "05598c61-3eab-4292-9316-da3070454427",
        "relation_kind": "calls",
        "confidence": "unresolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 93
      },
      {
        "source": "0e0d3a60-54fe-48ae-ae2f-d7b82eda2f81",
        "target": "05598c61-3eab-4292-9316-da3070454427",
        "relation_kind": "calls",
        "confidence": "unresolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 94
      },
      {
        "source": "0e0d3a60-54fe-48ae-ae2f-d7b82eda2f81",
        "target": "05598c61-3eab-4292-9316-da3070454427",
        "relation_kind": "calls",
        "confidence": "unresolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 95
      },
      {
        "source": "0e0d3a60-54fe-48ae-ae2f-d7b82eda2f81",
        "target": "05598c61-3eab-4292-9316-da3070454427",
        "relation_kind": "calls",
        "confidence": "unresolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 96
      },
      {
        "source": "0e0d3a60-54fe-48ae-ae2f-d7b82eda2f81",
        "target": "05598c61-3eab-4292-9316-da3070454427",
        "relation_kind": "calls",
        "confidence": "unresolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 100
      }
    ]
  },
  "calls_depth_2": {
    "center": "spark.GenericIntegrationTest.setup",
    "node_count": 66,
    "edge_count": 183,
    "depth": 2,
    "sample_edges": [
      {
        "source": "00a61b11-97dc-44ec-a427-d417c90537d2",
        "target": "05598c61-3eab-4292-9316-da3070454427",
        "relation_kind": "calls",
        "confidence": "unresolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 11
      },
      {
        "source": "06ea38c2-8478-46f9-9c9c-76f48fbd0b47",
        "target": "06ea38c2-8478-46f9-9c9c-76f48fbd0b47",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 1198
      },
      {
        "source": "0e0d3a60-54fe-48ae-ae2f-d7b82eda2f81",
        "target": "04c1a223-c6bb-42da-b832-fa3abd98ab37",
        "relation_kind": "calls",
        "confidence": "unresolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 152
      },
      {
        "source": "0e0d3a60-54fe-48ae-ae2f-d7b82eda2f81",
        "target": "05598c61-3eab-4292-9316-da3070454427",
        "relation_kind": "calls",
        "confidence": "unresolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 91
      },
      {
        "source": "0e0d3a60-54fe-48ae-ae2f-d7b82eda2f81",
        "target": "05598c61-3eab-4292-9316-da3070454427",
        "relation_kind": "calls",
        "confidence": "unresolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 92
      },
      {
        "source": "0e0d3a60-54fe-48ae-ae2f-d7b82eda2f81",
        "target": "05598c61-3eab-4292-9316-da3070454427",
        "relation_kind": "calls",
        "confidence": "unresolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 93
      },
      {
        "source": "0e0d3a60-54fe-48ae-ae2f-d7b82eda2f81",
        "target": "05598c61-3eab-4292-9316-da3070454427",
        "relation_kind": "calls",
        "confidence": "unresolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 94
      },
      {
        "source": "0e0d3a60-54fe-48ae-ae2f-d7b82eda2f81",
        "target": "05598c61-3eab-4292-9316-da3070454427",
        "relation_kind": "calls",
        "confidence": "unresolved",
        "language": "java",
        "weight": 1,
        "inferred": false,
        "line": 95
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
        "id": "26312f24-b9f7-420b-95f7-fcd5c88c9617",
        "snapshot_id": "999b1470-c3c7-4f9c-a054-10b619ab7c94",
        "source_file_id": "0022a701-49ae-4033-b92f-3f617f9caaa1",
        "path": "src/test/java/spark/GenericIntegrationTest.java",
        "caller_symbol_id": "0e0d3a60-54fe-48ae-ae2f-d7b82eda2f81",
        "caller_qualified_name": "spark.GenericIntegrationTest.setup",
        "raw_callee": "System.getProperty",
        "qualified_expression": "System.getProperty",
        "line": 68,
        "candidate_qualified_name": null,
        "confidence": "unresolved",
        "language": "java",
        "created_at": "2026-07-20T02:23:47.774689Z"
      },
      {
        "id": "828da67f-01ea-4c87-b27e-1eaa76fcd263",
        "snapshot_id": "999b1470-c3c7-4f9c-a054-10b619ab7c94",
        "source_file_id": "0022a701-49ae-4033-b92f-3f617f9caaa1",
        "path": "src/test/java/spark/GenericIntegrationTest.java",
        "caller_symbol_id": "0e0d3a60-54fe-48ae-ae2f-d7b82eda2f81",
        "caller_qualified_name": "spark.GenericIntegrationTest.setup",
        "raw_callee": "writer.write",
        "qualified_expression": "writer.write",
        "line": 71,
        "candidate_qualified_name": null,
        "confidence": "unresolved",
        "language": "java",
        "created_at": "2026-07-20T02:23:47.774689Z"
      },
      {
        "id": "4a7993e0-691e-4c22-b6ea-b6175a3c2953",
        "snapshot_id": "999b1470-c3c7-4f9c-a054-10b619ab7c94",
        "source_file_id": "0022a701-49ae-4033-b92f-3f617f9caaa1",
        "path": "src/test/java/spark/GenericIntegrationTest.java",
        "caller_symbol_id": "0e0d3a60-54fe-48ae-ae2f-d7b82eda2f81",
        "caller_qualified_name": "spark.GenericIntegrationTest.setup",
        "raw_callee": "writer.flush",
        "qualified_expression": "writer.flush",
        "line": 72,
        "candidate_qualified_name": null,
        "confidence": "unresolved",
        "language": "java",
        "created_at": "2026-07-20T02:23:47.774689Z"
      },
      {
        "id": "8daacc81-a57b-4928-bf3f-d4a3f59b41e6",
        "snapshot_id": "999b1470-c3c7-4f9c-a054-10b619ab7c94",
        "source_file_id": "0022a701-49ae-4033-b92f-3f617f9caaa1",
        "path": "src/test/java/spark/GenericIntegrationTest.java",
        "caller_symbol_id": "0e0d3a60-54fe-48ae-ae2f-d7b82eda2f81",
        "caller_qualified_name": "spark.GenericIntegrationTest.setup",
        "raw_callee": "writer.close",
        "qualified_expression": "writer.close",
        "line": 73,
        "candidate_qualified_name": null,
        "confidence": "unresolved",
        "language": "java",
        "created_at": "2026-07-20T02:23:47.774689Z"
      },
      {
        "id": "51a9c654-7d32-4be7-9e0a-2061600405a4",
        "snapshot_id": "999b1470-c3c7-4f9c-a054-10b619ab7c94",
        "source_file_id": "0022a701-49ae-4033-b92f-3f617f9caaa1",
        "path": "src/test/java/spark/GenericIntegrationTest.java",
        "caller_symbol_id": "0e0d3a60-54fe-48ae-ae2f-d7b82eda2f81",
        "caller_qualified_name": "spark.GenericIntegrationTest.setup",
        "raw_callee": "staticFileLocation",
        "qualified_expression": "staticFileLocation",
        "line": 75,
        "candidate_qualified_name": "spark.Spark.staticFileLocation",
        "confidence": "resolved",
        "language": "java",
        "created_at": "2026-07-20T02:23:47.774689Z"
      }
    ]
  }
}
```

## Callers / callees samples

```json
{
  "multi_caller": {
    "qn": "spark.Spark.awaitInitialization",
    "callers": 19
  },
  "multi_callee": {
    "qn": "spark.GenericIntegrationTest.setup",
    "callees": 86
  },
  "ambiguous_symbol": {
    "id": "1396ee8d-49df-4793-9b36-b3925be50a70",
    "qualified_name": "spark.CustomErrorPages.getFor",
    "language": "java",
    "kind": "method"
  },
  "unresolved_samples": [
    {
      "caller_qualified_name": "spark.Access.changeMatch",
      "raw_callee": "request.changeMatch",
      "confidence": "unresolved",
      "line": 31,
      "language": "java"
    },
    {
      "caller_qualified_name": "spark.Base64.encode",
      "raw_callee": "toEncodeContent.getBytes",
      "confidence": "unresolved",
      "line": 34,
      "language": "java"
    },
    {
      "caller_qualified_name": "spark.Base64.encode",
      "raw_callee": "urlEncoder.encodeToString",
      "confidence": "unresolved",
      "line": 34,
      "language": "java"
    },
    {
      "caller_qualified_name": "spark.Base64.decode",
      "raw_callee": "decoder.decode",
      "confidence": "unresolved",
      "line": 49,
      "language": "java"
    },
    {
      "caller_qualified_name": "spark.Base64.decode",
      "raw_callee": "e.printStackTrace",
      "confidence": "unresolved",
      "line": 51,
      "language": "java"
    }
  ],
  "no_callers": [
    {
      "id": "353454f5-bf6f-4bf1-8b46-07f0b1206983",
      "qualified_name": "spark.CustomErrorPages.add",
      "kind": "method",
      "language": "java"
    },
    {
      "id": "468f43f4-0ef3-47c8-939e-e1edd73b5471",
      "qualified_name": "spark.CustomErrorPages.add",
      "kind": "method",
      "language": "java"
    },
    {
      "id": "fdae6165-06c9-4b20-abc3-a98b2ce7aef9",
      "qualified_name": "spark.CustomErrorPages.getInstance",
      "kind": "method",
      "language": "java"
    }
  ],
  "multi_caller_symbol": {
    "id": "76c6344e-d7aa-4f9b-b068-4276f524cddd",
    "qualified_name": "spark.Spark.awaitInitialization",
    "kind": "method",
    "language": "java",
    "start_line": 1205,
    "end_line": 1207
  },
  "multi_callee_symbol": {
    "id": "0e0d3a60-54fe-48ae-ae2f-d7b82eda2f81",
    "qualified_name": "spark.GenericIntegrationTest.setup",
    "kind": "method",
    "language": "java",
    "start_line": 64,
    "end_line": 213
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
      "from_qualified_name": "spark.embeddedserver.jetty.HttpRequestWrapper",
      "raw_target": "HttpServletRequestWrapper",
      "candidate_qualified_name": "javax.servlet.http.HttpServletRequestWrapper",
      "linked": true,
      "language": "java",
      "line": 33
    },
    {
      "relation_kind": "extends",
      "confidence": "unresolved",
      "from_qualified_name": "spark.embeddedserver.jetty.HttpRequestWrapper.CachedServletInputStream",
      "raw_target": "ServletInputStream",
      "candidate_qualified_name": "javax.servlet.ServletInputStream",
      "linked": true,
      "language": "java",
      "line": 76
    },
    {
      "relation_kind": "extends",
      "confidence": "unresolved",
      "from_qualified_name": "spark.embeddedserver.jetty.JettyHandler",
      "raw_target": "SessionHandler",
      "candidate_qualified_name": "org.eclipse.jetty.server.session.SessionHandler",
      "linked": true,
      "language": "java",
      "line": 34
    },
    {
      "relation_kind": "extends",
      "confidence": "unresolved",
      "from_qualified_name": "spark.embeddedserver.jetty.websocket.WebSocketCreatorFactoryTest.ListenerHandler",
      "raw_target": "WebSocketAdapter",
      "candidate_qualified_name": "org.eclipse.jetty.websocket.api.WebSocketAdapter",
      "linked": true,
      "language": "java",
      "line": 62
    },
    {
      "relation_kind": "extends",
      "confidence": "unresolved",
      "from_qualified_name": "spark.embeddedserver.NotSupportedException",
      "raw_target": "RuntimeException",
      "candidate_qualified_name": null,
      "linked": false,
      "language": "java",
      "line": 22
    },
    {
      "relation_kind": "extends",
      "confidence": "unresolved",
      "from_qualified_name": "spark.examples.exception.BaseException",
      "raw_target": "RuntimeException",
      "candidate_qualified_name": null,
      "linked": false,
      "language": "java",
      "line": 3
    },
    {
      "relation_kind": "extends",
      "confidence": "unresolved",
      "from_qualified_name": "spark.examples.exception.JWGmeligMeylingException",
      "raw_target": "RuntimeException",
      "candidate_qualified_name": null,
      "linked": false,
      "language": "java",
      "line": 3
    },
    {
      "relation_kind": "extends",
      "confidence": "unresolved",
      "from_qualified_name": "spark.examples.exception.NotFoundException",
      "raw_target": "RuntimeException",
      "candidate_qualified_name": null,
      "linked": false,
      "language": "java",
      "line": 3
    },
    {
      "relation_kind": "extends",
      "confidence": "resolved",
      "from_qualified_name": "spark.examples.exception.SubclassOfBaseException",
      "raw_target": "BaseException",
      "candidate_qualified_name": "spark.examples.exception.BaseException",
      "linked": true,
      "language": "java",
      "line": 3
    },
    {
      "relation_kind": "extends",
      "confidence": "resolved",
      "from_qualified_name": "spark.examples.sugar.http",
      "raw_target": "Spark",
      "candidate_qualified_name": "spark.Spark",
      "linked": true,
      "language": "java",
      "line": 24
    },
    {
      "relation_kind": "extends",
      "confidence": "resolved",
      "from_qualified_name": "spark.examples.templateview.FreeMarkerTemplateEngine",
      "raw_target": "TemplateEngine",
      "candidate_qualified_name": "spark.TemplateEngine",
      "linked": true,
      "language": "java",
      "line": 12
    },
    {
      "relation_kind": "extends",
      "confidence": "unresolved",
      "from_qualified_name": "spark.HaltException",
      "raw_target": "RuntimeException",
      "candidate_qualified_name": null,
      "linked": false,
      "language": "java",
      "line": 26
    },
    {
      "relation_kind": "extends",
      "confidence": "resolved",
      "from_qualified_name": "spark.http.matching.RequestWrapper",
      "raw_target": "Request",
      "candidate_qualified_name": "spark.Request",
      "linked": true,
      "language": "java",
      "line": 30
    },
    {
      "relation_kind": "extends",
      "confidence": "resolved",
      "from_qualified_name": "spark.http.matching.ResponseWrapper",
      "raw_target": "Response",
      "candidate_qualified_name": "spark.Response",
      "linked": true,
      "language": "java",
      "line": 23
    },
    {
      "relation_kind": "extends",
      "confidence": "resolved",
      "from_qualified_name": "spark.QueryParamsMap.NullQueryParamsMap",
      "raw_target": "QueryParamsMap",
      "candidate_qualified_name": "spark.QueryParamsMap",
      "linked": true,
      "language": "java",
      "line": 280
    },
    {
      "relation_kind": "extends",
      "confidence": "resolved",
      "from_qualified_name": "spark.resource.AbstractFileResolvingResource",
      "raw_target": "AbstractResource",
      "candidate_qualified_name": "spark.resource.AbstractResource",
      "linked": true,
      "language": "java",
      "line": 37
    },
    {
      "relation_kind": "extends",
      "confidence": "resolved",
      "from_qualified_name": "spark.resource.ClassPathResource",
      "raw_target": "AbstractFileResolvingResource",
      "candidate_qualified_name": "spark.resource.AbstractFileResolvingResource",
      "linked": true,
      "language": "java",
      "line": 42
    },
    {
      "relation_kind": "extends",
      "confidence": "resolved",
      "from_qualified_name": "spark.resource.ClassPathResourceHandler",
      "raw_target": "AbstractResourceHandler",
      "candidate_qualified_name": "spark.resource.AbstractResourceHandler",
      "linked": true,
      "language": "java",
      "line": 32
    },
    {
      "relation_kind": "extends",
      "confidence": "resolved",
      "from_qualified_name": "spark.resource.ExternalResource",
      "raw_target": "AbstractFileResolvingResource",
      "candidate_qualified_name": "spark.resource.AbstractFileResolvingResource",
      "linked": true,
      "language": "java",
      "line": 30
    },
    {
      "relation_kind": "extends",
      "confidence": "resolved",
      "from_qualified_name": "spark.resource.ExternalResourceHandler",
      "raw_target": "AbstractResourceHandler",
      "candidate_qualified_name": "spark.resource.AbstractResourceHandler",
      "linked": true,
      "language": "java",
      "line": 32
    }
  ],
  "interface_count": 15,
  "class_count": 189,
  "implementations_api": [
    {
      "interface": "spark.ExceptionHandler",
      "total": 1,
      "sample": [
        {
          "symbol_id": "a522f44d-bf14-4711-b34d-7ede490204dc",
          "qualified_name": "spark.ExceptionHandlerImpl",
          "name": "ExceptionHandlerImpl",
          "kind": "class",
          "path": "src/main/java/spark/ExceptionHandlerImpl.java",
          "line": 19,
          "confidence": "resolved",
          "relation_kind": "implements",
          "language": "java",
          "created_at": "2026-07-20T02:23:47.774689Z"
        }
      ]
    },
    {
      "interface": "spark.Filter",
      "total": 1,
      "sample": [
        {
          "symbol_id": "1ba917f0-efad-4a25-9d8a-06ae3f3af3a1",
          "qualified_name": "spark.FilterImpl",
          "name": "FilterImpl",
          "kind": "import",
          "path": "src/main/java/spark/FilterImpl.java",
          "line": 21,
          "confidence": "resolved",
          "relation_kind": "implements",
          "language": "java",
          "created_at": "2026-07-20T02:23:47.774689Z"
        }
      ]
    },
    {
      "interface": "spark.ResponseTransformer",
      "total": 1,
      "sample": [
        {
          "symbol_id": "651b365e-908d-478a-b2c0-796748192877",
          "qualified_name": "spark.examples.transformer.JsonTransformer",
          "name": "JsonTransformer",
          "kind": "class",
          "path": "src/test/java/spark/examples/transformer/JsonTransformer.java",
          "line": 7,
          "confidence": "resolved",
          "relation_kind": "implements",
          "language": "java",
          "created_at": "2026-07-20T02:23:47.774689Z"
        }
      ]
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
    "node_count": 56,
    "edge_count": 55
  },
  "modules_lang_java": {
    "node_count": 100,
    "edge_count": 27,
    "filters": {
      "language": "java",
      "local_imports_only": false,
      "max_nodes": 100,
      "max_edges": 200
    }
  },
  "inferred_false": {
    "node_count": 61,
    "edge_count": 60,
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
  "repository_id": "bf7bfeb4-2a0f-4086-8563-6277782e1d22",
  "snapshot_id": "999b1470-c3c7-4f9c-a054-10b619ab7c94",
  "commit_sha": "1973e402f5d4c1442ad34a1d38ed0758079f7773",
  "status": "SUCCEEDED",
  "indexing_duration_seconds": 10.03,
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
    "with_parser": 1582
  },
  "edges_by_kind": {
    "contains": 1340,
    "imports": 1032,
    "extends": 33,
    "implements": 19
  },
  "call_totals": {
    "total": 3660,
    "resolved": 624,
    "ambiguous": 689,
    "unresolved": 2347
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
