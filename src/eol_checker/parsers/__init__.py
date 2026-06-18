"""Manifest parsers for the dependency EOL checker."""

from eol_checker.parsers.base import (
    BaseParser,
    ManifestParser,
    ParserRegistry,
    default_registry,
)
from eol_checker.parsers.gradle import GradleParser
from eol_checker.parsers.maven import MavenPomParser
from eol_checker.parsers.requirements import RequirementsParser

__all__ = [
    "BaseParser",
    "ManifestParser",
    "ParserRegistry",
    "default_registry",
    "GradleParser",
    "RequirementsParser",
    "MavenPomParser",
]
