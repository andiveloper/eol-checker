# eol-checker

Scan dependency manifest files (or whole directories) and check the declared
package versions against [endoflife.date](https://endoflife.date/).

It parses explicitly declared dependencies, builds a [package URL (purl)](https://github.com/package-url/purl-spec)
for each, maps it to an endoflife.date product, and reports whether the version
you use falls in an end-of-life (EOL) release cycle.

The parser layer is pluggable. Supported formats:

| Format | Files matched | `--type` | Ecosystem |
| --- | --- | --- | --- |
| Gradle | `build.gradle`, `build.gradle.kts`, `*.gradle`, `*.gradle.kts` | `gradle` | maven |
| Python pip | `requirements.txt`, `requirements*.txt`, `*-requirements.txt` | `pip` | pypi |
| Maven POM | `pom.xml` | `maven` | maven |

Adding more formats does not require changing the API or reporting layers.

## Requirements

- Python 3.9+
- Network access to `https://endoflife.date`

## Setup (virtual environment)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

Scan one or more files and/or directories:

```bash
# A single build file
eol-checker path/to/build.gradle

# Python requirements or a Maven POM
eol-checker requirements.txt
eol-checker pom.xml

# A whole project tree (recursively discovers all supported manifests)
eol-checker path/to/project/

# Mix of files and directories
eol-checker build.gradle services/ requirements.txt pom.xml
```

### Options

| Option | Description |
| --- | --- |
| `--format {markdown,json}` | Output format (default: `markdown`). |
| `--output PATH`, `-o PATH` | Write the report to a file instead of stdout. |
| `--type NAME` | Force a parser (`gradle`, `pip`, or `maven`) for explicitly passed files. |
| `--no-recursive` | Only scan the top level of given directories. |
| `--include-hidden` | Include hidden files/directories during discovery. |
| `--base-url URL` | Override the endoflife.date API base URL. |
| `--no-fail` | Always exit `0`, even when EOL dependencies are found. |

Directory discovery skips noisy/vendored directories by default
(`.git`, `.gradle`, `build`, `node_modules`, `.venv`, `venv`, `target`,
`dist`, `__pycache__`).

### Exit codes

- `0`: completed; no EOL dependencies found (or `--no-fail`).
- `1`: at least one dependency is in an EOL release cycle.
- `2`: invalid usage (e.g. unknown `--type`).

## Output

Markdown is the default. It includes a summary table (counts per status) and a
results table with file, package, version, ecosystem, matched product, release
cycle, EOL date, maintained status, and overall status.

Statuses:

- `ok`: matched a release cycle that is not EOL.
- `eol`: matched an EOL release cycle.
- `unknown-version`: mapped to a product, but the version did not match a tracked cycle (or no version was declared).
- `unsupported-version`: dynamic version (e.g. `1.+`, `latest.release`) that cannot be resolved statically.
- `unmapped`: not tracked by endoflife.date.
- `api-error`: the API request failed.

## Development

```bash
source .venv/bin/activate
pytest
```

## Limitations

- Text-based parsing only; it does not execute build tools. Versions resolved
  through version catalogs, variables, BOMs/platforms, constraints, or
  transitive dependencies are not resolved.
- endoflife.date tracks product lifecycles, not every artifact, so many
  dependencies will legitimately be reported as `unmapped`.
- `requirements.txt`: includes (`-r`/`-c`) are not followed (discovery finds
  those files separately if present); only exact pins (`==`/`===`) yield a
  concrete version, ranges/unpinned report as `unknown-version`, and wildcard
  pins (e.g. `2.*`) as `unsupported-version`. Environment markers are ignored
  but the dependency is still listed.
- `pom.xml`: `${property}` resolution is limited to properties defined in the
  same POM; versions inherited from a parent or BOM are reported as
  `unknown-version`, and unresolved properties as `unsupported-version`. POM
  line numbers are best-effort.

## Extending with new formats

Add a parser in `src/eol_checker/parsers/` that subclasses `BaseParser`,
declares its `name`, `ecosystem`, and filename `patterns`, and implements
`parse()` to return `Dependency` records. Register it in `default_registry()`
in `src/eol_checker/parsers/base.py`. Discovery and reporting pick it up
automatically.
