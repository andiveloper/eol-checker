from eol_checker.eol_api import EolApiClient

BASE = "https://eol.test/api/v1"

IDENTIFIERS = {
    "schema_version": "1.0.0",
    "generated_at": "2026-01-01T00:00:00+00:00",
    "total": 1,
    "result": [
        {
            "identifier": "pkg:maven/org.springframework.boot/spring-boot-starter-web",
            "product": {
                "name": "spring-boot",
                "uri": f"{BASE}/products/spring-boot/",
            },
        }
    ],
}

PRODUCT = {
    "schema_version": "1.0.0",
    "generated_at": "2026-01-01T00:00:00+00:00",
    "last_modified": "2026-01-01T00:00:00+00:00",
    "result": {
        "name": "spring-boot",
        "label": "Spring Boot",
        "releases": [
            {"name": "2.7", "isEol": True, "eolFrom": "2023-11-18"},
            {"name": "3.2", "isEol": False, "eolFrom": "2025-08-31"},
        ],
    },
}


def test_purl_index_maps_normalized_purl_to_product(httpx_mock):
    httpx_mock.add_response(url=f"{BASE}/identifiers/purl", json=IDENTIFIERS)
    with EolApiClient(base_url=BASE) as client:
        product = client.find_product_for_purl(
            "pkg:maven/org.springframework.boot/spring-boot-starter-web@2.7.0"
        )
    assert product == "spring-boot"


def test_purl_index_is_cached(httpx_mock):
    httpx_mock.add_response(url=f"{BASE}/identifiers/purl", json=IDENTIFIERS)
    with EolApiClient(base_url=BASE) as client:
        client.purl_index()
        client.purl_index()
    # Only one request should have been made despite two calls.
    assert len(httpx_mock.get_requests()) == 1


def test_product_returns_none_on_404(httpx_mock):
    httpx_mock.add_response(url=f"{BASE}/products/missing", status_code=404)
    with EolApiClient(base_url=BASE) as client:
        assert client.product("missing") is None


def test_product_returns_release_data(httpx_mock):
    httpx_mock.add_response(url=f"{BASE}/products/spring-boot", json=PRODUCT)
    with EolApiClient(base_url=BASE) as client:
        product = client.product("spring-boot")
    assert product["releases"][0]["name"] == "2.7"
