"""Render a Report as Markdown (default) or JSON."""

from __future__ import annotations

import json
from typing import Optional

from eol_checker.models import CheckResult, Report, Status

_STATUS_LABEL = {
    Status.OK: "OK",
    Status.EOL: "EOL",
    Status.UNKNOWN_VERSION: "Unknown version",
    Status.UNMAPPED: "Unmapped",
    Status.UNSUPPORTED_VERSION: "Unsupported version",
    Status.API_ERROR: "API error",
}

# Order used for the summary section.
_SUMMARY_ORDER = [
    Status.EOL,
    Status.OK,
    Status.UNKNOWN_VERSION,
    Status.UNSUPPORTED_VERSION,
    Status.UNMAPPED,
    Status.API_ERROR,
]


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
    counts = report.counts()
    total = len(report.results)
    lines: list[str] = []
    lines.append("# Dependency EOL Report")
    lines.append("")
    lines.append(f"Checked **{total}** dependencies against endoflife.date.")
    lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.append("| Status | Count |")
    lines.append("| --- | --- |")
    for status in _SUMMARY_ORDER:
        if status.value in counts:
            lines.append(f"| {_STATUS_LABEL[status]} | {counts[status.value]} |")
    lines.append("")

    lines.append("## Results")
    lines.append("")
    header = (
        "| File | Package | Version | Ecosystem | Product | Cycle | "
        "EOL date | Maintained | Status |"
    )
    lines.append(header)
    lines.append("| " + " | ".join(["---"] * 9) + " |")

    for result in _sorted_results(report.results):
        lines.append(_result_row(result))
    lines.append("")

    return "\n".join(lines)


def _sorted_results(results: list[CheckResult]) -> list[CheckResult]:
    # Surface problems first, then group by file for readability.
    priority = {status: i for i, status in enumerate(_SUMMARY_ORDER)}
    return sorted(
        results,
        key=lambda r: (
            priority.get(r.status, 99),
            r.dependency.source_file,
            r.dependency.line or 0,
        ),
    )


def _result_row(result: CheckResult) -> str:
    dep = result.dependency
    match = result.match
    location = dep.source_file
    if dep.line:
        location = f"{location}:{dep.line}"
    cells = [
        _cell(location),
        _cell(dep.coordinate),
        _cell(dep.version),
        _cell(dep.ecosystem),
        _cell(match.product if match else None),
        _cell(match.release_cycle if match else None),
        _cell(match.eol_from if match else None),
        _cell(match.is_maintained if match else None),
        _cell(_STATUS_LABEL.get(result.status, result.status.value)),
    ]
    return "| " + " | ".join(cells) + " |"


def render_json(report: Report) -> str:
    payload = {
        "summary": report.counts(),
        "total": len(report.results),
        "results": [_result_dict(r) for r in report.results],
    }
    return json.dumps(payload, indent=2)


def _result_dict(result: CheckResult) -> dict:
    dep = result.dependency
    match = result.match
    return {
        "file": dep.source_file,
        "line": dep.line,
        "ecosystem": dep.ecosystem,
        "package": dep.coordinate,
        "version": dep.version,
        "purl": dep.purl,
        "dep_type": dep.dep_type,
        "status": result.status.value,
        "detail": result.detail,
        "match": None
        if match is None
        else {
            "product": match.product,
            "release_cycle": match.release_cycle,
            "eol_from": match.eol_from,
            "is_eol": match.is_eol,
            "is_maintained": match.is_maintained,
            "latest_version": match.latest_version,
        },
    }
