from rich.console import Console
from rich.text import Text


def banner(console: Console):
    txt = _banner()
    with_color = Text(txt, style="bold cyan")
    console.print(with_color)


def _banner():
    txt = """
    ███████╗██████╗ ██╗     
    ██╔════╝██╔══██╗██║     
    ███████╗██████╔╝██║     
    ╚════██║██╔══██╗██║     
    ███████║██║  ██║███████║
    ╚══════╝╚═╝  ╚═╝╚══════╝
"""
    return txt
