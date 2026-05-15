from rich.console import Console

from .utils import create_backup


def handle(args, console: Console):
    create_backup(console)


def add_subparser(subparsers):
    parser = subparsers.add_parser(
        "create",
        help="Create a backup",
    )

    parser.set_defaults(handler=handle)
