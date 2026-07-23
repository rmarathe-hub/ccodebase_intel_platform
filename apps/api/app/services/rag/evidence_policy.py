"""Ask evidence classification, routing helpers, and ranking priors.

Prioritizes shipped source/README/architecture over plans/checklists, and
supports exact-file + symbol routing for grounded Ask answers.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import IntEnum, StrEnum
from pathlib import PurePosixPath
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import Chunk, SourceFile, Symbol
from app.services.chunks_query import ChunkSearchResult
from app.services.rag.query_analysis import QueryAnalysis, QueryKind


def normalize_repo_path(path: str) -> str:
    """Normalize path separators and strip a ``./`` prefix only.

    Do not use ``str.lstrip('./')`` — that treats ``.`` and ``/`` as a
    character set and corrupts paths like ``.github/workflows/...``.
    """
    p = (path or "").replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    return p


# Basename / path patterns treated as plans or speculative docs (demoted).
_PLAN_NAME_RE = re.compile(
    r"(?:"
    r"DAY\d+_CHECKLIST|"
    r"WEEK\d+_PLAN|"
    r"FLAGSHIP_PLAN|"
    r"_PLAN\.md$|"
    r"CHECKLIST\.md$|"
    r"TODO\.md$|"
    r"ROADMAP"
    r")",
    re.I,
)
_PROPOSED_ML_RE = re.compile(
    r"(?:ML_ENGINEER_PATH|proposed|not yet implemented|plan only)",
    re.I,
)

_SOURCE_EXTS = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".java",
    ".go",
    ".rs",
    ".cs",
    ".cpp",
    ".c",
    ".h",
    ".rb",
    ".sh",
    ".sql",
    ".yml",
    ".yaml",
    ".toml",
    ".json",
    ".xml",
    ".gradle",
    ".dockerfile",
}
_FILE_WALK_RE = re.compile(
    r"\b(?:"
    r"walk\s*through|walkthrough|list\s+columns?|enumerate\s+columns?|"
    r"explain\s+(?:this\s+)?file|explain\s+|"
    r"produced\s+by|contents?\s+of|"
    r"what\s+(?:sql\s+)?columns?|full\s+(?:select|file|sql)|"
    r"show\s+(?:me\s+)?(?:the\s+)?(?:file|sql|model)|"
    r"why\s+is\b.+\bin\b|"
    r"trace\b"
    r")\b",
    re.I,
)
_ONBOARDING_RE = re.compile(
    r"\b(?:"
    r"onboard|new\s+engineer|getting\s+started|how\s+(?:is\s+)?(?:the\s+)?"
    r"(?:repo|repository|project)\s+(?:structured|organized|laid\s+out)|"
    r"repository\s+overview|architecture\s+overview|reading\s+order|"
    r"where\s+should\s+i\s+start|take\s+ownership|taking\s+ownership|"
    r"explain\s+(?:this|the)\s+(?:repo|repository|project|codebase)|"
    r"how\s+does\s+(?:this|the)\s+(?:application|app|repo|repository|project)\s+work|"
    r"what\s+(?:is\s+)?(?:this|the)\s+(?:repo|project)|strength|"
    r"data\s+engineering|strongest\s+role"
    r")\b",
    re.I,
)
_NEGATIVE_INFRA_RE = re.compile(
    r"\b(?:kubernetes|k8s|redis|kafka|terraform)\b",
    re.I,
)
_DEPLOYMENT_QUERY_RE = re.compile(
    r"\b(?:"
    r"deploy(?:ment|s|ing)?|"
    r"continuous\s+integration|continuous\s+delivery|"
    r"\bci\b|\bcd\b|pipeline|"
    r"github\s+pages|gitlab\s+pages|"
    r"push\s+to\s+(?:main|master|prod)|"
    r"live\s+site|production\s+(?:site|deploy)|"
    r"release\s+(?:pipeline|workflow)|"
    r"how\s+(?:does|do)\s+(?:a\s+)?(?:push|commit|merge)\b"
    r")\b",
    re.I,
)
_DEPLOYMENT_PATH_RE = re.compile(
    r"(?:"
    r"/\.github/workflows/|"
    r"/\.gitlab-ci|"
    r"gitlab-ci\.ya?ml|"
    r"/\.circleci/|"
    r"/jenkins|"
    r"cloudbuild\.ya?ml|"
    r"buildspec\.ya?ml|"
    r"azure-pipelines|"
    r"/deploy(?:ment)?/|"
    r"/infra(?:structure)?/|"
    r"/terraform/|"
    r"/helm/|"
    r"/k8s/|"
    r"/kubernetes/|"
    r"dockerfile|"
    r"docker-compose\.ya?ml"
    r")",
    re.I,
)


# Universal onboarding anchors (always preferred when present).
ONBOARDING_UNIVERSAL_SUFFIXES: tuple[str, ...] = (
    "README.md",
    "docs/ARCHITECTURE.md",
    "ARCHITECTURE.md",
)

# Backward-compatible alias (universal + common DE manifests).
ONBOARDING_PATH_SUFFIXES: tuple[str, ...] = (
    *ONBOARDING_UNIVERSAL_SUFFIXES,
    "docker-compose.yml",
    "docker-compose.yaml",
    "dbt/dbt_project.yml",
    "dbt_project.yml",
)


class ProjectEcosystem(StrEnum):
    """Detected repository ecosystems for adaptive onboarding seeds."""

    NODE = "node"
    PYTHON = "python"
    JAVA = "java"
    GO = "go"
    RUST = "rust"
    DATA_ENGINEERING = "data_engineering"


@dataclass(frozen=True, slots=True)
class OnboardingAnchorSpec:
    """File basenames/suffixes and path prefixes to seed for an ecosystem."""

    suffixes: tuple[str, ...] = ()
    prefixes: tuple[str, ...] = ()
    like_patterns: tuple[str, ...] = ()


_ECOSYSTEM_ONBOARDING: dict[ProjectEcosystem, OnboardingAnchorSpec] = {
    ProjectEcosystem.NODE: OnboardingAnchorSpec(
        suffixes=(
            "package.json",
            "vite.config.ts",
            "vite.config.js",
            "vite.config.mjs",
            "next.config.js",
            "next.config.ts",
            "next.config.mjs",
            "tsconfig.json",
            "index.html",
            "src/main.tsx",
            "src/main.ts",
            "src/main.jsx",
            "src/main.js",
            "src/App.tsx",
            "src/App.ts",
            "src/App.jsx",
            "src/App.js",
            "app/page.tsx",
            "app/layout.tsx",
        ),
        prefixes=("src/", "app/", "pages/", "components/"),
    ),
    ProjectEcosystem.PYTHON: OnboardingAnchorSpec(
        suffixes=(
            "pyproject.toml",
            "requirements.txt",
            "setup.py",
            "setup.cfg",
            "Pipfile",
            "manage.py",
        ),
        prefixes=("src/", "app/"),
    ),
    ProjectEcosystem.JAVA: OnboardingAnchorSpec(
        suffixes=("pom.xml", "build.gradle", "build.gradle.kts"),
        prefixes=("src/main/java/", "src/main/kotlin/", "src/main/resources/"),
    ),
    ProjectEcosystem.GO: OnboardingAnchorSpec(
        suffixes=("go.mod",),
        prefixes=("cmd/", "internal/", "pkg/"),
    ),
    ProjectEcosystem.RUST: OnboardingAnchorSpec(
        suffixes=("Cargo.toml",),
        prefixes=("src/", "crates/"),
    ),
    ProjectEcosystem.DATA_ENGINEERING: OnboardingAnchorSpec(
        suffixes=(
            "dbt_project.yml",
            "dbt/dbt_project.yml",
            "docker-compose.yml",
            "docker-compose.yaml",
        ),
        prefixes=("dbt/models/", "ingestion/", "dashboard/"),
        like_patterns=(
            "%/airflow/dags/%.py",
            "%/dags/%.py",
            "%streamlit%.py",
        ),
    ),
}

# Deployment is supplemental and capped — never universal-first.
_DEPLOYMENT_LIKE_PATTERNS: tuple[str, ...] = (
    "%.github/workflows/%.yml",
    "%.github/workflows/%.yaml",
    "%.gitlab-ci.yml",
    "%.gitlab-ci.yaml",
    "%.circleci/%.yml",
    "%Dockerfile%",
    "%docker-compose.y%ml",
    "%cloudbuild.y%ml",
    "%azure-pipelines%.yml",
    "%/terraform/%.tf",
)

# Per-category caps so one category cannot consume the onboarding budget.
_ONBOARDING_CATEGORY_CAPS: dict[str, int] = {
    "docs": 8,
    "manifest_config": 10,
    "entrypoints": 10,
    "application": 12,
    "deployment": 2,
}


def _onboarding_category(path: str) -> str:
    norm = normalize_repo_path(path).lower()
    name = PurePosixPath(norm).name
    if name.startswith("readme") or "architecture" in name or norm.startswith("docs/"):
        return "docs"
    if "/.github/workflows/" in f"/{norm}" or name in {
        "dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
    }:
        return "deployment"
    if name in {
        "package.json",
        "pyproject.toml",
        "requirements.txt",
        "go.mod",
        "cargo.toml",
        "pom.xml",
        "tsconfig.json",
        "dbt_project.yml",
    } or name.startswith("vite.config.") or name.startswith("next.config."):
        return "manifest_config"
    if name in {
        "index.html",
        "main.tsx",
        "main.ts",
        "main.jsx",
        "main.js",
        "main.go",
        "main.rs",
        "app.tsx",
        "app.ts",
        "app.jsx",
        "app.js",
        "app.py",
        "manage.py",
    } or norm.endswith("/main.tsx") or norm.endswith("/app.tsx") or norm.endswith(
        "/main.ts"
    ):
        return "entrypoints"
    return "application"



class EvidenceTier(IntEnum):
    """Lower ordinal = higher priority for Ask evidence."""

    EXACT_FILE = 0
    SOURCE = 1
    README = 2
    ARCHITECTURE = 3
    CONFIG_WORKFLOW = 4
    TEST_SCHEMA = 5
    DATA_DICTIONARY = 6
    OTHER_DOC = 7
    PLAN = 8


_TIER_BOOST: dict[EvidenceTier, float] = {
    EvidenceTier.EXACT_FILE: 2.50,
    EvidenceTier.SOURCE: 1.10,
    EvidenceTier.README: 0.95,
    EvidenceTier.ARCHITECTURE: 0.80,
    EvidenceTier.CONFIG_WORKFLOW: 0.65,
    EvidenceTier.TEST_SCHEMA: 0.45,
    EvidenceTier.DATA_DICTIONARY: 0.35,
    EvidenceTier.OTHER_DOC: 0.10,
    EvidenceTier.PLAN: -1.75,
}


def classify_evidence_path(path: str) -> EvidenceTier:
    """Map a repository path to an Ask evidence tier."""
    norm = normalize_repo_path(path)
    lower = norm.lower()
    name = PurePosixPath(norm).name
    stem_lower = name.lower()

    if _PLAN_NAME_RE.search(name) or _PLAN_NAME_RE.search(norm):
        return EvidenceTier.PLAN
    if "flagship_plan" in lower or lower.endswith("_plan.md"):
        return EvidenceTier.PLAN
    if stem_lower == "readme.md" or stem_lower.startswith("readme."):
        return EvidenceTier.README
    if "architecture" in stem_lower or lower.endswith("docs/architecture.md"):
        return EvidenceTier.ARCHITECTURE
    if "data_dictionary" in lower or stem_lower in {"data-dictionary.md", "dictionary.md"}:
        return EvidenceTier.DATA_DICTIONARY
    if (
        "/tests/" in f"/{lower}"
        or "/test/" in f"/{lower}"
        or stem_lower.startswith("test_")
        or stem_lower.endswith("_test.py")
        or "schema" in stem_lower
    ):
        # Prefer treating .sql models as SOURCE below; schema yml under dbt stays test/schema.
        if not lower.endswith(".sql"):
            return EvidenceTier.TEST_SCHEMA
    if (
        stem_lower in {"docker-compose.yml", "docker-compose.yaml", "dockerfile", "makefile"}
        or _DEPLOYMENT_PATH_RE.search(f"/{lower}")
        or "/airflow/" in f"/{lower}"
        or "/dags/" in f"/{lower}"
        or stem_lower == "dbt_project.yml"
    ):
        return EvidenceTier.CONFIG_WORKFLOW

    ext = PurePosixPath(norm).suffix.lower()
    if ext in _SOURCE_EXTS or stem_lower == "dockerfile":
        return EvidenceTier.SOURCE
    if ext in {".md", ".rst", ".txt"}:
        if _PROPOSED_ML_RE.search(norm):
            return EvidenceTier.PLAN
        return EvidenceTier.OTHER_DOC
    return EvidenceTier.OTHER_DOC


def tier_boost(tier: EvidenceTier) -> float:
    return float(_TIER_BOOST.get(tier, 0.0))


def is_file_walk_query(query: str) -> bool:
    return bool(_FILE_WALK_RE.search(query or ""))


def is_onboarding_query(query: str, analysis: QueryAnalysis | None = None) -> bool:
    if _ONBOARDING_RE.search(query or ""):
        return True
    if analysis is not None and analysis.kind == QueryKind.ARCHITECTURAL:
        return True
    return False


def is_negative_infra_query(query: str) -> bool:
    return bool(_NEGATIVE_INFRA_RE.search(query or ""))


def is_deployment_query(query: str) -> bool:
    """True when the question is about CI/CD, release, or live deployment."""
    return bool(_DEPLOYMENT_QUERY_RE.search(query or ""))


def is_deployment_evidence_path(path: str) -> bool:
    norm = normalize_repo_path(path)
    return bool(_DEPLOYMENT_PATH_RE.search(f"/{norm.lower()}"))


def apply_evidence_priors(
    ranked: list[ChunkSearchResult],
    *,
    analysis: QueryAnalysis,
    mandatory_paths: set[str] | None = None,
) -> list[ChunkSearchResult]:
    """Re-score ranked hits with path-tier priors and exact-file boosts.

    Exact-file boost applies only to paths/basenames named in the query.
    Onboarding / prefer-path seeds stay in ``mandatory_paths`` for expand but
    keep their natural path tier (so workflows cannot dominate README/source).
    """
    mandatory = {normalize_repo_path(p).lower() for p in (mandatory_paths or set())}
    path_tokens = {normalize_repo_path(p).lower() for p in analysis.paths}
    basename_tokens = {PurePosixPath(p).name.lower() for p in path_tokens}

    rescored: list[ChunkSearchResult] = []
    for item in ranked:
        path = normalize_repo_path(item.chunk.path)
        path_l = path.lower()
        base_l = PurePosixPath(path).name.lower()
        tier = classify_evidence_path(path)
        boost = tier_boost(tier)
        exact_file = False
        if path_l in path_tokens or base_l in basename_tokens:
            exact_file = True
            boost = max(boost, tier_boost(EvidenceTier.EXACT_FILE))
            tier = EvidenceTier.EXACT_FILE
        elif path_l in mandatory:
            # Prefer-path / onboarding seed: mild boost, keep classified tier.
            boost = max(boost, 0.40)
        if is_deployment_query(analysis.original):
            if is_deployment_evidence_path(path) or tier == EvidenceTier.CONFIG_WORKFLOW:
                boost += 1.35
                breakdown_deploy = True
            elif "/components/" in f"/{path_l}" or "/ui/" in f"/{path_l}":
                # UI widgets should not crowd out CI/config for deploy questions.
                boost -= 0.85
                breakdown_deploy = True
            else:
                breakdown_deploy = False
        else:
            breakdown_deploy = False
        # Extra demotion when plans compete with implementation questions.
        if tier == EvidenceTier.PLAN and (
            analysis.paths or analysis.identifiers or is_file_walk_query(analysis.original)
        ):
            boost -= 0.75

        base_score = float(item.score or 0.0)
        new_score = base_score + boost
        breakdown = dict(item.score_breakdown or {})
        breakdown["evidence_tier"] = float(int(tier))
        breakdown["evidence_tier_boost"] = round(boost, 6)
        breakdown["exact_file_match"] = 1.0 if exact_file else 0.0
        breakdown["prefer_path_seed"] = 1.0 if (path_l in mandatory and not exact_file) else 0.0
        breakdown["deployment_intent_adjust"] = 1.0 if breakdown_deploy else 0.0
        breakdown["prior_score"] = round(base_score, 6)
        breakdown["fused"] = round(new_score, 6)
        rescored.append(
            ChunkSearchResult(
                chunk=item.chunk,
                score=round(new_score, 6),
                score_breakdown=breakdown,
            )
        )

    rescored.sort(
        key=lambda r: (
            -(r.score or 0.0),
            int((r.score_breakdown or {}).get("evidence_tier", 9)),
            r.chunk.path,
            r.chunk.start_line,
            str(r.chunk.id),
        )
    )
    return rescored


def is_exact_file_mode(query: str, analysis: QueryAnalysis | None = None) -> bool:
    """True when Ask should prefer complete retrieval of named file(s)."""
    if analysis is not None and analysis.paths:
        return True
    return is_file_walk_query(query)


def resolve_path_chunks(
    session: Session,
    *,
    snapshot_id: UUID,
    path_token: str,
    limit: int | None = None,
) -> list[Chunk]:
    """Resolve chunks for an exact path or basename (source order).

    When ``limit`` is None, fetch all matching chunks (Exact File Mode).
    """
    token = normalize_repo_path(path_token.strip())
    if not token:
        return []
    basename = PurePosixPath(token).name
    cap = limit if limit is not None else 10_000

    # Prefer exact path match, then unique basename match.
    exact = list(
        session.scalars(
            select(Chunk)
            .where(Chunk.snapshot_id == snapshot_id, Chunk.path == token)
            .order_by(Chunk.start_line.asc(), Chunk.end_line.asc(), Chunk.id.asc())
            .limit(cap)
        ).all()
    )
    if exact:
        return exact

    # Case-insensitive path equality.
    exact_ci = list(
        session.scalars(
            select(Chunk)
            .where(
                Chunk.snapshot_id == snapshot_id,
                func.lower(Chunk.path) == token.lower(),
            )
            .order_by(Chunk.start_line.asc(), Chunk.end_line.asc(), Chunk.id.asc())
            .limit(cap)
        ).all()
    )
    if exact_ci:
        return exact_ci

    # Basename match (e.g. weather_at_departure.sql / vite.config.ts).
    rows = list(
        session.scalars(
            select(Chunk)
            .where(
                Chunk.snapshot_id == snapshot_id,
                or_(
                    Chunk.path.endswith("/" + basename),
                    func.lower(Chunk.path).endswith("/" + basename.lower()),
                    func.lower(Chunk.path) == basename.lower(),
                ),
            )
            .order_by(Chunk.path.asc(), Chunk.start_line.asc(), Chunk.id.asc())
            .limit(cap)
        ).all()
    )
    if not rows:
        return []
    # If multiple files share basename, keep the first path group only.
    first_path = rows[0].path
    return [c for c in rows if c.path == first_path]


def lookup_source_file(
    session: Session,
    *,
    snapshot_id: UUID,
    path: str,
) -> SourceFile | None:
    norm = normalize_repo_path(path)
    row = session.scalars(
        select(SourceFile).where(
            SourceFile.snapshot_id == snapshot_id, SourceFile.path == norm
        )
    ).first()
    if row is not None:
        return row
    return session.scalars(
        select(SourceFile).where(
            SourceFile.snapshot_id == snapshot_id,
            func.lower(SourceFile.path) == norm.lower(),
        )
    ).first()


def merge_line_ranges(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Merge overlapping/adjacent inclusive line ranges."""
    if not ranges:
        return []
    ordered = sorted((int(s), int(e)) for s, e in ranges if e >= s)
    if not ordered:
        return []
    merged: list[list[int]] = [[ordered[0][0], ordered[0][1]]]
    for start, end in ordered[1:]:
        cur = merged[-1]
        if start <= cur[1] + 1:
            cur[1] = max(cur[1], end)
        else:
            merged.append([start, end])
    return [(a, b) for a, b in merged]


