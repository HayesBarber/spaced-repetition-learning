from types import SimpleNamespace
from fastapi.testclient import TestClient

from srl import server as server_mod
from srl.server import create_app


def test_run_add_command_success():
    client = TestClient(create_app())
    cmd = 'add "HTTP Test Problem" 3'
    resp = client.post("/run", json={"cmd": cmd})
    assert resp.status_code == 200
    body = resp.json()
    assert "output" in body
    assert "Added rating 3" in body["output"]


def test_run_add_command_invalid_rating_returns_help():
    client = TestClient(create_app())
    cmd = 'add "Bad Rating" 7'
    resp = client.post("/run", json={"cmd": cmd})
    assert resp.status_code == 400
    body = resp.json()
    assert "output" in body
    assert "usage:" in body["output"]


def test_run_no_command_returns_help():
    client = TestClient(create_app())
    resp = client.post("/run", json={"argv": []})
    assert resp.status_code == 200
    body = resp.json()
    assert "output" in body
    assert "usage:" in body["output"] or body.get("exit") == 0


def test_run_handler_exception_returns_500():
    class FakeParser:
        def parse_args(self, argv):
            def handler(args, console):
                raise RuntimeError("boom")

            return SimpleNamespace(handler=handler)

        def print_help(self, file=None):
            if file:
                file.write("fake help\n")

    server_mod.parser = FakeParser()

    client = TestClient(create_app())
    resp = client.post("/run", json={"argv": ["ignored"]})
    assert resp.status_code == 500
    body = resp.json()
    assert "error" in body
    assert "Error executing handler" in body["error"]
