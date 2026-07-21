# Generalization validation — Python API — pallets/flask

- URL: https://github.com/pallets/flask
- Generated: 2026-07-20T03:06:14.834382+00:00
- API: `http://127.0.0.1:8001`
- LLM enrichment: **OFF**
- Clone size limit: 52428800 bytes (unchanged)

## Checks

| Check | Result | Detail |
| --- | --- | --- |
| repository imported successfully | PASS | status=SUCCEEDED err=None:None |
| snapshot created | PASS | 13b3f479-bcaf-498b-ad3b-05e1237f5a90 |
| files discovered | PASS | total=236 skipped=17 binaries=8 |
| chunks persisted | PASS | chunks=1037 unique_spans=1037 |
| no duplicate chunk spans | PASS | total=1037 unique=1037 |
| parser provenance stored | PASS | with_parser_name=1037 with_version=1037 |
| optional enrichment OFF | PASS | llm_enriched=0 |
| no fake verified symbols for non-deep langs | PASS | fake_deep=0 |
| deep analysis for expected languages | PASS | symbol_langs=['python'] verified_deep_chunks=919 |
| deterministic repository summary | PASS | llm_summary_status=disabled |
| exact chunk search operational | PASS | Flask→469; request→241; blueprint→127; route→214 |
| relation kinds only from unified model | PASS | kinds={'imports': 576, 'contains': 332} |
| no orphan from_symbol dangling IDs | PASS | orphans=0 |
| no orphan to_symbol dangling IDs | PASS | orphans=0 |
| no cross-snapshot relation leakage | PASS | cross=0 |
| no duplicate structural relation keys | PASS | total=908 unique=908 |
| IMPORTS/CONTAINS present for deep repo | PASS | edges={'imports': 576, 'contains': 332} |
| CALLS persisted with resolution labels | PASS | resolved=210 ambiguous=39 unresolved=3592 |
| modules graph returns | PASS | nodes=184 edges=423 |
| modules graph no host path leakage | PASS | leaked=0 |
| packages graph returns | PASS | nodes=23 edges=6 |
| packages graph no host path leakage | PASS | leaked=0 |
| directory graph usable | PASS | nodes=51 edges=54 |
| directories graph no host path leakage | PASS | leaked=0 |
| callers/callees neighborhood API | PASS | center=tests.test_config.common_object_test d1_nodes=9 |
| call edges carry confidence labels | PASS | confidences_seen=['resolved'] |
| ambiguous call symbols present | PASS | examples.tutorial.flaskr.auth.register |
| unresolved/external calls present or documented | PASS | unresolved_samples=5 |
| symbol with no callers found | PASS | count=3 |
| callers/callees list endpoints | PASS | callers=11 callees=0 |
| invalid filter returns validation error | PASS | status=422 body={"detail":{"code":"invalid_support_level","message":"support_level must be deep, generic, mixed, or skip"}} |
| invalid confidence rejected | PASS | status=422 |
| graph node/edge limits applied | PASS | nodes=5 edges=4 |
| path_prefix filter accepted | PASS | nodes=4 |
| language filter on modules | PASS | requested=python seen=['python'] |
| inferred=false filter respected | PASS | inferred_remaining=0 total_edges=50 |
| React Flow page wired to live graph APIs | PASS | {"loads_from_api": true, "no_fixture_data_in_page": true, "has_relation_filters": true, "has_language_filter": true, "has_support_level_filter": true, "has_depth_control": true, "has_generic_honesty_notice": true, "has_inferred_edge_styling": true, "selection_detail_panel": true, "uses_xyflow": true} |
| generic honesty notice present in Graph UI | PASS | GraphPage honesty copy checked |
| no regex structural parsing in chunking package | PASS | offenders=[] |
| re-index succeeded | PASS | status=SUCCEEDED duration_s=5.0 |
| stable content hashes on re-index | PASS | common=219 mismatches=0 |
| no duplicate chunks after re-index | PASS | total=1037 unique=1037 |
| deterministic chunk multiset on re-index | PASS | prev=1037 new=1037 |
| deterministic relationship multiset on re-index | PASS | prev=908 new=908 |
| deterministic call multiset on re-index | PASS | prev=3841 new=3841 |
| no duplicate relations after re-index | PASS | total=908 unique=908 |
| no cross-snapshot leakage after re-index | PASS | cross=0 |
| stable graph API output ordering | PASS | nodes=50 |

