"""Snapshot consistency checks for the worker Validating stage (Week 9 Day 5)."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import Settings, settings
from app.models import Chunk, ChunkEmbedding, SourceFile, Symbol


class SnapshotValidationError(RuntimeError):
    """Snapshot failed post-index consistency checks."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class SnapshotValidationStats:
    chunk_count: int
    embedding_count: int
    source_file_count: int
    symbol_count: int
    embeddings_required: bool


def validate_snapshot_for_job(
    session: Session,
    *,
    snapshot_id: UUID,
    cfg: Settings | None = None,
) -> SnapshotValidationStats:
    """Validate citation readiness + embedding consistency. Fail closed on defects."""
    conf = cfg or settings

    chunks = list(
        session.scalars(select(Chunk).where(Chunk.snapshot_id == snapshot_id)).all()
    )
    source_file_count = session.scalar(
        select(func.count()).select_from(SourceFile).where(
            SourceFile.snapshot_id == snapshot_id
        )
    ) or 0
    symbol_count = session.scalar(
        select(func.count()).select_from(Symbol).where(Symbol.snapshot_id == snapshot_id)
    ) or 0

    for chunk in chunks:
        if not chunk.path or not str(chunk.path).strip():
            raise SnapshotValidationError(
                "snapshot_validation_failed",
                f"chunk {chunk.id} missing path",
            )
        if chunk.start_line < 1 or chunk.end_line < chunk.start_line:
            raise SnapshotValidationError(
                "snapshot_validation_failed",
                f"chunk {chunk.id} invalid line range "
                f"{chunk.start_line}-{chunk.end_line}",
            )
        if chunk.support_level == "generic" and chunk.verified_deep:
            raise SnapshotValidationError(
                "snapshot_validation_failed",
                f"chunk {chunk.id} is generic but verified_deep=true",
            )

    embeddings = list(
        session.scalars(
            select(ChunkEmbedding).where(ChunkEmbedding.snapshot_id == snapshot_id)
        ).all()
    )
    chunk_ids = {c.id for c in chunks}
    for emb in embeddings:
        if emb.chunk_id not in chunk_ids:
            raise SnapshotValidationError(
                "snapshot_validation_failed",
                f"orphan embedding {emb.id} for missing chunk {emb.chunk_id}",
            )
        if emb.dimensions != conf.embedding_dimensions:
            raise SnapshotValidationError(
                "snapshot_validation_failed",
                f"embedding {emb.id} dimensions {emb.dimensions} != "
                f"configured {conf.embedding_dimensions}",
            )

    embeddings_required = conf.embeddings_active
    if embeddings_required:
        # After Embedding stage, expect exactly one active embedding per chunk.
        active = [
            e
            for e in embeddings
            if e.embedding_version == conf.embedding_version
            and e.dimensions == conf.embedding_dimensions
        ]
        by_chunk = {e.chunk_id: e for e in active}
        if len(by_chunk) != len(active):
            raise SnapshotValidationError(
                "snapshot_validation_failed",
                "duplicate embeddings for the same chunk under active model/version",
            )
        missing = [c.id for c in chunks if c.id not in by_chunk]
        if missing:
            raise SnapshotValidationError(
                "snapshot_validation_failed",
                f"missing embeddings for {len(missing)} chunk(s); "
                f"have={len(by_chunk)} chunks={len(chunks)}",
            )
    elif embeddings:
        # Embeddings disabled should leave a clean slate (persist clears rows).
        raise SnapshotValidationError(
            "snapshot_validation_failed",
            f"embeddings disabled but {len(embeddings)} rows remain for snapshot",
        )

    return SnapshotValidationStats(
        chunk_count=len(chunks),
        embedding_count=len(embeddings),
        source_file_count=int(source_file_count),
        symbol_count=int(symbol_count),
        embeddings_required=embeddings_required,
    )
