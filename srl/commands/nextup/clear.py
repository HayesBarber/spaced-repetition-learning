from rich.console import Console
from srl.storage import (
    save_json,
    NEXT_UP_FILE,
)


def handle_clear(args, console: Console):
    save_json(NEXT_UP_FILE, {})
    console.print("[green]Next Up queue cleared.[/green]")
