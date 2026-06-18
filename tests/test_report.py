import json

from eol_checker.models import CheckResult, Dependency, ReleaseMatch, Report, Status
from eol_checker.report import render


def _report():
    dep = Dependency(
        ecosystem="maven",
        namespace="org.springframework.boot",
        name="spring-boot-starter-web",
        version="2.7.0",
        purl="pkg:maven/org.springframework.boot/spring-boot-starter-web@2.7.0",
        source_file="build.gradle",
        line=8,
    )
    match = ReleaseMatch(
        product="spring-boot",
        release_cycle="2.7",
        eol_from="2023-11-18",
        is_eol=True,
        is_maintained=False,
        latest_version="2.7.18",
    )
    report = Report()
    report.results.append(CheckResult(dep, Status.EOL, match=match))
    return report


def test_markdown_has_summary_and_table():
    output = render(_report(), fmt="markdown")
    assert "# Dependency EOL Report" in output
    assert "## Summary" in output
    assert "| Status | Count |" in output
    assert "| EOL | 1 |" in output
    assert "spring-boot-starter-web" in output
    assert "build.gradle:8" in output
    assert "2023-11-18" in output


def test_json_structure():
    output = render(_report(), fmt="json")
    data = json.loads(output)
    assert data["total"] == 1
    assert data["summary"]["eol"] == 1
    result = data["results"][0]
    assert result["status"] == "eol"
    assert result["match"]["product"] == "spring-boot"
    assert result["package"] == "org.springframework.boot:spring-boot-starter-web"


def test_markdown_escapes_pipes():
    dep = Dependency(
        ecosystem="maven",
        name="weird|name",
        version="1.0",
        purl=None,
        source_file="build.gradle",
    )
    report = Report()
    report.results.append(CheckResult(dep, Status.UNMAPPED))
    output = render(report, fmt="markdown")
    assert "weird\\|name" in output
