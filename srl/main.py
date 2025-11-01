from srl.cli import build_parser
from srl.storage import ensure_data_dir
from srl.banner import banner
from rich.console import Console


def main():
    ensure_data_dir()
    parser = build_parser()
    args = parser.parse_args()
    console = Console()

    if hasattr(args, "handler"):
        args.handler(args, console)
    else:
        banner(console)
        parser.print_help()
