import io
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


def _patch(monkeypatch, data_dir, backup_dir):
    monkeypatch.setattr("srl.storage.BACKUP_DIR", backup_dir)
    monkeypatch.setattr("srl.storage.DATA_DIR", data_dir)
    monkeypatch.setattr("srl.commands.backup.BACKUP_DIR", backup_dir)
    monkeypatch.setattr("srl.commands.backup.DATA_DIR", data_dir)


def test_backup_creates_archive(test_dirs, console, monkeypatch):
    tmp_path, data_dir, backup_dir = test_dirs
    _patch(monkeypatch, data_dir, backup_dir)

    backup.handle(SimpleNamespace(), console)

    archives = list(backup_dir.glob("backup-*.tar.gz"))
    assert len(archives) == 1


def test_backup_includes_all_storage_files(test_dirs, console, monkeypatch, tmp_path):
    tmp_path, data_dir, backup_dir = test_dirs
    for fname in [
        "problems_in_progress.json",
        "problems_mastered.json",
        "next_up.json",
        "audit.json",
        "config.json",
    ]:
        (data_dir / fname).write_text("{}")

    _patch(monkeypatch, data_dir, backup_dir)

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
    for fname in [
        "problems_in_progress.json",
        "problems_mastered.json",
        "next_up.json",
        "audit.json",
        "config.json",
    ]:
        (data_dir / fname).write_text("{}")

    _patch(monkeypatch, data_dir, backup_dir)

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
    for fname in [
        "problems_in_progress.json",
        "problems_mastered.json",
        "next_up.json",
        "audit.json",
        "config.json",
    ]:
        (data_dir / fname).write_text("{}")

    _patch(monkeypatch, data_dir, backup_dir)

    backup.handle(SimpleNamespace(), console)
    time.sleep(0.01)
    backup.handle(SimpleNamespace(), console)

    archives = list(backup_dir.glob("backup-*.tar.gz"))
    assert len(archives) == 2

    names = sorted([a.name for a in archives])
    assert names[0] != names[1]


def test_backup_handles_empty_storage(test_dirs, console, monkeypatch):
    tmp_path, data_dir, backup_dir = test_dirs
    _patch(monkeypatch, data_dir, backup_dir)

    backup.handle(SimpleNamespace(), console)

    archives = list(backup_dir.glob("backup-*.tar.gz"))
    assert len(archives) == 1

    with tarfile.open(archives[0], "r:gz") as tar:
        manifest_file = tar.extractfile("manifest.json")
        manifest = json.loads(manifest_file.read().decode())

        assert manifest["schema_version"] == 1
        assert manifest["files"] == []


def test_prune_respects_max_backups(test_dirs, console, monkeypatch):
    tmp_path, data_dir, backup_dir = test_dirs
    _patch(monkeypatch, data_dir, backup_dir)

    for i in range(4):
        (backup_dir / f"backup-2026-01-{i+1:02d}T000000.tar.gz").touch()

    monkeypatch.setattr(
        "srl.commands.backup.Config.load",
        lambda: type("Config", (), {"backup": {"max_backups": 2}})(),
    )

    backup.handle(SimpleNamespace(), console)

    remaining = list(backup_dir.glob("backup-*.tar.gz"))
    assert len(remaining) == 2


def test_prune_keeps_newest_backup(test_dirs, console, monkeypatch):
    tmp_path, data_dir, backup_dir = test_dirs
    _patch(monkeypatch, data_dir, backup_dir)

    for i in range(2):
        (backup_dir / f"backup-2026-01-{i+1:02d}T000000.tar.gz").touch()

    monkeypatch.setattr(
        "srl.commands.backup.Config.load",
        lambda: type("Config", (), {"backup": {"max_backups": 1}})(),
    )

    backup.handle(SimpleNamespace(), console)

    remaining = list(backup_dir.glob("backup-*.tar.gz"))
    assert len(remaining) == 1


def test_prune_no_op_under_limit(test_dirs, console, monkeypatch):
    tmp_path, data_dir, backup_dir = test_dirs
    _patch(monkeypatch, data_dir, backup_dir)

    for i in range(3):
        (backup_dir / f"backup-2026-01-{i+1:02d}T000000.tar.gz").touch()

    monkeypatch.setattr(
        "srl.commands.backup.Config.load",
        lambda: type("Config", (), {"backup": {"max_backups": 10}})(),
    )

    backup.handle(SimpleNamespace(), console)

    remaining = list(backup_dir.glob("backup-*.tar.gz"))
    assert len(remaining) == 4


