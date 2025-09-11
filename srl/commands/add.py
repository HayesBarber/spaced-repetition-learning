from rich.console import Console
from srl.utils import today
from storage import (
    load_json,
    save_json,
    PROGRESS_FILE,
    MASTERED_FILE,
    NEXT_UP_FILE,
)


def handle(args, console: Console):
    name: str = args.name
    rating: int = args.rating

    data = load_json(PROGRESS_FILE)

    entry = data.get(name, {"history": []})
    entry["history"].append(
        {
            "rating": rating,
            "date": today().isoformat(),
        }
    )

    # Mastery check: last two ratings are 5
    history = entry["history"]
    if len(history) >= 2 and history[-1]["rating"] == 5 and history[-2]["rating"] == 5:
        mastered = load_json(MASTERED_FILE)
        mastered[name] = entry
        save_json(MASTERED_FILE, mastered)
        if name in data:
            del data[name]
        print(f"{name} moved to mastered!")
    else:
        data[name] = entry
        print(f"Added rating {rating} for '{name}'")

    save_json(PROGRESS_FILE, data)

    # Remove from next up if it exists there
    next_up = load_json(NEXT_UP_FILE)
    if name in next_up:
        del next_up[name]
        save_json(NEXT_UP_FILE, next_up)
