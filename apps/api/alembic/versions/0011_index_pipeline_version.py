"""Add repository_snapshots.index_pipeline_version for stale-worker detection."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0011_index_pipeline_version"
down_revision: str | None = "0010_embedding_dimensions_1536"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "repository_snapshots",
        sa.Column("index_pipeline_version", sa.String(length=32), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("repository_snapshots", "index_pipeline_version")
