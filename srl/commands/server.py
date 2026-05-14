import json
from io import StringIO
from rich.console import Console
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from srl.commands.backup import resolve_backup_path, verify_handle, prune_old_backups
from types import SimpleNamespace


def add_subparser(subparsers):
    parser = subparsers.add_parser("server", help="Run HTTP server to expose CLI")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    parser.set_defaults(handler=handle)
    return parser


def execute_command(argv, console: Console) -> dict:
    from srl.cli import build_parser

    parser = build_parser()

    try:
        args = parser.parse_args(argv)
    except (Exception, SystemExit):
        return {
            "status": "error",
            "output": "",
            "error": "Invalid arguments",
        }

    if not hasattr(args, "handler"):
        return {
            "status": "error",
            "output": "",
            "error": "No command specified",
        }

    if getattr(args, "command", None) == "server":
        return {
            "status": "error",
            "output": "",
            "error": "Cannot run server command from HTTP API",
        }

    output = StringIO()
    capture_console = Console(file=output, force_terminal=False)

    try:
        args.handler(args, capture_console)
    except Exception:
        return {
            "status": "error",
            "output": "",
            "error": "Error executing handler",
        }

    return {
        "status": "success",
        "output": output.getvalue(),
        "error": None,
    }


def root_handler(body: str, console: Console) -> tuple[int, str]:
    if not body:
        return 400, "Missing Body"

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return 400, "Invalid JSON"

    if "argv" not in data:
        return 400, "Missing argv"

    argv = data["argv"]
    if not isinstance(argv, list):
        return 400, "argv must be a list"

    result = execute_command(argv, console)
    if result["status"] == "error":
        return 400, result["error"]

    return 200, json.dumps(result).encode("utf-8")


class SRLRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        path = urlparse(self.path).path

        routes = {
            "/": self.handle_root,
            "/backup": self.handle_backup,
        }

        handler = routes.get(path, self.handle_404)
        handler()

    def handle_root(self):
        console = self.server.console
        content_length = int(self.headers.get("Content-Length", 0))
        body = (
            self.rfile.read(content_length).decode("utf-8")
            if content_length > 0
            else ""
        )

        code, response = root_handler(body, console)

        if code != 200:
            self._send_error(response, code)
        else:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(response)

    def handle_backup(self):
        content_type = self.headers.get("Content-Type")
        if content_type != "application/gzip":
            self._send_error("Expected application/gzip", code=415)
            return

        length = int(self.headers.get("Content-Length", 0))
        if length <= 0:
            self._send_error("Missing body")
            return

        data = self.rfile.read(length)
        filename, archive_path = resolve_backup_path()
        with open(archive_path, "wb") as f:
            f.write(data)

        verify_args = SimpleNamespace(file=str(archive_path))
        if verify_handle(verify_args, self.server.console):
            self._send_error("Bad data")
            if archive_path.exists():
                archive_path.unlink()
            return

        prune_old_backups()

        self._send_success()

    def _send_error(self, error_msg: str, code: int = 400):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(
            json.dumps({"status": "error", "output": "", "error": error_msg}).encode(
                "utf-8"
            )
        )

    def _send_success(self, result: dict | None = None):
        if result is not None:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
        else:
            self.send_response(200)
            self.end_headers()

    def log_message(self, format, *args):
        message = format % args
        self.server.console.print(f"{self.client_address} - {message}")

    def handle_404(self):
        self.send_response(404)
        self.end_headers()


def handle(args, console: Console):
    server = HTTPServer((args.host, args.port), SRLRequestHandler)
    server.console = console
    console.print(f"[green]Server listening on http://{args.host}:{args.port}[/green]")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        console.print("[yellow]\nShutting down server...[/yellow]")
    finally:
        server.server_close()
        console.print("[green]Server closed[/green]")
