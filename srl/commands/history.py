from rich.console import Console
from rich.table import Table
from srl.storage import (
    load_json,
    PROGRESS_FILE,
    MASTERED_FILE,
)


def add_subparser(subparsers):
    parser = subparsers.add_parser("history", help="List all problems and their status")
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    history_items = get_all_history()
    
    if not history_items:
        console.print("[yellow]No problems found in history.[/yellow]")
        return

    table = Table(title=f"Problem History ({len(history_items)})", title_justify="left")
    table.add_column("Problem", style="cyan", no_wrap=True)
    table.add_column("Status", no_wrap=True)
    table.add_column("Last Attempt", style="magenta")
    table.add_column("Last Rating", justify="center")

    for item in history_items:
        name = item["name"]
        status = item["status"]
        date = item["date"]
        rating = str(item["rating"])
        
        status_style = "green" if status == "Mastered" else "yellow"
        rating_style = get_rating_color(item["rating"])
        
        table.add_row(
            name,
            f"[{status_style}]{status}[/{status_style}]",
            date,
            f"[{rating_style}]{rating}[/{rating_style}]"
        )

    console.print(table)


def get_all_history():
    items = []
    
    # Process In Progress
    progress_data = load_json(PROGRESS_FILE)
    for name, info in progress_data.items():
        history = info.get("history", [])
        if history:
            last = history[-1]
            items.append({
                "name": name,
                "status": "In Progress",
                "date": last["date"],
                "rating": last["rating"]
            })

    # Process Mastered
    mastered_data = load_json(MASTERED_FILE)
    for name, info in mastered_data.items():
        history = info.get("history", [])
        if history:
            last = history[-1]
            items.append({
                "name": name,
                "status": "Mastered",
                "date": last["date"],
                "rating": last["rating"]
            })
            
    # Sort by date descending
    items.sort(key=lambda x: x["date"], reverse=True)
    return items


def get_rating_color(rating):
    if rating >= 5:
        return "green"
    elif rating >= 3:
        return "yellow"
    else:
        return "red"
