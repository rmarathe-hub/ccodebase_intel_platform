"""Concurrency and idempotency smoke tests for the job queue."""

from __future__ import annotations

import threading
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, update
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.models import IndexingJob, JobStatus, Repository
from app.services.job_queue import claim_next_job
from app.services.jobs import new_indexing_job
from tests.conftest import postgres_available, requires_postgres

pytestmark = requires_postgres


def _clear(session: Session) -> None:
    session.execute(
        update(IndexingJob)
        .where(IndexingJob.status.in_((JobStatus.QUEUED, JobStatus.RUNNING)))
        .values(status=JobStatus.CANCELLED, locked_by=None, locked_until=None)
    )
    session.commit()


def test_concurrent_claim_single_winner() -> None:
    """Two workers racing FOR UPDATE SKIP LOCKED must not both claim one job."""
    if not postgres_available():
        pytest.skip("PostgreSQL required")
    engine = create_engine(settings.database_url, pool_pre_ping=True, pool_size=5)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    with SessionLocal() as session:
        _clear(session)
        repo = Repository(
            host="github.com",
            owner_name="rmarathe-hub",
            name=f"concurrent-{uuid4().hex[:8]}",
            default_branch="main",
            clone_url="https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
        )
        session.add(repo)
        session.flush()
        job = new_indexing_job(repository_id=repo.id)
        session.add(job)
        session.commit()
        job_id = job.id

    barrier = threading.Barrier(2)
    results: list[str | None] = []
    lock = threading.Lock()

    def worker(worker_id: str) -> None:
        local = SessionLocal()
        try:
            barrier.wait(timeout=5)
            claimed = claim_next_job(local, worker_id=worker_id, lease_seconds=60)
            local.commit()
            with lock:
                results.append(None if claimed is None else str(claimed.id))
        finally:
            local.close()

    threads = [
        threading.Thread(target=worker, args=("worker-a",)),
        threading.Thread(target=worker, args=("worker-b",)),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)

    claimed_ids = [item for item in results if item is not None]
    assert len(results) == 2
    assert claimed_ids.count(str(job_id)) == 1
    assert len(claimed_ids) == 1

    engine.dispose()
