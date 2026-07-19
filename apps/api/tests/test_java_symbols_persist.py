"""Persist Java symbols without clobbering Python / JS/TS."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Repository, SnapshotStatus, SourceFile, Symbol, SymbolRelation
from app.services.discovery import discover_repository
from app.services.java_parser import PARSER_NAME, PARSER_VERSION
from app.services.java_symbols import replace_java_symbols_for_snapshot
from app.services.js_ts_symbols import replace_js_ts_symbols_for_snapshot
from app.services.snapshots import create_or_update_snapshot
from app.services.source_files import replace_source_files_for_snapshot
from app.services.symbols import replace_python_symbols_for_snapshot
from tests.conftest import requires_postgres

pytestmark = requires_postgres

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "java_deep"


def test_replace_java_symbols_for_snapshot(db_session: Session) -> None:
    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"java-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
    )
    db_session.add(repo)
    db_session.flush()
    snapshot = create_or_update_snapshot(
        db_session,
        repository_id=repo.id,
        branch="main",
        commit_sha="java123",
        file_count=0,
        status=SnapshotStatus.READY,
    )
    discovery = discover_repository(FIXTURE)
    replace_source_files_for_snapshot(
        db_session, snapshot_id=snapshot.id, discovery=discovery
    )
    db_session.flush()

    parsed, count, rel_count = replace_java_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=FIXTURE
    )
    db_session.commit()

    assert parsed >= 4  # broken file fails closed
    assert count >= 8
    assert rel_count >= 2

    rows = list(
        db_session.scalars(select(Symbol).where(Symbol.snapshot_id == snapshot.id)).all()
    )
    assert all(r.language == "java" for r in rows)
    assert any(
        r.qualified_name == "com.example.auth.AuthService.login" for r in rows
    )
    assert any(r.kind == "package" and r.qualified_name == "com.example.auth" for r in rows)
    assert any(r.kind == "record" and r.name == "Point" for r in rows)
    assert any(
        r.name == "UserController" and r.framework_role == "spring_rest_controller"
        for r in rows
    )

    relations = list(
        db_session.scalars(
            select(SymbolRelation).where(SymbolRelation.snapshot_id == snapshot.id)
        ).all()
    )
    assert relations
    assert any(
        r.relation_kind == "extends"
        and r.confidence == "resolved"
        and r.candidate_qualified_name == "com.example.common.BaseController"
        for r in relations
    )
    assert any(
        r.relation_kind == "implements"
        and r.confidence == "resolved"
        and r.candidate_qualified_name == "com.example.users.api.UserApi"
        for r in relations
    )

    stamped = list(
        db_session.scalars(
            select(SourceFile).where(
                SourceFile.snapshot_id == snapshot.id,
                SourceFile.language == "java",
                SourceFile.parser_name.is_not(None),
            )
        ).all()
    )
    assert stamped
    assert all(f.parser_name == PARSER_NAME for f in stamped)
    assert all(f.parser_version == PARSER_VERSION for f in stamped)

    broken = next(
        f
        for f in db_session.scalars(
            select(SourceFile).where(
                SourceFile.snapshot_id == snapshot.id,
                SourceFile.path == "Broken.java",
            )
        )
    )
    assert broken.parser_name is None


def test_java_coexists_with_python_and_js(db_session: Session, tmp_path: Path) -> None:
    (tmp_path / "svc.py").write_text("def helper():\n    return 1\n", encoding="utf-8")
    (tmp_path / "ui.ts").write_text(
        "export function add(a: number) { return a; }\n",
        encoding="utf-8",
    )
    (tmp_path / "Main.java").write_text(
        "package demo;\npublic class Main {\n  public void run() {}\n}\n",
        encoding="utf-8",
    )

    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"poly-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
    )
    db_session.add(repo)
    db_session.flush()
    snapshot = create_or_update_snapshot(
        db_session,
        repository_id=repo.id,
        branch="main",
        commit_sha="poly123",
        file_count=0,
        status=SnapshotStatus.READY,
    )
    discovery = discover_repository(tmp_path)
    replace_source_files_for_snapshot(
        db_session, snapshot_id=snapshot.id, discovery=discovery
    )
    db_session.flush()

    replace_python_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=tmp_path
    )
    replace_js_ts_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=tmp_path
    )
    java_files, java_syms, _rels = replace_java_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=tmp_path
    )
    db_session.commit()

    assert java_files == 1
    assert java_syms >= 2

    rows = list(
        db_session.scalars(select(Symbol).where(Symbol.snapshot_id == snapshot.id)).all()
    )
    langs = {r.language for r in rows}
    assert langs >= {"python", "typescript", "java"}
    assert any(r.qualified_name == "demo.Main.run" for r in rows)

    # Java replace must not wipe other languages.
    replace_java_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=tmp_path
    )
    db_session.commit()
    rows2 = list(
        db_session.scalars(select(Symbol).where(Symbol.snapshot_id == snapshot.id)).all()
    )
    assert any(r.language == "python" and r.name == "helper" for r in rows2)
    assert any(r.language == "typescript" and r.name == "add" for r in rows2)
