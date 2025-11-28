from rich.console import Console
from rich.panel import Panel
from srl.utils import today, get_difficulty_tag
from srl.commands.audit import get_current_audit, random_audit
from datetime import datetime, timedelta
import random
from srl.storage import (
    load_json,
    NEXT_UP_FILE,
    CONFIG_FILE,
    PROGRESS_FILE,
)


def add_subparser(subparsers):
    parser = subparsers.add_parser("list", help="List due problems")
    parser.add_argument("-n", type=int, default=None, help="Max number of problems")
    parser.set_defaults(handler=handle)
    return parser


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
        problem_lines = []
        for p in problems:
            name, _, _, difficulty = p
            diff_tag = get_difficulty_tag(difficulty)
            problem_lines.append(f"• {name}{diff_tag}")

        console.print(
            Panel.fit(
                "\n".join(problem_lines),
                title=f"[bold blue]Problems to Practice Today ({len(problems)})[/bold blue]",
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


def get_due_problems(limit=None) -> list[tuple]:
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
            difficulty = info.get("difficulty")
            due.append((name, last_date, last["rating"], difficulty))

    # Sort: older last attempt first, then lower rating
    due.sort(key=lambda x: (x[1], x[2]))
    
    # Slice if limit is provided
    if limit:
        due = due[:limit]

    # If we have due problems, return them (as tuples)
    if due:
        return due

    # Fallback to Next Up if no due problems
    next_up = load_json(NEXT_UP_FILE)
    # We need to return tuples to match the format: (name, date, rating, difficulty)
    # For Next Up items, date/rating are dummy values, difficulty is fetched if available
    fallback_items = []
    for name, info in list(next_up.items())[: limit or 3]:
        difficulty = info.get("difficulty")
        fallback_items.append((name, None, None, difficulty))
        
    return fallback_items
