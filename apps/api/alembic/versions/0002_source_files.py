"""Add source_files table for Week 3 discovery."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002_source_files"
down_revision: str | None = "0001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NOW = sa.text("now()")


def upgrade() -> None:
    op.create_table(
        "source_files",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("snapshot_id", sa.UUID(), nullable=False),
        sa.Column("path", sa.Text(), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("line_count", sa.Integer(), nullable=True),
        sa.Column("content_hash", sa.String(length=64), nullable=True),
        sa.Column("language", sa.String(length=64), nullable=True),
        sa.Column("support_level", sa.String(length=16), nullable=False),
        sa.Column("parser_name", sa.String(length=100), nullable=True),
        sa.Column("parser_version", sa.String(length=50), nullable=True),
        sa.Column("skip_reason", sa.String(length=64), nullable=True),
        sa.Column("is_test_file", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_generated", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_vendor", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_binary", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=NOW, nullable=False),
        sa.ForeignKeyConstraint(
            ["snapshot_id"],
            ["repository_snapshots.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("snapshot_id", "path", name="uq_source_files_snapshot_path"),
    )
    op.create_index("ix_source_files_snapshot_id", "source_files", ["snapshot_id"], unique=False)
    op.create_index(
        "ix_source_files_support_level",
        "source_files",
        ["support_level"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_source_files_support_level", table_name="source_files")
    op.drop_index("ix_source_files_snapshot_id", table_name="source_files")
    op.drop_table("source_files")
