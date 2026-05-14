from rich.console import Console
from rich.panel import Panel
from srl.utils import format_problem
from srl.storage import (
    load_json,
    PROGRESS_FILE,
)


def add_subparser(subparsers):
    parser = subparsers.add_parser("inprogress", help="List problems in progress")
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    in_progress = get_in_progress()

    if not in_progress:
        console.print("[yellow]No problems currently in progress.[/yellow]")
        return

    lines = []
    for i, (name, url) in enumerate(in_progress, start=1):
        display = format_problem(name, url)
        lines.append(f"{i}. {display}")

    console.print(
        Panel.fit(
            "\n".join(lines),
            title=f"[bold magenta]Problems in Progress ({len(in_progress)})[/bold magenta]",
            border_style="magenta",
            title_align="left",
        )
    )


def get_in_progress() -> list[tuple[str, str]]:
    """Returns a list of in progress problems as ``(name, url)`` tuples."""
    data = load_json(PROGRESS_FILE)
    res = []

    for name, info in data.items():
        url = info.get("url", "")
        res.append((name, url))

    return res
