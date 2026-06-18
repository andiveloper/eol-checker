"""endoflife.date provider for runtime/framework lifecycle findings."""

from __future__ import annotations

import importlib.resources
import re
from typing import Optional

try:  # Python 3.11+
    import tomllib  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - used on Python 3.9/3.10
    import tomli as tomllib  # type: ignore

from eol_checker.eol_api import DEFAULT_BASE_URL, EolApiClient, EolApiError
from eol_checker.models import Dependency, Finding, Severity
from eol_checker.purl import purl_without_version

_DYNAMIC_VERSION = re.compile(r"[+*\[\]()$]|latest|release|SNAPSHOT", re.IGNORECASE)


class EolProvider:
    """Checks mapped products against endoflife.date release cycles."""

    name = "eol"

    def __init__(
        self,
        *,
        base_url: Optional[str] = None,
        client: Optional[EolApiClient] = None,
    ) -> None:
        self._client = client or EolApiClient(base_url=base_url or DEFAULT_BASE_URL)
        self._owns_client = client is None
        self._product_map = _load_product_map()

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
        product_name = self._mapped_product(dependency)
        if not product_name and dependency.purl:
            try:
                product_name = self._client.find_product_for_purl(dependency.purl)
            except EolApiError as exc:
                return _api_error(str(exc))

        if not product_name:
            return None

        try:
            product = self._client.product(product_name)
        except EolApiError as exc:
            return _api_error(str(exc))

        if not product:
            return Finding(
                source=self.name,
                severity=Severity.UNKNOWN,
                summary=f"{product_name}: product data unavailable",
                detail=f"endoflife.date did not return product data for {product_name}.",
                metadata={"product": product_name},
            )

        if not dependency.version:
            return Finding(
                source=self.name,
                severity=Severity.UNKNOWN,
                summary=f"{product_name}: version unknown",
                detail="Dependency maps to an endoflife.date product, but no version was declared.",
                metadata={"product": product_name},
            )

        if _DYNAMIC_VERSION.search(dependency.version):
            return Finding(
                source=self.name,
                severity=Severity.UNKNOWN,
                summary=f"{product_name}: unsupported version {dependency.version}",
                detail="Dynamic or unresolved versions cannot be matched to an EOL cycle.",
                metadata={"product": product_name},
            )

        release = _match_release(dependency.version, product.get("releases", []))
        if release is None:
            return Finding(
                source=self.name,
                severity=Severity.UNKNOWN,
                summary=f"{product_name}: release cycle unknown",
                detail=f"Version {dependency.version} did not match a tracked release cycle.",
                metadata={"product": product_name},
            )

        is_eol = bool(release.get("isEol"))
        severity = Severity.HIGH if is_eol else Severity.NONE
        eol_from = release.get("eolFrom") or "unknown"
        cycle = release.get("name") or dependency.version
        return Finding(
            source=self.name,
            severity=severity,
            summary=(
                f"{product_name} {cycle} is EOL since {eol_from}"
                if is_eol
                else f"{product_name} {cycle} is supported"
            ),
            detail=f"endoflife.date release cycle {cycle}; EOL date: {eol_from}.",
            url=f"https://endoflife.date/{product_name}",
            metadata={
                "product": product_name,
                "release_cycle": cycle,
                "eol_from": release.get("eolFrom"),
                "is_eol": is_eol,
                "is_maintained": release.get("isMaintained"),
            },
        )

    def _mapped_product(self, dependency: Dependency) -> Optional[str]:
        if dependency.dep_type == "plugin" and dependency.namespace:
            product = self._product_map["gradle_plugins"].get(dependency.namespace)
            if product:
                return product
        if (
            dependency.ecosystem == "maven"
            and dependency.namespace == "org.springframework.boot"
            and dependency.name.startswith("spring-boot-")
        ):
            return "spring-boot"
        coordinate = dependency.coordinate
        return self._product_map["maven_artifacts"].get(coordinate)


def _api_error(detail: str) -> Finding:
    return Finding(
        source="eol",
        severity=Severity.UNKNOWN,
        summary="endoflife.date API error",
        detail=detail,
    )


def _match_release(version: str, releases: list[dict]) -> Optional[dict]:
    best: Optional[dict] = None
    best_len = -1
    for release in releases:
        name = str(release.get("name", ""))
        if not name:
            continue
        if version == name or version.startswith(name + "."):
            if len(name) > best_len:
                best = release
                best_len = len(name)
    return best


def _load_product_map() -> dict[str, dict[str, str]]:
    resource = importlib.resources.files("eol_checker.data").joinpath("product_map.toml")
    with resource.open("rb") as handle:
        data = tomllib.load(handle)
    return {
        "gradle_plugins": dict(data.get("gradle_plugins", {})),
        "maven_artifacts": {
            _normalize_coordinate(key): value
            for key, value in data.get("maven_artifacts", {}).items()
        },
    }


def _normalize_coordinate(coordinate: str) -> str:
    return purl_without_version(coordinate).strip()
