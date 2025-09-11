from rich.console import Console
from rich.panel import Panel
from srl.utils import today
from srl.storage import (
    load_json,
    save_json,
    NEXT_UP_FILE,
)


def handle(args, console: Console):
    if args.action == "add":
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
        next_up = load_json(NEXT_UP_FILE)
        if next_up:
            console.print(
                Panel.fit(
                    "\n".join(f"• {name}" for name in next_up),
                    title="[bold cyan]Next Up Problems[/bold cyan]",
                    border_style="cyan",
                    title_align="left",
                )
            )
        else:
            console.print("[yellow]Next Up queue is empty.[/yellow]")


def add_to_next_up(name, console):
    data = load_json(NEXT_UP_FILE)

    if name in data:
        console.print(f'[yellow]"{name}" is already in the Next Up queue.[/yellow]')
        return

    data[name] = {"added": today().isoformat()}
    save_json(NEXT_UP_FILE, data)
