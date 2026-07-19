"""Filesystem discovery and classification for cloned repositories (Week 3).

Pure, side-effect-light walker: no code execution, no symlink following outside
the repo root, deterministic relative paths (POSIX style).
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from app.core.language_contract import (
    BINARY_EXTENSIONS,
    IGNORED_DIR_NAMES,
    SkipReason,
    SupportLevel,
    is_secret_basename,
    language_for_path,
    path_has_ignored_directory,
    support_level_for_language,
)

DEFAULT_MAX_FILE_BYTES = 1_048_576
DEFAULT_MAX_FILES = 50_000
DEFAULT_BINARY_SAMPLE_BYTES = 8192


@dataclass(frozen=True, slots=True)
class DiscoveredFile:
    """Result of classifying one path under a repository root."""

    path: str
    size_bytes: int
    line_count: int | None
    content_hash: str | None
    language: str | None
    support_level: SupportLevel
    skip_reason: SkipReason | None
    is_test_file: bool
    is_generated: bool
    is_vendor: bool
    is_binary: bool


@dataclass(frozen=True, slots=True)
class DiscoveryResult:
    files: tuple[DiscoveredFile, ...]
    truncated: bool
    walked_file_count: int

    @property
    def deep_count(self) -> int:
        return sum(1 for f in self.files if f.support_level is SupportLevel.DEEP)

    @property
    def generic_count(self) -> int:
        return sum(1 for f in self.files if f.support_level is SupportLevel.GENERIC)

    @property
    def skip_count(self) -> int:
        return sum(1 for f in self.files if f.support_level is SupportLevel.SKIP)


def normalize_relative_path(path: str) -> str:
    """Normalize to a POSIX relative path without leading ./ or /."""
    cleaned = path.replace("\\", "/").strip()
    while cleaned.startswith("./"):
        cleaned = cleaned[2:]
    cleaned = cleaned.lstrip("/")
    return str(PurePosixPath(cleaned)) if cleaned else ""


def looks_like_test_path(relative_path: str) -> bool:
    parts = [p.lower() for p in PurePosixPath(relative_path).parts]
    name = PurePosixPath(relative_path).name.lower()
    if any(p in {"test", "tests", "__tests__", "spec", "specs"} for p in parts[:-1]):
        return True
    if name.startswith("test_") or name.endswith("_test.py"):
        return True
    if ".test." in name or ".spec." in name:
        return True
    return False


def looks_like_generated_path(relative_path: str) -> bool:
    name = PurePosixPath(relative_path).name.lower()
    if name.endswith(".min.js") or name.endswith(".min.css"):
        return True
    if name.endswith(".generated.py") or name.endswith(".g.cs"):
        return True
    parts = {p.lower() for p in PurePosixPath(relative_path).parts}
    return bool(parts & {"generated", "gen", "autogen"})


def looks_like_vendor_path(relative_path: str) -> bool:
    parts = {p.lower() for p in PurePosixPath(relative_path).parts}
    return bool(parts & {"vendor", "third_party", "third-party", "external"})


def is_probably_binary(sample: bytes) -> bool:
    if not sample:
        return False
    if b"\x00" in sample:
        return True
    # High ratio of non-text bytes → binary
    textish = sum(1 for b in sample if b in (9, 10, 13) or 32 <= b <= 126)
    return (textish / len(sample)) < 0.70


def count_lines(data: bytes) -> int:
    if not data:
        return 0
    # Count newline separators; files without trailing newline still count as 1+ lines.
    return data.count(b"\n") + (0 if data.endswith(b"\n") else 1)


def _safe_resolve_under(root: Path, candidate: Path) -> Path | None:
    """Resolve candidate and ensure it stays under root (symlink escape guard)."""
    try:
        root_resolved = root.resolve()
        resolved = candidate.resolve()
    except OSError:
        return None
    try:
        resolved.relative_to(root_resolved)
    except ValueError:
        return None
    return resolved


def classify_file(
    *,
    relative_path: str,
    size_bytes: int,
    sample: bytes | None,
    full_content: bytes | None,
    is_symlink: bool,
    max_file_bytes: int,
) -> DiscoveredFile:
    """Classify a single file given already-read metadata/content."""
    path = normalize_relative_path(relative_path)
    if not path or path in {".", ".."}:
        return DiscoveredFile(
            path=path or ".",
            size_bytes=size_bytes,
            line_count=None,
            content_hash=None,
            language=None,
            support_level=SupportLevel.SKIP,
            skip_reason=SkipReason.EMPTY_NAME,
            is_test_file=False,
            is_generated=False,
            is_vendor=False,
            is_binary=False,
        )

    basename = PurePosixPath(path).name
    is_test = looks_like_test_path(path)
    is_generated = looks_like_generated_path(path)
    is_vendor = looks_like_vendor_path(path) or path_has_ignored_directory(path)

    if is_symlink:
        return DiscoveredFile(
            path=path,
            size_bytes=size_bytes,
            line_count=None,
            content_hash=None,
            language=None,
            support_level=SupportLevel.SKIP,
            skip_reason=SkipReason.SYMLINK,
            is_test_file=is_test,
            is_generated=is_generated,
            is_vendor=is_vendor,
            is_binary=False,
        )

    if path_has_ignored_directory(path):
        return DiscoveredFile(
            path=path,
            size_bytes=size_bytes,
            line_count=None,
            content_hash=None,
            language=None,
            support_level=SupportLevel.SKIP,
            skip_reason=SkipReason.IGNORED_DIR,
            is_test_file=is_test,
            is_generated=is_generated,
            is_vendor=True,
            is_binary=False,
        )

    if is_secret_basename(basename):
        return DiscoveredFile(
            path=path,
            size_bytes=size_bytes,
            line_count=None,
            content_hash=None,
            language=None,
            support_level=SupportLevel.SKIP,
            skip_reason=SkipReason.SECRET_PATH,
            is_test_file=is_test,
            is_generated=is_generated,
            is_vendor=is_vendor,
            is_binary=False,
        )

    suffix = PurePosixPath(basename.lower()).suffix
    if suffix in BINARY_EXTENSIONS:
        return DiscoveredFile(
            path=path,
            size_bytes=size_bytes,
            line_count=None,
            content_hash=None,
            language=None,
            support_level=SupportLevel.SKIP,
            skip_reason=SkipReason.BINARY,
            is_test_file=is_test,
            is_generated=is_generated,
            is_vendor=is_vendor,
            is_binary=True,
        )

    if size_bytes > max_file_bytes:
        return DiscoveredFile(
            path=path,
            size_bytes=size_bytes,
            line_count=None,
            content_hash=None,
            language=None,
            support_level=SupportLevel.SKIP,
            skip_reason=SkipReason.OVERSIZED,
            is_test_file=is_test,
            is_generated=is_generated,
            is_vendor=is_vendor,
            is_binary=False,
        )

    probe = sample if sample is not None else b""
    if is_probably_binary(probe):
        return DiscoveredFile(
            path=path,
            size_bytes=size_bytes,
            line_count=None,
            content_hash=None,
            language=None,
            support_level=SupportLevel.SKIP,
            skip_reason=SkipReason.BINARY,
            is_test_file=is_test,
            is_generated=is_generated,
            is_vendor=is_vendor,
            is_binary=True,
        )

    language = language_for_path(path)
    if language is None:
        return DiscoveredFile(
            path=path,
            size_bytes=size_bytes,
            line_count=None,
            content_hash=None,
            language=None,
            support_level=SupportLevel.SKIP,
            skip_reason=SkipReason.UNSUPPORTED_EXT,
            is_test_file=is_test,
            is_generated=is_generated,
            is_vendor=is_vendor,
            is_binary=False,
        )

    level = support_level_for_language(language)
    content = full_content if full_content is not None else probe
    digest = hashlib.sha256(content).hexdigest() if content is not None else None
    lines = count_lines(content) if content is not None else None

    return DiscoveredFile(
        path=path,
        size_bytes=size_bytes,
        line_count=lines,
        content_hash=digest,
        language=language,
        support_level=level,
        skip_reason=None if level is not SupportLevel.SKIP else SkipReason.UNSUPPORTED_EXT,
        is_test_file=is_test,
        is_generated=is_generated,
        is_vendor=is_vendor,
        is_binary=False,
    )


def discover_repository(
    repo_path: str | Path,
    *,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    max_files: int = DEFAULT_MAX_FILES,
    binary_sample_bytes: int = DEFAULT_BINARY_SAMPLE_BYTES,
) -> DiscoveryResult:
    """Walk a cloned repository and classify every regular file encountered.

    Symlinks are recorded as SKIP (never followed). Ignored directory names are
    pruned from the walk so their children are not visited.
    """
    root = Path(repo_path)
    if not root.is_dir():
        raise NotADirectoryError(f"Repository path is not a directory: {repo_path}")

    discovered: list[DiscoveredFile] = []
    walked = 0
    truncated = False

    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        current = Path(dirpath)

        # Prune ignored directories in-place (os.walk contract).
        dirnames[:] = sorted(
            name for name in dirnames if name not in IGNORED_DIR_NAMES and name != ".git"
        )

        # Skip if somehow still under an ignored path (defensive).
        try:
            rel_dir = current.relative_to(root).as_posix()
        except ValueError:
            continue
        if rel_dir != "." and path_has_ignored_directory(rel_dir):
            dirnames[:] = []
            continue

        for name in sorted(filenames):
            if truncated:
                break
            walked += 1
            if walked > max_files:
                truncated = True
                break

            candidate = current / name
            try:
                rel = candidate.relative_to(root).as_posix()
            except ValueError:
                continue

            is_link = candidate.is_symlink()
            if is_link:
                discovered.append(
                    classify_file(
                        relative_path=rel,
                        size_bytes=0,
                        sample=None,
                        full_content=None,
                        is_symlink=True,
                        max_file_bytes=max_file_bytes,
                    )
                )
                continue

            resolved = _safe_resolve_under(root, candidate)
            if resolved is None or not resolved.is_file():
                discovered.append(
                    DiscoveredFile(
                        path=normalize_relative_path(rel),
                        size_bytes=0,
                        line_count=None,
                        content_hash=None,
                        language=None,
                        support_level=SupportLevel.SKIP,
                        skip_reason=SkipReason.UNREADABLE,
                        is_test_file=looks_like_test_path(rel),
                        is_generated=looks_like_generated_path(rel),
                        is_vendor=looks_like_vendor_path(rel),
                        is_binary=False,
                    )
                )
                continue

            try:
                size = resolved.stat().st_size
            except OSError:
                discovered.append(
                    DiscoveredFile(
                        path=normalize_relative_path(rel),
                        size_bytes=0,
                        line_count=None,
                        content_hash=None,
                        language=None,
                        support_level=SupportLevel.SKIP,
                        skip_reason=SkipReason.UNREADABLE,
                        is_test_file=looks_like_test_path(rel),
                        is_generated=looks_like_generated_path(rel),
                        is_vendor=looks_like_vendor_path(rel),
                        is_binary=False,
                    )
                )
                continue

            # Fast path skips that do not need a full read.
            basename = PurePosixPath(rel).name
            suffix = PurePosixPath(basename.lower()).suffix
            if (
                path_has_ignored_directory(rel)
                or is_secret_basename(basename)
                or suffix in BINARY_EXTENSIONS
                or size > max_file_bytes
            ):
                discovered.append(
                    classify_file(
                        relative_path=rel,
                        size_bytes=size,
                        sample=None,
                        full_content=None,
                        is_symlink=False,
                        max_file_bytes=max_file_bytes,
                    )
                )
                continue

            try:
                with resolved.open("rb") as handle:
                    sample = handle.read(binary_sample_bytes)
                    if is_probably_binary(sample):
                        discovered.append(
                            classify_file(
                                relative_path=rel,
                                size_bytes=size,
                                sample=sample,
                                full_content=None,
                                is_symlink=False,
                                max_file_bytes=max_file_bytes,
                            )
                        )
                        continue
                    # Read remainder for hash/line count (bounded by max_file_bytes).
                    rest = handle.read(max(0, max_file_bytes - len(sample)))
                    content = sample + rest
            except OSError:
                discovered.append(
                    DiscoveredFile(
                        path=normalize_relative_path(rel),
                        size_bytes=size,
                        line_count=None,
                        content_hash=None,
                        language=None,
                        support_level=SupportLevel.SKIP,
                        skip_reason=SkipReason.UNREADABLE,
                        is_test_file=looks_like_test_path(rel),
                        is_generated=looks_like_generated_path(rel),
                        is_vendor=looks_like_vendor_path(rel),
                        is_binary=False,
                    )
                )
                continue

            discovered.append(
                classify_file(
                    relative_path=rel,
                    size_bytes=size,
                    sample=content[:binary_sample_bytes],
                    full_content=content,
                    is_symlink=False,
                    max_file_bytes=max_file_bytes,
                )
            )

        if truncated:
            break

    # Stable order by path for deterministic indexing output.
    discovered.sort(key=lambda item: item.path)
    return DiscoveryResult(
        files=tuple(discovered),
        truncated=truncated,
        walked_file_count=min(walked, max_files) if truncated else walked,
    )
