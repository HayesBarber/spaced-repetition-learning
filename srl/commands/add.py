from rich.console import Console
from srl.utils import today
from srl.storage import (
    load_json,
    save_json,
    PROGRESS_FILE,
    MASTERED_FILE,
    NEXT_UP_FILE,
)
from srl.commands.list_ import get_due_problems


def add_subparser(subparsers):
    parser = subparsers.add_parser(
        "add",
        help="Add or update a problem attempt",
        description=(
            "Add or update a problem attempt. "
            "If no problem is specified, defaults to problem #1 from 'srl list'."
        ),
    )

    parser.add_argument(
        "rating",
        type=int,
        choices=range(1, 6),
        help="Rating from 1-5",
    )

    parser.add_argument(
        "-u",
        "--url",
        type=str,
        help="Problem URL",
    )

    parser.add_argument(
        "--amend",
        action="store_true",
        help="Replace the latest rating instead of adding a new attempt",
    )

    target = parser.add_mutually_exclusive_group()

    target.add_argument(
        "-n",
        "--number",
        type=int,
        help="Problem number from 'srl list'",
    )

    target.add_argument(
        "-p",
        "--problem",
        dest="name",
        type=str,
        help="Problem name",
    )

    parser.set_defaults(handler=handle)

    return parser


def handle(args, console: Console):
    name, err = _resolve_problem_name(args)
    if err:
        return console.print(err)

    rating: int = args.rating
    url: str = getattr(args, "url", "")
    data = load_json(PROGRESS_FILE)

    target_name = _get_canonical_name(data, name)
    entry = data.get(target_name, {"history": []})
    if getattr(args, "amend", False):
        if target_name not in data:
            console.print(
                f"[bold red]Problem '{target_name}' not found in progress[/bold red]"
            )
            return
        elif entry["history"]:
            entry["history"][-1]["rating"] = rating
        else:
            console.print(f"[bold red]No attempts found for '{target_name}'[/bold red]")
            return
    else:
        entry["history"].append(
            {
                "rating": rating,
                "date": today().isoformat(),
            }
        )
    if url:
        entry["url"] = url

    # Mastery check: last two ratings are 5
    history = entry["history"]
    if len(history) >= 2 and history[-1]["rating"] == 5 and history[-2]["rating"] == 5:
        mastered = load_json(MASTERED_FILE)
        if target_name in mastered:
            mastered[target_name]["history"].extend(history)
        else:
            mastered[target_name] = entry
        save_json(MASTERED_FILE, mastered)
        if target_name in data:
            del data[target_name]
        console.print(
            f"[bold green]{target_name}[/bold green] moved to [cyan]mastered[/cyan]!"
        )
    else:
        data[target_name] = entry
        console.print(
            f"Added rating [yellow]{rating}[/yellow] for '[cyan]{target_name}[/cyan]'"
        )

    save_json(PROGRESS_FILE, data)

    # Remove from next up if it exists there
    # and transfer the url if needed
    next_up = load_json(NEXT_UP_FILE)
    if target_name in next_up:
        if next_up[target_name].get("url") and not data[target_name].get("url"):
            data[target_name]["url"] = next_up[target_name]["url"]
            save_json(PROGRESS_FILE, data)

        del next_up[target_name]
        save_json(NEXT_UP_FILE, next_up)


def _resolve_problem_name(args) -> tuple[str, str]:
    """Returns tuple of (name, err)"""
    if hasattr(args, "number") and args.number is not None:
        problems = get_due_problems()
        if args.number > len(problems) or args.number <= 0:
            return None, f"[bold red]Invalid problem number: {args.number}[/bold red]"
        name = problems[args.number - 1][0]
        return name, None

    if hasattr(args, "name"):
        return args.name, None

    problems = get_due_problems()
    if len(problems) > 0:
        name = problems[0][0]
        return name, None

    return None, "[bold red]Unable to resolve problem name[/bold red]"


def _get_canonical_name(progress_data, name):
    """Returns existing problem name from progress_data case insensitive. If not found, returns name"""
    for key in progress_data:
        if key.lower() == name.lower():
            return key

    return name
