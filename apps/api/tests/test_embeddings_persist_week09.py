"""Week 9 Day 2: persist embeddings + worker Embedding stage."""

from __future__ import annotations

import sys
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic_settings import SettingsConfigDict
from sqlalchemy import select, update
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings
from app.models import (
    Chunk,
    ChunkEmbedding,
    IndexingJob,
    JobStatus,
    Repository,
)
from app.models.job_stages import JobStage
from app.services.embeddings import (
    LocalHashEmbeddingProvider,
    NullEmbeddingProvider,
    replace_embeddings_for_snapshot,
)
from app.services.git_clone import CloneResult
from app.services.jobs import new_indexing_job
from tests.conftest import requires_postgres

pytestmark = requires_postgres

_WORKER_ROOT = Path(__file__).resolve().parents[2] / "worker"
if str(_WORKER_ROOT) not in sys.path:
    sys.path.insert(0, str(_WORKER_ROOT))

from worker.__main__ import process_one  # noqa: E402


def _session_factory(db_session: Session) -> sessionmaker:  # type: ignore[type-arg]
    return sessionmaker(
        bind=db_session.get_bind(),
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )


def _quarantine_other_jobs(db_session: Session) -> None:
    db_session.execute(
        update(IndexingJob)
        .where(IndexingJob.status.in_([JobStatus.QUEUED, JobStatus.RUNNING]))
        .values(
            status=JobStatus.CANCELLED,
            locked_by=None,
            locked_until=None,
        )
    )
    db_session.commit()


def _enqueue_repo(db_session: Session) -> tuple[Repository, IndexingJob]:
    _quarantine_other_jobs(db_session)
    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"embed-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
    )
    db_session.add(repo)
    db_session.flush()
    job = new_indexing_job(repository_id=repo.id)
    db_session.add(job)
    db_session.commit()
    return repo, job


def test_replace_embeddings_idempotent_skip(
    db_session: Session,
) -> None:
    from app.models import RepositorySnapshot, SnapshotStatus, SourceFile

    repo = Repository(
        host="github.com",
        owner_name="t",
        name=f"emb-{uuid4().hex[:6]}",
        default_branch="main",
        clone_url="https://github.com/t/t.git",
    )
    db_session.add(repo)
    db_session.flush()
    snap = RepositorySnapshot(
        repository_id=repo.id,
        commit_sha="abc",
        branch="main",
        status=SnapshotStatus.INDEXING,
    )
    db_session.add(snap)
    db_session.flush()
    sf = SourceFile(
        snapshot_id=snap.id,
        path="a.py",
        language="python",
        support_level="deep",
        content_hash="h1",
        size_bytes=10,
        is_binary=False,
        parser_name="python-ast",
        parser_version="1",
    )
    db_session.add(sf)
    db_session.flush()
    chunk = Chunk(
        snapshot_id=snap.id,
        source_file_id=sf.id,
        path="a.py",
        language="python",
        support_level="deep",
        chunk_type="function",
        start_line=1,
        end_line=2,
        content="def a():\n    return 1\n",
        content_hash="content-hash-a",
        extraction_method="deep_symbol",
        parser_name="python-ast",
        parser_version="1",
        verified_deep=True,
    )
    db_session.add(chunk)
    db_session.commit()

    provider = LocalHashEmbeddingProvider()
    cfg = Settings()
    e1, s1 = replace_embeddings_for_snapshot(
        db_session, snapshot_id=snap.id, provider=provider, cfg=cfg
    )
    db_session.commit()
    assert e1 == 1 and s1 == 0

    e2, s2 = replace_embeddings_for_snapshot(
        db_session, snapshot_id=snap.id, provider=provider, cfg=cfg
    )
    db_session.commit()
    assert e2 == 0 and s2 == 1

    rows = list(
        db_session.scalars(
            select(ChunkEmbedding).where(ChunkEmbedding.snapshot_id == snap.id)
        ).all()
    )
    assert len(rows) == 1
    assert len(rows[0].embedding) == cfg.embedding_dimensions


