"""Persist chunk embeddings for a snapshot (idempotent by content hash + model)."""

from __future__ import annotations

import logging
import uuid

from sqlalchemy import delete, or_, select
from sqlalchemy.orm import Session

from app.core.config import Settings, settings
from app.models import Chunk, ChunkEmbedding
from app.services.embeddings.factory import get_embedding_provider
from app.services.embeddings.null_provider import NullEmbeddingProvider
from app.services.embeddings.provider import EmbeddingProvider

logger = logging.getLogger(__name__)


def replace_embeddings_for_snapshot(
    session: Session,
    *,
    snapshot_id: uuid.UUID,
    provider: EmbeddingProvider | None = None,
    cfg: Settings | None = None,
) -> tuple[int, int]:
    """Embed chunks for a snapshot.

    Returns ``(embedded_count, skipped_count)``.
    When embeddings are disabled / null provider, deletes existing rows for the
    snapshot (clean slate) and returns ``(0, chunk_count)``.
    """
    conf = cfg or settings
    emb = provider or get_embedding_provider(conf)

    chunks = list(
        session.scalars(
            select(Chunk)
            .where(Chunk.snapshot_id == snapshot_id)
            .order_by(Chunk.path, Chunk.start_line, Chunk.end_line)
        ).all()
    )

    if isinstance(emb, NullEmbeddingProvider) or emb.dimensions < 1:
        deleted = session.execute(
            delete(ChunkEmbedding).where(ChunkEmbedding.snapshot_id == snapshot_id)
        )
        session.flush()
        logger.info(
            "Embeddings disabled for snapshot %s; cleared=%s chunks=%s",
            snapshot_id,
            deleted.rowcount or 0,
            len(chunks),
        )
        return 0, len(chunks)

    if emb.dimensions != conf.embedding_dimensions:
        raise ValueError(
            f"provider dimensions {emb.dimensions} != configured {conf.embedding_dimensions}"
        )

    # Single active model/version per snapshot: drop other models and stale hashes.
    session.execute(
        delete(ChunkEmbedding).where(
            ChunkEmbedding.snapshot_id == snapshot_id,
            or_(
                ChunkEmbedding.embedding_model != emb.model_name,
                ChunkEmbedding.embedding_version != conf.embedding_version,
            ),
        )
    )
    session.flush()

    existing = list(
        session.scalars(
            select(ChunkEmbedding).where(
                ChunkEmbedding.snapshot_id == snapshot_id,
                ChunkEmbedding.embedding_model == emb.model_name,
                ChunkEmbedding.embedding_version == conf.embedding_version,
            )
        ).all()
    )
    chunk_by_id = {c.id: c for c in chunks}
    reusable: dict[uuid.UUID, ChunkEmbedding] = {}
    for row in existing:
        chunk = chunk_by_id.get(row.chunk_id)
        if chunk is not None and chunk.content_hash == row.content_hash:
            reusable[row.chunk_id] = row
        else:
            session.delete(row)
    session.flush()

    to_embed: list[Chunk] = [c for c in chunks if c.id not in reusable]
    embedded = 0
    skipped = len(reusable)
    batch_size = max(1, conf.embedding_batch_size)

    for start in range(0, len(to_embed), batch_size):
        batch = to_embed[start : start + batch_size]
        vectors = emb.embed_texts([c.content for c in batch])
        if len(vectors) != len(batch):
            raise RuntimeError(
                f"embedding provider returned {len(vectors)} vectors for {len(batch)} texts"
            )
        for chunk, vector in zip(batch, vectors, strict=True):
            if len(vector) != conf.embedding_dimensions:
                raise RuntimeError(
                    f"vector length {len(vector)} != {conf.embedding_dimensions}"
                )
            session.add(
                ChunkEmbedding(
                    chunk_id=chunk.id,
                    snapshot_id=snapshot_id,
                    content_hash=chunk.content_hash,
                    embedding_provider=emb.provider_name,
                    embedding_model=emb.model_name,
                    embedding_version=conf.embedding_version,
                    dimensions=conf.embedding_dimensions,
                    embedding=list(vector),
                )
            )
            embedded += 1
        session.flush()

    logger.info(
        "Embedded snapshot %s embedded=%s skipped=%s provider=%s model=%s",
        snapshot_id,
        embedded,
        skipped,
        emb.provider_name,
        emb.model_name,
    )
    return embedded, skipped
