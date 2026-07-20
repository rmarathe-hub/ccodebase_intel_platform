# Week 8 validation — Config/Docs — docker/awesome-compose

- URL: https://github.com/docker/awesome-compose
- Generated: 2026-07-20T02:54:38.283160+00:00
- API: `http://127.0.0.1:8001`
- LLM enrichment: **OFF**
- Clone size limit: 52428800 bytes (unchanged)

## Checks

| Check | Result | Detail |
| --- | --- | --- |
| repository imported successfully | PASS | status=SUCCEEDED err=None:None |
| snapshot created | PASS | 9202ad67-c514-470b-8d8e-5d844d787f26 |
| files discovered | PASS | total=479 skipped=124 binaries=50 |
| chunks persisted | PASS | chunks=956 unique_spans=956 |
| no duplicate chunk spans | PASS | total=956 unique=956 |
| optional enrichment OFF | PASS | llm_enriched=0 |
| no fake verified symbols for non-deep langs | PASS | fake_deep=0 |
| generic-primary: verified_deep not claimed repository-wide | PASS | verified_deep_chunks=116 (incidental deep files allowed=True) |
| deterministic repository summary | PASS | llm_summary_status=disabled |
| exact chunk search operational | PASS | docker-compose→31; postgres→60; redis→24; nginx→61 |
| relation kinds only from unified model | PASS | kinds={'imports': 167, 'contains': 41, 'extends': 2, 'implements': 1} |
| no orphan from_symbol dangling IDs | PASS | orphans=0 |
| no orphan to_symbol dangling IDs | PASS | orphans=0 |
| no cross-snapshot relation leakage | PASS | cross=0 |
| no duplicate structural relation keys | PASS | total=211 unique=211 |
| modules graph endpoint ok | PASS | nodes=148 edges=138 |
| modules graph no host path leakage | PASS | leaked=0 |
| packages graph endpoint ok | PASS | nodes=59 edges=15 |
| packages graph no host path leakage | PASS | leaked=0 |
| directory graph usable | PASS | nodes=167 edges=169 |
| directories graph no host path leakage | PASS | leaked=0 |
| generic Go/unsupported: no invented verified call graph | PASS | go_symbols=0 go_calls=0 |
| invalid filter returns validation error | PASS | status=422 body={"detail":{"code":"invalid_support_level","message":"support_level must be deep, generic, mixed, or skip"}} |
| invalid confidence rejected | PASS | status=422 |
| graph node/edge limits applied | PASS | nodes=5 edges=4 |
| path_prefix filter accepted | PASS | nodes=0 |
| inferred=false filter respected | PASS | inferred_remaining=0 total_edges=166 |
| React Flow page wired to live graph APIs | PASS | {"loads_from_api": true, "no_fixture_data_in_page": true, "has_relation_filters": true, "has_language_filter": true, "has_support_level_filter": true, "has_depth_control": true, "has_generic_honesty_notice": true, "has_inferred_edge_styling": true, "selection_detail_panel": true, "uses_xyflow": true} |
| generic honesty notice present in Graph UI | PASS | GraphPage honesty copy checked |
| no regex structural parsing in chunking package | PASS | offenders=[] |
| re-index succeeded | PASS | status=SUCCEEDED duration_s=5.1 |
| stable content hashes on re-index | PASS | common=355 mismatches=0 |
| no duplicate chunks after re-index | PASS | total=956 unique=956 |
| deterministic chunk multiset on re-index | PASS | prev=956 new=956 |
| deterministic relationship multiset on re-index | PASS | prev=211 new=211 |
| deterministic call multiset on re-index | PASS | prev=255 new=255 |
| no duplicate relations after re-index | PASS | total=211 unique=211 |
| no cross-snapshot leakage after re-index | PASS | cross=0 |
| stable graph API output ordering | PASS | nodes=50 |

## Metrics

