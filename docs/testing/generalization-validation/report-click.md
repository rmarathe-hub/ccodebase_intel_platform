# Generalization validation — Python CLI — pallets/click

- URL: https://github.com/pallets/click
- Generated: 2026-07-20T03:06:26.197507+00:00
- API: `http://127.0.0.1:8001`
- LLM enrichment: **OFF**
- Clone size limit: 52428800 bytes (unchanged)

## Checks

| Check | Result | Detail |
| --- | --- | --- |
| repository imported successfully | PASS | status=SUCCEEDED err=None:None |
| snapshot created | PASS | 06f73b11-f201-421e-a165-7f17599ac1a1 |
| files discovered | PASS | total=164 skipped=10 binaries=5 |
| chunks persisted | PASS | chunks=1694 unique_spans=1694 |
| no duplicate chunk spans | PASS | total=1694 unique=1694 |
| parser provenance stored | PASS | with_parser_name=1694 with_version=1694 |
| optional enrichment OFF | PASS | llm_enriched=0 |
| no fake verified symbols for non-deep langs | PASS | fake_deep=0 |
| deep analysis for expected languages | PASS | symbol_langs=['python'] verified_deep_chunks=1283 |
| deterministic repository summary | PASS | llm_summary_status=disabled |
| exact chunk search operational | PASS | Command→705; option→463; Context→350; click→842 |
| relation kinds only from unified model | PASS | kinds={'imports': 560, 'contains': 411} |
| no orphan from_symbol dangling IDs | PASS | orphans=0 |
| no orphan to_symbol dangling IDs | PASS | orphans=0 |
| no cross-snapshot relation leakage | PASS | cross=0 |
| no duplicate structural relation keys | PASS | total=971 unique=971 |
| IMPORTS/CONTAINS present for deep repo | PASS | edges={'imports': 560, 'contains': 411} |
| CALLS persisted with resolution labels | PASS | resolved=540 ambiguous=24 unresolved=5667 |
| modules graph returns | PASS | nodes=153 edges=384 |
| modules graph no host path leakage | PASS | leaked=0 |
| packages graph returns | PASS | nodes=18 edges=0 |
| packages graph no host path leakage | PASS | leaked=0 |
| directory graph usable | PASS | nodes=24 edges=23 |
| directories graph no host path leakage | PASS | leaked=0 |
| callers/callees neighborhood API | PASS | center=tests.test_shell_completion._get_words d1_nodes=25 |
| call edges carry confidence labels | PASS | confidences_seen=['resolved'] |
| ambiguous call symbols present | PASS | src.click.termui.prompt |
| unresolved/external calls present or documented | PASS | unresolved_samples=5 |
| symbol with no callers found | PASS | count=3 |
| callers/callees list endpoints | PASS | callers=20 callees=1 |
| invalid filter returns validation error | PASS | status=422 body={"detail":{"code":"invalid_support_level","message":"support_level must be deep, generic, mixed, or skip"}} |
| invalid confidence rejected | PASS | status=422 |
| graph node/edge limits applied | PASS | nodes=5 edges=4 |
| path_prefix filter accepted | PASS | nodes=2 |
| language filter on modules | PASS | requested=python seen=['python'] |
| inferred=false filter respected | PASS | inferred_remaining=0 total_edges=23 |
| React Flow page wired to live graph APIs | PASS | {"loads_from_api": true, "no_fixture_data_in_page": true, "has_relation_filters": true, "has_language_filter": true, "has_support_level_filter": true, "has_depth_control": true, "has_generic_honesty_notice": true, "has_inferred_edge_styling": true, "selection_detail_panel": true, "uses_xyflow": true} |
| generic honesty notice present in Graph UI | PASS | GraphPage honesty copy checked |
| no regex structural parsing in chunking package | PASS | offenders=[] |
| re-index succeeded | PASS | status=SUCCEEDED duration_s=10.1 |
| stable content hashes on re-index | PASS | common=154 mismatches=0 |
| no duplicate chunks after re-index | PASS | total=1694 unique=1694 |
| deterministic chunk multiset on re-index | PASS | prev=1694 new=1694 |
| deterministic relationship multiset on re-index | PASS | prev=971 new=971 |
| deterministic call multiset on re-index | PASS | prev=6231 new=6231 |
| no duplicate relations after re-index | PASS | total=971 unique=971 |
| no cross-snapshot leakage after re-index | PASS | cross=0 |
| stable graph API output ordering | PASS | nodes=24 |

## Metrics

