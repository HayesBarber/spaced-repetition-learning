from rich.console import Console
from . import add, list_, remove, clear


def add_subparser(subparsers):
    parser = subparsers.add_parser(
        "nextup",
        help="Manage the Nextup Queue",
    )

    nextup_subparsers = parser.add_subparsers(required=True)

    add.add_subparser(nextup_subparsers)
    list_.add_subparser(nextup_subparsers)
    remove.add_subparser(nextup_subparsers)
    clear.add_subparser(nextup_subparsers)

    return parser


# here for backwards compat since a lot of tests call this handler
def handle(args, console: Console):
    action = getattr(args, "action", "")

    switcher = {
        "add": add.handle_add,
        "list": list_.handle_list,
        "remove": remove.handle_remove,
        "clear": clear.handle_clear,
    }

    if action in switcher:
        switcher[action](args, console)