```json
{
  "repository_id": "fbbf6457-8d89-4191-8f5a-a86da1cff1a9",
  "snapshot_id": "9202ad67-c514-470b-8d8e-5d844d787f26",
  "commit_sha": "30f4b7f6a6c3b0c0ecf4d4efb0de203c48d11562",
  "indexing_duration_seconds": 5.03,
  "files": {
    "total": 479,
    "skipped": 124,
    "binaries": 50,
    "distinct_hashes": 311
  },
  "files_by_lang_level": [
    {
      "support_level": "generic",
      "language": "configuration",
      "n": 142,
      "binaries": 0
    },
    {
      "support_level": "skip",
      "language": null,
      "n": 124,
      "binaries": 50
    },
    {
      "support_level": "generic",
      "language": "documentation",
      "n": 81,
      "binaries": 0
    },
    {
      "support_level": "deep",
      "language": "javascript",
      "n": 47,
      "binaries": 0
    },
    {
      "support_level": "deep",
      "language": "typescript",
      "n": 15,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "css",
      "n": 15,
      "binaries": 0
    },
    {
      "support_level": "deep",
      "language": "python",
      "n": 13,
      "binaries": 0
    },
    {
      "support_level": "deep",
      "language": "java",
      "n": 11,
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
      "language": "sql",
      "n": 6,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "rust",
      "n": 5,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "c#",
      "n": 5,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "go",
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
      "language": "php",
      "n": 1,
      "binaries": 0
    }
  ],
  "chunks": {
    "total": 956,
    "verified_deep": 116,
    "llm_enriched": 0,
    "unique_spans": 956,
    "with_parser": 956
  },
  "chunk_breakdown": [
    {
      "language": "documentation",
      "support_level": "generic",
      "extraction_method": "markdown_ast",
      "parser_name": "mistune-ast",
      "n": 250
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "json-stdlib",
      "n": 238
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "yaml-compose",
      "n": 177
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "dockerfile-parse",
      "n": 92
    },
    {
      "language": "javascript",
      "support_level": "deep",
      "extraction_method": "deep_symbol",
      "parser_name": "javascript-treesitter",
      "n": 52
    },
    {
      "language": "java",
      "support_level": "deep",
      "extraction_method": "deep_symbol",
      "parser_name": "java-treesitter",
      "n": 41
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "defusedxml-sax",
      "n": 34
    },
    {
      "language": "rust",
      "support_level": "generic",
      "extraction_method": "treesitter_node",
      "parser_name": "rust-treesitter",
      "n": 21
    },
    {
      "language": "python",
      "support_level": "deep",
      "extraction_method": "deep_symbol",
      "parser_name": "python-ast",
      "n": 13
    },
    {
      "language": "go",
      "support_level": "generic",
      "extraction_method": "treesitter_node",
      "parser_name": "go-treesitter",
      "n": 12
    },
    {
      "language": "typescript",
      "support_level": "deep",
      "extraction_method": "deep_symbol",
      "parser_name": "typescript-treesitter",
      "n": 8
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "tomllib",
      "n": 6
    },
    {
      "language": "sql",
      "support_level": "generic",
      "extraction_method": "sqlglot_tokenizer",
      "parser_name": "sqlglot",
      "n": 6
    },
    {
      "language": "c#",
      "support_level": "generic",
      "extraction_method": "treesitter_node",
      "parser_name": "csharp-treesitter",
      "n": 4
    },
    {
      "language": "typescript",
      "support_level": "deep",
      "extraction_method": "deep_symbol",
      "parser_name": "tsx-treesitter",
      "n": 2
    }
  ],
  "nodes_by_type": {
    "javascript:import": 57,
    "java:import": 51,
    "javascript:function": 50,
    "typescript:import": 34,
    "python:import": 25,
    "java:method": 24,
    "java:package": 9,
    "java:class": 9,
    "python:function": 9,
    "javascript:method": 8,
    "java:constructor": 6,
    "java:field": 6,
    "typescript:function": 5,
    "python:method": 3,
    "javascript:class": 3,
    "typescript:class": 3,
    "java:interface": 2,
    "typescript:type_alias": 2,
    "python:class": 1
  },
  "edges_by_kind": {
    "imports": 167,
    "contains": 41,
    "extends": 2,
    "implements": 1
  },
  "edges_by_confidence": {
    "unresolved": 126,
    "resolved": 74,
    "ambiguous": 11
  },
  "call_totals": {
    "total": 255,
    "resolved": 22,
    "ambiguous": 0,
    "unresolved": 233
  },
  "inheritance_counts": [
    {
      "relation_kind": "extends",
      "confidence": "unresolved",
      "n": 2
    },
    {
      "relation_kind": "implements",
      "confidence": "unresolved",
      "n": 1
    }
  ],
  "symbol_totals": {
    "total": 307,
    "fake_deep": 0
  },
  "language_mix": {
    "configuration": 142,
    "documentation": 81,
    "javascript": 47,
    "css": 15,
    "typescript": 15,
    "python": 13,
    "java": 11,
    "html": 9,
    "sql": 6,
    "c#": 5,
    "rust": 5,
    "go": 4,
    "php": 1,
    "shell": 1
  }
}
```

