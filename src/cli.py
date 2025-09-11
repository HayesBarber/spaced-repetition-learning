import argparse
from problems import *
from storage import ensure_data_dir, load_json, NEXT_UP_FILE
from rich.table import Table
from rich.console import Console
from rich.panel import Panel


def main():
    ensure_data_dir()

    args = parser.parse_args()

    console = Console()

    if args.command == "list":
        if should_audit() and not get_current_audit():
            problem = random_audit()
            if problem:
                console.print("[bold red]You have been randomly audited![/bold red]")
                console.print(f"[yellow]Audit problem:[/yellow] [cyan]{problem}[/cyan]")
                console.print(
                    "Run [green]srl audit --pass[/green] or [red]--fail[/red] when done"
                )
                return

        problems = get_due_problems(args.n)
        if problems:
            console.print(
                Panel.fit(
                    "\n".join(f"• {p}" for p in problems),
                    title="[bold blue]Problems to Practice Today[/bold blue]",
                    border_style="blue",
                    title_align="left",
                )
            )
        else:
            console.print(
                "[bold green]No problems due today or in Next Up.[/bold green]"
            )
    elif args.command == "mastered":
        mastered_problems = get_mastered_problems()
        if args.c:
            mastered_count = len(mastered_problems)
            console.print(f"[bold green]Mastered Count:[/bold green] {mastered_count}")
        else:
            if not mastered_problems:
                console.print("[yellow]No mastered problems yet.[/yellow]")
            else:
                table = Table(title="Mastered Problems", title_justify="left")
                table.add_column("Problem", style="cyan", no_wrap=True)
                table.add_column("Attempts", style="magenta")

                for name, attempts in mastered_problems:
                    table.add_row(name, str(attempts))

                console.print(table)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
