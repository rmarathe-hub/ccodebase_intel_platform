"""Persist discovery rows into source_files."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Repository, SnapshotStatus, SourceFile
from app.services.discovery import discover_repository
from app.services.snapshots import create_or_update_snapshot
from app.services.source_files import replace_source_files_for_snapshot
from tests.conftest import requires_postgres

pytestmark = requires_postgres


def test_replace_source_files_idempotent(db_session: Session, tmp_path: Path) -> None:
    (tmp_path / "main.py").write_text("print(1)\n", encoding="utf-8")
    (tmp_path / "readme.md").write_text("# hi\n", encoding="utf-8")
    (tmp_path / ".env").write_text("X=1\n", encoding="utf-8")

    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"discover-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
    )
    db_session.add(repo)
    db_session.flush()
    snapshot = create_or_update_snapshot(
        db_session,
        repository_id=repo.id,
        branch="main",
        commit_sha="abc123",
        file_count=0,
        status=SnapshotStatus.READY,
    )
    discovery = discover_repository(tmp_path)
    first = replace_source_files_for_snapshot(
        db_session,
        snapshot_id=snapshot.id,
        discovery=discovery,
    )
    db_session.commit()
    assert len(first) == len(discovery.files)

    second = replace_source_files_for_snapshot(
        db_session,
        snapshot_id=snapshot.id,
        discovery=discovery,
    )
    db_session.commit()
    assert len(second) == len(first)

    rows = db_session.scalars(
        select(SourceFile).where(SourceFile.snapshot_id == snapshot.id)
    ).all()
    assert len(rows) == len(discovery.files)
    by_path = {row.path: row for row in rows}
    assert by_path["main.py"].support_level == "deep"
    assert by_path["readme.md"].support_level == "generic"
    assert by_path[".env"].support_level == "skip"
    assert by_path[".env"].skip_reason == "secret_path"
    assert by_path["main.py"].parser_name is None