def test_prune_handles_zero_max_backups(test_dirs, console, monkeypatch):
    tmp_path, data_dir, backup_dir = test_dirs
    _patch(monkeypatch, data_dir, backup_dir)

    (backup_dir / "backup-2026-01-01T000000.tar.gz").touch()

    monkeypatch.setattr(
        "srl.commands.backup.Config.load",
        lambda: type("Config", (), {"backup": {"max_backups": 0}})(),
    )

    backup.handle(SimpleNamespace(), console)

    remaining = list(backup_dir.glob("backup-*.tar.gz"))
    assert len(remaining) == 2


def test_prune_uses_default_when_not_configured(test_dirs, console, monkeypatch):
    tmp_path, data_dir, backup_dir = test_dirs
    _patch(monkeypatch, data_dir, backup_dir)

    for i in range(12):
        (backup_dir / f"backup-2026-01-{i+1:02d}T000000.tar.gz").touch()

    monkeypatch.setattr(
        "srl.commands.backup.Config.load", lambda: type("Config", (), {"backup": {}})()
    )

    backup.handle(SimpleNamespace(), console)

    remaining = list(backup_dir.glob("backup-*.tar.gz"))
    assert len(remaining) == 10


def _create_archive(backup_dir, name, files=None, manifest_extra=None):
    path = backup_dir / name
    files = files or []
    manifest = {
        "schema_version": 1,
        "created_at": "2026-01-01T00:00:00+00:00",
        "files": [f[1] for f in files],
    }
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

        _create_archive(
            backup_dir,
            "backup-2026-01-01T000000.tar.gz",
            [(data_dir / "problems_in_progress.json", "problems_in_progress.json")],
        )
        _create_archive(
            backup_dir,
            "backup-2026-01-02T000000.tar.gz",
            [(data_dir / "problems_mastered.json", "problems_mastered.json")],
        )

        backup.list_handle(SimpleNamespace(), console)

        output = _get_output(console)
        assert "backup-2026-01-01T000000.tar.gz" in output
        assert "backup-2026-01-02T000000.tar.gz" in output

    def test_parses_counter_suffix(self, test_dirs, console, monkeypatch, tmp_path):
        tmp_path, data_dir, backup_dir = test_dirs
        _patch(monkeypatch, data_dir, backup_dir)

        (data_dir / "test.json").write_text("{}")
        _create_archive(
            backup_dir,
            "backup-2026-01-01T000000-1.tar.gz",
            [(data_dir / "test.json", "test.json")],
        )

        backup.list_handle(SimpleNamespace(), console)

        output = _get_output(console)
        assert "backup-2026-01-01T000000-1.tar.gz" in output


class TestVerify:
    def test_valid_archive(self, test_dirs, console, monkeypatch, tmp_path):
        tmp_path, data_dir, backup_dir = test_dirs
        _patch(monkeypatch, data_dir, backup_dir)

        (data_dir / "test.json").write_text("{}")
        archive = _create_archive(
            backup_dir,
            "backup-2026-01-01T000000.tar.gz",
            [(data_dir / "test.json", "test.json")],
        )

        args = SimpleNamespace(file=str(archive))
        backup.verify_handle(args, console)

        assert "verified successfully" in _get_output(console)

    def test_valid_by_filename(self, test_dirs, console, monkeypatch, tmp_path):
        tmp_path, data_dir, backup_dir = test_dirs
        _patch(monkeypatch, data_dir, backup_dir)

        (data_dir / "test.json").write_text("{}")
        _create_archive(
            backup_dir,
            "backup-2026-01-01T000000.tar.gz",
            [(data_dir / "test.json", "test.json")],
        )

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

        manifest = {
            "schema_version": 1,
            "created_at": "2026-01-01T00:00:00+00:00",
            "files": ["missing.json"],
        }
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


