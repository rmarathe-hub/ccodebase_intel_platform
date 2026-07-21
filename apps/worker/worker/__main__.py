"""Background worker: claim jobs, clone, discover, parse Python, persist."""

from __future__ import annotations

import logging
import socket
import time
import uuid
from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.entities import IndexingJob, SnapshotStatus
from app.models.job_stages import JobStage
from app.services.discovery import discover_repository
from app.services.git_clone import GitCloneError, secure_clone
from app.services.job_queue import (
    claim_next_job,
    get_repository_for_job,
    heartbeat_job,
    schedule_retry,
)
from app.services.jobs import mark_job_succeeded, set_job_stage
from app.services.chunking import replace_chunks_for_snapshot
from app.services.embeddings import replace_embeddings_for_snapshot
from app.services.java_symbols import replace_java_symbols_for_snapshot
from app.services.js_ts_symbols import replace_js_ts_symbols_for_snapshot
from app.services.relationships import replace_structural_relations_for_snapshot
from app.services.snapshot_validation import (
    SnapshotValidationError,
    validate_snapshot_for_job,
)
from app.services.source_files import replace_source_files_for_snapshot
from app.services.snapshots import create_or_update_snapshot
from app.services.symbols import replace_python_symbols_for_snapshot

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
        repository_id = repo.id
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
                session.commit()

                discovery = discover_repository(
                    cloned.path,
                    max_file_bytes=settings.discovery_max_file_bytes,
                    max_files=settings.discovery_max_files,
                    binary_sample_bytes=settings.discovery_binary_sample_bytes,
                )

                job = session.get(IndexingJob, job_id)
                if job is None:
                    raise RuntimeError(f"Job {job_id} disappeared during discovery")
                heartbeat_job(
                    session,
                    job_id=job_id,
                    worker_id=worker_id,
                    lease_seconds=settings.job_lease_seconds,
                )

                snapshot = create_or_update_snapshot(
                    session,
                    repository_id=repository_id,
                    branch=cloned.branch,
                    commit_sha=cloned.commit_sha,
                    file_count=len(discovery.files),
                    status=SnapshotStatus.READY,
                )
                job.snapshot_id = snapshot.id
                replace_source_files_for_snapshot(
                    session,
                    snapshot_id=snapshot.id,
                    discovery=discovery,
                )
                session.flush()

                set_job_stage(job, JobStage.PARSING)
                session.commit()

                job = session.get(IndexingJob, job_id)
                if job is None:
                    raise RuntimeError(f"Job {job_id} disappeared during parsing")
                heartbeat_job(
                    session,
                    job_id=job_id,
                    worker_id=worker_id,
                    lease_seconds=settings.job_lease_seconds,
                )

                set_job_stage(job, JobStage.BUILDING_RELATIONSHIPS)
                session.commit()

                job = session.get(IndexingJob, job_id)
                if job is None:
                    raise RuntimeError(f"Job {job_id} disappeared during relationships")
                heartbeat_job(
                    session,
                    job_id=job_id,
                    worker_id=worker_id,
                    lease_seconds=settings.job_lease_seconds,
                )

                parsed_py, py_symbols, py_calls = replace_python_symbols_for_snapshot(
                    session,
                    snapshot_id=snapshot.id,
                    repo_root=cloned.path,
                )
                parsed_js, js_symbols, js_calls = replace_js_ts_symbols_for_snapshot(
                    session,
                    snapshot_id=snapshot.id,
                    repo_root=cloned.path,
                )
                parsed_java, java_symbols, java_relations, java_calls = (
                    replace_java_symbols_for_snapshot(
                        session,
                        snapshot_id=snapshot.id,
                        repo_root=cloned.path,
                    )
                )

                structural = replace_structural_relations_for_snapshot(
                    session,
                    snapshot_id=snapshot.id,
                )

                set_job_stage(job, JobStage.CHUNKING)
                session.commit()
                job = session.get(IndexingJob, job_id)
                if job is None:
                    raise RuntimeError(f"Job {job_id} disappeared during chunking")
                heartbeat_job(
                    session,
                    job_id=job_id,
                    worker_id=worker_id,
                    lease_seconds=settings.job_lease_seconds,
                )
                chunk_count, enriched_count = replace_chunks_for_snapshot(
                    session,
                    snapshot_id=snapshot.id,
                    repo_root=cloned.path,
                )

                set_job_stage(job, JobStage.EMBEDDING)
                session.commit()
                job = session.get(IndexingJob, job_id)
                if job is None:
                    raise RuntimeError(f"Job {job_id} disappeared during embedding")
                heartbeat_job(
                    session,
                    job_id=job_id,
                    worker_id=worker_id,
                    lease_seconds=settings.job_lease_seconds,
                )
                embedded_count, embedding_skipped = replace_embeddings_for_snapshot(
                    session,
                    snapshot_id=snapshot.id,
                )

                set_job_stage(job, JobStage.VALIDATING)
                session.commit()
                job = session.get(IndexingJob, job_id)
                if job is None:
                    raise RuntimeError(f"Job {job_id} disappeared during validating")
                heartbeat_job(
                    session,
                    job_id=job_id,
                    worker_id=worker_id,
                    lease_seconds=settings.job_lease_seconds,
                )
                validation = validate_snapshot_for_job(
                    session,
                    snapshot_id=snapshot.id,
                )

                mark_job_succeeded(job)
                session.commit()
                logger.info(
                    "Indexed snapshot %s for %s@%s files=%s deep=%s parsed_py=%s "
                    "parsed_js_ts=%s parsed_java=%s symbols=%s calls=%s "
                    "relations=%s import_edges=%s export_edges=%s contains_edges=%s "
                    "chunks=%s enriched=%s embeddings=%s embed_skipped=%s "
                    "validated_chunks=%s validated_embeddings=%s truncated=%s job=%s",
                    snapshot.id,
                    repo_label,
                    cloned.commit_sha[:12],
                    len(discovery.files),
                    discovery.deep_count,
                    parsed_py,
                    parsed_js,
                    parsed_java,
                    py_symbols + js_symbols + java_symbols,
                    py_calls + js_calls + java_calls,
                    java_relations,
                    structural.get("imports", 0),
                    structural.get("exports", 0),
                    structural.get("contains", 0),
                    chunk_count,
                    enriched_count,
                    embedded_count,
                    embedding_skipped,
                    validation.chunk_count,
                    validation.embedding_count,
                    discovery.truncated,
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
        except SnapshotValidationError as exc:
            logger.exception("Validation failed for job %s", job_id)
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
