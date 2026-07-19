"""Add symbol_calls table for Python call extraction."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0006_symbol_calls"
down_revision: str | None = "0005_framework_imports"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NOW = sa.text("now()")


def upgrade() -> None:
    op.create_table(
        "symbol_calls",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("snapshot_id", sa.UUID(), nullable=False),
        sa.Column("source_file_id", sa.UUID(), nullable=False),
        sa.Column("caller_symbol_id", sa.UUID(), nullable=True),
        sa.Column("caller_qualified_name", sa.Text(), nullable=True),
        sa.Column("raw_callee", sa.Text(), nullable=False),
        sa.Column("qualified_expression", sa.Text(), nullable=False),
        sa.Column("line", sa.Integer(), nullable=False),
        sa.Column("candidate_qualified_name", sa.Text(), nullable=True),
        sa.Column("confidence", sa.String(length=32), nullable=False),
        sa.Column("language", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=NOW, nullable=False),
        sa.ForeignKeyConstraint(
            ["snapshot_id"], ["repository_snapshots.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["source_file_id"], ["source_files.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["caller_symbol_id"], ["symbols.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_symbol_calls_snapshot_id", "symbol_calls", ["snapshot_id"])
    op.create_index("ix_symbol_calls_source_file_id", "symbol_calls", ["source_file_id"])
    op.create_index("ix_symbol_calls_caller_symbol_id", "symbol_calls", ["caller_symbol_id"])
    op.create_index("ix_symbol_calls_confidence", "symbol_calls", ["confidence"])


def downgrade() -> None:
    op.drop_index("ix_symbol_calls_confidence", table_name="symbol_calls")
    op.drop_index("ix_symbol_calls_caller_symbol_id", table_name="symbol_calls")
    op.drop_index("ix_symbol_calls_source_file_id", table_name="symbol_calls")
    op.drop_index("ix_symbol_calls_snapshot_id", table_name="symbol_calls")
    op.drop_table("symbol_calls")
