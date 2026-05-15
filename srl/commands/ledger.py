from rich.console import Console
from rich.table import Table
from rich import box
from srl.storage import (
    load_json,
    PROGRESS_FILE,
    MASTERED_FILE,
    AUDIT_FILE,
)
from srl.commands.list_ import get_due_problems


def add_subparser(subparsers):
    parser = subparsers.add_parser("ledger", help="Print a summary of all attempts")
    parser.add_argument(
        "-c", "--count", action="store_true", help="Show only the count of problems"
    )
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "name", nargs="?", type=str, help="Name of the problem to filter by"
    )
    group.add_argument(
        "-n", "--number", type=int, help="Problem number from `srl list`"
    )
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    progress_data = load_json(PROGRESS_FILE)
    mastered_data = load_json(MASTERED_FILE)
    audit_data = load_json(AUDIT_FILE)

    all_attempts = []

    (name, number), err = _resolve_name_and_number(args)
    if err:
        return console.print(err)

    for data, status in (
        (progress_data, "progress"),
        (mastered_data, "mastered"),
    ):
        for problem_url, problem_data in data.items():
            if number is not None and problem_url != name:
                continue
            if name and number is None and name.lower() not in problem_url.lower():
                continue
            for attempt in problem_data.get("history", []):
                all_attempts.append(
                    {
                        "date": attempt["date"],
                        "problem": problem_url,
                        "rating": attempt["rating"],
                        "status": status,
                    }
                )

    for attempt in audit_data.get("history", []):
        result = attempt["result"]
        if result == "fail":
            continue
        if name and name.lower() not in attempt["problem"].lower():
            continue
        all_attempts.append(
            {
                "date": attempt["date"],
                "problem": attempt["problem"],
                "rating": 5,
                "status": "audit",
            }
        )

    all_attempts.sort(key=lambda x: x["date"])

    if name and not all_attempts:
        console.print(f"[red]No problem found matching '{name}'.[/red]")
        return

    count_only = getattr(args, "count", False)
    if count_only:
        console.print(f"Total attempts: {len(all_attempts)}")
    elif name and all_attempts:
        focused_table = Table(
            title=f"{name} ({len(all_attempts)})",
            box=box.ROUNDED,
        )
        focused_table.add_column("Date", style="white")
        focused_table.add_column("Rating", justify="center")

        for attempt in all_attempts:
            rating_text = _format_rating(attempt["rating"])

            focused_table.add_row(attempt["date"], rating_text)

        console.print(focused_table)
    elif all_attempts:
        timeline_table = Table(box=box.ROUNDED)
        timeline_table.add_column("Date", style="white")
        timeline_table.add_column("Problem", style="cyan")
        timeline_table.add_column("Rating", justify="center")

        for attempt in all_attempts:
            rating_text = _format_rating(attempt["rating"])

            timeline_table.add_row(attempt["date"], attempt["problem"], rating_text)

        console.print(timeline_table)


def _format_rating(rating):
    color = "green" if rating >= 4 else "red"
    return f"[{color}]{rating}[/{color}]"


def _resolve_name_and_number(args):
    name = getattr(args, "name", None)
    number = getattr(args, "number", None)

    if number is not None:
        due = get_due_problems()
        if number < 1 or number > len(due):
            return (None, None), f"[red]Invalid problem number:[/red] {number}"
        name = due[number - 1][0]

    return (name, number), None
