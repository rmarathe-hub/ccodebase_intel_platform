"""Java tree-sitter parser — Days 1–2 extraction and qualified names."""

from __future__ import annotations

from pathlib import Path

from app.services.java_parser import (
    PARSER_NAME,
    PARSER_VERSION,
    parse_java_source,
    path_fallback_package,
    qualify,
)

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "java_deep"


def test_parser_stamps() -> None:
    assert PARSER_NAME == "java-treesitter"
    assert PARSER_VERSION == "6.2-treesitter"


def test_qualify_and_path_fallback() -> None:
    assert qualify("com.example", "AuthService", "login") == "com.example.AuthService.login"
    assert path_fallback_package("util/FallbackHelper.java") == "util"
    assert path_fallback_package("FallbackHelper.java") == ""


def test_extract_class_methods_fields_constructor() -> None:
    source = (FIXTURE / "com/example/auth/AuthService.java").read_text(encoding="utf-8")
    result = parse_java_source(
        source, relative_path="com/example/auth/AuthService.java"
    )
    assert result.ok
    assert result.parser_name == PARSER_NAME
    assert result.language == "java"
    by_q = {s.qualified_name: s for s in result.symbols}

    assert by_q["com.example.auth"].kind == "package"
    assert by_q["com.example.auth.AuthService"].kind == "class"
    assert by_q["com.example.auth.AuthService.login"].kind == "method"
    assert by_q["com.example.auth.AuthService.login"].return_annotation == "boolean"
    login_params = by_q["com.example.auth.AuthService.login"].parameters
    assert [p.name for p in login_params] == ["user", "password"]
    assert login_params[0].annotation == "String"

    assert by_q["com.example.auth.AuthService.AuthService"].kind == "constructor"
    assert by_q["com.example.auth.AuthService.users"].kind == "field"
    assert by_q["com.example.auth.AuthService.users"].return_annotation == "UserRepository"
    assert by_q["com.example.auth.AuthService.identity"].kind == "method"
    assert by_q["com.example.auth.AuthService.identity"].return_annotation == "R"

    imports = [s for s in result.symbols if s.kind == "import"]
    assert any(s.name == "List" and s.resolved_module == "java.util.List" for s in imports)
    assert any(
        s.name == "User" and s.qualified_name == "com.example.users.User" for s in imports
    )


def test_extract_interface_enum_record() -> None:
    iface = parse_java_source(
        (FIXTURE / "com/example/auth/AuthApi.java").read_text(encoding="utf-8"),
        relative_path="com/example/auth/AuthApi.java",
    )
    assert iface.ok
    assert any(
        s.kind == "interface" and s.qualified_name == "com.example.auth.AuthApi"
        for s in iface.symbols
    )
    assert any(
        s.kind == "method" and s.qualified_name == "com.example.auth.AuthApi.login"
        for s in iface.symbols
    )

    enum = parse_java_source(
        (FIXTURE / "com/example/auth/Role.java").read_text(encoding="utf-8"),
        relative_path="com/example/auth/Role.java",
    )
    assert enum.ok
    assert any(s.kind == "enum" and s.name == "Role" for s in enum.symbols)
    assert any(
        s.kind == "enum_constant" and s.qualified_name == "com.example.auth.Role.ADMIN"
        for s in enum.symbols
    )

    record = parse_java_source(
        (FIXTURE / "com/example/auth/Point.java").read_text(encoding="utf-8"),
        relative_path="com/example/auth/Point.java",
    )
    assert record.ok
    point = next(s for s in record.symbols if s.kind == "record")
    assert point.qualified_name == "com.example.auth.Point"
    assert [p.name for p in point.parameters] == ["x", "y"]
    assert point.parameters[0].annotation == "int"


def test_path_fallback_when_no_package() -> None:
    source = (FIXTURE / "util/FallbackHelper.java").read_text(encoding="utf-8")
    result = parse_java_source(source, relative_path="util/FallbackHelper.java")
    assert result.ok
    assert any(
        s.kind == "class" and s.qualified_name == "util.FallbackHelper" for s in result.symbols
    )
    assert any(
        s.kind == "method" and s.qualified_name == "util.FallbackHelper.add"
        for s in result.symbols
    )


def test_syntax_error_fails_closed() -> None:
    broken = (FIXTURE / "Broken.java").read_text(encoding="utf-8")
    result = parse_java_source(broken, relative_path="Broken.java")
    assert result.ok is False
    assert result.symbols == ()
    assert result.parser_name is None
