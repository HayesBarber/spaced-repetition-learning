import json
from io import StringIO
from rich.console import Console
import socket


def add_subparser(subparsers):
    parser = subparsers.add_parser("server", help="Run HTTP server to expose CLI")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    parser.set_defaults(handler=handle)
    return parser


def parse_request(request_bytes):
    try:
        request_str = request_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return None, "Invalid UTF-8"

    header_body = request_str.split("\r\n\r\n", 1)
    if len(header_body) < 2:
        return None, "Missing body"

    headers = header_body[0]
    body = header_body[1]

    content_length = 0
    for line in headers.split("\r\n"):
        if line.lower().startswith("content-length:"):
            content_length = int(line.split(":", 1)[1].strip())
            break

    if content_length > 0 and len(body) < content_length:
        return None, "Incomplete body"

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return None, "Invalid JSON"

    if "argv" not in data:
        return None, "Missing argv"

    argv = data["argv"]
    if not isinstance(argv, list):
        return None, "argv must be a list"

    return argv, None


def execute_command(argv, console: Console):
    from srl.cli import build_parser

    parser = build_parser()

    try:
        args = parser.parse_args(argv)
    except (Exception, SystemExit) as e:
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
    except Exception as e:
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


def build_response(data):
    body = json.dumps(data)
    body_bytes = body.encode("utf-8")
    response = (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: application/json\r\n"
        b"Content-Length: " + str(len(body_bytes)).encode("utf-8") + b"\r\n"
        b"\r\n" + body_bytes
    )
    return response


def handle(args, console: Console):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((args.host, args.port))
    server.listen()

    console.print(f"[green]Server listening on http://{args.host}:{args.port}[/green]")

    try:
        while 1:
            conn, addr = server.accept()
            with conn:
                console.print(f"Got request from {addr}")

                request_data = conn.recv(4096)

                argv, error = parse_request(request_data)

                if error:
                    result = {
                        "status": "error",
                        "output": "",
                        "error": error,
                    }
                else:
                    result = execute_command(argv, console)

                response = build_response(result)
                conn.sendall(response)

    except KeyboardInterrupt:
        console.print("[yellow]\nShutting down server...[/yellow]")
    finally:
        server.close()
        console.print("[green]Server closed[/green]")
