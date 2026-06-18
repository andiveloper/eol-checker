"""Package URL (purl) construction helpers.

endoflife.date exposes a `purl` identifier type, so we normalize parsed
dependencies into purls to look them up. Each ecosystem has slightly different
rules; keep them isolated here so parsers stay simple.

See https://github.com/package-url/purl-spec for the spec.
"""

from __future__ import annotations

import re
from typing import Optional
from urllib.parse import quote


def _encode(segment: str) -> str:
    return quote(segment, safe="")


def normalize_pypi_name(name: str) -> str:
    """Normalize a PyPI project name per PEP 503 (lowercase, collapse -_.)."""
    return re.sub(r"[-_.]+", "-", name).strip().lower()


def build_purl(
    ecosystem: str,
    name: str,
    version: Optional[str] = None,
    namespace: Optional[str] = None,
) -> str:
    """Build a purl string like `pkg:maven/group/artifact@version`.

    The version is appended only when known. Namespace and name are percent
    encoded per segment, but the purl type stays lowercase and unescaped.
    """

    purl_type = ecosystem.lower()
    parts = [f"pkg:{purl_type}/"]
    if namespace:
        parts.append(f"{_encode(namespace)}/")
    parts.append(_encode(name))
    if version:
        parts.append(f"@{_encode(version)}")
    return "".join(parts)


def purl_without_version(purl: str) -> str:
    """Strip the `@version` suffix from a purl, if present."""
    at_index = purl.rfind("@")
    slash_index = purl.rfind("/")
    if at_index > slash_index:
        return purl[:at_index]
    return purl
