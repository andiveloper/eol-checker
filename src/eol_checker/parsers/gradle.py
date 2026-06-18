"""Parser for Gradle build scripts (Groovy and Kotlin DSL).

This is a best-effort, text-based parser. It extracts explicitly declared
dependency coordinates and plugin versions. It deliberately does not execute
Gradle, so versions resolved via version catalogs, variables, BOMs, or
extra properties will not be resolved (see plan limitations).
"""

from __future__ import annotations

import re
from pathlib import Path

from eol_checker.models import Dependency
from eol_checker.parsers.base import BaseParser
from eol_checker.purl import build_purl

# A maven coordinate inside a quoted string: "group:artifact:version".
# Version is optional (it may come from a BOM/platform).
_STRING_COORD = re.compile(
    r"""["']
        (?P<group>[A-Za-z0-9_.\-]+)
        :
        (?P<artifact>[A-Za-z0-9_.\-]+)
        (?::(?P<version>[^"':\s]+))?
    ["']""",
    re.VERBOSE,
)

# A leading configuration name, e.g. implementation / testImplementation / api.
_CONFIG = re.compile(r"^(?P<config>[A-Za-z][A-Za-z0-9_]*)\s*[(\s]")

# Map-style notation: group: 'g', name: 'a', version: 'v' (order independent).
_MAP_GROUP = re.compile(r"group\s*:\s*[\"']([^\"']+)[\"']")
_MAP_NAME = re.compile(r"name\s*:\s*[\"']([^\"']+)[\"']")
_MAP_VERSION = re.compile(r"version\s*:\s*[\"']([^\"']+)[\"']")

# Plugin notation: id 'x.y.z' version '1.2.3'  /  id("x.y.z") version "1.2.3"
_PLUGIN = re.compile(
    r"""id\s*[(\s]\s*["'](?P<id>[A-Za-z0-9_.\-]+)["']\s*\)?
        (?:\s*version\s*[(\s]?\s*["'](?P<version>[^"')]+)["'])?""",
    re.VERBOSE,
)

_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
_LINE_COMMENT = re.compile(r"(?<!:)//.*$")


def _strip_block_comments(text: str) -> str:
    """Remove /* */ comments while preserving line numbers."""

    def _replace(match: re.Match) -> str:
        return "\n" * match.group(0).count("\n")

    return _BLOCK_COMMENT.sub(_replace, text)


class GradleParser(BaseParser):
    name = "gradle"
    ecosystem = "maven"
    patterns = ("build.gradle", "build.gradle.kts", "*.gradle", "*.gradle.kts")

    def parse(self, path: Path) -> list[Dependency]:
        text = path.read_text(encoding="utf-8", errors="replace")
        text = _strip_block_comments(text)
        source = str(path)
        deps: list[Dependency] = []

        for index, raw_line in enumerate(text.splitlines(), start=1):
            line = _LINE_COMMENT.sub("", raw_line).strip()
            if not line:
                continue

            plugin = self._parse_plugin(line, source, index)
            if plugin is not None:
                deps.append(plugin)
                continue

            map_dep = self._parse_map_notation(line, source, index)
            if map_dep is not None:
                deps.append(map_dep)
                continue

            string_dep = self._parse_string_notation(line, source, index)
            if string_dep is not None:
                deps.append(string_dep)

        return deps

    def _parse_plugin(self, line: str, source: str, lineno: int):
        if not line.lstrip().startswith("id"):
            return None
        match = _PLUGIN.search(line)
        if not match:
            return None
        plugin_id = match.group("id")
        version = match.group("version")
        # Gradle plugin marker artifact convention.
        artifact = f"{plugin_id}.gradle.plugin"
        return Dependency(
            ecosystem=self.ecosystem,
            namespace=plugin_id,
            name=artifact,
            version=version,
            purl=build_purl(self.ecosystem, artifact, version, namespace=plugin_id),
            source_file=source,
            line=lineno,
            dep_type="plugin",
            raw=line,
        )

    def _parse_map_notation(self, line: str, source: str, lineno: int):
        group_match = _MAP_GROUP.search(line)
        name_match = _MAP_NAME.search(line)
        if not group_match or not name_match:
            return None
        version_match = _MAP_VERSION.search(line)
        group = group_match.group(1)
        artifact = name_match.group(1)
        version = version_match.group(1) if version_match else None
        return Dependency(
            ecosystem=self.ecosystem,
            namespace=group,
            name=artifact,
            version=version,
            purl=build_purl(self.ecosystem, artifact, version, namespace=group),
            source_file=source,
            line=lineno,
            dep_type=self._config_name(line),
            raw=line,
        )

    def _parse_string_notation(self, line: str, source: str, lineno: int):
        match = _STRING_COORD.search(line)
        if not match:
            return None
        group = match.group("group")
        artifact = match.group("artifact")
        version = match.group("version")
        return Dependency(
            ecosystem=self.ecosystem,
            namespace=group,
            name=artifact,
            version=version,
            purl=build_purl(self.ecosystem, artifact, version, namespace=group),
            source_file=source,
            line=lineno,
            dep_type=self._config_name(line),
            raw=line,
        )

    @staticmethod
    def _config_name(line: str):
        match = _CONFIG.match(line)
        return match.group("config") if match else None
