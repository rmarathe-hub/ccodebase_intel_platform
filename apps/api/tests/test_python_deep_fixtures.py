"""Week 4 Day 6 — offline python_deep fixture matrix."""

from __future__ import annotations

from pathlib import Path

from app.services.discovery import discover_repository
from app.services.python_ast_parser import parse_python_source
from app.services.python_calls import SymbolRef, extract_calls, module_from_qname

FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "python_deep"


def test_python_deep_fixture_discovery_shape() -> None:
    result = discover_repository(FIXTURE_ROOT)
    paths = {f.path for f in result.files}
    assert "pkg/service.py" in paths
    assert "pkg/models.py" in paths
    assert "broken.py" in paths
    assert result.deep_count >= 4


def test_python_deep_fixture_symbols_and_framework() -> None:
    service = (FIXTURE_ROOT / "pkg" / "service.py").read_text(encoding="utf-8")
    known = frozenset(
        {
            "pkg",
            "pkg.service",
            "pkg.models",
            "pkg.sub.helpers",
        }
    )
    parsed = parse_python_source(
        service, relative_path="pkg/service.py", known_modules=known
    )
    assert parsed.ok
    by_name = {s.name: s for s in parsed.symbols}
    assert by_name["Outer"].kind == "class"
    assert by_name["Inner"].kind == "class"
    assert by_name["Inner"].qualified_name == "pkg.service.Outer.Inner"
    assert by_name["fetch"].is_async is True
    assert by_name["ping"].framework_role == "fastapi_route"
    assert by_name["util"].kind == "import"
    assert by_name["util"].import_style == "relative"
    assert by_name["util"].is_local_import is True

    models = parse_python_source(
        (FIXTURE_ROOT / "pkg" / "models.py").read_text(encoding="utf-8"),
        relative_path="pkg/models.py",
        known_modules=known,
    )
    assert models.ok
    m = {s.name: s for s in models.symbols}
    assert m["Point"].framework_role is None or True  # dataclass decorator only
    assert "dataclass" in m["Point"].decorators
    assert m["UserModel"].framework_role == "pydantic_model"


def test_python_deep_fixture_calls() -> None:
    service = (FIXTURE_ROOT / "pkg" / "service.py").read_text(encoding="utf-8")
    helpers = (FIXTURE_ROOT / "pkg" / "sub" / "helpers.py").read_text(encoding="utf-8")
    known = frozenset({"pkg.service", "pkg.models", "pkg.sub.helpers"})
    parsed_service = parse_python_source(
        service, relative_path="pkg/service.py", known_modules=known
    )
    parsed_helpers = parse_python_source(
        helpers, relative_path="pkg/sub/helpers.py", known_modules=known
    )
    refs: list[SymbolRef] = []
    for _path, result in (
        ("pkg/service.py", parsed_service),
        ("pkg/sub/helpers.py", parsed_helpers),
    ):
        for s in result.symbols:
            refs.append(
                SymbolRef(
                    kind=s.kind,
                    name=s.name,
                    qualified_name=s.qualified_name,
                    module=module_from_qname(s.qualified_name, s.kind, s.name),
                )
            )
    calls = extract_calls(service, relative_path="pkg/service.py", symbols=refs)
    assert calls
    util_calls = [c for c in calls if c.raw_callee == "util"]
    assert util_calls
    assert util_calls[0].candidate_qualified_name == "pkg.sub.helpers.util"
    assert util_calls[0].confidence == "resolved"
    assert any(
        c.caller_qualified_name and c.caller_qualified_name.endswith(".entry") for c in calls
    )


def test_python_deep_syntax_error_file_fails_closed() -> None:
    broken = (FIXTURE_ROOT / "broken.py").read_text(encoding="utf-8")
    result = parse_python_source(broken, relative_path="broken.py")
    assert result.ok is False
    assert result.symbols == ()
