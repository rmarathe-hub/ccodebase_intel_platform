"""Alembic revision template placeholders."""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "0001_placeholder"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Domain tables (users, repositories, snapshots, jobs) land in a later day.
    pass


def downgrade() -> None:
    pass
