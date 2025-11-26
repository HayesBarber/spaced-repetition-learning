from srl.cli import build_parser
from srl.storage import ensure_data_dir
from srl.banner import banner
from rich.console import Console


from rich.table import Table


def print_help_table(console: Console):
    table = Table(title="Available Commands", show_header=True, header_style="bold magenta")
    table.add_column("Command", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")
    table.add_column("Example", style="dim")

    commands = [
        ("add", "Add or update a problem attempt", 'srl add "Two Sum" 3'),
        ("list", "List due problems", "srl list"),
        ("mastered", "List mastered problems", "srl mastered"),
        ("inprogress", "List problems in progress", "srl inprogress"),
        ("nextup", "Manage the Next Up queue", 'srl nextup add "Problem"'),
        ("audit", "Random audit functionality", "srl audit"),
        ("remove", "Remove a problem from in-progress", 'srl remove "Two Sum"'),
        ("config", "Update configuration values", "srl config --get"),
        ("take", "Output a problem by index", "srl take 1"),
        ("server", "Run HTTP server to expose CLI", "srl server"),
        ("random", "Pick a random due problem", "srl random"),
        ("calendar", "Graph of SRL activity", "srl calendar"),
    ]

    for cmd, desc, example in commands:
        table.add_row(cmd, desc, example)

    console.print(table)
    console.print("\n[dim]Run 'srl <command> --help' for more information on a specific command.[/dim]\n")


def main():
    ensure_data_dir()
    parser = build_parser()
    args = parser.parse_args()
    console = Console()

    if hasattr(args, "handler"):
        args.handler(args, console)
    else:
        banner(console)
        print_help_table(console)
