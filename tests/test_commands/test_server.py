import json
import threading
import time
import socket
import tarfile
import io
from types import SimpleNamespace
from datetime import datetime, timezone

from http.server import HTTPServer
from http.client import HTTPConnection

import pytest
from srl.commands import server


def _get_available_port():
    """Get an available port number."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        _, port = s.getsockname()
    return port


def _start_server(console):
    """Start the server and wait for it to be ready. Returns the port number."""
    HTTPServer.allow_reuse_address = True
    port = _get_available_port()
    args = SimpleNamespace(host="127.0.0.1", port=port)
    server_thread = threading.Thread(target=server.handle, args=(args, console))
    server_thread.daemon = True
    server_thread.start()

    for _ in range(20):
        conn = HTTPConnection("127.0.0.1", port, timeout=1)
        try:
            conn.request("POST", "/test")
            resp = conn.getresponse()
            if resp.status == 404:
                break
        except (ConnectionRefusedError, OSError):
            pass
        finally:
            conn.close()
        time.sleep(0.05)
    else:
        raise RuntimeError("Server failed to start")

    return port


def _post_backup(port, body, content_type="application/gzip", content_length=None):
    """Make a POST request to the /backup endpoint. Returns (status, response_data)."""
    conn = HTTPConnection("127.0.0.1", port)
    headers = {"Content-Type": content_type}
    if content_length is not None:
        headers["Content-Length"] = str(content_length)
    conn.request("POST", "/backup", body=body, headers=headers)
    resp = conn.getresponse()
    status = resp.status
    data = b""
    try:
        data = resp.read()
    except (ConnectionResetError, OSError):
        pass
    conn.close()
    return status, data.decode("utf-8")


@pytest.fixture(scope="module")
def live_server():
    """Start the server once for all integration tests in this module."""
    from rich.console import Console

    console = Console()
    port = _start_server(console)
    yield port


def test_root_handler_missing_body(console):
    code, response = server.root_handler("", console)
    assert code == 400
    assert "Missing Body" in response


def test_root_handler_invalid_json(console):
    code, response = server.root_handler("not json", console)
    assert code == 400
    assert "Invalid JSON" in response


def test_root_handler_missing_argv(console):
    code, response = server.root_handler("{}", console)
    assert code == 400
    assert "Missing argv" in response


def test_root_handler_argv_not_list(console):
    code, response = server.root_handler('{"argv": "ledger"}', console)
    assert code == 400
    assert "argv must be a list" in response


def test_root_handler_ledger_command(console):
    body = json.dumps({"argv": ["ledger", "-c"]})
    code, response = server.root_handler(body, console)
    assert code == 200
    data = json.loads(response)
    assert data["status"] == "success"
    assert "Total attempts: 0" in data["output"]


def test_verify_backup_request_wrong_content_type():
    code, msg = server.verify_backup_request("text/plain", 10)
    assert code == 415
    assert "Expected application/gzip" in msg


def test_verify_backup_request_missing_body():
    code, msg = server.verify_backup_request("application/gzip", 0)
    assert code == 400
    assert "Missing body" in msg


def test_verify_backup_request_valid():
    code, msg = server.verify_backup_request("application/gzip", 10)
    assert code == 200
    assert msg == ""


def test_backup_handler_bad_data(console, mock_data):
    code, msg = server.backup_handler(b"not a valid gzip file", console)
    assert code == 400
    assert "Bad data" in msg

    backups = list(mock_data.BACKUP_DIR.glob("backup-*.tar.gz"))
    assert len(backups) == 0, "Backup file should be deleted after bad data"


def test_backup_handler_success_and_prunes(console, mock_data, monkeypatch):
    called_prune = False

    def mock_prune():
        nonlocal called_prune
        called_prune = True

    monkeypatch.setattr("srl.commands.server.prune_old_backups", mock_prune)

    valid_backup = _create_valid_backup()
    code, msg = server.backup_handler(valid_backup, console)

    assert code == 200
    assert called_prune, "prune_old_backups should be called on successful backup"

    backups = list(mock_data.BACKUP_DIR.glob("backup-*.tar.gz"))
    assert len(backups) == 1, "Valid backup file should be saved"


def _create_valid_backup():
    """Create a valid gzip tar backup with manifest."""
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
        manifest = {
            "schema_version": 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "files": [],
        }
        manifest_data = json.dumps(manifest).encode()
        manifest_info = tarfile.TarInfo(name="manifest.json")
        manifest_info.size = len(manifest_data)
        tar.addfile(manifest_info, io.BytesIO(manifest_data))
    return buffer.getvalue()


def test_integration_ledger_command(live_server):
    conn = HTTPConnection("127.0.0.1", live_server)
    body = json.dumps({"argv": ["ledger", "-c"]})
    conn.request("POST", "/", body=body, headers={"Content-Type": "application/json"})
    resp = conn.getresponse()
    data = json.loads(resp.read().decode("utf-8"))
    conn.close()

    assert data["status"] == "success"
    assert "Total attempts: 0" in data["output"]


def test_integration_backup_not_gzip(live_server):
    status, data = _post_backup(live_server, b"some data", content_type="text/plain")
    assert status == 415
    response = json.loads(data)
    assert response["status"] == "error"
    assert response["error"] == "Expected application/gzip"
