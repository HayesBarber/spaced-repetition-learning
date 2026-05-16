from rich.console import Console
from srl.storage import (
    load_json,
    save_json,
    PROGRESS_FILE,
)


def add_subparser(subparsers):
    parser = subparsers.add_parser("remove", help="Remove a problem from in-progress")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "name", nargs="?", type=str, help="Name of the problem to remove"
    )
    group.add_argument(
        "-n", "--number", type=int, help="Problem number from `srl inprogress`"
    )
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    progress_data = load_json(PROGRESS_FILE)
    name, err = _resolve_name(progress_data, args)
    if err:
        return console.print(err)

    del progress_data[name]
    save_json(PROGRESS_FILE, progress_data)
    console.print(
        f"[green]Removed[/green] '[cyan]{name}[/cyan]' [green]from in-progress.[/green]"
    )


def _resolve_name(progress_data, args):
    """Returns tuple of (name, err)"""
    name = getattr(args, "name", None)
    number = getattr(args, "number", None)

    if number is not None:
        names = list(progress_data.keys())
        if number < 1 or number > len(names):
            return None, f"[red]Invalid problem number:[/red] {number}"

        name = names[args.number - 1]

    if name:
        key = _resolve_in_progress_key(progress_data, name.lower())
        if not key:
            return (
                None,
                f"[red]Problem[/red] '[cyan]{name}[/cyan]' [red]not found in in-progress.[/red]",
            )
        return key, None

    return None, "[red]Invalid args[/red]"


def _resolve_in_progress_key(progress_data: dict, name):
    """Returns progress_data key if name is in progress_data, None otherwise. Case insensitive. Expects name to be passed in as lowercase"""

    for key in progress_data:
        if key.lower() == name:
            return key

    return None