def missing_line_ranges(
    *,
    indexed_start: int,
    indexed_end: int,
    covered: list[tuple[int, int]],
) -> list[tuple[int, int]]:
    if indexed_end < indexed_start:
        return []
    gaps: list[tuple[int, int]] = []
    cursor = indexed_start
    for start, end in merge_line_ranges(covered):
        if start > cursor:
            gaps.append((cursor, start - 1))
        cursor = max(cursor, end + 1)
    if cursor <= indexed_end:
        gaps.append((cursor, indexed_end))
    return gaps


def assemble_file_lines(
    chunks: list[Chunk],
    *,
    max_chars: int,
) -> tuple[str, int, int, bool, list[tuple[int, int]]]:
    """Assemble same-file chunks in source order with per-line dedupe.

    Returns (text, chars_stored, chars_sent, truncated, covered_ranges).
    """
    if not chunks:
        return "", 0, 0, False, []

    line_map: dict[int, str] = {}
    for chunk in sorted(chunks, key=lambda c: (c.start_line, c.end_line, str(c.id))):
        # Prefer split("\n") semantics matching discovery/physical_lines so a
        # trailing blank line is not dropped by str.splitlines().
        content = chunk.content or ""
        if content.endswith("\n"):
            lines = content.split("\n")[:-1]
        else:
            lines = content.split("\n") if content else []
        span = max(1, chunk.end_line - chunk.start_line + 1)
        if len(lines) < span:
            lines = list(lines) + [""] * (span - len(lines))
        if len(lines) == span:
            for i, line in enumerate(lines):
                line_no = chunk.start_line + i
                line_map.setdefault(line_no, line)
        else:
            # Best-effort placement when content line count ≠ span.
            for i, line in enumerate(lines):
                line_no = chunk.start_line + i
                if line_no > chunk.end_line:
                    break
                line_map.setdefault(line_no, line)

    if not line_map:
        # Fallback: naive join
        ordered = sorted(chunks, key=lambda c: (c.start_line, c.end_line, str(c.id)))
        text = "\n".join(c.content for c in ordered)
        stored = len(text)
        if stored <= max_chars:
            covered = merge_line_ranges([(c.start_line, c.end_line) for c in ordered])
            return text, stored, stored, False, covered
        covered = merge_line_ranges([(c.start_line, c.end_line) for c in ordered])
        return text[:max_chars] + "…", stored, max_chars, True, covered

    ordered_lines = sorted(line_map.items())
    full = "\n".join(text for _, text in ordered_lines)
    stored = len(full)
    covered = merge_line_ranges([(ln, ln) for ln, _ in ordered_lines])
    if stored <= max_chars:
        return full, stored, stored, False, covered

    # Deterministic truncation: keep from the start (imports/declarations first).
    kept: list[str] = []
    used = 0
    kept_lines: list[int] = []
    for line_no, text in ordered_lines:
        add = len(text) + (1 if kept else 0)
        if used + add > max_chars:
            break
        kept.append(text)
        kept_lines.append(line_no)
        used += add
    out = "\n".join(kept)
    if len(out) < stored:
        out = out + "…"
    return out, stored, min(used, max_chars), True, merge_line_ranges(
        [(ln, ln) for ln in kept_lines]
    )


