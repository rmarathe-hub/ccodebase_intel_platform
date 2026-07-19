"""Add Python symbol metadata columns (docstring, decorators, params, async)."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0004_symbol_metadata"
down_revision: str | None = "0003_symbols"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("symbols", sa.Column("docstring", sa.Text(), nullable=True))
    op.add_column("symbols", sa.Column("decorators_json", sa.Text(), nullable=True))
    op.add_column("symbols", sa.Column("parameters_json", sa.Text(), nullable=True))
    op.add_column("symbols", sa.Column("return_annotation", sa.Text(), nullable=True))
    op.add_column(
        "symbols",
        sa.Column(
            "is_async",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )


def downgrade() -> None:
    op.drop_column("symbols", "is_async")
    op.drop_column("symbols", "return_annotation")
    op.drop_column("symbols", "parameters_json")
    op.drop_column("symbols", "decorators_json")
    op.drop_column("symbols", "docstring")
