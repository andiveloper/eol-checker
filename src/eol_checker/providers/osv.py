"""OSV.dev vulnerability provider."""

from __future__ import annotations

import re
from typing import Optional

import httpx

from eol_checker.models import Dependency, Finding, Severity
from eol_checker.purl import purl_without_version

OSV_BASE_URL = "https://api.osv.dev/v1"
_DYNAMIC_VERSION = re.compile(r"[+*\[\]()$]|latest|release|SNAPSHOT", re.IGNORECASE)


class OsvProvider:
    """Checks package versions against OSV vulnerabilities."""

    name = "osv"

    def __init__(
        self,
        *,
        base_url: str = OSV_BASE_URL,
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
        self._vuln_cache: dict[str, dict] = {}

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def check(self, dependencies: list[Dependency]) -> dict[Dependency, list[Finding]]:
        query_deps = [
            dependency
            for dependency in dependencies
            if dependency.purl
            and dependency.version
            and not _DYNAMIC_VERSION.search(dependency.version)
        ]
        results: dict[Dependency, list[Finding]] = {}
        if not query_deps:
            return results

        payload = {
            "queries": [
                {
                    "version": dependency.version,
                    "package": {"purl": purl_without_version(dependency.purl)},
                }
                for dependency in query_deps
            ]
        }
        try:
            response = self._client.post(f"{self._base_url}/querybatch", json=payload)
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            error = Finding(
                source=self.name,
                severity=Severity.UNKNOWN,
                summary="OSV API error",
                detail=str(exc),
            )
            return {dependency: [error] for dependency in query_deps}

        for dependency, entry in zip(query_deps, data.get("results", [])):
            vulns = entry.get("vulns", []) if isinstance(entry, dict) else []
            findings = [self._finding_for_vuln(vuln) for vuln in vulns]
            if findings:
                results[dependency] = findings
        return results

    def _finding_for_vuln(self, vuln_ref: dict) -> Finding:
        vuln_id = vuln_ref.get("id") or "unknown"
        vuln = self._fetch_vuln(vuln_id)
        summary = vuln.get("summary") or vuln_ref.get("summary") or vuln_id
        severity = _severity(vuln)
        fixed_version = _fixed_version(vuln)
        return Finding(
            source=self.name,
            severity=severity,
            summary=summary,
            detail=vuln.get("details"),
            identifier=vuln_id,
            url=f"https://osv.dev/vulnerability/{vuln_id}",
            fixed_version=fixed_version,
            metadata={"aliases": vuln.get("aliases", [])},
        )

    def _fetch_vuln(self, vuln_id: str) -> dict:
        if vuln_id in self._vuln_cache:
            return self._vuln_cache[vuln_id]
        try:
            response = self._client.get(f"{self._base_url}/vulns/{vuln_id}")
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, ValueError):
            data = {"id": vuln_id}
        self._vuln_cache[vuln_id] = data
        return data


def _severity(vuln: dict) -> Severity:
    for severity in vuln.get("severity", []):
        score = severity.get("score", "")
        parsed = _parse_cvss(score)
        if parsed is not None:
            return _severity_from_score(parsed)
    database_specific = vuln.get("database_specific", {})
    value = str(database_specific.get("severity", "")).lower()
    if value in {s.value for s in Severity}:
        return Severity(value)
    return Severity.UNKNOWN


def _parse_cvss(score: str) -> Optional[float]:
    match = re.search(r"/AV:|CVSS:", score)
    if not match:
        try:
            return float(score)
        except ValueError:
            return None
    metric = re.search(r"/?([A-Z]{1,3}):", score)
    # OSV often stores vector only. Without full CVSS calculation, treat it as unknown.
    return None if metric else None


def _severity_from_score(score: float) -> Severity:
    if score >= 9.0:
        return Severity.CRITICAL
    if score >= 7.0:
        return Severity.HIGH
    if score >= 4.0:
        return Severity.MEDIUM
    if score > 0:
        return Severity.LOW
    return Severity.NONE


def _fixed_version(vuln: dict) -> Optional[str]:
    for affected in vuln.get("affected", []):
        for range_data in affected.get("ranges", []):
            for event in range_data.get("events", []):
                fixed = event.get("fixed")
                if fixed:
                    return fixed
    return None
