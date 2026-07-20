"""Chunk extraction types (parser-authoritative ranges)."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from uuid import UUID


def hash_content(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class ExtractedChunk:
    path: str
    language: str | None
    support_level: str
    chunk_type: str
    start_line: int
    end_line: int
    content: str
    content_hash: str
    parent_context: str | None
    extraction_method: str
    parser_name: str
    parser_version: str
    verified_deep: bool
    symbol_id: UUID | None = None
    metadata_json: str | None = None

    @staticmethod
    def make(
        *,
        path: str,
        language: str | None,
        support_level: str,
        chunk_type: str,
        start_line: int,
        end_line: int,
        content: str,
        parent_context: str | None,
        extraction_method: str,
        parser_name: str,
        parser_version: str,
        verified_deep: bool,
        symbol_id: UUID | None = None,
        metadata_json: str | None = None,
    ) -> ExtractedChunk:
        return ExtractedChunk(
            path=path,
            language=language,
            support_level=support_level,
            chunk_type=chunk_type,
            start_line=start_line,
            end_line=end_line,
            content=content,
            content_hash=hash_content(content),
            parent_context=parent_context,
            extraction_method=extraction_method,
            parser_name=parser_name,
            parser_version=parser_version,
            verified_deep=verified_deep,
            symbol_id=symbol_id,
            metadata_json=metadata_json,
        )

    @property
    def enrichment_key(self) -> str:
        return f"{self.path}:{self.start_line}:{self.end_line}:{self.content_hash}"
