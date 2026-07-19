# Performance Smoke Report — Week 0–4

Performance checks use **generous** CI/laptop budgets (`@pytest.mark.slow`). They are smoke gates, not microbenchmarks.

## Suites

| Test module | What it measures |
| --- | --- |
| `test_performance_smoke.py` | Classification / URL throughput smoke |
| `test_discovery_perf.py` | Large tiny-file trees, ignore pruning, retail_shape wall clock |

## Guidance

```bash
cd /Users/rohitmarathe/codebase_intel_platform
./scripts/testing/run-slow.sh
```

## Frontend build

`npm run build` in `apps/web` completed successfully in this session (~sub-second Vite build after typecheck).

## Notes

- Do not tighten thresholds without multi-machine calibration.
- Full retail fixture network clone is optional (`@integration` / cache) and not required for CI.
- Offline `retail_shape` indexing via worker mocked-clone path is covered functionally, not as a hard latency SLA.
