from rich.console import Console
from .utils import get_next_up_problems
from srl.storage import (
    load_json,
    save_json,
    NEXT_UP_FILE,
)


def add_subparser(subparsers):
    remove_parser = subparsers.add_parser(
        "remove",
        help="Remove a problem from the queue",
    )
    remove_parser.add_argument(
        "name",
        nargs="?",
        help="Problem name to remove",
    )
    remove_parser.add_argument(
        "-n",
        "--number",
        type=int,
        help="Problem number from 'srl nextup list'",
    )
    remove_parser.set_defaults(handler=handle_remove)

    return remove_parser


def handle_remove(args, console: Console):
    name = args.name
    if args.number is not None:
        problems = get_next_up_problems()
        if args.number < 1 or args.number > len(problems):
            console.print(f"[red]Invalid problem number:[/red] {args.number}")
            return
        name = problems[args.number - 1][0]

    if not name:
        console.print(
            "[bold red]Please provide a problem name to remove from Next Up.[/bold red]"
        )
    else:
        remove_from_next_up(name, console)


def remove_from_next_up(name: str, console: Console):
    data = load_json(NEXT_UP_FILE)

    if name not in data:
        console.print(f'[yellow]"{name}" not found in the Next Up queue.[/yellow]')
        return

    del data[name]
    save_json(NEXT_UP_FILE, data)
    console.print(f"[green]Removed[/green] [bold]{name}[/bold] from Next Up Queue")
