from rich.console import Console
from datetime import date
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
from srl.commands.mastered import get_mastered_problems as get_all_mastered_problems


def add_subparser(subparsers):
    parser = subparsers.add_parser("summary", help="Print summary of all stats")
    parser.add_argument(
        "--from-date",
        type=str,
        help="Show stats since this date (ISO format: YYYY-MM-DD)",
    )
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    from_date_str = getattr(args, "from_date", None)
    from_date = None
    if from_date_str:
        from_date = date.fromisoformat(from_date_str)

    title = "Summary"
    if from_date:
        title = f"Summary (since {from_date_str})"
    console.print(f"[dim]── {title} {'─' * 50}[/dim]")

    total_attempts = get_total_attempts(from_date)
    console.print(f"Total Attempts: {total_attempts}")

    mastered_count = len(get_mastered_problems(from_date))
    console.print(f"Total Mastered: {mastered_count}")

    in_progress_count = len(get_in_progress_filtered(from_date))
    console.print(f"Total In-Progress: {in_progress_count}")

    console.print()
    print_audit_stats(console, from_date)

    console.print()
    print_calendar(console, from_date)


def get_total_attempts(from_date: date | None = None) -> int:
    progress_data = load_json(PROGRESS_FILE)
    mastered_data = load_json(MASTERED_FILE)
    audit_data = load_json(AUDIT_FILE)

    count = 0

    for data in (progress_data, mastered_data):
        for problem_data in data.values():
            history = problem_data.get("history", [])
            if from_date:
                history = [
                    h for h in history
                    if date.fromisoformat(h["date"]) >= from_date
                ]
            count += len(history)

    for attempt in audit_data.get("history", []):
        if attempt.get("result") != "fail":
            attempt_date = date.fromisoformat(attempt["date"])
            if from_date is None or attempt_date >= from_date:
                count += 1

    return count


def get_mastered_problems(from_date: date | None = None) -> list:
    all_mastered = get_all_mastered_problems()
    if from_date is None:
        return all_mastered

    mastered = []
    data = load_json(MASTERED_FILE)
    for name, info in data.items():
        history = info.get("history", [])
        if not history:
            continue
        last_attempt = history[-1]
        last_date = date.fromisoformat(last_attempt["date"])
        if last_date >= from_date:
            mastered.append((name, len(history), last_attempt["date"]))
    return mastered


def get_in_progress_filtered(from_date: date | None = None) -> list:
    data = load_json(PROGRESS_FILE)
    result = []
    for name, info in data.items():
        history = info.get("history", [])
        if not history:
            continue
        if from_date is None:
            result.append({"name": name, "url": info.get("url", "")})
        else:
            has_activity = any(
                date.fromisoformat(h["date"]) >= from_date
                for h in history
            )
            if has_activity:
                result.append({"name": name, "url": info.get("url", "")})
    return result


def print_audit_stats(console: Console, from_date: date | None = None):
    audit_data = load_json(AUDIT_FILE)
    history = audit_data.get("history", [])

    if from_date:
        history = [
            h for h in history
            if date.fromisoformat(h["date"]) >= from_date
        ]

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


def print_calendar(console: Console, from_date: date | None = None):
    counts = get_all_date_counts()

    if not counts:
        console.print("[bold]Calendar:[/bold] No activity data.")
        return

    if from_date:
        months = calculate_months_from(from_date)
    else:
        earliest = get_earliest_date(list(counts.keys()))
        months = calculate_months_from(earliest)

    colors = Config.load().calendar_colors

    render_activity(console, counts, colors, months)
    console.print(f"[dim]{'─' * 5}[/dim]")
    from srl.commands.calendar import render_legend

    render_legend(console, colors)