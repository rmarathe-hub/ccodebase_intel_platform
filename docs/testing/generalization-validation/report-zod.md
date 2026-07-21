# Generalization validation — TypeScript — colinhacks/zod

- URL: https://github.com/colinhacks/zod
- Generated: 2026-07-20T03:06:58.853012+00:00
- API: `http://127.0.0.1:8001`
- LLM enrichment: **OFF**
- Clone size limit: 52428800 bytes (unchanged)

## Checks

| Check | Result | Detail |
| --- | --- | --- |
| repository imported successfully | PASS | status=SUCCEEDED err=None:None |
| snapshot created | PASS | f84568ba-aa72-4e8b-92e3-4d0cbfbc2541 |
| files discovered | PASS | total=580 skipped=110 binaries=61 |
| chunks persisted | PASS | chunks=2373 unique_spans=2373 |
| no duplicate chunk spans | PASS | total=2373 unique=2373 |
| parser provenance stored | PASS | with_parser_name=2373 with_version=2373 |
| optional enrichment OFF | PASS | llm_enriched=0 |
| no fake verified symbols for non-deep langs | PASS | fake_deep=0 |
| deep analysis for expected languages | PASS | symbol_langs=['javascript', 'typescript'] verified_deep_chunks=1900 |
| deterministic repository summary | PASS | llm_summary_status=disabled |
| exact chunk search operational | PASS | ZodSchema→8; parse→402; object→271; string→839 |
| relation kinds only from unified model | PASS | kinds={'imports': 1280, 'contains': 280, 'exports': 267} |
| no orphan from_symbol dangling IDs | PASS | orphans=0 |
| no orphan to_symbol dangling IDs | PASS | orphans=0 |
| no cross-snapshot relation leakage | PASS | cross=0 |
| no duplicate structural relation keys | PASS | total=1827 unique=1827 |
| IMPORTS/CONTAINS present for deep repo | PASS | edges={'imports': 1280, 'contains': 280, 'exports': 267} |
| CALLS persisted with resolution labels | PASS | resolved=447 ambiguous=8 unresolved=2192 |
| modules graph returns | PASS | nodes=491 edges=914 |
| modules graph no host path leakage | PASS | leaked=0 |
| packages graph returns | PASS | nodes=212 edges=90 |
| packages graph no host path leakage | PASS | leaked=0 |
| directory graph usable | PASS | nodes=59 edges=88 |
| directories graph no host path leakage | PASS | leaked=0 |
| callers/callees neighborhood API | PASS | center=packages.zod.src.v4.classic.from-json-schema.convertBaseSchema d1_nodes=3 |
| call edges carry confidence labels | PASS | confidences_seen=['resolved'] |
| ambiguous call symbols present | PASS | packages.zod.src.v4.classic.compat.setErrorMap |
| unresolved/external calls present or documented | PASS | unresolved_samples=5 |
| symbol with no callers found | PASS | count=3 |
| callers/callees list endpoints | PASS | callers=2 callees=20 |
| invalid filter returns validation error | PASS | status=422 body={"detail":{"code":"invalid_support_level","message":"support_level must be deep, generic, mixed, or skip"}} |
| invalid confidence rejected | PASS | status=422 |
| graph node/edge limits applied | PASS | nodes=5 edges=4 |
| path_prefix filter accepted | PASS | nodes=0 |
| language filter on modules | PASS | requested=typescript seen=['typescript'] |
| inferred=false filter respected | PASS | inferred_remaining=0 total_edges=58 |
| React Flow page wired to live graph APIs | PASS | {"loads_from_api": true, "no_fixture_data_in_page": true, "has_relation_filters": true, "has_language_filter": true, "has_support_level_filter": true, "has_depth_control": true, "has_generic_honesty_notice": true, "has_inferred_edge_styling": true, "selection_detail_panel": true, "uses_xyflow": true} |
| generic honesty notice present in Graph UI | PASS | GraphPage honesty copy checked |
| no regex structural parsing in chunking package | PASS | offenders=[] |
| re-index succeeded | PASS | status=SUCCEEDED duration_s=15.0 |
| stable content hashes on re-index | PASS | common=470 mismatches=0 |
| no duplicate chunks after re-index | PASS | total=2373 unique=2373 |
| deterministic chunk multiset on re-index | PASS | prev=2373 new=2373 |
| deterministic relationship multiset on re-index | PASS | prev=1827 new=1827 |
| deterministic call multiset on re-index | PASS | prev=2647 new=2647 |
| no duplicate relations after re-index | PASS | total=1827 unique=1827 |
| no cross-snapshot leakage after re-index | PASS | cross=0 |
| stable graph API output ordering | PASS | nodes=50 |