## Exact search

```json
[
  {
    "query": "docker-compose",
    "total": 31,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "angular/README.md",
        "start_line": 31,
        "end_line": 48,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "fastapi/README.md",
        "start_line": 29,
        "end_line": 33,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "minecraft/README.md",
        "start_line": 39,
        "end_line": 82,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "nginx-flask-mysql/README.md",
        "start_line": 44,
        "end_line": 58,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "nginx-golang-mysql/README.md",
        "start_line": 54,
        "end_line": 70,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "postgres",
    "total": 60,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "gitea-postgres/compose.yaml",
        "start_line": 1,
        "end_line": 26,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "gitea-postgres/compose.yaml",
        "start_line": 2,
        "end_line": 15,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "gitea-postgres/compose.yaml",
        "start_line": 15,
        "end_line": 26,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "gitea-postgres/README.md",
        "start_line": 1,
        "end_line": 28,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "gitea-postgres/README.md",
        "start_line": 29,
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
    "query": "redis",
    "total": 24,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "CONTRIBUTING.md",
        "start_line": 51,
        "end_line": 103,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "flask-redis/app.py",
        "start_line": 8,
        "end_line": 11,
        "language": "python",
        "support_level": "deep",
        "verified_deep": true
      },
      {
        "path": "flask-redis/compose.yaml",
        "start_line": 1,
        "end_line": 19,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "flask-redis/compose.yaml",
        "start_line": 2,
        "end_line": 6,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "flask-redis/compose.yaml",
        "start_line": 6,
        "end_line": 19,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "nginx",
    "total": 61,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "elasticsearch-logstash-kibana/compose.yaml",
        "start_line": 1,
        "end_line": 46,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "elasticsearch-logstash-kibana/compose.yaml",
        "start_line": 18,
        "end_line": 37,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "elasticsearch-logstash-kibana/README.md",
        "start_line": 56,
        "end_line": 58,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "nginx-aspnet-mysql/proxy/Dockerfile",
        "start_line": 1,
        "end_line": 2,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "nginx-aspnet-mysql/README.md",
        "start_line": 2,
        "end_line": 47,
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
    "node_count": 148,
    "edge_count": 138,
    "graph_type": "modules",
    "snapshot_id": "9202ad67-c514-470b-8d8e-5d844d787f26",
    "filters": {
      "local_imports_only": false,
      "max_nodes": 500,
      "max_edges": 2000
    },
    "sample_nodes": [
      {
        "id": "@angular/core",
        "label": "@angular/core",
        "node_type": "module",
        "language": "typescript",
        "support_level": "generic",
        "path": null,
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "@angular/core/testing",
        "label": "@angular/core/testing",
        "node_type": "module",
        "language": "typescript",
        "support_level": "generic",
        "path": null,
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "@angular/platform-browser",
        "label": "@angular/platform-browser",
        "node_type": "module",
        "language": "typescript",
        "support_level": "generic",
        "path": null,
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "@angular/platform-browser-dynamic",
        "label": "@angular/platform-browser-dynamic",
        "node_type": "module",
        "language": "typescript",
        "support_level": "generic",
        "path": null,
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "@angular/platform-browser-dynamic/testing",
        "label": "@angular/platform-browser-dynamic/testing",
        "node_type": "module",
        "language": "typescript",
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
        "source": "angular.angular.src.app.app-routing.module",
        "target": "@angular/core",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "typescript",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "angular.angular.src.app.app-routing.module",
        "target": "@angular/router",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "typescript",
        "weight": 2,
        "inferred": false,
        "line": null
      },
      {
        "source": "angular.angular.src.app.app.component",
        "target": "@angular/core",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "typescript",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "angular.angular.src.app.app.component.spec",
        "target": "@angular/core/testing",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "typescript",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "angular.angular.src.app.app.component.spec",
        "target": "@angular/router/testing",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "typescript",
        "weight": 1,
        "inferred": false,
        "line": null
      }
    ]
  },
  "packages": {
    "node_count": 59,
    "edge_count": 15,
    "graph_type": "packages",
    "snapshot_id": "9202ad67-c514-470b-8d8e-5d844d787f26",
    "filters": {
      "local_imports_only": true,
      "max_nodes": 500,
      "max_edges": 2000
    },
    "sample_nodes": [
      {
        "id": "angular.angular.karma",
        "label": "angular.angular.karma",
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
        "id": "angular.angular.src",
        "label": "angular.angular.src",
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
        "id": "angular.angular.src.app.app",
        "label": "angular.angular.src.app.app",
        "node_type": "package",
        "language": "typescript",
        "support_level": "deep",
        "path": null,
        "symbol_count": 2,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "angular.angular.src.app.app-routing",
        "label": "angular.angular.src.app.app-routing",
        "node_type": "package",
        "language": "typescript",
        "support_level": "deep",
        "path": null,
        "symbol_count": 1,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "angular.angular.src.app.app.component",
        "label": "angular.angular.src.app.app.component",
        "node_type": "package",
        "language": "typescript",
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
        "source": "angular.angular.src",
        "target": "angular.angular.src.app.app",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "typescript",
        "weight": 1,
        "inferred": true,
        "line": null
      },
      {
        "source": "angular.angular.src",
        "target": "angular.angular.src.environments",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "typescript",
        "weight": 1,
        "inferred": true,
        "line": null
      },
      {
        "source": "angular.angular.src.app.app",
        "target": "angular.angular.src.app.app-routing",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "typescript",
        "weight": 1,
        "inferred": true,
        "line": null
      },
      {
        "source": "angular.angular.src.app.app.component",
        "target": "angular.angular.src.app.app",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "typescript",
        "weight": 1,
        "inferred": true,
        "line": null
      },
      {
        "source": "react-express-mongodb.frontend",
        "target": "react-express-mongodb.frontend.src",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "javascript",
        "weight": 2,
        "inferred": true,
        "line": null
      }
    ]
  },
  "directories": {
    "node_count": 167,
    "edge_count": 169,
    "graph_type": "directories",
    "snapshot_id": "9202ad67-c514-470b-8d8e-5d844d787f26",
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
        "id": "angular",
        "label": "angular",
        "node_type": "directory",
        "language": null,
        "support_level": "mixed",
        "path": null,
        "symbol_count": 0,
        "file_count": 2,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "angular/angular",
        "label": "angular/angular",
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
        "target": "angular",
        "relation_kind": "contains",
        "confidence": "resolved",
        "language": null,
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": ".",
        "target": "apache-php",
        "relation_kind": "contains",
        "confidence": "resolved",
        "language": null,
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": ".",
        "target": "aspnet-mssql",
        "relation_kind": "contains",
        "confidence": "resolved",
        "language": null,
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": ".",
        "target": "django",
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
    "node_count": 167,
    "edge_count": 166,
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
  "repository_id": "fbbf6457-8d89-4191-8f5a-a86da1cff1a9",
  "snapshot_id": "9202ad67-c514-470b-8d8e-5d844d787f26",
  "commit_sha": "30f4b7f6a6c3b0c0ecf4d4efb0de203c48d11562",
  "status": "SUCCEEDED",
  "indexing_duration_seconds": 5.08,
  "files": {
    "total": 479,
    "skipped": 124,
    "binaries": 50,
    "distinct_hashes": 311
  },
  "chunks": {
    "total": 956,
    "verified_deep": 116,
    "llm_enriched": 0,
    "distinct_content_hashes": 751,
    "unique_spans": 956,
    "with_parser": 956
  },
  "edges_by_kind": {
    "imports": 167,
    "contains": 41,
    "extends": 2,
    "implements": 1
  },
  "call_totals": {
    "total": 255,
    "resolved": 22,
    "ambiguous": 0,
    "unresolved": 233
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
