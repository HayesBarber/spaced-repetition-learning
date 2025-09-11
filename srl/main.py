from cli import build_parser
from commands import DISPATCH
from storage import ensure_data_dir
from rich.console import Console


def main():
    ensure_data_dir()
    parser = build_parser()
    args = parser.parse_args()
    console = Console()

    handler = DISPATCH.get(args.command)
    if handler:
        handler(args, console)
    else:
        parser.print_help()
