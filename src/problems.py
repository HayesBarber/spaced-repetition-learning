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


def get_due_problems(limit=None):
    data = load_json(PROGRESS_FILE)
    due = []

    for name, info in data.items():
        history = info["history"]
        if not history:
            continue
        last = history[-1]
        last_date = datetime.fromisoformat(last["date"]).date()
        due_date = last_date + timedelta(days=last["rating"])
        if due_date <= _today():
            due.append((name, last_date, last["rating"]))

    # Sort: older last attempt first, then lower rating
    due.sort(key=lambda x: (x[1], x[2]))
    due_names = [name for name, _, _ in (due[:limit] if limit else due)]

    if not due_names:
        next_up = load_json(NEXT_UP_FILE)
        fallback = list(next_up.keys())[: limit or 3]
        return fallback

    return due_names


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
