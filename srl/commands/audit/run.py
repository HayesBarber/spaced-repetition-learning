from rich.console import Console

from .utils import get_current_audit, random_audit, get_problem_url
from srl.utils import format_problem


def add_subparser(subparsers):
    parser = subparsers.add_parser(
        "run",
        help="Start a random audit",
    )

    parser.set_defaults(handler=handle_run)
    return parser


def handle_run(args, console: Console):
    curr = get_current_audit()

    if curr:
        url = get_problem_url(curr)
        display = format_problem(curr, url)
        console.print(f"Current audit problem: [cyan]{display}[/cyan]")
        console.print("[blue]Run 'pass' or 'fail' to complete it.[/blue]")
        return

    problem, url = random_audit()

    if problem:
        display = format_problem(problem, url)
        console.print(f"You are now being audited on: [cyan]{display}[/cyan]")
        console.print("[blue]Run 'pass' or 'fail' to complete the audit.[/blue]")
    else:
        console.print("[yellow]No mastered problems available for audit.[/yellow]")
