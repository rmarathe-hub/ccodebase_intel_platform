"""Background worker: claim jobs, securely clone, heartbeat, retry."""

from __future__ import annotations

import logging
import socket
import time
import uuid
from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.entities import IndexingJob
from app.models.job_stages import JobStage
from app.services.git_clone import GitCloneError, secure_clone
from app.services.job_queue import (
    claim_next_job,
    get_repository_for_job,
    heartbeat_job,
    schedule_retry,
)
from app.services.jobs import mark_job_succeeded, set_job_stage


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("codeintel.worker")


def _worker_id() -> str:
    return f"{settings.worker_id}-{socket.gethostname()}-{uuid.uuid4().hex[:8]}"


def process_one(session_factory: sessionmaker, worker_id: str) -> bool:  # type: ignore[type-arg]
    """Claim and process a single job. Returns True if work was done."""
    with session_factory() as session:
        job = claim_next_job(
            session,
            worker_id=worker_id,
            lease_seconds=settings.job_lease_seconds,
            retry_delay_seconds=settings.job_retry_delay_seconds,
        )
        if job is None:
            session.commit()
            return False

        job_id = job.id
        repo = get_repository_for_job(session, job)
        clone_url = repo.clone_url
        repo_label = f"{repo.owner_name}/{repo.name}"
        set_job_stage(job, JobStage.CLONING)
        session.commit()
        logger.info("Claimed job %s for %s", job_id, repo_label)

        try:
            with secure_clone(
                clone_url,
                timeout_seconds=settings.git_clone_timeout_seconds,
                max_bytes=settings.git_clone_max_bytes,
                base_dir=settings.git_clone_base_dir,
            ) as cloned:
                job = session.get(IndexingJob, job_id)
                if job is None:
                    raise RuntimeError(f"Job {job_id} disappeared during clone")
                heartbeat_job(
                    session,
                    job_id=job_id,
                    worker_id=worker_id,
                    lease_seconds=settings.job_lease_seconds,
                )
                set_job_stage(job, JobStage.DISCOVERING_FILES)
                # Snapshot creation lands next; clone success completes this slice of work.
                mark_job_succeeded(job)
                session.commit()
                logger.info(
                    "Cloned %s@%s (%s bytes) for job %s",
                    repo_label,
                    cloned.commit_sha[:12],
                    cloned.bytes_on_disk,
                    job_id,
                )
            return True
        except GitCloneError as exc:
            logger.exception("Clone failed for job %s", job_id)
            job = session.get(IndexingJob, job_id)
            if job is not None:
                schedule_retry(
                    session,
                    job,
                    delay_seconds=settings.job_retry_delay_seconds,
                    error_code=exc.code,
                    error_message=str(exc),
                )
                session.commit()
            return True
        except Exception as exc:  # noqa: BLE001 — keep the poll loop alive
            logger.exception("Unexpected failure for job %s", job_id)
            job = session.get(IndexingJob, job_id)
            if job is not None:
                schedule_retry(
                    session,
                    job,
                    delay_seconds=settings.job_retry_delay_seconds,
                    error_code="worker_error",
                    error_message=str(exc),
                )
                session.commit()
            return True


def main() -> None:
    worker_id = _worker_id()
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    logger.info("Worker started id=%s at %s", worker_id, datetime.now(UTC).isoformat())

    while True:
        did_work = process_one(session_factory, worker_id)
        if not did_work:
            time.sleep(settings.worker_poll_interval_seconds)


if __name__ == "__main__":
    main()
