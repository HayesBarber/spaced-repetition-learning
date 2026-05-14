from rich.console import Console

from .utils import get_current_audit, audit_fail


def add_subparser(subparsers):
    parser = subparsers.add_parser(
        "fail",
        help="Mark the current audit as failed",
    )

    parser.set_defaults(handler=handle_fail)
    return parser


def handle_fail(args, console: Console):
    curr = get_current_audit()

    if curr:
        audit_fail(curr, console)
        console.print("[red]Audit failed.[/red] Problem moved back to in-progress.")
    else:
        console.print("[yellow]No active audit to fail.[/yellow]")
