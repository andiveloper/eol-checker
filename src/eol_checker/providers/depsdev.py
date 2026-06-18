"""deps.dev provider for dependency currency/outdated findings."""

from __future__ import annotations

from typing import Optional
from urllib.parse import quote

import httpx
from packaging.version import InvalidVersion, Version

from eol_checker.models import Dependency, Finding, Severity

DEPS_DEV_BASE_URL = "https://api.deps.dev/v3"


class DepsDevProvider:
    """Checks whether dependency versions are behind the ecosystem default/latest."""

    name = "deps.dev"

    def __init__(
        self,
        *,
        base_url: str = DEPS_DEV_BASE_URL,
        client: Optional[httpx.Client] = None,
        timeout: float = 20.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._owns_client = client is None
        self._client = client or httpx.Client(
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": "eol-checker/0.1", "Accept": "application/json"},
        )
        self._cache: dict[tuple[str, str], Optional[dict]] = {}

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def check(self, dependencies: list[Dependency]) -> dict[Dependency, list[Finding]]:
        results: dict[Dependency, list[Finding]] = {}
        for dependency in dependencies:
            finding = self._check_one(dependency)
            if finding is not None:
                results.setdefault(dependency, []).append(finding)
        return results

    def _check_one(self, dependency: Dependency) -> Optional[Finding]:
        if not dependency.version:
            return None
        system = _system(dependency.ecosystem)
        if system is None:
            return None
        package_name = _package_name(dependency)
        data = self._package(system, package_name)
        if not data:
            return None
        latest = _latest_version(data)
        if not latest or latest == dependency.version:
            return None
        severity = _currency_severity(dependency.version, latest)
        if severity == Severity.NONE:
            return None
        return Finding(
            source=self.name,
            severity=severity,
            summary=f"{dependency.coordinate} is behind latest {latest}",
            detail=f"Current version {dependency.version}; latest/default version {latest}.",
            current_version=dependency.version,
            latest_version=latest,
            url=f"https://deps.dev/{system.lower()}/{quote(package_name, safe='')}",
        )

    def _package(self, system: str, package_name: str) -> Optional[dict]:
        cache_key = (system, package_name)
        if cache_key in self._cache:
            return self._cache[cache_key]
        url = f"{self._base_url}/systems/{system}/packages/{quote(package_name, safe='')}"
        try:
            response = self._client.get(url)
            if response.status_code == 404:
                self._cache[cache_key] = None
                return None
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, ValueError):
            self._cache[cache_key] = None
            return None
        self._cache[cache_key] = data
        return data


def _system(ecosystem: str) -> Optional[str]:
    if ecosystem == "maven":
        return "MAVEN"
    if ecosystem == "pypi":
        return "PYPI"
    return None


def _package_name(dependency: Dependency) -> str:
    if dependency.ecosystem == "maven" and dependency.namespace:
        return f"{dependency.namespace}:{dependency.name}"
    return dependency.name


def _latest_version(data: dict) -> Optional[str]:
    default_version = data.get("defaultVersion")
    if isinstance(default_version, str):
        return default_version
    versions = data.get("versions", [])
    for version in versions:
        version_key = version.get("versionKey", {})
        if version.get("isDefault") and version_key.get("version"):
            return version_key["version"]
    # Fall back to the final version in the list if deps.dev doesn't flag a default.
    for version in reversed(versions):
        version_key = version.get("versionKey", {})
        if version_key.get("version"):
            return version_key["version"]
    return None


def _currency_severity(current: str, latest: str) -> Severity:
    try:
        current_v = Version(current)
        latest_v = Version(latest)
    except InvalidVersion:
        return Severity.UNKNOWN if current != latest else Severity.NONE
    if current_v >= latest_v:
        return Severity.NONE
    current_major = current_v.release[0] if current_v.release else 0
    latest_major = latest_v.release[0] if latest_v.release else 0
    if latest_major - current_major >= 2:
        return Severity.HIGH
    if latest_major > current_major:
        return Severity.MEDIUM
    return Severity.LOW
