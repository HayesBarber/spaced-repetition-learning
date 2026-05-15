from rich.console import Console
from rich.panel import Panel
from srl.utils import format_problem
from .util import get_next_up_problems


def add_subparser(subparsers):
    list_parser = subparsers.add_parser(
        "list",
        help="List queued problems",
    )
    list_parser.set_defaults(handler=handle_list)

    return list_parser


def handle_list(args, console: Console):
    next_up = get_next_up_problems()

    if not next_up:
        console.print("[yellow]Next Up queue is empty.[/yellow]")
        return

    lines = []
    for i, (name, url) in enumerate(next_up, start=1):
        display = format_problem(name, url)
        lines.append(f"{i}. {display}")

    console.print(
        Panel.fit(
            "\n".join(lines),
            title=f"[bold cyan]Next Up Problems ({len(next_up)})[/bold cyan]",
            border_style="cyan",
            title_align="left",
        )
    )
