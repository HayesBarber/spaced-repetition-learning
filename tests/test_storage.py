import runpy

import pytest

from srl import storage


@pytest.mark.parametrize(
    ("value", "directory"),
    [(None, ".srl"), ("", ".srl"), ("~/aoc", "aoc"), ("relative/aoc", "relative/aoc")],
)
def test_data_directory_selection(tmp_path, monkeypatch, value, directory):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    if value is None:
        monkeypatch.delenv("SRL_DATA_DIR", raising=False)
    else:
        monkeypatch.setenv("SRL_DATA_DIR", value)

    paths = runpy.run_path(storage.__file__)
    expected = tmp_path / directory
    assert paths["DATA_DIR"].resolve() == expected
    for name in (
        "PROGRESS_FILE", "MASTERED_FILE", "NEXT_UP_FILE",
        "AUDIT_FILE", "CONFIG_FILE", "BACKUP_DIR",
    ):
        assert paths[name].parent.resolve() == expected
    paths["ensure_data_dir"]()
    assert expected.is_dir()


def test_data_directories_are_independent(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    saved = []
    for profile in ("leetcode", "aoc"):
        data_dir = tmp_path / profile
        monkeypatch.setenv("SRL_DATA_DIR", str(data_dir))
        paths = runpy.run_path(storage.__file__)
        assert paths["DATA_DIR"] == data_dir
        paths["ensure_data_dir"]()
        for name in ("PROGRESS_FILE", "NEXT_UP_FILE", "CONFIG_FILE"):
            path = paths[name]
            paths["save_json"](path, {"profile": profile})
            saved.append((path, profile))

    for path, profile in saved:
        assert storage.load_json(path) == {"profile": profile}
