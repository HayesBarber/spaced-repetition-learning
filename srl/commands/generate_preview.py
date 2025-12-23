from rich.console import Console
from types import SimpleNamespace


def add_subparser(subparsers):
    gen_preview = subparsers.add_parser(
        "generate-preview", help="Generate SVG preview for the README"
    )
    gen_preview.set_defaults(handler=handle)
    return gen_preview


def handle(_, console: Console):
    from srl.commands import calendar

    console.record = True
    calendar.handle(SimpleNamespace(months=8), console)
    console.save_svg(path="./preview.svg", title="srl")
