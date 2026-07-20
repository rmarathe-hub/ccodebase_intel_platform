"""Tree-sitter generic structural chunks (not verified deep)."""

from __future__ import annotations

from dataclasses import dataclass

from tree_sitter import Language, Node, Parser

# Import grammars; package names vary slightly.
import tree_sitter_bash as ts_bash
import tree_sitter_c as ts_c
import tree_sitter_cpp as ts_cpp
import tree_sitter_c_sharp as ts_csharp
import tree_sitter_go as ts_go
import tree_sitter_ruby as ts_ruby
import tree_sitter_rust as ts_rust

from app.core.language_contract import SupportLevel
from app.services.chunking.types import ExtractedChunk

PARSER_VERSION = "7.2-treesitter"
MAX_NODE_CHARS = 12_000


@dataclass(frozen=True, slots=True)
class _LangSpec:
    language_key: str
    parser_name: str
    language: Language
    node_types: frozenset[str]


def _spec(
    language_key: str,
    parser_name: str,
    lang_mod: object,
    node_types: set[str],
) -> _LangSpec:
    return _LangSpec(
        language_key=language_key,
        parser_name=parser_name,
        language=Language(lang_mod.language()),  # type: ignore[attr-defined]
        node_types=frozenset(node_types),
    )


SPECS: dict[str, _LangSpec] = {
    "go": _spec(
        "go",
        "go-treesitter",
        ts_go,
        {
            "function_declaration",
            "method_declaration",
            "type_declaration",
            "const_declaration",
            "var_declaration",
        },
    ),
    "rust": _spec(
        "rust",
        "rust-treesitter",
        ts_rust,
        {
            "function_item",
            "impl_item",
            "struct_item",
            "enum_item",
            "trait_item",
            "mod_item",
            "type_item",
            "const_item",
        },
    ),
    "c": _spec(
        "c",
        "c-treesitter",
        ts_c,
        {
            "function_definition",
            "declaration",
            "struct_specifier",
            "enum_specifier",
            "type_definition",
        },
    ),
    "c++": _spec(
        "c++",
        "cpp-treesitter",
        ts_cpp,
        {
            "function_definition",
            "class_specifier",
            "struct_specifier",
            "enum_specifier",
            "namespace_definition",
            "declaration",
            "template_declaration",
        },
    ),
    "c#": _spec(
        "c#",
        "csharp-treesitter",
        ts_csharp,
        {
            "class_declaration",
            "struct_declaration",
            "interface_declaration",
            "enum_declaration",
            "method_declaration",
            "constructor_declaration",
            "namespace_declaration",
            "record_declaration",
        },
    ),
    "ruby": _spec(
        "ruby",
        "ruby-treesitter",
        ts_ruby,
        {
            "method",
            "singleton_method",
            "class",
            "module",
        },
    ),
    "shell": _spec(
        "shell",
        "bash-treesitter",
        ts_bash,
        {
            "function_definition",
        },
    ),
}


def supported_generic_languages() -> frozenset[str]:
    return frozenset(SPECS.keys()) | frozenset({"sql"})


def _line_slice(source: str, start_line: int, end_line: int) -> str:
    lines = source.splitlines()
    return "\n".join(lines[start_line - 1 : end_line])


def _emit_node(
    *,
    node: Node,
    source: str,
    source_bytes: bytes,
    path: str,
    spec: _LangSpec,
    parent_context: str | None,
) -> list[ExtractedChunk]:
    start_line = node.start_point[0] + 1
    end_line = node.end_point[0] + 1
    content = source_bytes[node.start_byte : node.end_byte].decode("utf-8", errors="replace")
    if len(content) <= MAX_NODE_CHARS:
        return [
            ExtractedChunk.make(
                path=path,
                language=spec.language_key,
                support_level=SupportLevel.GENERIC.value,
                chunk_type="generic_structure",
                start_line=start_line,
                end_line=end_line,
                content=content,
                parent_context=parent_context or node.type,
                extraction_method="treesitter_node",
                parser_name=spec.parser_name,
                parser_version=PARSER_VERSION,
                verified_deep=False,
                metadata_json=f'{{"node_type":"{node.type}"}}',
            )
        ]
    # Oversized: prefer child syntax nodes.
    child_chunks: list[ExtractedChunk] = []
    for child in node.children:
        if child.type in spec.node_types or child.is_named:
            if child.type in spec.node_types:
                child_chunks.extend(
                    _emit_node(
                        node=child,
                        source=source,
                        source_bytes=source_bytes,
                        path=path,
                        spec=spec,
                        parent_context=f"{parent_context or node.type}/{node.type}",
                    )
                )
    if child_chunks:
        return child_chunks
    # Final fallback: deterministic line windows (labeled).
    window = 80
    out: list[ExtractedChunk] = []
    for start in range(start_line, end_line + 1, window):
        end = min(start + window - 1, end_line)
        piece = _line_slice(source, start, end)
        out.append(
            ExtractedChunk.make(
                path=path,
                language=spec.language_key,
                support_level=SupportLevel.GENERIC.value,
                chunk_type="generic_structure",
                start_line=start,
                end_line=end,
                content=piece,
                parent_context=parent_context or node.type,
                extraction_method="line_window_fallback",
                parser_name=spec.parser_name,
                parser_version=PARSER_VERSION,
                verified_deep=False,
                metadata_json=f'{{"node_type":"{node.type}","fallback":true}}',
            )
        )
    return out


def chunk_generic_source(
    *,
    source: str,
    path: str,
    language: str,
) -> list[ExtractedChunk]:
    spec = SPECS.get(language)
    if spec is None:
        return []
    source_bytes = source.encode("utf-8")
    parser = Parser(spec.language)
    tree = parser.parse(source_bytes)
    root = tree.root_node
    if root.has_error and not root.children:
        return []
    chunks: list[ExtractedChunk] = []
    for child in root.children:
        if child.type in spec.node_types:
            chunks.extend(
                _emit_node(
                    node=child,
                    source=source,
                    source_bytes=source_bytes,
                    path=path,
                    spec=spec,
                    parent_context=None,
                )
            )
    # Nested declarations (e.g. C# methods inside classes): also walk one level deep.
    if not chunks:
        stack = list(root.children)
        while stack:
            node = stack.pop()
            if node.type in spec.node_types:
                chunks.extend(
                    _emit_node(
                        node=node,
                        source=source,
                        source_bytes=source_bytes,
                        path=path,
                        spec=spec,
                        parent_context=None,
                    )
                )
            else:
                stack.extend(node.children)
    return chunks
