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


def handle(args, console: Console | None = None):
    from srl.server import run_server

    host = "0.0.0.0" if args.public else args.host
    msg = f"Starting server on {host}:{args.port} (reload={bool(args.reload)})"
    if console:
        console.print(msg)
    else:
        print(msg)

    run_server(host=host, port=args.port, reload=bool(args.reload))
