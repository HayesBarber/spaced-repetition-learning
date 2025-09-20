from rich.console import Console
from srl.commands import inprogress, nextup


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

    console.print(problem)