```json
{
  "repository_id": "4fc27f23-574f-411f-a4ca-55e69d697b25",
  "snapshot_id": "06f73b11-f201-421e-a165-7f17599ac1a1",
  "commit_sha": "333c28d79cd982990ee98eef61ec20ab1a4f38ba",
  "indexing_duration_seconds": 5.07,
  "files": {
    "total": 164,
    "skipped": 10,
    "binaries": 5,
    "distinct_hashes": 152
  },
  "files_by_lang_level": [
    {
      "support_level": "deep",
      "language": "python",
      "n": 77,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "documentation",
      "n": 54,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "configuration",
      "n": 22,
      "binaries": 0
    },
    {
      "support_level": "skip",
      "language": null,
      "n": 10,
      "binaries": 5
    },
    {
      "support_level": "generic",
      "language": "shell",
      "n": 1,
      "binaries": 0
    }
  ],
  "chunks": {
    "total": 1694,
    "verified_deep": 1283,
    "llm_enriched": 0,
    "unique_spans": 1694,
    "with_parser": 1694,
    "with_parser_version": 1694
  },
  "chunk_breakdown": [
    {
      "language": "python",
      "support_level": "deep",
      "extraction_method": "deep_symbol",
      "parser_name": "python-ast",
      "n": 1283
    },
    {
      "language": "documentation",
      "support_level": "generic",
      "extraction_method": "markdown_ast",
      "parser_name": "mistune-ast",
      "n": 285
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "tomllib",
      "n": 68
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "yaml-compose",
      "n": 54
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "json-stdlib",
      "n": 4
    }
  ],
  "nodes_by_type": {
    "python:function": 761,
    "python:import": 560,
    "python:method": 411,
    "python:class": 111
  },
  "edges_by_kind": {
    "imports": 560,
    "contains": 411
  },
  "edges_by_confidence": {
    "unresolved": 461,
    "resolved": 510
  },
  "call_totals": {
    "total": 6231,
    "resolved": 540,
    "ambiguous": 24,
    "unresolved": 5667
  },
  "inheritance_counts": [],
  "symbol_totals": {
    "total": 1843,
    "fake_deep": 0
  },
  "language_mix": {
    "python": 77,
    "documentation": 54,
    "configuration": 22,
    "shell": 1
  }
}
```

## Exact search

