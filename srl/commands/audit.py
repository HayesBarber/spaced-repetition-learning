from rich.console import Console
from srl.utils import today
import random
from storage import (
    load_json,
    save_json,
    AUDIT_FILE,
    MASTERED_FILE,
    PROGRESS_FILE,
)


def handle(args, console: Console):
    audit_pass_arg = args.audit_pass
    audit_fail_arg = args.audit_fail

    if audit_pass_arg:
        curr = get_current_audit()
        if curr:
            audit_pass(curr)
            console.print("[green]Audit passed![/green]")
        else:
            console.print("[yellow]No active audit to pass.[/yellow]")
    elif audit_fail_arg:
        curr = get_current_audit()
        if curr:
            audit_fail(curr, console)
            console.print("[red]Audit failed.[/red] Problem moved back to in-progress.")
        else:
            console.print("[yellow]No active audit to fail.[/yellow]")
    else:
        curr = get_current_audit()
        if curr:
            console.print(f"Current audit problem: [cyan]{curr}[/cyan]")
            console.print("[blue]Run with --pass or --fail to complete it.[/blue]")
        else:
            problem = random_audit()
            if problem:
                console.print(f"You are now being audited on: [cyan]{problem}[/cyan]")
                console.print(
                    "[blue]Run with --pass or --fail to complete the audit.[/blue]"
                )
            else:
                console.print(
                    "[yellow]No mastered problems available for audit.[/yellow]"
                )


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
