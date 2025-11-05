from rich.console import Console
import random
from srl.commands.list_ import get_due_problems


def add_subparser(subparsers):
    parser = subparsers.add_parser("random", help="Pick a random due problem")
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    problems = get_due_problems()
    if not problems:
        console.print("[bold green]No problems available to pick from.[/bold green]")
        return

    choice = random.choice(problems)
    console.print(f"[bold blue]Random problem:[/bold blue] [cyan]{choice}[/cyan]")
