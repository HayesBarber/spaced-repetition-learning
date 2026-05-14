from rich.console import Console
from srl.commands.list_ import format_problem
from srl.utils import today
from srl.storage import (
    load_json,
    save_json,
    NEXT_UP_FILE,
    PROGRESS_FILE,
    MASTERED_FILE,
)


def add_subparser(subparsers):
    add_parser = subparsers.add_parser(
        "add",
        help="Add problem(s) to the queue",
    )
    add_parser.add_argument(
        "name",
        nargs="?",
        help="Problem name to add",
    )
    add_parser.add_argument(
        "-f",
        "--file",
        help="Path to a file with one problem per line: 'name' or 'name,url'",
    )
    add_parser.add_argument(
        "--allow-mastered",
        action="store_true",
        help="Allow problems that are already mastered",
    )
    add_parser.add_argument(
        "-u",
        "--url",
        nargs="?",
        const="",
        default=None,
        help="URL to the problem",
    )
    add_parser.set_defaults(handler=handle_add)

    return add_parser


def handle_add(args, console: Console):
    file = getattr(args, "file", None)
    allow_mastered = getattr(args, "allow_mastered", False)
    url = getattr(args, "url", "") or ""

    if file:
        handle_add_file(file, allow_mastered, console)
        return

    if not args.name:
        console.print(
            "[bold red]Please provide a problem name to add to Next Up.[/bold red]"
        )
        return

    add_to_next_up(
        args.name,
        console,
        allow_mastered,
        url,
    )

    console.print(f"[green]Added[/green] [bold]{args.name}[/bold] to Next Up Queue")


def handle_add_file(path: str, allow_mastered: bool, console: Console):
    try:
        with open(path, "r") as f:
            lines = [line.strip() for line in f]
    except FileNotFoundError:
        console.print(f"[bold red]File not found:[/bold red] {path}")
        return

    added_count = 0

    for line in lines:
        if not line:
            continue

        name, url = parse_problem_line(line)

        added = add_to_next_up(
            name,
            console,
            allow_mastered,
            url,
        )

        if added:
            added_count += 1

    console.print(
        f"[green]Added {added_count} problems from file[/green] "
        f"[bold]{path}[/bold] to Next Up Queue"
    )


def parse_problem_line(line: str) -> tuple[str, str]:
    parts = line.split(",", 1)

    name = parts[0].strip()
    url = parts[1].strip() if len(parts) > 1 else ""

    return name, url


def _create_name_lookup(json: dict[str, dict]) -> dict[str, str]:
    """Maps lowercase names to actual stored names for error messages."""
    return {key.lower(): key for key in json}


def _create_url_set(json: dict[str, dict]) -> set[str]:
    """Returns lowercase URLs from the json."""
    return {v.get("url", "").lower() for v in json.values() if v.get("url")}


def add_to_next_up(name, console, allow_mastered=False, url="") -> bool:
    """
    Add a problem to Next Up queue if not already present, in progress, or mastered.
    Returns True if added, False otherwise.
    """
    next_up = load_json(NEXT_UP_FILE)
    in_progress = load_json(PROGRESS_FILE)
    mastered = load_json(MASTERED_FILE)

    next_up_names_lower = _create_name_lookup(next_up)
    in_progress_names_lower = _create_name_lookup(in_progress)
    mastered_names_lower = _create_name_lookup(mastered)

    next_up_urls = _create_url_set(next_up)
    in_progress_urls = _create_url_set(in_progress)
    mastered_urls = _create_url_set(mastered)

    name_lower = name.lower()
    if name_lower in next_up_names_lower:
        existing = next_up_names_lower[name_lower]
        console.print(f'[yellow]"{existing}" is already in the Next Up queue.[/yellow]')
        return False

    if name_lower in in_progress_names_lower:
        existing = in_progress_names_lower[name_lower]
        console.print(f'[yellow]"{existing}" is already in progress.[/yellow]')
        return False

    if name_lower in mastered_names_lower:
        if allow_mastered:
            existing = mastered_names_lower[name_lower]
            console.print(
                f'[blue]"{existing}" is mastered but will be added due to flag.[/blue]'
            )
        else:
            existing = mastered_names_lower[name_lower]
            console.print(f'[yellow]"{existing}" is already mastered.[/yellow]')
            return False

    if url:
        url_lower = url.lower()
        if url_lower in next_up_urls:
            console.print(
                "[yellow]A problem with that URL is already in the Next Up queue.[/yellow]"
            )
            return False
        if url_lower in in_progress_urls:
            console.print(
                "[yellow]A problem with that URL is already in progress.[/yellow]"
            )
            return False
        if url_lower in mastered_urls:
            if allow_mastered:
                console.print(
                    "[blue]A problem with that URL is mastered but will be added due to flag.[/blue]"
                )
            else:
                console.print(
                    "[yellow]A problem with that URL is already mastered.[/yellow]"
                )
                return False

    next_up[name] = {"added": today().isoformat()}
    if url:
        next_up[name]["url"] = url

    save_json(NEXT_UP_FILE, next_up)
    return True
