from rich.console import Console
from srl.storage import (
    load_json,
    save_json,
    PROGRESS_FILE,
    MASTERED_FILE,
)


def add_subparser(subparsers):
    parser = subparsers.add_parser("remove", help="Remove a problem from in-progress")
    parser.add_argument("name", type=str, help="Name of the problem to remove")
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    name: str = args.name

    data = load_json(PROGRESS_FILE)
    mastered = load_json(MASTERED_FILE)
    
    removed_from = []
    
    if name in data:
        del data[name]
        save_json(PROGRESS_FILE, data)
        removed_from.append("in-progress")
        
    if name in mastered:
        del mastered[name]
        save_json(MASTERED_FILE, mastered)
        removed_from.append("mastered")
        
    if removed_from:
        locations = " and ".join(removed_from)
        console.print(
            f"[green]Removed[/green] '[cyan]{name}[/cyan]' [green]from {locations}.[/green]"
        )
    else:
        console.print(
            f"[red]Problem[/red] '[cyan]{name}[/cyan]' [red]not found.[/red]"
        )
