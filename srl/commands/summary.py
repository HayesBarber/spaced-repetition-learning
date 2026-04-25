from rich.console import Console
from srl.storage import (
    load_json,
    PROGRESS_FILE,
    MASTERED_FILE,
    AUDIT_FILE,
)
from srl.commands.calendar import (
    get_all_date_counts,
    calculate_months_from,
    get_earliest_date,
    render_activity,
)
from srl.commands.config import Config
from srl.commands.inprogress import get_in_progress
from srl.commands.mastered import get_mastered_problems


def add_subparser(subparsers):
    parser = subparsers.add_parser("summary", help="Print summary of all stats")
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    console.print("[bold]Summary[/bold]")
    console.print(f"[dim]{'─' * 50}[/dim]")

    total_attempts = get_total_attempts()
    console.print(f"Total Attempts: {total_attempts}")

    mastered_count = len(get_mastered_problems())
    console.print(f"Total Mastered: {mastered_count}")

    in_progress_count = len(get_in_progress())
    console.print(f"Total In-Progress: {in_progress_count}")

    console.print()
    print_audit_stats(console)

    console.print()
    print_calendar_from_first(console)


def get_total_attempts() -> int:
    progress_data = load_json(PROGRESS_FILE)
    mastered_data = load_json(MASTERED_FILE)
    audit_data = load_json(AUDIT_FILE)

    count = 0

    for data in (progress_data, mastered_data):
        for problem_data in data.values():
            count += len(problem_data.get("history", []))

    for attempt in audit_data.get("history", []):
        if attempt.get("result") != "fail":
            count += 1

    return count


def print_audit_stats(console: Console):
    audit_data = load_json(AUDIT_FILE)
    history = audit_data.get("history", [])

    if not history:
        console.print("[bold]Audit Stats:[/bold] No audits yet.")
        return

    total = len(history)
    passed = sum(1 for entry in history if entry.get("result") == "pass")
    failed = total - passed
    pass_rate = (passed / total * 100) if total > 0 else 0

    console.print("[bold]Audit Stats:[/bold]")
    console.print(f"  Total: {total}")
    console.print(f"  Passed: {passed} ({pass_rate:.1f}%)")
    console.print(f"  Failed: {failed} ({100 - pass_rate:.1f}%)")


def print_calendar_from_first(console: Console):
    counts = get_all_date_counts()

    if not counts:
        console.print("[bold]Calendar:[/bold] No activity data.")
        return

    earliest = get_earliest_date(list(counts.keys()))
    months = calculate_months_from(earliest)

    colors = Config.load().calendar_colors

    render_activity(console, counts, colors, months)
    console.print(f"[dim]{'─' * 5}[/dim]")
    from srl.commands.calendar import render_legend

    render_legend(console, colors)
