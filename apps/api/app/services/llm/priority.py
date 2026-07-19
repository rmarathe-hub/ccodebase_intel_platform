"""Priority helpers for enrichment batching (no LLM calls)."""

from __future__ import annotations

from enum import IntEnum


class EnrichmentPriority(IntEnum):
    REPOSITORY_SUMMARY = 0
    README_DOCS = 1
    TOP_LEVEL_DECLARATION = 2
    ENTRY_POINT_CANDIDATE = 3
    CONFIGURATION_BUILD = 4
    HIGH_VALUE_SEARCH = 5
    DEFAULT = 9


def pack_batches(
    prioritized: list[tuple[EnrichmentPriority, object]],
    *,
    max_chunks_per_request: int,
) -> list[list[object]]:
    """Pack items into batches; never forces one-item batches."""
    if max_chunks_per_request < 1:
        raise ValueError("max_chunks_per_request must be >= 1")
    ordered = [item for _, item in sorted(prioritized, key=lambda pair: int(pair[0]))]
    batches: list[list[object]] = []
    for i in range(0, len(ordered), max_chunks_per_request):
        batches.append(ordered[i : i + max_chunks_per_request])
    return batches
