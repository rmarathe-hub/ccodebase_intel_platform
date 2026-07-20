"""Canonical relationship kinds for deep-language graphs.

CALLS remain stored in ``symbol_calls`` (high-volume call sites). All other
kinds use ``symbol_relations``. API consumers should treat both as the same
RelationKind vocabulary.
"""

from __future__ import annotations

import enum


class RelationKind(enum.StrEnum):
    IMPORTS = "imports"
    EXPORTS = "exports"
    CALLS = "calls"
    EXTENDS = "extends"
    IMPLEMENTS = "implements"
    REFERENCES = "references"
    INSTANTIATES = "instantiates"
    CONTAINS = "contains"


# Kinds rebuilt from symbols after language parsers finish (not Java inheritance).
STRUCTURAL_RELATION_KINDS: frozenset[str] = frozenset(
    {
        RelationKind.IMPORTS.value,
        RelationKind.EXPORTS.value,
        RelationKind.CONTAINS.value,
    }
)

# Kinds owned by language-specific persist (Java inheritance today).
INHERITANCE_RELATION_KINDS: frozenset[str] = frozenset(
    {
        RelationKind.EXTENDS.value,
        RelationKind.IMPLEMENTS.value,
    }
)

ALL_RELATION_KINDS: frozenset[str] = frozenset(k.value for k in RelationKind)

# Confidence labels shared by calls + relations.
RELATION_CONFIDENCES: frozenset[str] = frozenset(
    {"resolved", "ambiguous", "unresolved"}
)
