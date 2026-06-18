"""Parser for Gradle version catalogs (`gradle/libs.versions.toml`)."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

try:  # Python 3.11+
    import tomllib  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - used on Python 3.9/3.10
    import tomli as tomllib  # type: ignore

from eol_checker.models import Dependency
from eol_checker.parsers.base import BaseParser
from eol_checker.purl import build_purl


class GradleCatalogParser(BaseParser):
    name = "gradle-catalog"
    ecosystem = "maven"
    patterns = ("libs.versions.toml",)

    def parse(self, path: Path) -> list[Dependency]:
        text = path.read_text(encoding="utf-8", errors="replace")
        try:
            data = tomllib.loads(text)
        except tomllib.TOMLDecodeError:
            return []

        versions = data.get("versions", {})
        libraries = data.get("libraries", {})
        deps: list[Dependency] = []
        for alias, value in libraries.items():
            parsed = _parse_library(value, versions)
            if parsed is None:
                continue
            group, artifact, version = parsed
            deps.append(
                Dependency(
                    ecosystem=self.ecosystem,
                    namespace=group,
                    name=artifact,
                    version=version,
                    purl=build_purl(self.ecosystem, artifact, version, namespace=group),
                    source_file=str(path),
                    line=_find_line(text.splitlines(), alias),
                    dep_type="version-catalog",
                    raw=alias,
                )
            )
        return deps


def _parse_library(value, versions: dict) -> Optional[tuple[str, str, Optional[str]]]:
    if isinstance(value, str):
        parts = value.split(":")
        if len(parts) == 3:
            return parts[0], parts[1], parts[2]
        if len(parts) == 2:
            return parts[0], parts[1], None
        return None

    if not isinstance(value, dict):
        return None

    module = value.get("module")
    group = value.get("group")
    name = value.get("name")
    if module:
        parts = str(module).split(":")
        if len(parts) != 2:
            return None
        group, name = parts
    if not group or not name:
        return None
    version = _catalog_version(value.get("version"), versions)
    return str(group), str(name), version


def _catalog_version(value, versions: dict) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if not isinstance(value, dict):
        return None
    if "ref" in value:
        ref = value["ref"]
        resolved = versions.get(ref)
        if isinstance(resolved, str):
            return resolved
        if isinstance(resolved, dict):
            return resolved.get("strictly") or resolved.get("require") or resolved.get("prefer")
    return value.get("strictly") or value.get("require") or value.get("prefer")


def _find_line(lines: list[str], alias: str) -> Optional[int]:
    needle = f"{alias} "
    for index, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith(f"{alias}=") or stripped.startswith(needle):
            return index
    return None
