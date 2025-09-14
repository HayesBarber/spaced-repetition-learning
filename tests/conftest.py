import pytest
import srl.storage


@pytest.fixture(autouse=True)
def temp_data_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(srl.storage, "DATA_DIR", tmp_path)
    monkeypatch.setattr(
        srl.storage, "PROGRESS_FILE", tmp_path / "problems_in_progress.json"
    )
    monkeypatch.setattr(
        srl.storage, "MASTERED_FILE", tmp_path / "problems_mastered.json"
    )
    monkeypatch.setattr(srl.storage, "NEXT_UP_FILE", tmp_path / "next_up.json")
    monkeypatch.setattr(srl.storage, "AUDIT_FILE", tmp_path / "audit.json")
    monkeypatch.setattr(srl.storage, "CONFIG_FILE", tmp_path / "config.json")
    yield
