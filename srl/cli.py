import argparse
from srl.commands import (
    add,
    list_,
    mastered,
    inprogress,
    calendar,
    nextup,
    audit,
    remove,
    config,
    take,
    server,
    ledger,
    summary,
    backup,
)


def get_version() -> str:
    try:
        from srl._version import version

        return version
    except Exception:
        return "unknown"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="srl")
    parser.add_argument("-v", "--version", action="version", version=get_version())
    subparsers = parser.add_subparsers(dest="command")

    add.add_subparser(subparsers)
    list_.add_subparser(subparsers)
    mastered.add_subparser(subparsers)
    inprogress.add_subparser(subparsers)
    calendar.add_subparser(subparsers)
    nextup.add_subparser(subparsers)
    audit.add_subparser(subparsers)
    remove.add_subparser(subparsers)
    config.add_subparser(subparsers)
    take.add_subparser(subparsers)
    server.add_subparser(subparsers)
    ledger.add_subparser(subparsers)
    summary.add_subparser(subparsers)
    backup.add_subparser(subparsers)
    return parser
