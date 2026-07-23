"""Best-effort incremental indexing plans (Week 11 Day 5).

Full re-index remains the safe default when change volume is high or
incremental mode is disabled. Unchanged commits short-circuit unless the
stored embedding identity no longer matches the active search config
(otherwise Hybrid/Semantic silently get zero semantic candidates).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import Settings, settings
from app.models.entities import Chunk, ChunkEmbedding, SourceFile
from app.services.discovery import DiscoveryResult
from app.services.files_query import latest_ready_snapshot

IndexMode = Literal["unchanged", "incremental", "full"]


@dataclass(frozen=True, slots=True)
class IndexPlan:
    mode: IndexMode
    reason: str
    prior_snapshot_id: UUID | None
    prior_commit_sha: str | None
    current_commit_sha: str
    prior_file_count: int
    current_file_count: int
    added: int
    removed: int
    changed: int
    unchanged: int
    change_ratio: float

    def summary(self) -> str:
        return (
            f"mode={self.mode} reason={self.reason} "
            f"added={self.added} removed={self.removed} changed={self.changed} "
            f"unchanged={self.unchanged} ratio={self.change_ratio:.3f}"
        )


def _hashed_paths(discovery: DiscoveryResult) -> dict[str, str | None]:
    return {f.path: f.content_hash for f in discovery.files}


def snapshot_embeddings_match_search_config(
    session: Session,
    *,
    snapshot_id: UUID,
    cfg: Settings | None = None,
) -> bool:
    """True when every chunk has an embedding matching active search filters.

    Hybrid/semantic ANN filters on embedding_model + version + dimensions.
    If the snapshot still has a prior provider (e.g. local-hash) after config
    switched to Azure, those rows do not match and semantic scores stay 0.
    """
    conf = cfg or settings
    if not conf.embeddings_active:
        return True

    chunk_count = int(
        session.scalar(
            select(func.count()).select_from(Chunk).where(Chunk.snapshot_id == snapshot_id)
        )
        or 0
    )
    if chunk_count == 0:
        return True

    match_count = int(
        session.scalar(
            select(func.count())
            .select_from(ChunkEmbedding)
            .where(
                ChunkEmbedding.snapshot_id == snapshot_id,
                ChunkEmbedding.embedding_model == conf.embedding_model,
                ChunkEmbedding.embedding_version == conf.embedding_version,
                ChunkEmbedding.dimensions == conf.embedding_dimensions,
            )
        )
        or 0
    )
    return match_count == chunk_count


def force_full_index_plan(
    *,
    commit_sha: str,
    discovery: DiscoveryResult,
    prior_snapshot_id: UUID | None,
    prior_commit_sha: str | None,
    prior_file_count: int,
) -> IndexPlan:
    """Bypass planner heuristics — always rebuild chunks/embeddings."""
    current_count = len(discovery.files)
    return IndexPlan(
        mode="full",
        reason="force_full",
        prior_snapshot_id=prior_snapshot_id,
        prior_commit_sha=prior_commit_sha,
        current_commit_sha=commit_sha,
        prior_file_count=prior_file_count,
        current_file_count=current_count,
        added=current_count,
        removed=prior_file_count,
        changed=0,
        unchanged=0,
        change_ratio=1.0,
    )


def plan_index(
    session: Session,
    *,
    repository_id: UUID,
    commit_sha: str,
    discovery: DiscoveryResult,
    cfg: Settings | None = None,
) -> IndexPlan:
    """Decide unchanged / incremental / full for this clone+discovery."""
    conf = cfg or settings
    prior = latest_ready_snapshot(session, repository_id)
    current_files = _hashed_paths(discovery)
    current_count = len(current_files)

    if prior is None:
        return IndexPlan(
            mode="full",
            reason="no_prior_snapshot",
            prior_snapshot_id=None,
            prior_commit_sha=None,
            current_commit_sha=commit_sha,
            prior_file_count=0,
            current_file_count=current_count,
            added=current_count,
            removed=0,
            changed=0,
            unchanged=0,
            change_ratio=1.0,
        )

    if prior.commit_sha == commit_sha:
        if snapshot_embeddings_match_search_config(
            session, snapshot_id=prior.id, cfg=conf
        ):
            return IndexPlan(
                mode="unchanged",
                reason="same_commit",
                prior_snapshot_id=prior.id,
                prior_commit_sha=prior.commit_sha,
                current_commit_sha=commit_sha,
                prior_file_count=prior.file_count,
                current_file_count=current_count,
                added=0,
                removed=0,
                changed=0,
                unchanged=current_count,
                change_ratio=0.0,
            )
        # Same git commit, but vectors are missing / wrong model for search.
        return IndexPlan(
            mode="full",
            reason="embedding_config_mismatch",
            prior_snapshot_id=prior.id,
            prior_commit_sha=prior.commit_sha,
            current_commit_sha=commit_sha,
            prior_file_count=prior.file_count,
            current_file_count=current_count,
            added=0,
            removed=0,
            changed=current_count,
            unchanged=0,
            change_ratio=1.0,
        )

    prior_rows = list(
        session.scalars(select(SourceFile).where(SourceFile.snapshot_id == prior.id)).all()
    )
    prior_map = {row.path: row.content_hash for row in prior_rows}
    prior_paths = set(prior_map)
    current_paths = set(current_files)

    added_paths = current_paths - prior_paths
    removed_paths = prior_paths - current_paths
    common = current_paths & prior_paths
    changed_paths = {
        path
        for path in common
        if (current_files.get(path) or "") != (prior_map.get(path) or "")
    }
    unchanged_paths = common - changed_paths

    added = len(added_paths)
    removed = len(removed_paths)
    changed = len(changed_paths)
    unchanged = len(unchanged_paths)
    touched = added + removed + changed
    denom = max(1, len(prior_paths), current_count)
    change_ratio = touched / denom

    if not conf.incremental_indexing_enabled:
        return IndexPlan(
            mode="full",
            reason="incremental_disabled",
            prior_snapshot_id=prior.id,
            prior_commit_sha=prior.commit_sha,
            current_commit_sha=commit_sha,
            prior_file_count=len(prior_paths),
            current_file_count=current_count,
            added=added,
            removed=removed,
            changed=changed,
            unchanged=unchanged,
            change_ratio=change_ratio,
        )

    if touched > conf.incremental_max_changed_files:
        return IndexPlan(
            mode="full",
            reason="too_many_changed_files",
            prior_snapshot_id=prior.id,
            prior_commit_sha=prior.commit_sha,
            current_commit_sha=commit_sha,
            prior_file_count=len(prior_paths),
            current_file_count=current_count,
            added=added,
            removed=removed,
            changed=changed,
            unchanged=unchanged,
            change_ratio=change_ratio,
        )

    if change_ratio > conf.incremental_max_change_ratio:
        return IndexPlan(
            mode="full",
            reason="change_ratio_exceeded",
            prior_snapshot_id=prior.id,
            prior_commit_sha=prior.commit_sha,
            current_commit_sha=commit_sha,
            prior_file_count=len(prior_paths),
            current_file_count=current_count,
            added=added,
            removed=removed,
            changed=changed,
            unchanged=unchanged,
            change_ratio=change_ratio,
        )

    return IndexPlan(
        mode="incremental",
        reason="within_thresholds",
        prior_snapshot_id=prior.id,
        prior_commit_sha=prior.commit_sha,
        current_commit_sha=commit_sha,
        prior_file_count=len(prior_paths),
        current_file_count=current_count,
        added=added,
        removed=removed,
        changed=changed,
        unchanged=unchanged,
        change_ratio=change_ratio,
    )
