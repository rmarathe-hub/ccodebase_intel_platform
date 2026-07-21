"""Expand chunk_embeddings.vector from 64 to 1536 dimensions (Azure text-embedding-3-small)."""

from collections.abc import Sequence

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

from alembic import op

revision: str = "0010_embedding_dimensions_1536"
down_revision: str | None = "0009_chunk_embeddings"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

OLD_DIMENSIONS = 64
NEW_DIMENSIONS = 1536


def upgrade() -> None:
    # Incompatible vectors cannot be cast; clear before altering column type.
    op.execute(sa.text("DELETE FROM chunk_embeddings"))
    op.alter_column(
        "chunk_embeddings",
        "embedding",
        type_=Vector(NEW_DIMENSIONS),
        existing_type=Vector(OLD_DIMENSIONS),
        existing_nullable=False,
        postgresql_using="embedding::text::vector",
    )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM chunk_embeddings"))
    op.alter_column(
        "chunk_embeddings",
        "embedding",
        type_=Vector(OLD_DIMENSIONS),
        existing_type=Vector(NEW_DIMENSIONS),
        existing_nullable=False,
        postgresql_using="embedding::text::vector",
    )
