from pathlib import Path

from eol_checker.parsers.requirements import RequirementsParser

FIXTURE = Path(__file__).parent / "fixtures" / "requirements.txt"


def _by_name(deps):
    return {d.name: d for d in deps}


def test_exact_pin_yields_version_and_purl():
    deps = RequirementsParser().parse(FIXTURE)
    names = _by_name(deps)
    django = names["django"]
    assert django.version == "5.0.1"
    assert django.ecosystem == "pypi"
    assert django.purl == "pkg:pypi/django@5.0.1"
    assert django.line == 2


def test_name_is_pep503_normalized():
    deps = RequirementsParser().parse(FIXTURE)
    names = _by_name(deps)
    assert "flask-sqlalchemy" in names
    assert names["flask-sqlalchemy"].purl == "pkg:pypi/flask-sqlalchemy@3.1.1"


def test_unpinned_has_no_version():
    deps = RequirementsParser().parse(FIXTURE)
    names = _by_name(deps)
    assert names["requests"].version is None
    assert names["requests"].purl == "pkg:pypi/requests"


def test_range_has_no_version():
    deps = RequirementsParser().parse(FIXTURE)
    names = _by_name(deps)
    assert names["flask"].version is None


def test_wildcard_pin_passed_through_raw():
    deps = RequirementsParser().parse(FIXTURE)
    names = _by_name(deps)
    # urllib3==2.* is kept raw so the checker can flag it as unsupported.
    assert names["urllib3"].version == "2.*"


def test_extras_are_stripped_from_name():
    deps = RequirementsParser().parse(FIXTURE)
    names = _by_name(deps)
    assert "uvicorn" in names
    assert names["uvicorn"].version == "0.29.0"


def test_options_and_includes_are_skipped():
    deps = RequirementsParser().parse(FIXTURE)
    names = _by_name(deps)
    assert "base.txt" not in names
    assert all(not d.name.startswith("-") for d in deps)


def test_matches_patterns():
    parser = RequirementsParser()
    assert parser.matches(Path("requirements.txt"))
    assert parser.matches(Path("requirements-dev.txt"))
    assert parser.matches(Path("dev-requirements.txt"))
    assert not parser.matches(Path("pom.xml"))
