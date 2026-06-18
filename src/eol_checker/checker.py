"""Map parsed dependencies to endoflife.date products and evaluate EOL status.

endoflife.date tracks product *release cycles* (e.g. "3.2"), not every
artifact version, so version matching is done conservatively by matching the
declared version against a release cycle name on dot boundaries.
"""

from __future__ import annotations

import re
from typing import Optional

from eol_checker.eol_api import EolApiClient, EolApiError
from eol_checker.models import CheckResult, Dependency, ReleaseMatch, Report, Status

# Versions we cannot resolve to a concrete number (dynamic, ranges, variables,
# wildcards like "2.*", or unresolved Maven properties like "${x}").
_DYNAMIC_VERSION = re.compile(r"[+*\[\]()$]|latest|release|SNAPSHOT", re.IGNORECASE)


def check_dependencies(
    dependencies: list[Dependency],
    client: EolApiClient,
) -> Report:
    report = Report()
    for dependency in dependencies:
        report.results.append(_check_one(dependency, client))
    return report


def _check_one(dependency: Dependency, client: EolApiClient) -> CheckResult:
    if dependency.purl is None:
        return CheckResult(dependency, Status.UNMAPPED, detail="No purl could be built")

    try:
        product_name = client.find_product_for_purl(dependency.purl)
    except EolApiError as exc:
        return CheckResult(dependency, Status.API_ERROR, detail=str(exc))

    if not product_name:
        return CheckResult(
            dependency,
            Status.UNMAPPED,
            detail="Not tracked by endoflife.date",
        )

    try:
        product = client.product(product_name)
    except EolApiError as exc:
        return CheckResult(dependency, Status.API_ERROR, detail=str(exc))

    if not product:
        return CheckResult(
            dependency,
            Status.UNMAPPED,
            detail=f"Product '{product_name}' has no data",
        )

    if not dependency.version:
        return CheckResult(
            dependency,
            Status.UNKNOWN_VERSION,
            match=ReleaseMatch(product=product_name),
            detail="No version declared",
        )

    if _DYNAMIC_VERSION.search(dependency.version):
        return CheckResult(
            dependency,
            Status.UNSUPPORTED_VERSION,
            match=ReleaseMatch(product=product_name),
            detail=f"Dynamic version '{dependency.version}' not resolvable",
        )

    releases = product.get("releases", []) if isinstance(product, dict) else []
    release = _match_release(dependency.version, releases)
    if release is None:
        return CheckResult(
            dependency,
            Status.UNKNOWN_VERSION,
            match=ReleaseMatch(product=product_name),
            detail="Version did not match any tracked release cycle",
        )

    match = _to_release_match(product_name, release)
    status = Status.EOL if release.get("isEol") else Status.OK
    return CheckResult(dependency, status, match=match)


def _match_release(version: str, releases: list[dict]) -> Optional[dict]:
    """Return the best matching release cycle for a version.

    Prefers the longest cycle name that is a dotted prefix of the version
    (e.g. version "3.2.5" matches cycle "3.2" over "3").
    """

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


def _to_release_match(product_name: str, release: dict) -> ReleaseMatch:
    latest = release.get("latest")
    latest_version = None
    if isinstance(latest, dict):
        latest_version = latest.get("name")
    return ReleaseMatch(
        product=product_name,
        release_cycle=str(release.get("name")) if release.get("name") else None,
        eol_from=release.get("eolFrom"),
        is_eol=release.get("isEol"),
        is_maintained=release.get("isMaintained"),
        latest_version=latest_version,
    )
