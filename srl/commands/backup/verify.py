import tarfile

from rich.console import Console

from .utils import (
    resolve_existing_backup_path,
    validate_archive,
)


def handle(args, console: Console) -> int:
    backup_path = resolve_existing_backup_path(args.file)

    if backup_path is None:
        console.print(f"[red]Error: Backup file not found: {args.file}[/red]")
        return -1

    try:
        with tarfile.open(backup_path, "r:gz") as tar:
            manifest = validate_archive(tar)

            console.print(
                f"[green]Backup verified successfully: {backup_path.name}[/green]"
            )
            console.print(f"  Schema version: {manifest['schema_version']}")
            console.print(f"  Created: {manifest.get('created_at', 'unknown')}")
            console.print(f"  Files: {len(manifest.get('files', []))}")

    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        return -1

    except tarfile.TarError:
        console.print("[red]Error: Cannot open archive (corrupt or invalid).[/red]")
        return -1

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return -1

    return 0


def add_subparser(subparsers):
    parser = subparsers.add_parser(
        "verify",
        help="Verify a backup archive",
    )

    parser.add_argument(
        "file",
        help="Backup file (filename or path)",
    )

    parser.set_defaults(handler=handle)