class TestRestore:
    def test_declines_restore(self, test_dirs, console, monkeypatch, tmp_path):
        tmp_path, data_dir, backup_dir = test_dirs
        _patch(monkeypatch, data_dir, backup_dir)

        (data_dir / "problems_in_progress.json").write_text('{"foo": 1}')
        (data_dir / "problems_mastered.json").write_text('{"bar": 2}')
        archive = _create_archive(
            backup_dir,
            "backup-2026-01-01T000000.tar.gz",
            [
                (data_dir / "problems_in_progress.json", "problems_in_progress.json"),
                (data_dir / "problems_mastered.json", "problems_mastered.json"),
            ],
        )

        monkeypatch.setattr("builtins.input", lambda: "n")

        args = SimpleNamespace(file=str(archive))
        backup.restore_handle(args, console)

        output = _get_output(console)
        assert "Restore cancelled" in output

    def test_successful_restore(self, test_dirs, console, monkeypatch, tmp_path):
        tmp_path, data_dir, backup_dir = test_dirs
        _patch(monkeypatch, data_dir, backup_dir)

        (data_dir / "problems_in_progress.json").write_text('{"foo": 1}')
        (data_dir / "problems_mastered.json").write_text('{"bar": 2}')
        archive = _create_archive(
            backup_dir,
            "backup-2026-01-01T000000.tar.gz",
            [
                (data_dir / "problems_in_progress.json", "problems_in_progress.json"),
                (data_dir / "problems_mastered.json", "problems_mastered.json"),
            ],
        )

        args = SimpleNamespace(file=str(archive), yes=True)
        backup.restore_handle(args, console)

        output = _get_output(console)
        assert "Restore complete" in output

    def test_cancels_at_backup_prompt(self, test_dirs, console, monkeypatch, tmp_path):
        tmp_path, data_dir, backup_dir = test_dirs
        _patch(monkeypatch, data_dir, backup_dir)

        (data_dir / "problems_in_progress.json").write_text('{"foo": 1}')
        archive = _create_archive(
            backup_dir,
            "backup-2026-01-01T000000.tar.gz",
            [
                (data_dir / "problems_in_progress.json", "problems_in_progress.json"),
            ],
        )

        responses = iter(["y", "n"])
        monkeypatch.setattr("builtins.input", lambda: next(responses))

        args = SimpleNamespace(file=str(archive))
        backup.restore_handle(args, console)

        output = _get_output(console)
        assert "Restore cancelled" not in output
        assert "Restore complete" in output

    def test_creates_pre_restore_backup(
        self, test_dirs, console, monkeypatch, tmp_path
    ):
        tmp_path, data_dir, backup_dir = test_dirs
        _patch(monkeypatch, data_dir, backup_dir)

        (data_dir / "problems_in_progress.json").write_text('{"foo": 1}')
        archive = _create_archive(
            backup_dir,
            "backup-2026-01-01T000000.tar.gz",
            [
                (data_dir / "problems_in_progress.json", "problems_in_progress.json"),
            ],
        )

        args = SimpleNamespace(file=str(archive), yes=True)
        backup.restore_handle(args, console)

        backups = sorted(backup_dir.glob("backup-*.tar.gz"))
        assert len(backups) == 2

    def test_corrupt_archive(self, test_dirs, console, monkeypatch, tmp_path):
        tmp_path, data_dir, backup_dir = test_dirs
        _patch(monkeypatch, data_dir, backup_dir)

        (data_dir / "problems_in_progress.json").write_text('{"original": true}')
        corrupt = backup_dir / "corrupt.tar.gz"
        corrupt.write_bytes(b"not a tar file")

        args = SimpleNamespace(file=str(corrupt), yes=True)
        backup.restore_handle(args, console)

        output = _get_output(console)
        assert "Error" in output
        assert "Cannot open archive" in output
        assert (
            data_dir / "problems_in_progress.json"
        ).read_text() == '{"original": true}'

    def test_missing_manifest(self, test_dirs, console, monkeypatch, tmp_path):
        tmp_path, data_dir, backup_dir = test_dirs
        _patch(monkeypatch, data_dir, backup_dir)

        (data_dir / "problems_in_progress.json").write_text('{"original": true}')
        path = backup_dir / "no-manifest.tar.gz"
        with tarfile.open(path, "w:gz") as tar:
            info = tarfile.TarInfo(name="somefile.json")
            info.size = 0
            tar.addfile(info, io.BytesIO(b""))

        args = SimpleNamespace(file=str(path), yes=True)
        backup.restore_handle(args, console)

        output = _get_output(console)
        assert "manifest.json not found" in output
        assert (
            data_dir / "problems_in_progress.json"
        ).read_text() == '{"original": true}'

    def test_invalid_json_in_manifest(self, test_dirs, console, monkeypatch, tmp_path):
        tmp_path, data_dir, backup_dir = test_dirs
        _patch(monkeypatch, data_dir, backup_dir)

        (data_dir / "problems_in_progress.json").write_text('{"original": true}')
        path = backup_dir / "bad-manifest.tar.gz"
        with tarfile.open(path, "w:gz") as tar:
            data = b"{no}"
            info = tarfile.TarInfo(name="manifest.json")
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))

        args = SimpleNamespace(file=str(path), yes=True)
        backup.restore_handle(args, console)

        output = _get_output(console)
        assert "Error" in output and "Expecting" in output
        assert (
            data_dir / "problems_in_progress.json"
        ).read_text() == '{"original": true}'

    def test_missing_schema_version(self, test_dirs, console, monkeypatch, tmp_path):
        tmp_path, data_dir, backup_dir = test_dirs
        _patch(monkeypatch, data_dir, backup_dir)

        (data_dir / "problems_in_progress.json").write_text('{"original": true}')
        manifest = {"created_at": "2026-01-01T00:00:00+00:00", "files": []}
        path = backup_dir / "no-schema.tar.gz"
        with tarfile.open(path, "w:gz") as tar:
            data = json.dumps(manifest).encode()
            info = tarfile.TarInfo(name="manifest.json")
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))

        args = SimpleNamespace(file=str(path), yes=True)
        backup.restore_handle(args, console)

        output = _get_output(console)
        assert "schema_version" in output
        assert (
            data_dir / "problems_in_progress.json"
        ).read_text() == '{"original": true}'

    def test_referenced_file_missing(self, test_dirs, console, monkeypatch, tmp_path):
        tmp_path, data_dir, backup_dir = test_dirs
        _patch(monkeypatch, data_dir, backup_dir)

        (data_dir / "problems_in_progress.json").write_text('{"original": true}')
        manifest = {
            "schema_version": 1,
            "created_at": "2026-01-01T00:00:00+00:00",
            "files": ["missing.json"],
        }
        path = backup_dir / "missing-file.tar.gz"
        with tarfile.open(path, "w:gz") as tar:
            data = json.dumps(manifest).encode()
            info = tarfile.TarInfo(name="manifest.json")
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))

        args = SimpleNamespace(file=str(path), yes=True)
        backup.restore_handle(args, console)

        output = _get_output(console)
        assert "Referenced file not in archive" in output
        assert (
            data_dir / "problems_in_progress.json"
        ).read_text() == '{"original": true}'

    def test_file_not_found(self, test_dirs, console, monkeypatch, tmp_path):
        tmp_path, data_dir, backup_dir = test_dirs
        _patch(monkeypatch, data_dir, backup_dir)

        args = SimpleNamespace(file="nonexistent.tar.gz")
        backup.restore_handle(args, console)

        output = _get_output(console)
        assert "not found" in output

    def test_keyboard_interrupt_at_first_prompt(
        self, test_dirs, console, monkeypatch, tmp_path
    ):
        tmp_path, data_dir, backup_dir = test_dirs
        _patch(monkeypatch, data_dir, backup_dir)

        archive = _create_archive(backup_dir, "backup-2026-01-01T000000.tar.gz")

        def raise_interrupt():
            raise KeyboardInterrupt()

        monkeypatch.setattr("builtins.input", raise_interrupt)

        args = SimpleNamespace(file=str(archive))
        backup.restore_handle(args, console)

        assert "Restore cancelled" in _get_output(console)

    def test_keyboard_interrupt_at_second_prompt(
        self, test_dirs, console, monkeypatch, tmp_path
    ):
        tmp_path, data_dir, backup_dir = test_dirs
        _patch(monkeypatch, data_dir, backup_dir)

        archive = _create_archive(backup_dir, "backup-2026-01-01T000000.tar.gz")

        responses = iter(["y", KeyboardInterrupt()])

        def input_side_effect():
            val = next(responses)
            if isinstance(val, BaseException):
                raise val
            return val

        monkeypatch.setattr("builtins.input", input_side_effect)

        args = SimpleNamespace(file=str(archive))
        backup.restore_handle(args, console)

        output = _get_output(console)
        assert "Restore cancelled" in output