## Metrics

```json
{
  "repository_id": "380d1380-a6e9-4d54-b857-6643e108e610",
  "snapshot_id": "13b3f479-bcaf-498b-ad3b-05e1237f5a90",
  "commit_sha": "36e4a824f340fdee7ed50937ba8e7f6bc7d17f81",
  "indexing_duration_seconds": 5.05,
  "files": {
    "total": 236,
    "skipped": 17,
    "binaries": 8,
    "distinct_hashes": 215
  },
  "files_by_lang_level": [
    {
      "support_level": "generic",
      "language": "documentation",
      "n": 95,
      "binaries": 0
    },
    {
      "support_level": "deep",
      "language": "python",
      "n": 83,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "html",
      "n": 20,
      "binaries": 0
    },
    {
      "support_level": "skip",
      "language": null,
      "n": 17,
      "binaries": 8
    },
    {
      "support_level": "generic",
      "language": "configuration",
      "n": 16,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "sql",
      "n": 2,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "css",
      "n": 2,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "shell",
      "n": 1,
      "binaries": 0
    }
  ],
  "chunks": {
    "total": 1037,
    "verified_deep": 919,
    "llm_enriched": 0,
    "unique_spans": 1037,
    "with_parser": 1037,
    "with_parser_version": 1037
  },
  "chunk_breakdown": [
    {
      "language": "python",
      "support_level": "deep",
      "extraction_method": "deep_symbol",
      "parser_name": "python-ast",
      "n": 919
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "tomllib",
      "n": 54
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "yaml-compose",
      "n": 46
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "json-stdlib",
      "n": 6
    },
    {
      "language": "documentation",
      "support_level": "generic",
      "extraction_method": "markdown_ast",
      "parser_name": "mistune-ast",
      "n": 6
    },
    {
      "language": "sql",
      "support_level": "generic",
      "extraction_method": "sqlglot_tokenizer",
      "parser_name": "sqlglot",
      "n": 6
    }
  ],
  "nodes_by_type": {
    "python:import": 576,
    "python:function": 523,
    "python:method": 332,
    "python:class": 64
  },
  "edges_by_kind": {
    "imports": 576,
    "contains": 332
  },
  "edges_by_confidence": {
    "unresolved": 482,
    "resolved": 425,
    "ambiguous": 1
  },
  "call_totals": {
    "total": 3841,
    "resolved": 210,
    "ambiguous": 39,
    "unresolved": 3592
  },
  "inheritance_counts": [],
  "symbol_totals": {
    "total": 1495,
    "fake_deep": 0
  },
  "language_mix": {
    "documentation": 95,
    "python": 83,
    "html": 20,
    "configuration": 16,
    "sql": 2,
    "css": 2,
    "shell": 1
  }
}
```

## Exact search

