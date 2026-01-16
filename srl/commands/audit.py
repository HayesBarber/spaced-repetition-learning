from rich.console import Console
from srl.utils import today
import random
from srl.storage import (
    load_json,
    save_json,
    AUDIT_FILE,
    MASTERED_FILE,
    PROGRESS_FILE,
)


def add_subparser(subparsers):
    parser = subparsers.add_parser("audit", help="Random audit functionality")
    audit_subparsers = parser.add_subparsers(dest="audit_command")

    pass_parser = audit_subparsers.add_parser("pass", help="Pass the audit")
    pass_parser.set_defaults(handler=handle_pass)

    fail_parser = audit_subparsers.add_parser("fail", help="Fail the audit")
    fail_parser.set_defaults(handler=handle_fail)

    history_parser = audit_subparsers.add_parser("history", help="Show audit history")
    history_parser.set_defaults(handler=handle_history)

    parser.set_defaults(handler=handle_default)
    return parser


def handle_default(args, console: Console):
    curr = get_current_audit()
    if curr:
        console.print(f"Current audit problem: [cyan]{curr}[/cyan]")
        console.print("[blue]Run with 'pass' or 'fail' to complete it.[/blue]")
    else:
        problem = random_audit()
        if problem:
            console.print(f"You are now being audited on: [cyan]{problem}[/cyan]")
            console.print(
                "[blue]Run with 'pass' or 'fail' to complete the audit.[/blue]"
            )
        else:
            console.print("[yellow]No mastered problems available for audit.[/yellow]")


def handle_pass(args, console: Console):
    curr = get_current_audit()
    if curr:
        audit_pass(curr)
        console.print("[green]Audit passed![/green]")
    else:
        console.print("[yellow]No active audit to pass.[/yellow]")


def handle_fail(args, console: Console):
    curr = get_current_audit()
    if curr:
        audit_fail(curr, console)
        console.print("[red]Audit failed.[/red] Problem moved back to in-progress.")
    else:
        console.print("[yellow]No active audit to fail.[/yellow]")


def handle_history(args, console: Console):
    audit_data = load_json(AUDIT_FILE)
    history = audit_data.get("history", [])

    if not history:
        console.print("[yellow]No audit history found.[/yellow]")
        return

    total = len(history)
    passed = sum(1 for entry in history if entry.get("result") == "pass")
    failed = total - passed
    pass_rate = (passed / total * 100) if total > 0 else 0

    console.print("[bold]Audit History Summary[/bold]")
    console.print(
        f"Total Audits: {total} | Passed: {passed} ({pass_rate:.1f}%) | Failed: {failed} ({100-pass_rate:.1f}%)"
    )
    console.print()

    console.print("[bold]Audit History[/bold]")

    sorted_history = sorted(history, key=lambda x: x.get("date", ""), reverse=True)

    for entry in sorted_history:
        date_str = entry.get("date", "Unknown date")
        problem = entry.get("problem", "Unknown problem")
        result = entry.get("result", "unknown")

        if result == "pass":
            result_str = "[green]PASS[/green]"
        elif result == "fail":
            result_str = "[red]FAIL[/red]"
        else:
            result_str = "[yellow]UNKNOWN[/yellow]"

        console.print(f"{date_str}  {problem:<20} {result_str}")


def get_current_audit():
    data = load_json(AUDIT_FILE)
    return data.get("current_audit")


def log_audit_attempt(problem, result):
    audit_data = load_json(AUDIT_FILE)
    if "history" not in audit_data:
        audit_data["history"] = []

    audit_data["history"].append(
        {
            "date": today().isoformat(),
            "problem": problem,
            "result": result,
        }
    )

    audit_data.pop("current_audit", None)

    save_json(AUDIT_FILE, audit_data)


def audit_pass(curr):
    log_audit_attempt(curr, "pass")


def audit_fail(curr, console: Console):
    mastered = load_json(MASTERED_FILE)
    progress = load_json(PROGRESS_FILE)

    if curr not in mastered:
        console.print(f"[red]{curr}[/red] not found in mastered.")
        return

    entry = mastered[curr]
    # Append new failed attempt
    entry["history"].append(
        {
            "rating": 1,
            "date": today().isoformat(),
        }
    )

    # Move to progress
    progress[curr] = entry
    save_json(PROGRESS_FILE, progress)

    # Remove from mastered
    del mastered[curr]
    save_json(MASTERED_FILE, mastered)

    log_audit_attempt(curr, "fail")


def random_audit():
    data_mastered = load_json(MASTERED_FILE)
    mastered = list(data_mastered)
    if not mastered:
        return None
    problem: str = random.choice(mastered)
    audit_data = load_json(AUDIT_FILE)
    audit_data["current_audit"] = problem
    save_json(AUDIT_FILE, audit_data)
    return problem
