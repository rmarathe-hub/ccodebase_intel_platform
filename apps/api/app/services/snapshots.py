"""Create and upsert repository snapshots after a successful clone."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import RepositorySnapshot, SnapshotStatus


def count_files_excluding_git(repo_path: Path) -> int:
    """Count files in a cloned repo, excluding the .git directory."""
    total = 0
    for path in repo_path.rglob("*"):
        if not path.is_file():
            continue
        # Skip anything under .git/
        try:
            path.relative_to(repo_path / ".git")
            continue
        except ValueError:
            pass
        total += 1
    return total


def create_or_update_snapshot(
    session: Session,
    *,
    repository_id: UUID,
    branch: str,
    commit_sha: str,
    file_count: int,
    status: SnapshotStatus = SnapshotStatus.READY,
) -> RepositorySnapshot:
    """Idempotently store a snapshot for (repository_id, commit_sha)."""
    existing = session.scalars(
        select(RepositorySnapshot).where(
            RepositorySnapshot.repository_id == repository_id,
            RepositorySnapshot.commit_sha == commit_sha,
        )
    ).first()
    if existing is not None:
        existing.branch = branch
        existing.file_count = file_count
        existing.status = status
        session.flush()
        return existing

    snapshot = RepositorySnapshot(
        repository_id=repository_id,
        branch=branch,
        commit_sha=commit_sha,
        file_count=file_count,
        status=status,
    )
    session.add(snapshot)
    session.flush()
    return snapshot
