from . import create, list_, restore, verify


def add_subparser(subparsers):
    parser = subparsers.add_parser(
        "backup",
        help="Manage backups",
    )

    backup_subparsers = parser.add_subparsers(required=True)

    create.add_subparser(backup_subparsers)
    list_.add_subparser(backup_subparsers)
    restore.add_subparser(backup_subparsers)
    verify.add_subparser(backup_subparsers)
