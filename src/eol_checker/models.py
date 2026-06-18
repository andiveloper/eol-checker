"""Core data models shared across parsers, the API client, and reporting.

These records are intentionally ecosystem-neutral so that new parsers
(`requirements.txt`, `pom.xml`, lockfiles, ...) can be added without changing
the API lookup or reporting layers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Status(str, Enum):
    """Outcome of checking a single dependency against endoflife.date."""

    OK = "ok"
    EOL = "eol"
    UNKNOWN_VERSION = "unknown-version"
    UNMAPPED = "unmapped"
    UNSUPPORTED_VERSION = "unsupported-version"
    API_ERROR = "api-error"


@dataclass(frozen=True)
class Dependency:
    """A single declared dependency parsed from a manifest file."""

    ecosystem: str
    name: str
    version: Optional[str]
    purl: Optional[str]
    source_file: str
    line: Optional[int] = None
    namespace: Optional[str] = None
    dep_type: Optional[str] = None
    raw: Optional[str] = None

    @property
    def coordinate(self) -> str:
        """A human-readable package coordinate, ecosystem dependent."""
        if self.namespace:
            return f"{self.namespace}:{self.name}"
        return self.name


@dataclass
class ReleaseMatch:
    """The endoflife.date product/release a dependency was matched to."""

    product: str
    release_cycle: Optional[str] = None
    eol_from: Optional[str] = None
    is_eol: Optional[bool] = None
    is_maintained: Optional[bool] = None
    latest_version: Optional[str] = None


@dataclass
class CheckResult:
    """The result of checking one dependency, used to build reports."""

    dependency: Dependency
    status: Status
    match: Optional[ReleaseMatch] = None
    detail: Optional[str] = None

    @property
    def is_problem(self) -> bool:
        return self.status in (Status.EOL, Status.API_ERROR)


@dataclass
class Report:
    """Aggregated results for a full run."""

    results: list[CheckResult] = field(default_factory=list)

    def counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for result in self.results:
            counts[result.status.value] = counts.get(result.status.value, 0) + 1
        return counts

    @property
    def has_eol(self) -> bool:
        return any(r.status == Status.EOL for r in self.results)
