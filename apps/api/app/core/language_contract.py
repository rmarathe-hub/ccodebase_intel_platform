"""Language-support honesty contract + discovery policy constants.

Discovery and routing must honor these lists. Deep analysis may be claimed
only for DEEP languages. Generic languages use parser-derived structure
without verified-deep claims (see docs/language-support.md).
"""

from __future__ import annotations

from enum import StrEnum
from pathlib import PurePosixPath


class SupportLevel(StrEnum):
    DEEP = "deep"
    GENERIC = "generic"
    SKIP = "skip"


class SkipReason(StrEnum):
    """Why a path was not indexed for searchable/deep analysis."""

    IGNORED_DIR = "ignored_dir"
    BINARY = "binary"
    OVERSIZED = "oversized"
    UNSUPPORTED_EXT = "unsupported_ext"
    SECRET_PATH = "secret_path"
    SYMLINK = "symlink"
    UNREADABLE = "unreadable"
    EMPTY_NAME = "empty_name"


DEEP_LANGUAGES: frozenset[str] = frozenset(
    {
        "python",
        "java",
        "typescript",
        "javascript",
    }
)

GENERIC_LANGUAGES: frozenset[str] = frozenset(
    {
        "c",
        "c++",
        "c#",
        "go",
        "rust",
        "ruby",
        "php",
        "kotlin",
        "swift",
        "scala",
        "shell",
        "sql",
        "html",
        "css",
        "configuration",
        "documentation",
    }
)

# Extension → language key used by discovery.
EXTENSION_LANGUAGE: dict[str, str] = {
    ".py": "python",
    ".java": "java",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".c": "c",
    ".h": "c",
    ".cpp": "c++",
    ".cc": "c++",
    ".cxx": "c++",
    ".hpp": "c++",
    ".hh": "c++",
    ".cs": "c#",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".php": "php",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".swift": "swift",
    ".scala": "scala",
    ".sh": "shell",
    ".bash": "shell",
    ".zsh": "shell",
    ".sql": "sql",
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".scss": "css",
    ".json": "configuration",
    ".yaml": "configuration",
    ".yml": "configuration",
    ".toml": "configuration",
    ".xml": "configuration",
    ".ini": "configuration",
    ".cfg": "configuration",
    ".conf": "configuration",
    ".md": "documentation",
    ".rst": "documentation",
    ".txt": "documentation",
    ".markdown": "documentation",
}

# Directory names (any depth) that cause the entire subtree to be skipped.
IGNORED_DIR_NAMES: frozenset[str] = frozenset(
    {
        ".git",
        "node_modules",
        ".venv",
        "venv",
        "target",
        "dist",
        "build",
        "coverage",
        "vendor",
        "__pycache__",
        ".tox",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".next",
        ".nuxt",
        "Pods",
        "DerivedData",
        ".idea",
        ".vscode",
        "htmlcov",
        "eggs",
        ".eggs",
        "site-packages",
    }
)

# Basename patterns treated as secret-bearing (SKIP, never deep/generic indexed).
SECRET_BASENAME_EXACT: frozenset[str] = frozenset(
    {
        ".env",
        ".env.local",
        ".env.production",
        ".env.development",
        "credentials.json",
        "service-account.json",
        "id_rsa",
        "id_ed25519",
        "id_ecdsa",
    }
)

SECRET_BASENAME_SUFFIXES: tuple[str, ...] = (
    ".pem",
    ".p12",
    ".pfx",
    ".key",
)

# Extensions treated as binary/media/archives without content sniffing.
BINARY_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".webp",
        ".ico",
        ".bmp",
        ".svg",
        ".pdf",
        ".zip",
        ".tar",
        ".gz",
        ".tgz",
        ".bz2",
        ".xz",
        ".7z",
        ".rar",
        ".exe",
        ".dll",
        ".so",
        ".dylib",
        ".o",
        ".a",
        ".class",
        ".jar",
        ".war",
        ".pyc",
        ".pyo",
        ".wasm",
        ".woff",
        ".woff2",
        ".ttf",
        ".eot",
        ".mp3",
        ".mp4",
        ".mov",
        ".avi",
        ".bin",
        ".dat",
        ".sqlite",
        ".db",
    }
)

# Special filenames without (or with special) extensions.
SPECIAL_FILENAMES: dict[str, str] = {
    "dockerfile": "configuration",
    "makefile": "configuration",
    "cmakelists.txt": "configuration",
    "gemfile": "configuration",
    "rakefile": "configuration",
    "procfile": "configuration",
    "license": "documentation",
    "licence": "documentation",
    "readme": "documentation",
    "changelog": "documentation",
}


def support_level_for_language(language: str) -> SupportLevel:
    key = language.lower().strip()
    if key in DEEP_LANGUAGES:
        return SupportLevel.DEEP
    if key in GENERIC_LANGUAGES:
        return SupportLevel.GENERIC
    return SupportLevel.SKIP


def support_level_for_extension(extension: str) -> SupportLevel:
    ext = extension.lower() if extension.startswith(".") else f".{extension.lower()}"
    language = EXTENSION_LANGUAGE.get(ext)
    if language is None:
        return SupportLevel.SKIP
    return support_level_for_language(language)


def claims_deep_analysis(language: str) -> bool:
    """Deep analysis may be claimed only for the deep language set."""
    return support_level_for_language(language) is SupportLevel.DEEP


def language_for_path(relative_path: str) -> str | None:
    """Return language key for a relative path, or None if unsupported."""
    name = PurePosixPath(relative_path.replace("\\", "/")).name
    lower_name = name.lower()
    if lower_name in SPECIAL_FILENAMES:
        return SPECIAL_FILENAMES[lower_name]
    suffix = PurePosixPath(lower_name).suffix
    if not suffix:
        return None
    return EXTENSION_LANGUAGE.get(suffix)


def is_secret_basename(basename: str) -> bool:
    lower = basename.lower()
    if lower in SECRET_BASENAME_EXACT:
        return True
    if lower.startswith(".env."):
        return True
    return any(lower.endswith(suffix) for suffix in SECRET_BASENAME_SUFFIXES)


def path_has_ignored_directory(relative_path: str) -> bool:
    """True if any path segment is an ignored directory name."""
    parts = PurePosixPath(relative_path.replace("\\", "/")).parts
    return any(part in IGNORED_DIR_NAMES for part in parts)
