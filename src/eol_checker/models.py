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


class Severity(str, Enum):
    """Provider-neutral severity scale used for aggregated findings."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

    @property
    def rank(self) -> int:
        return _SEVERITY_RANK[self.value]


_SEVERITY_RANK = {
    "none": 0,
    "unknown": 1,
    "low": 2,
    "medium": 3,
    "high": 4,
    "critical": 5,
}


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

    @property
    def location(self) -> str:
        if self.line:
            return f"{self.source_file}:{self.line}"
        return self.source_file


@dataclass
class Finding:
    """A finding emitted by one provider for one dependency."""

    source: str
    severity: Severity
    summary: str
    detail: Optional[str] = None
    identifier: Optional[str] = None
    url: Optional[str] = None
    fixed_version: Optional[str] = None
    current_version: Optional[str] = None
    latest_version: Optional[str] = None
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class DependencyReport:
    """All provider findings for a single dependency."""

    dependency: Dependency
    findings: list[Finding] = field(default_factory=list)

    @property
    def top_severity(self) -> Severity:
        if not self.findings:
            return Severity.NONE
        return max((finding.severity for finding in self.findings), key=lambda s: s.rank)

    def findings_by_source(self, source: str) -> list[Finding]:
        return [finding for finding in self.findings if finding.source == source]


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
    dependency_reports: list[DependencyReport] = field(default_factory=list)

    def counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for result in self.results:
            counts[result.status.value] = counts.get(result.status.value, 0) + 1
        if not self.results and self.dependency_reports:
            for dep_report in self.dependency_reports:
                severity = dep_report.top_severity.value
                counts[severity] = counts.get(severity, 0) + 1
        return counts

    @property
    def has_eol(self) -> bool:
        if any(r.status == Status.EOL for r in self.results):
            return True
        return any(
            finding.source == "eol" and finding.severity.rank >= Severity.HIGH.rank
            for dep_report in self.dependency_reports
            for finding in dep_report.findings
        )

    @property
    def max_severity(self) -> Severity:
        if not self.dependency_reports:
            return Severity.NONE
        return max(
            (dep_report.top_severity for dep_report in self.dependency_reports),
            key=lambda s: s.rank,
        )
