from rich.console import Console

from .utils import get_current_audit, random_audit


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
        console.print(f"Current audit problem: [cyan]{curr}[/cyan]")
        console.print("[blue]Run with 'pass' or 'fail' to complete it.[/blue]")
        return

    problem = random_audit()

    if problem:
        console.print(f"You are now being audited on: [cyan]{problem}[/cyan]")
        console.print(
            "[blue]Run with 'pass' or 'fail' to complete the audit.[/blue]"
        )
    else:
        console.print("[yellow]No mastered problems available for audit.[/yellow]")
