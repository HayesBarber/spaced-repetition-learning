import pytest
import srl.commands
from srl.utils import today
from rich.console import Console
from dataclasses import dataclass
import pathlib
import json
from datetime import datetime, timedelta


@dataclass
class Paths:
    PROGRESS_FILE: pathlib.Path
    MASTERED_FILE: pathlib.Path
    NEXT_UP_FILE: pathlib.Path
    AUDIT_FILE: pathlib.Path
    CONFIG_FILE: pathlib.Path


@pytest.fixture
def console():
    return Console(record=True)


@pytest.fixture
def today_string():
    return today().isoformat()


@pytest.fixture(autouse=True)
def mock_data(tmp_path, monkeypatch):
    paths = Paths(
        PROGRESS_FILE=tmp_path / "problems_in_progress.json",
        MASTERED_FILE=tmp_path / "problems_mastered.json",
        NEXT_UP_FILE=tmp_path / "next_up.json",
        AUDIT_FILE=tmp_path / "audit.json",
        CONFIG_FILE=tmp_path / "config.json",
    )

    for name, path in vars(paths).items():
        path.write_text("{}")
        for mod in vars(srl.commands).values():
            if hasattr(mod, name):
                monkeypatch.setattr(f"{mod.__name__}.{name}", path)
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
