import json

from eol_checker.models import Dependency, DependencyReport, Finding, Report, Severity
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
    finding = Finding(
        source="eol",
        severity=Severity.HIGH,
        summary="spring-boot 2.7 is EOL since 2023-11-18",
        detail="endoflife.date release cycle 2.7; EOL date: 2023-11-18.",
        metadata={"product": "spring-boot", "release_cycle": "2.7"},
    )
    return Report(dependency_reports=[DependencyReport(dep, [finding])])


def test_markdown_has_summary_and_table():
    output = render(_report(), fmt="markdown")
    assert "# Dependency Report" in output
    assert "## Summary" in output
    assert "| Top severity | Count |" in output
    assert "| High | 1 |" in output
    assert "spring-boot-starter-web" in output
    assert "build.gradle:8" in output
    assert "2023-11-18" in output


def test_json_structure():
    output = render(_report(), fmt="json")
    data = json.loads(output)
    assert data["total"] == 1
    assert data["summary"]["high"] == 1
    result = data["results"][0]
    assert result["top_severity"] == "high"
    assert result["findings"][0]["metadata"]["product"] == "spring-boot"
    assert result["package"] == "org.springframework.boot:spring-boot-starter-web"


def test_markdown_escapes_pipes():
    dep = Dependency(
        ecosystem="maven",
        name="weird|name",
        version="1.0",
        purl=None,
        source_file="build.gradle",
    )
    report = Report(dependency_reports=[DependencyReport(dep)])
    output = render(report, fmt="markdown")
    assert "weird\\|name" in output


def test_supported_eol_cell_includes_eol_date():
    dep = Dependency(
        ecosystem="maven",
        namespace="org.springframework.boot",
        name="spring-boot-starter-web",
        version="3.5.10",
        purl="pkg:maven/org.springframework.boot/spring-boot-starter-web@3.5.10",
        source_file="build.gradle",
    )
    finding = Finding(
        source="eol",
        severity=Severity.NONE,
        summary="spring-boot 3.5 is supported",
        metadata={"eol_from": "2027-06-26"},
    )
    report = Report(dependency_reports=[DependencyReport(dep, [finding])])
    output = render(report, fmt="markdown")
    assert "supported (EOL: 2027-06-26)" in output
