from rich.console import Console

from srl.pause_state import resume_schedule


def add_subparser(subparsers):
    parser = subparsers.add_parser(
        "resume",
        aliases=["unpause"],
        help="Resume your review schedule after a pause",
    )
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    if not resume_schedule(console=console, auto=False):
        console.print("[yellow]Schedule is not paused.[/yellow]")
