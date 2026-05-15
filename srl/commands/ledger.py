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


import argparse


def add_subparser(subparsers):
    parser = subparsers.add_parser(
        "ledger",
        help="Show attempt history for problems",
    )

    parser.add_argument(
        "-c",
        "--count",
        action="store_true",
        help="Show only total attempt count",
    )

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "-n",
        "--name",
        type=str,
        help="Filter by problem name",
    )

    group.add_argument(
        "-i",
        "--index",
        type=int,
        help="Filter by 1-based index from 'srl list'",
    )

    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    name, err = _resolve_name(args)
    if err:
        return console.print(err)

    all_attempts = _get_inprogress_and_mastered_attempts(
        name,
    ) + _get_audit_attemps(
        name,
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


def _resolve_name(args):
    name = getattr(args, "name", None)
    index = getattr(args, "index", None)

    if index is not None:
        due = get_due_problems()
        if index < 1 or index > len(due):
            return None, f"[red]Invalid problem number:[/red] {index}"
        name = due[index - 1][0]

    if name:
        return name.lower(), None

    return None, None


def _get_inprogress_and_mastered_attempts(name):
    progress_data = load_json(PROGRESS_FILE)
    mastered_data = load_json(MASTERED_FILE)

    attempts = []

    for data, status in (
        (progress_data, "progress"),
        (mastered_data, "mastered"),
    ):
        for problem, problem_data in data.items():
            if name and name != problem.lower():
                continue
            for attempt in problem_data.get("history", []):
                attempts.append(
                    {
                        "date": attempt["date"],
                        "problem": problem,
                        "rating": attempt["rating"],
                        "status": status,
                    }
                )

    return attempts


def _get_audit_attemps(name):
    audit_data = load_json(AUDIT_FILE)

    attempts = []

    for attempt in audit_data.get("history", []):
        result = attempt["result"]
        if result == "fail":
            continue
        problem = attempt["problem"]
        if name and name != problem.lower():
            continue
        attempts.append(
            {
                "date": attempt["date"],
                "problem": problem,
                "rating": 5,
                "status": "audit",
            }
        )

    return attempts
