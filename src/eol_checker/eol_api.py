"""Typed-ish client for the endoflife.date API.

Only the endpoints needed by this tool are implemented:
- GET /identifiers/purl  -> map purl identifiers to products
- GET /products/{product} -> fetch a product's release cycles

The client follows redirects (products/categories may be renamed), uses a
timeout, and caches responses in-memory for the lifetime of the run.
"""

from __future__ import annotations

from typing import Optional

import httpx

from eol_checker.purl import purl_without_version

DEFAULT_BASE_URL = "https://endoflife.date/api/v1"
USER_AGENT = "eol-checker/0.1 (+https://endoflife.date)"


class EolApiError(RuntimeError):
    """Raised when the endoflife.date API cannot satisfy a request."""


class EolApiClient:
    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        client: Optional[httpx.Client] = None,
        timeout: float = 15.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._owns_client = client is None
        self._client = client or httpx.Client(
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        )
        self._purl_index: Optional[dict[str, str]] = None
        self._product_cache: dict[str, Optional[dict]] = {}

    def __enter__(self) -> "EolApiClient":
        return self

    def __exit__(self, *exc_info) -> None:
        self.close()

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def _get_json(self, path: str) -> dict:
        url = f"{self._base_url}/{path.lstrip('/')}"
        try:
            response = self._client.get(url)
        except httpx.HTTPError as exc:  # network/timeout
            raise EolApiError(f"Request to {url} failed: {exc}") from exc
        if response.status_code == 404:
            raise EolApiError(f"Not found: {url}")
        if response.status_code != 200:
            raise EolApiError(
                f"Unexpected status {response.status_code} from {url}"
            )
        try:
            return response.json()
        except ValueError as exc:
            raise EolApiError(f"Invalid JSON from {url}: {exc}") from exc

    def purl_index(self) -> dict[str, str]:
        """Return a mapping of normalized purl (no version) -> product name."""
        if self._purl_index is not None:
            return self._purl_index

        data = self._get_json("/identifiers/purl")
        index: dict[str, str] = {}
        for entry in data.get("result", []):
            identifier = entry.get("identifier")
            product = entry.get("product") or {}
            product_name = product.get("name")
            if not identifier or not product_name:
                continue
            key = _normalize_purl(identifier)
            index[key] = product_name
        self._purl_index = index
        return index

    def product(self, product: str) -> Optional[dict]:
        """Fetch a product's details, or None if it does not exist."""
        if product in self._product_cache:
            return self._product_cache[product]
        try:
            data = self._get_json(f"/products/{product}")
        except EolApiError:
            self._product_cache[product] = None
            return None
        result = data.get("result")
        self._product_cache[product] = result
        return result

    def find_product_for_purl(self, purl: str) -> Optional[str]:
        """Look up the product name for a given purl, ignoring its version."""
        index = self.purl_index()
        return index.get(_normalize_purl(purl))


def _normalize_purl(purl: str) -> str:
    return purl_without_version(purl).strip().lower()
