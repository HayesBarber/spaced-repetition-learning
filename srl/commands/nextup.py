from rich.console import Console
from rich.panel import Panel
from srl.utils import today
from srl.storage import (
    load_json,
    save_json,
    NEXT_UP_FILE,
    PROGRESS_FILE,
    MASTERED_FILE,
)


def add_subparser(subparsers):
    parser = subparsers.add_parser("nextup", help="Next up problem queue")
    parser.add_argument(
        "action",
        choices=["add", "list", "remove", "clear"],
        help="Add, remove, list, or clear next-up problems",
    )
    parser.add_argument(
        "name", nargs="?", help="Problem name (only needed for 'add' or 'remove')"
    )
    parser.add_argument(
        "-f",
        "--file",
        help="Path to a file containing problem names (one per line)",
    )
    parser.add_argument(
        "--allow-mastered",
        action="store_true",
        help="Allow adding problems that are already mastered",
    )
    parser.add_argument(
        "-n",
        "--number",
        type=int,
        help="Remove by 1-based index from 'srl nextup list'",
    )
    parser.add_argument(
        "-u",
        "--url",
        nargs="?",
        type=str,
        const="",
        default=None,
        help="URL to the problem for 'add' or include URLs in output for 'list'",
    )
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    if args.action == "add":
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
    elif args.action == "list":
        url_requested = isinstance(getattr(args, "url", None), str)
        next_up = get_next_up_problems(include_urls=url_requested)

        if next_up:
            lines = []
            for i, name in enumerate(next_up, start=1):
                if url_requested:
                    if name[1]:
                        lines.append(
                            f"{i}. {name[0]}  [blue][link={name[1]}]Open in Browser[/link][/blue]"
                        )
                    else:
                        lines.append(f"{i}. {name[0]}")
                else:
                    lines.append(f"{i}. {name}")

            console.print(
                Panel.fit(
                    "\n".join(lines),
                    title=f"[bold cyan]Next Up Problems ({len(next_up)})[/bold cyan]",
                    border_style="cyan",
                    title_align="left",
                )
            )
        else:
            console.print("[yellow]Next Up queue is empty.[/yellow]")
    elif args.action == "remove":
        if args.number is not None:
            problems = get_next_up_problems()
            if args.number < 1 or args.number > len(problems):
                console.print(f"[red]Invalid problem number:[/red] {args.number}")
                return
            args.name = problems[args.number - 1]
        if not args.name:
            console.print(
                "[bold red]Please provide a problem name to remove from Next Up.[/bold red]"
            )
        else:
            remove_from_next_up(args.name, console)
    elif args.action == "clear":
        clear_next_up(console)


def add_to_next_up(name, console, allow_mastered=False, url="") -> bool:
    """
    Add a problem to Next Up queue if not already present, in progress, or mastered.
    Returns True if added, False otherwise.
    """
    next_up = load_json(NEXT_UP_FILE)
    in_progress = load_json(PROGRESS_FILE)
    mastered = load_json(MASTERED_FILE)

    if name in next_up:
        console.print(f'[yellow]"{name}" is already in the Next Up queue.[/yellow]')
        return False

    if name in in_progress:
        console.print(f'[yellow]"{name}" is already in progress.[/yellow]')
        return False

    if name in mastered:
        if allow_mastered:
            console.print(
                f'[blue]"{name}" is mastered but will be added due to flag.[/blue]'
            )
        else:
            console.print(f'[yellow]"{name}" is already mastered.[/yellow]')
            return False

    next_up[name] = {"added": today().isoformat()}
    if url:
        next_up[name]["url"] = url

    save_json(NEXT_UP_FILE, next_up)
    return True


def get_next_up_problems(include_urls=False) -> list[str] | list[tuple[str, str]]:
    """
    returns a list of tuples (name, url) if include_urls is True
    otherwise returns a list of only problem names
    """
    data = load_json(NEXT_UP_FILE)
    res = []

    for name, info in data.items():
        if include_urls:
            res.append((name, info.get("url", "")))
        else:
            res.append(name)

    return res


def remove_from_next_up(name: str, console: Console):
    data = load_json(NEXT_UP_FILE)

    if name not in data:
        console.print(f'[yellow]"{name}" not found in the Next Up queue.[/yellow]')
        return

    del data[name]
    save_json(NEXT_UP_FILE, data)
    console.print(f"[green]Removed[/green] [bold]{name}[/bold] from Next Up Queue")


def clear_next_up(console: Console):
    save_json(NEXT_UP_FILE, {})
    console.print("[green]Next Up queue cleared.[/green]")
