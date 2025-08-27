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


def _today():
    return datetime.today().date()


def add_to_next_up(name):
    data = load_json(NEXT_UP_FILE)

    if name in data:
        print(f'"{name}" is already in the Next Up queue.')
        return

    data[name] = {"added": _today().isoformat()}
    save_json(NEXT_UP_FILE, data)


def add_or_update_problem(name, rating):
    data = load_json(PROGRESS_FILE)

    entry = data.get(name, {"history": []})
    entry["history"].append(
        {
            "rating": rating,
            "date": _today().isoformat(),
        }
    )

    # Mastery check: last two ratings are 5
    history = entry["history"]
    if len(history) >= 2 and history[-1]["rating"] == 5 and history[-2]["rating"] == 5:
        mastered = load_json(MASTERED_FILE)
        mastered[name] = entry
        save_json(MASTERED_FILE, mastered)
        if name in data:
            del data[name]
        print(f"{name} moved to mastered!")
    else:
        data[name] = entry
        print(f"Added rating {rating} for '{name}'")

    save_json(PROGRESS_FILE, data)

    # Remove from next up if it exists there
    next_up = load_json(NEXT_UP_FILE)
    if name in next_up:
        del next_up[name]
        save_json(NEXT_UP_FILE, next_up)


def get_in_progress():
    data = load_json(PROGRESS_FILE)
    res = []

    for name, _ in data.items():
        res.append(name)

    return res


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


def get_mastered_problems():
    data = load_json(MASTERED_FILE)
    mastered = []

    for name, info in data.items():
        history = info["history"]
        if not history:
            continue
        attempts = len(history)
        mastered.append(f"{name} -> {attempts} attempts")

    return mastered


def should_audit():
    config = load_json(CONFIG_FILE)
    probability = config.get("audit_probability", 0.1)
    try:
        probability = float(probability)
    except (ValueError, TypeError):
        probability = 0.1
    return random.random() < probability


def random_audit():
    data = load_json(MASTERED_FILE)
    mastered = list(data)
    if not mastered:
        return None
    problem: str = random.choice(mastered)
    data = load_json(AUDIT_FILE)
    data["current_audit"] = problem
    save_json(AUDIT_FILE, data)
    return problem


def get_current_audit():
    data = load_json(AUDIT_FILE)
    return data.get("current_audit")


def audit_pass():
    save_json(AUDIT_FILE, {})


def audit_fail():
    curr = get_current_audit()
    if not curr:
        print("Current audit does not exist")
        return

    mastered = load_json(MASTERED_FILE)
    progress = load_json(PROGRESS_FILE)

    if curr not in mastered:
        print(f"{curr} not found in mastered.")
        return

    entry = mastered[curr]
    # Append new failed attempt
    entry["history"].append(
        {
            "rating": 1,
            "date": _today().isoformat(),
        }
    )

    # Move to progress
    progress[curr] = entry
    save_json(PROGRESS_FILE, progress)

    # Remove from mastered
    del mastered[curr]
    save_json(MASTERED_FILE, mastered)

    # Clear audit file
    save_json(AUDIT_FILE, {})


def remove_problem(name):
    data = load_json(PROGRESS_FILE)
    if name in data:
        del data[name]
        save_json(PROGRESS_FILE, data)
        print(f"Removed '{name}' from in-progress.")
    else:
        print(f"Problem '{name}' not found in in-progress.")
