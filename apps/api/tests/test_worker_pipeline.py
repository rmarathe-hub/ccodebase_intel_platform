"""Worker pipeline integration: claim → mocked clone → discover → parse → SUCCEEDED."""

from __future__ import annotations

import sys
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import update
from sqlalchemy.orm import Session, sessionmaker

from app.models import IndexingJob, JobStatus, Repository, Symbol, SymbolCall
from app.models.job_stages import JobStage
from app.services.git_clone import CloneResult, GitCloneError
from app.services.jobs import new_indexing_job
from tests.conftest import requires_postgres

pytestmark = requires_postgres

_WORKER_ROOT = Path(__file__).resolve().parents[2] / "worker"
if str(_WORKER_ROOT) not in sys.path:
    sys.path.insert(0, str(_WORKER_ROOT))

from worker.__main__ import process_one  # noqa: E402


def _session_factory(db_session: Session) -> sessionmaker:  # type: ignore[type-arg]
    return sessionmaker(
        bind=db_session.get_bind(),
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )


def _quarantine_other_jobs(db_session: Session) -> None:
    """Shared developer DB may contain leftover QUEUED jobs — neutralize them."""
    db_session.execute(
        update(IndexingJob)
        .where(IndexingJob.status.in_([JobStatus.QUEUED, JobStatus.RUNNING]))
        .values(
            status=JobStatus.CANCELLED,
            locked_by=None,
            locked_until=None,
        )
    )
    db_session.commit()


def _enqueue_repo(db_session: Session) -> tuple[Repository, IndexingJob]:
    _quarantine_other_jobs(db_session)
    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"worker-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
    )
    db_session.add(repo)
    db_session.flush()
    job = new_indexing_job(repository_id=repo.id)
    db_session.add(job)
    db_session.commit()
    return repo, job


def test_worker_pipeline_succeeds_with_python_fixture(
    db_session: Session,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (tmp_path / "svc.py").write_text(
        "def helper():\n"
        "    return 1\n\n"
        "def main():\n"
        "    return helper()\n",
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text("# x\n", encoding="utf-8")
    (tmp_path / "Main.java").write_text("class Main {}\n", encoding="utf-8")

    _repo, job = _enqueue_repo(db_session)

    @contextmanager
    def fake_clone(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        yield CloneResult(
            path=tmp_path,
            branch="main",
            commit_sha="abc123def456",
            bytes_on_disk=128,
        )

    monkeypatch.setattr("worker.__main__.secure_clone", fake_clone)

    factory = _session_factory(db_session)
    assert process_one(factory, worker_id="test-worker-1") is True

    db_session.expire_all()
    refreshed = db_session.get(IndexingJob, job.id)
    assert refreshed is not None
    assert refreshed.status == JobStatus.SUCCEEDED, (
        f"status={refreshed.status} err={refreshed.error_code}:{refreshed.error_message}"
    )
    assert refreshed.stage == JobStage.COMPLETED.value
    assert refreshed.progress_percentage == 100
    assert refreshed.snapshot_id is not None
    assert refreshed.stage not in {
        JobStage.CHUNKING.value,
        JobStage.EMBEDDING.value,
        JobStage.VALIDATING.value,
    }

    symbols = (
        db_session.query(Symbol)
        .filter(Symbol.snapshot_id == refreshed.snapshot_id)
        .all()
    )
    assert any(s.name == "helper" for s in symbols)
    assert any(s.name == "main" for s in symbols)
    assert all(s.language == "python" for s in symbols)

    calls = (
        db_session.query(SymbolCall)
        .filter(SymbolCall.snapshot_id == refreshed.snapshot_id)
        .all()
    )
    assert any(c.confidence == "resolved" for c in calls)


def test_worker_clone_failure_schedules_retry(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _repo, job = _enqueue_repo(db_session)

    @contextmanager
    def boom(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        raise GitCloneError("clone_failed", "simulated clone failure")
        yield  # pragma: no cover

    monkeypatch.setattr("worker.__main__.secure_clone", boom)
    factory = _session_factory(db_session)
    assert process_one(factory, worker_id="test-worker-2") is True

    db_session.expire_all()
    refreshed = db_session.get(IndexingJob, job.id)
    assert refreshed is not None
    assert refreshed.status == JobStatus.QUEUED
    assert refreshed.error_code == "clone_failed"
    assert refreshed.attempt_count >= 1


def test_worker_idle_when_no_jobs(db_session: Session) -> None:
    _quarantine_other_jobs(db_session)
    factory = _session_factory(db_session)
    assert process_one(factory, worker_id="idle-worker") is False


def test_worker_empty_repo_still_succeeds(
    db_session: Session,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _repo, job = _enqueue_repo(db_session)

    @contextmanager
    def fake_clone(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        yield CloneResult(
            path=tmp_path,
            branch="main",
            commit_sha="empty000111222",
            bytes_on_disk=0,
        )

    monkeypatch.setattr("worker.__main__.secure_clone", fake_clone)
    factory = _session_factory(db_session)
    assert process_one(factory, worker_id="empty-worker") is True

    db_session.expire_all()
    refreshed = db_session.get(IndexingJob, job.id)
    assert refreshed is not None
    assert refreshed.status == JobStatus.SUCCEEDED
