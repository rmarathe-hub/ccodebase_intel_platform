#!/usr/bin/env python3
"""Re-embed all snapshots that have chunks using the configured embedding provider."""

from __future__ import annotations

from sqlalchemy import create_engine, distinct, select
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models import Chunk
from app.services.embeddings import replace_embeddings_for_snapshot


def main() -> int:
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    try:
        snapshot_ids = list(
            session.scalars(select(distinct(Chunk.snapshot_id))).all()
        )
        if not snapshot_ids:
            print("reindex_embeddings: no snapshots with chunks", flush=True)
            return 0

        print(
            f"reindex_embeddings: provider={settings.embedding_provider} "
            f"model={settings.embedding_model or settings.azure_openai_embedding_deployment} "
            f"dims={settings.embedding_dimensions} snapshots={len(snapshot_ids)}",
            flush=True,
        )
        total_embedded = 0
        total_skipped = 0
        for snapshot_id in snapshot_ids:
            embedded, skipped = replace_embeddings_for_snapshot(
                session, snapshot_id=snapshot_id
            )
            session.commit()
            total_embedded += embedded
            total_skipped += skipped
            print(
                f"snapshot={snapshot_id} embedded={embedded} skipped={skipped}",
                flush=True,
            )
        print(
            f"reindex_embeddings=done embedded={total_embedded} skipped={total_skipped}",
            flush=True,
        )
        return 0
    finally:
        session.close()
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
