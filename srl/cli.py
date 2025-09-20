import argparse


def build_parser() -> argparse.ArgumentParser:
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
    config.add_argument(
        "--get", action="store_true", help="Display current configuration"
    )

    def positive_int(value):
        ivalue = int(value)
        if ivalue < 0:
            raise argparse.ArgumentTypeError(f"{value} is not a positive integer")
        return ivalue

    take = subparsers.add_parser("take", help="Output a problem by index")
    take.add_argument("index", type=positive_int, help="Index of the problem to output")
    take.add_argument(
        "action",
        nargs="?",
        choices=["add"],
        default=None,
        help="Optional action to perform",
    )
    take.add_argument(
        "rating", type=int, choices=range(1, 6), nargs="?", help="Rating from 1-5"
    )

    return parser
