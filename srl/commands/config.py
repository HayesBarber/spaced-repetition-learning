from rich.console import Console
from srl.storage import (
    load_json,
    save_json,
    CONFIG_FILE,
)
from dataclasses import dataclass, field


@dataclass
class Config:
    audit_probability: float = 0.1
    calendar_colors: dict[int, str] = field(
        default_factory=lambda: Config.default_calendar_colors()
    )

    @staticmethod
    def default_calendar_colors() -> dict[int, str]:
        return {
            0: "#1a1a1a",
            1: "#99e699",
            2: "#33cc33",
            3: "#00ff00",
        }

    @classmethod
    def load(cls) -> "Config":
        raw = load_json(CONFIG_FILE)

        if "calendar_colors" in raw:
            raw["calendar_colors"] = {
                int(k): v for k, v in raw["calendar_colors"].items()
            }

        return cls(**raw)

    def save(self):
        save_json(CONFIG_FILE, self.__dict__)

    def set(self, key: str, value):
        if not hasattr(self, key):
            raise KeyError(f"Unknown config field: {key}")
        setattr(self, key, value)

    def reset_colors(self):
        self.calendar_colors = self.default_calendar_colors().copy()


def add_subparser(subparsers):
    parser = subparsers.add_parser("config", help="Update configuration values")
    parser.add_argument(
        "--audit-probability", type=float, help="Set audit probability (0-1)"
    )
    parser.add_argument(
        "--get", action="store_true", help="Display current configuration"
    )
    parser.add_argument(
        "--set-color",
        action="append",
        help="Set a calendar color (format: level=#hex). Can be repeated",
    )
    parser.add_argument(
        "--reset-colors",
        action="store_true",
        help="Reset calendar colors to defaults",
    )
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    cfg = Config.load()

    if getattr(args, "get", False):
        console.print_json(data=cfg.__dict__)
    elif getattr(args, "reset_colors", False):
        cfg.reset_colors()
        cfg.save()
        console.print("Colors reset")
    elif getattr(args, "set_color", []):
        updated_levels = []

        for entry in args.set_color:
            try:
                level_str, hex_value = entry.split("=")
                level = int(level_str)
                cfg.calendar_colors[level] = hex_value
                updated_levels.append(level)
            except ValueError:
                console.print(f"[red]Invalid format: {entry}[/red]")
                continue

        cfg.save()

        if updated_levels:
            lvls = ", ".join(str(level) for level in updated_levels)
            console.print(f"[green]Updated colors for level(s): {lvls}.[/green]")
        else:
            console.print("[yellow]No valid color updates provided.[/yellow]")
    else:
        probability: float | None = args.audit_probability

        if probability is None or probability < 0:
            console.print("[yellow]Invalid configuration option provided.[/yellow]")
            return

        cfg.set("audit_probability", probability)
        cfg.save()
        console.print(f"Audit probability set to [cyan]{probability}[/cyan]")
