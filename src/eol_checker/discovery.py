"""Resolve file and directory inputs into a deterministic list of manifests.

Individual files are accepted as-is. Directories are scanned (recursively by
default) and any file matching a registered parser's patterns is collected.
Noisy/vendored directories are skipped unless overridden.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from eol_checker.parsers.base import ParserRegistry

DEFAULT_SKIP_DIRS = frozenset(
    {
        ".git",
        ".gradle",
        ".idea",
        "build",
        "node_modules",
        ".venv",
        "venv",
        "target",
        "dist",
        "__pycache__",
    }
)


@dataclass
class DiscoveryResult:
    """The outcome of resolving inputs."""

    files: list[Path]
    warnings: list[str]


def _is_hidden(name: str) -> bool:
    return name.startswith(".")


def discover_manifests(
    inputs: Iterable[str | Path],
    registry: ParserRegistry,
    *,
    recursive: bool = True,
    include_hidden: bool = False,
    skip_dirs: Iterable[str] = DEFAULT_SKIP_DIRS,
) -> DiscoveryResult:
    """Turn a mix of files and directories into a sorted, de-duplicated list."""

    skip = set(skip_dirs)
    found: set[Path] = set()
    warnings: list[str] = []

    for raw in inputs:
        path = Path(raw)
        if not path.exists():
            warnings.append(f"Path does not exist: {path}")
            continue
        if path.is_file():
            # Explicit files are always included; parser routing happens later.
            found.add(path.resolve())
            continue
        if path.is_dir():
            matches = _scan_directory(
                path,
                registry,
                recursive=recursive,
                include_hidden=include_hidden,
                skip=skip,
            )
            if not matches:
                warnings.append(f"No recognized manifest files found in: {path}")
            found.update(matches)

    return DiscoveryResult(files=sorted(found), warnings=warnings)


def _scan_directory(
    directory: Path,
    registry: ParserRegistry,
    *,
    recursive: bool,
    include_hidden: bool,
    skip: set[str],
) -> set[Path]:
    matches: set[Path] = set()

    if recursive:
        # Manual walk so we can prune skipped directories early.
        stack = [directory]
        while stack:
            current = stack.pop()
            for entry in _safe_iterdir(current):
                if entry.is_dir():
                    if entry.name in skip:
                        continue
                    if not include_hidden and _is_hidden(entry.name):
                        continue
                    stack.append(entry)
                elif entry.is_file():
                    if not include_hidden and _is_hidden(entry.name):
                        continue
                    if registry.for_file(entry) is not None:
                        matches.add(entry.resolve())
    else:
        for entry in _safe_iterdir(directory):
            if entry.is_file():
                if not include_hidden and _is_hidden(entry.name):
                    continue
                if registry.for_file(entry) is not None:
                    matches.add(entry.resolve())

    return matches


def _safe_iterdir(directory: Path) -> list[Path]:
    try:
        return list(directory.iterdir())
    except (PermissionError, OSError):
        return []
