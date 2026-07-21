#!/usr/bin/env python3
"""Week 11 Day 7 — optional live API dry-run helper.

Prefer the CI-safe pytest:

  cd apps/api && .venv/bin/pytest tests/test_week11_day7_e2e.py -q

This script exercises a *live* API + worker against a public URL when you want
a manual demo check. It does not mock clone.

Usage:
  python docs/testing/week11-e2e-dry-run/run_dry_run.py [API_BASE] [REPO_URL]
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

API = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8001"
REPO_URL = (
    sys.argv[2]
    if len(sys.argv) > 2
    else "https://github.com/rmarathe-hub/retail-retention-revenue-intel"
)
OUT = Path(__file__).resolve().parent
POLL_S = 3
TIMEOUT_S = 30 * 60


def _req(method: str, path: str, body: dict[str, Any] | None = None) -> Any:
    data = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request(
        f"{API}{path}",
        data=data,
        method=method,
        headers={"Content-Type": "application/json"} if body is not None else {},
    )
    with urllib.request.urlopen(request, timeout=120) as resp:
        raw = resp.read().decode()
        return json.loads(raw) if raw else None


def main() -> int:
    checks: list[tuple[str, bool, str]] = []
    print(f"API={API}")
    print(f"REPO={REPO_URL}")

    try:
        health = _req("GET", "/health")
        checks.append(("health", health.get("status") == "ok", str(health)))
    except urllib.error.URLError as exc:
        print(f"API unreachable: {exc}", file=sys.stderr)
        return 2

    imported = _req("POST", "/api/v1/repositories/import", {"url": REPO_URL})
    repo_id = imported["repository"]["id"]
    job_id = imported["job"]["id"]
    checks.append(("import", True, f"repo={repo_id} job={job_id}"))

    deadline = time.time() + TIMEOUT_S
    job: dict[str, Any] = {}
    while time.time() < deadline:
        job = _req("GET", f"/api/v1/jobs/{job_id}")
        status = job.get("status")
        print(f"  job {status} stage={job.get('stage')} {job.get('progress_percentage')}%")
        if status in {"SUCCEEDED", "FAILED", "CANCELLED"}:
            break
        time.sleep(POLL_S)

    ready = job.get("status") == "SUCCEEDED"
    checks.append(("ready", ready, f"status={job.get('status')} info={job.get('error_code')}"))
    if not ready:
        _write(checks)
        return 1

    search = _req(
        "GET",
        f"/api/v1/repositories/{repo_id}/chunks/search?"
        + urllib.parse.urlencode({"q": "def", "search_mode": "exact", "limit": 10}),
    )
    checks.append(("search", search.get("total", 0) >= 0, f"total={search.get('total')}"))

    ask = _req(
        "POST",
        f"/api/v1/repositories/{repo_id}/ask",
        {"question": "what is the main entry point?", "apply_rerank": True, "expand": True},
    )
    checks.append(
        (
            "ask",
            ask.get("status") in {"ok", "partial", "no_evidence"},
            f"status={ask.get('status')} cites={len(ask.get('citations') or [])}",
        )
    )

    graph = _req(
        "GET",
        f"/api/v1/repositories/{repo_id}/graph/modules?"
        + urllib.parse.urlencode({"max_nodes": 40, "max_edges": 80}),
    )
    checks.append(
        (
            "graph",
            graph.get("node_count", 0) >= 0,
            f"nodes={graph.get('node_count')} edges={graph.get('edge_count')}",
        )
    )

    path = _write(checks)
    print(f"Wrote {path}")
    return 0 if all(ok for _, ok, _ in checks) else 1


def _write(checks: list[tuple[str, bool, str]]) -> Path:
    passed = sum(1 for _, ok, _ in checks if ok)
    lines = [
        "# Week 11 Day 7 — live API dry run",
        "",
        f"- Generated: {datetime.now(UTC).isoformat()}",
        f"- API: `{API}`",
        f"- Repo: `{REPO_URL}`",
        f"- Verdict: **{'PASS' if passed == len(checks) else 'FAIL'}** ({passed}/{len(checks)})",
        "",
        "| Step | Pass | Detail |",
        "| --- | --- | --- |",
    ]
    for name, ok, detail in checks:
        lines.append(f"| {name} | {'yes' if ok else 'NO'} | {detail} |")
    lines.append("")
    out = OUT / "REPORT.live.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


if __name__ == "__main__":
    raise SystemExit(main())
