from rich.console import Console
from rich.table import Table

from .utils import (
    BACKUP_DIR,
    format_size,
    parse_timestamp_from_name,
)


def handle(args, console: Console):
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    backups = sorted(BACKUP_DIR.glob("backup-*.tar.gz"))

    if not backups:
        console.print("[yellow]No backups found.[/yellow]")
        return

    table = Table(title="Backups", show_header=True)

    table.add_column("Filename", style="cyan")
    table.add_column("Created", style="green")
    table.add_column("Size", justify="right", style="magenta")

    for archive in backups:
        ts = parse_timestamp_from_name(archive.name)

        if ts:
            created = ts.strftime("%Y-%m-%d %H:%M:%S")
        else:
            created = "unknown"

        size = format_size(archive.stat().st_size)

        table.add_row(archive.name, created, size)

    console.print(table)


def add_subparser(subparsers):
    parser = subparsers.add_parser(
        "list",
        help="List backups",
    )

    parser.set_defaults(handler=handle)
