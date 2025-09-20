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
    colors = colors_dict()
    render_legend(console, colors)
    counts = get_all_date_counts()
    render_activity(console, counts, colors)


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
    today = date.today()
    start = today - timedelta(days=365)

    # Walk backwards until start is a Sunday (weekday() 6)
    while start.weekday() != 6:
        start -= timedelta(days=1)

    def key(d: date) -> str:
        return d.isoformat()

    day = start
    all_days = []
    while day <= today:
        all_days.append(day)
        day += timedelta(days=1)

    weeks = []
    week = [None] * 7
    for d in all_days:
        weekday = d.weekday()  # 0=Monday ... 6=Sunday
        # Map Monday=0 → index 1, Sunday=6 → index 0
        col_index = (weekday + 1) % 7
        week[col_index] = counts.get(key(d), 0)

        if col_index == 6:
            weeks.append(week)
            week = [None] * 7

    if any(week):
        weeks.append(week)

    table = Table(show_header=False, show_edge=False, padding=(0, 0))
    for _ in weeks:
        table.add_column()

    default = list(colors.values())[-1]

    for row_idx in range(7):
        table.add_row(
            *[
                (
                    f"[{colors.get(week[row_idx], default)}]■[/]"
                    if week[row_idx] is not None
                    else " "
                )
                for week in weeks
            ]
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
