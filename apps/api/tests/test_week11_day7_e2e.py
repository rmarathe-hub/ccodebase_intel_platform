"""Week 11 Day 7 — product E2E dry run (import → search → ask → graph).

CI-safe: mocked shallow clone against the mixed frontend/backend fixture.
Exercises the demo path without hitting the public internet.
"""

from __future__ import annotations

import shutil
import sys
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic_settings import SettingsConfigDict
from sqlalchemy import update
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings
from app.db.deps import get_db
from app.main import app
from app.models import IndexingJob, JobStatus
from app.models.job_stages import JobStage
from app.services.git_clone import CloneResult
from app.services.rag.ask_repo_budget import reset_repository_ask_budget
from tests.conftest import requires_postgres

pytestmark = requires_postgres

_WORKER_ROOT = Path(__file__).resolve().parents[2] / "worker"
if str(_WORKER_ROOT) not in sys.path:
    sys.path.insert(0, str(_WORKER_ROOT))

from worker.__main__ import process_one  # noqa: E402

MIXED = Path(__file__).resolve().parent / "fixtures" / "mixed_frontend_backend"
REPORT_DIR = (
    Path(__file__).resolve().parents[3] / "docs" / "testing" / "week11-e2e-dry-run"
)
STABLE_COMMIT = "week11e2edryrun01"
DEMO_URL = "https://github.com/week11-platform/e2e-dry-run"


