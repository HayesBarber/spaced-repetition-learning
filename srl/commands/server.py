from rich.console import Console
import socket


def add_subparser(subparsers):
    parser = subparsers.add_parser("server", help="Run HTTP server to expose CLI")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((args.host, args.port))
    server.listen()

    console.print(f"[green]Server listening on http://{args.host}:{args.port}[/green]")

    try:
        while True:
            conn, addr = server.accept()
            with conn:
                console.print(f"Got request")
    except KeyboardInterrupt:
        console.print("[yellow]\nShutting down server...[/yellow]")
    finally:
        server.close()
        console.print("[green]Server closed[/green]")
