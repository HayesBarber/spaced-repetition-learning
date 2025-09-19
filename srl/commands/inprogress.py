from rich.console import Console
from rich.panel import Panel
from srl.storage import (
    load_json,
    PROGRESS_FILE,
)


def handle(args, console: Console):
    in_progress = get_in_progress()
    if in_progress:
        console.print(
            Panel.fit(
                "\n".join(f"• {p}" for p in in_progress),
                title=f"[bold magenta]Problems in Progress ({len(in_progress)})[/bold magenta]",
                border_style="magenta",
                title_align="left",
            )
        )
    else:
        console.print("[yellow]No problems currently in progress.[/yellow]")


def get_in_progress():
    data = load_json(PROGRESS_FILE)
    res = []

    for name, _ in data.items():
        res.append(name)

    return res
