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
    max_days_without_audit: int = 7
    calendar_colors: dict[int, str] = field(
        default_factory=lambda: Config.default_calendar_colors()
    )
    backup: dict = field(
        default_factory=lambda: {
            "max_backups": 10,
            "replication_remote_host": "",
            "replication_remote_port": 8080,
            "replication_enabled": False,
        }
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

        known_fields = set(cls.__dataclass_fields__)
        filtered = {k: v for k, v in raw.items() if k in known_fields}
        return cls(**filtered)

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
        "--max-days-without-audit",
        type=int,
        help="Maximum days without audit (0 to disable, default: 7)",
    )
    parser.add_argument(
        "--max-backups",
        type=int,
        help="Maximum number of backups to retain",
    )
    parser.add_argument(
        "--replication-remote-host",
        type=str,
        help="Set replication remote host",
    )
    parser.add_argument(
        "--replication-remote-port",
        type=int,
        help="Set replication remote port",
    )
    parser.add_argument(
        "--replication-enabled",
        action="store_true",
        dest="replication_enabled",
        help="Enable replication",
    )
    parser.add_argument(
        "--replication-disabled",
        action="store_false",
        dest="replication_enabled",
        help="Disable replication",
    )
    parser.add_argument(
        "--get", action="store_true", help="Display current configuration"
    )
    parser.add_argument(
        "--set-color",
        action="append",
        help="Set a color for the calendar heatmap (format: level=#hex). Higher level = more activity. Can be repeated",
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
        return _handle_get(cfg, console)

    if getattr(args, "reset_colors", False):
        return _handle_reset_colors(cfg, console)

    if getattr(args, "set_color", []):
        return _handle_set_colors(cfg, console, args)

    return _handle_updates(cfg, console, args)


def _handle_get(cfg: Config, console: Console):
    console.print_json(data=cfg.__dict__)


def _handle_reset_colors(cfg: Config, console: Console):
    cfg.reset_colors()
    cfg.save()
    console.print("Colors reset")


def _handle_set_colors(cfg: Config, console: Console, args):
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


def _handle_updates(cfg: Config, console: Console, args):
    updated = []

    updates = [
        (
            args.audit_probability,
            lambda v: v >= 0,
            lambda v: cfg.set("audit_probability", v),
            lambda v: f"audit probability to [cyan]{v}[/cyan]",
        ),
        (
            args.max_days_without_audit,
            lambda v: v >= 0,
            lambda v: cfg.set("max_days_without_audit", v),
            lambda v: (
                "max days without audit to [cyan]disabled[/cyan]"
                if v == 0
                else f"max days without audit to [cyan]{v}[/cyan]"
            ),
        ),
        (
            args.max_backups,
            lambda v: v > 0,
            lambda v: cfg.backup.__setitem__("max_backups", v),
            lambda v: f"max backups to [cyan]{v}[/cyan]",
        ),
    ]

    for value, validator, setter, message in updates:
        if value is None or not validator(value):
            continue

        setter(value)
        updated.append(message(value))

    _handle_replication_updates(cfg, args, updated)

    if not updated:
        return console.print("[yellow]No valid configuration option provided.[/yellow]")

    cfg.save()
    console.print(f"Updated: {', '.join(updated)}")


def _handle_replication_updates(cfg, args, updated):
    replication_updates = {
        "replication_remote_host": args.replication_remote_host,
        "replication_remote_port": args.replication_remote_port,
        "replication_enabled": args.replication_enabled,
    }

    for key, value in replication_updates.items():
        if value is None:
            continue

        cfg.backup[key] = value

        if key == "replication_enabled":
            state = "enabled" if value else "disabled"
            updated.append(f"replication [cyan]{state}[/cyan]")
        else:
            label = key.replace("_", " ")
            updated.append(f"{label} to [cyan]{value}[/cyan]")
