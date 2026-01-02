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
    parser.add_argument("-u", "--url", action="store_true", help="Include problem URLs")
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    url_requested: bool = getattr(args, "url", False)
    index: int = abs(args.index)
    problem = None
    url = None
    due_problems = list_.get_due_problems(None, url_requested)

    if due_problems and 0 < index <= len(due_problems):
        has_url = due_problems[index - 1].endswith("[/link][/blue]")
        if not has_url:
            problem = due_problems[index - 1]
        elif has_url:
            raw_markup = due_problems[index - 1]
            url_start = raw_markup.find("[link=") + len("[link=")
            url_end = raw_markup.find("]Open")
            name_end = url_end - 2 # -2 for double space delimiter between name and hyperlink
            
            problem = raw_markup[:name_end]
            url = raw_markup[url_start:url_end]
        
        # NOTE: if url_requested and not has_url, url will stay None, and "None" will be printed

    if not problem:
        return

    if args.action == "add":
        if args.rating is None:
            console.print(
                "[red]Error: rating must be provided when action is 'add'[/red]"
            )
            return
        add.handle(
            SimpleNamespace(name=problem, rating=args.rating), console
        )
    else:
        console.print(url if url_requested else problem)
