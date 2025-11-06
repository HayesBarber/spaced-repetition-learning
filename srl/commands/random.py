from rich.console import Console
import random
from srl.commands.list_ import get_due_problems
from srl.storage import load_json, PROGRESS_FILE, MASTERED_FILE, NEXT_UP_FILE


def add_subparser(subparsers):
    parser = subparsers.add_parser(
        "random",
        help="Pick a random due problem (use --all to pick from progress, mastered and next up)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        dest="all",
        help="Pick a random problem from all problems (progress, mastered, next up)",
    )
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    # If --all requested, aggregate from all storage files (progress, mastered, next_up)
    if getattr(args, "all", False):
        progress = load_json(PROGRESS_FILE)
        mastered = load_json(MASTERED_FILE)
        next_up = load_json(NEXT_UP_FILE)

        names = set()
        if isinstance(progress, dict):
            names.update(progress.keys())
        if isinstance(mastered, dict):
            names.update(mastered.keys())
        if isinstance(next_up, dict):
            names.update(next_up.keys())

        names = list(names)
        if not names:
            console.print("[bold green]No problems available to pick from.[/bold green]")
            return

        choice = random.choice(names)
        console.print(f"[bold blue]Random problem (all):[/bold blue] [cyan]{choice}[/cyan]")
        return

    # default behaviour: pick from due problems (falls back to Next Up)
    problems = get_due_problems()
    if not problems:
        console.print("[bold green]No problems available to pick from.[/bold green]")
        return

    choice = random.choice(problems)
    console.print(f"[bold blue]Random problem:[/bold blue] [cyan]{choice}[/cyan]")
