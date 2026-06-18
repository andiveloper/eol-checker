from eol_checker.models import Dependency
from eol_checker.resolution import resolve_versions


def test_spring_boot_plugin_version_backfills_starters(tmp_path):
    build = tmp_path / "build.gradle"
    plugin = Dependency(
        ecosystem="maven",
        namespace="org.springframework.boot",
        name="org.springframework.boot.gradle.plugin",
        version="3.5.10",
        purl="pkg:maven/org.springframework.boot/org.springframework.boot.gradle.plugin@3.5.10",
        source_file=str(build),
        line=1,
        dep_type="plugin",
    )
    starter = Dependency(
        ecosystem="maven",
        namespace="org.springframework.boot",
        name="spring-boot-starter-web",
        version=None,
        purl="pkg:maven/org.springframework.boot/spring-boot-starter-web",
        source_file=str(build),
        line=2,
        dep_type="implementation",
    )

    resolved = resolve_versions([plugin, starter])

    assert resolved[1].version == "3.5.10"
    assert resolved[1].purl.endswith("@3.5.10")


def test_gradle_lockfile_backfills_maven_versions(tmp_path):
    build = tmp_path / "build.gradle"
    (tmp_path / "gradle.lockfile").write_text(
        "org.example:demo:1.2.3=runtimeClasspath\n", encoding="utf-8"
    )
    dep = Dependency(
        ecosystem="maven",
        namespace="org.example",
        name="demo",
        version=None,
        purl="pkg:maven/org.example/demo",
        source_file=str(build),
        line=1,
    )

    resolved = resolve_versions([dep])

    assert resolved[0].version == "1.2.3"
    assert resolved[0].purl == "pkg:maven/org.example/demo@1.2.3"


def test_poetry_lockfile_backfills_pypi_versions(tmp_path):
    req = tmp_path / "requirements.txt"
    (tmp_path / "poetry.lock").write_text(
        '[[package]]\nname = "Django"\nversion = "5.0.1"\n', encoding="utf-8"
    )
    dep = Dependency(
        ecosystem="pypi",
        name="django",
        version=None,
        purl="pkg:pypi/django",
        source_file=str(req),
        line=1,
    )

    resolved = resolve_versions([dep])

    assert resolved[0].version == "5.0.1"
    assert resolved[0].purl == "pkg:pypi/django@5.0.1"
