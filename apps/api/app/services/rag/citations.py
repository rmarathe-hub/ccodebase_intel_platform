"""Citation extraction + post-validation against retrieved evidence spans."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from uuid import UUID

from app.models import Chunk
from app.services.rag.context_expand import ContextUnit

# path:start-end or path:line (single line). Paths may include dirs and dots.
_CITATION_RE = re.compile(
    r"(?P<path>[A-Za-z0-9_./\-]+\.[A-Za-z0-9]+):(?P<start>\d+)(?:-(?P<end>\d+))?"
)


@dataclass(frozen=True, slots=True)
class CitationRef:
    path: str
    start_line: int
    end_line: int
    raw: str
    chunk_id: UUID | None = None
    valid: bool = False
    reason: str = ""


@dataclass(frozen=True, slots=True)
class CitationValidationResult:
    citations: tuple[CitationRef, ...]
    valid_citations: tuple[CitationRef, ...]
    dropped: tuple[CitationRef, ...]
    ok: bool
    errors: tuple[str, ...] = field(default_factory=tuple)


def citation_key(path: str, start_line: int, end_line: int) -> str:
    return f"{path}:{start_line}-{end_line}"


def parse_citations(text: str) -> list[CitationRef]:
    """Extract citation refs from free text (order preserved, deduped)."""
    out: list[CitationRef] = []
    seen: set[str] = set()
    for match in _CITATION_RE.finditer(text or ""):
        path = match.group("path")
        start = int(match.group("start"))
        end_raw = match.group("end")
        end = int(end_raw) if end_raw is not None else start
        if end < start:
            start, end = end, start
        raw = match.group(0)
        key = citation_key(path, start, end)
        if key in seen:
            continue
        seen.add(key)
        out.append(
            CitationRef(
                path=path,
                start_line=start,
                end_line=end,
                raw=raw,
            )
        )
    return out


def _span_covered_by_chunk(chunk: Chunk, start: int, end: int) -> bool:
    """True when [start, end] is fully inside the chunk's parser span."""
    return chunk.start_line <= start <= end <= chunk.end_line


def _span_covered_by_path_union(
    same_path: list[Chunk], start: int, end: int
) -> bool:
    """True when every line in [start, end] is covered by some same-path chunk."""
    if not same_path or end < start:
        return False
    for line in range(start, end + 1):
        if not any(c.start_line <= line <= c.end_line for c in same_path):
            return False
    return True


def _matching_chunk(
    evidence: list[Chunk],
    *,
    path: str,
    start: int,
    end: int,
) -> Chunk | None:
    for chunk in evidence:
        if chunk.path != path:
            continue
        if _span_covered_by_chunk(chunk, start, end):
            return chunk
    # Allow citation that exactly matches a chunk span even if path casing differs.
    path_l = path.lower()
    same_path: list[Chunk] = []
    for chunk in evidence:
        if chunk.path.lower() != path_l:
            continue
        same_path.append(chunk)
        if _span_covered_by_chunk(chunk, start, end):
            return chunk
    # Exact-file aggregates may cite a multi-chunk union span.
    if _span_covered_by_path_union(same_path, start, end):
        return min(same_path, key=lambda c: (c.start_line, c.end_line, str(c.id)))
    return None


def evidence_chunks_from_units(units: tuple[ContextUnit, ...] | list[ContextUnit]) -> list[Chunk]:
    seen: set[UUID] = set()
    out: list[Chunk] = []
    for unit in units:
        if unit.chunk.id in seen:
            continue
        seen.add(unit.chunk.id)
        out.append(unit.chunk)
    return out


def validate_citations(
    text: str,
    *,
    evidence: list[Chunk],
    declared: list[CitationRef] | None = None,
) -> CitationValidationResult:
    """Validate citations against retrieved evidence only — never invent ranges."""
    refs = list(declared) if declared is not None else parse_citations(text)
    # Also merge any citations found in the answer body.
    if declared is not None:
        for extra in parse_citations(text):
            key = citation_key(extra.path, extra.start_line, extra.end_line)
            if not any(
                citation_key(r.path, r.start_line, r.end_line) == key for r in refs
            ):
                refs.append(extra)

    validated: list[CitationRef] = []
    dropped: list[CitationRef] = []
    errors: list[str] = []

    for ref in refs:
        if ref.start_line < 1 or ref.end_line < 1:
            bad = CitationRef(
                path=ref.path,
                start_line=ref.start_line,
                end_line=ref.end_line,
                raw=ref.raw,
                valid=False,
                reason="invalid_line_numbers",
            )
            dropped.append(bad)
            errors.append(f"{ref.raw}: invalid_line_numbers")
            continue
        match = _matching_chunk(
            evidence, path=ref.path, start=ref.start_line, end=ref.end_line
        )
        if match is None:
            bad = CitationRef(
                path=ref.path,
                start_line=ref.start_line,
                end_line=ref.end_line,
                raw=ref.raw,
                valid=False,
                reason="not_in_evidence",
            )
            dropped.append(bad)
            errors.append(f"{ref.raw}: not_in_evidence")
            continue
        good = CitationRef(
            path=match.path,
            start_line=ref.start_line,
            end_line=ref.end_line,
            raw=citation_key(match.path, ref.start_line, ref.end_line),
            chunk_id=match.id,
            valid=True,
            reason="ok",
        )
        validated.append(good)

    ok = len(dropped) == 0 and (len(validated) > 0 or not refs)
    return CitationValidationResult(
        citations=tuple(validated + dropped),
        valid_citations=tuple(validated),
        dropped=tuple(dropped),
        ok=ok,
        errors=tuple(errors),
    )


def scrub_invalid_citations(text: str, dropped: tuple[CitationRef, ...]) -> str:
    """Remove invalid citation tokens from answer text."""
    out = text
    for ref in dropped:
        out = out.replace(ref.raw, "[citation removed]")
    return out
