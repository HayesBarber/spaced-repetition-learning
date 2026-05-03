import json
import threading
import time
from types import SimpleNamespace

from http.client import HTTPConnection

from srl.commands import server


def test_server_ledger_command(console):
    args = SimpleNamespace(host="127.0.0.1", port=8765)

    server_thread = threading.Thread(target=server.handle, args=(args, console))
    server_thread.daemon = True
    server_thread.start()

    for _ in range(20):
        conn = HTTPConnection("127.0.0.1", 8765, timeout=1)
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

    conn = HTTPConnection("127.0.0.1", 8765)
    body = json.dumps({"argv": ["ledger", "-c"]})
    conn.request("POST", "/", body=body, headers={"Content-Type": "application/json"})
    resp = conn.getresponse()
    data = json.loads(resp.read().decode("utf-8"))
    conn.close()

    assert data["status"] == "success"
    assert "Total attempts: 0" in data["output"]


def test_server_backup_not_gzip():
    pass


def test_server_backup_missing_body():
    pass


def test_server_backup_bad_data():
    pass


def test_server_backup_not_success_and_prunes():
    pass
