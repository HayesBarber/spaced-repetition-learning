from rich.console import Console
from collections import Counter
from pathlib import Path
from datetime import date, timedelta
from rich.table import Table
from srl.storage import (
    load_json,
    MASTERED_FILE,
    PROGRESS_FILE,
    AUDIT_FILE,
)


def handle(args, console: Console):
    colors = colors_dict()
    counts = get_all_date_counts()
    render_activity(console, counts, colors)
    console.print("-" * 5)
    render_legend(console, colors)


def colors_dict() -> dict[int, str]:
    return {
        0: "#1a1a1a",
        1: "#2ca86d",
        2: "#7ed957",
        3: "#b5f5b0",
    }


def render_legend(console: Console, colors: dict[int, str]) -> str:
    squares = " ".join(f"[{colors[level]}]■[/]" for level in colors)
    legend = f"Less {squares} More"
    console.print(legend)


def render_activity(
    console: Console,
    counts: Counter[str],
    colors: dict[int, str],
):
    weeks = build_weeks(counts)

    table = Table(
        show_header=False,
        show_edge=False,
        padding=(0, 0),
    )

    days_of_week = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    default_color = list(colors.values())[-1]

    for row_idx in range(7):
        row = [days_of_week[row_idx]]
        row.extend(
            [
                (
                    f"[{colors.get(week[row_idx], default_color)}]■[/]"
                    if week[row_idx] is not None
                    else " "
                )
                for week in weeks
            ]
        )
        table.add_row(*row)

    console.print(table)


def build_weeks(counts: Counter[str]) -> list[list[int | None]]:
    today = date.today()
    start = today - timedelta(days=365)

    # Walk backwards until start is a Sunday (weekday() 6)
    while start.weekday() != 6:
        start -= timedelta(days=1)

    def key(d: date) -> str:
        return d.isoformat()

    day = start
    weeks: list[list[int | None]] = []
    week: list[int | None] = []

    while day <= today:
        week.append(counts.get(key(day), 0))
        if len(week) == 7:
            weeks.append(week)
            week = []
        day += timedelta(days=1)

    if week:
        week.extend([None] * (7 - len(week)))
        weeks.append(week)

    return weeks


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
