import json
import socket
import threading
import time
from types import SimpleNamespace

from srl.commands import server


def test_server_ledger_command(console):
    args = SimpleNamespace(host="127.0.0.1", port=8765)

    server_thread = threading.Thread(target=server.handle, args=(args, console))
    server_thread.daemon = True
    server_thread.start()

    time.sleep(0.5)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 8765))

    body = json.dumps({"argv": ["ledger"]})
    request = (
        f"POST / HTTP/1.1\r\n"
        f"Host: localhost\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"\r\n"
        f"{body}"
    )
    sock.sendall(request.encode("utf-8"))

    response = sock.recv(4096)
    sock.close()

    response_str = response.decode("utf-8")
    _, _, body = response_str.partition("\r\n\r\n")
    data = json.loads(body)

    assert data["status"] == "success"
