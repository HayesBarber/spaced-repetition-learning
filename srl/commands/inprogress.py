from rich.console import Console
from rich.panel import Panel
from srl.storage import (
    load_json,
    PROGRESS_FILE,
)
from srl.utils import get_difficulty_tag


def add_subparser(subparsers):
    parser = subparsers.add_parser("inprogress", help="List problems in progress")
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    in_progress = get_in_progress()
    if in_progress:
        problem_lines = []
        for name, difficulty in in_progress:
            diff_tag = ""
            diff_tag = get_difficulty_tag(difficulty)
            problem_lines.append(f"• {name}{diff_tag}")

        console.print(
            Panel.fit(
                "\n".join(problem_lines),
                title=f"[bold magenta]Problems in Progress ({len(in_progress)})[/bold magenta]",
                border_style="magenta",
                title_align="left",
            )
        )
    else:
        console.print("[yellow]No problems currently in progress.[/yellow]")


def get_in_progress() -> list[tuple]:
    data = load_json(PROGRESS_FILE)
    res = []

    for name, info in data.items():
        difficulty = info.get("difficulty")
        res.append((name, difficulty))

    return res
