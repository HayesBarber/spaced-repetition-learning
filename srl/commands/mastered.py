from rich.console import Console
from rich.table import Table
from srl.storage import (
    load_json,
    MASTERED_FILE,
)
from srl.utils import fuzzy_find


def add_subparser(subparsers):
    parser = subparsers.add_parser("mastered", help="List mastered problems")
    parser.add_argument(
        "-c", "--count", action="store_true", help="Show count of mastered problems"
    )
    parser.add_argument(
        "-f",
        "--fuzzy",
        type=str,
        dest="query",
        help="Fuzzy find by query",
    )
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    mastered_problems = get_mastered_problems()
    count_only = getattr(args, "count", False)
    query = getattr(args, "query", None)

    mastered_problems, mastered_count = _resolve_query(query, mastered_problems)

    if count_only:
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


def _resolve_query(query, mastered_problems):
    if not query:
        return (mastered_problems, len(mastered_problems))

    problems = [
        {
            "problem": name,
            "attempts": attempts,
            "mastered_date": mastered_date,
        }
        for name, attempts, mastered_date in mastered_problems
    ]
    results = fuzzy_find(query, problems)
    mastered_problems = [
        (d["problem"], d["attempts"], d["mastered_date"]) for _, d in results
    ]
    return (mastered_problems, len(mastered_problems))


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
