"""Format-native configuration chunking (no regex structure)."""

from __future__ import annotations

import json
import tomllib
from io import StringIO
from pathlib import Path
from xml.sax import ContentHandler, handler
from xml.sax.xmlreader import InputSource

import defusedxml.sax
import yaml
from dockerfile_parse import DockerfileParser
from yaml.nodes import MappingNode, ScalarNode

from app.core.language_contract import SupportLevel
from app.services.chunking.types import ExtractedChunk

PARSER_VERSION = "7.3-config"


def physical_line_count(source: str) -> int:
    """Match discovery.count_lines: newline separators, 1-based physical lines."""
    if not source:
        return 0
    return source.count("\n") + (0 if source.endswith("\n") else 1)


def physical_lines(source: str) -> list[str]:
    """Split into physical lines without dropping a trailing blank line.

    ``str.splitlines()`` drops a final empty line when the source ends with a
    newline; that breaks 1-based coverage for files that end with ``}\\n\\n``.
    """
    if not source:
        return []
    parts = source.split("\n")
    if source.endswith("\n") and parts:
        parts = parts[:-1]
    return parts


def _slice(source: str, start_line: int, end_line: int) -> str:
    lines = physical_lines(source)
    return "\n".join(lines[start_line - 1 : end_line])


def _chunk(
    *,
    path: str,
    start_line: int,
    end_line: int,
    source: str,
    parent_context: str,
    parser_name: str,
    metadata: str,
) -> ExtractedChunk:
    return ExtractedChunk.make(
        path=path,
        language="configuration",
        support_level=SupportLevel.GENERIC.value,
        chunk_type="configuration_section",
        start_line=start_line,
        end_line=end_line,
        content=_slice(source, start_line, end_line),
        parent_context=parent_context,
        extraction_method="format_native",
        parser_name=parser_name,
        parser_version=PARSER_VERSION,
        verified_deep=False,
        metadata_json=metadata,
    )


def _top_level_json_key_spans(source: str) -> list[tuple[str, int, int]]:
    """Brace-depth scanner after json.loads validation — not regex."""
    data = json.loads(source)
    total = max(1, physical_line_count(source))
    if not isinstance(data, dict):
        return [("__root__", 1, total)]

    def line_at(pos: int) -> int:
        return source.count("\n", 0, pos) + 1

    keys_order = list(data.keys())
    spans: list[tuple[str, int, int]] = []
    i = 0
    n = len(source)
    while i < n and source[i] != "{":
        i += 1
    if i >= n:
        return []
    i += 1
    depth = 1
    in_str = False
    escape = False
    key_idx = 0
    pending_key: str | None = None
    current_start: int | None = None

    while i < n:
        ch = source[i]
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
            i += 1
            continue
        if ch == '"':
            if depth == 1 and key_idx < len(keys_order):
                j = i + 1
                buf: list[str] = []
                while j < n:
                    c = source[j]
                    if c == "\\" and j + 1 < n:
                        buf.append(source[j + 1])
                        j += 2
                        continue
                    if c == '"':
                        break
                    buf.append(c)
                    j += 1
                key = "".join(buf)
                k = j + 1
                while k < n and source[k] in " \t\n\r":
                    k += 1
                if k < n and source[k] == ":" and key == keys_order[key_idx]:
                    if pending_key is not None and current_start is not None:
                        end_line = max(current_start, line_at(i) - 1)
                        spans.append((pending_key, current_start, end_line))
                    pending_key = key
                    # First key always starts at line 1 so opening `{` and any
                    # blank preamble are never dropped (off-by-one / first-line loss).
                    current_start = 1 if key_idx == 0 else line_at(i)
                    key_idx += 1
            in_str = True
            i += 1
            continue
        if ch in "{[":
            depth += 1
        elif ch in "}]":
            depth -= 1
            if depth == 0:
                if pending_key is not None and current_start is not None:
                    spans.append((pending_key, current_start, max(line_at(i), total)))
                break
        i += 1
    if spans:
        k0, _s0, e0 = spans[0]
        spans[0] = (k0, 1, e0)
        kN, sN, _eN = spans[-1]
        spans[-1] = (kN, sN, max(spans[-1][2], total))
    return spans


