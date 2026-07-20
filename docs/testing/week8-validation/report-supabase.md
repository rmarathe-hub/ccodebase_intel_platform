# Week 8 validation — Mixed monorepo — supabase/supabase

- URL: https://github.com/supabase/supabase
- Generated: 2026-07-20T02:37:31.656414+00:00
- API: `http://127.0.0.1:8001`
- LLM enrichment: **OFF**
- Clone size limit: 52428800 bytes (unchanged)

## Checks

| Check | Result | Detail |
| --- | --- | --- |
| oversized monorepo rejected by existing clone/safety limits | PASS | status=FAILED clone_timeout:git clone --depth 1 --single-branch --no-recurse-submodules -- https://github.com/supabase/supabase.git [clone-dir-redacted] timed out github_size_kb≈2412903 limit_bytes=52428800 timeout_s=120 |
| safety limits not weakened | PASS | git_clone_max_bytes remains 52428800 |
| no regex structural parsing in chunking package | PASS | offenders=[] |
| re-index skipped (clone limit) | PASS | oversized repo never indexed; re-index N/A |

## Metrics

```json
{
  "indexing_duration_seconds": 0.0,
  "job": {
    "status": "FAILED",
    "error_code": "clone_timeout",
    "error_message": "git clone --depth 1 --single-branch --no-recurse-submodules -- https://github.com/supabase/supabase.git [clone-dir-redacted] timed out",
    "stage": "cloning"
  },
  "note": "Supabase (~2.4M KB GitHub size) exceeds the 50 MiB clone cap. Import failed under unchanged safety limits \u2014 expected stress outcome."
}
```

## Exact search

```json
[]
```

## Graphs

```json
{}
```

## Callers / callees samples

```json
{}
```

## Inheritance / implementations

```json
{}
```

## API filters

```json
{}
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
  "uses_xyflow": true
}
```

## Re-index

```json
{
  "skipped": true,
  "reason": "clone_limit"
}
```

## Failures and limitations

- None

## Recommendation before Week 9

- Keep clone/discovery caps; consider optional sparse/subtree import in a later week if mixed-monorepo graph demos are required without raising global limits.