## Metrics

```json
{
  "repository_id": "608d359f-8a79-4b9f-aa92-31fd9c6a6fe4",
  "snapshot_id": "f84568ba-aa72-4e8b-92e3-4d0cbfbc2541",
  "commit_sha": "912f0f51b0ced654d0069741e7160834dca742ee",
  "indexing_duration_seconds": 10.06,
  "files": {
    "total": 580,
    "skipped": 110,
    "binaries": 61,
    "distinct_hashes": 464
  },
  "files_by_lang_level": [
    {
      "support_level": "deep",
      "language": "typescript",
      "n": 394,
      "binaries": 0
    },
    {
      "support_level": "skip",
      "language": null,
      "n": 110,
      "binaries": 61
    },
    {
      "support_level": "generic",
      "language": "configuration",
      "n": 43,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "documentation",
      "n": 23,
      "binaries": 0
    },
    {
      "support_level": "deep",
      "language": "javascript",
      "n": 5,
      "binaries": 0
    },
    {
      "support_level": "generic",
      "language": "html",
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
    "total": 2373,
    "verified_deep": 1900,
    "llm_enriched": 0,
    "unique_spans": 2373,
    "with_parser": 2373,
    "with_parser_version": 2373
  },
  "chunk_breakdown": [
    {
      "language": "typescript",
      "support_level": "deep",
      "extraction_method": "deep_symbol",
      "parser_name": "typescript-treesitter",
      "n": 1848
    },
    {
      "language": "documentation",
      "support_level": "generic",
      "extraction_method": "markdown_ast",
      "parser_name": "mistune-ast",
      "n": 284
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "json-stdlib",
      "n": 126
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "yaml-compose",
      "n": 62
    },
    {
      "language": "typescript",
      "support_level": "deep",
      "extraction_method": "deep_symbol",
      "parser_name": "tsx-treesitter",
      "n": 51
    },
    {
      "language": "configuration",
      "support_level": "generic",
      "extraction_method": "format_native",
      "parser_name": "defusedxml-sax",
      "n": 1
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
    "typescript:import": 1266,
    "typescript:type_alias": 785,
    "typescript:function": 598,
    "typescript:method": 280,
    "typescript:export": 267,
    "typescript:interface": 169,
    "typescript:class": 67,
    "javascript:import": 14,
    "javascript:function": 1
  },
  "edges_by_kind": {
    "imports": 1280,
    "contains": 280,
    "exports": 267
  },
  "edges_by_confidence": {
    "resolved": 1018,
    "unresolved": 412,
    "ambiguous": 397
  },
  "call_totals": {
    "total": 2647,
    "resolved": 447,
    "ambiguous": 8,
    "unresolved": 2192
  },
  "inheritance_counts": [],
  "symbol_totals": {
    "total": 3447,
    "fake_deep": 0
  },
  "language_mix": {
    "typescript": 394,
    "configuration": 43,
    "documentation": 23,
    "javascript": 5,
    "html": 2,
    "css": 2,
    "shell": 1
  }
}
```

## Exact search