```json
[
  {
    "query": "Command",
    "total": 705,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "CHANGES.md",
        "start_line": 1,
        "end_line": 46,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGES.md",
        "start_line": 47,
        "end_line": 75,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGES.md",
        "start_line": 90,
        "end_line": 205,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGES.md",
        "start_line": 206,
        "end_line": 245,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGES.md",
        "start_line": 339,
        "end_line": 464,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "option",
    "total": 463,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "CHANGES.md",
        "start_line": 1,
        "end_line": 46,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGES.md",
        "start_line": 47,
        "end_line": 75,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGES.md",
        "start_line": 76,
        "end_line": 89,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGES.md",
        "start_line": 90,
        "end_line": 205,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGES.md",
        "start_line": 206,
        "end_line": 245,
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
    "total": 350,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "CHANGES.md",
        "start_line": 90,
        "end_line": 205,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGES.md",
        "start_line": 263,
        "end_line": 279,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGES.md",
        "start_line": 280,
        "end_line": 309,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGES.md",
        "start_line": 339,
        "end_line": 464,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGES.md",
        "start_line": 465,
        "end_line": 493,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "click",
    "total": 842,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "CHANGES.md",
        "start_line": 1,
        "end_line": 46,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGES.md",
        "start_line": 90,
        "end_line": 205,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGES.md",
        "start_line": 280,
        "end_line": 309,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGES.md",
        "start_line": 310,
        "end_line": 328,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "CHANGES.md",
        "start_line": 339,
        "end_line": 464,
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
    "node_count": 153,
    "edge_count": 384,
    "graph_type": "modules",
    "snapshot_id": "06f73b11-f201-421e-a165-7f17599ac1a1",
    "filters": {
      "local_imports_only": false,
      "max_nodes": 500,
      "max_edges": 2000
    },
    "sample_nodes": [
      {
        "id": "PIL",
        "label": "PIL",
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
      },
      {
        "id": "click",
        "label": "click",
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
        "id": "click._compat",
        "label": "click._compat",
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
        "target": "pallets_sphinx_themes",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "python",
        "weight": 2,
        "inferred": false,
        "line": null
      },
      {
        "source": "examples.aliases.aliases",
        "target": "click",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "examples.aliases.aliases",
        "target": "configparser",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "examples.aliases.aliases",
        "target": "os",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "examples.colors.colors",
        "target": "click",
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
    "node_count": 18,
    "edge_count": 0,
    "graph_type": "packages",
    "snapshot_id": "06f73b11-f201-421e-a165-7f17599ac1a1",
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
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "examples.aliases",
        "label": "examples.aliases",
        "node_type": "package",
        "language": "python",
        "support_level": "deep",
        "path": null,
        "symbol_count": 16,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "examples.colors",
        "label": "examples.colors",
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
        "id": "examples.completion",
        "label": "examples.completion",
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
        "id": "examples.complex",
        "label": "examples.complex",
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
    "sample_edges": []
  },
  "directories": {
    "node_count": 24,
    "edge_count": 23,
    "graph_type": "directories",
    "snapshot_id": "06f73b11-f201-421e-a165-7f17599ac1a1",
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
        "file_count": 6,
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
    "center": "tests.test_shell_completion._get_words",
    "node_count": 25,
    "edge_count": 70,
    "depth": 1,
    "sample_edges": [
      {
        "source": "14be59f5-4808-4f54-ad2d-5f1de1d79ab0",
        "target": "c9580d15-184f-4995-9cd7-640ec1139320",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 83
      },
      {
        "source": "14be59f5-4808-4f54-ad2d-5f1de1d79ab0",
        "target": "c9580d15-184f-4995-9cd7-640ec1139320",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 84
      },
      {
        "source": "14be59f5-4808-4f54-ad2d-5f1de1d79ab0",
        "target": "c9580d15-184f-4995-9cd7-640ec1139320",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 85
      },
      {
        "source": "14be59f5-4808-4f54-ad2d-5f1de1d79ab0",
        "target": "c9580d15-184f-4995-9cd7-640ec1139320",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 86
      },
      {
        "source": "23ef9950-f35b-4a41-94ba-8725568416f6",
        "target": "c9580d15-184f-4995-9cd7-640ec1139320",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 222
      },
      {
        "source": "23ef9950-f35b-4a41-94ba-8725568416f6",
        "target": "c9580d15-184f-4995-9cd7-640ec1139320",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 224
      },
      {
        "source": "34c16e9a-02d4-4a85-aa60-9fd9961d6c74",
        "target": "c9580d15-184f-4995-9cd7-640ec1139320",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 302
      },
      {
        "source": "34c16e9a-02d4-4a85-aa60-9fd9961d6c74",
        "target": "c9580d15-184f-4995-9cd7-640ec1139320",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 303
      }
    ]
  },
  "calls_depth_2": {
    "center": "tests.test_shell_completion._get_words",
    "node_count": 34,
    "edge_count": 162,
    "depth": 2,
    "sample_edges": [
      {
        "source": "07b2b9d1-b314-4a63-9a1b-f3949fadc13f",
        "target": "409b78f5-9704-4e36-a9a0-eb744c471c42",
        "relation_kind": "calls",
        "confidence": "unresolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 25
      },
      {
        "source": "14be59f5-4808-4f54-ad2d-5f1de1d79ab0",
        "target": "4971bf90-8b3a-4997-994e-2141772d8aae",
        "relation_kind": "calls",
        "confidence": "unresolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 81
      },
      {
        "source": "14be59f5-4808-4f54-ad2d-5f1de1d79ab0",
        "target": "af8f44c6-c42c-45ab-bcb2-31ec3ec373d8",
        "relation_kind": "calls",
        "confidence": "unresolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 81
      },
      {
        "source": "14be59f5-4808-4f54-ad2d-5f1de1d79ab0",
        "target": "b70515c0-5a3e-45d8-95ee-51d0d528523e",
        "relation_kind": "calls",
        "confidence": "unresolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 80
      },
      {
        "source": "14be59f5-4808-4f54-ad2d-5f1de1d79ab0",
        "target": "c9580d15-184f-4995-9cd7-640ec1139320",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 83
      },
      {
        "source": "14be59f5-4808-4f54-ad2d-5f1de1d79ab0",
        "target": "c9580d15-184f-4995-9cd7-640ec1139320",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 84
      },
      {
        "source": "14be59f5-4808-4f54-ad2d-5f1de1d79ab0",
        "target": "c9580d15-184f-4995-9cd7-640ec1139320",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 85
      },
      {
        "source": "14be59f5-4808-4f54-ad2d-5f1de1d79ab0",
        "target": "c9580d15-184f-4995-9cd7-640ec1139320",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "python",
        "weight": 1,
        "inferred": false,
        "line": 86
      }
    ]
  },
  "callers_api": {
    "total": 20,
    "sample": [
      {
        "id": "bc7a8c8b-a117-425b-a7c7-531bbe01116d",
        "snapshot_id": "06f73b11-f201-421e-a165-7f17599ac1a1",
        "source_file_id": "f919a787-66b8-4cf6-b4cf-0d7e0ab9102e",
        "path": "tests/test_shell_completion.py",
        "caller_symbol_id": "5e4200d1-c149-4b2e-b404-b498b4909262",
        "caller_qualified_name": "tests.test_shell_completion.test_command",
        "raw_callee": "_get_words",
        "qualified_expression": "_get_words",
        "line": 35,
        "candidate_qualified_name": "tests.test_shell_completion._get_words",
        "confidence": "resolved",
        "language": "python",
        "created_at": "2026-07-20T03:05:14.302675Z"
      },
      {
        "id": "32dd82a1-1f8d-4588-abd9-92d2258609f2",
        "snapshot_id": "06f73b11-f201-421e-a165-7f17599ac1a1",
        "source_file_id": "f919a787-66b8-4cf6-b4cf-0d7e0ab9102e",
        "path": "tests/test_shell_completion.py",
        "caller_symbol_id": "5e4200d1-c149-4b2e-b404-b498b4909262",
        "caller_qualified_name": "tests.test_shell_completion.test_command",
        "raw_callee": "_get_words",
        "qualified_expression": "_get_words",
        "line": 36,
        "candidate_qualified_name": "tests.test_shell_completion._get_words",
        "confidence": "resolved",
        "language": "python",
        "created_at": "2026-07-20T03:05:14.302675Z"
      },
      {
        "id": "405bd00b-b0a0-40de-8efc-904d6b8d8c43",
        "snapshot_id": "06f73b11-f201-421e-a165-7f17599ac1a1",
        "source_file_id": "f919a787-66b8-4cf6-b4cf-0d7e0ab9102e",
        "path": "tests/test_shell_completion.py",
        "caller_symbol_id": "5e4200d1-c149-4b2e-b404-b498b4909262",
        "caller_qualified_name": "tests.test_shell_completion.test_command",
        "raw_callee": "_get_words",
        "qualified_expression": "_get_words",
        "line": 37,
        "candidate_qualified_name": "tests.test_shell_completion._get_words",
        "confidence": "resolved",
        "language": "python",
        "created_at": "2026-07-20T03:05:14.302675Z"
      },
      {
        "id": "a44750f4-64d3-49b4-b948-7770127383eb",
        "snapshot_id": "06f73b11-f201-421e-a165-7f17599ac1a1",
        "source_file_id": "f919a787-66b8-4cf6-b4cf-0d7e0ab9102e",
        "path": "tests/test_shell_completion.py",
        "caller_symbol_id": "5e4200d1-c149-4b2e-b404-b498b4909262",
        "caller_qualified_name": "tests.test_shell_completion.test_command",
        "raw_callee": "_get_words",
        "qualified_expression": "_get_words",
        "line": 38,
        "candidate_qualified_name": "tests.test_shell_completion._get_words",
        "confidence": "resolved",
        "language": "python",
        "created_at": "2026-07-20T03:05:14.302675Z"
      },
      {
        "id": "c70b9b26-6116-475d-924b-7bfaf6893f0b",
        "snapshot_id": "06f73b11-f201-421e-a165-7f17599ac1a1",
        "source_file_id": "f919a787-66b8-4cf6-b4cf-0d7e0ab9102e",
        "path": "tests/test_shell_completion.py",
        "caller_symbol_id": "5e4200d1-c149-4b2e-b404-b498b4909262",
        "caller_qualified_name": "tests.test_shell_completion.test_command",
        "raw_callee": "_get_words",
        "qualified_expression": "_get_words",
        "line": 40,
        "candidate_qualified_name": "tests.test_shell_completion._get_words",
        "confidence": "resolved",
        "language": "python",
        "created_at": "2026-07-20T03:05:14.302675Z"
      }
    ]
  },
  "callees_api": {
    "total": 1,
    "sample": [
      {
        "id": "369e383a-98e3-487f-869b-9ebcb936fe86",
        "snapshot_id": "06f73b11-f201-421e-a165-7f17599ac1a1",
        "source_file_id": "f919a787-66b8-4cf6-b4cf-0d7e0ab9102e",
        "path": "tests/test_shell_completion.py",
        "caller_symbol_id": "c9580d15-184f-4995-9cd7-640ec1139320",
        "caller_qualified_name": "tests.test_shell_completion._get_words",
        "raw_callee": "_get_completions",
        "qualified_expression": "_get_completions",
        "line": 30,
        "candidate_qualified_name": "tests.test_shell_completion._get_completions",
        "confidence": "resolved",
        "language": "python",
        "created_at": "2026-07-20T03:05:14.302675Z"
      }
    ]
  }
}
```

