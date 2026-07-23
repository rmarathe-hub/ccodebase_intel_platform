"""Deterministic repository summary + optional LLM-enhanced summary."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import Settings, settings
from app.core.language_contract import SupportLevel
from app.models import Chunk, SourceFile
from app.services.llm.factory import get_llm_provider
from app.services.llm.null_provider import NullLLMProvider
from app.services.llm.schemas import LineRange, RepositoryLlmSummary
from app.services.llm.validation import validate_repository_summary

# Filename hints only — candidates, not verified entry points.
_ENTRY_POINT_NAMES = frozenset(
    {
        "main.go",
        "main.rs",
        "main.c",
        "main.cpp",
        "main.py",
        "app.py",
        "program.cs",
        "index.js",
        "index.ts",
        "index.tsx",
        "manage.py",
        "wsgi.py",
        "asgi.py",
    }
)

_BUILD_HINTS = frozenset(
    {
        "package.json",
        "pom.xml",
        "cargo.toml",
        "go.mod",
        "build.gradle",
        "build.gradle.kts",
        "cmakelists.txt",
        "makefile",
        "dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        "pyproject.toml",
        "requirements.txt",
        "setup.py",
        "gemfile",
    }
)


def _is_test_dir(path: str) -> bool:
    parts = Path(path).parts
    return any(p.lower() in {"test", "tests", "__tests__", "spec", "specs"} for p in parts)


def _is_docs_dir(path: str) -> bool:
    parts = Path(path).parts
    name = Path(path).name.lower()
    return (
        any(p.lower() in {"docs", "doc", "documentation"} for p in parts)
        or name.startswith("readme")
        or name in {"architecture.md", "changelog.md"}
    )


def build_deterministic_summary(
    session: Session,
    *,
    snapshot_id: UUID,
) -> dict[str, object]:
    files = list(
        session.scalars(select(SourceFile).where(SourceFile.snapshot_id == snapshot_id)).all()
    )
    lang_counts: Counter[str] = Counter()
    support_counts: Counter[str] = Counter()
    skip_reasons: Counter[str] = Counter()
    important_dirs: set[str] = set()
    test_dirs: set[str] = set()
    doc_dirs: set[str] = set()
    build_systems: set[str] = set()
    config_files: list[str] = []
    doc_files: list[str] = []
    entry_candidates: list[str] = []
    parser_coverage: Counter[str] = Counter()

    for f in files:
        support_counts[f.support_level] += 1
        if f.language:
            lang_counts[f.language] += 1
        if f.skip_reason:
            skip_reasons[f.skip_reason] += 1
        if f.parser_name:
            parser_coverage[f.parser_name] += 1

        top = Path(f.path).parts[0] if Path(f.path).parts else ""
        if top and f.support_level != SupportLevel.SKIP.value:
            important_dirs.add(top)
        if _is_test_dir(f.path):
            test_dirs.add(str(Path(f.path).parts[0]) if Path(f.path).parts else f.path)
        if _is_docs_dir(f.path):
            doc_dirs.add(
                str(Path(f.path).parts[0])
                if Path(f.path).parts and Path(f.path).parts[0].lower() in {"docs", "doc"}
                else "docs"
            )
            if f.support_level == SupportLevel.GENERIC.value:
                doc_files.append(f.path)

        base = Path(f.path).name.lower()
        if base in _BUILD_HINTS or base.startswith("dockerfile"):
            build_systems.add(base)
        if f.language == "configuration":
            config_files.append(f.path)
        if base in _ENTRY_POINT_NAMES:
            entry_candidates.append(f.path)

    chunk_total = int(
        session.scalar(
            select(func.count()).select_from(Chunk).where(Chunk.snapshot_id == snapshot_id)
        )
        or 0
    )
    chunk_by_type = dict(
        session.execute(
            select(Chunk.chunk_type, func.count())
            .where(Chunk.snapshot_id == snapshot_id)
            .group_by(Chunk.chunk_type)
        ).all()
    )

    return {
        "language_mix": dict(lang_counts.most_common()),
        "support_level_mix": dict(support_counts),
        "important_directories": sorted(important_dirs)[:50],
        "test_directories": sorted(test_dirs)[:50],
        "documentation_directories": sorted(doc_dirs)[:50],
        "build_systems": sorted(build_systems),
        "configuration_files": sorted(config_files)[:100],
        "documentation_files": sorted(doc_files)[:100],
        "entry_point_candidates": sorted(entry_candidates)[:50],
        "chunk_counts": {
            "total": chunk_total,
            "by_type": {str(k): int(v) for k, v in chunk_by_type.items()},
        },
        "parser_coverage": dict(parser_coverage.most_common()),
        "skipped_file_counts": dict(skip_reasons),
        "file_count": len(files),
    }


def _select_evidence_chunks(session: Session, *, snapshot_id: UUID, limit: int = 12) -> list[Chunk]:
    """High-value chunks for LLM summary grounding."""
    rows = list(
        session.scalars(
            select(Chunk)
            .where(Chunk.snapshot_id == snapshot_id)
            .order_by(Chunk.path.asc(), Chunk.start_line.asc())
            .limit(500)
        ).all()
    )

    def score(c: Chunk) -> int:
        name = Path(c.path).name.lower()
        s = 0
        if name.startswith("readme") or "architecture" in name:
            s += 100
        if c.chunk_type == "documentation_section":
            s += 80
        if c.chunk_type == "configuration_section":
            s += 60
        if name in _ENTRY_POINT_NAMES:
            s += 70
        if c.verified_deep and c.chunk_type == "symbol":
            s += 40
        if c.parent_context and any(
            x in (c.parent_context or "").lower() for x in ("main", "app", "service")
        ):
            s += 20
        return s

    ranked = sorted(rows, key=score, reverse=True)
    return ranked[:limit]


def build_repository_summary(
    session: Session,
    *,
    snapshot_id: UUID,
    cfg: Settings | None = None,
) -> dict[str, object]:
    """Return deterministic_summary always; llm_summary only when enrichment active."""
    conf = cfg or settings
    deterministic = build_deterministic_summary(session, snapshot_id=snapshot_id)
    result: dict[str, object] = {
        "deterministic_summary": deterministic,
        "llm_summary": None,
        "llm_summary_status": "skipped",
        "evidence": [],
        "model_provenance": None,
    }

    if not conf.llm_enrichment_active:
        result["llm_summary_status"] = "disabled"
        return result

    provider = get_llm_provider(conf)
    if isinstance(provider, NullLLMProvider) or provider.provider_name == "none":
        result["llm_summary_status"] = "provider_unavailable"
        return result

    evidence_chunks = _select_evidence_chunks(session, snapshot_id=snapshot_id)
    if not evidence_chunks:
        result["llm_summary_status"] = "no_evidence"
        return result

    evidence_payload = [
        {
            "path": c.path,
            "start_line": c.start_line,
            "end_line": c.end_line,
            "chunk_type": c.chunk_type,
            "language": c.language,
            "content": c.content[:2000],
        }
        for c in evidence_chunks
    ]
    allowed_ranges = [(c.start_line, c.end_line) for c in evidence_chunks]
    result["evidence"] = [
        {
            "path": c.path,
            "start_line": c.start_line,
            "end_line": c.end_line,
        }
        for c in evidence_chunks
    ]

    try:
        llm_summary = provider.summarize_repository(
            deterministic_summary=deterministic,
            evidence=evidence_payload,
            prompt_version=conf.llm_prompt_version,
        )
    except Exception as exc:
        result["llm_summary_status"] = "error"
        result["model_provenance"] = {"error": str(exc)[:500]}
        return result

    validation = validate_repository_summary(llm_summary, allowed_ranges)
    # Also reject if claims verified deep
    if not validation.ok:
        result["llm_summary_status"] = "rejected"
        result["model_provenance"] = {
            "provider": llm_summary.provider,
            "model": llm_summary.model,
            "prompt_version": llm_summary.prompt_version,
            "validation_errors": validation.errors,
        }
        return result

    result["llm_summary"] = llm_summary.model_dump()
    result["llm_summary_status"] = "ok"
    result["model_provenance"] = {
        "provider": llm_summary.provider,
        "model": llm_summary.model,
        "prompt_version": llm_summary.prompt_version,
        "confidence": llm_summary.confidence,
    }
    return result


def mock_repository_summary(
    *,
    deterministic_summary: dict[str, object],
    evidence: list[dict[str, object]],
    prompt_version: str,
) -> RepositoryLlmSummary:
    """Test helper — no network."""
    _ = deterministic_summary
    if not evidence:
        raise ValueError("evidence required")
    first = evidence[0]
    start = int(first["start_line"])
    end = int(first["end_line"])
    return RepositoryLlmSummary(
        probable_architecture="mock layered service",
        major_components=["api", "worker"],
        likely_entry_points=[str(first.get("path", ""))],
        notable_frameworks=[],
        repository_purpose="mock purpose grounded in evidence",
        uncertainty_notes=["mock"],
        evidence_line_ranges=[LineRange(start_line=start, end_line=end)],
        confidence=0.4,
        claims_verified_deep=False,
        model="mock",
        prompt_version=prompt_version,
        provider="mock",
    )
