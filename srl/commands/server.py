import json
from io import StringIO
from rich.console import Console
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse


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

        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._send_error("Invalid JSON")
            return

        if "argv" not in data:
            self._send_error("Missing argv")
            return
        argv = data["argv"]
        if not isinstance(argv, list):
            self._send_error("argv must be a list")
            return

        result = execute_command(argv, console)
        self._send_success(result)

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

        # todo save data

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
        self.server.console.print(f"Got request from {self.client_address}")

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
