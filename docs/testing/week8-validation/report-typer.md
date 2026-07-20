# Week 8 validation — Python — fastapi/typer

- URL: https://github.com/fastapi/typer
- Generated: 2026-07-20T02:31:22.553167+00:00
- API: `http://127.0.0.1:8001`
- LLM enrichment: **OFF**
- Clone size limit: 52428800 bytes (unchanged)

## Checks

| Check | Result | Detail |
| --- | --- | --- |
| repository imported successfully | PASS | status=SUCCEEDED err=None:None |
| snapshot created | PASS | 6440e822-d927-45cf-82df-c8c7031f4fef |
| files discovered | PASS | total=773 skipped=18 binaries=11 |
| chunks persisted | PASS | chunks=2904 unique_spans=2904 |
| no duplicate chunk spans | PASS | total=2904 unique=2904 |
| optional enrichment OFF | PASS | llm_enriched=0 |
| no fake verified symbols for non-deep langs | PASS | fake_deep=0 |
| deep analysis for expected languages | PASS | symbol_langs=['javascript', 'python'] verified_deep_chunks=2161 |
| deterministic repository summary | PASS | llm_summary_status=disabled |
| exact chunk search operational | PASS | Typer→1076; command→528; Option→603; callback→185 |
| relation kinds only from unified model | PASS | kinds={'imports': 2097, 'contains': 366} |
| no orphan from_symbol dangling IDs | PASS | orphans=0 |
| no orphan to_symbol dangling IDs | PASS | orphans=0 |
| no cross-snapshot relation leakage | PASS | cross=0 |
| no duplicate structural relation keys | PASS | total=2463 unique=2463 |
| IMPORTS/CONTAINS present for deep repo | PASS | edges={'imports': 2097, 'contains': 366} |
| CALLS persisted with resolution labels | PASS | resolved=1082 ambiguous=377 unresolved=5274 |
| modules graph returns | PASS | nodes=500 edges=613 |
| modules graph no host path leakage | PASS | leaked=0 |
| packages graph returns | PASS | nodes=122 edges=144 |
| packages graph no host path leakage | PASS | leaked=0 |
| directory graph usable | PASS | nodes=142 edges=289 |
| directories graph no host path leakage | PASS | leaked=0 |
| callers/callees neighborhood API | PASS | center=typer._click.utils.echo d1_nodes=65 |
| call edges carry confidence labels | PASS | confidences_seen=['resolved'] |
| ambiguous call symbols present | PASS | docs_src.arguments.default.tutorial001_an_py310.main |
| unresolved/external calls present or documented | PASS | unresolved_samples=5 |
| symbol with no callers found | PASS | count=3 |
| callers/callees list endpoints | PASS | callers=20 callees=0 |
| invalid filter returns validation error | PASS | status=422 body={"detail":{"code":"invalid_support_level","message":"support_level must be deep, generic, mixed, or skip"}} |
| invalid confidence rejected | PASS | status=422 |
| graph node/edge limits applied | PASS | nodes=5 edges=4 |
| path_prefix filter accepted | PASS | nodes=0 |
| language filter on modules | PASS | requested=python seen=['python'] |
| inferred=false filter respected | PASS | inferred_remaining=0 total_edges=141 |
| React Flow page wired to live graph APIs | PASS | {"loads_from_api": true, "no_fixture_data_in_page": true, "has_relation_filters": true, "has_language_filter": true, "has_support_level_filter": true, "has_depth_control": true, "has_generic_honesty_notice": true, "has_inferred_edge_styling": true, "selection_detail_panel": true, "uses_xyflow": true} |
| generic honesty notice present in Graph UI | PASS | GraphPage honesty copy checked |
| no regex structural parsing in chunking package | PASS | offenders=[] |
| re-index succeeded | PASS | status=SUCCEEDED duration_s=10.0 |
| stable content hashes on re-index | PASS | common=755 mismatches=0 |
| no duplicate chunks after re-index | PASS | total=2904 unique=2904 |
| deterministic chunk multiset on re-index | PASS | prev=2904 new=2904 |
| deterministic relationship multiset on re-index | PASS | prev=2463 new=2463 |
| deterministic call multiset on re-index | PASS | prev=6733 new=6733 |
| no duplicate relations after re-index | PASS | total=2463 unique=2463 |
| no cross-snapshot leakage after re-index | PASS | cross=0 |
| stable graph API output ordering | PASS | nodes=50 |

