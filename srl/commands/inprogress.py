from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
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
        console.print(
            Panel.fit(
                # TODO: update tests to accept MD output
                # meanwhile, don't render MD for default input to pass tests
                (
                    Markdown("\n".join(f"{i+1}. {p["name"]}{f"  [Open in LeetCode]({p["url"]})" if p["url"] else ""}" for i, p in enumerate(in_progress)))
                    if url_enabled 
                    else "\n".join(f"{i+1}. {p["name"]}" for i, p in enumerate(in_progress))
                ),
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
