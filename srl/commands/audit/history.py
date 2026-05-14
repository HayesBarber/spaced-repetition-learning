from rich.console import Console
from rich.table import Table
from rich import box

from srl.storage import load_json, AUDIT_FILE


def add_subparser(subparsers):
    parser = subparsers.add_parser(
        "history",
        help="Show audit history",
    )

    parser.set_defaults(handler=handle_history)
    return parser


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
        f"Total Audits: {total} | "
        f"Passed: {passed} ({pass_rate:.1f}%) | "
        f"Failed: {failed} ({100 - pass_rate:.1f}%)"
    )
    console.print()

    console.print("[bold]Audit History[/bold]")

    sorted_history = sorted(history, key=lambda x: x.get("date", ""))

    history_table = Table(box=box.ROUNDED)
    history_table.add_column("Date", style="white")
    history_table.add_column("Problem", style="cyan")
    history_table.add_column("Result", justify="center")

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

        history_table.add_row(date_str, problem, result_str)

    console.print(history_table)
