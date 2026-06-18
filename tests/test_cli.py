from eol_checker.cli import _find_git_root


def test_find_git_root_returns_parent_so_repo_name_is_displayed(tmp_path):
    repo = tmp_path / "eol-checker"
    nested = repo / "samples"
    nested.mkdir(parents=True)
    (repo / ".git").mkdir()

    assert _find_git_root(nested) == tmp_path.resolve()
