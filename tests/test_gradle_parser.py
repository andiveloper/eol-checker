from pathlib import Path

from eol_checker.parsers.gradle import GradleParser

FIXTURE = Path(__file__).parent / "fixtures" / "build.gradle"


def _by_name(deps):
    return {d.name: d for d in deps}


def test_parses_all_supported_notations():
    deps = GradleParser().parse(FIXTURE)
    names = _by_name(deps)

    # String notation with version.
    web = names["spring-boot-starter-web"]
    assert web.namespace == "org.springframework.boot"
    assert web.version == "2.7.0"
    assert web.ecosystem == "maven"
    assert web.purl == "pkg:maven/org.springframework.boot/spring-boot-starter-web@2.7.0"
    assert web.dep_type == "implementation"
    assert web.line == 7

    # Kotlin-style call notation.
    junit = names["junit-jupiter"]
    assert junit.version == "5.10.2"
    assert junit.dep_type == "testImplementation"

    # Map notation.
    guava = names["guava"]
    assert guava.namespace == "com.google.guava"
    assert guava.version == "32.1.2-jre"

    # Plugin notation becomes a marker artifact.
    plugin = names["org.springframework.boot.gradle.plugin"]
    assert plugin.version == "2.7.0"
    assert plugin.dep_type == "plugin"


def test_commented_dependencies_are_ignored():
    deps = GradleParser().parse(FIXTURE)
    assert all(d.name != "appear" for d in deps)


def test_version_optional_when_from_bom():
    deps = GradleParser().parse(FIXTURE)
    commons = next(d for d in deps if d.name == "commons-lang3")
    assert commons.version is None
    assert commons.purl == "pkg:maven/org.apache.commons/commons-lang3"


def test_dynamic_version_is_captured_raw():
    deps = GradleParser().parse(FIXTURE)
    dynamic = next(d for d in deps if d.name == "dynamic-artifact")
    assert dynamic.version == "1.+"


def test_matches_file_patterns(tmp_path):
    parser = GradleParser()
    assert parser.matches(Path("build.gradle"))
    assert parser.matches(Path("build.gradle.kts"))
    assert parser.matches(Path("settings.gradle"))
    assert not parser.matches(Path("requirements.txt"))
