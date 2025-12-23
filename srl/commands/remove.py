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
    data = load_json(PROGRESS_FILE)
    name = getattr(args, "name", None)

    if getattr(args, "number", None) is not None:
        names = list(data.keys())

        if args.number < 1 or args.number > len(names):
            console.print(f"[red]Invalid problem number:[/red] {args.number}")
            return

        name = names[args.number - 1]

    if not name:
        console.print("[red]Invalid args[/red]")
        return

    if name in data:
        del data[name]
        save_json(PROGRESS_FILE, data)
        console.print(
            f"[green]Removed[/green] '[cyan]{name}[/cyan]' [green]from in-progress.[/green]"
        )
    else:
        console.print(
            f"[red]Problem[/red] '[cyan]{name}[/cyan]' [red]not found in in-progress.[/red]"
        )
