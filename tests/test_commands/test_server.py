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
            conn.request("GET", "/")
            resp = conn.getresponse()
            if resp.status in (405,):
                break
        except (ConnectionRefusedError, OSError):
            pass
        finally:
            conn.close()
        time.sleep(0.05)
    else:
        raise RuntimeError("Server failed to start")

    conn = HTTPConnection("127.0.0.1", 8765)
    body = json.dumps({"argv": ["ledger"]})
    conn.request("POST", "/", body=body, headers={"Content-Type": "application/json"})
    resp = conn.getresponse()
    data = json.loads(resp.read().decode("utf-8"))
    conn.close()

    assert data["status"] == "success"
