from . import fail, history, pass_, run


def add_subparser(subparsers):
    parser = subparsers.add_parser(
        "audit",
        help="Manage random audits",
    )

    audit_subparsers = parser.add_subparsers(
        dest="audit_command",
        required=True,
    )

    run.add_subparser(audit_subparsers)
    pass_.add_subparser(audit_subparsers)
    fail.add_subparser(audit_subparsers)
    history.add_subparser(audit_subparsers)

    return parser
