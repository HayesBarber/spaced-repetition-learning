from rich.console import Console
from rich.panel import Panel
from utils import today
from commands.audit import get_current_audit, random_audit
from datetime import datetime, timedelta
import random
from storage import (
    load_json,
    NEXT_UP_FILE,
    CONFIG_FILE,
    PROGRESS_FILE,
)


def handle(args, console: Console):
    if should_audit() and not get_current_audit():
        problem = random_audit()
        if problem:
            console.print("[bold red]You have been randomly audited![/bold red]")
            console.print(f"[yellow]Audit problem:[/yellow] [cyan]{problem}[/cyan]")
            console.print(
                "Run [green]srl audit --pass[/green] or [red]--fail[/red] when done"
            )
            return

    problems = get_due_problems(args.n)
    if problems:
        console.print(
            Panel.fit(
                "\n".join(f"• {p}" for p in problems),
                title="[bold blue]Problems to Practice Today[/bold blue]",
                border_style="blue",
                title_align="left",
            )
        )
    else:
        console.print("[bold green]No problems due today or in Next Up.[/bold green]")


def should_audit():
    config = load_json(CONFIG_FILE)
    probability = config.get("audit_probability", 0.1)
    try:
        probability = float(probability)
    except (ValueError, TypeError):
        probability = 0.1
    return random.random() < probability


def get_due_problems(limit=None):
    data = load_json(PROGRESS_FILE)
    due = []

    for name, info in data.items():
        history = info["history"]
        if not history:
            continue
        last = history[-1]
        last_date = datetime.fromisoformat(last["date"]).date()
        due_date = last_date + timedelta(days=last["rating"])
        if due_date <= today():
            due.append((name, last_date, last["rating"]))

    # Sort: older last attempt first, then lower rating
    due.sort(key=lambda x: (x[1], x[2]))
    due_names = [name for name, _, _ in (due[:limit] if limit else due)]

    if not due_names:
        next_up = load_json(NEXT_UP_FILE)
        fallback = list(next_up.keys())[: limit or 3]
        return fallback

    return due_names
