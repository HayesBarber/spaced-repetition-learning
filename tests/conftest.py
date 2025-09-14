import pytest
import srl.commands
from rich.console import Console


@pytest.fixture
def console():
    return Console(record=True)


@pytest.fixture(autouse=True)
def temp_data_dir(tmp_path, monkeypatch):
    paths = {
        "PROGRESS_FILE": tmp_path / "problems_in_progress.json",
        "MASTERED_FILE": tmp_path / "problems_mastered.json",
        "NEXT_UP_FILE": tmp_path / "next_up.json",
        "AUDIT_FILE": tmp_path / "audit.json",
        "CONFIG_FILE": tmp_path / "config.json",
    }

    for name, path in paths.items():
        if "NEXT_UP" in name:
            path.write_text("[]")
        else:
            path.write_text("{}")

        for mod in vars(srl.commands).values():
            if hasattr(mod, name):
                monkeypatch.setattr(f"{mod.__name__}.{name}", path)
        monkeypatch.setattr(f"srl.storage.{name}", path)

    yield paths