## Metrics

```json
{
  "repository_id": "07f7c912-8073-4bf2-bd38-2b046eb8ceb2",
  "snapshot_id": "6440e822-d927-45cf-82df-c8c7031f4fef",
  "commit_sha": "60af34b60ab2650a74af32c6ce340c5cfbceb3d8",
  "indexing_duration_seconds": 10.05,
  "files": {
    "total": 773,
    "skipped": 18,
    "binaries": 11,
    "distinct_hashes": 637
  },
  "files_by_lang_level": [
    {
      "support_level": "deep",
      "language": "python",
      "n": 635,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "documentation",
      "n": 83,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "configuration",
      "n": 26,
      "binaries": 0
    },
    {
      "support_level": "skip",
      "language": null,
      "n": 18,
      "binaries": 11
    },
    {
      "support_level": "generic",
      "language": "shell",
      "n": 6,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "css",
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
      "language": "html",
      "n": 1,
      "binaries": 0
    }
  ],
  "chunks": {
    "total": 2904,
    "verified_deep": 2161,
    "llm_enriched": 0,
    "unique_spans": 2904,
    "with_parser": 2904
  },
  "chunk_breakdown": [
    {
      "language": "python",
      "support_level": "deep",
      "extraction_method": "deep_symbol",
      "parser_name": "python-ast",
      "n": 2142
    },
    {
      "language": "documentation",
      "support_level": "generic",
      "extraction_method": "markdown_ast",
      "parser_name": "mistune-ast",
      "n": 564
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "yaml-compose",
      "n": 155
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "tomllib",
      "n": 23
    },
    {
      "language": "javascript",
      "support_level": "deep",
      "extraction_method": "deep_symbol",
      "parser_name": "javascript-treesitter",
      "n": 19
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "dockerfile-parse",
      "n": 1
    }
  ],
  "nodes_by_type": {
    "python:import": 2097,
    "python:function": 1687,
    "python:method": 353,
    "python:class": 102,
    "javascript:method": 13,
    "javascript:function": 5,
    "javascript:class": 1
  },
  "edges_by_kind": {
    "imports": 2097,
    "contains": 366
  },
  "edges_by_confidence": {
    "unresolved": 1236,
    "resolved": 1222,
    "ambiguous": 5
  },
  "call_totals": {
    "total": 6733,
    "resolved": 1082,
    "ambiguous": 377,
    "unresolved": 5274
  },
  "inheritance_counts": [],
  "symbol_totals": {
    "total": 4258,
    "fake_deep": 0
  },
  "language_mix": {
    "python": 635,
    "documentation": 83,
    "configuration": 26,
    "shell": 6,
    "css": 2,
    "javascript": 2,
    "html": 1
  }
}
```

## Exact search

