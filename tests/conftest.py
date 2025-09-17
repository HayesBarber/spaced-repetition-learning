import pytest
import srl.commands
from rich.console import Console
from dataclasses import dataclass
import pathlib
import json


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
