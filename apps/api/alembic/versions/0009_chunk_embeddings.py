"""Add chunk_embeddings table (pgvector) for Week 9 retrieval."""

from collections.abc import Sequence

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

from alembic import op

revision: str = "0009_chunk_embeddings"
down_revision: str | None = "0008_chunks"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NOW = sa.text("now()")
# Local-hash default dims; Azure providers pad/truncate to this for Day 1–2.
EMBEDDING_DIMENSIONS = 64


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "chunk_embeddings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("chunk_id", sa.UUID(), nullable=False),
        sa.Column("snapshot_id", sa.UUID(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("embedding_provider", sa.String(length=64), nullable=False),
        sa.Column("embedding_model", sa.String(length=128), nullable=False),
        sa.Column("embedding_version", sa.String(length=32), nullable=False),
        sa.Column("dimensions", sa.Integer(), nullable=False),
        sa.Column("embedding", Vector(EMBEDDING_DIMENSIONS), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=NOW, nullable=False),
        sa.ForeignKeyConstraint(["chunk_id"], ["chunks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["snapshot_id"], ["repository_snapshots.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "chunk_id",
            "embedding_model",
            "embedding_version",
            name="uq_chunk_embeddings_chunk_model_version",
        ),
    )
    op.create_index("ix_chunk_embeddings_chunk_id", "chunk_embeddings", ["chunk_id"])
    op.create_index("ix_chunk_embeddings_snapshot_id", "chunk_embeddings", ["snapshot_id"])
    op.create_index(
        "ix_chunk_embeddings_content_hash", "chunk_embeddings", ["content_hash"]
    )
    op.create_index(
        "ix_chunk_embeddings_model_version",
        "chunk_embeddings",
        ["embedding_model", "embedding_version"],
    )


def downgrade() -> None:
    op.drop_index("ix_chunk_embeddings_model_version", table_name="chunk_embeddings")
    op.drop_index("ix_chunk_embeddings_content_hash", table_name="chunk_embeddings")
    op.drop_index("ix_chunk_embeddings_snapshot_id", table_name="chunk_embeddings")
    op.drop_index("ix_chunk_embeddings_chunk_id", table_name="chunk_embeddings")
    op.drop_table("chunk_embeddings")
