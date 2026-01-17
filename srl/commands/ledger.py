from rich.console import Console
from rich.table import Table
from rich import box
from srl.storage import (
    load_json,
    PROGRESS_FILE,
    MASTERED_FILE,
    AUDIT_FILE,
)


def add_subparser(subparsers):
    parser = subparsers.add_parser("ledger", help="Print a summary of all attempts")
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    progress_data = load_json(PROGRESS_FILE)
    mastered_data = load_json(MASTERED_FILE)
    audit_data = load_json(AUDIT_FILE)

    all_attempts = []

    # Process progress and mastered problems
    for data, status in (
        (progress_data, "progress"),
        (mastered_data, "mastered"),
    ):
        for problem_url, problem_data in data.items():
            for attempt in problem_data.get("history", []):
                all_attempts.append(
                    {
                        "date": attempt["date"],
                        "problem": problem_url,
                        "rating": attempt["rating"],
                        "status": status,
                    }
                )

    # Process audit attempts
    for attempt in audit_data.get("history", []):
        audit_rating = 5 if attempt["result"] == "pass" else 1
        all_attempts.append(
            {
                "date": attempt["date"],
                "problem": attempt["problem"],
                "rating": audit_rating,
                "status": "audit",
            }
        )

    all_attempts.sort(key=lambda x: x["date"])

    if all_attempts:
        timeline_table = Table(box=box.ROUNDED)
        timeline_table.add_column("Date", style="white")
        timeline_table.add_column("Problem", style="cyan")
        timeline_table.add_column("Rating", justify="center")
        timeline_table.add_column("Status", justify="center")

        for attempt in all_attempts:
            rating_color = "green" if attempt["rating"] >= 4 else "red"
            rating_text = f"[{rating_color}]{attempt['rating']}[/{rating_color}]"
            status_color = {
                "progress": "yellow",
                "mastered": "green",
                "audit": "blue",
            }.get(attempt["status"], "white")
            status_text = f"[{status_color}]{attempt['status']}[/{status_color}]"

            timeline_table.add_row(
                attempt["date"], attempt["problem"], rating_text, status_text
            )

        console.print(timeline_table)