def compute_file_coverage(
    chunks: list[Chunk],
    *,
    source_file: SourceFile | None = None,
    covered_ranges: list[tuple[int, int]] | None = None,
) -> dict[str, object]:
    """Coverage metadata for Exact File Mode diagnostics."""
    if not chunks and source_file is None:
        return {
            "indexed": False,
            "coverage_complete": False,
            "indexed_line_range": None,
            "retrieved_line_ranges": [],
            "missing_ranges": [],
            "chunk_count": 0,
        }

    path = (source_file.path if source_file is not None else chunks[0].path) if (
        source_file is not None or chunks
    ) else ""
    chunk_ranges = [(c.start_line, c.end_line) for c in chunks]
    retrieved = merge_line_ranges(covered_ranges or chunk_ranges)
    if source_file is not None and source_file.line_count and source_file.line_count > 0:
        indexed_start, indexed_end = 1, int(source_file.line_count)
    elif chunk_ranges:
        indexed_start = min(s for s, _ in chunk_ranges)
        indexed_end = max(e for _, e in chunk_ranges)
    else:
        indexed_start, indexed_end = 1, 0

    missing = missing_line_ranges(
        indexed_start=indexed_start,
        indexed_end=indexed_end,
        covered=retrieved,
    )
    complete = indexed_end >= indexed_start and not missing and bool(retrieved)
    return {
        "path": path,
        "indexed": True if chunks or (source_file is not None and source_file.support_level != "skip") else False,
        "coverage_complete": complete,
        "indexed_line_range": [indexed_start, indexed_end] if indexed_end >= indexed_start else None,
        "retrieved_line_ranges": [[s, e] for s, e in retrieved],
        "missing_ranges": [[s, e] for s, e in missing],
        "chunk_count": len(chunks),
        "language": source_file.language if source_file is not None else (
            chunks[0].language if chunks else None
        ),
        "classification": (
            source_file.support_level if source_file is not None else (
                chunks[0].support_level if chunks else None
            )
        ),
        "line_count": source_file.line_count if source_file is not None else None,
    }


