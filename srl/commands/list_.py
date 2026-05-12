from rich.console import Console
from rich.panel import Panel
from srl.utils import today
from srl.commands.audit import get_current_audit, random_audit, get_last_audit_date
from datetime import datetime, timedelta
import random
from srl.storage import (
    load_json,
    NEXT_UP_FILE,
    PROGRESS_FILE,
)
from srl.commands.config import Config

DEFAULT_NUM = 5


def add_subparser(subparsers):
    parser = subparsers.add_parser(
        "list",
        help="List due problems, supplementing from the Nextup Queue as needed",
    )

    parser.add_argument(
        "-n",
        "--num",
        type=int,
        default=DEFAULT_NUM,
        dest="n",
        help="Target number of problems to list, filling from the Nextup Queue as needed",
    )

    parser.set_defaults(handler=handle)

    return parser


def handle(args, console: Console):
    if should_audit() and not get_current_audit():
        problem, problem_url = random_audit(with_url=True)
        if problem:
            console.print("[bold red]You have been randomly audited![/bold red]")
            display = format_problem(problem, problem_url)
            console.print(f"[yellow]Audit problem:[/yellow] [cyan]{display}[/cyan]")
            console.print(
                "Run [green]srl audit pass[/green] or [red]fail[/red] when done"
            )
            return

    target_num: int = getattr(args, "n", DEFAULT_NUM)
    problems = get_due_problems(target_num)
    if not problems:
        console.print("[bold green]No problems due today or in Next Up.[/bold green]")
        return

    masters = mastery_candidates()
    lines = []
    for i, (name, url) in enumerate(problems):
        mark = " [magenta]*[/magenta]" if name in masters else ""
        display = format_problem(name, url)
        lines.append(f"{i + 1}. {display}{mark}")

    console.print(
        Panel.fit(
            "\n".join(lines),
            title=f"[bold blue]Problems to Practice [{today().isoformat()}] ({len(problems)})[/bold blue]",
            border_style="blue",
            title_align="left",
        )
    )


def should_audit():
    cfg = Config.load()

    # Check max days without audit first
    if cfg.max_days_without_audit and cfg.max_days_without_audit > 0:
        last_audit_date = get_last_audit_date()
        if last_audit_date:
            days_since_last = (today() - last_audit_date).days
            if days_since_last >= cfg.max_days_without_audit:
                return True

    # Fall back to probability-based audit
    probability = cfg.audit_probability
    try:
        probability = float(probability)
    except (ValueError, TypeError):
        probability = 0.1
    return random.random() < probability


def format_problem(problem: str, problem_url: str | None):
    """Returns "problem (url)" if url is present, otherwise "problem" """
    if problem_url:
        return f"{problem} ([blue]{problem_url}[/blue])"

    return problem


def get_due_problems(limit: int | None = None) -> list[tuple[str, str]]:
    """Return problems as ``(name, url)`` tuples.

    Due problems are returned first, sorted by oldest attempt then lowest rating.
    Remaining slots are filled from the Nextup Queue.

    Args:
        limit: Maximum number of problems to return. If ``None``, returns all due
            problems, or all Nextup Queue problems if no due problems exist.
    """
    data = load_json(PROGRESS_FILE)
    due = []

    for name, info in data.items():
        url = info.get("url", "")
        history = info["history"]
        if not history:
            continue
        last = history[-1]
        last_date = datetime.fromisoformat(last["date"]).date()
        due_date = last_date + timedelta(days=last["rating"])
        if due_date <= today():
            due.append((name, url, last_date, last["rating"]))

    # Sort: older last attempt first, then lower rating
    due.sort(key=lambda x: (x[2], x[3]))

    result = [(name, url) for name, url, _, _ in due[:limit]]

    if limit is None:
        if result:
            return result

        next_up = load_json(NEXT_UP_FILE)

        return [(prob, info.get("url", "")) for prob, info in next_up.items()]

    if len(result) >= limit:
        return result

    next_up = load_json(NEXT_UP_FILE)

    remaining = limit - len(result)

    supplement = [
        (prob, info.get("url", "")) for prob, info in list(next_up.items())[:remaining]
    ]

    return result + supplement


def mastery_candidates() -> set[str]:
    """Return names of problems whose *last* rating was 5."""
    data = load_json(PROGRESS_FILE)
    out = set()
    for name, info in data.items():
        hist = info.get("history", [])
        if hist and hist[-1].get("rating") == 5:
            out.add(name)
    return out
