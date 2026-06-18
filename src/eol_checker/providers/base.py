"""Provider plugin interface and aggregation helpers."""

from __future__ import annotations

from typing import Iterable, Optional, Protocol, runtime_checkable

from eol_checker.models import Dependency, DependencyReport, Finding


@runtime_checkable
class Provider(Protocol):
    """A source of findings for parsed dependencies."""

    name: str

    def check(self, dependencies: list[Dependency]) -> dict[Dependency, list[Finding]]:
        """Return findings keyed by dependency."""
        ...

    def close(self) -> None:
        """Release provider resources."""
        ...


class ProviderRegistry:
    """Holds enabled providers and runs them over a dependency set."""

    def __init__(self, providers: Optional[Iterable[Provider]] = None) -> None:
        self._providers = list(providers) if providers else []

    @property
    def providers(self) -> list[Provider]:
        return list(self._providers)

    def by_name(self, name: str) -> Optional[Provider]:
        for provider in self._providers:
            if provider.name == name:
                return provider
        return None

    def close(self) -> None:
        for provider in self._providers:
            provider.close()

    def check(self, dependencies: list[Dependency]) -> list[DependencyReport]:
        return aggregate_findings(dependencies, self._providers)


def aggregate_findings(
    dependencies: list[Dependency], providers: Iterable[Provider]
) -> list[DependencyReport]:
    """Run providers and aggregate their findings per dependency."""

    reports = {dependency: DependencyReport(dependency) for dependency in dependencies}
    for provider in providers:
        findings_by_dependency = provider.check(dependencies)
        for dependency, findings in findings_by_dependency.items():
            if dependency in reports:
                reports[dependency].findings.extend(findings)
    return list(reports.values())


def default_providers(
    selection: Optional[Iterable[str]] = None,
    *,
    eol_base_url: Optional[str] = None,
) -> ProviderRegistry:
    """Build a provider registry for the selected provider names."""

    from eol_checker.providers.depsdev import DepsDevProvider
    from eol_checker.providers.eol import EolProvider
    from eol_checker.providers.osv import OsvProvider

    available = {
        "eol": EolProvider(base_url=eol_base_url),
        "osv": OsvProvider(),
        "deps-dev": DepsDevProvider(),
    }
    selected = list(selection) if selection else ["eol", "osv", "deps-dev"]
    return ProviderRegistry([available[name] for name in selected])
