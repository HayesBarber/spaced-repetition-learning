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
    progress_data = load_json(PROGRESS_FILE)

    target_name = _get_canonical_name(progress_data, name)
    entry: dict = progress_data.get(target_name, {"history": []})
    if getattr(args, "amend", False):
        if err := _amend_problem(progress_data, entry, target_name, rating):
            return console.print(err)
    else:
        _append_problem(entry, rating)

    if url:
        entry["url"] = url

    display_text = _update_progress_data(progress_data, entry, target_name)
    console.print(display_text)

    _remove_from_nextup(progress_data, target_name)


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


def _amend_problem(progress_data, entry, name, rating) -> str | None:
    """Returns err as str or None if successful"""
    if name not in progress_data:
        return f"[bold red]Problem '{name}' not found in progress[/bold red]"
    elif entry["history"]:
        entry["history"][-1]["rating"] = rating
    else:
        return f"[bold red]No attempts found for '{name}'[/bold red]"


def _append_problem(entry, rating):
    entry["history"].append(
        {
            "rating": rating,
            "date": today().isoformat(),
        }
    )


def _update_progress_data(progress_data, entry, name) -> str:
    """Returns display_text"""
    display_text = _check_mastery(progress_data, entry, name)
    if not display_text:
        progress_data[name] = entry
        display_text = f"Added rating [yellow]{entry["history"][-1]["rating"]}[/yellow] for '[cyan]{name}[/cyan]'"

    save_json(PROGRESS_FILE, progress_data)

    return display_text


def _check_mastery(progress_data, entry, name) -> str | None:
    """Returns display_text if moved to mastered, None otherwise"""
    history = entry["history"]

    mastered = (
        len(history) >= 2 and history[-1]["rating"] == 5 and history[-2]["rating"] == 5
    )

    if not mastered:
        return None

    mastered = load_json(MASTERED_FILE)
    if name in mastered:
        mastered[name]["history"].extend(history)
    else:
        mastered[name] = entry
    save_json(MASTERED_FILE, mastered)

    if name in progress_data:
        del progress_data[name]

    return f"[bold green]{name}[/bold green] moved to [cyan]mastered[/cyan]!"


def _remove_from_nextup(progress_data, name):
    next_up = load_json(NEXT_UP_FILE)
    if name not in next_up:
        return

    if next_up[name].get("url") and not progress_data[name].get("url"):
        progress_data[name]["url"] = next_up[name]["url"]
        save_json(PROGRESS_FILE, progress_data)

    del next_up[name]
    save_json(NEXT_UP_FILE, next_up)
