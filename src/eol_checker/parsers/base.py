"""Parser plugin interface and registry.

A parser knows how to recognize and read a particular kind of manifest file
(Gradle build scripts today; `requirements.txt`, `pom.xml`, lockfiles in the
future). Each parser declares the filename patterns it supports so that
directory discovery can find candidate files automatically.
"""

from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Iterable, Optional, Protocol, runtime_checkable

from eol_checker.models import Dependency


@runtime_checkable
class ManifestParser(Protocol):
    """Protocol implemented by every manifest parser."""

    #: Stable identifier used for the `--type` override (e.g. "gradle").
    name: str

    #: Package ecosystem emitted by this parser (e.g. "maven", "pypi").
    ecosystem: str

    #: Glob patterns matched against a file name (not full path).
    patterns: tuple[str, ...]

    def matches(self, path: Path) -> bool:
        """Return True if this parser can handle the given file."""
        ...

    def parse(self, path: Path) -> list[Dependency]:
        """Parse a manifest file into normalized dependency records."""
        ...


class BaseParser:
    """Convenience base providing default `matches` via filename patterns."""

    name: str = ""
    ecosystem: str = ""
    patterns: tuple[str, ...] = ()

    def matches(self, path: Path) -> bool:
        return any(fnmatch.fnmatch(path.name, pattern) for pattern in self.patterns)

    def parse(self, path: Path) -> list[Dependency]:  # pragma: no cover - abstract
        raise NotImplementedError


class ParserRegistry:
    """Holds the available parsers and routes files to them."""

    def __init__(self, parsers: Optional[Iterable[ManifestParser]] = None) -> None:
        self._parsers: list[ManifestParser] = list(parsers) if parsers else []

    def register(self, parser: ManifestParser) -> None:
        self._parsers.append(parser)

    @property
    def parsers(self) -> list[ManifestParser]:
        return list(self._parsers)

    def all_patterns(self) -> set[str]:
        patterns: set[str] = set()
        for parser in self._parsers:
            patterns.update(parser.patterns)
        return patterns

    def by_name(self, name: str) -> Optional[ManifestParser]:
        for parser in self._parsers:
            if parser.name == name:
                return parser
        return None

    def for_file(self, path: Path) -> Optional[ManifestParser]:
        """Return the first parser whose patterns match the file name."""
        for parser in self._parsers:
            if parser.matches(path):
                return parser
        return None


def default_registry() -> ParserRegistry:
    """Build a registry pre-populated with all built-in parsers."""
    from eol_checker.parsers.gradle import GradleParser
    from eol_checker.parsers.gradle_catalog import GradleCatalogParser
    from eol_checker.parsers.maven import MavenPomParser
    from eol_checker.parsers.requirements import RequirementsParser

    return ParserRegistry(
        [GradleParser(), RequirementsParser(), MavenPomParser(), GradleCatalogParser()]
    )
