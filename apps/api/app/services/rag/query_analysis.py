"""Week 10 Day 3: query classification + NL rewrite (≤4). Identifiers never paraphrased."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import StrEnum

from app.core.config import Settings, settings

# Strong identifier / path signals (do not paraphrase these tokens).
_IDENT_RE = re.compile(
    r"(?:"
    r"[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]+)+"  # PascalCase
    r"|[a-z][a-z0-9]*(?:_[a-z0-9]+)+"  # snake_case
    r"|[a-zA-Z_]\w*\.[a-zA-Z_]\w*"  # dotted
    r")"
)
_PATH_RE = re.compile(
    r"(?:^|[\s`\"'])([A-Za-z0-9_.\-]+(?:/[A-Za-z0-9_.\-]+)+\.[A-Za-z0-9]+)"
)
_FILE_EXT_RE = re.compile(
    r"(?:^|[\s`\"'])([A-Za-z0-9_\-]+\.(?:py|ts|tsx|js|jsx|java|go|rs|cs|cpp|c|h|rb|sh|sql|md|yml|yaml|toml|json))\b"
)
_QUESTION_RE = re.compile(
    r"\b(?:how|where|what|why|when|which|who|does|is|are|can|should|find|show|explain|list)\b",
    re.I,
)
_DEBUG_RE = re.compile(
    r"\b(?:error|exception|traceback|stack\s*trace|segfault|panic|nullpointer|"
    r"typeerror|valueerror|assertion|failed|crash|bug|fix)\b",
    re.I,
)
_ARCH_RE = re.compile(
    r"\b(?:architecture|entrypoint|entry[\s\-]?point|pipeline|"
    r"module\s+structure|data\s+flow|system\s+design|overview|"
    r"responsib\w+|cross[\s\-]?cutting)\b",
    re.I,
)

# Conservative NL → code-token expansions (not paraphrasing user identifiers).
_NL_EXPANSIONS: dict[str, tuple[str, ...]] = {
    "authentication": ("auth", "login", "middleware", "session"),
    "authorize": ("auth", "permission", "rbac"),
    "authorization": ("auth", "permission", "rbac"),
    "retry": ("retries", "backoff", "retriable"),
    "retries": ("retry", "backoff"),
    "database": ("db", "repository", "sql", "query"),
    "repository": ("repo", "dao", "store"),
    "request": ("http", "handler", "endpoint", "route"),
    "endpoint": ("route", "handler", "api", "controller"),
    "middleware": ("middleware", "interceptor", "filter"),
    "user": ("user", "account", "profile"),
    "config": ("configuration", "settings", "env"),
    "logging": ("logger", "log", "audit"),
}


class QueryKind(StrEnum):
    IDENTIFIER = "identifier"
    NATURAL_LANGUAGE = "natural_language"
    ARCHITECTURAL = "architectural"
    DEBUGGING = "debugging"
    MIXED = "mixed"
    PATH = "path"


@dataclass(frozen=True, slots=True)
class QueryAnalysis:
    original: str
    kind: QueryKind
    identifiers: tuple[str, ...] = ()
    paths: tuple[str, ...] = ()
    frameworks: tuple[str, ...] = ()
    concepts: tuple[str, ...] = ()
    retrieval_queries: tuple[str, ...] = ()
    rewrite_applied: bool = False
    notes: tuple[str, ...] = field(default_factory=tuple)


def _extract_paths(q: str) -> list[str]:
    found: list[str] = []
    for match in _PATH_RE.finditer(q):
        found.append(match.group(1))
    for match in _FILE_EXT_RE.finditer(q):
        token = match.group(1)
        if token not in found:
            found.append(token)
    return found


def _extract_identifiers(q: str, *, paths: list[str]) -> list[str]:
    skip = set(paths)
    for p in paths:
        skip.update(p.split("/"))
    out: list[str] = []
    for match in _IDENT_RE.finditer(q):
        token = match.group(0)
        if token in skip or token in out:
            continue
        out.append(token)
    # Backtick-quoted tokens
    for match in re.finditer(r"`([^`]+)`", q):
        token = match.group(1).strip()
        if token and token not in out and "/" not in token:
            out.append(token)
    return out


def _extract_concepts(q: str) -> list[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9_\-]{2,}", q.lower())
    stop = {
        "the",
        "and",
        "for",
        "with",
        "from",
        "that",
        "this",
        "into",
        "about",
        "where",
        "what",
        "when",
        "which",
        "how",
        "does",
        "are",
        "is",
        "can",
        "find",
        "show",
        "code",
        "file",
        "function",
        "class",
        "method",
    }
    return [w for w in words if w not in stop][:12]


_FRAMEWORK_HINTS = (
    "fastapi",
    "flask",
    "django",
    "express",
    "react",
    "spring",
    "nextjs",
    "nestjs",
    "rails",
    "laravel",
)


def _extract_frameworks(q: str) -> list[str]:
    lower = q.lower()
    return [name for name in _FRAMEWORK_HINTS if name in lower]


def classify_query(query: str) -> QueryKind:
    q = query.strip()
    if not q:
        return QueryKind.NATURAL_LANGUAGE

    paths = _extract_paths(q)
    idents = _extract_identifiers(q, paths=paths)
    has_question = bool(_QUESTION_RE.search(q))
    has_debug = bool(_DEBUG_RE.search(q))
    has_arch = bool(_ARCH_RE.search(q))
    has_spaces = " " in q
    quoted_error = bool(re.search(r"[\"'].+[\"']", q)) and has_debug

    if paths and not has_question and not has_spaces:
        return QueryKind.PATH
    if has_debug or quoted_error:
        if idents or paths:
            return QueryKind.MIXED
        return QueryKind.DEBUGGING
    if has_arch and (has_question or has_spaces):
        return QueryKind.ARCHITECTURAL
    if idents and not has_question and (not has_spaces or len(q.split()) <= 3):
        return QueryKind.IDENTIFIER
    if idents and (has_question or has_spaces):
        return QueryKind.MIXED
    if has_question or has_spaces:
        return QueryKind.NATURAL_LANGUAGE
    if idents:
        return QueryKind.IDENTIFIER
    return QueryKind.NATURAL_LANGUAGE


def _should_rewrite(kind: QueryKind) -> bool:
    return kind in {
        QueryKind.NATURAL_LANGUAGE,
        QueryKind.ARCHITECTURAL,
        QueryKind.MIXED,
    }


def _deterministic_rewrites(
    query: str,
    *,
    kind: QueryKind,
    identifiers: list[str],
    paths: list[str],
    concepts: list[str],
    max_rewrites: int,
) -> list[str]:
    """Build ≤ max_rewrites retrieval queries. Never alter identifier/path tokens."""
    original = query.strip()
    out: list[str] = [original]

    # Always keep exact identifiers / paths as standalone retrieval queries.
    for token in [*paths, *identifiers]:
        if token not in out:
            out.append(token)
        if len(out) >= max_rewrites:
            return out[:max_rewrites]

    if not _should_rewrite(kind):
        return out[:max_rewrites]

    # Concept expansions (add related code tokens; do not replace identifiers).
    expanded_terms: list[str] = []
    for concept in concepts:
        extras = _NL_EXPANSIONS.get(concept)
        if extras:
            expanded_terms.extend(extras)
        else:
            expanded_terms.append(concept)

    # Keyword bag query (identifiers preserved verbatim).
    bag_parts = [*identifiers, *paths, *expanded_terms[:6]]
    if bag_parts:
        bag = " ".join(dict.fromkeys(bag_parts))
        if bag and bag not in out:
            out.append(bag)

    if kind == QueryKind.ARCHITECTURAL and "architecture" not in original.lower():
        arch_q = f"{original} architecture entrypoint"
        if arch_q not in out:
            out.append(arch_q)

    if kind in {QueryKind.NATURAL_LANGUAGE, QueryKind.MIXED} and concepts:
        intent = " ".join(concepts[:4])
        if intent and intent not in out:
            out.append(intent)

    return out[:max_rewrites]


def analyze_query(
    query: str,
    *,
    cfg: Settings | None = None,
) -> QueryAnalysis:
    """Classify query and produce up to ask_query_max_rewrites retrieval queries."""
    conf = cfg or settings
    original = query.strip()
    if not original:
        return QueryAnalysis(
            original="",
            kind=QueryKind.NATURAL_LANGUAGE,
            retrieval_queries=(),
            notes=("empty_query",),
        )

    max_n = max(1, min(4, conf.ask_query_max_rewrites))
    paths = _extract_paths(original)
    identifiers = _extract_identifiers(original, paths=paths)
    frameworks = _extract_frameworks(original)
    concepts = _extract_concepts(original)
    kind = classify_query(original)

    if not conf.ask_query_rewrite_enabled:
        return QueryAnalysis(
            original=original,
            kind=kind,
            identifiers=tuple(identifiers),
            paths=tuple(paths),
            frameworks=tuple(frameworks),
            concepts=tuple(concepts),
            retrieval_queries=(original,),
            rewrite_applied=False,
            notes=("rewrite_disabled",),
        )

    rewrites = _deterministic_rewrites(
        original,
        kind=kind,
        identifiers=identifiers,
        paths=paths,
        concepts=concepts,
        max_rewrites=max_n,
    )
    # Safety: every extracted identifier/path must appear unchanged in at least
    # one retrieval query (never paraphrased away).
    for token in [*identifiers, *paths]:
        if not any(token in rq for rq in rewrites):
            if len(rewrites) < max_n:
                rewrites.append(token)
            else:
                rewrites[-1] = token

    rewrite_applied = _should_rewrite(kind) and (
        len(rewrites) > 1 or rewrites[0] != original
    )
    notes: list[str] = []
    if not _should_rewrite(kind):
        notes.append("skip_rewrite_for_kind")
    notes.append(f"rewrite_count={len(rewrites)}")

    return QueryAnalysis(
        original=original,
        kind=kind,
        identifiers=tuple(identifiers),
        paths=tuple(paths),
        frameworks=tuple(frameworks),
        concepts=tuple(concepts),
        retrieval_queries=tuple(rewrites[:max_n]),
        rewrite_applied=rewrite_applied,
        notes=tuple(notes),
    )
