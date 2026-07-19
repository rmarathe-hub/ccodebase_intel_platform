"""Add symbol_relations for Java EXTENDS / IMPLEMENTS edges."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0007_symbol_relations"
down_revision: str | None = "0006_symbol_calls"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NOW = sa.text("now()")


def upgrade() -> None:
    op.create_table(
        "symbol_relations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("snapshot_id", sa.UUID(), nullable=False),
        sa.Column("source_file_id", sa.UUID(), nullable=False),
        sa.Column("from_symbol_id", sa.UUID(), nullable=True),
        sa.Column("from_qualified_name", sa.Text(), nullable=False),
        sa.Column("relation_kind", sa.String(length=32), nullable=False),
        sa.Column("raw_target", sa.Text(), nullable=False),
        sa.Column("line", sa.Integer(), nullable=False),
        sa.Column("candidate_qualified_name", sa.Text(), nullable=True),
        sa.Column("to_symbol_id", sa.UUID(), nullable=True),
        sa.Column("confidence", sa.String(length=32), nullable=False),
        sa.Column("language", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=NOW, nullable=False),
        sa.ForeignKeyConstraint(
            ["snapshot_id"], ["repository_snapshots.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["source_file_id"], ["source_files.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["from_symbol_id"], ["symbols.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["to_symbol_id"], ["symbols.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_symbol_relations_snapshot_id", "symbol_relations", ["snapshot_id"])
    op.create_index(
        "ix_symbol_relations_source_file_id", "symbol_relations", ["source_file_id"]
    )
    op.create_index(
        "ix_symbol_relations_from_symbol_id", "symbol_relations", ["from_symbol_id"]
    )
    op.create_index(
        "ix_symbol_relations_to_symbol_id", "symbol_relations", ["to_symbol_id"]
    )
    op.create_index(
        "ix_symbol_relations_relation_kind", "symbol_relations", ["relation_kind"]
    )
    op.create_index("ix_symbol_relations_confidence", "symbol_relations", ["confidence"])


def downgrade() -> None:
    op.drop_index("ix_symbol_relations_confidence", table_name="symbol_relations")
    op.drop_index("ix_symbol_relations_relation_kind", table_name="symbol_relations")
    op.drop_index("ix_symbol_relations_to_symbol_id", table_name="symbol_relations")
    op.drop_index("ix_symbol_relations_from_symbol_id", table_name="symbol_relations")
    op.drop_index("ix_symbol_relations_source_file_id", table_name="symbol_relations")
    op.drop_index("ix_symbol_relations_snapshot_id", table_name="symbol_relations")
    op.drop_table("symbol_relations")
