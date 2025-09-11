from datetime import datetime, timedelta
import random
from storage import (
    AUDIT_FILE,
    CONFIG_FILE,
    load_json,
    save_json,
    PROGRESS_FILE,
    MASTERED_FILE,
    NEXT_UP_FILE,
)


def should_audit():
    config = load_json(CONFIG_FILE)
    probability = config.get("audit_probability", 0.1)
    try:
        probability = float(probability)
    except (ValueError, TypeError):
        probability = 0.1
    return random.random() < probability


def remove_problem(name):
    data = load_json(PROGRESS_FILE)
    if name in data:
        del data[name]
        save_json(PROGRESS_FILE, data)
        print(f"Removed '{name}' from in-progress.")
    else:
        print(f"Problem '{name}' not found in in-progress.")
