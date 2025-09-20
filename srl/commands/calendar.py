from rich.console import Console
from srl.storage import (
    load_json,
    MASTERED_FILE,
    AUDIT_FILE,
)


def handle(args, console: Console):
    pass


def get_mastered_dates() -> list[str]:
    mastered_data = load_json(MASTERED_FILE)
    res = []

    for obj in mastered_data.values():
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
