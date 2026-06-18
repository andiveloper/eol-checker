# eol-checker

Scan dependency manifest files (or whole directories) and check the declared
package versions across lifecycle, vulnerability, and dependency-currency data
sources.

It parses explicitly declared dependencies, builds a [package URL (purl)](https://github.com/package-url/purl-spec)
for each, and combines findings from multiple data sources.

## Data sources

| Source | `--source` value | Purpose |
| --- | --- | --- |
| [endoflife.date](https://endoflife.date/) | `eol` | Product lifecycle / EOL checks for runtimes and frameworks. |
| [OSV.dev](https://osv.dev/) | `osv` | Known vulnerabilities for concrete package versions. |
| [deps.dev](https://deps.dev/) | `deps-dev` | Latest-version / dependency currency checks. |

The parser layer is pluggable. Supported formats:

| Format | Files matched | `--type` | Ecosystem |
| --- | --- | --- | --- |
| Gradle | `build.gradle`, `build.gradle.kts`, `*.gradle`, `*.gradle.kts` | `gradle` | maven |
| Gradle version catalog | `libs.versions.toml` | `gradle-catalog` | maven |
| Python pip | `requirements.txt`, `requirements*.txt`, `*-requirements.txt` | `pip` | pypi |
| Maven POM | `pom.xml` | `maven` | maven |

Adding more formats does not require changing the API or reporting layers.

## Requirements

- Python 3.9+
- Network access to `https://endoflife.date`, `https://api.osv.dev`, and
  `https://api.deps.dev` unless sources are disabled with `--source`.

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

# Write a Markdown report to a file
eol-checker samples/build.gradle --no-fail --output samples/build-report.md
```

See `samples/build-report.md` for an example Markdown report generated from
`samples/build.gradle`.

### Options

| Option | Description |
| --- | --- |
| `--format {markdown,json}` | Output format (default: `markdown`). |
| `--output PATH`, `-o PATH` | Write the report to a file instead of stdout. |
| `--type NAME` | Force a parser (`gradle`, `pip`, or `maven`) for explicitly passed files. |
| `--no-recursive` | Only scan the top level of given directories. |
| `--include-hidden` | Include hidden files/directories during discovery. |
| `--base-url URL` | Override the endoflife.date API base URL. |
| `--source eol,osv,deps-dev` | Comma-separated providers to run (default: all). |
| `--min-severity none|low|medium|high|critical|unknown` | Exit non-zero when top severity is at least this value (default: `high`). |
| `--no-fail` | Always exit `0`, even when findings meet `--min-severity`. |

Directory discovery skips noisy/vendored directories by default
(`.git`, `.gradle`, `build`, `node_modules`, `.venv`, `venv`, `target`,
`dist`, `__pycache__`).

### Exit codes

- `0`: completed; no finding meets `--min-severity` (or `--no-fail`).
- `1`: at least one dependency has a finding at or above `--min-severity`.
- `2`: invalid usage (e.g. unknown `--type` or `--source`).

## Output

Markdown is the default. It includes a severity summary, one row per dependency,
and a detailed findings section for non-`none` findings.

Main result columns:

- `EOL`: endoflife.date result (`supported`, EOL finding, unknown, or unmapped).
- `Vulns`: number of OSV vulnerabilities found for the concrete version, with
  CVE/OSV/GHSA identifiers when available; `error` means OSV could not be queried.
- `Latest version`: latest/default version from deps.dev when the current version is behind.
- `Severity`: the highest-impact finding from all enabled sources for that dependency.

Severity combines lifecycle, vulnerability, and version-currency signals into
one sortable value:

- `critical` / `high` / `medium` / `low`: vulnerability severity from OSV, an
  EOL finding, or a currency finding scaled by how far behind the latest version is.
- `unknown`: the tool found a relevant issue but could not confidently rank it
  (for example an unresolved version or provider API error).
- `none`: no enabled provider found a problem for that dependency.

## Development

```bash
source .venv/bin/activate
pytest
```

## Limitations

- Static parsing only by default; it does not execute build tools. Some static
  backfills are supported: Gradle version catalogs, `gradle.lockfile`,
  `poetry.lock`, and curated Spring Boot plugin/BOM mappings. Fully resolved
  transitive dependency graphs still require a future build-tool mode.
- endoflife.date tracks product lifecycles, not every artifact, so many
  dependencies will legitimately show as EOL `unmapped`; OSV/deps.dev are used
  for broad library coverage.
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

## Extending with new data sources

Add a provider in `src/eol_checker/providers/` implementing the `Provider`
protocol and register it in `default_providers()` in
`src/eol_checker/providers/base.py`. Providers emit `Finding` objects, which
are aggregated into the Markdown/JSON report automatically.
