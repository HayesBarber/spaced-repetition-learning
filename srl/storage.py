from pathlib import Path
import json
import os

env_dir = os.environ.get("SRL_DATA_DIR")
DATA_DIR = Path(env_dir).expanduser() if env_dir else Path.home() / ".srl"

PROGRESS_FILE = DATA_DIR / "problems_in_progress.json"
MASTERED_FILE = DATA_DIR / "problems_mastered.json"
NEXT_UP_FILE = DATA_DIR / "next_up.json"
AUDIT_FILE = DATA_DIR / "audit.json"
CONFIG_FILE = DATA_DIR / "config.json"
BACKUP_DIR = DATA_DIR / "backups"


def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_json(file_path: Path) -> dict:
    if not file_path.exists():
        return {}
    with open(file_path, "r") as f:
        return json.load(f)


def save_json(file_path: Path, data: dict):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
