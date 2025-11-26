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
        "--file",
        "-f",
        help="Path to a file containing problem names (one per line)",
    )
    parser.add_argument(
        "--allow-mastered",
        action="store_true",
        help="Allow adding problems that are already mastered",
    )
    parser.add_argument(
        "--difficulty",
        "-d",
        choices=["easy", "medium", "hard"],
        help="Difficulty level",
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
                # File import doesn't support difficulty tag per line yet easily without parsing changes
                # So we pass None for difficulty when importing from file for now
                added = add_to_next_up(
                    line,
                    console,
                    hasattr(args, "allow_mastered") and args.allow_mastered,
                    difficulty=None,
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
                    difficulty=args.difficulty if hasattr(args, "difficulty") else None,
                )
                console.print(
                    f"[green]Added[/green] [bold]{args.name}[/bold] to Next Up Queue"
                )
    elif args.action == "list":
        next_up = get_next_up_problems()
        if next_up:
            problem_lines = []
            for name, difficulty in next_up:
                diff_tag = ""
                if difficulty:
                    color = {
                        "easy": "green",
                        "medium": "yellow",
                        "hard": "red",
                    }.get(difficulty.lower(), "white")
                    diff_tag = f" [{color}][{difficulty.capitalize()}][/{color}]"
                problem_lines.append(f"• {name}{diff_tag}")

            console.print(
                Panel.fit(
                    "\n".join(problem_lines),
                    title=f"[bold cyan]Next Up Problems ({len(next_up)})[/bold cyan]",
                    border_style="cyan",
                    title_align="left",
                )
            )
        else:
            console.print("[yellow]Next Up queue is empty.[/yellow]")
    elif args.action == "remove":
        if not args.name:
            console.print(
                "[bold red]Please provide a problem name to remove from Next Up.[/bold red]"
            )
        else:
            remove_from_next_up(args.name, console)
    elif args.action == "clear":
        clear_next_up(console)


def add_to_next_up(name, console, allow_mastered=False, difficulty=None) -> bool:
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

    entry = {"added": today().isoformat()}
    if difficulty:
        entry["difficulty"] = difficulty
    
    next_up[name] = entry
    save_json(NEXT_UP_FILE, next_up)
    return True


def get_next_up_problems() -> list[tuple]:
    data = load_json(NEXT_UP_FILE)
    res = []

    for name, info in data.items():
        difficulty = info.get("difficulty")
        res.append((name, difficulty))

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
