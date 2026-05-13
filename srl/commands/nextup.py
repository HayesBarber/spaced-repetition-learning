from rich.console import Console
from rich.panel import Panel
from srl.utils import today
from srl.commands.list_ import format_problem
from srl.storage import (
    load_json,
    save_json,
    NEXT_UP_FILE,
    PROGRESS_FILE,
    MASTERED_FILE,
)


def add_subparser(subparsers):
    parser = subparsers.add_parser(
        "nextup",
        help="Manage the next-up problem queue",
    )

    nextup_subparsers = parser.add_subparsers(required=True)

    # add
    add_parser = nextup_subparsers.add_parser(
        "add",
        help="Add problems to the queue",
    )
    add_parser.add_argument("name", nargs="?")
    add_parser.add_argument("-f", "--file")
    add_parser.add_argument(
        "--allow-mastered",
        action="store_true",
    )
    add_parser.add_argument(
        "-u",
        "--url",
        nargs="?",
        const="",
        default=None,
    )
    add_parser.set_defaults(handler=handle_add)

    # list
    list_parser = nextup_subparsers.add_parser(
        "list",
        help="List queued problems",
    )
    list_parser.set_defaults(handler=handle_list)

    # remove
    remove_parser = nextup_subparsers.add_parser(
        "remove",
        help="Remove a problem from the queue",
    )
    remove_parser.add_argument("name", nargs="?")
    remove_parser.add_argument(
        "-n",
        "--number",
        type=int,
    )
    remove_parser.set_defaults(handler=handle_remove)

    # clear
    clear_parser = nextup_subparsers.add_parser(
        "clear",
        help="Clear the queue",
    )
    clear_parser.set_defaults(handler=handle_clear)

    return parser


def handle_add(args, console: Console):
    if hasattr(args, "file") and args.file:
        try:
            with open(args.file, "r") as f:
                lines = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            console.print(f"[bold red]File not found:[/bold red] {args.file}")
            return

        added_count = 0
        for line in lines:
            if not line:
                continue
            parts = line.split(",", 1)
            name = parts[0].strip()
            url = parts[1].strip() if len(parts) > 1 else ""
            added = add_to_next_up(
                name,
                console,
                hasattr(args, "allow_mastered") and args.allow_mastered,
                url,
            )
            if added:
                added_count += 1

        console.print(
            f"[green]Added {added_count} problems from file[/green] [bold]{args.file}[/bold] to Next Up Queue"
        )
    else:
        if not args.name:
            console.print(
                "[bold red]Please provide a problem name to add to Next Up.[/bold red]"
            )
        else:
            add_to_next_up(
                args.name,
                console,
                hasattr(args, "allow_mastered") and args.allow_mastered,
                getattr(args, "url", ""),
            )
            console.print(
                f"[green]Added[/green] [bold]{args.name}[/bold] to Next Up Queue"
            )


def handle_list(args, console: Console):
    next_up = get_next_up_problems()

    if not next_up:
        console.print("[yellow]Next Up queue is empty.[/yellow]")
        return

    lines = []
    for i, (name, url) in enumerate(next_up, start=1):
        display = format_problem(name, url)
        lines.append(f"{i}. {display}")

    console.print(
        Panel.fit(
            "\n".join(lines),
            title=f"[bold cyan]Next Up Problems ({len(next_up)})[/bold cyan]",
            border_style="cyan",
            title_align="left",
        )
    )


def handle_remove(args, console: Console):
    if args.number is not None:
        problems = get_next_up_problems()
        if args.number < 1 or args.number > len(problems):
            console.print(f"[red]Invalid problem number:[/red] {args.number}")
            return
        args.name = problems[args.number - 1][0]
    if not args.name:
        console.print(
            "[bold red]Please provide a problem name to remove from Next Up.[/bold red]"
        )
    else:
        remove_from_next_up(args.name, console)


def handle_clear(args, console: Console):
    save_json(NEXT_UP_FILE, {})
    console.print("[green]Next Up queue cleared.[/green]")


# Keeping for now for testing backwards compat
def handle(args, console: Console):
    if args.action == "add":
        handle_add(args, console)
    elif args.action == "list":
        handle_list(args, console)
    elif args.action == "remove":
        handle_remove(args, console)
    elif args.action == "clear":
        handle_clear(args, console)


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


def get_next_up_problems() -> list[tuple[str, str]]:
    """
    returns a list of tuples (name, url)
    """
    data = load_json(NEXT_UP_FILE)
    res = []

    for name, info in data.items():
        res.append((name, info.get("url", "")))

    return res


def remove_from_next_up(name: str, console: Console):
    data = load_json(NEXT_UP_FILE)

    if name not in data:
        console.print(f'[yellow]"{name}" not found in the Next Up queue.[/yellow]')
        return

    del data[name]
    save_json(NEXT_UP_FILE, data)
    console.print(f"[green]Removed[/green] [bold]{name}[/bold] from Next Up Queue")
