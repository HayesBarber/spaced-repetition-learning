from rich.console import Console
from rich.text import Text


def banner(console: Console):
    txt = f"""
    ███████╗██████╗ ██╗     
    ██╔════╝██╔══██╗██║     
    ███████╗██████╔╝██║     
    ╚════██║██╔══██╗██║     
    ███████║██║  ██║███████║
    ╚══════╝╚═╝  ╚═╝╚══════╝
"""
    with_color = Text(txt, style="bold cyan")
    console.print(with_color)
