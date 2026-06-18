from pathlib import Path

from eol_checker.parsers.gradle_catalog import GradleCatalogParser


def test_parses_gradle_version_catalog(tmp_path):
    catalog = tmp_path / "libs.versions.toml"
    catalog.write_text(
        """
[versions]
spring = "3.5.10"
guava = { strictly = "32.1.2-jre" }

[libraries]
spring-boot-web = { module = "org.springframework.boot:spring-boot-starter-web", version.ref = "spring" }
guava = { group = "com.google.guava", name = "guava", version.ref = "guava" }
junit = "org.junit.jupiter:junit-jupiter:5.10.2"
""".strip(),
        encoding="utf-8",
    )

    deps = GradleCatalogParser().parse(catalog)
    by_name = {dep.name: dep for dep in deps}

    assert by_name["spring-boot-starter-web"].version == "3.5.10"
    assert by_name["spring-boot-starter-web"].dep_type == "version-catalog"
    assert by_name["guava"].version == "32.1.2-jre"
    assert by_name["junit-jupiter"].purl == "pkg:maven/org.junit.jupiter/junit-jupiter@5.10.2"


def test_gradle_catalog_matches_only_catalog_name():
    parser = GradleCatalogParser()
    assert parser.matches(Path("libs.versions.toml"))
    assert not parser.matches(Path("other.toml"))
