from types import SimpleNamespace
from rich.console import Console
from srl.commands import add, list_
import argparse


def add_subparser(subparsers):
    def positive_int(value):
        ivalue = int(value)
        if ivalue < 0:
            raise argparse.ArgumentTypeError(f"{value} is not a positive integer")
        return ivalue

    parser = subparsers.add_parser("take", help="Output a problem by index")
    parser.add_argument(
        "index", type=positive_int, help="Index of the problem to output"
    )
    parser.add_argument(
        "action",
        nargs="?",
        choices=["add"],
        default=None,
        help="Optional action to perform",
    )
    parser.add_argument(
        "rating", type=int, choices=range(1, 6), nargs="?", help="Rating from 1-5"
    )
    parser.set_defaults(handler=handle)
    return parser


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
