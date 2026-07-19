"""Add symbols table for Python AST deep extraction."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003_symbols"
down_revision: str | None = "0002_source_files"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NOW = sa.text("now()")


def upgrade() -> None:
    op.create_table(
        "symbols",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("snapshot_id", sa.UUID(), nullable=False),
        sa.Column("source_file_id", sa.UUID(), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=500), nullable=False),
        sa.Column("qualified_name", sa.Text(), nullable=False),
        sa.Column("language", sa.String(length=64), nullable=False),
        sa.Column("start_line", sa.Integer(), nullable=False),
        sa.Column("end_line", sa.Integer(), nullable=False),
        sa.Column("signature", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=NOW, nullable=False),
        sa.ForeignKeyConstraint(
            ["snapshot_id"],
            ["repository_snapshots.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["source_file_id"],
            ["source_files.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "snapshot_id",
            "source_file_id",
            "kind",
            "qualified_name",
            "start_line",
            name="uq_symbols_identity",
        ),
    )
    op.create_index("ix_symbols_snapshot_id", "symbols", ["snapshot_id"], unique=False)
    op.create_index("ix_symbols_source_file_id", "symbols", ["source_file_id"], unique=False)
    op.create_index("ix_symbols_kind", "symbols", ["kind"], unique=False)
    op.create_index("ix_symbols_name", "symbols", ["name"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_symbols_name", table_name="symbols")
    op.drop_index("ix_symbols_kind", table_name="symbols")
    op.drop_index("ix_symbols_source_file_id", table_name="symbols")
    op.drop_index("ix_symbols_snapshot_id", table_name="symbols")
    op.drop_table("symbols")
