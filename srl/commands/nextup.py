from rich.console import Console
from rich.panel import Panel
from srl.utils import today
from srl.storage import (
    load_json,
    save_json,
    NEXT_UP_FILE,
)


def add_subparser(subparsers):
    parser = subparsers.add_parser("nextup", help="Next up problem queue")
    parser.add_argument(
        "action",
        choices=["add", "list", "remove", "clear"],
        help="Add, remove, list, or clear next-up problems",
    )
    parser.add_argument(
        "name", nargs="?", help="Problem name (only needed for 'add' or 'remove')"
    )
    parser.add_argument(
        "--file",
        "-f",
        help="Path to a file containing problem names (one per line)",
    )
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    if args.action == "add":
        if args.file:
            try:
                with open(args.file, "r") as f:
                    lines = [line.strip() for line in f.readlines()]
            except FileNotFoundError:
                console.print(f"[bold red]File not found:[/bold red] {args.file}")
                return

            added_count = 0
            for line in lines:
                if not line:
                    continue
                add_to_next_up(line, console)
                added_count += 1

            console.print(
                f"[green]Added {added_count} problems from file[/green] [bold]{args.file}[/bold] to Next Up Queue"
            )
        else:
            if not args.name:
                console.print(
                    "[bold red]Please provide a problem name to add to Next Up.[/bold red]"
                )
            else:
                add_to_next_up(args.name, console)
                console.print(
                    f"[green]Added[/green] [bold]{args.name}[/bold] to Next Up Queue"
                )
    elif args.action == "list":
        next_up = get_next_up_problems()
        if next_up:
            console.print(
                Panel.fit(
                    "\n".join(f"• {name}" for name in next_up),
                    title=f"[bold cyan]Next Up Problems ({len(next_up)})[/bold cyan]",
                    border_style="cyan",
                    title_align="left",
                )
            )
        else:
            console.print("[yellow]Next Up queue is empty.[/yellow]")
    elif args.action == "remove":
        if not args.name:
            console.print(
                "[bold red]Please provide a problem name to remove from Next Up.[/bold red]"
            )
        else:
            remove_from_next_up(args.name, console)
    elif args.action == "clear":
        clear_next_up(console)


def add_to_next_up(name, console):
    data = load_json(NEXT_UP_FILE)

    if name in data:
        console.print(f'[yellow]"{name}" is already in the Next Up queue.[/yellow]')
        return

    data[name] = {"added": today().isoformat()}
    save_json(NEXT_UP_FILE, data)


def get_next_up_problems() -> list[str]:
    data = load_json(NEXT_UP_FILE)
    res = []

    for name in data.keys():
        res.append(name)

    return res


def remove_from_next_up(name: str, console: Console):
    data = load_json(NEXT_UP_FILE)

    if name not in data:
        console.print(f'[yellow]"{name}" not found in the Next Up queue.[/yellow]')
        return

    del data[name]
    save_json(NEXT_UP_FILE, data)
    console.print(f"[green]Removed[/green] [bold]{name}[/bold] from Next Up Queue")


def clear_next_up(console: Console):
    save_json(NEXT_UP_FILE, {})
    console.print("[green]Next Up queue cleared.[/green]")
