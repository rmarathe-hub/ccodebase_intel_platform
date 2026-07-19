"""Spring fixture repository matrix — full controller/service/impl stack."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.main import app
from app.models import (
    Repository,
    SnapshotStatus,
    SourceFile,
    Symbol,
    SymbolCall,
    SymbolRelation,
)
from app.services.discovery import discover_repository
from app.services.java_parser import PARSER_NAME, parse_java_source
from app.services.java_symbols import replace_java_symbols_for_snapshot
from app.services.snapshots import create_or_update_snapshot
from app.services.source_files import replace_source_files_for_snapshot
from tests.conftest import requires_postgres

pytestmark = requires_postgres

FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "spring_fixture"

EXPECTED_PATHS = {
    "com/example/demo/Application.java",
    "com/example/demo/SecurityConfig.java",
    "com/example/demo/user/UserController.java",
    "com/example/demo/user/UserService.java",
    "com/example/demo/user/UserServiceImpl.java",
    "com/example/demo/user/UserRepository.java",
    "com/example/demo/user/UserEntity.java",
}


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    def _override() -> Session:
        return db_session

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_spring_fixture_discovery_shape() -> None:
    result = discover_repository(FIXTURE_ROOT)
    paths = {f.path for f in result.files}
    assert EXPECTED_PATHS <= paths
    assert result.deep_count >= len(EXPECTED_PATHS)


def test_spring_fixture_offline_parse_roles() -> None:
    controller = parse_java_source(
        (FIXTURE_ROOT / "com/example/demo/user/UserController.java").read_text(
            encoding="utf-8"
        ),
        relative_path="com/example/demo/user/UserController.java",
    )
    assert controller.ok
    assert any(
        s.name == "UserController"
        and s.kind == "class"
        and s.framework_role == "spring_rest_controller"
        for s in controller.symbols
    )
    assert any(
        s.name == "get" and s.framework_role == "spring_route" for s in controller.symbols
    )

    impl = parse_java_source(
        (FIXTURE_ROOT / "com/example/demo/user/UserServiceImpl.java").read_text(
            encoding="utf-8"
        ),
        relative_path="com/example/demo/user/UserServiceImpl.java",
    )
    assert impl.ok
    assert any(
        s.name == "UserServiceImpl" and s.framework_role == "spring_service"
        for s in impl.symbols
    )
    assert any(
        r.relation_kind == "implements" and r.raw_target == "UserService"
        for r in impl.relations
    )

    entity = parse_java_source(
        (FIXTURE_ROOT / "com/example/demo/user/UserEntity.java").read_text(
            encoding="utf-8"
        ),
        relative_path="com/example/demo/user/UserEntity.java",
    )
    assert entity.ok
    assert any(
        s.name == "UserEntity" and s.framework_role == "spring_entity" for s in entity.symbols
    )

    app_sym = parse_java_source(
        (FIXTURE_ROOT / "com/example/demo/Application.java").read_text(encoding="utf-8"),
        relative_path="com/example/demo/Application.java",
    )
    assert app_sym.ok
    assert any(
        s.name == "Application" and s.framework_role == "spring_configuration"
        for s in app_sym.symbols
    )


def test_spring_fixture_index_relations_calls_and_api(
    client: TestClient, db_session: Session
) -> None:
    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"spring-{uuid4().hex[:8]}",
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
    discovery = discover_repository(FIXTURE_ROOT)
    replace_source_files_for_snapshot(
        db_session, snapshot_id=snapshot.id, discovery=discovery
    )
    db_session.flush()

    parsed, sym_count, rel_count, call_count = replace_java_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=FIXTURE_ROOT
    )
    db_session.commit()

    assert parsed == len(EXPECTED_PATHS)
    assert sym_count >= 15
    assert rel_count >= 1
    assert call_count >= 2

    symbols = list(
        db_session.scalars(select(Symbol).where(Symbol.snapshot_id == snapshot.id)).all()
    )

    def role_of(name: str) -> str | None:
        for s in symbols:
            if s.name == name and s.kind in {"class", "interface", "enum", "record"}:
                return s.framework_role
        return None

    def detail_of(name: str) -> str | None:
        for s in symbols:
            if s.name == name and s.kind in {"class", "interface", "enum", "record"}:
                return s.framework_detail
        return None

    assert role_of("UserController") == "spring_rest_controller"
    assert role_of("UserService") == "spring_interface"
    assert role_of("UserServiceImpl") == "spring_service"
    assert "implements:com.example.demo.user.UserService" in (detail_of("UserServiceImpl") or "")
    assert role_of("UserRepository") == "spring_repository"
    assert role_of("UserEntity") == "spring_entity"
    assert role_of("SecurityConfig") == "spring_configuration"
    assert role_of("Application") == "spring_configuration"

    java_files = list(
        db_session.scalars(
            select(SourceFile).where(
                SourceFile.snapshot_id == snapshot.id,
                SourceFile.path.in_(EXPECTED_PATHS),
            )
        ).all()
    )
    assert len(java_files) == len(EXPECTED_PATHS)
    assert all(f.parser_name == PARSER_NAME for f in java_files)

    relations = list(
        db_session.scalars(
            select(SymbolRelation).where(SymbolRelation.snapshot_id == snapshot.id)
        ).all()
    )
    assert any(
        r.relation_kind == "implements"
        and r.confidence == "resolved"
        and r.from_qualified_name == "com.example.demo.user.UserServiceImpl"
        and r.candidate_qualified_name == "com.example.demo.user.UserService"
        for r in relations
    )

    calls = list(
        db_session.scalars(
            select(SymbolCall).where(SymbolCall.snapshot_id == snapshot.id)
        ).all()
    )
    assert any(
        c.confidence == "resolved"
        and c.candidate_qualified_name == "com.example.demo.user.UserService.findById"
        for c in calls
    ) or any(
        c.confidence == "resolved"
        and c.candidate_qualified_name
        == "com.example.demo.user.UserServiceImpl.findById"
        for c in calls
    )
    assert any(
        c.confidence == "resolved"
        and c.candidate_qualified_name == "com.example.demo.user.UserRepository.findById"
        for c in calls
    )

    # API filters
    rest = client.get(
        f"/api/v1/repositories/{repo.id}/symbols",
        params={"framework_role": "spring_rest_controller"},
    )
    assert rest.status_code == 200
    assert rest.json()["total"] >= 1

    iface = client.get(
        f"/api/v1/repositories/{repo.id}/symbols",
        params={"framework_role": "spring_interface"},
    )
    assert iface.status_code == 200
    assert any(s["name"] == "UserService" for s in iface.json()["symbols"])

    rel_api = client.get(
        f"/api/v1/repositories/{repo.id}/relations",
        params={"relation_kind": "implements", "confidence": "resolved"},
    )
    assert rel_api.status_code == 200
    assert rel_api.json()["total"] >= 1

    calls_api = client.get(
        f"/api/v1/repositories/{repo.id}/calls",
        params={"confidence": "resolved", "limit": 200},
    )
    assert calls_api.status_code == 200
    assert calls_api.json()["total"] >= 2
    assert all(c["language"] == "java" for c in calls_api.json()["calls"])
