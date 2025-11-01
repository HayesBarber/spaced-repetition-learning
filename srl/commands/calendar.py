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
    months = []
    year = today.year
    month = today.month
    for _ in range(12):
        months.append((year, month))
        month -= 1
        if month == 0:
            month = 12
            year -= 1

    grids: list[list[list[int | str]]] = []
    for y, m in reversed(months):
        month_start = date(y, m, 1)
        grid = build_month(month_start, counts, today)
        grids.append(grid)

    days_of_week = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    default_color = list(colors.values())[-1]
    table = Table(
        show_header=False,
        show_edge=False,
        box=None,
        padding=(0, 0),
    )

    for row_idx in range(7):
        combined_row = [days_of_week[row_idx], " "]
        for grid in grids:
            combined_row.extend(grid[row_idx])

        rendered_row = []
        for item in combined_row:
            rendered_row.append(
                f" [{colors.get(item, default_color)}]■[/]"
                if isinstance(item, int)
                else item
            )
        table.add_row(*rendered_row)

    console.print(table)


def key(d: date) -> str:
    return d.isoformat()


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
    today: date,
) -> list[list[int | str]]:
    grid: list[list[int | str]] = [[" " for _ in range(8)] for _ in range(7)]

    current_month = month_start.month
    day = month_start

    col = 0
    while day.month == current_month and day <= today:
        row = (day.weekday() + 1) % 7
        grid[row][col] = counts.get(key(day), 0)
        day += timedelta(days=1)
        if row == 6:
            col += 1

    grid = remove_empty_columns(grid)
    return grid


def remove_empty_columns(grid) -> list[list[int | str]]:
    non_empty_cols = []
    num_cols = len(grid[0]) if grid else 0
    for col_idx in range(num_cols):
        if any(row[col_idx] != " " for row in grid):
            non_empty_cols.append(col_idx)

    new_grid = []
    for row in grid:
        new_row = [row[col_idx] for col_idx in non_empty_cols] + [" "]
        new_grid.append(new_row)

    return new_grid
