from .run import add_subparser as add_run_subparser
from .pass_ import add_subparser as add_pass_subparser
from .fail import add_subparser as add_fail_subparser
from .history import add_subparser as add_history_subparser


def add_subparser(subparsers):
    parser = subparsers.add_parser(
        "audit",
        help="Manage random audits",
    )

    audit_subparsers = parser.add_subparsers(
        dest="audit_command",
        required=True,
    )

    add_run_subparser(audit_subparsers)
    add_pass_subparser(audit_subparsers)
    add_fail_subparser(audit_subparsers)
    add_history_subparser(audit_subparsers)

    return parser