class _DryRunSettings(Settings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")
    embedding_provider: str = "local"
    embedding_model: str = "local-hash-v1"
    embedding_version: str = "9.2"
    embedding_dimensions: int = 1536
    embeddings_enabled: bool = True
    ask_enabled: bool = True
    ask_use_mock: bool = True
    ask_cache_enabled: bool = False
    ask_max_requests_per_repository: int = 40
    incremental_indexing_enabled: bool = True


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    def _override() -> Session:
        return db_session

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _session_factory(db_session: Session) -> sessionmaker:  # type: ignore[type-arg]
    return sessionmaker(
        bind=db_session.get_bind(),
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )


def _quarantine(db_session: Session) -> None:
    db_session.execute(
        update(IndexingJob)
        .where(IndexingJob.status.in_([JobStatus.QUEUED, JobStatus.RUNNING]))
        .values(status=JobStatus.CANCELLED, locked_by=None, locked_until=None)
    )
    db_session.commit()


def _force_settings(monkeypatch: pytest.MonkeyPatch, cfg: Settings) -> None:
    monkeypatch.setattr("worker.__main__.settings", cfg)
    monkeypatch.setattr("app.services.embeddings.persist.settings", cfg)
    monkeypatch.setattr("app.services.snapshot_validation.settings", cfg)
    monkeypatch.setattr("app.services.chunks_query.settings", cfg)
    monkeypatch.setattr("app.services.embeddings.factory.settings", cfg)
    monkeypatch.setattr("app.services.incremental_index.settings", cfg)
    monkeypatch.setattr("app.services.rag.answer.settings", cfg)
    monkeypatch.setattr("app.services.rag.ask_repo_budget.settings", cfg)


def _install_fake_clone(
    monkeypatch: pytest.MonkeyPatch,
    *,
    root: Path,
    commit_sha: str = STABLE_COMMIT,
) -> None:
    @contextmanager
    def fake_clone(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        yield CloneResult(
            path=root,
            branch="main",
            commit_sha=commit_sha,
            bytes_on_disk=2048,
        )

    monkeypatch.setattr("worker.__main__.secure_clone", fake_clone)


def _write_report(checks: list[tuple[str, bool, str]]) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORT_DIR / "REPORT.md"
    passed = sum(1 for _, ok, _ in checks if ok)
    total = len(checks)
    lines = [
        "# Week 11 Day 7 — E2E dry run",
        "",
        f"- Generated: {datetime.now(UTC).isoformat()}",
        "- Fixture: `apps/api/tests/fixtures/mixed_frontend_backend` (mocked clone)",
        "- Path: import → Ready → Search → Ask → Graph → summary → re-index unchanged → cancel",
        f"- Verdict: **{'PASS' if passed == total else 'FAIL'}** ({passed}/{total})",
        "",
        "## Checks",
        "",
        "| Step | Pass | Detail |",
        "| --- | --- | --- |",
    ]
    for name, ok, detail in checks:
        lines.append(f"| {name} | {'yes' if ok else 'NO'} | {detail} |")
    lines += [
        "",
        "## Notes",
        "",
        "- Clone is mocked for CI; live public GitHub import remains the demo path.",
        "- Ask uses mock answers over retrieved evidence (citation-validated).",
        "- Search stays deterministic; Ask stays budgeted.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def test_week11_day7_product_e2e_dry_run(
    client: TestClient,
    db_session: Session,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Full product dry run for Week 11 exit criteria."""
    cfg = _DryRunSettings()
    reset_repository_ask_budget()
    _quarantine(db_session)
    _force_settings(monkeypatch, cfg)

    root = tmp_path / "mixed"
    shutil.copytree(MIXED, root)
    _install_fake_clone(monkeypatch, root=root)

    checks: list[tuple[str, bool, str]] = []

    # --- Import ---
    imported = client.post(
        "/api/v1/repositories/import",
        json={"url": DEMO_URL, "branch": "main"},
    )
    assert imported.status_code == 202, imported.text
    body = imported.json()
    repo_id = body["repository"]["id"]
    job_id = body["job"]["id"]
    checks.append(("import", True, f"repo={repo_id[:8]}… job={job_id[:8]}…"))

    # --- Worker → Ready ---
    assert process_one(_session_factory(db_session), worker_id="week11-day7") is True
    db_session.expire_all()
    job = client.get(f"/api/v1/jobs/{job_id}")
    assert job.status_code == 200
    job_body = job.json()
    ready = (
        job_body["status"] == JobStatus.SUCCEEDED.value
        and job_body["stage"] == JobStage.COMPLETED.value
    )
    checks.append(
        (
            "indexing_ready",
            ready,
            f"status={job_body['status']} stage={job_body['stage']} "
            f"info={job_body.get('error_code')}",
        )
    )
    assert ready

    # --- Repositories list / overview surfaces ---
    repos = client.get("/api/v1/repositories")
    assert repos.status_code == 200
    assert any(r["id"] == repo_id for r in repos.json())
    checks.append(("repo_list", True, f"n={len(repos.json())}"))

    summary = client.get(f"/api/v1/repositories/{repo_id}/summary")
    assert summary.status_code == 200
    det = summary.json().get("deterministic_summary") or {}
    support = det.get("support_level_mix") or {}
    checks.append(
        (
            "summary_support_mix",
            bool(det) and bool(support),
            f"files={det.get('file_count')} mix={support}",
        )
    )
    assert det and support

    # --- Search ---
    search = client.get(
        f"/api/v1/repositories/{repo_id}/chunks/search",
        params={"q": "compute_score", "search_mode": "exact", "limit": 20},
    )
    assert search.status_code == 200
    search_body = search.json()
    search_ok = search_body["total"] >= 1 and all(
        "path" in h and "start_line" in h and "end_line" in h for h in search_body["hits"]
    )
    checks.append(
        (
            "search_exact",
            search_ok,
            f"total={search_body['total']} mode={search_body['search_mode']}",
        )
    )
    assert search_ok

    hybrid = client.get(
        f"/api/v1/repositories/{repo_id}/chunks/search",
        params={"q": "compute_score", "search_mode": "hybrid", "limit": 20},
    )
    assert hybrid.status_code == 200
    hybrid_body = hybrid.json()
    hybrid_ok = hybrid_body["total"] >= 1
    checks.append(
        ("search_hybrid", hybrid_ok, f"total={hybrid_body['total']}"),
    )
    assert hybrid_ok

    # --- Ask ---
    ask = client.post(
        f"/api/v1/repositories/{repo_id}/ask",
        json={
            "question": "where is compute_score defined?",
            "apply_rerank": True,
            "expand": True,
        },
    )
    assert ask.status_code == 200
    ask_body = ask.json()
    ask_ok = (
        ask_body["status"] in {"ok", "partial"}
        and ask_body.get("budget") is not None
        and isinstance(ask_body.get("citations"), list)
    )
    checks.append(
        (
            "ask_grounded",
            ask_ok,
            f"status={ask_body['status']} citations={len(ask_body.get('citations') or [])} "
            f"budget_used={ask_body['budget']['requests_used']}",
        )
    )
    assert ask_ok

    budget = client.get(f"/api/v1/repositories/{repo_id}/ask/budget")
    assert budget.status_code == 200
    assert budget.json()["requests_used"] >= 1
    checks.append(("ask_budget", True, f"used={budget.json()['requests_used']}"))

    # --- Graph ---
    graph = client.get(
        f"/api/v1/repositories/{repo_id}/graph/modules",
        params={"max_nodes": 50, "max_edges": 100},
    )
    assert graph.status_code == 200
    graph_body = graph.json()
    graph_ok = graph_body.get("node_count", 0) >= 1
    checks.append(
        (
            "graph_modules",
            graph_ok,
            f"nodes={graph_body.get('node_count')} edges={graph_body.get('edge_count')}",
        )
    )
    assert graph_ok

    # --- Re-index unchanged (same commit) ---
    reindexed = client.post(f"/api/v1/repositories/{repo_id}/reindex")
    assert reindexed.status_code == 202
    re_job_id = reindexed.json()["job"]["id"]
    assert process_one(_session_factory(db_session), worker_id="week11-day7-re") is True
    db_session.expire_all()
    re_job = client.get(f"/api/v1/jobs/{re_job_id}")
    assert re_job.status_code == 200
    re_body = re_job.json()
    unchanged = (
        re_body["status"] == JobStatus.SUCCEEDED.value
        and re_body.get("error_code") == "index_unchanged"
    )
    checks.append(
        (
            "reindex_unchanged",
            unchanged,
            f"info={re_body.get('error_code')} msg={re_body.get('error_message')}",
        )
    )
    assert unchanged

    # --- Cancel path ---
    queued = client.post(
        "/api/v1/repositories/import",
        json={"url": f"https://github.com/week11-platform/cancel-{uuid4().hex[:6]}"},
    )
    assert queued.status_code == 202
    cancel_job_id = queued.json()["job"]["id"]
    cancelled = client.post(f"/api/v1/jobs/{cancel_job_id}/cancel")
    assert cancelled.status_code == 200
    cancel_ok = cancelled.json()["status"] == JobStatus.CANCELLED.value
    checks.append(("cancel_queued", cancel_ok, f"job={cancel_job_id[:8]}…"))
    assert cancel_ok

    report_path = _write_report(checks)
    assert report_path.is_file()
    assert "PASS" in report_path.read_text(encoding="utf-8")
