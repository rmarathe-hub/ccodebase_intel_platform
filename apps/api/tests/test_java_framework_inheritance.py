"""Java annotation heuristics and inheritance resolution (Days 3–4)."""

from __future__ import annotations

from pathlib import Path

from app.services.java_framework import annotation_leaf, detect_java_framework_meta
from app.services.java_inheritance import (
    ExtractedRelation,
    TypeRef,
    resolve_relations,
    resolve_type_name,
)
from app.services.java_parser import PARSER_VERSION, parse_java_source

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "java_deep"


def test_parser_version_day34() -> None:
    assert PARSER_VERSION == "6.6-treesitter"


def test_annotation_leaf_and_class_roles() -> None:
    assert annotation_leaf("@RestController") == "RestController"
    assert annotation_leaf("@org.springframework.stereotype.Service") == "Service"
    meta = detect_java_framework_meta(
        kind="class",
        decorators=('@RestController', '@RequestMapping("/users")'),
    )
    assert meta is not None
    assert meta.role == "spring_rest_controller"


def test_spring_annotations_on_fixture() -> None:
    source = (FIXTURE / "com/example/users/UserController.java").read_text(
        encoding="utf-8"
    )
    result = parse_java_source(
        source, relative_path="com/example/users/UserController.java"
    )
    assert result.ok
    by_name = {s.name: s for s in result.symbols}
    assert by_name["UserController"].framework_role == "spring_rest_controller"
    assert by_name["UserController"].decorators
    assert any("@RestController" in d for d in by_name["UserController"].decorators)
    assert by_name["get"].framework_role == "spring_route"

    service = parse_java_source(
        (FIXTURE / "com/example/users/UserService.java").read_text(encoding="utf-8"),
        relative_path="com/example/users/UserService.java",
    )
    assert service.ok
    svc = next(s for s in service.symbols if s.name == "UserService")
    assert svc.framework_role == "spring_service"


def test_extract_extends_implements_edges() -> None:
    source = (FIXTURE / "com/example/users/UserController.java").read_text(
        encoding="utf-8"
    )
    result = parse_java_source(
        source, relative_path="com/example/users/UserController.java"
    )
    assert result.ok
    kinds = {(r.relation_kind, r.raw_target) for r in result.relations}
    assert ("extends", "BaseController") in kinds
    assert ("implements", "UserApi") in kinds


def test_resolve_same_package_and_import() -> None:
    types = [
        TypeRef(
            kind="class",
            name="BaseController",
            qualified_name="com.example.common.BaseController",
            package="com.example.common",
        ),
        TypeRef(
            kind="interface",
            name="UserApi",
            qualified_name="com.example.users.api.UserApi",
            package="com.example.users.api",
        ),
        TypeRef(
            kind="class",
            name="UserController",
            qualified_name="com.example.users.UserController",
            package="com.example.users",
        ),
    ]
    imports = {
        "BaseController": "com.example.common.BaseController",
        "UserApi": "com.example.users.api.UserApi",
    }
    candidate, confidence = resolve_type_name(
        "BaseController",
        package="com.example.users",
        imports=imports,
        by_qname={t.qualified_name: t for t in types},
        by_simple={t.name: [t] for t in types},
    )
    assert confidence == "resolved"
    assert candidate == "com.example.common.BaseController"

    edges = [
        ExtractedRelation(
            from_qualified_name="com.example.users.UserController",
            relation_kind="extends",
            raw_target="BaseController",
            line=12,
            package="com.example.users",
        ),
        ExtractedRelation(
            from_qualified_name="com.example.users.UserController",
            relation_kind="implements",
            raw_target="UserApi",
            line=12,
            package="com.example.users",
        ),
    ]
    resolved = resolve_relations(
        edges,
        types=types,
        imports_by_from={"com.example.users.UserController": imports},
    )
    assert all(r.confidence == "resolved" for r in resolved)
    targets = {r.relation_kind: r.candidate_qualified_name for r in resolved}
    assert targets["extends"] == "com.example.common.BaseController"
    assert targets["implements"] == "com.example.users.api.UserApi"


def test_resolve_ambiguous_duplicate_simple_name() -> None:
    types = [
        TypeRef(kind="class", name="Helper", qualified_name="pkg.a.Helper", package="pkg.a"),
        TypeRef(kind="class", name="Helper", qualified_name="pkg.b.Helper", package="pkg.b"),
    ]
    candidate, confidence = resolve_type_name(
        "Helper",
        package="pkg.c",
        imports={},
        by_qname={t.qualified_name: t for t in types},
        by_simple={"Helper": types},
    )
    assert confidence == "ambiguous"
    assert candidate is None


def test_interface_extends_edges() -> None:
    source = """
package com.example.api;
public interface AdminApi extends UserApi {}
"""
    result = parse_java_source(source, relative_path="com/example/api/AdminApi.java")
    assert result.ok
    assert any(
        r.relation_kind == "extends" and r.raw_target == "UserApi" for r in result.relations
    )
