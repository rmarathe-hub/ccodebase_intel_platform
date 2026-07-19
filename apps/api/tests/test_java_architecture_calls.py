"""Spring architecture classification + Java call extraction (Days 5–6)."""

from __future__ import annotations

from pathlib import Path

from app.services.java_calls import SymbolRef, extract_java_calls, module_from_qname
from app.services.java_framework import (
    ArchitectureSymbol,
    classify_spring_architecture,
)
from app.services.java_parser import PARSER_VERSION, parse_java_source

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "java_deep"


def test_parser_version_day56() -> None:
    assert PARSER_VERSION == "6.6-treesitter"


def test_architecture_marks_interface_and_implements_detail() -> None:
    updates = classify_spring_architecture(
        [
            ArchitectureSymbol(
                kind="interface",
                name="UserApi",
                qualified_name="com.example.users.api.UserApi",
                framework_role=None,
                framework_detail=None,
            ),
            ArchitectureSymbol(
                kind="class",
                name="UserService",
                qualified_name="com.example.users.UserService",
                framework_role="spring_service",
                framework_detail="@Service",
            ),
            ArchitectureSymbol(
                kind="class",
                name="BillingServiceImpl",
                qualified_name="com.example.billing.BillingServiceImpl",
                framework_role=None,
                framework_detail=None,
            ),
        ],
        implements_edges=[
            ("com.example.users.UserService", "com.example.users.api.UserApi"),
            (
                "com.example.billing.BillingServiceImpl",
                "com.example.billing.BillingService",
            ),
        ],
    )
    assert updates["com.example.users.api.UserApi"].role == "spring_interface"
    assert "implemented_by:" in (updates["com.example.users.api.UserApi"].detail or "")
    assert updates["com.example.users.UserService"].role == "spring_service"
    assert "implements:com.example.users.api.UserApi" in (
        updates["com.example.users.UserService"].detail or ""
    )
    assert updates["com.example.billing.BillingServiceImpl"].role == "spring_implementation"


def test_fixture_service_has_architecture_and_calls() -> None:
    known_paths = [
        "com/example/users/UserService.java",
        "com/example/users/UserRepository.java",
        "com/example/users/api/UserApi.java",
    ]
    refs: list[SymbolRef] = []
    import_map: dict[str, str] = {}
    service_text = ""
    for rel in known_paths:
        text = (FIXTURE / rel).read_text(encoding="utf-8")
        parsed = parse_java_source(text, relative_path=rel)
        assert parsed.ok
        if rel.endswith("UserService.java"):
            service_text = text
            import_map = dict(parsed.import_map)
            svc = next(s for s in parsed.symbols if s.name == "UserService")
            assert svc.framework_role == "spring_service"
        for s in parsed.symbols:
            refs.append(
                SymbolRef(
                    kind=s.kind,
                    name=s.name,
                    qualified_name=s.qualified_name,
                    module=module_from_qname(s.qualified_name, s.kind, s.name),
                    resolved_module=s.resolved_module,
                    return_annotation=s.return_annotation,
                )
            )

    calls = extract_java_calls(
        service_text,
        relative_path="com/example/users/UserService.java",
        symbols=refs,
        import_map=import_map,
        interface_impls={
            "com.example.users.api.UserApi": ["com.example.users.UserService"]
        },
    )
    assert calls
    helper = [c for c in calls if c.raw_callee in {"helper", "this.helper"}]
    assert helper
    assert all(c.confidence == "resolved" for c in helper)
    assert all(
        c.candidate_qualified_name == "com.example.users.UserService.helper"
        for c in helper
    )

    repo_calls = [c for c in calls if "findById" in c.raw_callee]
    assert repo_calls
    assert repo_calls[0].confidence == "resolved"
    assert (
        repo_calls[0].candidate_qualified_name
        == "com.example.users.UserRepository.findById"
    )


def test_unresolved_external_call() -> None:
    source = """
package demo;
public class Main {
  public void run() { unknownThing(); }
}
"""
    parsed = parse_java_source(source, relative_path="demo/Main.java")
    refs = [
        SymbolRef(
            kind=s.kind,
            name=s.name,
            qualified_name=s.qualified_name,
            module=module_from_qname(s.qualified_name, s.kind, s.name),
            resolved_module=s.resolved_module,
            return_annotation=s.return_annotation,
        )
        for s in parsed.symbols
    ]
    calls = extract_java_calls(source, relative_path="demo/Main.java", symbols=refs)
    assert calls[0].confidence == "unresolved"
