"""Command-line interface for the dependency EOL checker."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from eol_checker import __version__
from eol_checker.checker import check_dependencies
from eol_checker.discovery import DEFAULT_SKIP_DIRS, discover_manifests
from eol_checker.eol_api import DEFAULT_BASE_URL, EolApiClient
from eol_checker.models import Dependency, Report, Status
from eol_checker.parsers.base import ParserRegistry, default_registry
from eol_checker.report import render


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="eol-checker",
        description=(
            "Scan dependency manifests (files or directories) and check package "
            "versions against endoflife.date."
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
        "--no-fail",
        action="store_true",
        help="Always exit 0, even when EOL dependencies are found.",
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


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    registry = default_registry()

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

    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)

    if not dependencies:
        print("No dependencies found to check.", file=sys.stderr)
        report = Report()
    else:
        with EolApiClient(base_url=args.base_url) as client:
            report = check_dependencies(dependencies, client)

    output = render(report, fmt=args.format)

    if args.output:
        Path(args.output).write_text(output + "\n", encoding="utf-8")
    else:
        print(output)

    if report.has_eol and not args.no_fail:
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
