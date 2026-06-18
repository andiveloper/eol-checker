from eol_checker.checker import check_dependencies
from eol_checker.eol_api import EolApiClient
from eol_checker.models import Dependency, Status

BASE = "https://eol.test/api/v1"

IDENTIFIERS = {
    "result": [
        {
            "identifier": "pkg:maven/org.springframework.boot/spring-boot-starter-web",
            "product": {"name": "spring-boot", "uri": f"{BASE}/products/spring-boot/"},
        }
    ],
}

PRODUCT = {
    "result": {
        "name": "spring-boot",
        "releases": [
            {
                "name": "2.7",
                "isEol": True,
                "eolFrom": "2023-11-18",
                "isMaintained": False,
                "latest": {"name": "2.7.18"},
            },
            {
                "name": "3.2",
                "isEol": False,
                "eolFrom": "2025-08-31",
                "isMaintained": True,
                "latest": {"name": "3.2.5"},
            },
        ],
    },
}


def _dep(version):
    return Dependency(
        ecosystem="maven",
        namespace="org.springframework.boot",
        name="spring-boot-starter-web",
        version=version,
        purl=(
            "pkg:maven/org.springframework.boot/spring-boot-starter-web"
            + (f"@{version}" if version else "")
        ),
        source_file="build.gradle",
        line=1,
    )


def _setup(httpx_mock):
    httpx_mock.add_response(url=f"{BASE}/identifiers/purl", json=IDENTIFIERS)
    httpx_mock.add_response(url=f"{BASE}/products/spring-boot", json=PRODUCT)


def test_eol_release_is_flagged(httpx_mock):
    _setup(httpx_mock)
    with EolApiClient(base_url=BASE) as client:
        report = check_dependencies([_dep("2.7.0")], client)
    result = report.results[0]
    assert result.status == Status.EOL
    assert result.match.release_cycle == "2.7"
    assert result.match.eol_from == "2023-11-18"
    assert result.match.latest_version == "2.7.18"


def test_supported_release_is_ok(httpx_mock):
    _setup(httpx_mock)
    with EolApiClient(base_url=BASE) as client:
        report = check_dependencies([_dep("3.2.5")], client)
    assert report.results[0].status == Status.OK


def test_unknown_version_when_no_cycle_matches(httpx_mock):
    _setup(httpx_mock)
    with EolApiClient(base_url=BASE) as client:
        report = check_dependencies([_dep("9.9.9")], client)
    assert report.results[0].status == Status.UNKNOWN_VERSION


def test_dynamic_version_unsupported(httpx_mock):
    _setup(httpx_mock)
    with EolApiClient(base_url=BASE) as client:
        report = check_dependencies([_dep("1.+")], client)
    assert report.results[0].status == Status.UNSUPPORTED_VERSION


def test_unmapped_when_no_purl_match(httpx_mock):
    httpx_mock.add_response(url=f"{BASE}/identifiers/purl", json={"result": []})
    dep = Dependency(
        ecosystem="maven",
        namespace="com.unknown",
        name="thing",
        version="1.0.0",
        purl="pkg:maven/com.unknown/thing@1.0.0",
        source_file="build.gradle",
        line=1,
    )
    with EolApiClient(base_url=BASE) as client:
        report = check_dependencies([dep], client)
    assert report.results[0].status == Status.UNMAPPED