def aggregate_file_content(
    chunks: list[Chunk],
    *,
    max_chars: int,
) -> tuple[str, int, int, bool]:
    """Concatenate same-file chunks in source order with overlap dedupe.

    Returns (text, chars_stored, chars_sent, truncated).
    """
    text, stored, sent, trunc, _covered = assemble_file_lines(chunks, max_chars=max_chars)
    return text, stored, sent, trunc


def build_path_retrieval_diagnostic(
    session: Session,
    *,
    snapshot_id: UUID,
    path: str,
    chunks: list[Chunk],
    reason: str,
    coverage: dict[str, object] | None = None,
) -> dict[str, object]:
    sf = lookup_source_file(session, snapshot_id=snapshot_id, path=path)
    cov = coverage or compute_file_coverage(chunks, source_file=sf)
    basename = PurePosixPath(path).name
    return {
        "path": path,
        "basename_aliases": [basename],
        "indexed": bool(chunks) or (sf is not None and sf.support_level != "skip"),
        "source_file_present": sf is not None,
        "skip_reason": sf.skip_reason if sf is not None else None,
        "classification": cov.get("classification"),
        "language": cov.get("language"),
        "chunk_count": len(chunks),
        "line_coverage": cov.get("retrieved_line_ranges"),
        "indexed_line_range": cov.get("indexed_line_range"),
        "coverage_complete": cov.get("coverage_complete"),
        "missing_ranges": cov.get("missing_ranges"),
        "retrieval_reason": reason,
        "snapshot_id": str(snapshot_id),
    }


