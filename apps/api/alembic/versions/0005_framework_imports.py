"""Add framework + import resolution columns on symbols."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0005_framework_imports"
down_revision: str | None = "0004_symbol_metadata"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("symbols", sa.Column("framework_role", sa.String(length=64), nullable=True))
    op.add_column("symbols", sa.Column("framework_detail", sa.Text(), nullable=True))
    op.add_column("symbols", sa.Column("resolved_module", sa.Text(), nullable=True))
    op.add_column("symbols", sa.Column("import_style", sa.String(length=32), nullable=True))
    op.add_column("symbols", sa.Column("is_local_import", sa.Boolean(), nullable=True))
    op.add_column("symbols", sa.Column("import_alias", sa.String(length=500), nullable=True))
    op.create_index("ix_symbols_framework_role", "symbols", ["framework_role"], unique=False)
    op.create_index("ix_symbols_is_local_import", "symbols", ["is_local_import"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_symbols_is_local_import", table_name="symbols")
    op.drop_index("ix_symbols_framework_role", table_name="symbols")
    op.drop_column("symbols", "import_alias")
    op.drop_column("symbols", "is_local_import")
    op.drop_column("symbols", "import_style")
    op.drop_column("symbols", "resolved_module")
    op.drop_column("symbols", "framework_detail")
    op.drop_column("symbols", "framework_role")
