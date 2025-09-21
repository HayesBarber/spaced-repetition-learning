from rich.console import Console
from srl.storage import (
    load_json,
    save_json,
    CONFIG_FILE,
)


def add_subparser(subparsers):
    parser = subparsers.add_parser("config", help="Update configuration values")
    parser.add_argument(
        "--audit-probability", type=float, help="Set audit probability (0-1)"
    )
    parser.add_argument(
        "--get", action="store_true", help="Display current configuration"
    )
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    if args.get:
        config = load_json(CONFIG_FILE)
        console.print_json(data=config)
    else:
        probability: float | None = args.audit_probability

        if probability is None or probability < 0:
            console.print("[yellow]Invalid configuration option provided.[/yellow]")
            return

        config = load_json(CONFIG_FILE)
        config["audit_probability"] = probability
        save_json(CONFIG_FILE, config)
        console.print(f"Audit probability set to [cyan]{probability}[/cyan]")
