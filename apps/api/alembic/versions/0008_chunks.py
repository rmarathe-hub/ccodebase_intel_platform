"""Add chunks and llm_enrichment_cache tables."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0008_chunks"
down_revision: str | None = "0007_symbol_relations"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NOW = sa.text("now()")


def upgrade() -> None:
    op.create_table(
        "chunks",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("snapshot_id", sa.UUID(), nullable=False),
        sa.Column("source_file_id", sa.UUID(), nullable=False),
        sa.Column("symbol_id", sa.UUID(), nullable=True),
        sa.Column("path", sa.Text(), nullable=False),
        sa.Column("language", sa.String(length=64), nullable=True),
        sa.Column("support_level", sa.String(length=16), nullable=False),
        sa.Column("chunk_type", sa.String(length=64), nullable=False),
        sa.Column("start_line", sa.Integer(), nullable=False),
        sa.Column("end_line", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("parent_context", sa.Text(), nullable=True),
        sa.Column("extraction_method", sa.String(length=64), nullable=False),
        sa.Column("parser_name", sa.String(length=100), nullable=False),
        sa.Column("parser_version", sa.String(length=50), nullable=False),
        sa.Column("verified_deep", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("llm_enriched", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("llm_provider", sa.String(length=64), nullable=True),
        sa.Column("llm_model", sa.String(length=128), nullable=True),
        sa.Column("prompt_version", sa.String(length=32), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("validation_status", sa.String(length=32), nullable=True),
        sa.Column("semantic_label", sa.String(length=200), nullable=True),
        sa.Column("concise_summary", sa.Text(), nullable=True),
        sa.Column("probable_construct_type", sa.String(length=64), nullable=True),
        sa.Column("entry_point_likelihood", sa.Float(), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=NOW, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=NOW, nullable=False),
        sa.ForeignKeyConstraint(
            ["snapshot_id"], ["repository_snapshots.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["source_file_id"], ["source_files.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["symbol_id"], ["symbols.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chunks_snapshot_id", "chunks", ["snapshot_id"])
    op.create_index("ix_chunks_source_file_id", "chunks", ["source_file_id"])
    op.create_index("ix_chunks_path", "chunks", ["path"])
    op.create_index("ix_chunks_language", "chunks", ["language"])
    op.create_index("ix_chunks_chunk_type", "chunks", ["chunk_type"])
    op.create_index("ix_chunks_content_hash", "chunks", ["content_hash"])
    op.create_index("ix_chunks_support_level", "chunks", ["support_level"])
    op.create_index("ix_chunks_extraction_method", "chunks", ["extraction_method"])

    op.create_table(
        "llm_enrichment_cache",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("cache_key", sa.String(length=128), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("model", sa.String(length=128), nullable=False),
        sa.Column("prompt_version", sa.String(length=32), nullable=False),
        sa.Column("response_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=NOW, nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cache_key", name="uq_llm_enrichment_cache_key"),
    )
    op.create_index("ix_llm_enrichment_cache_key", "llm_enrichment_cache", ["cache_key"])


def downgrade() -> None:
    op.drop_index("ix_llm_enrichment_cache_key", table_name="llm_enrichment_cache")
    op.drop_table("llm_enrichment_cache")
    op.drop_index("ix_chunks_extraction_method", table_name="chunks")
    op.drop_index("ix_chunks_support_level", table_name="chunks")
    op.drop_index("ix_chunks_content_hash", table_name="chunks")
    op.drop_index("ix_chunks_chunk_type", table_name="chunks")
    op.drop_index("ix_chunks_language", table_name="chunks")
    op.drop_index("ix_chunks_path", table_name="chunks")
    op.drop_index("ix_chunks_source_file_id", table_name="chunks")
    op.drop_index("ix_chunks_snapshot_id", table_name="chunks")
    op.drop_table("chunks")