def chunks_to_search_results(
    chunks: list[Chunk],
    *,
    role_score: float,
    evidence_tier: EvidenceTier,
    reason: str,
) -> list[ChunkSearchResult]:
    out: list[ChunkSearchResult] = []
    for i, chunk in enumerate(chunks):
        score = role_score - (i * 0.001)
        out.append(
            ChunkSearchResult(
                chunk=chunk,
                score=round(score, 6),
                score_breakdown={
                    "routing": 1.0,
                    "routing_reason": hash(reason) % 10_000 / 10_000.0,  # placeholder numeric
                    "evidence_tier": float(int(evidence_tier)),
                    "evidence_tier_boost": tier_boost(evidence_tier),
                    "exact_file_match": 1.0,
                    "fused": round(score, 6),
                    "route_rank": float(i + 1),
                },
            )
        )
    return out


def detect_project_ecosystems(paths: list[str] | tuple[str, ...]) -> tuple[ProjectEcosystem, ...]:
    """Infer ecosystems from indexed paths (order = confidence / priority)."""
    norms = [normalize_repo_path(p) for p in paths]
    lowers = [p.lower() for p in norms]
    basenames = {PurePosixPath(p).name.lower() for p in lowers}
    joined = "\n".join(lowers)

    scores: dict[ProjectEcosystem, int] = {}

    def bump(eco: ProjectEcosystem, n: int = 1) -> None:
        scores[eco] = scores.get(eco, 0) + n

    if "package.json" in basenames or "pnpm-lock.yaml" in basenames or "yarn.lock" in basenames:
        bump(ProjectEcosystem.NODE, 3)
    if any(
        b.startswith("vite.config.") or b.startswith("next.config.") for b in basenames
    ):
        bump(ProjectEcosystem.NODE, 2)
    if any(p.startswith("src/") or p.startswith("app/") or p.startswith("pages/") for p in lowers):
        if "package.json" in basenames or any(p.endswith((".ts", ".tsx", ".js", ".jsx")) for p in lowers):
            bump(ProjectEcosystem.NODE, 1)

    if basenames & {"pyproject.toml", "requirements.txt", "setup.py", "setup.cfg", "pipfile"}:
        bump(ProjectEcosystem.PYTHON, 3)
    py_count = sum(1 for p in lowers if p.endswith(".py"))
    if py_count >= 3:
        bump(ProjectEcosystem.PYTHON, 2)
    elif py_count >= 1:
        bump(ProjectEcosystem.PYTHON, 1)
    if any(p.startswith("src/") and p.endswith(".py") for p in lowers):
        bump(ProjectEcosystem.PYTHON, 1)

    if basenames & {"pom.xml", "build.gradle", "build.gradle.kts"}:
        bump(ProjectEcosystem.JAVA, 3)
    if any("/src/main/java/" in f"/{p}" or p.endswith(".java") for p in lowers):
        bump(ProjectEcosystem.JAVA, 2)

    if "go.mod" in basenames or any(p.endswith(".go") for p in lowers):
        bump(ProjectEcosystem.GO, 3 if "go.mod" in basenames else 1)

    if "cargo.toml" in basenames or any(p.endswith(".rs") for p in lowers):
        bump(ProjectEcosystem.RUST, 3 if "cargo.toml" in basenames else 1)

    if "dbt_project.yml" in basenames or any(p.endswith("dbt_project.yml") for p in lowers):
        bump(ProjectEcosystem.DATA_ENGINEERING, 4)
    if "/airflow/" in joined or "/dags/" in joined:
        bump(ProjectEcosystem.DATA_ENGINEERING, 3)
    if basenames & {"docker-compose.yml", "docker-compose.yaml"} and (
        "dbt_project.yml" in basenames
        or "/airflow/" in joined
        or "/dags/" in joined
        or "/ingestion/" in joined
    ):
        bump(ProjectEcosystem.DATA_ENGINEERING, 2)

    # Keep ecosystems with meaningful signal; prefer higher scores.
    ranked = sorted(
        ((eco, score) for eco, score in scores.items() if score >= 2),
        key=lambda t: (-t[1], t[0].value),
    )
    return tuple(eco for eco, _ in ranked)


