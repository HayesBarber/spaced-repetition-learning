from rich.console import Console

from .utils import get_current_audit, audit_pass


def add_subparser(subparsers):
    parser = subparsers.add_parser(
        "pass",
        help="Mark the current audit as passed",
    )

    parser.set_defaults(handler=handle_pass)
    return parser


def handle_pass(args, console: Console):
    curr = get_current_audit()

    if curr:
        audit_pass(curr)
        console.print("[green]Audit passed![/green]")
    else:
        console.print("[yellow]No active audit to pass.[/yellow]")