def test_replace_embeddings_disabled_clears(
    db_session: Session,
) -> None:
    from app.models import RepositorySnapshot, SnapshotStatus, SourceFile

    repo = Repository(
        host="github.com",
        owner_name="t",
        name=f"emb-off-{uuid4().hex[:6]}",
        default_branch="main",
        clone_url="https://github.com/t/t.git",
    )
    db_session.add(repo)
    db_session.flush()
    snap = RepositorySnapshot(
        repository_id=repo.id,
        commit_sha="def",
        branch="main",
        status=SnapshotStatus.INDEXING,
    )
    db_session.add(snap)
    db_session.flush()
    sf = SourceFile(
        snapshot_id=snap.id,
        path="b.py",
        language="python",
        support_level="deep",
        content_hash="h2",
        size_bytes=10,
        is_binary=False,
        parser_name="python-ast",
        parser_version="1",
    )
    db_session.add(sf)
    db_session.flush()
    chunk = Chunk(
        snapshot_id=snap.id,
        source_file_id=sf.id,
        path="b.py",
        language="python",
        support_level="deep",
        chunk_type="function",
        start_line=1,
        end_line=1,
        content="def b():\n    pass\n",
        content_hash="content-hash-b",
        extraction_method="deep_symbol",
        parser_name="python-ast",
        parser_version="1",
        verified_deep=True,
    )
    db_session.add(chunk)
    db_session.commit()

    replace_embeddings_for_snapshot(
        db_session,
        snapshot_id=snap.id,
        provider=LocalHashEmbeddingProvider(),
        cfg=Settings(),
    )
    db_session.commit()
    assert (
        db_session.scalars(
            select(ChunkEmbedding).where(ChunkEmbedding.snapshot_id == snap.id)
        ).first()
        is not None
    )

    class Off(Settings):
        model_config = SettingsConfigDict(env_file=None, extra="ignore")
        embeddings_enabled: bool = False

    embedded, skipped = replace_embeddings_for_snapshot(
        db_session,
        snapshot_id=snap.id,
        provider=NullEmbeddingProvider(),
        cfg=Off(),
    )
    db_session.commit()
    assert embedded == 0
    assert skipped == 1
    assert (
        list(
            db_session.scalars(
                select(ChunkEmbedding).where(ChunkEmbedding.snapshot_id == snap.id)
            ).all()
        )
        == []
    )


def test_worker_pipeline_embeds_chunks(
    db_session: Session,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (tmp_path / "svc.py").write_text(
        "def helper():\n"
        "    return 1\n\n"
        "def main():\n"
        "    return helper()\n",
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text("# x\n", encoding="utf-8")

    _repo, job = _enqueue_repo(db_session)

    @contextmanager
    def fake_clone(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        yield CloneResult(
            path=tmp_path,
            branch="main",
            commit_sha="embed123abc456",
            bytes_on_disk=128,
        )

    monkeypatch.setattr("worker.__main__.secure_clone", fake_clone)

    factory = _session_factory(db_session)
    assert process_one(factory, worker_id="test-worker-embed") is True

    db_session.expire_all()
    refreshed = db_session.get(IndexingJob, job.id)
    assert refreshed is not None
    assert refreshed.status == JobStatus.SUCCEEDED
    assert refreshed.stage == JobStage.COMPLETED.value
    assert refreshed.snapshot_id is not None

    chunks = list(
        db_session.scalars(
            select(Chunk).where(Chunk.snapshot_id == refreshed.snapshot_id)
        ).all()
    )
    assert len(chunks) >= 1

    embeddings = list(
        db_session.scalars(
            select(ChunkEmbedding).where(
                ChunkEmbedding.snapshot_id == refreshed.snapshot_id
            )
        ).all()
    )
    assert len(embeddings) == len(chunks)
    assert all(e.embedding_provider == "local" for e in embeddings)
    assert all(e.dimensions == 64 for e in embeddings)