```json
[
  {
    "query": "ZodSchema",
    "total": 8,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "packages/docs-v3/CHANGELOG.md",
        "start_line": 184,
        "end_line": 188,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "packages/docs-v3/README_ZH.md",
        "start_line": 1271,
        "end_line": 1325,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "packages/docs-v3/README_ZH.md",
        "start_line": 1326,
        "end_line": 1342,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "packages/tsc/generate.ts",
        "start_line": 327,
        "end_line": 355,
        "language": "typescript",
        "support_level": "deep",
        "verified_deep": true
      },
      {
        "path": "packages/zod/src/v4/classic/from-json-schema.ts",
        "start_line": 146,
        "end_line": 531,
        "language": "typescript",
        "support_level": "deep",
        "verified_deep": true
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "parse",
    "total": 402,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": ".github/workflows/release.yml",
        "start_line": 13,
        "end_line": 167,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": ".github/workflows/release.yml",
        "start_line": 63,
        "end_line": 167,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "packages/docs/app/llms-full.txt/route.ts",
        "start_line": 8,
        "end_line": 44,
        "language": "typescript",
        "support_level": "deep",
        "verified_deep": true
      },
      {
        "path": "packages/docs/pnpm-lock.yaml",
        "start_line": 58,
        "end_line": 1836,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "packages/docs/pnpm-lock.yaml",
        "start_line": 1836,
        "end_line": 3906,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "object",
    "total": 271,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "AGENTS.md",
        "start_line": 97,
        "end_line": 118,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "package.json",
        "start_line": 67,
        "end_line": 91,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "packages/bench/benchUtil.ts",
        "start_line": 27,
        "end_line": 34,
        "language": "typescript",
        "support_level": "deep",
        "verified_deep": true
      },
      {
        "path": "packages/bench/discriminated-union.ts",
        "start_line": 53,
        "end_line": 97,
        "language": "typescript",
        "support_level": "deep",
        "verified_deep": true
      },
      {
        "path": "packages/bench/instanceof.ts",
        "start_line": 23,
        "end_line": 23,
        "language": "typescript",
        "support_level": "deep",
        "verified_deep": true
      }
    ],
    "citation_ok": true,
    "notes": []
  },
  {
    "query": "string",
    "total": 839,
    "search_mode": "exact",
    "top_hits": [
      {
        "path": "AGENTS.md",
        "start_line": 5,
        "end_line": 23,
        "language": "documentation",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": ".github/workflows/pullfrog.yml",
        "start_line": 4,
        "end_line": 14,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": ".github/workflows/pullfrog.yml",
        "start_line": 5,
        "end_line": 14,
        "language": "configuration",
        "support_level": "generic",
        "verified_deep": false
      },
      {
        "path": "packages/bench/benchUtil.ts",
        "start_line": 14,
        "end_line": 21,
        "language": "typescript",
        "support_level": "deep",
        "verified_deep": true
      },
      {
        "path": "packages/bench/benchUtil.ts",
        "start_line": 36,
        "end_line": 65,
        "language": "typescript",
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
    "node_count": 491,
    "edge_count": 914,
    "graph_type": "modules",
    "snapshot_id": "f84568ba-aa72-4e8b-92e3-4d0cbfbc2541",
    "filters": {
      "local_imports_only": false,
      "max_nodes": 500,
      "max_edges": 2000
    },
    "sample_nodes": [
      {
        "id": ".configs.rollup.config",
        "label": ".configs.rollup.config",
        "node_type": "module",
        "language": "javascript",
        "support_level": "deep",
        "path": ".configs/rollup.config.js",
        "symbol_count": 0,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "@/.source",
        "label": "@/.source",
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
        "id": "@/app/(doc)/layout",
        "label": "@/app/(doc)/layout",
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
        "id": "@/app/layout.config",
        "label": "@/app/layout.config",
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
        "id": "@/components/copy-markdown-button",
        "label": "@/components/copy-markdown-button",
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
        "source": ".configs.rollup.config",
        "target": "@rollup/plugin-commonjs",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": ".configs.rollup.config",
        "target": "@rollup/plugin-node-resolve",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": ".configs.rollup.config",
        "target": "@rollup/plugin-typescript",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": ".configs.rollup.config",
        "target": "rollup-plugin-filesize",
        "relation_kind": "imports",
        "confidence": "unresolved",
        "language": "javascript",
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": "packages.bench",
        "target": "execa",
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
    "node_count": 212,
    "edge_count": 90,
    "graph_type": "packages",
    "snapshot_id": "f84568ba-aa72-4e8b-92e3-4d0cbfbc2541",
    "filters": {
      "local_imports_only": true,
      "max_nodes": 500,
      "max_edges": 2000
    },
    "sample_nodes": [
      {
        "id": ".configs.rollup",
        "label": ".configs.rollup",
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
        "id": "packages",
        "label": "packages",
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
        "id": "packages.bench",
        "label": "packages.bench",
        "node_type": "package",
        "language": "typescript",
        "support_level": "deep",
        "path": null,
        "symbol_count": 43,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      },
      {
        "id": "packages.docs.app",
        "label": "packages.docs.app",
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
        "id": "packages.docs.app.(doc)",
        "label": "packages.docs.app.(doc)",
        "node_type": "package",
        "language": "typescript",
        "support_level": "deep",
        "path": null,
        "symbol_count": 1,
        "file_count": 0,
        "symbol_id": null,
        "kind": null
      }
    ],
    "sample_edges": [
      {
        "source": "packages.bench",
        "target": "packages.zod",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "typescript",
        "weight": 1,
        "inferred": true,
        "line": null
      },
      {
        "source": "packages.docs.vitest",
        "target": "vitest",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "typescript",
        "weight": 3,
        "inferred": true,
        "line": null
      },
      {
        "source": "packages.resolution.vitest",
        "target": "vitest",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "typescript",
        "weight": 3,
        "inferred": true,
        "line": null
      },
      {
        "source": "packages.tsc.bench",
        "target": "packages.tsc",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "typescript",
        "weight": 3,
        "inferred": true,
        "line": null
      },
      {
        "source": "packages.zod",
        "target": "packages.zod.src.v4.classic",
        "relation_kind": "imports",
        "confidence": "resolved",
        "language": "typescript",
        "weight": 1,
        "inferred": true,
        "line": null
      }
    ]
  },
  "directories": {
    "node_count": 59,
    "edge_count": 88,
    "graph_type": "directories",
    "snapshot_id": "f84568ba-aa72-4e8b-92e3-4d0cbfbc2541",
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
        "id": ".configs",
        "label": ".configs",
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
        "file_count": 6,
        "symbol_id": null,
        "kind": null
      }
    ],
    "sample_edges": [
      {
        "source": ".",
        "target": ".configs",
        "relation_kind": "contains",
        "confidence": "resolved",
        "language": null,
        "weight": 1,
        "inferred": false,
        "line": null
      },
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
        "target": "packages",
        "relation_kind": "contains",
        "confidence": "resolved",
        "language": null,
        "weight": 1,
        "inferred": false,
        "line": null
      },
      {
        "source": ".",
        "target": "rfcs",
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
    "center": "packages.zod.src.v4.classic.from-json-schema.convertBaseSchema",
    "node_count": 3,
    "edge_count": 14,
    "depth": 1,
    "sample_edges": [
      {
        "source": "49c290f9-ada9-4c75-bc33-155c1df3e101",
        "target": "49c290f9-ada9-4c75-bc33-155c1df3e101",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "typescript",
        "weight": 1,
        "inferred": false,
        "line": 241
      },
      {
        "source": "49c290f9-ada9-4c75-bc33-155c1df3e101",
        "target": "ad77802f-e6c8-4c1a-850e-3e14c4bf45f9",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "typescript",
        "weight": 1,
        "inferred": false,
        "line": 186
      },
      {
        "source": "49c290f9-ada9-4c75-bc33-155c1df3e101",
        "target": "c443b01f-e85a-46d9-973e-50fdd82153b2",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "typescript",
        "weight": 1,
        "inferred": false,
        "line": 187
      },
      {
        "source": "49c290f9-ada9-4c75-bc33-155c1df3e101",
        "target": "c443b01f-e85a-46d9-973e-50fdd82153b2",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "typescript",
        "weight": 1,
        "inferred": false,
        "line": 380
      },
      {
        "source": "49c290f9-ada9-4c75-bc33-155c1df3e101",
        "target": "c443b01f-e85a-46d9-973e-50fdd82153b2",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "typescript",
        "weight": 1,
        "inferred": false,
        "line": 387
      },
      {
        "source": "49c290f9-ada9-4c75-bc33-155c1df3e101",
        "target": "c443b01f-e85a-46d9-973e-50fdd82153b2",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "typescript",
        "weight": 1,
        "inferred": false,
        "line": 390
      },
      {
        "source": "49c290f9-ada9-4c75-bc33-155c1df3e101",
        "target": "c443b01f-e85a-46d9-973e-50fdd82153b2",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "typescript",
        "weight": 1,
        "inferred": false,
        "line": 415
      },
      {
        "source": "49c290f9-ada9-4c75-bc33-155c1df3e101",
        "target": "c443b01f-e85a-46d9-973e-50fdd82153b2",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "typescript",
        "weight": 1,
        "inferred": false,
        "line": 452
      }
    ]
  },
  "calls_depth_2": {
    "center": "packages.zod.src.v4.classic.from-json-schema.convertBaseSchema",
    "node_count": 4,
    "edge_count": 19,
    "depth": 2,
    "sample_edges": [
      {
        "source": "49c290f9-ada9-4c75-bc33-155c1df3e101",
        "target": "49c290f9-ada9-4c75-bc33-155c1df3e101",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "typescript",
        "weight": 1,
        "inferred": false,
        "line": 241
      },
      {
        "source": "49c290f9-ada9-4c75-bc33-155c1df3e101",
        "target": "ad77802f-e6c8-4c1a-850e-3e14c4bf45f9",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "typescript",
        "weight": 1,
        "inferred": false,
        "line": 186
      },
      {
        "source": "49c290f9-ada9-4c75-bc33-155c1df3e101",
        "target": "c443b01f-e85a-46d9-973e-50fdd82153b2",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "typescript",
        "weight": 1,
        "inferred": false,
        "line": 187
      },
      {
        "source": "49c290f9-ada9-4c75-bc33-155c1df3e101",
        "target": "c443b01f-e85a-46d9-973e-50fdd82153b2",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "typescript",
        "weight": 1,
        "inferred": false,
        "line": 380
      },
      {
        "source": "49c290f9-ada9-4c75-bc33-155c1df3e101",
        "target": "c443b01f-e85a-46d9-973e-50fdd82153b2",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "typescript",
        "weight": 1,
        "inferred": false,
        "line": 387
      },
      {
        "source": "49c290f9-ada9-4c75-bc33-155c1df3e101",
        "target": "c443b01f-e85a-46d9-973e-50fdd82153b2",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "typescript",
        "weight": 1,
        "inferred": false,
        "line": 390
      },
      {
        "source": "49c290f9-ada9-4c75-bc33-155c1df3e101",
        "target": "c443b01f-e85a-46d9-973e-50fdd82153b2",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "typescript",
        "weight": 1,
        "inferred": false,
        "line": 415
      },
      {
        "source": "49c290f9-ada9-4c75-bc33-155c1df3e101",
        "target": "c443b01f-e85a-46d9-973e-50fdd82153b2",
        "relation_kind": "calls",
        "confidence": "resolved",
        "language": "typescript",
        "weight": 1,
        "inferred": false,
        "line": 452
      }
    ]
  },
  "callers_api": {
    "total": 2,
    "sample": [
      {
        "id": "f03e4757-8392-4233-981d-7d0a9733cca6",
        "snapshot_id": "f84568ba-aa72-4e8b-92e3-4d0cbfbc2541",
        "source_file_id": "b02c73b1-e348-4cf1-bcc4-df362d0217e4",
        "path": "packages/zod/src/v4/classic/from-json-schema.ts",
        "caller_symbol_id": "49c290f9-ada9-4c75-bc33-155c1df3e101",
        "caller_qualified_name": "packages.zod.src.v4.classic.from-json-schema.convertBaseSchema",
        "raw_callee": "convertBaseSchema",
        "qualified_expression": "convertBaseSchema",
        "line": 241,
        "candidate_qualified_name": "packages.zod.src.v4.classic.from-json-schema.convertBaseSchema",
        "confidence": "resolved",
        "language": "typescript",
        "created_at": "2026-07-20T03:05:31.299916Z"
      },
      {
        "id": "aaf71598-6927-4589-a8c9-b2827cc2297b",
        "snapshot_id": "f84568ba-aa72-4e8b-92e3-4d0cbfbc2541",
        "source_file_id": "b02c73b1-e348-4cf1-bcc4-df362d0217e4",
        "path": "packages/zod/src/v4/classic/from-json-schema.ts",
        "caller_symbol_id": "c443b01f-e85a-46d9-973e-50fdd82153b2",
        "caller_qualified_name": "packages.zod.src.v4.classic.from-json-schema.convertSchema",
        "raw_callee": "convertBaseSchema",
        "qualified_expression": "convertBaseSchema",
        "line": 539,
        "candidate_qualified_name": "packages.zod.src.v4.classic.from-json-schema.convertBaseSchema",
        "confidence": "resolved",
        "language": "typescript",
        "created_at": "2026-07-20T03:05:31.299916Z"
      }
    ]
  },
  "callees_api": {
    "total": 20,
    "sample": [
      {
        "id": "a6941d60-7b92-44f1-adb9-79bc8f9ffade",
        "snapshot_id": "f84568ba-aa72-4e8b-92e3-4d0cbfbc2541",
        "source_file_id": "b02c73b1-e348-4cf1-bcc4-df362d0217e4",
        "path": "packages/zod/src/v4/classic/from-json-schema.ts",
        "caller_symbol_id": "49c290f9-ada9-4c75-bc33-155c1df3e101",
        "caller_qualified_name": "packages.zod.src.v4.classic.from-json-schema.convertBaseSchema",
        "raw_callee": "Object.keys",
        "qualified_expression": "Object.keys",
        "line": 150,
        "candidate_qualified_name": null,
        "confidence": "unresolved",
        "language": "typescript",
        "created_at": "2026-07-20T03:05:31.299916Z"
      },
      {
        "id": "7a1e372e-58f9-4214-a725-0de46647e635",
        "snapshot_id": "f84568ba-aa72-4e8b-92e3-4d0cbfbc2541",
        "source_file_id": "b02c73b1-e348-4cf1-bcc4-df362d0217e4",
        "path": "packages/zod/src/v4/classic/from-json-schema.ts",
        "caller_symbol_id": "49c290f9-ada9-4c75-bc33-155c1df3e101",
        "caller_qualified_name": "packages.zod.src.v4.classic.from-json-schema.convertBaseSchema",
        "raw_callee": "z.never",
        "qualified_expression": "z.never",
        "line": 151,
        "candidate_qualified_name": "zod.z.never",
        "confidence": "unresolved",
        "language": "typescript",
        "created_at": "2026-07-20T03:05:31.299916Z"
      },
      {
        "id": "90a15609-ead3-4213-b758-f457f9e952d6",
        "snapshot_id": "f84568ba-aa72-4e8b-92e3-4d0cbfbc2541",
        "source_file_id": "b02c73b1-e348-4cf1-bcc4-df362d0217e4",
        "path": "packages/zod/src/v4/classic/from-json-schema.ts",
        "caller_symbol_id": "49c290f9-ada9-4c75-bc33-155c1df3e101",
        "caller_qualified_name": "packages.zod.src.v4.classic.from-json-schema.convertBaseSchema",
        "raw_callee": "ctx.refs.has",
        "qualified_expression": "ctx.refs.has",
        "line": 171,
        "candidate_qualified_name": null,
        "confidence": "unresolved",
        "language": "typescript",
        "created_at": "2026-07-20T03:05:31.299916Z"
      },
      {
        "id": "78eec0e7-8216-4667-802b-f30771453d13",
        "snapshot_id": "f84568ba-aa72-4e8b-92e3-4d0cbfbc2541",
        "source_file_id": "b02c73b1-e348-4cf1-bcc4-df362d0217e4",
        "path": "packages/zod/src/v4/classic/from-json-schema.ts",
        "caller_symbol_id": "49c290f9-ada9-4c75-bc33-155c1df3e101",
        "caller_qualified_name": "packages.zod.src.v4.classic.from-json-schema.convertBaseSchema",
        "raw_callee": "ctx.refs.get",
        "qualified_expression": "ctx.refs.get",
        "line": 172,
        "candidate_qualified_name": null,
        "confidence": "unresolved",
        "language": "typescript",
        "created_at": "2026-07-20T03:05:31.299916Z"
      },
      {
        "id": "e504fabf-ba2f-4622-9f4e-73910c233d05",
        "snapshot_id": "f84568ba-aa72-4e8b-92e3-4d0cbfbc2541",
        "source_file_id": "b02c73b1-e348-4cf1-bcc4-df362d0217e4",
        "path": "packages/zod/src/v4/classic/from-json-schema.ts",
        "caller_symbol_id": "49c290f9-ada9-4c75-bc33-155c1df3e101",
        "caller_qualified_name": "packages.zod.src.v4.classic.from-json-schema.convertBaseSchema",
        "raw_callee": "ctx.processing.has",
        "qualified_expression": "ctx.processing.has",
        "line": 175,
        "candidate_qualified_name": null,
        "confidence": "unresolved",
        "language": "typescript",
        "created_at": "2026-07-20T03:05:31.299916Z"
      }
    ]
  }
}
```

