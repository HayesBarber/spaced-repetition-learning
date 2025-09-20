from rich.console import Console
from srl.storage import (
    load_json,
    MASTERED_FILE,
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