def chunk_json_source(*, source: str, path: str) -> list[ExtractedChunk]:
    try:
        spans = _top_level_json_key_spans(source)
    except json.JSONDecodeError:
        return []
    return [
        _chunk(
            path=path,
            start_line=start,
            end_line=end,
            source=source,
            parent_context=key,
            parser_name="json-stdlib",
            metadata=f'{{"key":{json.dumps(key)}}}',
        )
        for key, start, end in spans
        if end >= start
    ]


def _yaml_mapping_chunks(
    node: MappingNode,
    *,
    source: str,
    path: str,
    parent: str | None,
    nest_children_for: frozenset[str],
) -> list[ExtractedChunk]:
    out: list[ExtractedChunk] = []
    for key_node, value_node in node.value:
        if not isinstance(key_node, ScalarNode):
            continue
        key = str(key_node.value)
        start = key_node.start_mark.line + 1
        end = value_node.end_mark.line + 1
        ctx = f"{parent}.{key}" if parent else key
        out.append(
            _chunk(
                path=path,
                start_line=start,
                end_line=end,
                source=source,
                parent_context=ctx,
                parser_name="yaml-compose",
                metadata=f'{{"key":{json.dumps(ctx)}}}',
            )
        )
        if key in nest_children_for and isinstance(value_node, MappingNode):
            out.extend(
                _yaml_mapping_chunks(
                    value_node,
                    source=source,
                    path=path,
                    parent=ctx,
                    nest_children_for=frozenset(),
                )
            )
    return out


def chunk_yaml_source(*, source: str, path: str) -> list[ExtractedChunk]:
    try:
        root = yaml.compose(source)
    except yaml.YAMLError:
        return []
    if root is None:
        return []
    if isinstance(root, MappingNode):
        return _yaml_mapping_chunks(
            root,
            source=source,
            path=path,
            parent=None,
            nest_children_for=frozenset({"services", "jobs", "on"}),
        )
    start = root.start_mark.line + 1
    end = root.end_mark.line + 1
    return [
        _chunk(
            path=path,
            start_line=start,
            end_line=end,
            source=source,
            parent_context="__root__",
            parser_name="yaml-compose",
            metadata='{"key":"__root__"}',
        )
    ]


def chunk_toml_source(*, source: str, path: str) -> list[ExtractedChunk]:
    try:
        data = tomllib.loads(source)
    except tomllib.TOMLDecodeError:
        return []
    if not isinstance(data, dict) or not data:
        return []

    lines = source.splitlines()
    # Section headers: lines that are exactly [table] / [[array]] after strip.
    headers: list[tuple[str, int]] = []
    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("[[") and stripped.endswith("]]"):
            name = stripped[2:-2].strip()
            headers.append((name, i))
        elif stripped.startswith("[") and stripped.endswith("]"):
            name = stripped[1:-1].strip()
            headers.append((name, i))

    chunks: list[ExtractedChunk] = []
    if headers:
        for idx, (name, start) in enumerate(headers):
            end = headers[idx + 1][1] - 1 if idx + 1 < len(headers) else len(lines)
            if end < start:
                end = start
            chunks.append(
                _chunk(
                    path=path,
                    start_line=start,
                    end_line=end,
                    source=source,
                    parent_context=name,
                    parser_name="tomllib",
                    metadata=f'{{"table":{json.dumps(name)}}}',
                )
            )
        return chunks

    # No tables — one chunk per top-level key via full-file spans (key order from parse).
    # Map each key to first line that starts with `key` then `=` (string prefix scan).
    for key in data:
        prefix = f"{key}"
        start = 1
        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith(prefix):
                rest = stripped[len(prefix) :].lstrip()
                if rest.startswith("="):
                    start = i
                    break
        chunks.append(
            _chunk(
                path=path,
                start_line=start,
                end_line=len(lines) or 1,
                source=source,
                parent_context=key,
                parser_name="tomllib",
                metadata=f'{{"key":{json.dumps(key)}}}',
            )
        )
    return chunks