## Callers / callees samples

```json
{
  "multi_caller": {
    "qn": "packages.zod.src.v3.helpers.parseUtil.addIssueToContext",
    "callers": 74
  },
  "multi_callee": {
    "qn": "packages.zod.src.v4.classic.from-json-schema.convertBaseSchema",
    "callees": 146
  },
  "ambiguous_symbol": {
    "id": "9e762a74-df57-4849-9857-5e9280607354",
    "qualified_name": "packages.zod.src.v4.classic.compat.setErrorMap",
    "language": "typescript",
    "kind": "function"
  },
  "unresolved_samples": [
    {
      "caller_qualified_name": "packages.docs.app.llms-full.txt.route.GET",
      "raw_callee": "join",
      "confidence": "unresolved",
      "line": 12,
      "language": "typescript"
    },
    {
      "caller_qualified_name": "packages.zod.src.v3.types.ZodUnion.handleResults",
      "raw_callee": "results.map",
      "confidence": "unresolved",
      "line": 2969,
      "language": "typescript"
    },
    {
      "caller_qualified_name": "packages.bench.benchUtil.makeSchema",
      "raw_callee": "factory",
      "confidence": "unresolved",
      "line": 8,
      "language": "typescript"
    },
    {
      "caller_qualified_name": "packages.bench.benchUtil.makeSchema",
      "raw_callee": "factory",
      "confidence": "unresolved",
      "line": 9,
      "language": "typescript"
    },
    {
      "caller_qualified_name": "packages.bench.benchUtil.randomString",
      "raw_callee": "Math.floor",
      "confidence": "unresolved",
      "line": 18,
      "language": "typescript"
    }
  ],
  "no_callers": [
    {
      "id": "c698f3d8-d145-44bc-9b9c-d087a140b80f",
      "qualified_name": "packages.zod.src.v3.tests.primitive.test.f",
      "kind": "function",
      "language": "typescript"
    },
    {
      "id": "7fe4b1e6-ea9e-4381-963a-14fcc1e961ae",
      "qualified_name": "packages.zod.src.v3.tests.primitive.test.f",
      "kind": "function",
      "language": "typescript"
    },
    {
      "id": "87035ad2-7e08-40d0-8dbf-c091a7d20b50",
      "qualified_name": "packages.zod.src.v3.tests.primitive.test.f",
      "kind": "function",
      "language": "typescript"
    }
  ],
  "multi_caller_symbol": {
    "id": "c89866df-1d63-490b-a719-2bf10cad1081",
    "qualified_name": "packages.zod.src.v3.helpers.parseUtil.addIssueToContext",
    "kind": "function",
    "language": "typescript",
    "start_line": 72,
    "end_line": 86
  },
  "multi_callee_symbol": {
    "id": "49c290f9-ada9-4c75-bc33-155c1df3e101",
    "qualified_name": "packages.zod.src.v4.classic.from-json-schema.convertBaseSchema",
    "kind": "function",
    "language": "typescript",
    "start_line": 146,
    "end_line": 531
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
    "node_count": 100,
    "edge_count": 78,
    "filters": {
      "language": "typescript",
      "local_imports_only": false,
      "max_nodes": 100,
      "max_edges": 200
    }
  },
  "inferred_false": {
    "node_count": 59,
    "edge_count": 58,
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
  "repository_id": "608d359f-8a79-4b9f-aa92-31fd9c6a6fe4",
  "snapshot_id": "f84568ba-aa72-4e8b-92e3-4d0cbfbc2541",
  "commit_sha": "912f0f51b0ced654d0069741e7160834dca742ee",
  "status": "SUCCEEDED",
  "indexing_duration_seconds": 15.05,
  "files": {
    "total": 580,
    "skipped": 110,
    "binaries": 61,
    "distinct_hashes": 464
  },
  "chunks": {
    "total": 2373,
    "verified_deep": 1900,
    "llm_enriched": 0,
    "distinct_content_hashes": 2074,
    "unique_spans": 2373,
    "with_parser": 2373,
    "with_parser_version": 2373
  },
  "edges_by_kind": {
    "imports": 1280,
    "contains": 280,
    "exports": 267
  },
  "call_totals": {
    "total": 2647,
    "resolved": 447,
    "ambiguous": 8,
    "unresolved": 2192
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
