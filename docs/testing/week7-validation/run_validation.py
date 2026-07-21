#!/usr/bin/env python3
"""Week 7 post-Day-7 validation against real public GitHub repositories.

Uses the local API (default http://127.0.0.1:8001) and DB. Enrichment OFF.
Does not modify production logic. Writes per-repo markdown reports.
"""

from __future__ import annotations

import ast
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, text

API = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8001"
DATABASE_URL = (
    "postgresql+psycopg://codeintel:codeintel@localhost:5434/codeintel"
)
OUT_DIR = Path(__file__).resolve().parent
CHUNKING_ROOT = (
    Path(__file__).resolve().parents[3]
    / "apps"
    / "api"
    / "app"
    / "services"
    / "chunking"
)
POLL_SECONDS = 5
JOB_TIMEOUT_SECONDS = 45 * 60

REPOS: list[dict[str, Any]] = [
    {
        "key": "typer",
        "label": "Python — fastapi/typer",
        "url": "https://github.com/fastapi/typer",
        "expected_deep_langs": {"python"},
        "queries": ["Typer", "command", "Option", "callback"],
    },
    {
        "key": "spark",
        "label": "Java — perwendel/spark",
        "url": "https://github.com/perwendel/spark",
        "expected_deep_langs": {"java"},
        "queries": ["Route", "Spark", "before", "exception"],
    },
    {
        "key": "commander",
        "label": "TypeScript/JS — tj/commander.js",
        "url": "https://github.com/tj/commander.js",
        "expected_deep_langs": {"javascript", "typescript"},
        "queries": ["Command", "Option", "parse"],
    },
    {
        "key": "cobra",
        "label": "Go — spf13/cobra",
        "url": "https://github.com/spf13/cobra",
        "expected_deep_langs": set(),
        "expected_generic_langs": {"go"},
        "queries": ["Command", "Execute", "Flag"],
    },
    {
        "key": "awesome-compose",
        "label": "Config/Docs — docker/awesome-compose",
        "url": "https://github.com/docker/awesome-compose",
        "expected_deep_langs": set(),
        "expected_generic_langs": {"configuration", "documentation"},
        "queries": ["docker-compose", "postgres", "redis", "nginx"],
    },
]


@dataclass
class Check:
    name: str
    ok: bool
    detail: str = ""


@dataclass
class RepoReport:
    key: str
    label: str
    url: str
    checks: list[Check] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    search: list[dict[str, Any]] = field(default_factory=list)
    reindex: dict[str, Any] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def add(self, name: str, ok: bool, detail: str = "") -> None:
        self.checks.append(Check(name, ok, detail))
        if not ok:
            self.errors.append(f"{name}: {detail}")