class _TopLevelXmlHandler(ContentHandler):
    def __init__(self) -> None:
        super().__init__()
        self.depth = 0
        self.spans: list[tuple[str, int, int]] = []
        self._stack: list[tuple[str, int]] = []
        self._locator: handler.Locator | None = None

    def setDocumentLocator(self, locator: handler.Locator) -> None:
        self._locator = locator

    def startElement(self, name: str, attrs: handler.Attributes) -> None:  # type: ignore[override]
        line = self._locator.getLineNumber() if self._locator else 1
        self.depth += 1
        if self.depth == 2:
            self._stack.append((name, line))

    def endElement(self, name: str) -> None:
        if self.depth == 2 and self._stack:
            start_name, start_line = self._stack.pop()
            end_line = self._locator.getLineNumber() if self._locator else start_line
            self.spans.append((start_name, start_line, end_line))
        self.depth -= 1


def chunk_xml_source(*, source: str, path: str) -> list[ExtractedChunk]:
    handler_obj = _TopLevelXmlHandler()
    parser = defusedxml.sax.make_parser()
    parser.setContentHandler(handler_obj)
    try:
        stream = StringIO(source)
        input_source = InputSource()
        input_source.setByteStream(stream)  # type: ignore[arg-type]
        input_source.setCharacterStream(stream)
        parser.parse(input_source)
    except Exception:
        return []
    return [
        _chunk(
            path=path,
            start_line=start,
            end_line=end,
            source=source,
            parent_context=name,
            parser_name="defusedxml-sax",
            metadata=f'{{"element":{json.dumps(name)}}}',
        )
        for name, start, end in handler_obj.spans
        if end >= start
    ]


def chunk_dockerfile_source(*, source: str, path: str) -> list[ExtractedChunk]:
    try:
        df = DockerfileParser(fileobj=StringIO(source))
        structure = list(df.structure or [])
    except Exception:
        return []
    if not structure:
        return []

    chunks: list[ExtractedChunk] = []
    stage_start: int | None = None
    stage_name = "stage0"
    stage_idx = 0
    for entry in structure:
        instr = str(entry.get("instruction", "")).upper()
        start = int(entry["startline"]) + 1
        end = int(entry["endline"]) + 1
        if instr == "FROM":
            if stage_start is not None:
                chunks.append(
                    _chunk(
                        path=path,
                        start_line=stage_start,
                        end_line=start - 1 if start > stage_start else stage_start,
                        source=source,
                        parent_context=stage_name,
                        parser_name="dockerfile-parse",
                        metadata=f'{{"stage":{json.dumps(stage_name)}}}',
                    )
                )
            value = str(entry.get("value", ""))
            value_upper = value.upper()
            as_token = " AS "
            if as_token in value_upper:
                idx = value_upper.rfind(as_token)
                stage_name = value[idx + len(as_token) :].strip() or f"stage{stage_idx}"
            else:
                stage_name = f"stage{stage_idx}"
            stage_start = start
            stage_idx += 1
        last_end = end
    if stage_start is not None:
        chunks.append(
            _chunk(
                path=path,
                start_line=stage_start,
                end_line=last_end,
                source=source,
                parent_context=stage_name,
                parser_name="dockerfile-parse",
                metadata=f'{{"stage":{json.dumps(stage_name)}}}',
            )
        )
    return chunks


def chunk_configuration_file(*, source: str, path: str) -> list[ExtractedChunk]:
    name = Path(path).name.lower()
    suffix = Path(path).suffix.lower()

    if name == "dockerfile" or name.startswith("dockerfile."):
        chunks = chunk_dockerfile_source(source=source, path=path)
    elif name in {"go.mod", "go.sum"}:
        end = max(1, physical_line_count(source) or 1)
        chunks = [
            _chunk(
                path=path,
                start_line=1,
                end_line=end,
                source=source,
                parent_context=name,
                parser_name="go-mod",
                metadata="{}",
            )
        ]
    elif suffix == ".json":
        chunks = chunk_json_source(source=source, path=path)
    elif suffix in {".yaml", ".yml"}:
        chunks = chunk_yaml_source(source=source, path=path)
    elif suffix == ".toml":
        chunks = chunk_toml_source(source=source, path=path)
    elif suffix == ".xml":
        chunks = chunk_xml_source(source=source, path=path)
    else:
        chunks = []

    # Whole-file fallback when format parsers yield nothing but file has text.
    if not chunks and source.strip():
        end = max(1, physical_line_count(source) or 1)
        return [
            _chunk(
                path=path,
                start_line=1,
                end_line=end,
                source=source,
                parent_context="__file__",
                parser_name="config-whole-file",
                metadata='{"fallback":"whole_file"}',
            )
        ]
    return chunks
