from rich.console import Console
from storage import (
    load_json,
    save_json,
    PROGRESS_FILE,
)


def handle(args, console: Console):
    name: str = args.name

    data = load_json(PROGRESS_FILE)
    if name in data:
        del data[name]
        save_json(PROGRESS_FILE, data)
        print(f"Removed '{name}' from in-progress.")
    else:
        print(f"Problem '{name}' not found in in-progress.")