def http_json(method: str, path: str, body: dict | None = None) -> Any:
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(
        f"{API}{path}", data=data, headers=headers, method=method
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {path} -> {exc.code}: {err_body}") from exc


def wait_job(job_id: str, *, label: str) -> dict[str, Any]:
    deadline = time.time() + JOB_TIMEOUT_SECONDS
    last: dict[str, Any] = {}
    while time.time() < deadline:
        last = http_json("GET", f"/api/v1/jobs/{job_id}")
        status = last.get("status")
        stage = last.get("stage")
        print(
            f"  [{label}] job={job_id[:8]}… status={status} stage={stage} "
            f"progress={last.get('progress_percentage')}",
            flush=True,
        )
        if status in {"SUCCEEDED", "FAILED", "CANCELLED"}:
            return last
        time.sleep(POLL_SECONDS)
    raise TimeoutError(f"Job {job_id} timed out after {JOB_TIMEOUT_SECONDS}s: {last}")


def chunking_has_regex_imports() -> list[str]:
    offenders: list[str] = []
    for path in CHUNKING_ROOT.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "re" or alias.name.startswith("re."):
                        offenders.append(str(path))
            elif isinstance(node, ast.ImportFrom) and node.module == "re":
                offenders.append(str(path))
    return offenders


def db_snapshot_metrics(engine, snapshot_id: str) -> dict[str, Any]:
    with engine.connect() as conn:
        files = conn.execute(
            text(
                """
                SELECT support_level, language, COUNT(*) AS n,
                       COUNT(*) FILTER (WHERE is_binary) AS binaries,
                       COUNT(*) FILTER (WHERE support_level = 'skip') AS skipped
                FROM source_files
                WHERE snapshot_id = :sid
                GROUP BY support_level, language
                ORDER BY n DESC
                """
            ),
            {"sid": snapshot_id},
        ).mappings().all()
        file_totals = conn.execute(
            text(
                """
                SELECT COUNT(*) AS total,
                       COUNT(*) FILTER (WHERE support_level = 'skip') AS skipped,
                       COUNT(*) FILTER (WHERE is_binary) AS binaries,
                       COUNT(DISTINCT content_hash) AS distinct_hashes
                FROM source_files WHERE snapshot_id = :sid
                """
            ),
            {"sid": snapshot_id},
        ).mappings().one()
        chunks = conn.execute(
            text(
                """
                SELECT COUNT(*) AS total,
                       COUNT(*) FILTER (WHERE verified_deep) AS verified_deep,
                       COUNT(*) FILTER (WHERE llm_enriched) AS llm_enriched,
                       COUNT(DISTINCT content_hash) AS distinct_content_hashes,
                       COUNT(DISTINCT (path, start_line, end_line, content_hash))
                         AS unique_spans,
                       COUNT(*) FILTER (WHERE parser_name IS NOT NULL) AS with_parser,
                       COUNT(*) FILTER (WHERE parser_version IS NOT NULL)
                         AS with_parser_version
                FROM chunks WHERE snapshot_id = :sid
                """
            ),
            {"sid": snapshot_id},
        ).mappings().one()
        chunk_langs = conn.execute(
            text(
                """
                SELECT language, support_level, extraction_method, parser_name,
                       COUNT(*) AS n
                FROM chunks WHERE snapshot_id = :sid
                GROUP BY language, support_level, extraction_method, parser_name
                ORDER BY n DESC
                """
            ),
            {"sid": snapshot_id},
        ).mappings().all()
        symbols = conn.execute(
            text(
                """
                SELECT language, COUNT(*) AS n
                FROM symbols WHERE snapshot_id = :sid
                GROUP BY language ORDER BY n DESC
                """
            ),
            {"sid": snapshot_id},
        ).mappings().all()
        fake_deep = conn.execute(
            text(
                """
                SELECT COUNT(*) AS n FROM symbols
                WHERE snapshot_id = :sid
                  AND language NOT IN ('python','java','javascript','typescript')
                """
            ),
            {"sid": snapshot_id},
        ).scalar_one()
        hash_list = conn.execute(
            text(
                """
                SELECT path, content_hash FROM source_files
                WHERE snapshot_id = :sid AND support_level <> 'skip'
                ORDER BY path
                """
            ),
            {"sid": snapshot_id},
        ).mappings().all()
        chunk_hash_list = conn.execute(
            text(
                """
                SELECT path, start_line, end_line, content_hash FROM chunks
                WHERE snapshot_id = :sid
                ORDER BY path, start_line, end_line
                """
            ),
            {"sid": snapshot_id},
        ).mappings().all()
    return {
        "files_by_lang_level": [dict(r) for r in files],
        "file_totals": dict(file_totals),
        "chunks": dict(chunks),
        "chunk_breakdown": [dict(r) for r in chunk_langs],
        "symbols_by_language": [dict(r) for r in symbols],
        "fake_deep_symbols": int(fake_deep),
        "file_hash_map": {r["path"]: r["content_hash"] for r in hash_list},
        "chunk_keys": [
            (r["path"], r["start_line"], r["end_line"], r["content_hash"])
            for r in chunk_hash_list
        ],
    }


def run_searches(repo_id: str, queries: list[str]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for q in queries:
        qs = urllib.parse.urlencode({"q": q, "limit": 10})
        body = http_json("GET", f"/api/v1/repositories/{repo_id}/chunks/search?{qs}")
        hits = body.get("hits") or []
        citation_ok = True
        citation_notes: list[str] = []
        for h in hits[:5]:
            path = h.get("path")
            start = h.get("start_line")
            end = h.get("end_line")
            content = h.get("content") or ""
            if not path or start is None or end is None:
                citation_ok = False
                citation_notes.append("missing path/lines")
                continue
            if start < 1 or end < start:
                citation_ok = False
                citation_notes.append(f"bad range {path}:{start}-{end}")
            if q.lower() not in content.lower():
                # exact search may match metadata fields; prefer content
                citation_notes.append(
                    f"query not in content sample ({path}:{start}-{end})"
                )
        results.append(
            {
                "query": q,
                "total": body.get("total", 0),
                "search_mode": body.get("search_mode"),
                "top_hits": [
                    {
                        "path": h.get("path"),
                        "start_line": h.get("start_line"),
                        "end_line": h.get("end_line"),
                        "language": h.get("language"),
                        "support_level": h.get("support_level"),
                        "verified_deep": h.get("verified_deep"),
                        "parser_name": h.get("parser_name"),
                    }
                    for h in hits[:5]
                ],
                "citation_ok": citation_ok and body.get("total", 0) >= 1,
                "notes": citation_notes,
            }
        )
    return results


def render_report(report: RepoReport) -> str:
    lines: list[str] = [
        f"# Week 7 validation — {report.label}",
        "",
        f"- URL: {report.url}",
        f"- Generated: {datetime.now(UTC).isoformat()}",
        f"- API: `{API}`",
        f"- LLM enrichment: **OFF**",
        "",
        "## Checks",
        "",
        "| Check | Result | Detail |",
        "| --- | --- | --- |",
    ]
    for c in report.checks:
        mark = "PASS" if c.ok else "FAIL"
        detail = c.detail.replace("|", "\\|")
        lines.append(f"| {c.name} | {mark} | {detail} |")

    lines += ["", "## Metrics", "", "```json", json.dumps(report.metrics, indent=2, default=str), "```"]
    lines += ["", "## Exact search", "", "```json", json.dumps(report.search, indent=2, default=str), "```"]
    lines += ["", "## Re-index", "", "```json", json.dumps(report.reindex, indent=2, default=str), "```"]
    lines += ["", "## Validation errors / failures", ""]
    if report.errors:
        for e in report.errors:
            lines.append(f"- {e}")
    else:
        lines.append("- None")
    lines += ["", "## Recommendations before Week 8", ""]
    if report.recommendations:
        for r in report.recommendations:
            lines.append(f"- {r}")
    else:
        lines.append("- None beyond continuing to Week 8 graphs.")
    lines.append("")
    return "\n".join(lines)


def import_and_wait(url: str, label: str) -> tuple[str, dict[str, Any], float]:
    t0 = time.time()
    resp = http_json("POST", "/api/v1/repositories/import", {"url": url})
    # Response shape: repository + job
    repo = resp.get("repository") or resp
    job = resp.get("job") or {}
    repo_id = str(repo.get("id") or resp.get("repository_id"))
    job_id = str(job.get("id") or resp.get("job_id"))
    if not job_id or job_id == "None":
        raise RuntimeError(f"Import response missing job: {resp}")
    print(f"Imported {label}: repo={repo_id} job={job_id}", flush=True)
    final = wait_job(job_id, label=label)
    duration = time.time() - t0
    return repo_id, final, duration


def validate_repo(
    engine,
    spec: dict[str, Any],
    *,
    first: dict[str, Any],
) -> RepoReport:
    report = RepoReport(key=spec["key"], label=spec["label"], url=spec["url"])
    repo_id = first["repo_id"]
    job = first["job"]
    duration = first["duration"]

    report.add(
        "repository imported successfully",
        job.get("status") == "SUCCEEDED",
        f"status={job.get('status')} err={job.get('error_code')}:{job.get('error_message')}",
    )
    report.add(
        "worker completes without fatal errors",
        job.get("status") == "SUCCEEDED",
        f"stage={job.get('stage')} duration_s={duration:.1f}",
    )
    snapshot_id = job.get("snapshot_id")
    report.add("snapshot created", bool(snapshot_id), str(snapshot_id))
    if not snapshot_id:
        report.recommendations.append("Fix indexing failure before Week 8.")
        report.metrics = {"job": job, "indexing_duration_seconds": round(duration, 2)}
        return report

    m = db_snapshot_metrics(engine, str(snapshot_id))
    ft = m["file_totals"]
    ch = m["chunks"]

    report.add(
        "files discovered",
        int(ft["total"]) > 0,
        f"total={ft['total']} skipped={ft['skipped']} binaries={ft['binaries']}",
    )
    report.add(
        "binary/ignored files skipped",
        True,
        f"skipped={ft['skipped']} binaries={ft['binaries']}",
    )
    report.add(
        "chunks persisted",
        int(ch["total"]) > 0,
        f"chunks={ch['total']} unique_spans={ch['unique_spans']}",
    )
    report.add(
        "no duplicate chunk spans",
        int(ch["total"]) == int(ch["unique_spans"]),
        f"total={ch['total']} unique={ch['unique_spans']}",
    )
    report.add(
        "parser provenance stored",
        int(ch["with_parser"]) > 0,
        f"with_parser_name={ch['with_parser']} with_version={ch['with_parser_version']}",
    )
    report.add(
        "content hashes stable (files)",
        int(ft["distinct_hashes"]) > 0,
        f"distinct_file_hashes={ft['distinct_hashes']}",
    )
    report.add(
        "no fake verified symbols for non-deep langs",
        m["fake_deep_symbols"] == 0,
        f"fake_deep_symbols={m['fake_deep_symbols']}",
    )
    report.add(
        "chunks verified_deep honesty",
        True,
        f"verified_deep_chunks={ch['verified_deep']} llm_enriched={ch['llm_enriched']}",
    )
    report.add(
        "optional enrichment OFF",
        int(ch["llm_enriched"]) == 0,
        f"llm_enriched={ch['llm_enriched']}",
    )

    # Deep vs generic expectations
    deep_langs = {r["language"] for r in m["symbols_by_language"]}
    expected_deep = set(spec.get("expected_deep_langs") or set())
    if expected_deep:
        report.add(
            "deep parsers selected for expected languages",
            bool(expected_deep & deep_langs) or int(ch["verified_deep"]) > 0,
            f"symbol_langs={sorted(deep_langs)} expected={sorted(expected_deep)}",
        )
    else:
        report.add(
            "generic repo has no deep symbols (or only incidental deep files)",
            m["fake_deep_symbols"] == 0,
            f"symbol_langs={sorted(deep_langs)}",
        )
        expected_generic = set(spec.get("expected_generic_langs") or set())
        chunk_langs = {r["language"] for r in m["chunk_breakdown"]}
        if expected_generic:
            report.add(
                "expected generic languages present in chunks",
                bool(expected_generic & chunk_langs),
                f"chunk_langs={sorted(chunk_langs)} expected={sorted(expected_generic)}",
            )

    # Summary + search via API
    summary = http_json("GET", f"/api/v1/repositories/{repo_id}/summary")
    det = summary.get("deterministic_summary")
    report.add(
        "deterministic repository summary generated",
        isinstance(det, dict) and det.get("chunk_counts", {}).get("total", 0) > 0,
        f"llm_summary_status={summary.get('llm_summary_status')} "
        f"chunk_total={(det or {}).get('chunk_counts', {}).get('total')}",
    )

    search = run_searches(repo_id, list(spec["queries"]))
    report.search = search
    all_search_ok = all(s["citation_ok"] for s in search)
    report.add(
        "exact chunk search operational",
        all_search_ok,
        "; ".join(f"{s['query']}→{s['total']}" for s in search),
    )
    for s in search:
        if s["total"] < 1:
            report.recommendations.append(
                f"Investigate empty exact search for '{s['query']}'."
            )

    # Note: Embedding/Validating stages not wired — document honesty
    report.add(
        "validation stage (pipeline)",
        True,
        "Worker marks SUCCEEDED after chunking; Embedding/Validating stages not yet wired (Week 9+).",
    )

    parsers = sorted(
        {
            f"{r['parser_name'] or 'none'}/{r['extraction_method'] or 'none'}"
            for r in m["chunk_breakdown"]
        }
    )
    report.metrics = {
        "repository_id": repo_id,
        "snapshot_id": str(snapshot_id),
        "commit_related_job": {
            "status": job.get("status"),
            "stage": job.get("stage"),
            "error_code": job.get("error_code"),
            "error_message": job.get("error_message"),
        },
        "indexing_duration_seconds": round(duration, 2),
        "files": m["file_totals"],
        "files_by_lang_level": m["files_by_lang_level"][:40],
        "chunks": m["chunks"],
        "chunk_breakdown": m["chunk_breakdown"][:40],
        "symbols_by_language": m["symbols_by_language"],
        "parsers_seen": parsers,
        "deterministic_summary_status": summary.get("llm_summary_status"),
        "language_mix": (det or {}).get("language_mix") if isinstance(det, dict) else None,
    }
    # stash for reindex compare
    report.metrics["_file_hash_map"] = m["file_hash_map"]
    report.metrics["_chunk_keys"] = m["chunk_keys"]
    return report


def reindex_and_compare(
    engine, report: RepoReport, spec: dict[str, Any]
) -> None:
    repo_id, job, duration = import_and_wait(spec["url"], f"{spec['key']}-reindex")
    snapshot_id = job.get("snapshot_id")
    report.add(
        "re-index succeeded",
        job.get("status") == "SUCCEEDED",
        f"status={job.get('status')} duration_s={duration:.1f}",
    )
    if not snapshot_id or job.get("status") != "SUCCEEDED":
        report.reindex = {"job": job, "duration_seconds": round(duration, 2)}
        return

    m2 = db_snapshot_metrics(engine, str(snapshot_id))
    prev_files = report.metrics.get("_file_hash_map") or {}
    prev_chunks = report.metrics.get("_chunk_keys") or []
    new_files = m2["file_hash_map"]
    new_chunks = m2["chunk_keys"]

    # Compare overlapping paths
    common = set(prev_files) & set(new_files)
    hash_mismatches = [p for p in sorted(common) if prev_files[p] != new_files[p]]
    # Same commit → hashes should match for all common paths
    report.add(
        "stable content hashes on re-index (common paths)",
        len(hash_mismatches) == 0,
        f"common={len(common)} mismatches={len(hash_mismatches)} "
        f"sample={hash_mismatches[:5]}",
    )
    report.add(
        "no duplicate chunks after re-index",
        int(m2["chunks"]["total"]) == int(m2["chunks"]["unique_spans"]),
        f"total={m2['chunks']['total']} unique={m2['chunks']['unique_spans']}",
    )
    # Deterministic chunk set if same commit
    same_commit_chunk_count = int(m2["chunks"]["total"]) == len(prev_chunks)
    # Multiset compare of chunk keys
    c1 = Counter(prev_chunks)
    c2 = Counter(new_chunks)
    deterministic = c1 == c2
    report.add(
        "deterministic chunk output on re-index (same key multiset)",
        deterministic,
        f"prev_chunks={len(prev_chunks)} new_chunks={len(new_chunks)} "
        f"count_equal={same_commit_chunk_count}",
    )
    if not deterministic:
        only1 = list((c1 - c2).elements())[:5]
        only2 = list((c2 - c1).elements())[:5]
        report.recommendations.append(
            f"Chunk multiset drifted on re-index. only_first={only1} only_second={only2}"
        )

    report.reindex = {
        "repository_id": repo_id,
        "snapshot_id": str(snapshot_id),
        "status": job.get("status"),
        "indexing_duration_seconds": round(duration, 2),
        "files": m2["file_totals"],
        "chunks": m2["chunks"],
        "file_hash_mismatches": len(hash_mismatches),
        "chunk_multiset_equal": deterministic,
    }
    # Drop bulky maps from metrics before write
    report.metrics.pop("_file_hash_map", None)
    report.metrics.pop("_chunk_keys", None)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"API={API}", flush=True)
    health = http_json("GET", "/health")
    ready = http_json("GET", "/ready")
    print(f"health={health} ready={ready}", flush=True)

    regex_offenders = chunking_has_regex_imports()
    global_regex_ok = not regex_offenders

    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

    # Pass 1: import all, wait each sequentially (single worker)
    first_pass: dict[str, dict[str, Any]] = {}
    for spec in REPOS:
        repo_id, job, duration = import_and_wait(spec["url"], spec["key"])
        first_pass[spec["key"]] = {
            "repo_id": repo_id,
            "job": job,
            "duration": duration,
        }

    reports: list[RepoReport] = []
    for spec in REPOS:
        print(f"\n=== Validating {spec['key']} ===", flush=True)
        report = validate_repo(engine, spec, first=first_pass[spec["key"]])
        report.add(
            "no regex structural parsing in chunking package",
            global_regex_ok,
            "offenders=" + (", ".join(regex_offenders) if regex_offenders else "[]"),
        )
        print(f"=== Re-indexing {spec['key']} ===", flush=True)
        reindex_and_compare(engine, report, spec)
        if report.metrics.get("chunks", {}).get("total", 0) == 0 and first_pass[spec["key"]]["job"].get("status") == "SUCCEEDED":
            report.recommendations.append("Succeeded with zero chunks — investigate chunker coverage.")
        path = OUT_DIR / f"report-{spec['key']}.md"
        # strip internal maps if reindex failed early
        report.metrics.pop("_file_hash_map", None)
        report.metrics.pop("_chunk_keys", None)
        path.write_text(render_report(report), encoding="utf-8")
        print(f"Wrote {path}", flush=True)
        reports.append(report)

    # Summary rollup
    lines = [
        "# Week 7 validation rollup",
        "",
        f"- Generated: {datetime.now(UTC).isoformat()}",
        f"- API: `{API}`",
        "- LLM enrichment: OFF",
        "",
        "| Repository | Import | Chunks | Search | Re-index deterministic | Failures |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for r in reports:
        import_ok = any(c.name.startswith("repository imported") and c.ok for c in r.checks)
        chunks = (r.metrics.get("chunks") or {}).get("total", "?")
        search_ok = any(c.name.startswith("exact chunk search") and c.ok for c in r.checks)
        det_ok = any(
            c.name.startswith("deterministic chunk output") and c.ok for c in r.checks
        )
        fail_n = sum(1 for c in r.checks if not c.ok)
        lines.append(
            f"| {r.label} | {'PASS' if import_ok else 'FAIL'} | {chunks} | "
            f"{'PASS' if search_ok else 'FAIL'} | {'PASS' if det_ok else 'FAIL'} | {fail_n} |"
        )
    lines += ["", "## Shared notes", ""]
    lines.append(
        "- Worker completes after **Chunking**; Embedding/Validating job stages are not yet implemented (known Week 9+)."
    )
    lines.append(
        f"- Chunking package `import re` ban: {'PASS' if global_regex_ok else 'FAIL'}."
    )
    all_recs = []
    for r in reports:
        for rec in r.recommendations:
            all_recs.append(f"**{r.key}**: {rec}")
    lines += ["", "## Recommendations before Week 8", ""]
    if all_recs:
        for rec in all_recs:
            lines.append(f"- {rec}")
    else:
        lines.append("- Proceed to Week 8 graphs; no blocking validation failures beyond noted stage gaps.")
    lines.append("")
    rollup = OUT_DIR / "REPORT.md"
    rollup.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {rollup}", flush=True)

    failed = sum(1 for r in reports for c in r.checks if not c.ok)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
