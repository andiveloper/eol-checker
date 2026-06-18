import httpx
import json

from eol_checker.models import Dependency, Severity
from eol_checker.providers.depsdev import DepsDevProvider
from eol_checker.providers.eol import EolProvider
from eol_checker.providers.osv import OsvProvider


def _dep(version="2.7.0"):
    return Dependency(
        ecosystem="maven",
        namespace="org.springframework.boot",
        name="spring-boot-starter-web",
        version=version,
        purl=f"pkg:maven/org.springframework.boot/spring-boot-starter-web@{version}",
        source_file="build.gradle",
        line=1,
    )


def test_eol_provider_uses_curated_spring_boot_mapping(httpx_mock):
    httpx_mock.add_response(
        url="https://eol.test/products/spring-boot",
        json={
            "result": {
                "releases": [
                    {
                        "name": "2.7",
                        "isEol": True,
                        "eolFrom": "2023-06-30",
                        "isMaintained": False,
                    }
                ]
            }
        },
    )

    provider = EolProvider(base_url="https://eol.test")
    findings = provider.check([_dep()])[_dep()]
    provider.close()

    assert findings[0].severity == Severity.HIGH
    assert findings[0].metadata["product"] == "spring-boot"


def test_osv_provider_batches_queries_and_enriches_vulnerability(httpx_mock):
    dep = _dep()
    httpx_mock.add_response(
        method="POST",
        url="https://api.osv.dev/v1/querybatch",
        json={"results": [{"vulns": [{"id": "GHSA-1234"}]}]},
    )
    httpx_mock.add_response(
        url="https://api.osv.dev/v1/vulns/GHSA-1234",
        json={
            "id": "GHSA-1234",
            "summary": "Example vulnerability",
            "database_specific": {"severity": "HIGH"},
            "affected": [{"ranges": [{"events": [{"fixed": "2.7.1"}]}]}],
        },
    )

    provider = OsvProvider()
    findings = provider.check([dep])[dep]
    provider.close()

    assert findings[0].identifier == "GHSA-1234"
    assert findings[0].severity == Severity.HIGH
    assert findings[0].fixed_version == "2.7.1"
    request = httpx_mock.get_requests()[0]
    payload = json.loads(request.content.decode())
    assert payload["queries"][0]["version"] == "2.7.0"
    assert (
        payload["queries"][0]["package"]["purl"]
        == "pkg:maven/org.springframework.boot/spring-boot-starter-web"
    )


def test_depsdev_provider_reports_outdated_versions(httpx_mock):
    dep = Dependency(
        ecosystem="pypi",
        name="django",
        version="4.2.0",
        purl="pkg:pypi/django@4.2.0",
        source_file="requirements.txt",
        line=1,
    )
    httpx_mock.add_response(
        url="https://api.deps.dev/v3/systems/PYPI/packages/django",
        json={"defaultVersion": "5.2.1"},
    )

    provider = DepsDevProvider()
    findings = provider.check([dep])[dep]
    provider.close()

    assert findings[0].source == "deps.dev"
    assert findings[0].latest_version == "5.2.1"
    assert findings[0].severity == Severity.MEDIUM


def test_osv_provider_ignores_versionless_dependencies(httpx_mock):
    dep = _dep(version=None)
    provider = OsvProvider(client=httpx.Client(transport=httpx.MockTransport(lambda _: None)))
    assert provider.check([dep]) == {}
    provider.close()
