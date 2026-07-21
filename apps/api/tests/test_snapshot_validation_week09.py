"""Unit tests for Week 9 Day 5 snapshot validation."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from pydantic_settings import SettingsConfigDict
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models import Chunk, ChunkEmbedding, Repository, SnapshotStatus
from app.services.chunking import replace_chunks_for_snapshot
from app.services.discovery import discover_repository
from app.services.embeddings import replace_embeddings_for_snapshot
from app.services.snapshots import create_or_update_snapshot
from app.services.snapshot_validation import (
    SnapshotValidationError,
    validate_snapshot_for_job,
)
from app.services.source_files import replace_source_files_for_snapshot
from app.services.symbols import replace_python_symbols_for_snapshot
from tests.conftest import requires_postgres

pytestmark = requires_postgres

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "python_deep"


class _LocalSettings(Settings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")
    embedding_provider: str = "local"
    embedding_model: str = "local-hash-v1"
    embedding_version: str = "9.2"
    embedding_dimensions: int = 1536
    embeddings_enabled: bool = True


class _DisabledSettings(_LocalSettings):
    embeddings_enabled: bool = False
    embedding_provider: str = "none"


def _index(db_session: Session) -> object:
    repo = Repository(
        host="github.com",
        owner_name="eval",
        name=f"validate-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/eval/validate.git",
    )
    db_session.add(repo)
    db_session.flush()
    snapshot = create_or_update_snapshot(
        db_session,
        repository_id=repo.id,
        branch="main",
        commit_sha=uuid4().hex[:12],
        file_count=0,
        status=SnapshotStatus.READY,
    )
    discovery = discover_repository(FIXTURE)
    replace_source_files_for_snapshot(
        db_session, snapshot_id=snapshot.id, discovery=discovery
    )
    db_session.flush()
    replace_python_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=FIXTURE
    )
    db_session.flush()
    replace_chunks_for_snapshot(db_session, snapshot_id=snapshot.id, repo_root=FIXTURE)
    db_session.flush()
    return snapshot


def test_validate_passes_after_local_embeddings(db_session: Session) -> None:
    cfg = _LocalSettings()
    snapshot = _index(db_session)
    replace_embeddings_for_snapshot(db_session, snapshot_id=snapshot.id, cfg=cfg)
    db_session.commit()

    stats = validate_snapshot_for_job(db_session, snapshot_id=snapshot.id, cfg=cfg)
    assert stats.chunk_count >= 1
    assert stats.embedding_count == stats.chunk_count
    assert stats.embeddings_required is True


def test_validate_fails_on_generic_verified_deep(db_session: Session) -> None:
    cfg = _LocalSettings()
    snapshot = _index(db_session)
    replace_embeddings_for_snapshot(db_session, snapshot_id=snapshot.id, cfg=cfg)
    chunk = db_session.query(Chunk).filter(Chunk.snapshot_id == snapshot.id).first()
    assert chunk is not None
    chunk.support_level = "generic"
    chunk.verified_deep = True
    db_session.commit()

    with pytest.raises(SnapshotValidationError) as exc:
        validate_snapshot_for_job(db_session, snapshot_id=snapshot.id, cfg=cfg)
    assert exc.value.code == "snapshot_validation_failed"


def test_validate_fails_when_embedding_missing(db_session: Session) -> None:
    cfg = _LocalSettings()
    snapshot = _index(db_session)
    replace_embeddings_for_snapshot(db_session, snapshot_id=snapshot.id, cfg=cfg)
    emb = (
        db_session.query(ChunkEmbedding)
        .filter(ChunkEmbedding.snapshot_id == snapshot.id)
        .first()
    )
    assert emb is not None
    db_session.delete(emb)
    db_session.commit()

    with pytest.raises(SnapshotValidationError):
        validate_snapshot_for_job(db_session, snapshot_id=snapshot.id, cfg=cfg)


def test_validate_passes_when_embeddings_disabled_and_cleared(
    db_session: Session,
) -> None:
    local = _LocalSettings()
    disabled = _DisabledSettings()
    snapshot = _index(db_session)
    replace_embeddings_for_snapshot(db_session, snapshot_id=snapshot.id, cfg=local)
    replace_embeddings_for_snapshot(db_session, snapshot_id=snapshot.id, cfg=disabled)
    db_session.commit()

    stats = validate_snapshot_for_job(db_session, snapshot_id=snapshot.id, cfg=disabled)
    assert stats.embedding_count == 0
    assert stats.embeddings_required is False
