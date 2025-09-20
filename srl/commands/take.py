from types import SimpleNamespace
from rich.console import Console
from srl.commands import inprogress, nextup, add


def handle(args, console: Console):
    index: int = abs(args.index)
    problem = None
    inprogress_problems = inprogress.get_in_progress()

    if inprogress_problems and index < len(inprogress_problems):
        problem = inprogress_problems[index]
    else:
        nextup_problems = nextup.get_next_up_problems()
        if nextup_problems and index < len(nextup_problems):
            problem = nextup_problems[index]

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
