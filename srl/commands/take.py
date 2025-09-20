from types import SimpleNamespace
from rich.console import Console
from srl.commands import add, list_


def handle(args, console: Console):
    index: int = abs(args.index)
    problem = None
    due_problems = list_.get_due_problems()

    if due_problems and index < len(due_problems):
        problem = due_problems[index]

    if not problem:
        return

    if args.action == "add":
        if args.rating is None:
            console.print(
                "[red]Error: rating must be provided when action is 'add'[/red]"
            )
            return
        add.handle(SimpleNamespace(name=problem, rating=args.rating), console)
    else:
        console.print(problem)
