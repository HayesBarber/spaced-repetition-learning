import io
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from rich.console import Console
from rich.table import Table
import tarfile

from srl.storage import DATA_DIR, BACKUP_DIR
from srl.commands.config import Config

STORAGE_FILES = [
    "problems_in_progress.json",
    "problems_mastered.json",
    "next_up.json",
    "audit.json",
    "config.json",
]

BACKUP_REPLICATION_ENDPOINT = "/backup"


def _format_size(size: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def _parse_timestamp_from_name(name: str) -> datetime | None:
    import re

    match = re.search(r"backup-(\d{4}-\d{2}-\d{2}T\d{6})", name)
    if not match:
        match = re.search(r"backup-(\d{8}T\d{6})", name)
    if match:
        ts = match.group(1)
        if "-" in ts:
            try:
                return datetime.strptime(ts, "%Y-%m-%dT%H%M%S").replace(
                    tzinfo=timezone.utc
                )
            except ValueError:
                pass
    return None


def list_handle(args, console: Console):
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
        ts = _parse_timestamp_from_name(archive.name)
        if ts:
            created = ts.strftime("%Y-%m-%d %H:%M:%S")
        else:
            created = "unknown"

        size = _format_size(archive.stat().st_size)
        table.add_row(archive.name, created, size)

    console.print(table)


def _get_archive_members(tar: tarfile.TarFile) -> set[str]:
    return set(tar.getnames())


def _read_manifest(tar: tarfile.TarFile) -> dict | None:
    manifest_file = tar.extractfile("manifest.json")
    if manifest_file is None:
        return None
    return json.loads(manifest_file.read().decode())


def verify_handle(args, console: Console) -> int:
    """Returns 0 if valid, non-zero otherwise"""
    file_arg = getattr(args, "file", None)
    if not file_arg:
        console.print("[red]Error: No backup file specified.[/red]")
        return -1

    backup_path = Path(file_arg)
    if not backup_path.exists():
        resolved = BACKUP_DIR / file_arg
        if resolved.exists():
            backup_path = resolved
        else:
            console.print(f"[red]Error: Backup file not found: {file_arg}[/red]")
            return -1

    try:
        with tarfile.open(backup_path, "r:gz") as tar:
            members = _get_archive_members(tar)

            if "manifest.json" not in members:
                console.print("[red]Error: manifest.json not found in archive.[/red]")
                return -1

            manifest = _read_manifest(tar)
            if manifest is None:
                console.print(
                    "[red]Error: Failed to parse manifest.json (invalid JSON).[/red]"
                )
                return -1

            if "schema_version" not in manifest:
                console.print("[red]Error: manifest.json missing schema_version.[/red]")
                return -1

            for fname in manifest.get("files", []):
                if fname not in members:
                    console.print(
                        f"[red]Error: Referenced file not in archive: {fname}[/red]"
                    )
                    return -1

            console.print(
                f"[green]Backup verified successfully: {backup_path.name}[/green]"
            )
            console.print(f"  Schema version: {manifest['schema_version']}")
            console.print(f"  Created: {manifest.get('created_at', 'unknown')}")
            console.print(f"  Files: {len(manifest.get('files', []))}")

    except tarfile.TarError:
        console.print("[red]Error: Cannot open archive (corrupt or invalid).[/red]")
        return -1
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return -1

    return 0


def prune_old_backups():
    max_backups = Config.load().backup.get("max_backups", 10)
    if max_backups <= 0:
        max_backups = 10
    backups = sorted(BACKUP_DIR.glob("backup-*.tar.gz"))

    if len(backups) > max_backups:
        for old_backup in backups[:-max_backups]:
            old_backup.unlink()


def restore_handle(args, console: Console):
    file_arg = getattr(args, "file", None)
    if not file_arg:
        console.print("[red]Error: No backup file specified.[/red]")
        return

    backup_path = Path(file_arg)
    if not backup_path.exists():
        resolved = BACKUP_DIR / file_arg
        if resolved.exists():
            backup_path = resolved
        else:
            console.print(f"[red]Error: Backup file not found: {file_arg}[/red]")
            return

    auto_yes = getattr(args, "yes", False)
    if auto_yes:
        handle(args, console)
    else:
        try:
            console.print(
                "This will overwrite current SRL state. Continue? (y/N): ", end=""
            )
            if input().strip().lower() not in ("y", "yes"):
                console.print("[yellow]Restore cancelled.[/yellow]")
                return

            console.print(
                "Create a backup of current state before restoring? (y/N): ", end=""
            )
            if input().strip().lower() in ("y", "yes"):
                handle(args, console)
        except KeyboardInterrupt:
            console.print("\n[yellow]Restore cancelled.[/yellow]")
            return

    try:
        with tarfile.open(backup_path, "r:gz") as tar:
            members = _get_archive_members(tar)

            if "manifest.json" not in members:
                console.print("[red]Error: manifest.json not found in archive.[/red]")
                return

            manifest = _read_manifest(tar)
            if manifest is None:
                console.print(
                    "[red]Error: Failed to parse manifest.json (invalid JSON).[/red]"
                )
                return

            if "schema_version" not in manifest:
                console.print("[red]Error: manifest.json missing schema_version.[/red]")
                return

            for fname in manifest.get("files", []):
                if fname not in members:
                    console.print(
                        f"[red]Error: Referenced file not in archive: {fname}[/red]"
                    )
                    return

            tar.extractall(DATA_DIR, filter="data")

            console.print(f"[green]Restore complete: {backup_path.name}[/green]")
            console.print(f"  Restored {len(manifest.get('files', []))} files.")

    except tarfile.TarError:
        console.print("[red]Error: Cannot open archive (corrupt or invalid).[/red]")
        return
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return


def replicate_backup(filename, console: Console):
    backup_cfg = Config.load().backup
    enabled = backup_cfg.get("replication_enabled", False)
    if not enabled:
        return

    remote_host = backup_cfg.get("replication_remote_host")
    remote_port = backup_cfg.get("replication_remote_port", 8080)
    if not remote_host:
        console.stderr = True
        console.print("[yellow]Remote host not configured for replication[/yellow]")
        return

    url = f"http://{remote_host}:{remote_port}{BACKUP_REPLICATION_ENDPOINT}"
    archive_path = BACKUP_DIR / filename

    if not archive_path.exists():
        console.stderr = True
        console.print("[yellow]Backup file not found for replication[/yellow]")
        return

    try:
        with open(archive_path, "rb") as f:
            backup_data = f.read()

        req = urllib.request.Request(url, data=backup_data, method="POST")
        req.add_header("Content-Type", "application/gzip")
        req.add_header("Content-Length", str(len(backup_data)))

        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                console.print(
                    f"[green]Backup replicated to remote: {remote_host}:{remote_port}[/green]"
                )
            else:
                console.stderr = True
                console.print(
                    f"[yellow]Remote replication failed with status {response.status}[/yellow]"
                )
    except urllib.error.URLError as e:
        console.stderr = True
        console.print(
            f"[yellow]Failed to connect to remote server: {e.reason}[/yellow]"
        )
    except Exception as e:
        console.stderr = True
        console.print(f"[yellow]Error during replication: {e}[/yellow]")

    console.stderr = False


def resolve_backup_path():
    """Returns a valid filename, archive_path"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%S")
    base_filename = f"backup-{timestamp}"
    archive_path = BACKUP_DIR / f"{base_filename}.tar.gz"
    counter = 1
    while archive_path.exists():
        archive_path = BACKUP_DIR / f"{base_filename}-{counter}.tar.gz"
        counter += 1

    filename = archive_path.name

    return filename, archive_path


def add_subparser(subparsers):
    parser = subparsers.add_parser("backup", help="Backup commands")
    subparsers2 = parser.add_subparsers(dest="backup_subcommand")

    list_parser = subparsers2.add_parser("list", help="List all backups")
    list_parser.set_defaults(handler=list_handle)

    verify_parser = subparsers2.add_parser("verify", help="Verify a backup archive")
    verify_parser.add_argument("file", help="Backup file (filename or path)")
    verify_parser.set_defaults(handler=verify_handle)

    restore_parser = subparsers2.add_parser("restore", help="Restore from a backup")
    restore_parser.add_argument("file", help="Backup file (filename or path)")
    restore_parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Skip confirmation and create a backup before restoring",
    )
    restore_parser.set_defaults(handler=restore_handle)

    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    filename, archive_path = resolve_backup_path()

    try:
        files_to_backup = []
        for fname in STORAGE_FILES:
            fpath = DATA_DIR / fname
            if fpath.exists():
                files_to_backup.append((fpath, fname))

        manifest = {
            "schema_version": 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "files": [fname for _, fname in files_to_backup],
        }

        with tarfile.open(archive_path, "w:gz") as tar:
            for fpath, arcname in files_to_backup:
                tar.add(fpath, arcname=arcname)

            manifest_data = json.dumps(manifest, indent=2).encode()
            tarinfo = tarfile.TarInfo(name="manifest.json")
            tarinfo.size = len(manifest_data)
            tar.addfile(tarinfo, io.BytesIO(manifest_data))

        prune_old_backups()
        console.print(f"[green]Backup created: {filename}[/green]")

    except Exception:
        if archive_path.exists():
            archive_path.unlink()
        raise

    replicate_backup(filename, console)
