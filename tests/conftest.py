import pytest
from srl.utils import today
from rich.console import Console
from dataclasses import dataclass
import pathlib
import json
from datetime import datetime, timedelta
from srl import cli
import sys


@dataclass
class Paths:
    PROGRESS_FILE: pathlib.Path
    MASTERED_FILE: pathlib.Path
    NEXT_UP_FILE: pathlib.Path
    AUDIT_FILE: pathlib.Path
    CONFIG_FILE: pathlib.Path
    BACKUP_DIR: pathlib.Path
    DATA_DIR: pathlib.Path


@pytest.fixture
def console():
    c = Console(record=True)

    original_clear = c.clear

    def patched_clear(*args, **kwargs):
        original_clear(*args, **kwargs)

        c._record_buffer.clear()

    c.clear = patched_clear

    return c


@pytest.fixture
def parser():
    return cli.build_parser()


@pytest.fixture
def today_string():
    return today().isoformat()


@pytest.fixture(autouse=True)
def mock_data(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    backup_dir = tmp_path / "backups"
    data_dir.mkdir()
    backup_dir.mkdir()

    paths = Paths(
        PROGRESS_FILE=data_dir / "problems_in_progress.json",
        MASTERED_FILE=data_dir / "problems_mastered.json",
        NEXT_UP_FILE=data_dir / "next_up.json",
        AUDIT_FILE=data_dir / "audit.json",
        CONFIG_FILE=data_dir / "config.json",
        BACKUP_DIR=backup_dir,
        DATA_DIR=data_dir,
    )

    for name, path in vars(paths).items():
        if name not in ("BACKUP_DIR", "DATA_DIR"):
            path.write_text("{}")

        for module in sys.modules.values():
            if module and getattr(module, "__name__", "").startswith("srl.commands"):
                if hasattr(module, name):
                    monkeypatch.setattr(f"{module.__name__}.{name}", path)

        monkeypatch.setattr(f"srl.storage.{name}", path)

    yield paths


@pytest.fixture
def dump_json():
    def _dump(path, data):
        with open(path, "w") as f:
            json.dump(data, f)

    return _dump


@pytest.fixture
def load_json():

    def _load(path):
        with open(path) as f:
            data = json.load(f)
        return data

    return _load


@pytest.fixture
def backdate_problem(load_json, dump_json, mock_data):

    def _backdate(problem, days):
        progress_path = mock_data.PROGRESS_FILE
        data = load_json(progress_path)
        if problem in data and data[problem].get("history"):
            last_entry = data[problem]["history"][-1]
            old_date = datetime.fromisoformat(last_entry["date"])
            new_date = (old_date - timedelta(days=days)).isoformat()
            last_entry["date"] = new_date
            dump_json(progress_path, data)

    return _backdate