def detect_snapshot_ecosystems(
    session: Session,
    *,
    snapshot_id: UUID,
) -> tuple[ProjectEcosystem, ...]:
    paths = list(
        session.scalars(
            select(SourceFile.path).where(SourceFile.snapshot_id == snapshot_id)
        ).all()
    )
    if not paths:
        # Fallback when source_files missing: use distinct chunk paths.
        paths = list(
            session.scalars(
                select(Chunk.path).where(Chunk.snapshot_id == snapshot_id).distinct()
            ).all()
        )
    return detect_project_ecosystems(paths)


def onboarding_anchor_specs_for(
    ecosystems: tuple[ProjectEcosystem, ...] | list[ProjectEcosystem],
) -> list[OnboardingAnchorSpec]:
    """Compose universal + ecosystem-specific onboarding targets.

    Deployment/workflows are appended last with a separate low cap so they
    cannot crowd out README / manifests / entrypoints.
    """
    specs: list[OnboardingAnchorSpec] = [
        OnboardingAnchorSpec(suffixes=ONBOARDING_UNIVERSAL_SUFFIXES),
    ]
    seen: set[ProjectEcosystem] = set()
    for eco in ecosystems:
        if eco in seen:
            continue
        seen.add(eco)
        spec = _ECOSYSTEM_ONBOARDING.get(eco)
        if spec is not None:
            specs.append(spec)
    # Deployment last — supplemental only.
    specs.append(OnboardingAnchorSpec(like_patterns=_DEPLOYMENT_LIKE_PATTERNS))
    return specs


