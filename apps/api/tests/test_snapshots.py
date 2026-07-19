from pathlib import Path
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models import Repository, SnapshotStatus
from app.services.snapshots import count_files_excluding_git, create_or_update_snapshot
from tests.conftest import requires_postgres


def test_count_files_excluding_git(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("hi", encoding="utf-8")
    src = tmp_path / "src"
    src.mkdir()
    (src / "main.py").write_text("print(1)\n", encoding="utf-8")
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("git", encoding="utf-8")
    (git_dir / "objects").mkdir()
    (git_dir / "objects" / "pack").write_text("x", encoding="utf-8")

    assert count_files_excluding_git(tmp_path) == 2


@requires_postgres
def test_create_or_update_snapshot_idempotent(db_session: Session) -> None:
    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"retail-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
    )
    db_session.add(repo)
    db_session.flush()

    first = create_or_update_snapshot(
        db_session,
        repository_id=repo.id,
        branch="main",
        commit_sha="abc123",
        file_count=10,
        status=SnapshotStatus.READY,
    )
    second = create_or_update_snapshot(
        db_session,
        repository_id=repo.id,
        branch="main",
        commit_sha="abc123",
        file_count=12,
        status=SnapshotStatus.READY,
    )
    db_session.commit()
    assert first.id == second.id
    assert second.file_count == 12