```json
[
  {
    "query": "Typer",
    "total": 1076,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "docs/about/index.md",
        "start_line": 1,
        "end_line": 3,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "docs/alternatives.md",
        "start_line": 1,
        "end_line": 4,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "docs/alternatives.md",
        "start_line": 5,
        "end_line": 10,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "docs/alternatives.md",
        "start_line": 11,
        "end_line": 103,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "docs/contributing.md",
        "start_line": 1,
        "end_line": 4,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "command",
    "total": 528,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "docs/alternatives.md",
        "start_line": 11,
        "end_line": 103,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "docs/contributing.md",
        "start_line": 9,
        "end_line": 148,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "docs/environment-variables.md",
        "start_line": 162,
        "end_line": 289,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "docs/features.md",
        "start_line": 45,
        "end_line": 65,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "docs/index.md",
        "start_line": 1,
        "end_line": 47,
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
    "total": 603,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "docs/alternatives.md",
        "start_line": 11,
        "end_line": 103,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "docs/features.md",
        "start_line": 39,
        "end_line": 44,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "docs/features.md",
        "start_line": 45,
        "end_line": 65,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "docs/index.md",
        "start_line": 1,
        "end_line": 47,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "docs/index.md",
        "start_line": 79,
        "end_line": 124,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "callback",
    "total": 185,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "docs/features.md",
        "start_line": 39,
        "end_line": 44,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "docs/reference/context.md",
        "start_line": 1,
        "end_line": 39,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "docs/release-notes.md",
        "start_line": 538,
        "end_line": 541,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "docs/release-notes.md",
        "start_line": 787,
        "end_line": 842,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "docs/release-notes.md",
        "start_line": 1479,
        "end_line": 1496,
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
    "node_count": 500,
    "edge_count": 613,
    "graph_type": "modules",
    "snapshot_id": "6440e822-d927-45cf-82df-c8c7031f4fef",
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
        "id": "_click.exceptions",
        "label": "_click.exceptions",
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
        "id": "_click.termui",
        "label": "_click.termui",
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
        "id": "_click.utils",
        "label": "_click.utils",
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
        "id": "abc",
        "label": "abc",
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
        "source": "docs_src.app_dir.tutorial001_py310",
        "target": "pathlib",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "docs_src.arguments.default.tutorial002_an_py310",
        "target": "random",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "docs_src.arguments.default.tutorial002_py310",
        "target": "random",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "docs_src.launch.tutorial002_py310",
        "target": "pathlib",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "docs_src.multiple_values.arguments_with_multiple_values.tutorial001_py310",
        "target": "pathlib",
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
    "node_count": 122,
    "edge_count": 144,
    "graph_type": "packages",
    "snapshot_id": "6440e822-d927-45cf-82df-c8c7031f4fef",
    "filters": {
      "local_imports_only": true,
      "max_nodes": 500,
      "max_edges": 2000
    },
    "sample_nodes": [
      {
        "id": "docs.js",
        "label": "docs.js",
        "node_type": "package",
        "language": "javascript",
        "support_level": "deep",
        "path": null,
        "symbol_count": 19,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "docs_src",
        "label": "docs_src",
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
        "id": "docs_src.app_dir",
        "label": "docs_src.app_dir",
        "node_type": "package",
        "language": "python",
        "support_level": "deep",
        "path": null,
        "symbol_count": 1,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "docs_src.arguments",
        "label": "docs_src.arguments",
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
        "id": "docs_src.arguments.default",
        "label": "docs_src.arguments.default",
        "node_type": "package",
        "language": "python",
        "support_level": "deep",
        "path": null,
        "symbol_count": 6,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      }
    ],
    "sample_edges": [
      {
        "source": "docs_src.app_dir",
        "target": "typer",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": true,
        "line": null
      },
      {
        "source": "docs_src.arguments.default",
        "target": "typer",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "python",
        "weight": 4,
        "inferred": true,
        "line": null
      },
      {
        "source": "docs_src.arguments.envvar",
        "target": "typer",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "python",
        "weight": 6,
        "inferred": true,
        "line": null
      },
      {
        "source": "docs_src.arguments.help",
        "target": "typer",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "python",
        "weight": 16,
        "inferred": true,
        "line": null
      },
      {
        "source": "docs_src.arguments.optional",
        "target": "typer",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "python",
        "weight": 7,
        "inferred": true,
        "line": null
      }
    ]
  },
  "directories": {
    "node_count": 142,
    "edge_count": 289,
    "graph_type": "directories",
    "snapshot_id": "6440e822-d927-45cf-82df-c8c7031f4fef",
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
        "id": ".github",
        "label": ".github",
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
        "id": ".github/workflows",
        "label": ".github/workflows",
        "node_type": "directory",
        "language": null,
        "support_level": "generic",
        "path": null,
        "symbol_count": 0,
        "file_count": 18,
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
        "file_count": 9,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "docs/about",
        "label": "docs/about",
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
        "target": "docs_src",
        "relation_kind": "contains",
        "confidence": "resolved",
        "language": null,
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": ".",
        "target": "scripts",
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
  "calls_depth_1": {
    "center": "typer._click.utils.echo",
    "node_count": 65,
    "edge_count": 98,
    "depth": 1,
    "sample_edges": [
      {
        "source": "01286ca5-868d-4882-ad62-7294c198ea14",
        "target": "d916263c-d1b8-4539-a84f-5f6fc27bb822",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 7
      },
      {
        "source": "01286ca5-868d-4882-ad62-7294c198ea14",
        "target": "d916263c-d1b8-4539-a84f-5f6fc27bb822",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 8
      },
      {
        "source": "01286ca5-868d-4882-ad62-7294c198ea14",
        "target": "d916263c-d1b8-4539-a84f-5f6fc27bb822",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 9
      },
      {
        "source": "033e9948-beac-4b3a-8f86-a9672c89c50f",
        "target": "d916263c-d1b8-4539-a84f-5f6fc27bb822",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 74
      },
      {
        "source": "033e9948-beac-4b3a-8f86-a9672c89c50f",
        "target": "d916263c-d1b8-4539-a84f-5f6fc27bb822",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 75
      },
      {
        "source": "0540cd88-4c93-454d-8bd1-54d1b65e4b1b",
        "target": "d916263c-d1b8-4539-a84f-5f6fc27bb822",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 10
      },
      {
        "source": "108c45bd-f562-43a3-b1c9-b943ce7b676d",
        "target": "d916263c-d1b8-4539-a84f-5f6fc27bb822",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 17
      },
      {
        "source": "15e6a7d0-b9ec-4b1a-ba4a-42a516cb1fb7",
        "target": "d916263c-d1b8-4539-a84f-5f6fc27bb822",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 22
      }
    ]
  },
  "calls_depth_2": {
    "center": "typer._click.utils.echo",
    "node_count": 110,
    "edge_count": 275,
    "depth": 2,
    "sample_edges": [
      {
        "source": "01286ca5-868d-4882-ad62-7294c198ea14",
        "target": "8faaf4a4-4496-4683-8c39-5332dc950528",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 7
      },
      {
        "source": "01286ca5-868d-4882-ad62-7294c198ea14",
        "target": "8faaf4a4-4496-4683-8c39-5332dc950528",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 8
      },
      {
        "source": "01286ca5-868d-4882-ad62-7294c198ea14",
        "target": "8faaf4a4-4496-4683-8c39-5332dc950528",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 9
      },
      {
        "source": "01286ca5-868d-4882-ad62-7294c198ea14",
        "target": "d916263c-d1b8-4539-a84f-5f6fc27bb822",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 7
      },
      {
        "source": "01286ca5-868d-4882-ad62-7294c198ea14",
        "target": "d916263c-d1b8-4539-a84f-5f6fc27bb822",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 8
      },
      {
        "source": "01286ca5-868d-4882-ad62-7294c198ea14",
        "target": "d916263c-d1b8-4539-a84f-5f6fc27bb822",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 9
      },
      {
        "source": "033e9948-beac-4b3a-8f86-a9672c89c50f",
        "target": "6aeb8438-7337-4459-a1e4-7b6f79e4efe8",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 62
      },
      {
        "source": "033e9948-beac-4b3a-8f86-a9672c89c50f",
        "target": "8faaf4a4-4496-4683-8c39-5332dc950528",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 74
      }
    ]
  },
  "callers_api": {
    "total": 20,
    "sample": [
      {
        "id": "6dbdb430-d2a5-4921-b255-263f674915d2",
        "snapshot_id": "6440e822-d927-45cf-82df-c8c7031f4fef",
        "source_file_id": "8ad5ad2a-20bf-45ff-b9ec-d41fa1191892",
        "path": "tests/assets/completion_no_types.py",
        "caller_symbol_id": "01286ca5-868d-4882-ad62-7294c198ea14",
        "caller_qualified_name": "tests.assets.completion_no_types.complete",
        "raw_callee": "typer.echo",
        "qualified_expression": "typer.echo",
        "line": 7,
        "candidate_qualified_name": "typer._click.utils.echo",
        "confidence": "resolved",
        "language": "python",
        "created_at": "2026-07-20T02:23:37.744816Z"
      },
      {
        "id": "824c7ad9-58a1-43f3-a5bf-b94aaca0927a",
        "snapshot_id": "6440e822-d927-45cf-82df-c8c7031f4fef",
        "source_file_id": "68136db1-246f-408d-8965-8937d0589da1",
        "path": "tests/assets/completion_no_types_order.py",
        "caller_symbol_id": "5ad66e24-07f0-4103-a736-f6fadc62914d",
        "caller_qualified_name": "tests.assets.completion_no_types_order.complete",
        "raw_callee": "typer.echo",
        "qualified_expression": "typer.echo",
        "line": 7,
        "candidate_qualified_name": "typer._click.utils.echo",
        "confidence": "resolved",
        "language": "python",
        "created_at": "2026-07-20T02:23:37.744816Z"
      },
      {
        "id": "95f7061f-b976-4a76-a855-64d7a9ac4caf",
        "snapshot_id": "6440e822-d927-45cf-82df-c8c7031f4fef",
        "source_file_id": "63a78be4-9428-46c1-994b-30228d3daa34",
        "path": "tests/assets/cli/multi_app_cli.py",
        "caller_symbol_id": "e2498a7f-3f9d-4f36-ae3a-9c2fbd04f660",
        "caller_qualified_name": "tests.assets.cli.multi_app_cli.hello",
        "raw_callee": "typer.echo",
        "qualified_expression": "typer.echo",
        "line": 8,
        "candidate_qualified_name": "typer._click.utils.echo",
        "confidence": "resolved",
        "language": "python",
        "created_at": "2026-07-20T02:23:37.744816Z"
      },
      {
        "id": "9c62d7a8-bab9-4d00-ae59-16ab67886810",
        "snapshot_id": "6440e822-d927-45cf-82df-c8c7031f4fef",
        "source_file_id": "279d8497-1b7c-4714-a4ed-e550f103272e",
        "path": "tests/assets/cli/app_other_name.py",
        "caller_symbol_id": "456751d5-bb4e-4389-bcb4-81495463ae35",
        "caller_qualified_name": "tests.assets.cli.app_other_name.callback",
        "raw_callee": "typer.echo",
        "qualified_expression": "typer.echo",
        "line": 8,
        "candidate_qualified_name": "typer._click.utils.echo",
        "confidence": "resolved",
        "language": "python",
        "created_at": "2026-07-20T02:23:37.744816Z"
      },
      {
        "id": "cc37a00f-e22e-485d-aff0-44a03ba5f849",
        "snapshot_id": "6440e822-d927-45cf-82df-c8c7031f4fef",
        "source_file_id": "70c992f0-4973-4274-84f8-190a34897d11",
        "path": "tests/assets/completion_argument.py",
        "caller_symbol_id": "9277e335-44cb-4458-8269-0a6963330674",
        "caller_qualified_name": "tests.assets.completion_argument.shell_complete",
        "raw_callee": "typer.echo",
        "qualified_expression": "typer.echo",
        "line": 8,
        "candidate_qualified_name": "typer._click.utils.echo",
        "confidence": "resolved",
        "language": "python",
        "created_at": "2026-07-20T02:23:37.744816Z"
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
    "qn": "typer._click.utils.echo",
    "callers": 131
  },
  "multi_callee": {
    "qn": "tests.test_progress_bar.main",
    "callees": 68
  },
  "ambiguous_symbol": {
    "id": "2233213a-2760-4783-a552-9bc084e6943b",
    "qualified_name": "docs_src.arguments.default.tutorial001_an_py310.main",
    "language": "python",
    "kind": "function"
  },
  "unresolved_samples": [
    {
      "caller_qualified_name": "docs_src.app_dir.tutorial001_py310.main",
      "raw_callee": "app.command",
      "confidence": "unresolved",
      "line": 10,
      "language": "python"
    },
    {
      "caller_qualified_name": "docs_src.app_dir.tutorial001_py310.main",
      "raw_callee": "Path",
      "confidence": "unresolved",
      "line": 13,
      "language": "python"
    },
    {
      "caller_qualified_name": "docs_src.app_dir.tutorial001_py310.main",
      "raw_callee": "config_path.is_file",
      "confidence": "unresolved",
      "line": 14,
      "language": "python"
    },
    {
      "caller_qualified_name": "docs_src.app_dir.tutorial001_py310.main",
      "raw_callee": "print",
      "confidence": "unresolved",
      "line": 15,
      "language": "python"
    },
    {
      "caller_qualified_name": "docs_src.arguments.default.tutorial001_an_py310.main",
      "raw_callee": "app.command",
      "confidence": "unresolved",
      "line": 8,
      "language": "python"
    }
  ],
  "no_callers": [
    {
      "id": "a5179d87-4664-4332-ab84-efb040d6660f",
      "qualified_name": "docs_src.app_dir.tutorial001_py310.main",
      "kind": "function",
      "language": "python"
    },
    {
      "id": "2233213a-2760-4783-a552-9bc084e6943b",
      "qualified_name": "docs_src.arguments.default.tutorial001_an_py310.main",
      "kind": "function",
      "language": "python"
    },
    {
      "id": "8f6e8a0b-9b71-485f-a5ed-b6aac7fb6770",
      "qualified_name": "docs_src.arguments.default.tutorial001_py310.main",
      "kind": "function",
      "language": "python"
    }
  ],
  "multi_caller_symbol": {
    "id": "d916263c-d1b8-4539-a84f-5f6fc27bb822",
    "qualified_name": "typer._click.utils.echo",
    "kind": "import",
    "language": "python",
    "start_line": 24,
    "end_line": 24
  },
  "multi_callee_symbol": {
    "qualified_name": "tests.test_progress_bar.main"
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
  "modules_lang_python": {
    "node_count": 100,
    "edge_count": 0,
    "filters": {
      "language": "python",
      "local_imports_only": false,
      "max_nodes": 100,
      "max_edges": 200
    }
  },
  "inferred_false": {
    "node_count": 142,
    "edge_count": 141,
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
  "repository_id": "07f7c912-8073-4bf2-bd38-2b046eb8ceb2",
  "snapshot_id": "6440e822-d927-45cf-82df-c8c7031f4fef",
  "commit_sha": "60af34b60ab2650a74af32c6ce340c5cfbceb3d8",
  "status": "SUCCEEDED",
  "indexing_duration_seconds": 10.04,
  "files": {
    "total": 773,
    "skipped": 18,
    "binaries": 11,
    "distinct_hashes": 637
  },
  "chunks": {
    "total": 2904,
    "verified_deep": 2161,
    "llm_enriched": 0,
    "distinct_content_hashes": 2457,
    "unique_spans": 2904,
    "with_parser": 2904
  },
  "edges_by_kind": {
    "imports": 2097,
    "contains": 366
  },
  "call_totals": {
    "total": 6733,
    "resolved": 1082,
    "ambiguous": 377,
    "unresolved": 5274
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
