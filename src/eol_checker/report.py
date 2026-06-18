"""Render multi-source dependency reports as Markdown (default) or JSON."""

from __future__ import annotations

import json
from typing import Optional

from eol_checker.models import DependencyReport, Finding, Report, Severity


def render(report: Report, fmt: str = "markdown") -> str:
    if fmt == "json":
        return render_json(report)
    if fmt == "markdown":
        return render_markdown(report)
    raise ValueError(f"Unknown format: {fmt}")


def _cell(value: Optional[object]) -> str:
    if value is None or value == "":
        return "-"
    if value is True:
        return "yes"
    if value is False:
        return "no"
    # Escape pipes so they don't break the Markdown table.
    return str(value).replace("|", "\\|")


def render_markdown(report: Report) -> str:
    dependency_reports = report.dependency_reports
    total = len(dependency_reports)
    lines: list[str] = []
    lines.append("# Dependency Report")
    lines.append("")
    lines.append(f"Checked **{total}** dependencies across enabled data sources.")
    lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.append("| Top severity | Count |")
    lines.append("| --- | --- |")
    counts = _severity_counts(dependency_reports)
    for severity in _SEVERITY_ORDER:
        if severity.value in counts:
            lines.append(f"| {_severity_label(severity)} | {counts[severity.value]} |")
    lines.append("")

    lines.append("## Results")
    lines.append("")
    header = (
        "| File | Package | Version | Ecosystem | EOL | Vulns | Latest | Top severity |"
    )
    lines.append(header)
    lines.append("| " + " | ".join(["---"] * 8) + " |")

    for dep_report in _sorted_reports(dependency_reports):
        lines.append(_dependency_row(dep_report))
    lines.append("")

    detail_lines = _details(dependency_reports)
    if detail_lines:
        lines.append("## Findings")
        lines.append("")
        lines.extend(detail_lines)
        lines.append("")

    return "\n".join(lines)


_SEVERITY_ORDER = [
    Severity.CRITICAL,
    Severity.HIGH,
    Severity.MEDIUM,
    Severity.LOW,
    Severity.UNKNOWN,
    Severity.NONE,
]


def _severity_label(severity: Severity) -> str:
    return severity.value.replace("-", " ").title()


def _severity_counts(reports: list[DependencyReport]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for dep_report in reports:
        key = dep_report.top_severity.value
        counts[key] = counts.get(key, 0) + 1
    return counts


def _sorted_reports(reports: list[DependencyReport]) -> list[DependencyReport]:
    return sorted(
        reports,
        key=lambda r: (
            -r.top_severity.rank,
            r.dependency.source_file,
            r.dependency.line or 0,
        ),
    )


def _dependency_row(dep_report: DependencyReport) -> str:
    dep = dep_report.dependency
    cells = [
        _cell(dep.location),
        _cell(dep.coordinate),
        _cell(dep.version),
        _cell(dep.ecosystem),
        _cell(_eol_cell(dep_report)),
        _cell(_vuln_cell(dep_report)),
        _cell(_latest_cell(dep_report)),
        _cell(_severity_label(dep_report.top_severity)),
    ]
    return "| " + " | ".join(cells) + " |"


def _eol_cell(dep_report: DependencyReport) -> str:
    findings = dep_report.findings_by_source("eol")
    if not findings:
        return "unmapped"
    finding = findings[0]
    if finding.severity == Severity.HIGH:
        return finding.summary
    if finding.severity == Severity.NONE:
        eol_from = finding.metadata.get("eol_from")
        if eol_from:
            return f"supported (EOL: {eol_from})"
        return "supported"
    return finding.summary


def _vuln_cell(dep_report: DependencyReport) -> str:
    findings = dep_report.findings_by_source("osv")
    if not findings:
        return "0"
    return str(len(findings))


def _latest_cell(dep_report: DependencyReport) -> str:
    findings = dep_report.findings_by_source("deps.dev")
    if not findings:
        return "-"
    finding = findings[0]
    if finding.latest_version:
        return finding.latest_version
    return finding.summary


def _details(reports: list[DependencyReport]) -> list[str]:
    lines: list[str] = []
    for dep_report in _sorted_reports(reports):
        problem_findings = [
            finding
            for finding in dep_report.findings
            if finding.severity != Severity.NONE
        ]
        if not problem_findings:
            continue
        dep = dep_report.dependency
        lines.append(f"### `{dep.coordinate}`")
        lines.append("")
        lines.append(f"- Location: `{dep.location}`")
        for finding in problem_findings:
            text = (
                f"- `{finding.source}` / {_severity_label(finding.severity)}: "
                f"{finding.summary}"
            )
            if finding.identifier:
                text += f" (`{finding.identifier}`)"
            if finding.fixed_version:
                text += f"; fixed in `{finding.fixed_version}`"
            if finding.url:
                text += f" - {finding.url}"
            lines.append(text)
        lines.append("")
    return lines


def render_json(report: Report) -> str:
    payload = {
        "summary": _severity_counts(report.dependency_reports),
        "total": len(report.dependency_reports),
        "results": [_dependency_report_dict(r) for r in report.dependency_reports],
    }
    return json.dumps(payload, indent=2)


def _dependency_report_dict(dep_report: DependencyReport) -> dict:
    dep = dep_report.dependency
    return {
        "file": dep.source_file,
        "line": dep.line,
        "ecosystem": dep.ecosystem,
        "package": dep.coordinate,
        "version": dep.version,
        "purl": dep.purl,
        "dep_type": dep.dep_type,
        "top_severity": dep_report.top_severity.value,
        "findings": [_finding_dict(finding) for finding in dep_report.findings],
    }


def _finding_dict(finding: Finding) -> dict:
    return {
        "source": finding.source,
        "severity": finding.severity.value,
        "summary": finding.summary,
        "detail": finding.detail,
        "identifier": finding.identifier,
        "url": finding.url,
        "fixed_version": finding.fixed_version,
        "current_version": finding.current_version,
        "latest_version": finding.latest_version,
        "metadata": finding.metadata,
    }
