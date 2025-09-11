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
    elif args.command == "inprogress":
        in_progress = get_in_progress()
        if in_progress:
            console.print(
                Panel.fit(
                    "\n".join(f"• {p}" for p in in_progress),
                    title="[bold magenta]Problems in Progress[/bold magenta]",
                    border_style="magenta",
                    title_align="left",
                )
            )
        else:
            console.print("[yellow]No problems currently in progress.[/yellow]")
    elif args.command == "nextup":
        if args.action == "add":
            if not args.name:
                console.print(
                    "[bold red]Please provide a problem name to add to Next Up.[/bold red]"
                )
            else:
                add_to_next_up(args.name)
                console.print(
                    f"[green]Added[/green] [bold]{args.name}[/bold] to Next Up Queue"
                )
        elif args.action == "list":
            next_up = load_json(NEXT_UP_FILE)
            if next_up:
                console.print(
                    Panel.fit(
                        "\n".join(f"• {name}" for name in next_up),
                        title="[bold cyan]Next Up Problems[/bold cyan]",
                        border_style="cyan",
                        title_align="left",
                    )
                )
            else:
                console.print("[yellow]Next Up queue is empty.[/yellow]")
    elif args.command == "audit":
        if args.audit_pass:
            curr = get_current_audit()
            if curr:
                audit_pass(curr)
                print("Audit passed!")
            else:
                print("No active audit to pass.")
        elif args.audit_fail:
            curr = get_current_audit()
            if curr:
                audit_fail(curr)
                print("Audit failed. Problem moved back to in-progress.")
            else:
                print("No active audit to fail.")
        else:
            curr = get_current_audit()
            if curr:
                print(f"Current audit problem: {curr}")
                print("Run with --pass or --fail to complete it.")
            else:
                problem = random_audit()
                if problem:
                    print(f"You are now being audited on: {problem}")
                    print("Run with --pass or --fail to complete the audit.")
                else:
                    print("No mastered problems available for audit.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
