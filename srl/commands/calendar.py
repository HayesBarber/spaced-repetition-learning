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


def add_subparser(subparsers):
    parser = subparsers.add_parser("calendar", help="Graph of SRL activity")
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    colors = colors_dict()
    counts = get_all_date_counts()
    render_activity(console, counts, colors)
    console.print("-" * 5)
    render_legend(console, colors)
    console.print("-" * 5)
    build_month(date(2025, 10, 1), counts)


def colors_dict() -> dict[int, str]:
    return {
        0: "#1a1a1a",
        1: "#99e699",
        2: "#33cc33",
        3: "#00ff00",
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
    weeks = build_weeks(counts, start, today)

    table = Table(
        show_header=False,
        show_edge=False,
        box=None,
        padding=(0, 0),
    )

    days_of_week = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    default_color = list(colors.values())[-1]

    for row_idx in range(7):
        row = [days_of_week[row_idx]] + [
            (
                f" [{colors.get(week[row_idx], default_color)}]■[/]"
                if week[row_idx] is not None
                else " "
            )
            for week in weeks
        ]
        table.add_row(*row)

    console.print(table)


def key(d: date) -> str:
    return d.isoformat()


def build_weeks(
    counts: Counter[str],
    start: date,
    today: date,
) -> list[list[int | None]]:
    # Walk backwards until start is a Sunday (weekday() 6)
    while start.weekday() != 6:
        start -= timedelta(days=1)

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


def build_month(
    month_start: date,
    counts: Counter[str],
) -> list[list[int | None]]:
    grid: list[list[int | None]] = [[None for _ in range(8)] for _ in range(7)]

    current_month = month_start.month
    day = month_start

    col = 0
    while day.month == current_month:
        row = (day.weekday() + 1) % 7
        grid[row][col] = counts.get(key(day), 0)
        day += timedelta(days=1)
        if row == 6:
            col += 1

    grid = remove_empty_columns(grid)
    print_grid(grid)
    return grid


def remove_empty_columns(grid):
    non_empty_cols = []
    num_cols = len(grid[0]) if grid else 0
    for col_idx in range(num_cols):
        if any(row[col_idx] is not None for row in grid):
            non_empty_cols.append(col_idx)

    new_grid = []
    for row in grid:
        new_row = [row[col_idx] for col_idx in non_empty_cols]
        new_grid.append(new_row)

    return new_grid


def print_grid(grid):
    for row in grid:
        print(" ".join(str(cell) if cell is not None else "." for cell in row))
