import io
import json
import tarfile
from types import SimpleNamespace

import pytest

from srl.commands import backup


@pytest.fixture
def test_dirs(tmp_path):
    data_dir = tmp_path / "data"
    backup_dir = tmp_path / "backups"
    data_dir.mkdir()
    backup_dir.mkdir()
    return tmp_path, data_dir, backup_dir


def _create_archive(backup_dir, name, files=None, manifest_extra=None):
    path = backup_dir / name
    files = files or []
    manifest = {"schema_version": 1, "created_at": "2026-01-01T00:00:00+00:00", "files": [f[1] for f in files]}
    if manifest_extra:
        manifest.update(manifest_extra)

    with tarfile.open(path, "w:gz") as tar:
        for fpath, arcname in files:
            tar.add(fpath, arcname=arcname)
        manifest_data = json.dumps(manifest).encode()
        tarinfo = tarfile.TarInfo(name="manifest.json")
        tarinfo.size = len(manifest_data)
        tar.addfile(tarinfo, io.BytesIO(manifest_data))
    return path


def _patch(monkeypatch, data_dir, backup_dir):
    monkeypatch.setattr("srl.storage.BACKUP_DIR", backup_dir)
    monkeypatch.setattr("srl.storage.DATA_DIR", data_dir)
    monkeypatch.setattr("srl.commands.backup.BACKUP_DIR", backup_dir)
    monkeypatch.setattr("srl.commands.backup.DATA_DIR", data_dir)


def _get_output(console):
    return "".join(s.text for s in console._record_buffer)


class TestList:
    def test_empty_dir_shows_message(self, test_dirs, console, monkeypatch):
        tmp_path, data_dir, backup_dir = test_dirs
        _patch(monkeypatch, data_dir, backup_dir)

        backup.list_handle(SimpleNamespace(), console)

        assert "No backups found" in _get_output(console)

    def test_shows_all_backups(self, test_dirs, console, monkeypatch, tmp_path):
        tmp_path, data_dir, backup_dir = test_dirs
        _patch(monkeypatch, data_dir, backup_dir)

        for fname in ["problems_in_progress.json", "problems_mastered.json"]:
            (data_dir / fname).write_text("{}")

        _create_archive(backup_dir, "backup-2026-01-01T000000.tar.gz", [(data_dir / "problems_in_progress.json", "problems_in_progress.json")])
        _create_archive(backup_dir, "backup-2026-01-02T000000.tar.gz", [(data_dir / "problems_mastered.json", "problems_mastered.json")])

        backup.list_handle(SimpleNamespace(), console)

        output = _get_output(console)
        assert "backup-2026-01-01T000000.tar.gz" in output
        assert "backup-2026-01-02T000000.tar.gz" in output

    def test_parses_counter_suffix(self, test_dirs, console, monkeypatch, tmp_path):
        tmp_path, data_dir, backup_dir = test_dirs
        _patch(monkeypatch, data_dir, backup_dir)

        (data_dir / "test.json").write_text("{}")
        _create_archive(backup_dir, "backup-2026-01-01T000000-1.tar.gz", [(data_dir / "test.json", "test.json")])

        backup.list_handle(SimpleNamespace(), console)

        output = _get_output(console)
        assert "backup-2026-01-01T000000-1.tar.gz" in output


