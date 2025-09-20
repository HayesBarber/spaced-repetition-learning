from rich.console import Console
from collections import Counter
from pathlib import Path
from collections import Counter
from datetime import date, timedelta
from rich.console import Console
from rich.table import Table
from srl.storage import (
    load_json,
    MASTERED_FILE,
    PROGRESS_FILE,
    AUDIT_FILE,
)


def handle(args, console: Console):
    counts = get_all_date_counts()
    render_activity(console, counts)


def render_activity(console: Console, counts: Counter[str]):
    today = date.today()
    start = today - timedelta(days=365)

    def key(d: date) -> str:
        return d.isoformat()

    # Build 7 rows (Mon–Sun) × 53 weeks (~365 days)
    weeks = []
    day = start
    while day <= today:
        week = []
        for _ in range(7):
            if day > today:
                week.append(None)
            else:
                week.append(counts.get(key(day), 0))
            day += timedelta(days=1)
        weeks.append(week)

    grid = list(zip(*weeks))

    table = Table(show_header=False, show_edge=False, padding=(0, 0))
    for _ in range(len(grid[0])):
        table.add_column()

    def style_for(val: int) -> str:
        if val == 0:
            return "grey23"
        elif val == 1:
            return "pale_green1"
        elif val == 2:
            return "spring_green3"
        elif val == 3:
            return "green3"
        else:
            return "green4"

    for row in grid:
        table.add_row(
            *[f"[{style_for(val)}]■[/]" if val is not None else " " for val in row]
        )

    console.print(table)


def get_all_date_counts() -> Counter[str]:
    counts = Counter()
    counts.update(get_dates(MASTERED_FILE))
    counts.update(get_dates(PROGRESS_FILE))
    counts.update(get_audit_dates())

    return counts


def get_dates(path: Path) -> list[str]:
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