## Callers / callees samples

```json
{
  "multi_caller": {
    "qn": "tests.test_shell_completion._get_words",
    "callers": 69
  },
  "multi_callee": {
    "qn": "tests.test_options.cli",
    "callees": 119
  },
  "ambiguous_symbol": {
    "id": "6c367be2-f60d-4985-acbc-b4f7b0b21e40",
    "qualified_name": "src.click.termui.prompt",
    "language": "python",
    "kind": "import"
  },
  "unresolved_samples": [
    {
      "caller_qualified_name": "examples.aliases.aliases.Config.__init__",
      "raw_callee": "os.getcwd",
      "confidence": "unresolved",
      "line": 11,
      "language": "python"
    },
    {
      "caller_qualified_name": "examples.aliases.aliases.Config.add_alias",
      "raw_callee": "self.aliases.update",
      "confidence": "unresolved",
      "line": 15,
      "language": "python"
    },
    {
      "caller_qualified_name": "examples.aliases.aliases.Config.read_config",
      "raw_callee": "configparser.RawConfigParser",
      "confidence": "unresolved",
      "line": 18,
      "language": "python"
    },
    {
      "caller_qualified_name": "examples.aliases.aliases.Config.read_config",
      "raw_callee": "parser.read",
      "confidence": "unresolved",
      "line": 19,
      "language": "python"
    },
    {
      "caller_qualified_name": "examples.aliases.aliases.Config.read_config",
      "raw_callee": "parser.items",
      "confidence": "unresolved",
      "line": 21,
      "language": "python"
    }
  ],
  "no_callers": [
    {
      "id": "e9482580-a9f2-4e89-b10d-75f99461372b",
      "qualified_name": "examples.aliases.aliases.Config.__init__",
      "kind": "method",
      "language": "python"
    },
    {
      "id": "bbd2a8e0-3e46-415e-b7d7-e0851f1ef67a",
      "qualified_name": "examples.aliases.aliases.Config.add_alias",
      "kind": "method",
      "language": "python"
    },
    {
      "id": "4be62c88-c0bb-4c0f-a996-2f30b05804cb",
      "qualified_name": "examples.aliases.aliases.Config.read_config",
      "kind": "method",
      "language": "python"
    }
  ],
  "multi_caller_symbol": {
    "id": "c9580d15-184f-4995-9cd7-640ec1139320",
    "qualified_name": "tests.test_shell_completion._get_words",
    "kind": "function",
    "language": "python",
    "start_line": 29,
    "end_line": 30
  },
  "multi_callee_symbol": {
    "qualified_name": "tests.test_options.cli"
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
    "node_count": 2,
    "edge_count": 1
  },
  "modules_lang_python": {
    "node_count": 100,
    "edge_count": 192,
    "filters": {
      "language": "python",
      "local_imports_only": false,
      "max_nodes": 100,
      "max_edges": 200
    }
  },
  "inferred_false": {
    "node_count": 24,
    "edge_count": 23,
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
  "repository_id": "4fc27f23-574f-411f-a4ca-55e69d697b25",
  "snapshot_id": "06f73b11-f201-421e-a165-7f17599ac1a1",
  "commit_sha": "333c28d79cd982990ee98eef61ec20ab1a4f38ba",
  "status": "SUCCEEDED",
  "indexing_duration_seconds": 10.06,
  "files": {
    "total": 164,
    "skipped": 10,
    "binaries": 5,
    "distinct_hashes": 152
  },
  "chunks": {
    "total": 1694,
    "verified_deep": 1283,
    "llm_enriched": 0,
    "distinct_content_hashes": 1674,
    "unique_spans": 1694,
    "with_parser": 1694,
    "with_parser_version": 1694
  },
  "edges_by_kind": {
    "imports": 560,
    "contains": 411
  },
  "call_totals": {
    "total": 6231,
    "resolved": 540,
    "ambiguous": 24,
    "unresolved": 5667
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
