import io
import json
import tarfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from srl.commands.config import Config
from srl.storage import BACKUP_DIR, DATA_DIR

STORAGE_FILES = [
    "problems_in_progress.json",
    "problems_mastered.json",
    "next_up.json",
    "audit.json",
    "config.json",
]

BACKUP_REPLICATION_ENDPOINT = "/backup"


def format_size(size: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def parse_timestamp_from_name(name: str) -> datetime | None:
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


def get_archive_members(tar: tarfile.TarFile) -> set[str]:
    return set(tar.getnames())


def read_manifest(tar: tarfile.TarFile) -> dict | None:
    manifest_file = tar.extractfile("manifest.json")

    if manifest_file is None:
        return None

    return json.loads(manifest_file.read().decode())


def validate_archive(tar: tarfile.TarFile):
    members = get_archive_members(tar)

    if "manifest.json" not in members:
        raise ValueError("manifest.json not found in archive")

    manifest = read_manifest(tar)

    if manifest is None:
        raise ValueError("Failed to parse manifest.json (invalid JSON)")

    if "schema_version" not in manifest:
        raise ValueError("manifest.json missing schema_version")

    for fname in manifest.get("files", []):
        if fname not in members:
            raise ValueError(f"Referenced file not in archive: {fname}")

    return manifest


def resolve_existing_backup_path(file_arg: str) -> Path | None:
    backup_path = Path(file_arg)

    if backup_path.exists():
        return backup_path

    resolved = BACKUP_DIR / file_arg

    if resolved.exists():
        return resolved

    return None


def prune_old_backups():
    max_backups = Config.load().backup.get("max_backups", 10)

    if max_backups <= 0:
        max_backups = 10

    backups = sorted(BACKUP_DIR.glob("backup-*.tar.gz"))

    if len(backups) > max_backups:
        for old_backup in backups[:-max_backups]:
            old_backup.unlink()


def replicate_backup(filename, console):
    backup_cfg = Config.load().backup
    enabled = backup_cfg.get("replication_enabled", False)

    if not enabled:
        return

    remote_host = backup_cfg.get("replication_remote_host")
    remote_port = backup_cfg.get("replication_remote_port", 8080)

    if not remote_host:
        console.stderr = True
        console.print("[yellow]Remote host not configured for replication[/yellow]")
        console.stderr = False
        return

    url = f"http://{remote_host}:{remote_port}{BACKUP_REPLICATION_ENDPOINT}"
    archive_path = BACKUP_DIR / filename

    if not archive_path.exists():
        console.stderr = True
        console.print("[yellow]Backup file not found for replication[/yellow]")
        console.stderr = False
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
                console.stderr = False

    except urllib.error.URLError as e:
        console.stderr = True
        console.print(
            f"[yellow]Failed to connect to remote server: {e.reason}[/yellow]"
        )
        console.stderr = False

    except Exception as e:
        console.stderr = True
        console.print(f"[yellow]Error during replication: {e}[/yellow]")
        console.stderr = False


def resolve_backup_path():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%S")
    base_filename = f"backup-{timestamp}"

    archive_path = BACKUP_DIR / f"{base_filename}.tar.gz"

    counter = 1

    while archive_path.exists():
        archive_path = BACKUP_DIR / f"{base_filename}-{counter}.tar.gz"
        counter += 1

    return archive_path.name, archive_path


def create_backup(console):
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

    return filename
