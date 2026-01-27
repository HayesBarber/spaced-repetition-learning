from rich.console import Console
from rich.panel import Panel
from srl.storage import (
    load_json,
    PROGRESS_FILE,
)


def add_subparser(subparsers):
    parser = subparsers.add_parser("inprogress", help="List problems in progress")
    parser.add_argument("-u", "--url", action="store_true", help="Include problem URLs")
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    url_enabled: bool = getattr(args, "url", False)
    in_progress = get_in_progress()
    if in_progress:
        lines = []
        for i, p in enumerate(in_progress):
            if url_enabled and p["url"]:
                lines.append(f"{i+1}. {p['name']}  [blue][link={p['url']}]Open in Browser[/link][/blue]")
            else:
                lines.append(f"{i+1}. {p['name']}")

        console.print(
            Panel.fit(
                "\n".join(lines),
                title=f"[bold magenta]Problems in Progress ({len(in_progress)})[/bold magenta]",
                border_style="magenta",
                title_align="left",
            )
        )
    else:
        console.print("[yellow]No problems currently in progress.[/yellow]")


def get_in_progress() -> list[str]:
    data = load_json(PROGRESS_FILE)
    res = []

    for name, info in data.items():
        res.append({"name": name, "url": info.get("url", "")})
    return res
