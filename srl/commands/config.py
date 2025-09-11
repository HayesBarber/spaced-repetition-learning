from rich.console import Console
from storage import (
    load_json,
    save_json,
    CONFIG_FILE,
)


def handle(args, console: Console):
    probability: float | None = args.audit_probability

    if not probability:
        print("No configuration option provided.")

    config = load_json(CONFIG_FILE)
    config["audit_probability"] = probability
    save_json(CONFIG_FILE, config)
    print(f"Audit probability set to {probability}")
