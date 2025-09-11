from rich.console import Console
from rich.table import Table
from srl.storage import (
    load_json,
    MASTERED_FILE,
)


def handle(args, console: Console):
    mastered_problems = get_mastered_problems()
    if args.c:
        mastered_count = len(mastered_problems)
        console.print(f"[bold green]Mastered Count:[/bold green] {mastered_count}")
    else:
        if not mastered_problems:
            console.print("[yellow]No mastered problems yet.[/yellow]")
        else:
            table = Table(title="Mastered Problems", title_justify="left")
            table.add_column("Problem", style="cyan", no_wrap=True)
            table.add_column("Attempts", style="magenta")

            for name, attempts in mastered_problems:
                table.add_row(name, str(attempts))

            console.print(table)


def get_mastered_problems():
    data = load_json(MASTERED_FILE)
    mastered = []

    for name, info in data.items():
        history = info["history"]
        if not history:
            continue
        attempts = len(history)
        mastered.append((name, attempts))

    return mastered
