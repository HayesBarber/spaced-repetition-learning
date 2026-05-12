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
        help="List due problems or fall back to the Nextup Queue",
    )

    parser.add_argument(
        "-n",
        "--num",
        type=int,
        default=DEFAULT_NUM,
        help="Target number of problems to list, filling from the Nextup Queue as needed",
    )

    url_group = parser.add_mutually_exclusive_group()

    url_group.add_argument(
        "--raw-urls",
        dest="url_format",
        action="store_const",
        const="raw",
        default="markdown",
        help="Show raw URLs instead of Markdown links",
    )

    url_group.add_argument(
        "--no-urls",
        dest="url_format",
        action="store_const",
        const="none",
        help="Omit URLs from output",
    )

    parser.set_defaults(handler=handle)

    return parser


def handle(args, console: Console):
    if should_audit() and not get_current_audit():
        problem = random_audit()
        if problem:
            console.print("[bold red]You have been randomly audited![/bold red]")
            console.print(f"[yellow]Audit problem:[/yellow] [cyan]{problem}[/cyan]")
            console.print(
                "Run [green]srl audit pass[/green] or [red]fail[/red] when done"
            )
            return

    target_num: int = getattr(args, "num", DEFAULT_NUM)
    problems = get_due_problems(target_num)
    if not problems:
        console.print("[bold green]No problems due today or in Next Up.[/bold green]")
        return

    include_url = True
    formatted = format_problems(problems, include_url)
    names = [name for name, _ in problems]
    masters = mastery_candidates()

    lines = []
    for i, p in enumerate(formatted):
        mark = " [magenta]*[/magenta]" if names[i] in masters else ""
        lines.append(f"{i + 1}. {p}{mark}")

    console.print(
        Panel.fit(
            "\n".join(lines),
            title=f"[bold blue]Problems to Practice [{today().isoformat()}] ({len(formatted)})[/bold blue]",
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


def format_problems(
    problems: list[tuple[str, str]], include_url: bool = False
) -> list[str]:
    if not include_url:
        return [name for name, _ in problems]

    return [
        f"{name}  [blue][link={url}]Open in Browser[/link][/blue]" if url else name
        for name, url in problems
    ]


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