class TestVerify:
    def test_valid_archive(self, test_dirs, console, monkeypatch, tmp_path):
        tmp_path, data_dir, backup_dir = test_dirs
        _patch(monkeypatch, data_dir, backup_dir)

        (data_dir / "test.json").write_text("{}")
        archive = _create_archive(backup_dir, "backup-2026-01-01T000000.tar.gz", [(data_dir / "test.json", "test.json")])

        args = SimpleNamespace(file=str(archive))
        backup.verify_handle(args, console)

        assert "verified successfully" in _get_output(console)

    def test_valid_by_filename(self, test_dirs, console, monkeypatch, tmp_path):
        tmp_path, data_dir, backup_dir = test_dirs
        _patch(monkeypatch, data_dir, backup_dir)

        (data_dir / "test.json").write_text("{}")
        _create_archive(backup_dir, "backup-2026-01-01T000000.tar.gz", [(data_dir / "test.json", "test.json")])

        args = SimpleNamespace(file="backup-2026-01-01T000000.tar.gz")
        backup.verify_handle(args, console)

        assert "verified successfully" in _get_output(console)

    def test_corrupt_archive(self, test_dirs, console, monkeypatch, tmp_path):
        tmp_path, data_dir, backup_dir = test_dirs
        _patch(monkeypatch, data_dir, backup_dir)

        corrupt = backup_dir / "corrupt.tar.gz"
        corrupt.write_bytes(b"not a tar file")

        args = SimpleNamespace(file=str(corrupt))
        backup.verify_handle(args, console)

        output = _get_output(console)
        assert "Error" in output
        assert "Cannot open archive" in output

    def test_missing_manifest(self, test_dirs, console, monkeypatch, tmp_path):
        tmp_path, data_dir, backup_dir = test_dirs
        _patch(monkeypatch, data_dir, backup_dir)

        path = backup_dir / "no-manifest.tar.gz"
        with tarfile.open(path, "w:gz") as tar:
            info = tarfile.TarInfo(name="somefile.json")
            info.size = 0
            tar.addfile(info, io.BytesIO(b""))

        args = SimpleNamespace(file=str(path))
        backup.verify_handle(args, console)

        output = _get_output(console)
        assert "manifest.json not found" in output

    def test_invalid_json_in_manifest(self, test_dirs, console, monkeypatch, tmp_path):
        tmp_path, data_dir, backup_dir = test_dirs
        _patch(monkeypatch, data_dir, backup_dir)

        path = backup_dir / "bad-manifest.tar.gz"
        with tarfile.open(path, "w:gz") as tar:
            data = b"{no}"
            info = tarfile.TarInfo(name="manifest.json")
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))

        args = SimpleNamespace(file=str(path))
        backup.verify_handle(args, console)

        output = _get_output(console)
        assert "Error" in output and "Expecting" in output

    def test_missing_schema_version(self, test_dirs, console, monkeypatch, tmp_path):
        tmp_path, data_dir, backup_dir = test_dirs
        _patch(monkeypatch, data_dir, backup_dir)

        manifest = {"created_at": "2026-01-01T00:00:00+00:00", "files": []}
        path = backup_dir / "no-schema.tar.gz"
        with tarfile.open(path, "w:gz") as tar:
            data = json.dumps(manifest).encode()
            info = tarfile.TarInfo(name="manifest.json")
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))

        args = SimpleNamespace(file=str(path))
        backup.verify_handle(args, console)

        output = _get_output(console)
        assert "schema_version" in output

    def test_referenced_file_missing(self, test_dirs, console, monkeypatch, tmp_path):
        tmp_path, data_dir, backup_dir = test_dirs
        _patch(monkeypatch, data_dir, backup_dir)

        manifest = {"schema_version": 1, "created_at": "2026-01-01T00:00:00+00:00", "files": ["missing.json"]}
        path = backup_dir / "missing-file.tar.gz"
        with tarfile.open(path, "w:gz") as tar:
            data = json.dumps(manifest).encode()
            info = tarfile.TarInfo(name="manifest.json")
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))

        args = SimpleNamespace(file=str(path))
        backup.verify_handle(args, console)

        output = _get_output(console)
        assert "Referenced file not in archive" in output

    def test_file_not_found(self, test_dirs, console, monkeypatch, tmp_path):
        tmp_path, data_dir, backup_dir = test_dirs
        _patch(monkeypatch, data_dir, backup_dir)

        args = SimpleNamespace(file="nonexistent.tar.gz")
        backup.verify_handle(args, console)

        output = _get_output(console)
        assert "not found" in output
