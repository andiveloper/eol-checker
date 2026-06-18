"""Command-line interface for the dependency EOL checker."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from eol_checker import __version__
from eol_checker.discovery import DEFAULT_SKIP_DIRS, discover_manifests
from eol_checker.eol_api import DEFAULT_BASE_URL
from eol_checker.models import Dependency, Report, Severity
from eol_checker.parsers.base import ParserRegistry, default_registry
from eol_checker.providers.base import default_providers
from eol_checker.report import render
from eol_checker.resolution import resolve_versions


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="eol-checker",
        description=(
            "Scan dependency manifests (files or directories) and check package "
            "versions across EOL, vulnerability, and version-currency sources."
        ),
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="Manifest files and/or directories to scan.",
    )
    parser.add_argument(
        "--type",
        dest="type",
        default=None,
        help="Force a parser for explicitly passed files (e.g. gradle).",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format (default: markdown).",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Write the report to PATH instead of stdout.",
    )
    parser.add_argument(
        "--no-recursive",
        dest="recursive",
        action="store_false",
        help="Only scan the top level of given directories.",
    )
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden files/directories during discovery.",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"endoflife.date API base URL (default: {DEFAULT_BASE_URL}).",
    )
    parser.add_argument(
        "--source",
        default="eol,osv,deps-dev",
        help="Comma-separated providers to run: eol,osv,deps-dev (default: all).",
    )
    parser.add_argument(
        "--min-severity",
        choices=[severity.value for severity in Severity],
        default=Severity.HIGH.value,
        help="Exit non-zero when top severity is at least this value (default: high).",
    )
    parser.add_argument(
        "--no-fail",
        action="store_true",
        help="Always exit 0, even when findings meet --min-severity.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def _collect_dependencies(
    files: Sequence[Path],
    explicit_files: set,
    registry: ParserRegistry,
    forced_type: Optional[str],
    warnings: list,
) -> list[Dependency]:
    forced_parser = registry.by_name(forced_type) if forced_type else None
    dependencies: list[Dependency] = []

    for file in files:
        parser = None
        if forced_parser is not None and file.resolve() in explicit_files:
            parser = forced_parser
        if parser is None:
            parser = registry.for_file(file)
        if parser is None:
            warnings.append(f"No parser for file (skipped): {file}")
            continue
        try:
            dependencies.extend(parser.parse(file))
        except OSError as exc:
            warnings.append(f"Could not read {file}: {exc}")
    return dependencies


def _find_git_root(start: Path) -> Path:
    current = start.resolve()
    for directory in [current, *current.parents]:
        if (directory / ".git").exists():
            return directory.parent
    return current


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    registry = default_registry()
    selected_sources = [source.strip() for source in args.source.split(",") if source.strip()]
    valid_sources = {"eol", "osv", "deps-dev"}
    unknown_sources = sorted(set(selected_sources) - valid_sources)
    if unknown_sources:
        print(
            f"Unknown --source value(s): {', '.join(unknown_sources)}. "
            f"Available: {', '.join(sorted(valid_sources))}",
            file=sys.stderr,
        )
        return 2

    if args.type and registry.by_name(args.type) is None:
        available = ", ".join(sorted(p.name for p in registry.parsers))
        print(
            f"Unknown --type '{args.type}'. Available: {available}",
            file=sys.stderr,
        )
        return 2

    discovery = discover_manifests(
        args.paths,
        registry,
        recursive=args.recursive,
        include_hidden=args.include_hidden,
        skip_dirs=DEFAULT_SKIP_DIRS,
    )

    explicit_files = {
        Path(p).resolve() for p in args.paths if Path(p).is_file()
    }

    warnings: list[str] = list(discovery.warnings)
    dependencies = _collect_dependencies(
        discovery.files, explicit_files, registry, args.type, warnings
    )
    dependencies = resolve_versions(dependencies)

    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)

    if not dependencies:
        print("No dependencies found to check.", file=sys.stderr)
        report = Report()
    else:
        provider_registry = default_providers(
            selected_sources,
            eol_base_url=args.base_url,
        )
        try:
            report = Report(
                dependency_reports=provider_registry.check(dependencies)
            )
        finally:
            provider_registry.close()

    output = render(report, fmt=args.format, base_path=_find_git_root(Path.cwd()))

    if args.output:
        Path(args.output).write_text(output + "\n", encoding="utf-8")
    else:
        print(output)

    min_severity = Severity(args.min_severity)
    if report.max_severity.rank >= min_severity.rank and not args.no_fail:
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
