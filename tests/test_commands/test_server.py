import json
import threading
import time
import socket
from types import SimpleNamespace
from pathlib import Path

from http.server import HTTPServer
from http.client import HTTPConnection

from srl.commands import server
from srl.commands.backup import resolve_backup_path, prune_old_backups


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
    data = resp.read().decode("utf-8")
    conn.close()
    return status, data


def test_server_ledger_command(console):
    port = _start_server(console)

    conn = HTTPConnection("127.0.0.1", port)
    body = json.dumps({"argv": ["ledger", "-c"]})
    conn.request("POST", "/", body=body, headers={"Content-Type": "application/json"})
    resp = conn.getresponse()
    data = json.loads(resp.read().decode("utf-8"))
    conn.close()

    assert data["status"] == "success"
    assert "Total attempts: 0" in data["output"]


def test_server_backup_not_gzip(console):
    port = _start_server(console)

    status, data = _post_backup(port, b"some data", content_type="text/plain")

    assert status == 415
    response = json.loads(data)
    assert response["status"] == "error"
    assert response["error"] == "Expected application/gzip"


def test_server_backup_missing_body(console):
    port = _start_server(console)

    status, data = _post_backup(port, b"", content_length=0)

    assert status == 400
    response = json.loads(data)
    assert response["status"] == "error"
    assert response["error"] == "Missing body"


def test_server_backup_bad_data(console, mock_data):
    port = _start_server(console)

    status, data = _post_backup(port, b"not a valid gzip file")

    assert status == 400
    response = json.loads(data)
    assert response["status"] == "error"
    assert response["error"] == "Bad data"

    backups = list(mock_data.BACKUP_DIR.glob("backup-*.tar.gz"))
    assert len(backups) == 0, "Backup file should be deleted after bad data"
