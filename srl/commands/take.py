from rich.console import Console
from srl.commands import list_
import argparse


def positive_int(value: str) -> int:
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(f"{value} is not a positive integer")
    return ivalue


def add_subparser(subparsers):
    parser = subparsers.add_parser(
        "take",
        help="Output a problem by index",
    )
    parser.add_argument(
        "index",
        type=positive_int,
        help="Problem number from `srl list`",
    )
    parser.add_argument(
        "-u",
        "--url",
        action="store_true",
        help="Output the problem URL instead of the name",
    )
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    url_requested: bool = getattr(args, "url", False)
    index: int = args.index
    if index <= 0:
        return
    problem = None
    url = None
    due_problems = list_.get_due_problems()

    if due_problems and 0 < index <= len(due_problems):
        problem, url = due_problems[index - 1]

    if not problem:
        return

    if url_requested and not url:
        return

    if url_requested:
        console.print(url)
    else:
        console.print(problem)
