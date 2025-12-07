from rich.console import Console
from rich.text import Text


def add_subparser(subparsers):
    gen_preview = subparsers.add_parser(
        "generate-preview", help="Generate SVG preview for the README"
    )
    gen_preview.set_defaults(handler=handle)
    return gen_preview


def handle(_, console: Console):
    from srl.banner import banner
    from srl.cli import build_parser

    console.record = True

    banner(console)

    parser = build_parser()
    text = Text.from_ansi(parser.format_help())
    console.print(text, crop=False)

    console.save_svg(path="./preview.svg", title="srl")
