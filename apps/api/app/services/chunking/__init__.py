"""Persist chunks for a snapshot and optionally enrich via LLMProvider."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID, uuid4

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import Settings, settings
from app.core.language_contract import SupportLevel
from app.models import Chunk, LlmEnrichmentCache, SourceFile
from app.services.chunking.deep_symbols import deep_chunks_from_symbols
from app.services.chunking.sql_chunks import chunk_sql_source
from app.services.chunking.treesitter_generic import (
    chunk_generic_source,
    supported_generic_languages,
)
from app.services.chunking.types import ExtractedChunk
from app.services.llm.budget import EnrichmentBudget, EnrichmentBudgetExceeded
from app.services.llm.factory import get_llm_provider
from app.services.llm.priority import EnrichmentPriority, pack_batches
from app.services.llm.schemas import EnrichmentItem
from app.services.llm.validation import ChunkEvidenceBounds, validate_enrichment_item


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def collect_generic_chunks(
    session: Session,
    *,
    snapshot_id: UUID,
    repo_root: Path,
) -> list[ExtractedChunk]:
    from app.services.chunking.config_chunking import chunk_configuration_file
    from app.services.chunking.markdown_chunks import chunk_markdown_source

    files = list(
        session.scalars(
            select(SourceFile).where(
                SourceFile.snapshot_id == snapshot_id,
                SourceFile.support_level == SupportLevel.GENERIC.value,
            )
        ).all()
    )
    out: list[ExtractedChunk] = []
    supported = supported_generic_languages()
    for file_row in files:
        if not file_row.language:
            continue
        text = _read_text(repo_root / file_row.path)
        if text is None:
            continue
        if file_row.language == "configuration":
            out.extend(chunk_configuration_file(source=text, path=file_row.path))
        elif file_row.language == "documentation":
            # Markdown AST for .md / .markdown; other docs as whole-file later.
            suffix = Path(file_row.path).suffix.lower()
            if suffix in {".md", ".markdown"}:
                out.extend(chunk_markdown_source(source=text, path=file_row.path))
        elif file_row.language == "sql":
            out.extend(chunk_sql_source(source=text, path=file_row.path))
        elif file_row.language in supported:
            out.extend(
                chunk_generic_source(
                    source=text, path=file_row.path, language=file_row.language
                )
            )
    return out


def _priority_for_chunk(chunk: ExtractedChunk) -> EnrichmentPriority:
    name = Path(chunk.path).name.lower()
    if name in {"readme.md", "readme.rst", "readme.txt", "architecture.md"}:
        return EnrichmentPriority.README_DOCS
    if name in {"main.go", "main.rs", "main.c", "program.cs", "app.rb"}:
        return EnrichmentPriority.ENTRY_POINT_CANDIDATE
    if chunk.chunk_type == "symbol" and chunk.verified_deep:
        return EnrichmentPriority.TOP_LEVEL_DECLARATION
    if chunk.language in {"sql", "configuration"} or "config" in chunk.path.lower():
        return EnrichmentPriority.CONFIGURATION_BUILD
    if chunk.chunk_type == "documentation_section":
        return EnrichmentPriority.README_DOCS
    if chunk.parent_context and "function" in (chunk.parent_context or "").lower():
        return EnrichmentPriority.TOP_LEVEL_DECLARATION
    return EnrichmentPriority.DEFAULT


def _cache_key(
    *,
    path: str,
    start_line: int,
    end_line: int,
    content_hash: str,
    parser_version: str,
    prompt_version: str,
    model: str,
) -> str:
    raw = (
        f"{path}:{start_line}:{end_line}|{content_hash}|{parser_version}|"
        f"{prompt_version}|{model}"
    )
    import hashlib

    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _apply_enrichment(
    session: Session,
    *,
    chunk_rows: list[Chunk],
    extracted: list[ExtractedChunk],
    cfg: Settings,
) -> int:
    if not cfg.llm_enrichment_active:
        return 0
    provider = get_llm_provider(cfg)
    if provider.provider_name == "none":
        return 0

    budget = EnrichmentBudget(
        max_requests=cfg.llm_max_requests_per_job,
        max_tokens=cfg.llm_max_tokens_per_job,
        max_estimated_cost_usd=cfg.llm_max_estimated_cost_usd_per_job,
    )
    by_key = {c.enrichment_key: c for c in extracted}
    row_by_key = {
        f"{r.path}:{r.start_line}:{r.end_line}:{r.content_hash}": r for r in chunk_rows
    }

    prioritized: list[tuple[EnrichmentPriority, ExtractedChunk]] = [
        (_priority_for_chunk(c), c) for c in extracted
    ]
    batches = pack_batches(prioritized, max_chunks_per_request=cfg.llm_max_chunks_per_request)
    enriched = 0
    model_name = cfg.llm_model or cfg.azure_openai_deployment or "unknown"

    for batch in batches:
        payloads: list[dict[str, object]] = []
        bounds_map: dict[str, ChunkEvidenceBounds] = {}
        for item in batch:
            assert isinstance(item, ExtractedChunk)
            payloads.append(
                {
                    "chunk_id": item.enrichment_key,
                    "path": item.path,
                    "language": item.language,
                    "support_level": item.support_level,
                    "parser_name": item.parser_name,
                    "parser_version": item.parser_version,
                    "start_line": item.start_line,
                    "end_line": item.end_line,
                    "parent_context": item.parent_context,
                    "content": item.content,
                    "numbered_lines": "\n".join(
                        f"{item.start_line + i}|{line}"
                        for i, line in enumerate(item.content.splitlines())
                    ),
                }
            )
            bounds_map[item.enrichment_key] = ChunkEvidenceBounds(
                chunk_id=item.enrichment_key,
                path=item.path,
                start_line=item.start_line,
                end_line=item.end_line,
                content=item.content,
            )

        # Cache: if every chunk hits, skip LLM call.
        cache_hits: list[EnrichmentItem] = []
        miss_payloads: list[dict[str, object]] = []
        pending_keys: set[str] = set()
        for payload in payloads:
            ext = by_key[str(payload["chunk_id"])]
            key = _cache_key(
                path=ext.path,
                start_line=ext.start_line,
                end_line=ext.end_line,
                content_hash=ext.content_hash,
                parser_version=ext.parser_version,
                prompt_version=cfg.llm_prompt_version,
                model=model_name,
            )
            cached = session.scalar(
                select(LlmEnrichmentCache).where(LlmEnrichmentCache.cache_key == key)
            )
            if cached is not None:
                try:
                    cache_hits.append(EnrichmentItem.model_validate_json(cached.response_json))
                    continue
                except Exception:
                    pass
            miss_payloads.append(payload)
            pending_keys.add(key)

        results: list[EnrichmentItem] = list(cache_hits)
        if miss_payloads:
            est_tokens = sum(len(str(p.get("content", ""))) // 4 for p in miss_payloads) + 500
            try:
                budget.consume(requests=1, tokens=est_tokens, cost_usd=0.01)
            except EnrichmentBudgetExceeded:
                break
            try:
                batch_result = provider.enrich_batch(
                    items=miss_payloads, prompt_version=cfg.llm_prompt_version
                )
            except Exception:
                # Fail closed: keep deterministic chunks.
                break
            for item in batch_result.items:
                validation = validate_enrichment_item(item, bounds_map)
                if not validation.ok:
                    row = row_by_key.get(item.chunk_id)
                    if row is not None:
                        row.validation_status = "rejected"
                        row.metadata_json = json.dumps({"validation_errors": validation.errors})
                    continue
                results.append(item)
                ext = by_key.get(item.chunk_id)
                if ext is None:
                    continue
                key = _cache_key(
                    path=ext.path,
                    start_line=ext.start_line,
                    end_line=ext.end_line,
                    content_hash=ext.content_hash,
                    parser_version=ext.parser_version,
                    prompt_version=cfg.llm_prompt_version,
                    model=model_name,
                )
                if key in pending_keys:
                    pending_keys.discard(key)
                    existing = session.scalar(
                        select(LlmEnrichmentCache).where(LlmEnrichmentCache.cache_key == key)
                    )
                    if existing is None:
                        session.add(
                            LlmEnrichmentCache(
                                id=uuid4(),
                                cache_key=key,
                                provider=batch_result.provider,
                                model=model_name,
                                prompt_version=cfg.llm_prompt_version,
                                response_json=item.model_dump_json(),
                            )
                        )

        for item in results:
            row = row_by_key.get(item.chunk_id)
            if row is None:
                continue
            row.llm_enriched = True
            row.llm_provider = provider.provider_name
            row.llm_model = model_name
            row.prompt_version = cfg.llm_prompt_version
            row.confidence = item.confidence
            row.validation_status = "accepted"
            row.semantic_label = item.semantic_label
            row.concise_summary = item.concise_summary
            row.probable_construct_type = item.probable_construct_type.value
            row.entry_point_likelihood = item.entry_point_likelihood
            enriched += 1
    return enriched


def replace_chunks_for_snapshot(
    session: Session,
    *,
    snapshot_id: UUID,
    repo_root: Path,
    cfg: Settings | None = None,
) -> tuple[int, int]:
    """Replace all chunks for a snapshot. Returns (chunk_count, enriched_count)."""
    conf = cfg or settings
    session.execute(delete(Chunk).where(Chunk.snapshot_id == snapshot_id))
    session.flush()

    extracted = deep_chunks_from_symbols(
        session, snapshot_id=snapshot_id, repo_root=repo_root
    )
    extracted.extend(collect_generic_chunks(session, snapshot_id=snapshot_id, repo_root=repo_root))
    # Dedupe by enrichment identity (path + lines + hash).
    deduped: dict[str, ExtractedChunk] = {}
    for ch in extracted:
        deduped[ch.enrichment_key] = ch
    extracted = list(deduped.values())

    files_by_path = {
        f.path: f
        for f in session.scalars(
            select(SourceFile).where(SourceFile.snapshot_id == snapshot_id)
        ).all()
    }

    rows: list[Chunk] = []
    for ch in extracted:
        file_row = files_by_path.get(ch.path)
        if file_row is None:
            continue
        row = Chunk(
            id=uuid4(),
            snapshot_id=snapshot_id,
            source_file_id=file_row.id,
            symbol_id=ch.symbol_id,
            path=ch.path,
            language=ch.language,
            support_level=ch.support_level,
            chunk_type=ch.chunk_type,
            start_line=ch.start_line,
            end_line=ch.end_line,
            content=ch.content,
            content_hash=ch.content_hash,
            parent_context=ch.parent_context,
            extraction_method=ch.extraction_method,
            parser_name=ch.parser_name,
            parser_version=ch.parser_version,
            verified_deep=ch.verified_deep,
            metadata_json=ch.metadata_json,
        )
        session.add(row)
        rows.append(row)
    session.flush()

    enriched = _apply_enrichment(
        session, chunk_rows=rows, extracted=extracted, cfg=conf
    )
    session.flush()
    return len(rows), enriched
