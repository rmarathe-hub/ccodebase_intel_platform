"""Week 5 Days 3–4: JS/TS module resolution and framework metadata."""

from __future__ import annotations

from pathlib import Path

from app.services.js_ts_framework import detect_js_ts_framework_meta
from app.services.js_ts_imports import (
    PathAlias,
    apply_path_alias,
    load_tsconfig_paths,
    resolve_import_specifier,
)
from app.services.js_ts_parser import PARSER_VERSION, parse_js_ts_source


def test_parser_version_day34() -> None:
    assert PARSER_VERSION == "5.6-treesitter"


def test_relative_and_index_resolution() -> None:
    known = frozenset({"src.components.Icon", "src.utils", "src.utils.helpers"})
    rel = resolve_import_specifier(
        "./Icon",
        current_path="src/components/Button.tsx",
        known_modules=known,
    )
    assert rel.style == "relative"
    assert rel.is_local is True
    assert rel.resolved_module == "src.components.Icon"

    parent = resolve_import_specifier(
        "../utils",
        current_path="src/components/Button.tsx",
        known_modules=known,
    )
    assert parent.resolved_module == "src.utils"
    assert parent.is_local is True


def test_tsconfig_alias_resolution(tmp_path: Path) -> None:
    (tmp_path / "tsconfig.json").write_text(
        '{"compilerOptions":{"paths":{"@/*":["src/*"],"@lib/*":["lib/*"]}}}',
        encoding="utf-8",
    )
    aliases = load_tsconfig_paths(tmp_path)
    assert apply_path_alias("@/components/Button", aliases) == "src/components/Button"
    known = frozenset({"src.components.Button"})
    resolved = resolve_import_specifier(
        "@/components/Button",
        current_path="src/app.tsx",
        known_modules=known,
        path_aliases=aliases,
    )
    assert resolved.style == "alias"
    assert resolved.is_local is True
    assert resolved.resolved_module == "src.components.Button"


def test_parse_resolves_imports_and_reexports() -> None:
    known = frozenset({"app.lib.helper", "app.utils"})
    aliases = (PathAlias(pattern="@/*", target="app/*"),)
    source = """
import { helper as h } from "./lib/helper";
import Button from "@/ui/Button";
export { helper } from "./lib/helper";
export { default as Util } from "../utils";
"""
    # current app/main.ts → ./lib/helper → app.lib.helper
    result = parse_js_ts_source(
        source,
        relative_path="app/main.ts",
        known_modules=known | frozenset({"app.ui.Button"}),
        path_aliases=aliases,
    )
    assert result.ok
    imports = [s for s in result.symbols if s.kind == "import"]
    by_name = {s.name: s for s in imports}
    assert by_name["h"].import_style == "relative"
    assert by_name["h"].is_local_import is True
    assert by_name["h"].resolved_module and "helper" in by_name["h"].resolved_module
    assert by_name["Button"].import_style == "alias"
    assert by_name["Button"].is_local_import is True

    exports = [s for s in result.symbols if s.kind == "export"]
    assert any(e.resolved_module for e in exports)


def test_nestjs_and_express_framework_roles() -> None:
    nest = """
@Controller("users")
export class UsersController {
  @Get()
  list() { return []; }
}
@Injectable()
export class UsersService {}
"""
    result = parse_js_ts_source(nest, relative_path="users.controller.ts")
    assert result.ok
    by_name = {s.name: s for s in result.symbols}
    assert by_name["UsersController"].framework_role == "nestjs_controller"
    assert by_name["list"].framework_role == "nestjs_route"
    assert by_name["UsersService"].framework_role == "nestjs_service"

    express = """
function listUsers(req, res) { res.send([]); }
router.get("/users", listUsers);
"""
    result2 = parse_js_ts_source(express, relative_path="routes.js")
    assert result2.ok
    list_users = next(s for s in result2.symbols if s.name == "listUsers")
    assert list_users.framework_role == "express_route"
    assert list_users.framework_detail and "GET" in list_users.framework_detail


def test_nextjs_path_and_route_handlers() -> None:
    source = """
export async function GET() { return Response.json({}); }
export async function POST() { return Response.json({}); }
"""
    result = parse_js_ts_source(source, relative_path="app/api/users/route.ts")
    assert result.ok
    roles = {s.name: s.framework_role for s in result.symbols if s.kind == "function"}
    assert roles.get("GET") == "nextjs_route"
    assert roles.get("POST") == "nextjs_route"

    page = """
export default function HomePage() { return null; }
"""
    result2 = parse_js_ts_source(page, relative_path="app/(marketing)/page.tsx")
    assert result2.ok
    home = next(s for s in result2.symbols if s.name == "HomePage")
    assert home.framework_role == "nextjs_page"


def test_framework_detector_unit() -> None:
    meta = detect_js_ts_framework_meta(
        kind="class",
        name="UsersController",
        decorators=("@Controller('users')",),
        relative_path="x.ts",
    )
    assert meta is not None
    assert meta.role == "nestjs_controller"
