"""Index pipeline version stamping + stale auto-reindex."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Chunk, IndexingJob, JobStatus, Repository, SnapshotStatus
from app.services.chunking import replace_chunks_for_snapshot
from app.services.discovery import discover_repository
from app.services.import_repository import FORCE_FULL_REINDEX_CODE
from app.services.index_pipeline import (
    INDEX_PIPELINE_VERSION,
    ensure_snapshot_pipeline_fresh,
    snapshot_pipeline_is_current,
    stamp_snapshot_pipeline_version,
)
from app.services.snapshots import create_or_update_snapshot
from app.services.source_files import replace_source_files_for_snapshot
from tests.conftest import requires_postgres

pytestmark = requires_postgres


def _repo_with_chunked_snapshot(db: Session, tmp_path: Path) -> tuple[Repository, object]:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "hello.py").write_text("def hello():\n    return 1\n", encoding="utf-8")
    repo = Repository(
        host="github.com",
        owner_name="pipe",
        name=f"v-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/pipe/v.git",
    )
    db.add(repo)
    db.flush()
    snap = create_or_update_snapshot(
        db,
        repository_id=repo.id,
        branch="main",
        commit_sha=uuid4().hex[:12],
        file_count=1,
        status=SnapshotStatus.READY,
    )
    disc = discover_repository(root)
    replace_source_files_for_snapshot(db, snapshot_id=snap.id, discovery=disc)
    db.flush()
    replace_chunks_for_snapshot(db, snapshot_id=snap.id, repo_root=root)
    db.commit()
    db.refresh(snap)
    return repo, snap


def test_chunking_stamps_current_pipeline_version(
    db_session: Session, tmp_path: Path
) -> None:
    _repo, snap = _repo_with_chunked_snapshot(db_session, tmp_path)
    assert snap.index_pipeline_version == INDEX_PIPELINE_VERSION
    assert snapshot_pipeline_is_current(snap)
    chunks = db_session.scalars(select(Chunk).where(Chunk.snapshot_id == snap.id)).all()
    assert chunks


def test_stale_pipeline_queues_force_full_once(
    db_session: Session, tmp_path: Path
) -> None:
    repo, snap = _repo_with_chunked_snapshot(db_session, tmp_path)
    snap.index_pipeline_version = "0.0-old"
    db_session.commit()

    first = ensure_snapshot_pipeline_fresh(
        db_session, repository_id=repo.id, snapshot=snap, auto_reindex=True
    )
    assert first.current is False
    assert first.reindex_queued is True
    assert any(n.startswith("index_pipeline_reindex_queued:") for n in first.notes)

    jobs = db_session.scalars(
        select(IndexingJob).where(IndexingJob.repository_id == repo.id)
    ).all()
    assert len(jobs) == 1
    assert jobs[0].error_code == FORCE_FULL_REINDEX_CODE
    assert jobs[0].status == JobStatus.QUEUED

    # Active job → no duplicate queue.
    second = ensure_snapshot_pipeline_fresh(
        db_session, repository_id=repo.id, snapshot=snap, auto_reindex=True
    )
    assert second.current is False
    assert any(n.startswith("index_pipeline_reindex_active:") for n in second.notes)
    jobs2 = db_session.scalars(
        select(IndexingJob).where(IndexingJob.repository_id == repo.id)
    ).all()
    assert len(jobs2) == 1


def test_stale_after_recent_force_full_hints_outdated_worker(
    db_session: Session, tmp_path: Path
) -> None:
    from datetime import UTC, datetime

    repo, snap = _repo_with_chunked_snapshot(db_session, tmp_path)
    snap.index_pipeline_version = "0.0-old"
    job = IndexingJob(
        repository_id=repo.id,
        snapshot_id=snap.id,
        status=JobStatus.SUCCEEDED,
        error_code=FORCE_FULL_REINDEX_CODE,
        error_message="Force full re-index requested",
        completed_at=datetime.now(UTC),
    )
    db_session.add(job)
    db_session.commit()

    result = ensure_snapshot_pipeline_fresh(
        db_session, repository_id=repo.id, snapshot=snap, auto_reindex=True
    )
    assert result.current is False
    assert result.reindex_queued is False
    assert any("index_pipeline_worker_outdated" in n for n in result.notes)
    queued = db_session.scalars(
        select(IndexingJob).where(
            IndexingJob.repository_id == repo.id,
            IndexingJob.status == JobStatus.QUEUED,
        )
    ).all()
    assert queued == []


def test_auto_reindex_can_be_disabled(db_session: Session, tmp_path: Path) -> None:
    repo, snap = _repo_with_chunked_snapshot(db_session, tmp_path)
    snap.index_pipeline_version = None
    db_session.commit()
    result = ensure_snapshot_pipeline_fresh(
        db_session, repository_id=repo.id, snapshot=snap, auto_reindex=False
    )
    assert result.current is False
    assert result.reindex_queued is False
    assert "index_pipeline_auto_reindex_disabled" in result.notes


def test_stamp_helper_sets_version(db_session: Session, tmp_path: Path) -> None:
    repo, snap = _repo_with_chunked_snapshot(db_session, tmp_path)
    snap.index_pipeline_version = None
    db_session.flush()
    stamp_snapshot_pipeline_version(db_session, snapshot_id=snap.id, version="9.9")
    db_session.commit()
    db_session.refresh(snap)
    assert snap.index_pipeline_version == "9.9"
