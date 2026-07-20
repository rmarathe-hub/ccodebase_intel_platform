"""Persist Java symbols without clobbering Python / JS/TS."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Repository, SnapshotStatus, SourceFile, Symbol, SymbolCall, SymbolRelation
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

    parsed, count, rel_count, call_count = replace_java_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=FIXTURE
    )
    db_session.commit()

    assert parsed >= 4  # broken file fails closed
    assert count >= 8
    assert rel_count >= 2
    assert call_count >= 1

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
    assert any(
        r.name == "UserApi" and r.framework_role == "spring_interface" for r in rows
    )
    assert any(
        r.name == "UserService"
        and r.framework_detail
        and "implements:com.example.users.api.UserApi" in r.framework_detail
        for r in rows
    )

    java_calls = list(
        db_session.scalars(
            select(SymbolCall).where(
                SymbolCall.snapshot_id == snapshot.id,
                SymbolCall.language == "java",
            )
        ).all()
    )
    assert java_calls
    assert any(c.confidence == "resolved" for c in java_calls)

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
    java_files, java_syms, _rels, _calls = replace_java_symbols_for_snapshot(
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


def test_duplicate_fqcn_across_sample_apps_keeps_per_file_extends(
    db_session: Session, tmp_path: Path
) -> None:
    """Regression: identical FQCNs in different sample trees must not collapse.

    awesome-compose ships the same GreetingRepository in multiple backends.
    Lookup-by-(qname,kind,raw,line) previously assigned both EXTENDS rows to one
    source_file_id, looking like duplicates on a single path.
    """
    sample = """
package com.company.project.repository;
import org.springframework.data.repository.CrudRepository;
public interface GreetingRepository extends CrudRepository {}
"""
    for tree in ("app-a", "app-b"):
        path = (
            tmp_path
            / tree
            / "src"
            / "main"
            / "java"
            / "com"
            / "company"
            / "project"
            / "repository"
        )
        path.mkdir(parents=True)
        (path / "GreetingRepository.java").write_text(sample, encoding="utf-8")

    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"java-dup-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
    )
    db_session.add(repo)
    db_session.flush()
    snapshot = create_or_update_snapshot(
        db_session,
        repository_id=repo.id,
        branch="main",
        commit_sha="dupfqcn1",
        file_count=0,
        status=SnapshotStatus.READY,
    )
    discovery = discover_repository(tmp_path)
    replace_source_files_for_snapshot(
        db_session, snapshot_id=snapshot.id, discovery=discovery
    )
    db_session.flush()

    _parsed, _syms, rel_count, _calls = replace_java_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=tmp_path
    )
    db_session.commit()

    extends = list(
        db_session.scalars(
            select(SymbolRelation).where(
                SymbolRelation.snapshot_id == snapshot.id,
                SymbolRelation.relation_kind == "extends",
            )
        ).all()
    )
    assert rel_count >= 2
    assert len(extends) == 2
    file_ids = {r.source_file_id for r in extends}
    assert len(file_ids) == 2
    paths = {
        db_session.get(SourceFile, fid).path  # type: ignore[union-attr]
        for fid in file_ids
    }
    assert any("app-a" in p for p in paths)
    assert any("app-b" in p for p in paths)
