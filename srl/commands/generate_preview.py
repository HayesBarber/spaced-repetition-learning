from rich.console import Console


def add_subparser(subparsers):
    gen_preview = subparsers.add_parser(
        "generate-preview", help="Generate SVG preview for the README"
    )
    gen_preview.set_defaults(handler=handle)
    return gen_preview


def handle(_, console: Console):
    from srl.banner import banner
    from srl.cli import build_parser

    banner(console)
    parser = build_parser()
    parser.print_help()
