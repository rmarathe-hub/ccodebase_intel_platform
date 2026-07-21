"""Week 11 Day 5: incremental index planning."""

from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings
from app.core.language_contract import SupportLevel
from app.models import Base, Repository, RepositorySnapshot, SnapshotStatus, SourceFile
from app.services.discovery import DiscoveredFile, DiscoveryResult
from app.services.incremental_index import plan_index
from tests.conftest import postgres_available, requires_postgres

pytestmark = requires_postgres


def _disc(*paths_hashes: tuple[str, str]) -> DiscoveryResult:
    files = tuple(
        DiscoveredFile(
            path=path,
            size_bytes=10,
            line_count=1,
            content_hash=h,
            language="python",
            support_level=SupportLevel.DEEP,
            skip_reason=None,
            is_test_file=False,
            is_generated=False,
            is_vendor=False,
            is_binary=False,
        )
        for path, h in paths_hashes
    )
    return DiscoveryResult(files=files, truncated=False, walked_file_count=len(files))


@pytest.fixture()
def session() -> Session:
    if not postgres_available():
        pytest.skip("PostgreSQL required")
    engine = create_engine(Settings().database_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as s:
        yield s
    engine.dispose()


def test_plan_full_when_no_prior(session: Session) -> None:
    repo = Repository(
        host="github.com",
        owner_name="t",
        name=f"inc-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/t/t.git",
    )
    session.add(repo)
    session.commit()

    plan = plan_index(
        session,
        repository_id=repo.id,
        commit_sha="abc",
        discovery=_disc(("a.py", "h1")),
    )
    assert plan.mode == "full"
    assert plan.reason == "no_prior_snapshot"


def test_plan_unchanged_same_commit(session: Session) -> None:
    repo = Repository(
        host="github.com",
        owner_name="t",
        name=f"inc-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/t/t.git",
    )
    session.add(repo)
    session.flush()
    snap = RepositorySnapshot(
        repository_id=repo.id,
        branch="main",
        commit_sha="deadbeef",
        file_count=1,
        status=SnapshotStatus.READY,
    )
    session.add(snap)
    session.commit()

    plan = plan_index(
        session,
        repository_id=repo.id,
        commit_sha="deadbeef",
        discovery=_disc(("a.py", "h1")),
    )
    assert plan.mode == "unchanged"
    assert plan.prior_snapshot_id == snap.id


def test_plan_incremental_within_threshold(session: Session) -> None:
    repo = Repository(
        host="github.com",
        owner_name="t",
        name=f"inc-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/t/t.git",
    )
    session.add(repo)
    session.flush()
    snap = RepositorySnapshot(
        repository_id=repo.id,
        branch="main",
        commit_sha="aaaa",
        file_count=3,
        status=SnapshotStatus.READY,
    )
    session.add(snap)
    session.flush()
    for path, h in (("a.py", "1"), ("b.py", "2"), ("c.py", "3")):
        session.add(
            SourceFile(
                snapshot_id=snap.id,
                path=path,
                size_bytes=1,
                line_count=1,
                content_hash=h,
                language="python",
                support_level="deep",
                parser_name=None,
                parser_version=None,
                skip_reason=None,
                is_test_file=False,
                is_generated=False,
                is_vendor=False,
                is_binary=False,
            )
        )
    session.commit()

    plan = plan_index(
        session,
        repository_id=repo.id,
        commit_sha="bbbb",
        discovery=_disc(("a.py", "1"), ("b.py", "2x"), ("c.py", "3")),
        cfg=Settings(incremental_max_change_ratio=0.5, incremental_max_changed_files=10),
    )
    assert plan.mode == "incremental"
    assert plan.changed == 1
    assert plan.unchanged == 2


def test_plan_full_when_ratio_exceeded(session: Session) -> None:
    repo = Repository(
        host="github.com",
        owner_name="t",
        name=f"inc-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/t/t.git",
    )
    session.add(repo)
    session.flush()
    snap = RepositorySnapshot(
        repository_id=repo.id,
        branch="main",
        commit_sha="aaaa",
        file_count=2,
        status=SnapshotStatus.READY,
    )
    session.add(snap)
    session.flush()
    for path, h in (("a.py", "1"), ("b.py", "2")):
        session.add(
            SourceFile(
                snapshot_id=snap.id,
                path=path,
                size_bytes=1,
                line_count=1,
                content_hash=h,
                language="python",
                support_level="deep",
                parser_name=None,
                parser_version=None,
                skip_reason=None,
                is_test_file=False,
                is_generated=False,
                is_vendor=False,
                is_binary=False,
            )
        )
    session.commit()

    plan = plan_index(
        session,
        repository_id=repo.id,
        commit_sha="bbbb",
        discovery=_disc(("a.py", "1x"), ("b.py", "2x")),
        cfg=Settings(incremental_max_change_ratio=0.1, incremental_max_changed_files=100),
    )
    assert plan.mode == "full"
    assert plan.reason == "change_ratio_exceeded"
