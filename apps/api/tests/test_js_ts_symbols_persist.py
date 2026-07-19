"""Persist JS/TS symbols alongside Python without clobbering (Week 5 Days 1–2)."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Repository, SnapshotStatus, Symbol, SymbolCall
from app.services.discovery import discover_repository
from app.services.js_ts_symbols import replace_js_ts_symbols_for_snapshot
from app.services.snapshots import create_or_update_snapshot
from app.services.source_files import replace_source_files_for_snapshot
from app.services.symbols import replace_python_symbols_for_snapshot
from tests.conftest import requires_postgres

pytestmark = requires_postgres


def test_js_ts_and_python_symbols_coexist(
    db_session: Session, tmp_path: Path
) -> None:
    (tmp_path / "svc.py").write_text(
        "def helper():\n    return 1\n",
        encoding="utf-8",
    )
    (tmp_path / "ui").mkdir()
    (tmp_path / "ui" / "Hello.tsx").write_text(
        "export function Hello() {\n  return <div />;\n}\n"
        "interface Props { name: string }\n",
        encoding="utf-8",
    )
    (tmp_path / "lib.js").write_text(
        "export function add(a, b) { return a + b; }\n"
        "export function main() { return add(1, 2); }\n",
        encoding="utf-8",
    )

    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"js-ts-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
    )
    db_session.add(repo)
    db_session.flush()
    snapshot = create_or_update_snapshot(
        db_session,
        repository_id=repo.id,
        branch="main",
        commit_sha="js123",
        file_count=0,
        status=SnapshotStatus.READY,
    )
    discovery = discover_repository(tmp_path)
    replace_source_files_for_snapshot(
        db_session, snapshot_id=snapshot.id, discovery=discovery
    )
    db_session.flush()

    py_files, py_syms, _calls = replace_python_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=tmp_path
    )
    js_files, js_syms, js_calls = replace_js_ts_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=tmp_path
    )
    db_session.commit()

    assert py_files == 1
    assert py_syms >= 1
    assert js_files == 2
    assert js_syms >= 2
    assert js_calls >= 1

    call_rows = list(
        db_session.scalars(
            select(SymbolCall).where(SymbolCall.snapshot_id == snapshot.id)
        ).all()
    )
    assert any(c.language == "javascript" and c.confidence == "resolved" for c in call_rows)

    rows = list(
        db_session.scalars(select(Symbol).where(Symbol.snapshot_id == snapshot.id)).all()
    )
    langs = {r.language for r in rows}
    assert "python" in langs
    assert "typescript" in langs
    assert "javascript" in langs
    assert any(r.name == "Hello" and r.framework_role == "react_component" for r in rows)
    assert any(r.kind == "interface" and r.name == "Props" for r in rows)

    # Replacing JS/TS must not wipe Python.
    replace_js_ts_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=tmp_path
    )
    db_session.commit()
    rows2 = list(
        db_session.scalars(select(Symbol).where(Symbol.snapshot_id == snapshot.id)).all()
    )
    assert any(r.language == "python" and r.name == "helper" for r in rows2)
