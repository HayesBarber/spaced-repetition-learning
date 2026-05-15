import tarfile

from rich.console import Console

from .utils import (
    DATA_DIR,
    create_backup,
    resolve_existing_backup_path,
    validate_archive,
)


def handle(args, console: Console):
    backup_path = resolve_existing_backup_path(args.file)

    if backup_path is None:
        console.print(f"[red]Error: Backup file not found: {args.file}[/red]")
        return

    if not getattr(args, "yes", False):
        try:
            console.print(
                "This will overwrite current SRL state. Continue? (y/N): ",
                end="",
            )

            if input().strip().lower() not in ("y", "yes"):
                console.print("[yellow]Restore cancelled.[/yellow]")
                return

            console.print(
                "Create a backup of current state before restoring? (y/N): ",
                end="",
            )

            if input().strip().lower() in ("y", "yes"):
                create_backup(console)

        except KeyboardInterrupt:
            console.print("\n[yellow]Restore cancelled.[/yellow]")
            return
    else:
        create_backup(console)

    try:
        with tarfile.open(backup_path, "r:gz") as tar:
            manifest = validate_archive(tar)

            tar.extractall(DATA_DIR, filter="data")

            console.print(f"[green]Restore complete: {backup_path.name}[/green]")
            console.print(f"  Restored {len(manifest.get('files', []))} files.")

    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")

    except tarfile.TarError:
        console.print("[red]Error: Cannot open archive (corrupt or invalid).[/red]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def add_subparser(subparsers):
    parser = subparsers.add_parser(
        "restore",
        help="Restore from a backup",
    )

    parser.add_argument(
        "file",
        help="Backup file (filename or path)",
    )

    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Skip confirmation (creates a backup before restoring)",
    )

    parser.set_defaults(handler=handle)