```json
[
  {
    "query": "Flask",
    "total": 469,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": ".devcontainer/devcontainer.json",
        "start_line": 2,
        "end_line": 2,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "docs/conf.py",
        "start_line": 72,
        "end_line": 97,
        "language": "python",
        "support_level": "deep",
        "verified_deep": true
      },
      {
        "path": "examples/celery/pyproject.toml",
        "start_line": 1,
        "end_line": 8,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "examples/celery/src/task_app/__init__.py",
        "start_line": 7,
        "end_line": 26,
        "language": "python",
        "support_level": "deep",
        "verified_deep": true
      },
      {
        "path": "examples/celery/src/task_app/__init__.py",
        "start_line": 29,
        "end_line": 39,
        "language": "python",
        "support_level": "deep",
        "verified_deep": true
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "request",
    "total": 241,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "examples/celery/src/task_app/views.py",
        "start_line": 22,
        "end_line": 26,
        "language": "python",
        "support_level": "deep",
        "verified_deep": true
      },
      {
        "path": "examples/celery/src/task_app/views.py",
        "start_line": 36,
        "end_line": 38,
        "language": "python",
        "support_level": "deep",
        "verified_deep": true
      },
      {
        "path": "examples/javascript/js_example/views.py",
        "start_line": 15,
        "end_line": 18,
        "language": "python",
        "support_level": "deep",
        "verified_deep": true
      },
      {
        "path": "examples/javascript/pyproject.toml",
        "start_line": 1,
        "end_line": 10,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "examples/tutorial/flaskr/auth.py",
        "start_line": 47,
        "end_line": 81,
        "language": "python",
        "support_level": "deep",
        "verified_deep": true
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "blueprint",
    "total": 127,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "examples/celery/src/task_app/__init__.py",
        "start_line": 7,
        "end_line": 26,
        "language": "python",
        "support_level": "deep",
        "verified_deep": true
      },
      {
        "path": "examples/tutorial/flaskr/__init__.py",
        "start_line": 6,
        "end_line": 48,
        "language": "python",
        "support_level": "deep",
        "verified_deep": true
      },
      {
        "path": "src/flask/app.py",
        "start_line": 109,
        "end_line": 1625,
        "language": "python",
        "support_level": "deep",
        "verified_deep": true
      },
      {
        "path": "src/flask/app.py",
        "start_line": 310,
        "end_line": 363,
        "language": "python",
        "support_level": "deep",
        "verified_deep": true
      },
      {
        "path": "src/flask/app.py",
        "start_line": 392,
        "end_line": 412,
        "language": "python",
        "support_level": "deep",
        "verified_deep": true
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "route",
    "total": 214,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "examples/celery/src/task_app/__init__.py",
        "start_line": 7,
        "end_line": 26,
        "language": "python",
        "support_level": "deep",
        "verified_deep": true
      },
      {
        "path": "examples/tutorial/flaskr/__init__.py",
        "start_line": 6,
        "end_line": 48,
        "language": "python",
        "support_level": "deep",
        "verified_deep": true
      },
      {
        "path": "README.md",
        "start_line": 20,
        "end_line": 37,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "src/flask/app.py",
        "start_line": 109,
        "end_line": 1625,
        "language": "python",
        "support_level": "deep",
        "verified_deep": true
      },
      {
        "path": "src/flask/app.py",
        "start_line": 310,
        "end_line": 363,
        "language": "python",
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
    "node_count": 184,
    "edge_count": 423,
    "graph_type": "modules",
    "snapshot_id": "13b3f479-bcaf-498b-ad3b-05e1237f5a90",
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
        "id": "_pytest",
        "label": "_pytest",
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
        "id": "_pytest.monkeypatch",
        "label": "_pytest.monkeypatch",
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
        "id": "ast",
        "label": "ast",
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
        "id": "asyncio",
        "label": "asyncio",
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
        "source": "docs.conf",
        "target": "packaging",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "docs.conf",
        "target": "pallets_sphinx_themes",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "python",
        "weight": 2,
        "inferred": false,
        "line": null
      },
      {
        "source": "examples.celery.make_celery",
        "target": "task_app",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "examples.celery.src.task_app",
        "target": "celery",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "python",
        "weight": 2,
        "inferred": false,
        "line": null
      },
      {
        "source": "examples.celery.src.task_app",
        "target": "flask",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "python",
        "weight": 2,
        "inferred": false,
        "line": null
      }
    ]
  },
  "packages": {
    "node_count": 23,
    "edge_count": 6,
    "graph_type": "packages",
    "snapshot_id": "13b3f479-bcaf-498b-ad3b-05e1237f5a90",
    "filters": {
      "local_imports_only": true,
      "max_nodes": 500,
      "max_edges": 2000
    },
    "sample_nodes": [
      {
        "id": "docs",
        "label": "docs",
        "node_type": "package",
        "language": "python",
        "support_level": "deep",
        "path": null,
        "symbol_count": 2,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "examples.celery",
        "label": "examples.celery",
        "node_type": "package",
        "language": "python",
        "support_level": "deep",
        "path": null,
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "examples.celery.src",
        "label": "examples.celery.src",
        "node_type": "package",
        "language": "python",
        "support_level": "deep",
        "path": null,
        "symbol_count": 2,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "examples.celery.src.task_app",
        "label": "examples.celery.src.task_app",
        "node_type": "package",
        "language": "python",
        "support_level": "deep",
        "path": null,
        "symbol_count": 7,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "examples.javascript",
        "label": "examples.javascript",
        "node_type": "package",
        "language": "python",
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
        "source": "examples.javascript.js_example",
        "target": "examples.javascript",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": true,
        "line": null
      },
      {
        "source": "src.flask",
        "target": "src.flask.json",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": true,
        "line": null
      },
      {
        "source": "src.flask",
        "target": "src.flask.sansio",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "python",
        "weight": 5,
        "inferred": true,
        "line": null
      },
      {
        "source": "src.flask.json",
        "target": "src.flask",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "python",
        "weight": 2,
        "inferred": true,
        "line": null
      },
      {
        "source": "src.flask.sansio",
        "target": "src.flask",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "python",
        "weight": 13,
        "inferred": true,
        "line": null
      }
    ]
  },
  "directories": {
    "node_count": 51,
    "edge_count": 54,
    "graph_type": "directories",
    "snapshot_id": "13b3f479-bcaf-498b-ad3b-05e1237f5a90",
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
        "file_count": 6,
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
        "file_count": 2,
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
        "file_count": 5,
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
        "target": "src",
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
    "center": "tests.test_config.common_object_test",
    "node_count": 9,
    "edge_count": 11,
    "depth": 1,
    "sample_edges": [
      {
        "source": "07c2bbb0-c824-450f-9b7d-511f26e01c9a",
        "target": "e8992d8a-ef7e-437a-b047-23b475cd85b0",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 22
      },
      {
        "source": "1cd6671f-5d23-4951-9dae-94a280df0dda",
        "target": "e8992d8a-ef7e-437a-b047-23b475cd85b0",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 28
      },
      {
        "source": "33f2d0a0-ecd7-45df-a753-4cd4615bc555",
        "target": "e8992d8a-ef7e-437a-b047-23b475cd85b0",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 208
      },
      {
        "source": "451b4db9-b348-468b-bf7d-0e58c6d02c0d",
        "target": "e8992d8a-ef7e-437a-b047-23b475cd85b0",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 45
      },
      {
        "source": "571f0fae-dd70-40f7-b5bb-87f4dcdeef1f",
        "target": "e8992d8a-ef7e-437a-b047-23b475cd85b0",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 141
      },
      {
        "source": "660cde01-cd7e-4b7e-b46d-9e6310e9a88a",
        "target": "e8992d8a-ef7e-437a-b047-23b475cd85b0",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 158
      },
      {
        "source": "a9c0502e-eaf1-40a2-8fc6-dee1e28cdab1",
        "target": "e8992d8a-ef7e-437a-b047-23b475cd85b0",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 35
      },
      {
        "source": "acbe0b4a-0aa9-441e-b5ff-797c61c19c85",
        "target": "e8992d8a-ef7e-437a-b047-23b475cd85b0",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 113
      }
    ]
  },
  "calls_depth_2": {
    "center": "tests.test_config.common_object_test",
    "node_count": 10,
    "edge_count": 23,
    "depth": 2,
    "sample_edges": [
      {
        "source": "07c2bbb0-c824-450f-9b7d-511f26e01c9a",
        "target": "e8992d8a-ef7e-437a-b047-23b475cd85b0",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 22
      },
      {
        "source": "07c2bbb0-c824-450f-9b7d-511f26e01c9a",
        "target": "fb613574-d07c-4c6f-ac7e-dfe4a00f5808",
        "relation_kind": "calls",
        "confidence": "unresolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 20
      },
      {
        "source": "1cd6671f-5d23-4951-9dae-94a280df0dda",
        "target": "e8992d8a-ef7e-437a-b047-23b475cd85b0",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 28
      },
      {
        "source": "1cd6671f-5d23-4951-9dae-94a280df0dda",
        "target": "fb613574-d07c-4c6f-ac7e-dfe4a00f5808",
        "relation_kind": "calls",
        "confidence": "unresolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 26
      },
      {
        "source": "33f2d0a0-ecd7-45df-a753-4cd4615bc555",
        "target": "e8992d8a-ef7e-437a-b047-23b475cd85b0",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 208
      },
      {
        "source": "33f2d0a0-ecd7-45df-a753-4cd4615bc555",
        "target": "fb613574-d07c-4c6f-ac7e-dfe4a00f5808",
        "relation_kind": "calls",
        "confidence": "unresolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 205
      },
      {
        "source": "451b4db9-b348-468b-bf7d-0e58c6d02c0d",
        "target": "e8992d8a-ef7e-437a-b047-23b475cd85b0",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 45
      },
      {
        "source": "451b4db9-b348-468b-bf7d-0e58c6d02c0d",
        "target": "fb613574-d07c-4c6f-ac7e-dfe4a00f5808",
        "relation_kind": "calls",
        "confidence": "unresolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 40
      }
    ]
  },
  "callers_api": {
    "total": 11,
    "sample": [
      {
        "id": "d7aca03e-7b4c-45aa-94dd-804d6b373f29",
        "snapshot_id": "13b3f479-bcaf-498b-ad3b-05e1237f5a90",
        "source_file_id": "f22bdf9d-df75-47a9-9b8f-0cd51de7bdf6",
        "path": "tests/test_config.py",
        "caller_symbol_id": "07c2bbb0-c824-450f-9b7d-511f26e01c9a",
        "caller_qualified_name": "tests.test_config.test_config_from_pyfile",
        "raw_callee": "common_object_test",
        "qualified_expression": "common_object_test",
        "line": 22,
        "candidate_qualified_name": "tests.test_config.common_object_test",
        "confidence": "resolved",
        "language": "python",
        "created_at": "2026-07-20T03:05:09.967312Z"
      },
      {
        "id": "77b51126-c020-42b2-9085-a9619d42b39e",
        "snapshot_id": "13b3f479-bcaf-498b-ad3b-05e1237f5a90",
        "source_file_id": "f22bdf9d-df75-47a9-9b8f-0cd51de7bdf6",
        "path": "tests/test_config.py",
        "caller_symbol_id": "1cd6671f-5d23-4951-9dae-94a280df0dda",
        "caller_qualified_name": "tests.test_config.test_config_from_object",
        "raw_callee": "common_object_test",
        "qualified_expression": "common_object_test",
        "line": 28,
        "candidate_qualified_name": "tests.test_config.common_object_test",
        "confidence": "resolved",
        "language": "python",
        "created_at": "2026-07-20T03:05:09.967312Z"
      },
      {
        "id": "c131878d-959e-4cc5-a6e1-85289665d4b7",
        "snapshot_id": "13b3f479-bcaf-498b-ad3b-05e1237f5a90",
        "source_file_id": "f22bdf9d-df75-47a9-9b8f-0cd51de7bdf6",
        "path": "tests/test_config.py",
        "caller_symbol_id": "a9c0502e-eaf1-40a2-8fc6-dee1e28cdab1",
        "caller_qualified_name": "tests.test_config.test_config_from_file_json",
        "raw_callee": "common_object_test",
        "qualified_expression": "common_object_test",
        "line": 35,
        "candidate_qualified_name": "tests.test_config.common_object_test",
        "confidence": "resolved",
        "language": "python",
        "created_at": "2026-07-20T03:05:09.967312Z"
      },
      {
        "id": "5bb143c8-70b3-41bd-80e5-b1c088bc371d",
        "snapshot_id": "13b3f479-bcaf-498b-ad3b-05e1237f5a90",
        "source_file_id": "f22bdf9d-df75-47a9-9b8f-0cd51de7bdf6",
        "path": "tests/test_config.py",
        "caller_symbol_id": "451b4db9-b348-468b-bf7d-0e58c6d02c0d",
        "caller_qualified_name": "tests.test_config.test_config_from_file_toml",
        "raw_callee": "common_object_test",
        "qualified_expression": "common_object_test",
        "line": 45,
        "candidate_qualified_name": "tests.test_config.common_object_test",
        "confidence": "resolved",
        "language": "python",
        "created_at": "2026-07-20T03:05:09.967312Z"
      },
      {
        "id": "9702a715-02bc-45be-bfc0-ab8dbc07edf4",
        "snapshot_id": "13b3f479-bcaf-498b-ad3b-05e1237f5a90",
        "source_file_id": "f22bdf9d-df75-47a9-9b8f-0cd51de7bdf6",
        "path": "tests/test_config.py",
        "caller_symbol_id": "acbe0b4a-0aa9-441e-b5ff-797c61c19c85",
        "caller_qualified_name": "tests.test_config.test_config_from_mapping",
        "raw_callee": "common_object_test",
        "qualified_expression": "common_object_test",
        "line": 113,
        "candidate_qualified_name": "tests.test_config.common_object_test",
        "confidence": "resolved",
        "language": "python",
        "created_at": "2026-07-20T03:05:09.967312Z"
      }
    ]
  },
  "callees_api": {
    "total": 0,
    "sample": []
  }
}
```

