"""Database constraint and model integrity tests."""

from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import IndexingJob, JobStatus, Repository, RepositorySnapshot, SnapshotStatus, User
from app.services.jobs import new_indexing_job
from tests.conftest import requires_postgres

pytestmark = requires_postgres


def test_repository_unique_identity(db_session: Session) -> None:
    suffix = uuid4().hex[:8]
    kwargs = dict(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"uniq-{suffix}",
        default_branch="main",
        clone_url="https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
    )
    db_session.add(Repository(**kwargs))
    db_session.commit()
    db_session.add(Repository(**kwargs))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_snapshot_unique_repo_commit(db_session: Session) -> None:
    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"snap-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
    )
    db_session.add(repo)
    db_session.flush()
    db_session.add(
        RepositorySnapshot(
            repository_id=repo.id,
            branch="main",
            commit_sha="abc",
            file_count=1,
            status=SnapshotStatus.READY,
        )
    )
    db_session.commit()
    db_session.add(
        RepositorySnapshot(
            repository_id=repo.id,
            branch="main",
            commit_sha="abc",
            file_count=2,
            status=SnapshotStatus.READY,
        )
    )
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_user_email_unique(db_session: Session) -> None:
    email = f"user-{uuid4().hex[:8]}@example.com"
    db_session.add(User(email=email, display_name="A"))
    db_session.commit()
    db_session.add(User(email=email, display_name="B"))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_job_requires_repository_fk(db_session: Session) -> None:
    job = new_indexing_job(repository_id=uuid4())
    db_session.add(job)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_repository_cascade_deletes_jobs(db_session: Session) -> None:
    from sqlalchemy import delete

    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"cascade-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
    )
    db_session.add(repo)
    db_session.flush()
    job = new_indexing_job(repository_id=repo.id)
    db_session.add(job)
    db_session.commit()
    job_id = job.id
    # Exercise DB-level ON DELETE CASCADE (avoid ORM nulling the FK).
    db_session.execute(delete(Repository).where(Repository.id == repo.id))
    db_session.commit()
    assert db_session.get(IndexingJob, job_id) is None


def test_job_status_enum_values_roundtrip(db_session: Session) -> None:
    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"status-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
    )
    db_session.add(repo)
    db_session.flush()
    for status in JobStatus:
        job = new_indexing_job(repository_id=repo.id)
        job.status = status
        db_session.add(job)
        db_session.flush()
        db_session.refresh(job)
        assert job.status == status
    db_session.commit()
