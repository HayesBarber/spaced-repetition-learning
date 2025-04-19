from datetime import datetime, timedelta
from storage import (
    ensure_data_dir, load_json, save_json,
    PROGRESS_FILE, MASTERED_FILE
)

def _today():
    return datetime.today().date()

def add_or_update_problem(name, rating):
    ensure_data_dir()
    data = load_json(PROGRESS_FILE)

    entry = data.get(name, {"history": []})
    entry["history"].append({
        "rating": rating,
        "date": _today().isoformat()
    })

    # Mastery check: last two ratings are 5
    history = entry["history"]
    if len(history) >= 2 and history[-1]["rating"] == 5 and history[-2]["rating"] == 5:
        mastered = load_json(MASTERED_FILE)
        mastered[name] = entry
        save_json(MASTERED_FILE, mastered)
        if name in data:
            del data[name]
    else:
        data[name] = entry

    save_json(PROGRESS_FILE, data)

def get_in_progress():
    ensure_data_dir()
    data = load_json(PROGRESS_FILE)
    res = []

    for name, _ in data.items():
        res.append(name)

    return res

def get_due_problems(limit=None):
    ensure_data_dir()
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

    return [name for name, _, _ in (due[:limit] if limit else due)]

def get_mastered_problems():
    ensure_data_dir()
    return list(load_json(MASTERED_FILE).keys())
