from rich.console import Console
from srl.storage import (
    load_json,
    save_json,
    CONFIG_FILE,
)


def handle(args, console: Console):
    probability: float | None = args.audit_probability

    if not probability:
        console.print("[yellow]No configuration option provided.[/yellow]")

    config = load_json(CONFIG_FILE)
    config["audit_probability"] = probability
    save_json(CONFIG_FILE, config)
    console.print(f"Audit probability set to [cyan]{probability}[/cyan]")
