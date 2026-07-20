from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class SnapshotStatus(enum.StrEnum):
    PENDING = "PENDING"
    INDEXING = "INDEXING"
    READY = "READY"
    FAILED = "FAILED"


class JobStatus(enum.StrEnum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    display_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    repositories: Mapped[list[Repository]] = relationship(back_populates="owner")


class Repository(Base):
    __tablename__ = "repositories"
    __table_args__ = (
        UniqueConstraint("host", "owner_name", "name", name="uq_repositories_identity"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    host: Mapped[str] = mapped_column(String(100), nullable=False, default="github.com")
    owner_name: Mapped[str] = mapped_column(String(200), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    default_branch: Mapped[str] = mapped_column(String(200), nullable=False, default="main")
    clone_url: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    owner: Mapped[User | None] = relationship(back_populates="repositories")
    snapshots: Mapped[list[RepositorySnapshot]] = relationship(back_populates="repository")
    jobs: Mapped[list[IndexingJob]] = relationship(back_populates="repository")


class RepositorySnapshot(Base):
    __tablename__ = "repository_snapshots"
    __table_args__ = (
        UniqueConstraint("repository_id", "commit_sha", name="uq_snapshots_repo_commit"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    branch: Mapped[str] = mapped_column(String(200), nullable=False)
    commit_sha: Mapped[str] = mapped_column(String(64), nullable=False)
    file_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[SnapshotStatus] = mapped_column(
        String(32),
        nullable=False,
        default=SnapshotStatus.PENDING,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    repository: Mapped[Repository] = relationship(back_populates="snapshots")
    jobs: Mapped[list[IndexingJob]] = relationship(back_populates="snapshot")
    source_files: Mapped[list[SourceFile]] = relationship(back_populates="snapshot")
    symbols: Mapped[list[Symbol]] = relationship(back_populates="snapshot")
    symbol_calls: Mapped[list[SymbolCall]] = relationship(back_populates="snapshot")
    symbol_relations: Mapped[list[SymbolRelation]] = relationship(
        back_populates="snapshot"
    )
    chunks: Mapped[list[Chunk]] = relationship(back_populates="snapshot")


class SourceFile(Base):
    """A discovered file under a repository snapshot (Week 3+)."""

    __tablename__ = "source_files"
    __table_args__ = (
        UniqueConstraint("snapshot_id", "path", name="uq_source_files_snapshot_path"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repository_snapshots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    path: Mapped[str] = mapped_column(Text, nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    line_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    language: Mapped[str | None] = mapped_column(String(64), nullable=True)
    support_level: Mapped[str] = mapped_column(String(16), nullable=False, default="skip")
    parser_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    parser_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    skip_reason: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_test_file: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_generated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_vendor: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_binary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    snapshot: Mapped[RepositorySnapshot] = relationship(back_populates="source_files")
    symbols: Mapped[list[Symbol]] = relationship(back_populates="source_file")
    chunks: Mapped[list[Chunk]] = relationship(back_populates="source_file")


class Symbol(Base):
    """Verified deep symbol extracted by a language parser (Week 3 Day 7+)."""

    __tablename__ = "symbols"
    __table_args__ = (
        UniqueConstraint(
            "snapshot_id",
            "source_file_id",
            "kind",
            "qualified_name",
            "start_line",
            name="uq_symbols_identity",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repository_snapshots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("source_files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    qualified_name: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(64), nullable=False, default="python")
    start_line: Mapped[int] = mapped_column(Integer, nullable=False)
    end_line: Mapped[int] = mapped_column(Integer, nullable=False)
    signature: Mapped[str | None] = mapped_column(Text, nullable=True)
    docstring: Mapped[str | None] = mapped_column(Text, nullable=True)
    decorators_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    parameters_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    return_annotation: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_async: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    framework_role: Mapped[str | None] = mapped_column(String(64), nullable=True)
    framework_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_module: Mapped[str | None] = mapped_column(Text, nullable=True)
    import_style: Mapped[str | None] = mapped_column(String(32), nullable=True)
    is_local_import: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    import_alias: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    snapshot: Mapped[RepositorySnapshot] = relationship(back_populates="symbols")
    source_file: Mapped[SourceFile] = relationship(back_populates="symbols")


class SymbolCall(Base):
    """A call site extracted from deep Python analysis (Week 4 Day 5)."""

    __tablename__ = "symbol_calls"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repository_snapshots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("source_files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    caller_symbol_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("symbols.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    caller_qualified_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_callee: Mapped[str] = mapped_column(Text, nullable=False)
    qualified_expression: Mapped[str] = mapped_column(Text, nullable=False)
    line: Mapped[int] = mapped_column(Integer, nullable=False)
    candidate_qualified_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[str] = mapped_column(String(32), nullable=False, default="unresolved")
    language: Mapped[str] = mapped_column(String(64), nullable=False, default="python")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    snapshot: Mapped[RepositorySnapshot] = relationship(back_populates="symbol_calls")


class SymbolRelation(Base):
    """Inheritance / interface edge (Week 6 Day 4+): EXTENDS / IMPLEMENTS."""

    __tablename__ = "symbol_relations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repository_snapshots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("source_files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    from_symbol_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("symbols.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    from_qualified_name: Mapped[str] = mapped_column(Text, nullable=False)
    relation_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    raw_target: Mapped[str] = mapped_column(Text, nullable=False)
    line: Mapped[int] = mapped_column(Integer, nullable=False)
    candidate_qualified_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    to_symbol_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("symbols.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    confidence: Mapped[str] = mapped_column(String(32), nullable=False, default="unresolved")
    language: Mapped[str] = mapped_column(String(64), nullable=False, default="java")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    snapshot: Mapped[RepositorySnapshot] = relationship(back_populates="symbol_relations")


class Chunk(Base):
    """Parser-derived source chunk (Week 7+). Ranges are parser-authoritative."""

    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repository_snapshots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("source_files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    symbol_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("symbols.id", ondelete="SET NULL"),
        nullable=True,
    )
    path: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    language: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    support_level: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    chunk_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    start_line: Mapped[int] = mapped_column(Integer, nullable=False)
    end_line: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    parent_context: Mapped[str | None] = mapped_column(Text, nullable=True)
    extraction_method: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    parser_name: Mapped[str] = mapped_column(String(100), nullable=False)
    parser_version: Mapped[str] = mapped_column(String(50), nullable=False)
    verified_deep: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    llm_enriched: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    llm_provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    llm_model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    validation_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    semantic_label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    concise_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    probable_construct_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    entry_point_likelihood: Mapped[float | None] = mapped_column(Float, nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    snapshot: Mapped[RepositorySnapshot] = relationship(back_populates="chunks")
    source_file: Mapped[SourceFile] = relationship(back_populates="chunks")


class LlmEnrichmentCache(Base):
    """Cache LLM enrichment by content + prompt + model hash."""

    __tablename__ = "llm_enrichment_cache"
    __table_args__ = (UniqueConstraint("cache_key", name="uq_llm_enrichment_cache_key"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cache_key: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(32), nullable=False)
    response_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class IndexingJob(Base):
    __tablename__ = "indexing_jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    snapshot_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repository_snapshots.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[JobStatus] = mapped_column(
        String(32),
        nullable=False,
        default=JobStatus.QUEUED,
        index=True,
    )
    stage: Mapped[str] = mapped_column(String(100), nullable=False, default="queued")
    progress_percentage: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    locked_by: Mapped[str | None] = mapped_column(String(200), nullable=True)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    repository: Mapped[Repository] = relationship(back_populates="jobs")
    snapshot: Mapped[RepositorySnapshot | None] = relationship(back_populates="jobs")
