from datetime import datetime
import random

from rich.console import Console

from srl.storage import (
    load_json,
    save_json,
    AUDIT_FILE,
    MASTERED_FILE,
    PROGRESS_FILE,
)
from srl.utils import today


def get_current_audit():
    data = load_json(AUDIT_FILE)
    return data.get("current_audit")


def get_problem_url(name):
    mastered = load_json(MASTERED_FILE)
    url = mastered.get(name, {}).get("url", None)
    return url


def get_last_audit_date():
    """Get the date of the most recent audit from history."""

    audit_data = load_json(AUDIT_FILE)
    history = audit_data.get("history", [])

    if not history:
        return None

    dates = [entry.get("date") for entry in history if entry.get("date")]
    if not dates:
        return None

    most_recent = max(dates)
    return datetime.fromisoformat(most_recent).date()


def log_audit_attempt(problem, result):
    audit_data = load_json(AUDIT_FILE)

    if "history" not in audit_data:
        audit_data["history"] = []

    audit_data["history"].append(
        {
            "date": today().isoformat(),
            "problem": problem,
            "result": result,
        }
    )

    audit_data.pop("current_audit", None)

    save_json(AUDIT_FILE, audit_data)


def audit_pass(curr):
    log_audit_attempt(curr, "pass")


def audit_fail(curr, console: Console):
    mastered = load_json(MASTERED_FILE)
    progress = load_json(PROGRESS_FILE)

    if curr not in mastered:
        console.print(f"[red]{curr}[/red] not found in mastered.")
        return

    entry = mastered[curr]

    entry["history"].append(
        {
            "rating": 1,
            "date": today().isoformat(),
        }
    )

    progress[curr] = entry
    save_json(PROGRESS_FILE, progress)

    del mastered[curr]
    save_json(MASTERED_FILE, mastered)

    log_audit_attempt(curr, "fail")


def random_audit():
    """Select and persist a random mastered problem for audit."""

    data_mastered = load_json(MASTERED_FILE)
    mastered = list(data_mastered)

    if not mastered:
        return None, None

    problem: str = random.choice(mastered)
    url = data_mastered[problem].get("url", None)

    audit_data = load_json(AUDIT_FILE)
    audit_data["current_audit"] = problem
    save_json(AUDIT_FILE, audit_data)

    return problem, url
