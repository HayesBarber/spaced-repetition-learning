from rich.console import Console
from srl.storage import (
    load_json,
    save_json,
    CONFIG_FILE,
)
from dataclasses import dataclass


@dataclass
class Config:
    audit_probability: float = 0.1

    @classmethod
    def load(cls) -> "Config":
        raw = load_json(CONFIG_FILE)
        return cls(**raw)

    def save(self):
        save_json(CONFIG_FILE, self.__dict__)

    def set(self, key: str, value):
        if not hasattr(self, key):
            raise KeyError(f"Unknown config field: {key}")
        setattr(self, key, value)


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
    cfg = Config.load()

    if args.get:
        console.print_json(data=cfg.__dict__)
    else:
        probability: float | None = args.audit_probability

        if probability is None or probability < 0:
            console.print("[yellow]Invalid configuration option provided.[/yellow]")
            return

        cfg.set("audit_probability", probability)
        cfg.save()
        console.print(f"Audit probability set to [cyan]{probability}[/cyan]")
