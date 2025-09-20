from rich.console import Console
from pathlib import Path
from srl.storage import (
    load_json,
    MASTERED_FILE,
    PROGRESS_FILE,
    AUDIT_FILE,
)


def handle(args, console: Console):
    mastered_dates = gets_dates(MASTERED_FILE)
    inprogress_dates = gets_dates(PROGRESS_FILE)
    audit_dates = get_audit_dates()


def gets_dates(path: Path) -> list[str]:
    json_data = load_json(path)
    res = []

    for obj in json_data.values():
        history = obj.get("history", [])
        if not history:
            continue
        for record in history:
            date = record.get("date", "")
            if date:
                res.append(date)

    return res


def get_audit_dates() -> list[str]:
    audit_data = load_json(AUDIT_FILE)
    history = audit_data.get("history", [])
    res = []

    for record in history:
        result = record.get("result", "")
        date = record.get("date", "")
        if date and result == "pass":
            res.append(date)

    return res
