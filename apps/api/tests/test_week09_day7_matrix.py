"""Week 9 Day 7 — retrieval matrix / honesty / smoke.

Covers Validating stage completion, exact/semantic/hybrid search,
generic vs deep honesty, and embeddings-disabled semantic emptiness.
"""

from __future__ import annotations

import shutil
import sys
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic_settings import SettingsConfigDict
from sqlalchemy import update
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings
from app.db.deps import get_db
from app.main import app
from app.models import Chunk, ChunkEmbedding, IndexingJob, JobStatus, Repository
from app.models.job_stages import JobStage
from app.services.git_clone import CloneResult
from app.services.jobs import new_indexing_job
from tests.conftest import requires_postgres

pytestmark = requires_postgres

_WORKER_ROOT = Path(__file__).resolve().parents[2] / "worker"
if str(_WORKER_ROOT) not in sys.path:
    sys.path.insert(0, str(_WORKER_ROOT))

from worker.__main__ import process_one  # noqa: E402

MIXED = Path(__file__).resolve().parent / "fixtures" / "mixed_frontend_backend"
POLYGLOT = Path(__file__).resolve().parent / "fixtures" / "generic_polyglot"


class _LocalSettings(Settings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")
    embedding_provider: str = "local"
    embedding_model: str = "local-hash-v1"
    embedding_version: str = "9.2"
    embedding_dimensions: int = 1536
    embeddings_enabled: bool = True
    hybrid_w_exact: float = 0.50
    hybrid_w_semantic: float = 0.50


class _DisabledEmbeddings(_LocalSettings):
    embeddings_enabled: bool = False
    embedding_provider: str = "none"


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    def _override() -> Session:
        return db_session

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _session_factory(db_session: Session) -> sessionmaker:  # type: ignore[type-arg]
    return sessionmaker(
        bind=db_session.get_bind(),
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )


def _force_local_embeddings(monkeypatch: pytest.MonkeyPatch, cfg: Settings) -> None:
    monkeypatch.setattr("worker.__main__.settings", cfg)
    monkeypatch.setattr("app.services.embeddings.persist.settings", cfg)
    monkeypatch.setattr("app.services.snapshot_validation.settings", cfg)
    monkeypatch.setattr("app.services.chunks_query.settings", cfg)
    monkeypatch.setattr("app.services.embeddings.factory.settings", cfg)


def _quarantine(db_session: Session) -> None:
    db_session.execute(
        update(IndexingJob)
        .where(IndexingJob.status.in_([JobStatus.QUEUED, JobStatus.RUNNING]))
        .values(status=JobStatus.CANCELLED, locked_by=None, locked_until=None)
    )
    db_session.commit()


def _run_worker(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
    *,
    root: Path,
    cfg: Settings,
) -> IndexingJob:
    _quarantine(db_session)
    _force_local_embeddings(monkeypatch, cfg)
    repo = Repository(
        host="github.com",
        owner_name="week09",
        name=f"day7-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/week09/day7.git",
    )
    db_session.add(repo)
    db_session.flush()
    job = new_indexing_job(repository_id=repo.id)
    db_session.add(job)
    db_session.commit()

    @contextmanager
    def fake_clone(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        yield CloneResult(
            path=root,
            branch="main",
            commit_sha=uuid4().hex[:12],
            bytes_on_disk=1024,
        )

    monkeypatch.setattr("worker.__main__.secure_clone", fake_clone)
    assert process_one(_session_factory(db_session), worker_id="week09-day7") is True
    db_session.expire_all()
    refreshed = db_session.get(IndexingJob, job.id)
    assert refreshed is not None
    return refreshed


def test_week09_day7_validating_and_search_matrix(
    client: TestClient,
    db_session: Session,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cfg = _LocalSettings()
    mixed = tmp_path / "mixed"
    shutil.copytree(MIXED, mixed)
    job = _run_worker(db_session, monkeypatch, root=mixed, cfg=cfg)

    assert job.status == JobStatus.SUCCEEDED
    assert job.stage == JobStage.COMPLETED.value
    assert job.snapshot_id is not None

    chunks = (
        db_session.query(Chunk).filter(Chunk.snapshot_id == job.snapshot_id).all()
    )
    embeddings = (
        db_session.query(ChunkEmbedding)
        .filter(ChunkEmbedding.snapshot_id == job.snapshot_id)
        .all()
    )
    assert len(chunks) >= 1
    assert len(embeddings) == len(chunks)

    # Deep Python/JS chunks may be verified; generic never.
    for chunk in chunks:
        if chunk.support_level == "generic":
            assert chunk.verified_deep is False

    repo_id = str(job.repository_id)
    exact = client.get(
        f"/api/v1/repositories/{repo_id}/chunks/search",
        params={"q": "def", "search_mode": "exact", "limit": 20},
    )
    assert exact.status_code == 200
    exact_body = exact.json()
    assert exact_body["search_mode"] == "exact"
    assert exact_body["total"] >= 1
    assert all("path" in h and "start_line" in h for h in exact_body["hits"])

    semantic = client.get(
        f"/api/v1/repositories/{repo_id}/chunks/search",
        params={"q": "user service handler", "search_mode": "semantic", "limit": 20},
    )
    assert semantic.status_code == 200
    semantic_body = semantic.json()
    assert semantic_body["search_mode"] == "semantic"
    assert semantic_body["total"] >= 1
    assert any(h.get("score") is not None for h in semantic_body["hits"])

    hybrid = client.get(
        f"/api/v1/repositories/{repo_id}/chunks/search",
        params={"q": "def", "search_mode": "hybrid", "limit": 20},
    )
    assert hybrid.status_code == 200
    hybrid_body = hybrid.json()
    assert hybrid_body["search_mode"] == "hybrid"
    assert hybrid_body["total"] >= 1
    assert any(
        h.get("score_breakdown") and "fused" in h["score_breakdown"]
        for h in hybrid_body["hits"]
    )


def test_week09_day7_polyglot_generic_honesty(
    client: TestClient,
    db_session: Session,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cfg = _LocalSettings()
    poly = tmp_path / "poly"
    shutil.copytree(POLYGLOT, poly)
    job = _run_worker(db_session, monkeypatch, root=poly, cfg=cfg)
    assert job.status == JobStatus.SUCCEEDED
    assert job.snapshot_id is not None

    chunks = (
        db_session.query(Chunk).filter(Chunk.snapshot_id == job.snapshot_id).all()
    )
    assert len(chunks) >= 1
    # Polyglot fixture is generic-heavy; never invent verified deep.
    generic = [c for c in chunks if c.support_level == "generic"]
    assert generic
    assert all(c.verified_deep is False for c in generic)

    resp = client.get(
        f"/api/v1/repositories/{job.repository_id}/chunks/search",
        params={"q": "main", "search_mode": "exact", "limit": 10},
    )
    assert resp.status_code == 200
    for hit in resp.json()["hits"]:
        if hit["support_level"] == "generic":
            assert hit["verified_deep"] is False


def test_week09_day7_semantic_empty_when_embeddings_disabled(
    client: TestClient,
    db_session: Session,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cfg = _DisabledEmbeddings()
    mixed = tmp_path / "mixed-off"
    shutil.copytree(MIXED, mixed)
    job = _run_worker(db_session, monkeypatch, root=mixed, cfg=cfg)
    assert job.status == JobStatus.SUCCEEDED
    assert job.snapshot_id is not None

    embeddings = (
        db_session.query(ChunkEmbedding)
        .filter(ChunkEmbedding.snapshot_id == job.snapshot_id)
        .all()
    )
    assert embeddings == []

    semantic = client.get(
        f"/api/v1/repositories/{job.repository_id}/chunks/search",
        params={"q": "hello", "search_mode": "semantic", "limit": 10},
    )
    assert semantic.status_code == 200
    body = semantic.json()
    assert body["search_mode"] == "semantic"
    assert body["total"] == 0
    assert body["hits"] == []

    # Exact still works offline.
    exact = client.get(
        f"/api/v1/repositories/{job.repository_id}/chunks/search",
        params={"q": "def", "search_mode": "exact", "limit": 10},
    )
    assert exact.status_code == 200
    assert exact.json()["total"] >= 0