def _chunks_under_prefix(
    session: Session,
    *,
    snapshot_id: UUID,
    prefix: str,
    limit: int,
) -> list[Chunk]:
    """Sample up to ``limit`` distinct paths under a prefix (1 chunk each).

    Whole-file fallbacks densify per-file chunk counts; taking the first N
    raw chunks would otherwise collapse onto a few short paths (e.g. App.tsx)
    and never reach deeper application files under the same prefix.
    """
    pref = normalize_repo_path(prefix)
    if not pref.endswith("/"):
        pref = pref + "/"
    # Over-fetch so path diversification still has candidates after densified
    # files contribute multiple chunks each.
    fetch_n = max(limit * 12, limit)
    rows = list(
        session.scalars(
            select(Chunk)
            .where(
                Chunk.snapshot_id == snapshot_id,
                or_(Chunk.path.like(pref + "%"), func.lower(Chunk.path).like(pref.lower() + "%")),
            )
            .order_by(func.length(Chunk.path).asc(), Chunk.path.asc(), Chunk.start_line.asc())
            .limit(fetch_n)
        ).all()
    )
    picked: list[Chunk] = []
    seen_paths: set[str] = set()
    for c in rows:
        key = normalize_repo_path(c.path)
        if key in seen_paths:
            continue
        seen_paths.add(key)
        picked.append(c)
        if len(picked) >= limit:
            break
    return picked


def _chunks_for_like(
    session: Session,
    *,
    snapshot_id: UUID,
    pattern: str,
    limit: int,
) -> list[Chunk]:
    return list(
        session.scalars(
            select(Chunk)
            .where(Chunk.snapshot_id == snapshot_id, Chunk.path.like(pattern))
            .order_by(Chunk.path.asc(), Chunk.start_line.asc())
            .limit(limit)
        ).all()
    )


def resolve_onboarding_chunks(
    session: Session,
    *,
    snapshot_id: UUID,
    limit_per_path: int = 12,
    prefix_chunk_limit: int = 4,
    max_chunks: int = 48,
    ecosystems: tuple[ProjectEcosystem, ...] | None = None,
) -> tuple[list[Chunk], tuple[ProjectEcosystem, ...], list[str]]:
    """Pull adaptive onboarding anchors with per-category caps.

    Returns (chunks, ecosystems, diagnostic_notes).
    """
    ecos = ecosystems if ecosystems is not None else detect_snapshot_ecosystems(
        session, snapshot_id=snapshot_id
    )
    collected: list[Chunk] = []
    seen_ids: set[UUID] = set()
    seen_paths: set[str] = set()
    category_counts: dict[str, int] = {k: 0 for k in _ONBOARDING_CATEGORY_CAPS}
    notes: list[str] = []
    selected: list[str] = []
    skipped: list[str] = []

    def _try_add(rows: list[Chunk], *, category: str | None = None) -> None:
        for c in rows:
            if len(collected) >= max_chunks:
                return
            if c.id in seen_ids:
                continue
            path_key = normalize_repo_path(c.path)
            cat = category or _onboarding_category(path_key)
            cap = _ONBOARDING_CATEGORY_CAPS.get(cat, 8)
            if category_counts.get(cat, 0) >= cap:
                if path_key not in seen_paths:
                    skipped.append(f"{path_key}:{cat}:cap")
                    seen_paths.add(path_key)
                continue
            seen_ids.add(c.id)
            collected.append(c)
            if path_key not in seen_paths:
                selected.append(f"{path_key}:{cat}")
                seen_paths.add(path_key)
                category_counts[cat] = category_counts.get(cat, 0) + 1

    # Category order: docs → manifests → entrypoints → app → deployment.
    for spec in onboarding_anchor_specs_for(ecos):
        if len(collected) >= max_chunks:
            break
        for suffix in spec.suffixes:
            if len(collected) >= max_chunks:
                break
            rows = resolve_path_chunks(
                session,
                snapshot_id=snapshot_id,
                path_token=suffix,
                limit=limit_per_path,
            )
            if not rows:
                skipped.append(f"{suffix}:missing_or_unchunked")
                continue
            _try_add(rows)
        for prefix in spec.prefixes:
            if len(collected) >= max_chunks:
                break
            _try_add(
                _chunks_under_prefix(
                    session,
                    snapshot_id=snapshot_id,
                    prefix=prefix,
                    limit=prefix_chunk_limit,
                )
            )
        for pattern in spec.like_patterns:
            if len(collected) >= max_chunks:
                break
            # Deployment patterns are hard-capped to category budget.
            _try_add(
                _chunks_for_like(
                    session,
                    snapshot_id=snapshot_id,
                    pattern=pattern,
                    limit=min(prefix_chunk_limit, _ONBOARDING_CATEGORY_CAPS["deployment"]),
                ),
                # All patterns in the supplemental deployment spec share this cap.
                category="deployment",
            )

    notes.append(
        "onboarding_selected:"
        + ",".join(selected[:24])
    )
    if skipped:
        notes.append("onboarding_skipped:" + ",".join(skipped[:24]))
    notes.append(
        "onboarding_category_counts:"
        + ",".join(f"{k}={v}" for k, v in sorted(category_counts.items()))
    )
    return collected, ecos, notes


