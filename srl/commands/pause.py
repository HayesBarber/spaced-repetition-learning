from rich.console import Console

from srl.pause_state import get_paused_on, pause_schedule


def add_subparser(subparsers):
    parser = subparsers.add_parser(
        "pause",
        help="Pause your review schedule until you resume",
    )
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    paused_on = pause_schedule()
    if paused_on is None:
        existing = get_paused_on()
        console.print(
            f"[yellow]Schedule is already paused since {existing.isoformat()}.[/yellow]"
        )
        return

    console.print(
        f"[green]Paused[/green] your schedule on {paused_on.isoformat()}. Run [cyan]srl resume[/cyan] when you return."
    )