## Callers / callees samples

```json
{
  "multi_caller": {
    "qn": "tests.test_config.common_object_test",
    "callers": 11
  },
  "multi_callee": {
    "qn": "tests.test_basic.index",
    "callees": 43
  },
  "ambiguous_symbol": {
    "id": "aaf042ac-198d-4cc2-81fa-04130d8024c3",
    "qualified_name": "examples.tutorial.flaskr.auth.register",
    "language": "python",
    "kind": "function"
  },
  "unresolved_samples": [
    {
      "caller_qualified_name": "docs.conf.github_link",
      "raw_callee": "text.endswith",
      "confidence": "unresolved",
      "line": 77,
      "language": "python"
    },
    {
      "caller_qualified_name": "docs.conf.github_link",
      "raw_callee": "text[:-1].rsplit",
      "confidence": "unresolved",
      "line": 78,
      "language": "python"
    },
    {
      "caller_qualified_name": "docs.conf.github_link",
      "raw_callee": "words.strip",
      "confidence": "unresolved",
      "line": 79,
      "language": "python"
    },
    {
      "caller_qualified_name": "docs.conf.github_link",
      "raw_callee": "packaging.version.parse",
      "confidence": "unresolved",
      "line": 83,
      "language": "python"
    },
    {
      "caller_qualified_name": "docs.conf.github_link",
      "raw_callee": "set_classes",
      "confidence": "unresolved",
      "line": 95,
      "language": "python"
    }
  ],
  "no_callers": [
    {
      "id": "2907e5d2-d478-41d6-a6d3-56f5d8cd377b",
      "qualified_name": "docs.conf.github_link",
      "kind": "function",
      "language": "python"
    },
    {
      "id": "4273806b-5888-4ff6-ada4-710e4e28f93b",
      "qualified_name": "docs.conf.setup",
      "kind": "function",
      "language": "python"
    },
    {
      "id": "df83f397-f776-4793-97a6-4eb4d5f55965",
      "qualified_name": "examples.celery.src.task_app.create_app",
      "kind": "function",
      "language": "python"
    }
  ],
  "multi_caller_symbol": {
    "id": "e8992d8a-ef7e-437a-b047-23b475cd85b0",
    "qualified_name": "tests.test_config.common_object_test",
    "kind": "function",
    "language": "python",
    "start_line": 13,
    "end_line": 16
  },
  "multi_callee_symbol": {
    "qualified_name": "tests.test_basic.index"
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
    "node_count": 4,
    "edge_count": 7
  },
  "modules_lang_python": {
    "node_count": 100,
    "edge_count": 112,
    "filters": {
      "language": "python",
      "local_imports_only": false,
      "max_nodes": 100,
      "max_edges": 200
    }
  },
  "inferred_false": {
    "node_count": 51,
    "edge_count": 50,
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
  "repository_id": "380d1380-a6e9-4d54-b857-6643e108e610",
  "snapshot_id": "13b3f479-bcaf-498b-ad3b-05e1237f5a90",
  "commit_sha": "36e4a824f340fdee7ed50937ba8e7f6bc7d17f81",
  "status": "SUCCEEDED",
  "indexing_duration_seconds": 5.03,
  "files": {
    "total": 236,
    "skipped": 17,
    "binaries": 8,
    "distinct_hashes": 215
  },
  "chunks": {
    "total": 1037,
    "verified_deep": 919,
    "llm_enriched": 0,
    "distinct_content_hashes": 1021,
    "unique_spans": 1037,
    "with_parser": 1037,
    "with_parser_version": 1037
  },
  "edges_by_kind": {
    "imports": 576,
    "contains": 332
  },
  "call_totals": {
    "total": 3841,
    "resolved": 210,
    "ambiguous": 39,
    "unresolved": 3592
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
