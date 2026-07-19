"""Persist Python symbols and stamp parser_name on deep Python files."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Repository, SnapshotStatus, SourceFile, Symbol
from app.services.discovery import discover_repository
from app.services.python_ast_parser import PARSER_NAME
from app.services.snapshots import create_or_update_snapshot
from app.services.source_files import replace_source_files_for_snapshot
from app.services.symbols import replace_python_symbols_for_snapshot
from tests.conftest import requires_postgres

pytestmark = requires_postgres


def test_replace_python_symbols_for_snapshot(db_session: Session, tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text(
        "class App:\n"
        "    def run(self):\n"
        "        return 1\n\n"
        "def helper(x: int) -> int:\n"
        "    return x\n",
        encoding="utf-8",
    )
    (tmp_path / "notes.md").write_text("# docs\n", encoding="utf-8")
    (tmp_path / "broken.py").write_text("def oops(:\n", encoding="utf-8")

    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"symbols-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
    )
    db_session.add(repo)
    db_session.flush()
    snapshot = create_or_update_snapshot(
        db_session,
        repository_id=repo.id,
        branch="main",
        commit_sha="sym123",
        file_count=0,
        status=SnapshotStatus.READY,
    )
    discovery = discover_repository(tmp_path)
    replace_source_files_for_snapshot(
        db_session,
        snapshot_id=snapshot.id,
        discovery=discovery,
    )
    db_session.flush()

    parsed, count = replace_python_symbols_for_snapshot(
        db_session,
        snapshot_id=snapshot.id,
        repo_root=tmp_path,
    )
    db_session.commit()

    assert parsed == 1  # broken.py fails syntax
    assert count >= 3

    files = {
        row.path: row
        for row in db_session.scalars(
            select(SourceFile).where(SourceFile.snapshot_id == snapshot.id)
        ).all()
    }
    assert files["app.py"].parser_name == PARSER_NAME
    assert files["app.py"].parser_version is not None
    assert files["app.py"].parser_version.startswith("4.1-")
    assert files["broken.py"].parser_name is None
    assert files["notes.md"].parser_name is None

    symbols = list(
        db_session.scalars(select(Symbol).where(Symbol.snapshot_id == snapshot.id)).all()
    )
    kinds = {s.kind for s in symbols}
    assert "class" in kinds
    assert "method" in kinds
    assert "function" in kinds
    helper = next(s for s in symbols if s.name == "helper")
    assert helper.qualified_name.endswith(".helper")
    assert helper.parameters_json is not None
    run = next(s for s in symbols if s.name == "run")
    assert "App.run" in run.qualified_name
    assert run.kind == "method"
    # Idempotent replace
    parsed2, count2 = replace_python_symbols_for_snapshot(
        db_session,
        snapshot_id=snapshot.id,
        repo_root=tmp_path,
    )
    db_session.commit()
    assert parsed2 == parsed
    assert count2 == count
    remaining = list(
        db_session.scalars(select(Symbol).where(Symbol.snapshot_id == snapshot.id)).all()
    )
    assert len(remaining) == count
