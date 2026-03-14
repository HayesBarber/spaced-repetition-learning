from rich.console import Console


def add_subparser(subparsers):
    parser = subparsers.add_parser("server", help="Run HTTP server to expose CLI")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload (dev)"
    )
    parser.add_argument("--public", action="store_true", help="Alias: bind to 0.0.0.0")
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    pass
