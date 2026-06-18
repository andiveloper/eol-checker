"""Parser for Maven ``pom.xml`` files (maven ecosystem).

Best-effort, static parser. It reads dependencies, managed dependencies, and
the parent coordinate, resolving ``${property}`` placeholders defined within
the same POM. Versions inherited from a parent or BOM (declared elsewhere) are
left unknown.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional
from xml.etree import ElementTree

from eol_checker.models import Dependency
from eol_checker.parsers.base import BaseParser
from eol_checker.purl import build_purl

_PROPERTY = re.compile(r"\$\{([^}]+)\}")
_MAX_RESOLVE_DEPTH = 10


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _find(elem, name: str):
    for child in elem:
        if _local(child.tag) == name:
            return child
    return None


def _findall(elem, name: str):
    return [child for child in elem if _local(child.tag) == name]


def _text(elem, name: str) -> Optional[str]:
    if elem is None:
        return None
    child = _find(elem, name)
    if child is None or child.text is None:
        return None
    return child.text.strip()


class MavenPomParser(BaseParser):
    name = "maven"
    ecosystem = "maven"
    patterns = ("pom.xml",)

    def parse(self, path: Path) -> list[Dependency]:
        text = path.read_text(encoding="utf-8", errors="replace")
        try:
            root = ElementTree.fromstring(text)
        except ElementTree.ParseError:
            return []

        lines = text.splitlines()
        properties = self._collect_properties(root)
        source = str(path)
        deps: list[Dependency] = []

        parent = _find(root, "parent")
        if parent is not None:
            dep = self._dependency_from(parent, properties, source, lines, "parent")
            if dep is not None:
                deps.append(dep)

        for dependency in self._iter_dependencies(root):
            dep = self._dependency_from(
                dependency.elem, properties, source, lines, dependency.dep_type
            )
            if dep is not None:
                deps.append(dep)

        return deps

    def _collect_properties(self, root) -> dict:
        properties: dict[str, str] = {}
        props = _find(root, "properties")
        if props is not None:
            for child in props:
                if child.text is not None:
                    properties[_local(child.tag)] = child.text.strip()

        parent = _find(root, "parent")
        project_version = _text(root, "version") or _text(parent, "version")
        project_group = _text(root, "groupId") or _text(parent, "groupId")
        if project_version:
            properties.setdefault("project.version", project_version)
            properties.setdefault("version", project_version)
        if project_group:
            properties.setdefault("project.groupId", project_group)
        if parent is not None:
            parent_version = _text(parent, "version")
            if parent_version:
                properties.setdefault("project.parent.version", parent_version)
        return properties

    def _iter_dependencies(self, root):
        results = []
        direct = _find(root, "dependencies")
        if direct is not None:
            for dependency in _findall(direct, "dependency"):
                results.append(_Tagged(dependency, None))

        management = _find(root, "dependencyManagement")
        if management is not None:
            managed = _find(management, "dependencies")
            if managed is not None:
                for dependency in _findall(managed, "dependency"):
                    results.append(_Tagged(dependency, "managed"))
        return results

    def _dependency_from(self, elem, properties, source, lines, dep_type):
        group = _resolve(_text(elem, "groupId"), properties)
        artifact = _resolve(_text(elem, "artifactId"), properties)
        if not artifact:
            return None
        version = _resolve(_text(elem, "version"), properties)
        return Dependency(
            ecosystem=self.ecosystem,
            namespace=group,
            name=artifact,
            version=version,
            purl=build_purl(self.ecosystem, artifact, version, namespace=group),
            source_file=source,
            line=_find_line(lines, artifact),
            dep_type=dep_type,
            raw=None,
        )


class _Tagged:
    __slots__ = ("elem", "dep_type")

    def __init__(self, elem, dep_type):
        self.elem = elem
        self.dep_type = dep_type


def _resolve(value: Optional[str], properties: dict) -> Optional[str]:
    """Resolve ${property} placeholders using the POM property map."""
    if value is None:
        return None
    resolved = value
    for _ in range(_MAX_RESOLVE_DEPTH):
        match = _PROPERTY.search(resolved)
        if not match:
            return resolved
        key = match.group(1)
        if key not in properties:
            # Leave unresolved placeholder so the checker can flag it.
            return resolved
        resolved = resolved[: match.start()] + properties[key] + resolved[match.end() :]
    return resolved


def _find_line(lines, artifact: str) -> Optional[int]:
    pattern = re.compile(r"<artifactId>\s*" + re.escape(artifact) + r"\s*</artifactId>")
    for index, line in enumerate(lines, start=1):
        if pattern.search(line):
            return index
    return None
