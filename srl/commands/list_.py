from rich.console import Console
from rich.panel import Panel
from srl.utils import today
from srl.commands.audit import get_current_audit, random_audit
from datetime import datetime, timedelta
import random
from srl.storage import (
    load_json,
    NEXT_UP_FILE,
    PROGRESS_FILE,
)
from srl.commands.config import Config


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
    masters = mastery_candidates()

    if problems:
        lines = []
        for i, p in enumerate(problems):
            mark = " [magenta]★[/magenta]" if p in masters else ""
            lines.append(f"{i+1}. {p}{mark}")

        console.print(
            Panel.fit(
                "\n".join(lines),
                title=f"[bold blue]Problems to Practice [{today().isoformat()}] ({len(problems)})[/bold blue]",
                border_style="blue",
                title_align="left",
            )
        )
    else:
        console.print("[bold green]No problems due today or in Next Up.[/bold green]")


def should_audit():
    cfg = Config.load()
    probability = cfg.audit_probability
    try:
        probability = float(probability)
    except (ValueError, TypeError):
        probability = 0.1
    return random.random() < probability


def get_due_problems(limit=None) -> list[str]:
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


def mastery_candidates() -> set[str]:
    """Return names of problems whose *last* rating was 5."""
    data = load_json(PROGRESS_FILE)
    out = set()
    for name, info in data.items():
        hist = info.get("history", [])
        if hist and hist[-1].get("rating") == 5:
            out.add(name)
    return out
