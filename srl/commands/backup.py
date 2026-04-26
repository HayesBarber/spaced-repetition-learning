import io
import json
from datetime import datetime, timezone
from rich.console import Console
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


def prune_old_backups():
    max_backups = Config.load().backup.get("max_backups", 10)
    backups = sorted(BACKUP_DIR.glob("backup-*.tar.gz"))

    if len(backups) > max_backups:
        for old_backup in backups[:-max_backups]:
            old_backup.unlink()


def add_subparser(subparsers):
    parser = subparsers.add_parser("backup", help="Create backup archive")
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%S")
    base_filename = f"backup-{timestamp}"
    archive_path = BACKUP_DIR / f"{base_filename}.tar.gz"
    counter = 1
    while archive_path.exists():
        archive_path = BACKUP_DIR / f"{base_filename}-{counter}.tar.gz"
        counter += 1

    filename = archive_path.name

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
