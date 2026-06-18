from pathlib import Path

from eol_checker.parsers.maven import MavenPomParser

FIXTURE = Path(__file__).parent / "fixtures" / "pom.xml"


def _by_name(deps):
    return {d.name: d for d in deps}


def test_parses_literal_version_and_purl():
    deps = MavenPomParser().parse(FIXTURE)
    names = _by_name(deps)
    junit = names["junit-jupiter"]
    assert junit.namespace == "org.junit.jupiter"
    assert junit.version == "5.10.2"
    assert junit.ecosystem == "maven"
    assert junit.purl == "pkg:maven/org.junit.jupiter/junit-jupiter@5.10.2"


def test_resolves_property_version():
    deps = MavenPomParser().parse(FIXTURE)
    guava = _by_name(deps)["guava"]
    assert guava.version == "32.1.2-jre"
    assert guava.purl == "pkg:maven/com.google.guava/guava@32.1.2-jre"


def test_parent_is_extracted():
    deps = MavenPomParser().parse(FIXTURE)
    parent = _by_name(deps)["spring-boot-starter-parent"]
    assert parent.dep_type == "parent"
    assert parent.version == "2.7.0"


def test_managed_dependency_tagged():
    deps = MavenPomParser().parse(FIXTURE)
    commons = _by_name(deps)["commons-lang3"]
    assert commons.dep_type == "managed"
    assert commons.version == "3.12.0"


def test_missing_version_is_none():
    deps = MavenPomParser().parse(FIXTURE)
    web = _by_name(deps)["spring-boot-starter-web"]
    assert web.version is None
    assert web.purl == "pkg:maven/org.springframework.boot/spring-boot-starter-web"


def test_line_numbers_best_effort():
    deps = MavenPomParser().parse(FIXTURE)
    junit = _by_name(deps)["junit-jupiter"]
    assert junit.line is not None


def test_matches_patterns():
    parser = MavenPomParser()
    assert parser.matches(Path("pom.xml"))
    assert not parser.matches(Path("requirements.txt"))
