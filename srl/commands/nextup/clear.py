from rich.console import Console
from srl.storage import (
    save_json,
    NEXT_UP_FILE,
)


def add_subparser(subparsers):
    clear_parser = subparsers.add_parser(
        "clear",
        help="Clear the queue",
    )
    clear_parser.set_defaults(handler=handle_clear)
    return clear_parser


def handle_clear(args, console: Console):
    save_json(NEXT_UP_FILE, {})
    console.print("[green]Next Up queue cleared.[/green]")