def resolve_deployment_chunks(
    session: Session,
    *,
    snapshot_id: UUID,
    max_chunks: int = 24,
) -> tuple[list[Chunk], list[str]]:
    """Seed CI/CD / infra evidence for deployment-intent questions.

    Uses path-pattern matching (workflows, compose, Docker, IaC) — not
    repository-specific filenames.
    """
    notes: list[str] = []
    collected: list[Chunk] = []
    seen: set[UUID] = set()
    for pattern in _DEPLOYMENT_LIKE_PATTERNS:
        if len(collected) >= max_chunks:
            break
        rows = _chunks_for_like(
            session,
            snapshot_id=snapshot_id,
            pattern=pattern,
            limit=8,
        )
        for c in rows:
            if c.id in seen:
                continue
            seen.add(c.id)
            collected.append(c)
            if len(collected) >= max_chunks:
                break
    # Also pull top-level package manifests when present (build scripts).
    for suffix in ("package.json", "pyproject.toml", "go.mod", "pom.xml", "Cargo.toml"):
        if len(collected) >= max_chunks:
            break
        rows = resolve_path_chunks(
            session, snapshot_id=snapshot_id, path_token=suffix, limit=4
        )
        for c in rows:
            if c.id in seen:
                continue
            seen.add(c.id)
            collected.append(c)
    if collected:
        notes.append(f"deployment_seeded:{len(collected)}")
        notes.append(
            "deployment_paths:"
            + ",".join(sorted({normalize_repo_path(c.path) for c in collected})[:16])
        )
    else:
        notes.append("deployment_seeded:0")
    return collected, notes


def resolve_symbol_chunks(
    session: Session,
    *,
    snapshot_id: UUID,
    name: str,
    limit: int = 12,
) -> tuple[list[Chunk], str]:
    """Resolve chunks for an exact symbol name, or closest match.

    Returns (chunks, note) where note is ``exact``, ``closest:<name>``, or ``missing``.
    """
    token = (name or "").strip()
    if not token:
        return [], "missing"

    exact = list(
        session.scalars(
            select(Symbol).where(
                Symbol.snapshot_id == snapshot_id,
                or_(Symbol.name == token, Symbol.qualified_name == token),
            )
        ).all()
    )
    note = "exact"
    symbols = exact
    if not symbols:
        ci = list(
            session.scalars(
                select(Symbol).where(
                    Symbol.snapshot_id == snapshot_id,
                    or_(
                        func.lower(Symbol.name) == token.lower(),
                        func.lower(Symbol.qualified_name) == token.lower(),
                    ),
                )
            ).all()
        )
        if ci:
            symbols = ci
            note = f"closest:{ci[0].name}"
        else:
            fuzzy = list(
                session.scalars(
                    select(Symbol)
                    .where(
                        Symbol.snapshot_id == snapshot_id,
                        or_(
                            Symbol.name.ilike(f"%{token}%"),
                            Symbol.qualified_name.ilike(f"%{token}%"),
                        ),
                    )
                    .order_by(func.length(Symbol.name).asc(), Symbol.name.asc())
                    .limit(5)
                ).all()
            )
            if not fuzzy:
                return [], "missing"
            symbols = [fuzzy[0]]
            note = f"closest:{fuzzy[0].name}"

    chunks: list[Chunk] = []
    seen: set[UUID] = set()
    for sym in symbols:
        by_symbol = list(
            session.scalars(
                select(Chunk)
                .where(Chunk.snapshot_id == snapshot_id, Chunk.symbol_id == sym.id)
                .order_by(Chunk.start_line.asc())
                .limit(limit)
            ).all()
        )
        overlapping = list(
            session.scalars(
                select(Chunk)
                .where(
                    Chunk.snapshot_id == snapshot_id,
                    Chunk.source_file_id == sym.source_file_id,
                    Chunk.start_line <= sym.start_line,
                    Chunk.end_line >= sym.start_line,
                )
                .order_by(Chunk.start_line.asc())
                .limit(limit)
            ).all()
        )
        for c in [*by_symbol, *overlapping]:
            if c.id in seen:
                continue
            seen.add(c.id)
            chunks.append(c)
            if len(chunks) >= limit:
                return chunks, note
    return chunks, note


def merge_routed_ahead(
    routed: list[ChunkSearchResult],
    ranked: list[ChunkSearchResult],
) -> list[ChunkSearchResult]:
    """Put routed hits first while preserving uniqueness."""
    seen: set[UUID] = set()
    out: list[ChunkSearchResult] = []
    for item in [*routed, *ranked]:
        cid = item.chunk.id
        if cid in seen:
            continue
        seen.add(cid)
        out.append(item)
    return out
