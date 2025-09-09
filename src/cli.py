import argparse
from problems import *
from storage import ensure_data_dir, load_json, NEXT_UP_FILE
from rich.table import Table
from rich.console import Console
from rich.panel import Panel


def main():
    ensure_data_dir()
    parser = argparse.ArgumentParser(prog="srl")
    subparsers = parser.add_subparsers(dest="command")

    add = subparsers.add_parser("add", help="Add or update a problem attempt")
    add.add_argument("name", type=str, help="Name of the LeetCode problem")
    add.add_argument("rating", type=int, choices=range(1, 6), help="Rating from 1-5")

    list_ = subparsers.add_parser("list", help="List due problems")
    list_.add_argument("-n", type=int, default=None, help="Max number of problems")

    mastered = subparsers.add_parser("mastered", help="List mastered problems")
    mastered.add_argument(
        "-c", action="store_true", help="Show count of mastered problems"
    )

    subparsers.add_parser("inprogress", help="List problems in progress")

    nextup = subparsers.add_parser("nextup", help="Next up problem queue")
    nextup.add_argument(
        "action", choices=["add", "list"], help="Add or list next-up problems"
    )
    nextup.add_argument("name", nargs="?", help="Problem name (only needed for 'add')")

    audit = subparsers.add_parser("audit", help="Random audit functionality")
    audit.add_argument(
        "--pass", dest="audit_pass", action="store_true", help="Pass the audit"
    )
    audit.add_argument(
        "--fail", dest="audit_fail", action="store_true", help="Fail the audit"
    )

    remove = subparsers.add_parser("remove", help="Remove a problem from in-progress")
    remove.add_argument("name", type=str, help="Name of the problem to remove")

    config = subparsers.add_parser("config", help="Update configuration values")
    config.add_argument(
        "--audit-probability", type=float, help="Set audit probability (0-1)"
    )

    args = parser.parse_args()

    console = Console()

    if args.command == "add":
        add_or_update_problem(args.name, args.rating)
    elif args.command == "remove":
        remove_problem(args.name)
    elif args.command == "list":
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
                "[bold underline]Problems to Practice Today:[/bold underline]"
            )
            for p in problems:
                console.print(f" • [cyan]{p}[/cyan]")
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
        console.print("[bold underline]Problems in progress:[/bold underline]")
        for p in in_progress:
            console.print(f" • [cyan]{p}[/cyan]")
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
    elif args.command == "config":
        if args.audit_probability is not None:
            set_audit_probability(args.audit_probability)
        else:
            print("No configuration option provided.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
