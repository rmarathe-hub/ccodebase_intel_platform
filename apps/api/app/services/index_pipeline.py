"""Index pipeline versioning — detects stale workers / outdated snapshots.

Bump ``INDEX_PIPELINE_VERSION`` whenever chunking coverage rules, path
normalization, or other index *output shape* changes. Ask and the worker
share this constant via the ``app`` package.
"""

from __future__ import annotations

import logging
import os
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import IndexingJob, JobStatus, RepositorySnapshot
from app.services.import_repository import FORCE_FULL_REINDEX_CODE, reindex_repository

logger = logging.getLogger(__name__)

# Bump when index output invariants change (coverage-complete chunking, etc.).
INDEX_PIPELINE_VERSION = "11.1"

# After a force-full job succeeds but the stamp is still wrong, the worker
# process is almost certainly running outdated code — do not spam requeues.
_WORKER_OUTDATED_COOLDOWN = timedelta(minutes=15)


@dataclass(frozen=True, slots=True)
class PipelineFreshness:
    """Result of checking a snapshot against the current pipeline version."""

    current: bool
    snapshot_version: str | None
    expected_version: str
    reindex_queued: bool
    notes: tuple[str, ...]


def current_index_pipeline_version() -> str:
    return INDEX_PIPELINE_VERSION


def resolve_build_identity() -> str:
    """Best-effort git SHA / image identity for ops logs and /health."""
    env = (
        os.environ.get("CODEINTEL_GIT_SHA")
        or os.environ.get("GIT_SHA")
        or os.environ.get("SOURCE_COMMIT")
        or ""
    ).strip()
    if env:
        return env[:40]
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=os.path.dirname(__file__),
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=2,
        )
        return out.strip()[:40] or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def snapshot_pipeline_is_current(snapshot: RepositorySnapshot | None) -> bool:
    if snapshot is None:
        return False
    stamped = getattr(snapshot, "index_pipeline_version", None)
    return stamped == INDEX_PIPELINE_VERSION


def stamp_snapshot_pipeline_version(
    session: Session,
    *,
    snapshot_id: UUID,
    version: str | None = None,
) -> None:
    """Persist the pipeline version that produced this snapshot's index."""
    snap = session.get(RepositorySnapshot, snapshot_id)
    if snap is None:
        return
    snap.index_pipeline_version = version or INDEX_PIPELINE_VERSION
    session.flush()


def _recent_force_full_succeeded(
    session: Session,
    *,
    repository_id: UUID,
) -> IndexingJob | None:
    cutoff = datetime.now(UTC) - _WORKER_OUTDATED_COOLDOWN
    return session.scalars(
        select(IndexingJob)
        .where(
            IndexingJob.repository_id == repository_id,
            IndexingJob.status == JobStatus.SUCCEEDED,
            IndexingJob.error_code == FORCE_FULL_REINDEX_CODE,
            IndexingJob.completed_at.is_not(None),
            IndexingJob.completed_at >= cutoff,
        )
        .order_by(IndexingJob.completed_at.desc())
        .limit(1)
    ).first()


def ensure_snapshot_pipeline_fresh(
    session: Session,
    *,
    repository_id: UUID,
    snapshot: RepositorySnapshot,
    auto_reindex: bool = True,
) -> PipelineFreshness:
    """If the snapshot was built by an older pipeline, optionally queue force-full.

    Ask continues with whatever evidence exists — this never blocks answers.
    When a recent force-full still left a stale stamp, we stop requeueing and
    surface a worker-outdated hint instead (stale long-lived worker).
    """
    expected = INDEX_PIPELINE_VERSION
    stamped = getattr(snapshot, "index_pipeline_version", None)
    if stamped == expected:
        return PipelineFreshness(
            current=True,
            snapshot_version=stamped,
            expected_version=expected,
            reindex_queued=False,
            notes=(),
        )

    notes: list[str] = [
        f"index_pipeline_stale:snapshot={stamped or 'none'}:expected={expected}",
    ]

    if not auto_reindex:
        return PipelineFreshness(
            current=False,
            snapshot_version=stamped,
            expected_version=expected,
            reindex_queued=False,
            notes=tuple(notes + ["index_pipeline_auto_reindex_disabled"]),
        )

    recent = _recent_force_full_succeeded(session, repository_id=repository_id)
    if recent is not None and stamped != expected:
        notes.append(
            "index_pipeline_worker_outdated:"
            "force_full_succeeded_but_stamp_still_stale;"
            "restart_worker_then_force_reindex"
        )
        logger.warning(
            "Snapshot %s still pipeline-stale after recent force-full job %s "
            "(stamped=%s expected=%s) — worker likely running outdated code",
            snapshot.id,
            recent.id,
            stamped,
            expected,
        )
        return PipelineFreshness(
            current=False,
            snapshot_version=stamped,
            expected_version=expected,
            reindex_queued=False,
            notes=tuple(notes),
        )

    try:
        _repo, job, created = reindex_repository(
            session, repository_id, force=True
        )
        if created:
            # Distinguish auto-queued jobs in the UI / job list.
            if job.error_message and "Force full" in (job.error_message or ""):
                job.error_message = (
                    f"Auto force-full: index pipeline "
                    f"{stamped or 'none'} → {expected}"
                )
                session.commit()
            notes.append(f"index_pipeline_reindex_queued:{job.id}")
            logger.info(
                "Queued force-full reindex %s for repo %s (pipeline %s → %s)",
                job.id,
                repository_id,
                stamped,
                expected,
            )
        else:
            notes.append(f"index_pipeline_reindex_active:{job.id}")
    except Exception as exc:  # noqa: BLE001 — Ask must not fail on reindex side effects
        notes.append(f"index_pipeline_reindex_error:{type(exc).__name__}")
        logger.exception(
            "Failed to auto-reindex stale pipeline for repo %s", repository_id
        )
        return PipelineFreshness(
            current=False,
            snapshot_version=stamped,
            expected_version=expected,
            reindex_queued=False,
            notes=tuple(notes),
        )

    return PipelineFreshness(
        current=False,
        snapshot_version=stamped,
        expected_version=expected,
        reindex_queued=True,
        notes=tuple(notes),
    )
