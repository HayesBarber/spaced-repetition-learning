import json
import tarfile
from types import SimpleNamespace
import time

import pytest

from srl.commands import backup


@pytest.fixture
def test_dirs(tmp_path):
    data_dir = tmp_path / "data"
    backup_dir = tmp_path / "backups"
    data_dir.mkdir()
    backup_dir.mkdir()
    return tmp_path, data_dir, backup_dir


def _patch_backup_modules(monkeypatch, data_dir, backup_dir):
    monkeypatch.setattr("srl.storage.BACKUP_DIR", backup_dir)
    monkeypatch.setattr("srl.storage.DATA_DIR", data_dir)
    monkeypatch.setattr("srl.commands.backup.BACKUP_DIR", backup_dir)
    monkeypatch.setattr("srl.commands.backup.DATA_DIR", data_dir)


def test_backup_creates_archive(test_dirs, console, monkeypatch):
    tmp_path, data_dir, backup_dir = test_dirs
    _patch_backup_modules(monkeypatch, data_dir, backup_dir)

    backup.handle(SimpleNamespace(), console)

    archives = list(backup_dir.glob("backup-*.tar.gz"))
    assert len(archives) == 1


def test_backup_includes_all_storage_files(test_dirs, console, monkeypatch, tmp_path):
    tmp_path, data_dir, backup_dir = test_dirs
    for fname in ["problems_in_progress.json", "problems_mastered.json", "next_up.json", "audit.json", "config.json"]:
        (data_dir / fname).write_text("{}")

    _patch_backup_modules(monkeypatch, data_dir, backup_dir)

    backup.handle(SimpleNamespace(), console)

    archives = list(backup_dir.glob("backup-*.tar.gz"))
    with tarfile.open(archives[0], "r:gz") as tar:
        names = tar.getnames()
        assert "problems_in_progress.json" in names
        assert "problems_mastered.json" in names
        assert "next_up.json" in names
        assert "audit.json" in names
        assert "config.json" in names


def test_backup_manifest_valid(test_dirs, console, monkeypatch, tmp_path):
    tmp_path, data_dir, backup_dir = test_dirs
    for fname in ["problems_in_progress.json", "problems_mastered.json", "next_up.json", "audit.json", "config.json"]:
        (data_dir / fname).write_text("{}")

    _patch_backup_modules(monkeypatch, data_dir, backup_dir)

    backup.handle(SimpleNamespace(), console)

    archives = list(backup_dir.glob("backup-*.tar.gz"))
    with tarfile.open(archives[0], "r:gz") as tar:
        manifest_file = tar.extractfile("manifest.json")
        manifest = json.loads(manifest_file.read().decode())

        assert manifest["schema_version"] == 1
        assert "created_at" in manifest
        assert "files" in manifest


def test_backup_multiple_runs_unique_names(test_dirs, console, monkeypatch):
    tmp_path, data_dir, backup_dir = test_dirs
    for fname in ["problems_in_progress.json", "problems_mastered.json", "next_up.json", "audit.json", "config.json"]:
        (data_dir / fname).write_text("{}")

    _patch_backup_modules(monkeypatch, data_dir, backup_dir)

    backup.handle(SimpleNamespace(), console)
    time.sleep(0.01)
    backup.handle(SimpleNamespace(), console)

    archives = list(backup_dir.glob("backup-*.tar.gz"))
    assert len(archives) == 2

    names = sorted([a.name for a in archives])
    assert names[0] != names[1]


def test_backup_handles_empty_storage(test_dirs, console, monkeypatch):
    tmp_path, data_dir, backup_dir = test_dirs
    _patch_backup_modules(monkeypatch, data_dir, backup_dir)

    backup.handle(SimpleNamespace(), console)

    archives = list(backup_dir.glob("backup-*.tar.gz"))
    assert len(archives) == 1

    with tarfile.open(archives[0], "r:gz") as tar:
        manifest_file = tar.extractfile("manifest.json")
        manifest = json.loads(manifest_file.read().decode())

        assert manifest["schema_version"] == 1
        assert manifest["files"] == []