"""Week 5 Day 6 — offline js_ts_deep fixture matrix."""

from __future__ import annotations

from pathlib import Path

from app.services.discovery import discover_repository
from app.services.js_ts_calls import SymbolRef, extract_js_ts_calls, module_from_qname
from app.services.js_ts_imports import load_tsconfig_paths, path_to_module
from app.services.js_ts_parser import parse_js_ts_source

FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "js_ts_deep"


def _known_modules() -> frozenset[str]:
    return frozenset(
        path_to_module(p.relative_to(FIXTURE_ROOT).as_posix())
        for p in FIXTURE_ROOT.rglob("*")
        if p.is_file() and p.suffix in {".ts", ".tsx", ".js", ".jsx"}
    )


def test_js_ts_deep_fixture_discovery_shape() -> None:
    result = discover_repository(FIXTURE_ROOT)
    paths = {f.path for f in result.files}
    assert "pkg/service.ts" in paths
    assert "ui/Badge.tsx" in paths
    assert "server/app.js" in paths
    assert "pages/index.tsx" in paths
    assert "pages/api/hello.ts" in paths
    assert "broken.ts" in paths
    assert result.deep_count >= 6


def test_js_ts_deep_fixture_symbols_and_framework() -> None:
    known = _known_modules()
    aliases = load_tsconfig_paths(FIXTURE_ROOT)

    service = parse_js_ts_source(
        (FIXTURE_ROOT / "pkg" / "service.ts").read_text(encoding="utf-8"),
        relative_path="pkg/service.ts",
        known_modules=known,
        path_aliases=aliases,
    )
    assert service.ok
    by_name = {s.name: s for s in service.symbols}
    assert by_name["Point"].kind == "interface"
    assert by_name["Size"].kind == "type_alias"
    assert by_name["helper"].kind == "function"
    assert by_name["fetchData"].is_async is True
    assert by_name["load"].kind == "function"
    assert by_name["load"].is_async is True
    assert by_name["util"].kind == "import"
    assert by_name["util"].is_local_import is True
    assert by_name["Greeter"].kind == "import"

    badge = parse_js_ts_source(
        (FIXTURE_ROOT / "ui" / "Badge.tsx").read_text(encoding="utf-8"),
        relative_path="ui/Badge.tsx",
        known_modules=known,
        path_aliases=aliases,
    )
    assert badge.ok
    b = {s.name: s for s in badge.symbols}
    assert b["Badge"].framework_role == "react_component"
    assert b["HomePage"].framework_role == "react_component"
    assert b["Props"].kind == "interface"

    express = parse_js_ts_source(
        (FIXTURE_ROOT / "server" / "app.js").read_text(encoding="utf-8"),
        relative_path="server/app.js",
        known_modules=known,
        path_aliases=aliases,
    )
    assert express.ok
    assert any(s.framework_role == "express_route" for s in express.symbols)

    page = parse_js_ts_source(
        (FIXTURE_ROOT / "pages" / "index.tsx").read_text(encoding="utf-8"),
        relative_path="pages/index.tsx",
        known_modules=known,
        path_aliases=aliases,
    )
    assert page.ok
    assert any(s.framework_role == "nextjs_page" for s in page.symbols)

    api = parse_js_ts_source(
        (FIXTURE_ROOT / "pages" / "api" / "hello.ts").read_text(encoding="utf-8"),
        relative_path="pages/api/hello.ts",
        known_modules=known,
        path_aliases=aliases,
    )
    assert api.ok
    assert any(s.framework_role == "nextjs_route" for s in api.symbols)

    greeter = parse_js_ts_source(
        (FIXTURE_ROOT / "pkg" / "greeter.ts").read_text(encoding="utf-8"),
        relative_path="pkg/greeter.ts",
        known_modules=known,
        path_aliases=aliases,
    )
    assert greeter.ok
    assert any(s.name == "Greeter" and s.kind == "class" for s in greeter.symbols)
    # Duplicate leaf name across modules
    assert any(s.name == "helper" and s.kind == "function" for s in greeter.symbols)
    assert any(s.name == "helper" and s.kind == "function" for s in service.symbols)


def test_js_ts_deep_fixture_calls() -> None:
    known = _known_modules()
    aliases = load_tsconfig_paths(FIXTURE_ROOT)
    paths = (
        "pkg/helpers.ts",
        "pkg/greeter.ts",
        "pkg/service.ts",
        "ui/Badge.tsx",
        "server/app.js",
    )
    refs: list[SymbolRef] = []
    texts: dict[str, str] = {}
    for rel in paths:
        text = (FIXTURE_ROOT / rel).read_text(encoding="utf-8")
        texts[rel] = text
        parsed = parse_js_ts_source(
            text,
            relative_path=rel,
            known_modules=known,
            path_aliases=aliases,
        )
        assert parsed.ok
        for s in parsed.symbols:
            refs.append(
                SymbolRef(
                    kind=s.kind,
                    name=s.name,
                    qualified_name=s.qualified_name,
                    module=module_from_qname(s.qualified_name, s.kind, s.name),
                    resolved_module=s.resolved_module,
                )
            )

    calls = extract_js_ts_calls(
        texts["pkg/service.ts"], relative_path="pkg/service.ts", symbols=refs
    )
    assert calls
    util_calls = [c for c in calls if c.raw_callee == "util"]
    assert util_calls
    assert util_calls[0].candidate_qualified_name == "pkg.helpers.util"
    assert util_calls[0].confidence == "resolved"

    this_calls = [c for c in calls if c.raw_callee.startswith("this.")]
    assert this_calls
    assert this_calls[0].confidence == "resolved"

    greeter_calls = [c for c in calls if c.raw_callee == "Greeter.hello"]
    assert greeter_calls
    assert greeter_calls[0].candidate_qualified_name == "pkg.greeter.Greeter.hello"
    assert greeter_calls[0].confidence == "resolved"

    unresolved = [c for c in calls if c.raw_callee == "unknownThing"]
    assert unresolved
    assert unresolved[0].confidence == "unresolved"

    assert any(
        c.caller_qualified_name and c.caller_qualified_name.endswith(".load")
        for c in calls
    )
    assert any(
        c.caller_qualified_name and c.caller_qualified_name.endswith(".fetchData")
        for c in calls
    )


def test_js_ts_deep_syntax_error_file_fails_closed() -> None:
    broken = (FIXTURE_ROOT / "broken.ts").read_text(encoding="utf-8")
    result = parse_js_ts_source(broken, relative_path="broken.ts")
    assert result.ok is False
    assert result.symbols == ()
