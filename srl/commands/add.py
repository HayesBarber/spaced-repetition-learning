from rich.console import Console
from srl.utils import today
from srl.storage import (
    load_json,
    save_json,
    PROGRESS_FILE,
    MASTERED_FILE,
    NEXT_UP_FILE,
)


def add_subparser(subparsers):
    add = subparsers.add_parser("add", help="Add or update a problem attempt")
    add.add_argument("name", type=str, help="Name of the LeetCode problem")
    add.add_argument("rating", type=int, choices=range(1, 6), help="Rating from 1-5")
    add.add_argument(
        "difficulty",
        nargs="?",
        choices=["easy", "medium", "hard"],
        help="Difficulty level (optional)",
    )
    add.set_defaults(handler=handle)
    return add


def handle(args, console: Console):
    name: str = args.name
    rating: int = args.rating
    difficulty: str = args.difficulty

    data = load_json(PROGRESS_FILE)

    entry = data.get(name, {"history": []})
    entry["history"].append(
        {
            "rating": rating,
            "date": today().isoformat(),
        }
    )
    if difficulty:
        entry["difficulty"] = difficulty

    # Mastery check: last two ratings are 5
    history = entry["history"]
    if len(history) >= 2 and history[-1]["rating"] == 5 and history[-2]["rating"] == 5:
        mastered = load_json(MASTERED_FILE)
        if name in mastered:
            mastered[name]["history"].extend(history)
            # Preserve existing difficulty if not provided in this update, or update if provided
            if difficulty:
                mastered[name]["difficulty"] = difficulty
            elif "difficulty" in entry:
                 mastered[name]["difficulty"] = entry["difficulty"]
        else:
            mastered[name] = entry
        save_json(MASTERED_FILE, mastered)
        if name in data:
            del data[name]
        console.print(
            f"[bold green]{name}[/bold green] moved to [cyan]mastered[/cyan]!"
        )
    else:
        data[name] = entry
        console.print(
            f"Added rating [yellow]{rating}[/yellow] for '[cyan]{name}[/cyan]'"
        )

    save_json(PROGRESS_FILE, data)
    
    next_up = load_json(NEXT_UP_FILE)
    if name in next_up:
        del next_up[name]
        save_json(NEXT_UP_FILE, next_up)
