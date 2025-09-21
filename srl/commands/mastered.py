from rich.console import Console
from rich.table import Table
from srl.storage import (
    load_json,
    MASTERED_FILE,
)


def add_subparser(subparsers):
    parser = subparsers.add_parser("mastered", help="List mastered problems")
    parser.add_argument(
        "-c", action="store_true", help="Show count of mastered problems"
    )
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    mastered_problems = get_mastered_problems()
    mastered_count = len(mastered_problems)
    if args.c:
        console.print(f"[bold green]Mastered Count:[/bold green] {mastered_count}")
    else:
        if not mastered_problems:
            console.print("[yellow]No mastered problems yet.[/yellow]")
        else:
            table = Table(
                title=f"Mastered Problems ({mastered_count})", title_justify="left"
            )
            table.add_column("Problem", style="cyan", no_wrap=True)
            table.add_column("Attempts", style="magenta")
            table.add_column("Mastered Date", style="green")

            for name, attempts, mastered_date in mastered_problems:
                table.add_row(name, str(attempts), mastered_date)

            console.print(table)


def get_mastered_problems():
    data = load_json(MASTERED_FILE)
    mastered = []

    for name, info in data.items():
        history = info["history"]
        if not history:
            continue
        attempts = len(history)
        mastered_date = history[-1]["date"]
        mastered.append((name, attempts, mastered_date))

    return mastered
