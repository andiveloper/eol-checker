"""Static version resolution helpers.

These helpers improve real-world static scans without executing build tools.
They infer versions from nearby declarations (e.g. the Spring Boot Gradle plugin)
and from lockfiles when available.
"""

from __future__ import annotations

import json
import re
from dataclasses import replace
from pathlib import Path
from typing import Optional

from eol_checker.models import Dependency
from eol_checker.purl import build_purl, normalize_pypi_name

_GRADLE_LOCK = re.compile(r"^([^:#\s]+):([^:#\s]+):([^=\s]+)=")


def resolve_versions(dependencies: list[Dependency]) -> list[Dependency]:
    """Return dependencies with best-effort static version backfills applied."""

    lock_versions = _collect_lock_versions(dependencies)
    spring_boot_versions = _spring_boot_versions_by_source(dependencies)
    resolved: list[Dependency] = []
    for dependency in dependencies:
        version = dependency.version
        if version is None:
            version = lock_versions.get(_key(dependency))
        if version is None and _is_spring_boot_starter(dependency):
            version = spring_boot_versions.get(dependency.source_file)
        if version and version != dependency.version:
            resolved.append(_with_version(dependency, version))
        else:
            resolved.append(dependency)
    return resolved


def _spring_boot_versions_by_source(dependencies: list[Dependency]) -> dict[str, str]:
    versions: dict[str, str] = {}
    for dependency in dependencies:
        if (
            dependency.dep_type == "plugin"
            and dependency.namespace == "org.springframework.boot"
            and dependency.version
        ):
            versions[dependency.source_file] = dependency.version
    return versions


def _is_spring_boot_starter(dependency: Dependency) -> bool:
    return (
        dependency.ecosystem == "maven"
        and dependency.namespace == "org.springframework.boot"
        and dependency.name.startswith("spring-boot-")
        and dependency.dep_type != "plugin"
    )


def _with_version(dependency: Dependency, version: str) -> Dependency:
    return replace(
        dependency,
        version=version,
        purl=build_purl(
            dependency.ecosystem,
            dependency.name,
            version,
            namespace=dependency.namespace,
        ),
    )


def _key(dependency: Dependency) -> tuple[str, str]:
    return dependency.ecosystem, dependency.coordinate


def _collect_lock_versions(dependencies: list[Dependency]) -> dict[tuple[str, str], str]:
    roots = {Path(dependency.source_file).parent for dependency in dependencies}
    versions: dict[tuple[str, str], str] = {}
    for root in roots:
        versions.update(_gradle_lock_versions(root))
        versions.update(_poetry_lock_versions(root))
        versions.update(_package_lock_versions(root))
    return versions


def _gradle_lock_versions(root: Path) -> dict[tuple[str, str], str]:
    versions: dict[tuple[str, str], str] = {}
    for lockfile in _parents(root, "gradle.lockfile"):
        try:
            lines = lockfile.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for line in lines:
            match = _GRADLE_LOCK.match(line.strip())
            if not match:
                continue
            group, artifact, version = match.groups()
            versions[("maven", f"{group}:{artifact}")] = version
    return versions


def _poetry_lock_versions(root: Path) -> dict[tuple[str, str], str]:
    versions: dict[tuple[str, str], str] = {}
    for lockfile in _parents(root, "poetry.lock"):
        current_name: Optional[str] = None
        try:
            lines = lockfile.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for line in lines:
            stripped = line.strip()
            if stripped == "[[package]]":
                current_name = None
                continue
            if stripped.startswith("name = "):
                current_name = normalize_pypi_name(stripped.split("=", 1)[1].strip(" \"'"))
            elif stripped.startswith("version = ") and current_name:
                version = stripped.split("=", 1)[1].strip(" \"'")
                versions[("pypi", current_name)] = version
    return versions


def _package_lock_versions(root: Path) -> dict[tuple[str, str], str]:
    # Included for future npm support; harmless today because there is no npm parser yet.
    versions: dict[tuple[str, str], str] = {}
    for lockfile in _parents(root, "package-lock.json"):
        try:
            data = json.loads(lockfile.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for package_path, package in data.get("packages", {}).items():
            if not package_path.startswith("node_modules/"):
                continue
            name = package_path.removeprefix("node_modules/")
            version = package.get("version")
            if name and version:
                versions[("npm", name)] = version
    return versions


def _parents(root: Path, filename: str) -> list[Path]:
    candidates = []
    current = root.resolve()
    for directory in [current, *current.parents]:
        candidate = directory / filename
        if candidate.exists():
            candidates.append(candidate)
            break
    return candidates
