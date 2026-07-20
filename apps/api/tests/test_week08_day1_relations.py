"""Week 8 Day 1 — unified RelationKind + structural relation persistence."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import RelationKind, SymbolRelation
from app.models.entities import Repository, SnapshotStatus
from app.services.discovery import discover_repository
from app.services.java_symbols import replace_java_symbols_for_snapshot
from app.services.js_ts_symbols import replace_js_ts_symbols_for_snapshot
from app.services.relationships import replace_structural_relations_for_snapshot
from app.services.snapshots import create_or_update_snapshot
from app.services.source_files import replace_source_files_for_snapshot
from app.services.symbols import replace_python_symbols_for_snapshot
from tests.conftest import requires_postgres

pytestmark = requires_postgres

MIXED = Path(__file__).resolve().parent / "fixtures" / "mixed_frontend_backend"
SPRING = Path(__file__).resolve().parent / "fixtures" / "spring_fixture"


def _index(db_session: Session, root: Path) -> object:
    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"w8d1-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
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
    discovery = discover_repository(root)
    replace_source_files_for_snapshot(
        db_session, snapshot_id=snapshot.id, discovery=discovery
    )
    db_session.flush()
    replace_python_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=root
    )
    replace_js_ts_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=root
    )
    replace_java_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=root
    )
    replace_structural_relations_for_snapshot(db_session, snapshot_id=snapshot.id)
    db_session.commit()
    return snapshot


def test_relation_kind_enum_covers_docs_set() -> None:
    values = {k.value for k in RelationKind}
    assert "imports" in values
    assert "exports" in values
    assert "extends" in values
    assert "implements" in values
    assert "contains" in values
    assert "calls" in values


def test_structural_relations_imports_and_contains(db_session: Session) -> None:
    snapshot = _index(db_session, MIXED)
    rows = list(
        db_session.scalars(
            select(SymbolRelation).where(SymbolRelation.snapshot_id == snapshot.id)
        ).all()
    )
    kinds = {r.relation_kind for r in rows}
    assert RelationKind.IMPORTS.value in kinds
    assert RelationKind.CONTAINS.value in kinds
    imports = [r for r in rows if r.relation_kind == RelationKind.IMPORTS.value]
    assert any(r.language == "python" for r in imports)
    assert any(r.language in {"javascript", "typescript"} for r in imports)
    assert all(r.relation_kind != RelationKind.CALLS.value for r in rows)


def test_java_inheritance_relations_preserved_after_structural_pass(
    db_session: Session,
) -> None:
    snapshot = _index(db_session, SPRING)
    rows = list(
        db_session.scalars(
            select(SymbolRelation).where(SymbolRelation.snapshot_id == snapshot.id)
        ).all()
    )
    kinds = {r.relation_kind for r in rows}
    assert RelationKind.EXTENDS.value in kinds or RelationKind.IMPLEMENTS.value in kinds
    assert RelationKind.IMPORTS.value in kinds
