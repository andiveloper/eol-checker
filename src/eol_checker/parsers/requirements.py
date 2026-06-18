"""Parser for Python ``requirements.txt`` files (pip / PyPI ecosystem).

This is a best-effort, text-based parser. It reads explicitly declared
requirements and extracts a concrete version only when the requirement is
pinned exactly (``==`` / ``===``). Includes (``-r``/``-c``) are not followed;
directory discovery picks up other requirement files separately.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from packaging.requirements import InvalidRequirement, Requirement

from eol_checker.models import Dependency
from eol_checker.parsers.base import BaseParser
from eol_checker.purl import build_purl, normalize_pypi_name

# Inline comment: a '#' that starts the line or is preceded by whitespace.
_INLINE_COMMENT = re.compile(r"(^|\s)#.*$")


class RequirementsParser(BaseParser):
    name = "pip"
    ecosystem = "pypi"
    patterns = ("requirements.txt", "requirements*.txt", "*-requirements.txt")

    def parse(self, path: Path) -> list[Dependency]:
        text = path.read_text(encoding="utf-8", errors="replace")
        source = str(path)
        deps: list[Dependency] = []

        for lineno, content in _logical_lines(text):
            line = _INLINE_COMMENT.sub("", content).strip()
            if not line:
                continue
            # Skip pip options and includes (-r, -c, -e, --hash, --index-url...).
            if line.startswith("-"):
                continue

            try:
                requirement = Requirement(line)
            except InvalidRequirement:
                continue

            name = normalize_pypi_name(requirement.name)
            version = _exact_version(requirement)
            deps.append(
                Dependency(
                    ecosystem=self.ecosystem,
                    name=name,
                    version=version,
                    purl=build_purl(self.ecosystem, name, version),
                    source_file=source,
                    line=lineno,
                    raw=line,
                )
            )
        return deps


def _logical_lines(text: str):
    """Yield (start_line_number, joined_content) handling ``\\`` continuations."""
    buffer = ""
    start_line: Optional[int] = None
    for index, raw in enumerate(text.splitlines(), start=1):
        if start_line is None:
            start_line = index
        if raw.endswith("\\"):
            buffer += raw[:-1] + " "
            continue
        buffer += raw
        yield start_line, buffer
        buffer = ""
        start_line = None
    if buffer:
        yield start_line or 1, buffer


def _exact_version(requirement: Requirement) -> Optional[str]:
    """Return the pinned version (``==``/``===``), or None for ranges/unpinned.

    Wildcard pins (e.g. ``2.*``) are returned raw so the checker can flag them
    as an unsupported version.
    """
    for spec in requirement.specifier:
        if spec.operator in ("==", "==="):
            return spec.version
    return None
