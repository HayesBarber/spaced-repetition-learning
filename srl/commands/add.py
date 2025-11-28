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
    add.set_defaults(handler=handle)
    return add


def handle(args, console: Console):
    name: str = args.name
    rating: int = args.rating

    data = load_json(PROGRESS_FILE)

    # Check for existing entry case-insensitively
    existing_name = None
    for key in data:
        if key.lower() == name.lower():
            existing_name = key
            break
    
    # Use existing name if found, otherwise use the provided name
    target_name = existing_name if existing_name else name
    entry = data.get(target_name, {"history": []})
    entry["history"].append(
        {
            "rating": rating,
            "date": today().isoformat(),
        }
    )

    # Mastery check: last two ratings are 5
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
    next_up = load_json(NEXT_UP_FILE)
    if target_name in next_up:
        del next_up[target_name]
        save_json(NEXT_UP_FILE, next_up)
