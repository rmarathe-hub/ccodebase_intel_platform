"""Persist discovery results as source_files rows for a snapshot."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.entities import SourceFile
from app.services.discovery import DiscoveredFile, DiscoveryResult


def replace_source_files_for_snapshot(
    session: Session,
    *,
    snapshot_id: UUID,
    discovery: DiscoveryResult,
) -> list[SourceFile]:
    """Idempotently replace all source_files for a snapshot with discovery output."""
    session.execute(delete(SourceFile).where(SourceFile.snapshot_id == snapshot_id))
    rows: list[SourceFile] = []
    for item in discovery.files:
        rows.append(_to_row(snapshot_id, item))
    session.add_all(rows)
    session.flush()
    return rows


def _to_row(snapshot_id: UUID, item: DiscoveredFile) -> SourceFile:
    return SourceFile(
        snapshot_id=snapshot_id,
        path=item.path,
        size_bytes=item.size_bytes,
        line_count=item.line_count,
        content_hash=item.content_hash,
        language=item.language,
        support_level=item.support_level.value,
        parser_name=None,
        parser_version=None,
        skip_reason=item.skip_reason.value if item.skip_reason else None,
        is_test_file=item.is_test_file,
        is_generated=item.is_generated,
        is_vendor=item.is_vendor,
        is_binary=item.is_binary,
    )
