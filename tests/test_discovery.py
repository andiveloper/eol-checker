from eol_checker.discovery import discover_manifests
from eol_checker.parsers.base import default_registry


def _make_tree(root):
    (root / "build.gradle").write_text("dependencies {}\n", encoding="utf-8")
    sub = root / "module"
    sub.mkdir()
    (sub / "build.gradle.kts").write_text("dependencies {}\n", encoding="utf-8")
    # Should be skipped by default.
    skipped = root / "build"
    skipped.mkdir()
    (skipped / "build.gradle").write_text("dependencies {}\n", encoding="utf-8")
    # Unrelated file.
    (root / "README.md").write_text("hi\n", encoding="utf-8")


def test_recursive_discovery_finds_manifests_and_skips_noise(tmp_path):
    _make_tree(tmp_path)
    result = discover_manifests([tmp_path], default_registry())
    names = sorted(p.name for p in result.files)
    assert names == ["build.gradle", "build.gradle.kts"]


def test_no_recursive_only_top_level(tmp_path):
    _make_tree(tmp_path)
    result = discover_manifests([tmp_path], default_registry(), recursive=False)
    names = sorted(p.name for p in result.files)
    assert names == ["build.gradle"]


def test_explicit_file_is_always_included(tmp_path):
    target = tmp_path / "anything.txt"
    target.write_text("x\n", encoding="utf-8")
    result = discover_manifests([target], default_registry())
    assert result.files == [target.resolve()]


def test_missing_path_produces_warning(tmp_path):
    missing = tmp_path / "nope"
    result = discover_manifests([missing], default_registry())
    assert result.files == []
    assert any("does not exist" in w for w in result.warnings)


def test_empty_directory_warns(tmp_path):
    result = discover_manifests([tmp_path], default_registry())
    assert any("No recognized manifest" in w for w in result.warnings)


def test_discovers_requirements_and_pom(tmp_path):
    (tmp_path / "requirements.txt").write_text("requests\n", encoding="utf-8")
    (tmp_path / "pom.xml").write_text("<project></project>\n", encoding="utf-8")
    sub = tmp_path / "service"
    sub.mkdir()
    (sub / "requirements-dev.txt").write_text("pytest\n", encoding="utf-8")
    result = discover_manifests([tmp_path], default_registry())
    names = sorted(p.name for p in result.files)
    assert names == ["pom.xml", "requirements-dev.txt", "requirements.txt"]
