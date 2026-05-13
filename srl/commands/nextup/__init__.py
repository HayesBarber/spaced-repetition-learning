from rich.console import Console
from .add import handle_add
from .clear import handle_clear
from .remove import handle_remove
from .list_ import handle_list


def add_subparser(subparsers):
    parser = subparsers.add_parser(
        "nextup",
        help="Manage the Nextup Queue",
    )

    nextup_subparsers = parser.add_subparsers(required=True)

    # add
    add_parser = nextup_subparsers.add_parser(
        "add",
        help="Add problem(s) to the queue",
    )
    add_parser.add_argument(
        "name",
        nargs="?",
        help="Problem name to add",
    )
    add_parser.add_argument(
        "-f",
        "--file",
        help="Path to a file with one problem per line: 'name' or 'name,url'",
    )
    add_parser.add_argument(
        "--allow-mastered",
        action="store_true",
        help="Allow problems that are already mastered",
    )
    add_parser.add_argument(
        "-u",
        "--url",
        nargs="?",
        const="",
        default=None,
        help="URL to the problem",
    )
    add_parser.set_defaults(handler=handle_add)

    # list
    list_parser = nextup_subparsers.add_parser(
        "list",
        help="List queued problems",
    )
    list_parser.set_defaults(handler=handle_list)

    # remove
    remove_parser = nextup_subparsers.add_parser(
        "remove",
        help="Remove a problem from the queue",
    )
    remove_parser.add_argument(
        "name",
        nargs="?",
        help="Problem name to remove",
    )
    remove_parser.add_argument(
        "-n",
        "--number",
        type=int,
        help="Remove by 1-based index from 'srl nextup list'",
    )
    remove_parser.set_defaults(handler=handle_remove)

    # clear
    clear_parser = nextup_subparsers.add_parser(
        "clear",
        help="Clear the queue",
    )
    clear_parser.set_defaults(handler=handle_clear)

    return parser


def handle(args, console: Console):
    if args.action == "add":
        handle_add(args, console)
    elif args.action == "list":
        handle_list(args, console)
    elif args.action == "remove":
        handle_remove(args, console)
    elif args.action == "clear":
        handle_clear(args, console)
